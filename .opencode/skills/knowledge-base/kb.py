#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AISI Agent 知识库管理工具 v2（本体 Markdown + SQLite FTS5，零依赖）。

三层架构：
  L1 索引层  knowledge/INDEX.md     由本工具自动生成，Agent 启动时轻量加载路由
  L2 本体层  knowledge/<分类>/*.md  每条知识一个文件，frontmatter 元数据 + 原文正文
  L3 检索层  knowledge/index.db     SQLite FTS5(trigram 中文友好) + 关系表 links

轻量本体 = 6 种知识类型 + 4 种关系（supersedes/supports/contradicts/related）+ 自由标签。

用法（项目规范 uv，uv 不可用时用 .venv\\Scripts\\python.exe 兜底）:
  uv run python .opencode/skills/knowledge-base/kb.py init
  uv run python .opencode/skills/knowledge-base/kb.py scan <文本文件> [--save]
  uv run python .opencode/skills/knowledge-base/kb.py save <知识.md> [...]
  uv run python .opencode/skills/knowledge-base/kb.py search "<关键词>" [-n 10] [--all]
  uv run python .opencode/skills/knowledge-base/kb.py get <KB-ID>
  uv run python .opencode/skills/knowledge-base/kb.py list [类型] [--all]
  uv run python .opencode/skills/knowledge-base/kb.py stats
  uv run python .opencode/skills/knowledge-base/kb.py link <A> <B> <关系> [--note 说明]
  uv run python .opencode/skills/knowledge-base/kb.py similar <KB-ID或标题>
  uv run python .opencode/skills/knowledge-base/kb.py rebuild

可用环境变量 AISI_KB_DIR 覆盖知识库根目录（测试/多项目复用）。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------- 常量与本体定义

SCHEMA_VERSION = 2

KB_DIR = Path(os.environ.get("AISI_KB_DIR") or (Path(__file__).resolve().parents[3] / "knowledge")).resolve()
DB_PATH = KB_DIR / "index.db"
INDEX_PATH = KB_DIR / "INDEX.md"

# 类型 -> (目录, 中文名)。业务知识与工作知识是两大主力类别。
TYPES: dict[str, tuple[str, str]] = {
    "business": ("business", "业务知识"),
    "workflow": ("workflow", "工作知识"),
    "decision": ("decisions", "决策记录"),
    "lesson": ("lessons", "经验教训"),
    "entity": ("entities", "实体卡片"),
    "domain": ("domains", "领域知识"),
}

ALLOWED_STATUS = {"active", "superseded", "outdated"}
RELATIONS = {"supersedes", "supports", "contradicts", "related"}

# --------------------------------------------------------------- frontmatter 解析


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """解析平铺 YAML frontmatter（零依赖；tags 支持列表写法）。"""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t", "-")):
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip().strip('"').strip("'").strip()
    return meta, m.group(2)


def norm_tags(raw: str) -> str:
    """`[a, b、c]` -> `a,b,c`。"""
    raw = re.sub(r"^\[|\]$", "", (raw or "").strip())
    parts = [p.strip() for p in re.split(r"[,，、;；]+", raw) if p.strip()]
    return ",".join(parts)


def slugify(text: str, fallback: str = "auto") -> str:
    """取 ASCII 标识；中文等非 ASCII 字符忽略。"""
    text = unicodedata.normalize("NFKD", text)
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return s[:40] or fallback


def today() -> str:
    return date.today().isoformat()


# ------------------------------------------------------------------------ 数据库


def connect() -> sqlite3.Connection:
    KB_DIR.mkdir(parents=True, exist_ok=True)
    for d, _ in TYPES.values():
        (KB_DIR / d).mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 关键修复：v1 缺此行导致 list/search 崩溃
    _migrate(conn)
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    """schema 版本迁移：旧/脏库（v1 遗留 FTS 行 id=NULL）直接丢弃并从 md 全量重建。"""
    v = conn.execute("PRAGMA user_version").fetchone()[0]
    if v == SCHEMA_VERSION:
        return
    conn.executescript(
        """
        DROP TABLE IF EXISTS entries;
        DROP TABLE IF EXISTS entries_fts;
        DROP TABLE IF EXISTS links;
        CREATE TABLE entries (
            id TEXT PRIMARY KEY, type TEXT NOT NULL, title TEXT NOT NULL,
            tags TEXT DEFAULT '', source TEXT DEFAULT '',
            status TEXT DEFAULT 'active', supersedes TEXT DEFAULT '',
            confidence TEXT DEFAULT '', created TEXT, updated TEXT,
            path TEXT NOT NULL UNIQUE, body TEXT NOT NULL
        );
        CREATE VIRTUAL TABLE entries_fts USING fts5(
            id, title, tags, body, tokenize='trigram'
        );
        CREATE TABLE links (
            from_id TEXT NOT NULL, to_id TEXT NOT NULL,
            relation TEXT NOT NULL, note TEXT DEFAULT '',
            created TEXT, PRIMARY KEY (from_id, to_id, relation)
        );
        """
    )
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    conn.commit()
    n = rebuild_files(conn, quiet=True)
    if n:
        print(f"[migrate] 检测到旧索引，已从 Markdown 全量重建 {n} 条知识")


def next_id(conn: sqlite3.Connection) -> str:
    year = date.today().year
    prefix = f"KB-{year}-"
    seq = 0
    for row in conn.execute("SELECT id FROM entries"):
        if str(row["id"]).startswith(prefix):
            try:
                seq = max(seq, int(row["id"].rsplit("-", 1)[1]))
            except ValueError:
                pass
    for f in KB_DIR.rglob("KB-*.md"):
        m = re.match(rf"^{prefix}(\d{{4}})", f.stem)
        if m:
            seq = max(seq, int(m.group(1)))
    return f"{prefix}{seq + 1:04d}"


def rel_path(md: Path) -> str:
    try:
        return md.resolve().relative_to(KB_DIR.parent).as_posix()
    except ValueError:
        return md.resolve().relative_to(KB_DIR).as_posix()


def upsert(conn: sqlite3.Connection, md_path: Path, auto_id: bool = False) -> str:
    """索引一条知识文件。auto_id=True 时若缺 id 自动分配并回写文件。"""
    md_path = md_path.resolve()
    if not md_path.exists():
        return f"跳过 {md_path.name}: 文件不存在"
    if KB_DIR.resolve() not in md_path.parents:
        return f"跳过 {md_path.name}: 不在知识库目录 {KB_DIR} 内"

    text = md_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    kb_id = meta.get("id", "")
    if not kb_id and auto_id:
        kb_id = next_id(conn)
        text = text.replace("---\n", f"---\nid: {kb_id}\n", 1)
        md_path.write_text(text, encoding="utf-8")
        meta, body = parse_frontmatter(text)
    if not kb_id:
        return f"跳过 {md_path.name}: 缺少 frontmatter id 字段"

    ktype = meta.get("type", "")
    if ktype not in TYPES:
        return f"跳过 {md_path.name}: type 必须是 {sorted(TYPES)} 之一"
    status = meta.get("status", "active")
    if status not in ALLOWED_STATUS:
        return f"跳过 {md_path.name}: status 必须是 {sorted(ALLOWED_STATUS)} 之一"

    rel = rel_path(md_path)
    old = conn.execute("SELECT created FROM entries WHERE id=?", (kb_id,)).fetchone()
    created = meta.get("created") or (old["created"] if old else today())
    row = (
        kb_id, ktype, meta.get("title", md_path.stem), norm_tags(meta.get("tags", "")),
        meta.get("source", ""), status, meta.get("supersedes", ""),
        meta.get("confidence", ""), created, today(), rel, body.strip(),
    )
    conn.execute("DELETE FROM entries WHERE id=? OR path=?", (kb_id, rel))
    conn.execute("DELETE FROM entries_fts WHERE id=?", (kb_id,))
    conn.execute("INSERT INTO entries VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", row)
    conn.execute(
        "INSERT INTO entries_fts (id,title,tags,body) VALUES (?,?,?,?)",
        (kb_id, row[2], row[3], row[11]),
    )
    # supersedes 关系自动入 links 表
    if row[6]:
        conn.execute(
            "INSERT OR REPLACE INTO links VALUES (?,?,?,?,?)",
            (kb_id, row[6], "supersedes", "frontmatter supersedes 字段", today()),
        )
    conn.commit()
    return f"已索引 {kb_id} [{ktype}] {row[2]} -> {rel}"


# ----------------------------------------------------------------------- 检索


def fts_escape(q: str) -> str:
    return '"' + q.replace('"', '""') + '"'


def build_match(query: str) -> str | None:
    terms = [t for t in re.split(r"[\s,，、;；]+", query) if len(t) >= 3]
    if not terms:
        joined = re.sub(r"\s+", "", query)
        if len(joined) >= 3:
            terms = [joined]
    return " ".join(fts_escape(t) for t in terms) if terms else None


def search_rows(conn: sqlite3.Connection, query: str, limit: int = 10,
                include_all: bool = False) -> list[sqlite3.Row]:
    match = build_match(query)
    if match is None:
        sys.exit("检索失败: 关键词过短（trigram 要求 >= 3 字符），请换更长的词")
    cond = "" if include_all else " AND e.status='active'"
    sql = (
        "SELECT e.*, snippet(entries_fts,3,'【','】','…',16) AS snip, "
        "bm25(entries_fts) AS score "
        "FROM entries_fts f JOIN entries e ON e.id=f.id "
        f"WHERE entries_fts MATCH ?{cond} ORDER BY score LIMIT ?"
    )
    try:
        return conn.execute(sql, (match, limit)).fetchall()
    except sqlite3.OperationalError as ex:
        sys.exit(f"检索失败: {ex}")


def print_hits(rows: list[sqlite3.Row]) -> None:
    for r in rows:
        print(f"[{r['id']}] ({r['type']}/{r['status']}) {r['title']}  tags={r['tags']}")
        print(f"    {r['snip']}")
        print(f"    -> {r['path']}  (score={r['score']:.2f})")


def check_duplicates(conn: sqlite3.Connection, title: str, exclude_id: str = "") -> None:
    """Mem0 式写前查重：save 时自动提示高相似条目。"""
    match = build_match(title)
    if not match:
        return
    rows = conn.execute(
        "SELECT e.id,e.title,e.status,bm25(entries_fts) s FROM entries_fts f "
        "JOIN entries e ON e.id=f.id WHERE entries_fts MATCH ? AND e.id<>? "
        "ORDER BY s LIMIT 3",
        (match, exclude_id),
    ).fetchall()
    for r in rows:
        if r["s"] < -1.5:  # bm25 越小越相关
            print(f"[查重提醒] 与 {r['id']}《{r['title']}》(status={r['status']}) 高度相似，"
                  f"请确认是更新还是新建")


# ------------------------------------------------------------------ 文本知识识别

CUES: dict[str, list[str]] = {
    "workflow": [
        "流程", "步骤", "操作", "如何", "怎么", "首先", "然后", "接着", "最后", "配置",
        "部署", "安装", "执行", "运行", "命令", "脚本", "使用方法", "SOP", "手册",
        "step", "workflow", "run ", "install", "deploy", "usage", "how to",
    ],
    "business": [
        "业务", "规则", "客户", "产品", "指标", "口径", "阈值", "计费", "结算", "审批",
        "合规", "需求", "范围", "KPI", "业务流程", "账期", "额度", "税率", "政策",
        "shall", "must", "business rule", "policy",
    ],
    "lesson": [
        "问题", "报错", "错误", "异常", "失败", "踩坑", "坑", "原因", "解决", "修复",
        "教训", "注意", "避免", "没想到", "结果发现", "error", "failed", "bug", "fix",
    ],
    "decision": [
        "决定", "决策", "选型", "采用", "否决", "选择了", "选择", "方案", "权衡", "取舍",
        "结论", "对比", "ADR", "decided", "choose", "trade-off",
    ],
    "entity": [
        "是一个", "指的是", "成立", "注册", "地址", "负责人", "团队", "组织", "部门",
        "官网", "架构师", "供应商", "is a", "located", "belongs to",
    ],
}


def iter_blocks(text: str):
    """按空行切块；代码块保持完整。返回 (起始行号, 块文本)。"""
    lines = text.splitlines()
    blocks, cur, start, in_code = [], [], 0, False
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith("```"):
            in_code = not in_code
            cur.append(line)
            continue
        if not in_code and not s:
            if cur:
                blocks.append((start, "\n".join(cur)))
                cur = []
            continue
        if not cur:
            start = i
        cur.append(line)
    if cur:
        blocks.append((start, "\n".join(cur)))
    return blocks


def guess_title(block: str) -> str:
    for ln in block.splitlines():
        s = re.sub(
            r"^[#>\s\-*•]+|^#{1,6}\s*|^\d+[.)、\s]+|^[（(][一二三四五六七八九十0-9]+[)）]\s*",
            "", ln.strip(),
        )
        if s:
            return s[:48] + ("…" if len(s) > 48 else "")
    return "(未命名)"


def classify(block: str) -> tuple[str, list[str], str]:
    """规则引擎识别知识类型；返回 (类型, 命中线索, 置信度)。"""
    low = block.lower()
    scores, hits = {}, {}
    for t, words in CUES.items():
        hits[t] = [w for w in words if w in low]
        scores[t] = len(hits[t])
    best = max(scores, key=lambda k: scores[k])
    if scores[best] == 0:
        return "domain", [], "low"
    conf = "high" if scores[best] >= 3 else ("medium" if scores[best] == 2 else "low")
    return best, hits[best], conf


def scan_text(text: str, source: str = "-") -> list[dict]:
    """识别文本中的业务知识/工作知识等候选块。只识别不落盘，Agent 审核后 save。"""
    out = []
    for start, block in iter_blocks(text):
        if len(block.strip()) < 12:
            continue
        ktype, cues, conf = classify(block)
        end = start + len(block.splitlines()) - 1
        out.append({
            "type": ktype,
            "title": guess_title(block),
            "text": block,
            "lines": f"L{start}-{end}",
            "cues": cues,
            "confidence": conf,
            "source": f"{source} L{start}-{end}",
        })
    return out


def render_candidate_md(c: dict, kb_id: str) -> str:
    return (
        "---\n"
        f"id: {kb_id}\n"
        f"type: {c['type']}\n"
        f"title: {c['title']}\n"
        "tags: []\n"
        f"source: {c['source']}\n"
        f"created: {today()}\n"
        "status: active\n"
        "supersedes: \"\"\n"
        f"confidence: {c['confidence']}\n"
        "---\n\n"
        "## 内容\n\n"
        f"{c['text']}\n\n"
        "## 适用场景\n\n(待补充：什么情况下应使用本条知识)\n"
    )


# ---------------------------------------------------------------- INDEX.md 生成


def render_index(conn: sqlite3.Connection) -> None:
    """L1 索引自动生成——修复 v1 手工维护导致的索引漂移问题。"""
    rows = conn.execute(
        "SELECT id,type,title,tags,status,updated,path FROM entries ORDER BY type,id"
    ).fetchall()
    by_type: dict[str, list[sqlite3.Row]] = {}
    for r in rows:
        by_type.setdefault(r["type"], []).append(r)
    n_active = sum(1 for r in rows if r["status"] == "active")
    desc = {
        "business": "业务规则、产品口径、指标定义、业务流程等领域事实",
        "workflow": "操作流程、工具用法、命令、配置、SOP 等工作方法",
        "decision": "技术/方案选型决策（ADR 风格），含理由与取舍",
        "lesson": "踩坑、调试结论、验证过的解决方案",
        "entity": "项目、工具、人物、组织等实体结构化卡片",
        "domain": "暂未细分的一般领域知识",
    }
    lines = [
        "# AISI 项目知识库索引",
        "",
        "> ⚠️ 本文件由 kb.py 自动生成（save/rebuild 时同步刷新），请勿手工编辑。",
        f"> 最后更新：{today()} ｜ 总条目 {len(rows)} ｜ active {n_active}",
        "",
        "## 使用说明",
        "",
        "- 检索：`kb.py search \"关键词\"`（中文友好，关键词 >= 3 字符）",
        "- 写入：先 `kb.py scan <文本>` 识别候选 → Agent 规范化 → `kb.py save <文件>`",
        "- 重建：`kb.py rebuild`（INDEX.md 同时刷新）",
        "",
    ]
    for t, (d, zh) in TYPES.items():
        lines += [f"## {d}/ — {zh}", "", f"{zh}。{desc[t]}", "",
                  "| ID | 标题 | 标签 | 状态 | 更新 | 文件 |",
                  "| -- | ---- | ---- | ---- | ---- | ---- |"]
        items = by_type.get(t, [])
        if items:
            lines += [
                f"| {r['id']} | {r['title']} | {r['tags']} | {r['status']} "
                f"| {r['updated']} | {r['path']} |" for r in items
            ]
        else:
            lines.append("| （暂无） | | | | | |")
        lines.append("")
    INDEX_PATH.write_text("\n".join(lines), encoding="utf-8")


def rebuild_files(conn: sqlite3.Connection, quiet: bool = False) -> int:
    conn.execute("DELETE FROM entries")
    conn.execute("DELETE FROM entries_fts")
    conn.commit()
    n = 0
    for md in sorted(KB_DIR.rglob("*.md")):
        if md.name == "INDEX.md":
            continue
        msg = upsert(conn, md, auto_id=True)
        if not quiet:
            print(msg)
        if msg.startswith("已索引"):
            n += 1
    render_index(conn)
    return n


# ---------------------------------------------------------------------- CLI


def cmd_scan(args) -> None:
    if args.file == "-":
        text, src = sys.stdin.read(), "stdin"
    else:
        p = Path(args.file)
        if not p.exists():
            sys.exit(f"错误: 文件不存在 {p}")
        text, src = p.read_text(encoding="utf-8"), p.name
    cands = scan_text(text, src)
    if not cands:
        print("未识别出知识候选块")
        return
    if not args.save:
        print(json.dumps({"file": src, "candidates": cands}, ensure_ascii=False, indent=2))
        return
    conn = connect()
    saved = []
    for c in cands:
        kb_id = next_id(conn)
        d = TYPES[c["type"]][0]
        fname = KB_DIR / d / f"{kb_id}-{slugify(c['title'])}.md"
        fname.write_text(render_candidate_md(c, kb_id), encoding="utf-8")
        msg = upsert(conn, fname)
        print(msg)
        saved.append(kb_id)
    render_index(conn)
    conn.close()
    print(f"已保存 {len(saved)} 条候选知识: {', '.join(saved)}（请复核标题与分类）")


def cmd_save(args) -> None:
    conn = connect()
    for f in args.files:
        p = Path(f)
        meta = {}
        if p.exists():
            meta, _ = parse_frontmatter(p.read_text(encoding="utf-8"))
        print(upsert(conn, p, auto_id=True))
        if meta.get("title"):
            check_duplicates(conn, meta["title"], meta.get("id", ""))
    render_index(conn)
    conn.close()


def cmd_search(args) -> None:
    conn = connect()
    rows = search_rows(conn, args.query, args.n, args.all)
    if not rows:
        print("未命中任何知识。可换更长关键词，或 `kb.py list` 浏览全部条目。")
    print_hits(rows)
    conn.close()


def cmd_get(args) -> None:
    conn = connect()
    r = conn.execute("SELECT * FROM entries WHERE id=?", (args.id,)).fetchone()
    if not r:
        sys.exit(f"错误: 未找到 {args.id}")
    fp = KB_DIR.parent / r["path"]
    if not fp.exists():
        fp = KB_DIR / r["path"]
    print(fp.read_text(encoding="utf-8"))
    links = conn.execute(
        "SELECT * FROM links WHERE from_id=? OR to_id=? ORDER BY relation",
        (args.id, args.id),
    ).fetchall()
    if links:
        print("\n## 关系")
        for l in links:
            other = l["to_id"] if l["from_id"] == args.id else l["from_id"]
            arrow = "->" if l["from_id"] == args.id else "<-"
            print(f"- {args.id} {arrow} [{l['relation']}] {other}  {l['note']}")
    conn.close()


def cmd_list(args) -> None:
    conn = connect()
    sql, params = "SELECT id,type,title,status,path FROM entries", []
    if args.type:
        sql += " WHERE type=?"
        params.append(args.type)
        if not args.all:
            sql += " AND status='active'"
    elif not args.all:
        sql += " WHERE status='active'"
    for r in conn.execute(sql + " ORDER BY id", params):
        print(f"[{r['id']}] ({r['type']}/{r['status']}) {r['title']}  -> {r['path']}")
    conn.close()


def cmd_stats(args) -> None:
    conn = connect()
    rows = conn.execute("SELECT type,status,tags FROM entries").fetchall()
    if not rows:
        print("知识库为空")
        conn.close()
        return
    print("按类型:")
    for k, v in Counter(r["type"] for r in rows).most_common():
        print(f"  {TYPES.get(k, (None, k))[1]:<8} {v}")
    print("按状态:")
    for k, v in Counter(r["status"] for r in rows).most_common():
        print(f"  {k:<10} {v}")
    tags = Counter(t for r in rows for t in r["tags"].split(",") if t)
    if tags:
        print("高频标签:")
        for k, v in tags.most_common(10):
            print(f"  {k:<16} {v}")
    conn.close()


def cmd_link(args) -> None:
    if args.relation not in RELATIONS:
        sys.exit(f"错误: 关系必须是 {sorted(RELATIONS)} 之一")
    conn = connect()
    for i in (args.src, args.dst):
        if not conn.execute("SELECT 1 FROM entries WHERE id=?", (i,)).fetchone():
            sys.exit(f"错误: 未找到 {i}")
    conn.execute(
        "INSERT OR REPLACE INTO links VALUES (?,?,?,?,?)",
        (args.src, args.dst, args.relation, args.note, today()),
    )
    conn.commit()
    print(f"已建立关系: {args.src} -[{args.relation}]-> {args.dst}")
    conn.close()


def cmd_similar(args) -> None:
    conn = connect()
    r = conn.execute("SELECT id,title FROM entries WHERE id=?", (args.id,)).fetchone()
    title = r["title"] if r else args.id
    rows = search_rows(conn, title, 5, include_all=True)
    rows = [x for x in rows if x["id"] != (r["id"] if r else "")]
    if not rows:
        print("无相似条目")
    print_hits(rows)
    conn.close()


def cmd_rebuild(args) -> None:
    conn = connect()
    n = rebuild_files(conn)
    render_index(conn)
    print(f"重建完成，共索引 {n} 条知识，INDEX.md 已刷新")
    conn.close()


def cmd_init(args) -> None:
    conn = connect()
    render_index(conn)
    print(f"知识库已就绪: {KB_DIR}")
    print(f"  索引文件: {INDEX_PATH}")
    print(f"  检索数据库: {DB_PATH}")
    conn.close()


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="AISI Agent 知识库（本体 md + SQLite FTS5）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="初始化目录结构与 INDEX.md")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("scan", help="识别文本中的知识候选（业务/工作/决策/教训/实体）")
    p.add_argument("file", help="文本文件路径，- 表示 stdin")
    p.add_argument("--save", action="store_true", help="识别后直接入库（默认仅输出 JSON 预览）")
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("save", aliases=["add"], help="索引知识文件（缺 id 自动分配）")
    p.add_argument("files", nargs="+")
    p.set_defaults(func=cmd_save)

    p = sub.add_parser("search", help="全文检索（trigram 中文友好）")
    p.add_argument("query")
    p.add_argument("-n", type=int, default=10)
    p.add_argument("--all", action="store_true", help="包含 superseded/outdated")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("get", help="读取某条知识全文及其关系")
    p.add_argument("id")
    p.set_defaults(func=cmd_get)

    p = sub.add_parser("list", help="列出已索引条目")
    p.add_argument("type", nargs="?", choices=sorted(TYPES))
    p.add_argument("--all", action="store_true")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("stats", help="分类/状态/标签统计").set_defaults(func=cmd_stats)

    p = sub.add_parser("link", help="建立知识间关系")
    p.add_argument("src")
    p.add_argument("dst")
    p.add_argument("relation")
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_link)

    p = sub.add_parser("similar", help="查重：找相似条目")
    p.add_argument("id", help="KB-ID 或标题文本")
    p.set_defaults(func=cmd_similar)

    p = sub.add_parser("rebuild", help="全量重建索引并刷新 INDEX.md").set_defaults(func=cmd_rebuild)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
