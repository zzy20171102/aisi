"""语义 lint：跨条目与跨视图一致性检查（error 阻断 validated，warning 不阻断）。"""
from __future__ import annotations

import json
from pathlib import Path


def issue(sev: str, code: str, path: str, msg: str, fix: str = "") -> dict:
    return {"severity": sev, "code": code, "path": path, "message": msg, "suggestion": fix}


def _load_view(ws_path: Path, view: str):
    p = ws_path / "views" / f"{view}.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return None


def _cycle(ids_parents: dict[str, str]) -> str | None:
    for start in ids_parents:
        seen, cur = set(), start
        while cur and cur in ids_parents:
            if cur in seen:
                return start
            seen.add(cur)
            cur = ids_parents[cur]
    return None


def lint(view: str, data: dict, ws_path: Path) -> list[dict]:
    other = {v: _load_view(ws_path, v) for v in
             ("requirements", "composition", "architecture", "processes")}
    fn = {"requirements": _req, "composition": _comp,
          "architecture": _arch, "processes": _proc}[view]
    return fn(data, other)


def _req(d, other) -> list[dict]:
    out, items = [], d.get("requirements", [])
    ids = [r["id"] for r in items]
    for i in ids:
        if ids.count(i) > 1:
            out.append(issue("error", "REQ_DUP", i, f"需求编号 {i} 重复"))
    parents = {r["id"]: r.get("parent", "") for r in items}
    for r in items:
        p = r.get("parent", "")
        if p == r["id"]:
            out.append(issue("error", "SELF_PARENT", r["id"], "父需求不能是自身"))
        elif p and p not in ids:
            out.append(issue("error", "PARENT_MISSING", r["id"], f"父需求 {p} 不存在"))
        if not r.get("source_refs"):
            out.append(issue("warning", "NO_SOURCE", r["id"], "无资料来源（source_refs 为空）",
                             "补充 source_refs 或在 rationale 说明为用户新增"))
        for a in r.get("allocations", []):
            comp = other.get("composition")
            if comp:
                mod_ids = [m["id"] for m in comp.get("modules", [])]
                if a["module_id"] not in mod_ids:
                    out.append(issue("error", "CROSS_REF", f"{r['id']}.allocations",
                                     f"模块 {a['module_id']} 不在组成视图中"))
            else:
                out.append(issue("warning", "CROSS_VIEW_UNAVAILABLE", f"{r['id']}.allocations",
                                 "组成视图尚未创建，跨视图引用暂未校验"))
        for ref in r.get("interfaces", []):
            proc = other.get("processes")
            if proc and ref not in [x["id"] for x in proc.get("interfaces", [])]:
                out.append(issue("warning", "CROSS_REF", f"{r['id']}.interfaces",
                                 f"接口 {ref} 未在流程视图中定义"))
    c = _cycle(parents)
    if c:
        out.append(issue("error", "PARENT_CYCLE", c, "父需求链存在环"))
    return out


def _comp(d, other) -> list[dict]:
    out, items = [], d.get("modules", [])
    ids = [m["id"] for m in items]
    if "MOD-00" not in ids:
        out.append(issue("error", "ROOT_MISSING", "modules", "缺少系统根模块 MOD-00"))
    for i in ids:
        if ids.count(i) > 1:
            out.append(issue("error", "MOD_DUP", i, f"模块编号 {i} 重复"))
    parents = {m["id"]: m.get("parent", "") for m in items}
    for m in items:
        p = m.get("parent", "")
        if p == m["id"]:
            out.append(issue("error", "SELF_PARENT", m["id"], "父模块不能是自身"))
        elif p and p not in ids:
            out.append(issue("error", "PARENT_MISSING", m["id"], f"父模块 {p} 不存在"))
        for ref in m.get("requirements", []):
            req = other.get("requirements")
            if req:
                if ref not in [x["id"] for x in req.get("requirements", [])]:
                    out.append(issue("warning", "CROSS_REF", f"{m['id']}.requirements",
                                     f"需求 {ref} 不在需求视图"))
            else:
                out.append(issue("warning", "CROSS_VIEW_UNAVAILABLE", f"{m['id']}.requirements",
                                 "需求视图尚未创建，跨视图引用暂未校验"))
        lay = m.get("layer", "")
        if lay:
            arch = other.get("architecture")
            if arch:
                if lay not in [x["id"] for x in arch.get("layers", [])]:
                    out.append(issue("error", "CROSS_REF", f"{m['id']}.layer",
                                     f"架构层 {lay} 不存在"))
            else:
                out.append(issue("warning", "CROSS_VIEW_UNAVAILABLE", f"{m['id']}.layer",
                                 "架构视图尚未创建，跨视图引用暂未校验"))
    roots = [m["id"] for m in items if not m.get("parent")]
    if len(roots) > 1:
        out.append(issue("warning", "MULTI_ROOT", ",".join(roots),
                         f"存在 {len(roots)} 个根模块", "仅保留 MOD-00 作为根"))
    c = _cycle(parents)
    if c:
        out.append(issue("error", "PARENT_CYCLE", c, "模块包含链存在环"))
    return out


