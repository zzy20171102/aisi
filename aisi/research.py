"""调研闭环：gaps → 调研问题清单（宿主搜索）→ findings 归档（可选沉淀知识库）。"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from .validator import load_schema, validate


def plan(ws) -> dict:
    gp = ws.base / "research" / "gaps.json"
    if not gp.exists():
        raise FileNotFoundError("research/gaps.json 不存在，请先运行 aisi coverage")
    gaps = json.loads(gp.read_text(encoding="utf-8"))
    questions, seen = [], set()
    for g in gaps.get("gaps", []):
        q = g["question_hint"]
        if q in seen:
            continue
        seen.add(q)
        questions.append({"id": f"Q{len(questions) + 1:02d}", "question": q,
                          "reason": f"{g['kind']}（{g['target']}）：{g['detail']}",
                          "status": "open"})
    data = {"schema": "aisi.research/1",
            "topic": f"{ws.manifest['name']} 证据缺口调研",
            "questions": questions, "sources": []}
    out = ws.base / "research" / "questions.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"questions": len(questions), "file": str(out),
            "next_action": "宿主 Agent 逐题搜索，结果按 aisi.research/1 填入 questions[].findings + sources，"
                           "再 aisi research ingest --file <findings.json> [--to-kb]"}


def ingest_findings(ws, data: dict, to_kb: bool = False) -> dict:
    errors = validate(data, load_schema("research"))
    if errors:
        raise ValueError(f"调研结果不符合 aisi.research/1 契约: {errors}")
    out = ws.base / "research" / "findings.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = {"file": str(out),
              "questions": len(data.get("questions", [])),
              "answered": sum(1 for q in data.get("questions", []) if q.get("status") == "answered"),
              "sources": len(data.get("sources", []))}
    if to_kb:
        result["kb_files"] = _write_kb(ws, data)
        result["next_action"] = ("执行 kb.py save 沉淀知识库：\n  " +
                                 "\n  ".join(f'uv run python .opencode/skills/knowledge-base/kb.py save "{f}"'
                                           for f in result["kb_files"]))
    else:
        result["next_action"] = "如需沉淀知识库，加 --to-kb 重新执行"
    return result


def _write_kb(ws, data: dict) -> list[str]:
    root = ws.base.parent.parent  # systems/<id> → 项目根
    kb_dir = None
    for cand in (root / "knowledge", Path.cwd() / "knowledge"):
        if cand.exists():
            kb_dir = cand
            break
    if kb_dir is None:
        kb_dir = root / "knowledge"  # 项目根无知识库时默认创建（12-Factor：状态即文件）
    n = 0
    for f in kb_dir.rglob("KB-????-????.md"):
        try:
            n = max(n, int(f.stem.split("-")[2]))
        except (IndexError, ValueError):
            pass
    year = date.today().year
    files = []
    for q in data.get("questions", []):
        if q.get("status") != "answered" or not q.get("findings"):
            continue
        n += 1
        kb_id = f"KB-{year}-{n:04d}"
        body = "\n".join(f"- {f.get('summary', '')}（置信度：{f.get('confidence', 'medium')}，"
                         f"来源：{', '.join(f.get('source_refs', []))}）"
                         for f in q["findings"])
        srcs = "\n".join(f"- {s['id']} {s['title']}：{s['url']}（{s['reliability']}，{s['accessed']}）"
                         for s in data.get("sources", [])
                         if s["id"] in {r for f in q["findings"] for r in f.get("source_refs", [])})
        content = (f"---\nid: {kb_id}\ntype: domain\ntitle: 调研：{q['question']}\n"
                   f"tags: [research, {ws.manifest['system_id']}]\n"
                   f"source: aisi research（{ws.manifest['system_id']}）\n"
                   f"created: {date.today().isoformat()}\nstatus: active\nsupersedes: \"\"\n"
                   f"confidence: medium\n---\n\n## 内容\n\n{body}\n\n"
                   f"## 来源\n\n{srcs or '（无登记来源）'}\n\n"
                   f"## 适用场景\n\n{ws.manifest['name']} 系统设计与需求完善时参考。\n")
        p = kb_dir / "domains" / f"{kb_id}-research.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        files.append(str(p))
    return files
