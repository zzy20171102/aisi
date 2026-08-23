"""SysML v2 导出器：四视图 → requirements/composition/architecture/processes .sysml。"""
from __future__ import annotations

import re


def camel(text: str) -> str:
    parts = re.split(r"[-_\s]+", text)
    return "".join(p[:1].upper() + p[1:] for p in parts if p) or "System"


def ident_req(rid: str) -> str:
    return rid.lower().replace("-", "").replace(".", "_")


def ident_mod(mid: str) -> str:
    return "Mod" + mid.split("-")[1]


def check_balance(text: str) -> list[str]:
    errs = []
    if text.count("{") != text.count("}"):
        errs.append(f"大括号不配对: {{={text.count('{')} }}={text.count('}')}")
    if text.count("/*") != text.count("*/"):
        errs.append("doc 注释不配对")
    return errs


def export_requirements(ws) -> str:
    pkg = camel(ws.manifest["system_id"]) + "Requirements"
    reqs = (ws.view_data("requirements") or {}).get("requirements", [])
    by_parent: dict[str, list[dict]] = {"": []}
    for r in reqs:
        by_parent.setdefault(r.get("parent", ""), []).append(r)

    def emit(r, indent) -> list[str]:
        pad = "    " * indent
        attrs = [f"type={r['type']}", f"priority={r['priority']}",
                 f"verification={r['verification']}", f"status={r['status']}"]
        if r.get("measures"):
            for m in r["measures"]:
                attrs.append(f"{m['metric']}={m['value']}{m.get('unit', '')}")
        lines = [f"{pad}requirement <'{r['id']}'> {ident_req(r['id'])} {{",
                 f"{pad}    doc /* {r['id']} {r['name']}：{r['text']} */",
                 f"{pad}    // 属性：{' ｜ '.join(attrs)}"]
        if r.get("source_refs"):
            lines.append(f"{pad}    // 来源：{', '.join(r['source_refs'])}")
        for c in r.get("clarifications", []):
            lines.append(f"{pad}    // 待澄清：{c['question']}"
                         + (f"（已答复：{c.get('answer', '')}）" if c.get("answer") else "（待答复）"))
        for child in by_parent.get(r["id"], []):
            lines += emit(child, indent + 1)
        lines.append(f"{pad}}}")
        return lines

    body = []
    for r in by_parent[""]:
        body += emit(r, 1)
    return f"package {pkg} {{\n" + "\n".join(body) + "\n}\n"


def export_composition(ws) -> str:
    pkg = camel(ws.manifest["system_id"]) + "Composition"
    mods = (ws.view_data("composition") or {}).get("modules", [])
    children: dict[str, list[dict]] = {}
    for m in mods:
        children.setdefault(m.get("parent", ""), []).append(m)
    lines = [f"package {pkg} {{"]
    for m in mods:
        lines.append(f"    part def {ident_mod(m['id'])} {{")
        lines.append(f"        doc /* {m['id']} {m['name']}（{m['kind']}）："
                     f"{'；'.join(m.get('responsibilities', [])[:4])} */")
        if m.get("notes"):
            lines.append(f"        // {m['notes']}")
        for c in children.get(m["id"], []):
            lines.append(f"        part {ident_mod(c['id']).lower()}: {ident_mod(c['id'])};"
                         f"  // {c['name']}")
        lines.append("    }")
    lines.append("}")
    return "\n".join(lines) + "\n"


def export_architecture(ws) -> str:
    pkg = camel(ws.manifest["system_id"]) + "Architecture"
    arch = ws.view_data("architecture") or {}
    lines = [f"package {pkg} {{"]
    for l in sorted(arch.get("layers", []), key=lambda x: x["order"]):
        lines.append(f"    package {camel(l['id'] + l['name'])} {{")
        lines.append(f"        doc /* {l['id']} {l['name']}（第{l['order']}层）：{l.get('description', '')} */")
        lines.append(f"        // 技术栈：{', '.join(l.get('technologies', []))}")
        for mod in l.get("modules", []):
            lines.append(f"        // allocate: {mod}")
        lines.append("    }")
    for s in arch.get("services", []):
        lines.append(f"    // service {s['id']} {s['name']}（{s['kind']}）挂载 {s['module']}"
                     f"：{s.get('api', '')}")
    for da in arch.get("data_assets", []):
        lines.append(f"    item def {da['id'].replace('-', '').lower()} {{")
        lines.append(f"        doc /* {da['id']} {da['name']}：{', '.join(da.get('entities', []))}"
                     f"（{da.get('store', '')}，归属 {da['owner_module']}，"
                     f"敏感级 {da.get('sensitivity', '')}） */")
        lines.append("    }")
    for n in arch.get("deploy_nodes", []):
        lines.append(f"    // deploy {n['id']} {n['name']}：{n.get('spec', '')}"
                     f"（承载 {', '.join(n.get('hosts', [])) or '客户端'}）")
    lines.append("}")
    return "\n".join(lines) + "\n"


def export_processes(ws) -> str:
    pkg = camel(ws.manifest["system_id"]) + "Processes"
    proc = ws.view_data("processes") or {}
    lines = [f"package {pkg} {{"]
    for p in proc.get("processes", []):
        pid = ident_req(p["id"])
        lines.append(f"    action def {pid} {{")
        lines.append(f"        doc /* {p['id']} {p['name']}：触发={p.get('trigger', '')}，"
                     f"参与者={', '.join(p.get('actors', []))} */")
        for s in p.get("steps", []):
            lines.append(f"        action S{s['id'][1:]} {{")
            lines.append(f"            doc /* {s['id']} [{s['actor']}] {s['action']} */")
            if s.get("module"):
                lines.append(f"            // executes: {s['module']}")
            if s.get("exceptions"):
                lines.append(f"            // 异常：{'；'.join(s['exceptions'])}")
            lines.append("        }")
        for s in p.get("steps", []):
            for nxt in s.get("next", []):
                if nxt != "END":
                    lines.append(f"        first S{s['id'][1:]} then S{nxt[1:]};")
                else:
                    lines.append(f"        // S{s['id'][1:]} -> END")
        lines.append("    }")
    for itf in proc.get("interfaces", []):
        msgs = "；".join(f"{m['name']}({m['direction']}: {', '.join(m['fields'])})"
                         for m in itf.get("messages", []))
        lines.append(f"    // interface {itf['id']} {itf['name']}：{itf['provider']} -> "
                     f"{', '.join(itf['consumers'])}（{itf.get('style', '')}/{itf.get('protocol', '')}）{msgs}")
    for df in proc.get("dataflows", []):
        lines.append(f"    // dataflow {df['id']}：{df['from']} -> {df['to']}"
                     f"（{df['payload']}，{df.get('frequency', '')}）")
    lines.append("}")
    return "\n".join(lines) + "\n"