def _arch(d, other) -> list[dict]:
    out = []
    layers = d.get("layers", [])
    lay_ids = [l["id"] for l in layers]
    for i in lay_ids:
        if lay_ids.count(i) > 1:
            out.append(issue("error", "LAY_DUP", i, f"架构层编号 {i} 重复"))
    orders = [l["order"] for l in layers]
    if len(set(orders)) != len(orders):
        out.append(issue("warning", "ORDER_DUP", "layers", "order 存在重复值"))
    comp = other.get("composition")
    mod_ids = [m["id"] for m in comp.get("modules", [])] if comp else None
    for l in layers:
        for ref in l.get("modules", []):
            if mod_ids is None:
                out.append(issue("warning", "CROSS_VIEW_UNAVAILABLE", f"{l['id']}.modules",
                                 "组成视图尚未创建，跨视图引用暂未校验"))
            elif ref not in mod_ids:
                out.append(issue("error", "CROSS_REF", f"{l['id']}.modules",
                                 f"模块 {ref} 不在组成视图"))
    svc_ids = [s["id"] for s in d.get("services", [])]
    for i in svc_ids:
        if svc_ids.count(i) > 1:
            out.append(issue("error", "SVC_DUP", i, f"服务编号 {i} 重复"))
    for s in d.get("services", []):
        if mod_ids is None:
            out.append(issue("warning", "CROSS_VIEW_UNAVAILABLE", f"{s['id']}.module",
                             "组成视图尚未创建，跨视图引用暂未校验"))
        elif s["module"] not in mod_ids:
            out.append(issue("error", "CROSS_REF", f"{s['id']}.module",
                             f"模块 {s['module']} 不在组成视图"))
    da_ids = [a["id"] for a in d.get("data_assets", [])]
    for i in da_ids:
        if da_ids.count(i) > 1:
            out.append(issue("error", "DA_DUP", i, f"数据资产编号 {i} 重复"))
    for a in d.get("data_assets", []):
        if mod_ids is not None and a["owner_module"] not in mod_ids:
            out.append(issue("error", "CROSS_REF", f"{a['id']}.owner_module",
                             f"模块 {a['owner_module']} 不在组成视图"))
    for n in d.get("deploy_nodes", []):
        for h in n.get("hosts", []):
            if svc_ids and h not in svc_ids:
                out.append(issue("warning", "CROSS_REF", f"{n['id']}.hosts",
                                 f"部署服务 {h} 未在 services 中定义"))
    return out


def _proc(d, other) -> list[dict]:
    out = []
    procs = d.get("processes", [])
    prc_ids = [p["id"] for p in procs]
    for i in prc_ids:
        if prc_ids.count(i) > 1:
            out.append(issue("error", "PRC_DUP", i, f"流程编号 {i} 重复"))
    comp = other.get("composition")
    mod_ids = [m["id"] for m in comp.get("modules", [])] if comp else None
    if_ids = [x["id"] for x in d.get("interfaces", [])]
    for i in if_ids:
        if if_ids.count(i) > 1:
            out.append(issue("error", "IF_DUP", i, f"接口编号 {i} 重复"))
    for p in procs:
        steps = p.get("steps", [])
        sids = [s["id"] for s in steps]
        for i in sids:
            if sids.count(i) > 1:
                out.append(issue("error", "STEP_DUP", f"{p['id']}.{i}", "步骤编号在流程内重复"))
        has_end = False
        for s in steps:
            for nxt in s.get("next", []):
                if nxt == "END":
                    has_end = True
                elif nxt not in sids:
                    out.append(issue("error", "NEXT_MISSING", f"{p['id']}.{s['id']}.next",
                                     f"后续步骤 {nxt} 不存在"))
            if not s.get("module"):
                out.append(issue("warning", "STEP_NO_MODULE", f"{p['id']}.{s['id']}",
                                 "步骤未关联执行模块", "补充 module 字段以进入追踪矩阵"))
            elif mod_ids is not None and s["module"] not in mod_ids:
                out.append(issue("error", "CROSS_REF", f"{p['id']}.{s['id']}.module",
                                 f"模块 {s['module']} 不在组成视图"))
        if steps and not has_end:
            out.append(issue("warning", "NO_END", p["id"], "流程无 END 终止步骤"))
    for df in d.get("dataflows", []):
        for end in (df["from"], df["to"]):
            if mod_ids is not None and end not in mod_ids:
                out.append(issue("warning", "CROSS_REF", df["id"],
                                 f"数据流端点 {end} 不在组成视图"))
        if df.get("interface") and if_ids and df["interface"] not in if_ids:
            out.append(issue("warning", "CROSS_REF", f"{df['id']}.interface",
                             f"接口 {df['interface']} 未定义"))
    for itf in d.get("interfaces", []):
        if not itf.get("consumers"):
            out.append(issue("warning", "IF_NO_CONSUMER", itf["id"], "接口无消费方"))
    return out
