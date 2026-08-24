"""证据缺口分析：需求 ↔ 来源索引 交叉核对，产出 research/gaps.json。"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .ingest import load_index


def analyze(ws, view: str = "requirements") -> dict:
    gaps = []
    index = load_index(ws)
    src_ids = {s["id"] for s in index["sources"]}
    findings_p = ws.base / "research" / "findings.json"
    if findings_p.exists():
        try:
            findings = json.loads(findings_p.read_text(encoding="utf-8"))
            src_ids |= {s["id"] for s in findings.get("sources", [])}
        except json.JSONDecodeError:
            pass
    if not src_ids:
        gaps.append({"kind": "NO_SOURCES_INGESTED", "severity": "high", "target": view,
                     "detail": "工作区尚未登记任何资料来源",
                     "question_hint": "请先 aisi ingest 资料，或由宿主抓取 URL 后回填"})
    reqs = (ws.view_data(view) or {}).get("requirements", [])
    for r in reqs:
        refs = r.get("source_refs", [])
        if not refs:
            gaps.append({"kind": "NO_SOURCE", "severity": "medium",
                         "target": r["id"],
                         "detail": f"{r['id']}《{r['name']}》无 source_refs",
                         "question_hint": f"确认 {r['id']} 是否为用户新增决策，或补充资料来源"})
        for ref in refs:
            sid = ref.split("#")[0]
            if sid not in src_ids:
                gaps.append({"kind": "UNRESOLVED_SOURCE", "severity": "high", "target": r["id"],
                             "detail": f"{r['id']} 引用的来源 {sid} 未入库",
                             "question_hint": f"提供 {sid} 对应资料并 ingest，或修正 {r['id']} 的 source_refs"})
        for c in r.get("clarifications", []):
            if not c.get("answer"):
                gaps.append({"kind": "OPEN_CLARIFICATION", "severity": "medium", "target": r["id"],
                             "detail": f"{r['id']} 待澄清：{c['question']}",
                             "question_hint": c["question"]})
        if r.get("type") == "performance" and not r.get("measures"):
            gaps.append({"kind": "MISSING_MEASURE", "severity": "medium", "target": r["id"],
                         "detail": f"性能类需求 {r['id']}《{r['name']}》缺少量化指标 measures",
                         "question_hint": f"调研行业典型值或与用户确认 {r['id']} 的量化指标（数值+单位+条件）"})
    sev = {"high": 0, "medium": 0, "low": 0}
    for g in gaps:
        sev[g["severity"]] += 1
    return {"schema": "aisi.gaps/1", "view": view, "system_id": ws.manifest["system_id"],
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "summary": {"total": len(gaps), "high": sev["high"],
                        "medium": sev["medium"], "low": sev["low"]},
            "gaps": gaps}
