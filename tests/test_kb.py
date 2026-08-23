#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kb.py 集成测试（stdlib unittest，无需第三方依赖）。

运行：.venv/Scripts/python.exe -X utf8 -m unittest discover -s tests -v
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KB_SCRIPT = Path(__file__).resolve().parents[1] / ".opencode/skills/knowledge-base/kb.py"


def run_kb(kb_dir: Path, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ, "AISI_KB_DIR": str(kb_dir), "PYTHONUTF8": "1"}
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(KB_SCRIPT), *args],
        capture_output=True, text=True, encoding="utf-8", env=env,
        input=stdin, timeout=60,
    )


MD_TEMPLATE = """---
type: {type}
title: {title}
tags: [test, {tag}]
source: tests L1-L2
created: 2026-08-23
status: active
supersedes: ""
confidence: high
---

## 内容

{body}

## 适用场景

测试场景。
"""


class KbTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="aisi-kb-test-"))
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write_md(self, rel: str, **kw) -> Path:
        p = self.tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(MD_TEMPLATE.format(**kw), encoding="utf-8")
        return p

    def test_scan_detects_business_and_workflow(self):
        src = self.tmp / "notes.txt"
        src.write_text(
            "今天天气不错，随便聊聊。\n\n"
            "计费规则：客户账期超过 30 天必须提交审批，超额不得结算。\n\n"
            "部署流程：首先执行 install.sh，然后修改 config.yaml，最后重启服务。\n\n"
            "踩坑记录：接口超时报错，原因是连接池太小，解决方法是调大 pool_size。\n",
            encoding="utf-8",
        )
        r = run_kb(self.tmp, "scan", str(src))
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        types = {c["type"] for c in data["candidates"]}
        self.assertIn("business", types)
        self.assertIn("workflow", types)
        self.assertIn("lesson", types)
        self.assertTrue(all(c["lines"].startswith("L") for c in data["candidates"]))

    def test_save_auto_id_search_get_stats_link(self):
        p = self.write_md("business/seed.md", type="business",
                          title="客户账期审批规则", tag="billing",
                          body="客户账期超过 30 天必须提交审批，不得直接结算。")
        r = run_kb(self.tmp, "save", str(p))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("已索引 KB-", r.stdout)
        m = re.search(r"已索引 (KB-\d{4}-\d{4})", r.stdout)
        self.assertTrue(m, r.stdout)
        kb_id = m.group(1)
        # 自动 id 已回写文件
        self.assertIn(f"id: {kb_id}", p.read_text(encoding="utf-8"))

        r = run_kb(self.tmp, "search", "账期审批")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(kb_id, r.stdout)

        r = run_kb(self.tmp, "get", kb_id)
        self.assertIn("客户账期超过 30 天", r.stdout)

        r = run_kb(self.tmp, "stats")
        self.assertIn("业务知识", r.stdout)

        # 第二条 + 关系
        p2 = self.write_md("workflow/seed.md", type="workflow",
                           title="账期审批操作流程", tag="billing",
                           body="审批操作流程：登录后台，进入账期页面，提交审批单。")
        r = run_kb(self.tmp, "save", str(p2))
        self.assertEqual(r.returncode, 0, r.stderr)
        m2 = re.search(r"已索引 (KB-\d{4}-\d{4})", r.stdout)
        kb_id2 = m2.group(1)
        r = run_kb(self.tmp, "link", kb_id, kb_id2, "supports", "--note", "规则约束流程")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run_kb(self.tmp, "get", kb_id2)
        self.assertIn("[supports]", r.stdout)

        # INDEX.md 自动生成且包含条目（v1 漂移问题的回归测试）
        index = (self.tmp / "INDEX.md").read_text(encoding="utf-8")
        self.assertIn("自动生成", index)
        self.assertIn(kb_id, index)
        self.assertIn(kb_id2, index)

    def test_superseded_filtered_by_default(self):
        p = self.write_md("lessons/old.md", type="lesson",
                          title="旧方案连接池经验", tag="pool",
                          body="连接池经验：旧方案 pool_size 设 5 导致超时。")
        r = run_kb(self.tmp, "save", str(p))
        kb_id = re.search(r"已索引 (KB-\d{4}-\d{4})", r.stdout).group(1)
        text = p.read_text(encoding="utf-8").replace("status: active", "status: superseded")
        p.write_text(text, encoding="utf-8")
        r = run_kb(self.tmp, "save", str(p))
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run_kb(self.tmp, "search", "连接池")
        self.assertNotIn(kb_id, r.stdout)
        r = run_kb(self.tmp, "search", "连接池", "--all")
        self.assertIn(kb_id, r.stdout)

    def test_migration_from_stale_v1_db(self):
        """v1 遗留脏库（FTS 行 id=NULL）应自动丢弃重建，且 list 不再崩溃。"""
        p = self.write_md("decisions/seed.md", type="decision",
                          title="知识库选型决策", tag="arch",
                          body="决定采用本体 Markdown + SQLite FTS5 存储知识。")
        # 伪造 v1 脏库：空文件、无 schema、user_version=0
        (self.tmp / "index.db").write_bytes(b"")
        r = run_kb(self.tmp, "list")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("知识库选型决策", r.stdout)
        self.assertNotIn("TypeError", r.stderr)


if __name__ == "__main__":
    unittest.main()
