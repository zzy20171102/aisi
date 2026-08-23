"""四视图追踪矩阵生成：REQ↔MOD↔LAY↔STEP↔DF/IF 全链路追踪。"""
from __future__ import annotations

from datetime import datetime


def build_edges(ws) -> list[dict]:
    edges: list[dict] = []

    def add(frm, to, rel, ev):
        e = {"from": frm, "to": to, "relation": rel, "evidence": ev}
        if e not in edges:
            edges.append(e)

    comp = ws.view_data("composition") or {}
    for m in comp.get("modules", []):
        for r in m.get("requirements", []):
            add(r, m["id"], "satisfy", f"{m['id']}.requirements")
        if m.get("layer"):
            add(m["id"], m["layer"], "allocate", f"{m['id']}.layer")
    arch = ws.view_data("architecture") or {}
    for l in arch.get("layers", []):
        for mod in l.get("modules", []):
            add(mod, l["id"], "allocate", f"{l['id']}.modules")
    for s in arch.get("services", []):
        add(s["id"], s["module"], "connects", f"{s['id']}.module")
    proc = ws.view_data("processes") or {}
    for p in proc.get("processes", []):
        for st in p.get("steps", []):
            if st.get("module"):
                add(f"{p['id']}.{st['id']}", st["module"], "executes", f"{p['id']} 步骤执行模块")
    for df in proc.get("dataflows", []):
        add(df["from"], df["to"], "connects", f"{df['id']}:{df['payload']}")
    for itf in proc.get("interfaces", []):
        for c in itf.get("consumers", []):
            add(itf["provider"], c, "connects", f"{itf['id']}:{itf['name']}")
    return edges


def analyze(ws, edges: list[dict]) -> dict:
    reqs = [r["id"] for r in (ws.view_data("requirements") or {}).get("requirements", [])]
    comp = ws.view_data("composition") or {}
    mods = [m["id"] for m in comp.get("modules", [])]
    layers = [l["id"] for l in (ws.view_data("architecture") or {}).get("layers", [])]
    sat = {e["to"] for e in edges if e["relation"] == "satisfy"}
    mods_sat = {e["from"] for e in edges if e["relation"] == "satisfy"}
    alloc = {e["from"] for e in edges if e["relation"] == "allocate"}
    lay_alloc = {e["to"] for e in edges if e["relation"] == "allocate"}
    return {
        "orphan_requirements": [r for r in reqs if r not in mods_sat],
        "modules_without_requirements": [m for m in mods if m not in sat and m != "MOD-00"],
        "modules_without_layer": [m for m in mods if m not in alloc],
        "layers_without_modules": [l for l in layers if l not in lay_alloc],
        "counts": {"requirements": len(reqs), "modules": len(mods),
                   "layers": len(layers), "edges": len(edges)},
    }


def render_markdown(ws, edges: list[dict], issues: dict) -> str:
    rel_zh = {"satisfy": "实现", "allocate": "部署于", "executes": "执行",
              "connects": "连接", "refine": "细化"}
    by_from: dict[str, list[dict]] = {}
    for e in edges:
        by_from.setdefault(e["from"], []).append(e)
    lines = [f"# {ws.manifest['name']} 四视图追踪矩阵", "",
             f"> 生成时间：{datetime.now().isoformat(timespec='seconds')} ｜ 边总数：{len(edges)}", "",
             "## 追踪概览", "",
             f"- 需求 {issues['counts']['requirements']} 条 ｜ 模块 {issues['counts']['modules']} 个 ｜ "
             f"架构层 {issues['counts']['layers']} 层",
             f"- 追踪边 {issues['counts']['edges']} 条"]
    for k, zh in (("orphan_requirements", "孤儿需求（无模块承载）"),
                  ("modules_without_requirements", "空模块（无承载需求）"),
                  ("modules_without_layer", "未分层模块"),
                  ("layers_without_modules", "空架构层")):
        v = issues[k]
        detail = f"（{', '.join(v[:10])}{'…' if len(v) > 10 else ''}）" if v else ""
        lines.append(f"- {zh}：{len(v)}{detail}")
    lines += ["", "## 需求 → 模块（satisfy）", "", "| 需求 | 模块 |", "|---|---|"]
    for r in (ws.view_data("requirements") or {}).get("requirements", []):
        ms = sorted({e["to"] for e in by_from.get(r["id"], []) if e["relation"] == "satisfy"})
        lines.append(f"| {r['id']} {r['name']} | {', '.join(ms) or '⚠ 无'} |")
    lines += ["", "## 模块 → 架构层（allocate）", "", "| 模块 | 架构层 |", "|---|---|"]
    for m in (ws.view_data("composition") or {}).get("modules", []):
        ls = sorted({e["to"] for e in by_from.get(m["id"], []) if e["relation"] == "allocate"})
        lines.append(f"| {m['id']} {m['name']} | {', '.join(ls) or '⚠ 无'} |")
    lines += ["", "## 流程步骤 → 模块（executes）", "", "| 流程步骤 | 模块 |", "|---|---|"]
    for p in (ws.view_data("processes") or {}).get("processes", []):
        for st in p.get("steps", []):
            es = by_from.get(f"{p['id']}.{st['id']}", [])
            lines.append(f"| {p['id']}.{st['id']} {st['action'][:24]} | "
                         f"{', '.join(sorted({e['to'] for e in es})) or '⚠ 无'} |")
    lines += ["", "## 全部追踪边", "", "| 源 | 关系 | 目标 | 证据 |", "|---|---|---|---|"]
    for e in edges:
        lines.append(f"| {e['from']} | {rel_zh[e['relation']]} | {e['to']} | {e['evidence']} |")
    return "\n".join(lines) + "\n"
