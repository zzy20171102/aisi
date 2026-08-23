"""图文渲染：Mermaid 图 + 自包含 HTML 查看器 + GJB 438C 风格规格说明报告。"""
from __future__ import annotations

import html
import json
from datetime import datetime

TYPE_ZH = {"functional": "功能需求", "performance": "性能需求", "interface": "接口需求",
           "data": "数据需求", "deployment": "部署需求", "safety": "安全性需求",
           "security": "安全需求", "reliability": "可靠性需求", "usability": "易用性需求",
           "environment": "环境需求", "operability": "可操作性需求", "constraint": "约束"}


def q(s: str) -> str:
    return '"' + s.replace('"', "'").replace("\n", " ") + '"'


def diagram_requirements(ws) -> str:
    reqs = (ws.view_data("requirements") or {}).get("requirements", [])
    lines = ["flowchart TD"]
    for r in reqs:
        nid = "r" + r["id"].replace("-", "").replace(".", "_")
        label = f"{r['id']} {r['name']}"
        if r.get("clarifications") and any(not c.get("answer") for c in r["clarifications"]):
            label += " ⚠"
        lines.append(f"    {nid}[{q(label)}]")
        if r.get("parent"):
            pid = "r" + r["parent"].replace("-", "").replace(".", "_")
            lines.append(f"    {pid} --> {nid}")
    return "\n".join(lines)


def diagram_composition(ws) -> str:
    mods = (ws.view_data("composition") or {}).get("modules", [])
    lines = ["flowchart TD"]
    for m in mods:
        nid = "m" + m["id"].replace("-", "")
        icon = {"subsystem": "📦", "module": "🧩", "service": "🔧",
                "database": "🗄️", "component": "⚙️", "external": "🌐"}.get(m["kind"], "")
        lines.append(f"    {nid}[{q(icon + ' ' + m['id'] + ' ' + m['name'])}]")
        if m.get("parent"):
            lines.append(f"    m{m['parent'].replace('-', '')} --> {nid}")
    return "\n".join(lines)


def diagram_architecture(ws) -> str:
    arch = ws.view_data("architecture") or {}
    lines = ["flowchart TD"]
    for l in sorted(arch.get("layers", []), key=lambda x: x["order"]):
        gid = "l" + l["id"].replace("-", "")
        lines.append(f"    subgraph {gid}[{q(l['id'] + ' ' + l['name'])}]")
        for mod in l.get("modules", []):
            mid = "m" + mod.replace("-", "")
            lines.append(f"        {mid}({q(mod)})")
        lines.append("    end")
    ordered = sorted(arch.get("layers", []), key=lambda x: x["order"])
    for a, b in zip(ordered, ordered[1:]):
        lines.append(f"    l{a['id'].replace('-', '')} --> l{b['id'].replace('-', '')}")
    return "\n".join(lines)


def diagram_process(ws, p: dict) -> str:
    lines = ["flowchart TD"]
    for s in p.get("steps", []):
        sid = "s" + s["id"][1:]
        label = f"{s['id']} [{s['actor']}] {s['action']}"
        if s.get("module"):
            label += f"\n({s['module']})"
        lines.append(f"    {sid}[{q(label)}]")
        for ex in s.get("exceptions", []):
            eid = sid + "x"
            lines.append(f"    {eid}{{'{ex}'}}")
            lines.append(f"    {sid} -. 异常 .-> {eid}")
        for nxt in s.get("next", []):
            if nxt == "END":
                lines.append(f"    {sid} --> END([END])")
            else:
                lines.append(f"    {sid} --> s{nxt[1:]}")
    return "\n".join(lines)


def diagram_dataflow(ws) -> str:
    proc = ws.view_data("processes") or {}
    lines = ["flowchart LR"]
    for df in proc.get("dataflows", []):
        f = "m" + df["from"].replace("-", "")
        t = "m" + df["to"].replace("-", "")
        lines.append(f"    {f}[{q(df['from'])}] --> |{q(df['id'] + ' ' + df['payload'])}| {t}[{q(df['to'])}]")
    for itf in proc.get("interfaces", []):
        p = "m" + itf["provider"].replace("-", "")
        lines.append(f"    {p}[{q(itf['provider'])}]")
        for c in itf.get("consumers", []):
            cid = "m" + c.replace("-", "")
            lines.append(f"    {cid}[{q(c)}]")
            lines.append(f"    {p} <-. {q(itf['id'] + ' ' + itf['name'])} .-> {cid}")
    return "\n".join(lines)


def all_diagrams(ws) -> dict[str, str]:
    d = {"requirements-tree": diagram_requirements(ws),
         "composition-tree": diagram_composition(ws),
         "architecture-layers": diagram_architecture(ws),
         "dataflow-interfaces": diagram_dataflow(ws)}
    for p in (ws.view_data("processes") or {}).get("processes", []):
        d[f"process-{p['id'].lower()}"] = diagram_process(ws, p)
    return d


def report_markdown(ws, trace_issues: dict, diagrams: dict[str, str]) -> str:
    reqs = (ws.view_data("requirements") or {}).get("requirements", [])
    comp = (ws.view_data("composition") or {}).get("modules", [])
    arch = ws.view_data("architecture") or {}
    proc = ws.view_data("processes") or {}
    m = ws.manifest
    now = datetime.now().isoformat(timespec="seconds")
    L = [f"# {m['name']} 系统规格说明（草案）", "",
         f"> AISI 工具套件自动生成 ｜ profile：{m['profile']} ｜ 标准：{'、'.join(m.get('standards', []))}",
         f"> 生成时间：{now} ｜ 四视图状态：全部 approved（门禁审计见 gates.json）", "",
         "## 1 范围", "", m.get("description", "") or f"本规格说明定义 {m['name']} 的系统需求、组成、架构与业务流程。", "",
         "## 2 引用文件", ""]
    L += [f"- {s}" for s in m.get("standards", [])]
    L += ["", "## 3 系统需求", "", "### 3.0 需求树", "",
          "```mermaid", diagrams["requirements-tree"], "```", ""]
    by_type: dict[str, list] = {}
    for r in reqs:
        by_type.setdefault(r["type"], []).append(r)
    sec = 1
    for t, rs in by_type.items():
        L += [f"### 3.{sec} {TYPE_ZH.get(t, t)}（{len(rs)} 条）", "",
              "| ID | 名称 | 需求内容 | 优先级 | 验证 | 来源 |", "|---|---|---|---|---|---|"]
        for r in rs:
            L.append(f"| {r['id']} | {r['name']} | {r['text']} | {r['priority']} "
                     f"| {r['verification']} | {'、'.join(r.get('source_refs', []))} |")
        L.append("")
        sec += 1
    L += ["## 4 系统组成", "", "### 4.0 模块分解树", "", "```mermaid",
          diagrams["composition-tree"], "```", "",
          "| ID | 名称 | 类型 | 父模块 | 承载数求数 | 职责 |", "|---|---|---|---|---|---|"]
    for mod in comp:
        L.append(f"| {mod['id']} | {mod['name']} | {mod['kind']} | {mod.get('parent', '') or '—'} "
                 f"| {len(mod.get('requirements', []))} | {'；'.join(mod.get('responsibilities', [])[:3])} |")
    L += ["", "## 5 系统架构", "", "### 5.0 分层架构", "", "```mermaid",
          diagrams["architecture-layers"], "```", "",
          "| 层 | 名称 | 技术栈 | 模块数 | 说明 |", "|---|---|---|---|---|"]
    for l in arch.get("layers", []):
        L.append(f"| {l['id']} | {l['name']} | {'、'.join(l.get('technologies', []))} "
                 f"| {len(l.get('modules', []))} | {l.get('description', '')} |")
    L += ["", "### 5.1 服务清单", "", "| ID | 服务 | 类型 | 挂载模块 | API |", "|---|---|---|---|---|"]
    for s in arch.get("services", []):
        L.append(f"| {s['id']} | {s['name']} | {s['kind']} | {s['module']} | {s.get('api', '')} |")
    L += ["", "### 5.2 数据资产", "", "| ID | 数据资产 | 实体 | 存储 | 归属 | 敏感级 |", "|---|---|---|---|---|---|"]
    for da in arch.get("data_assets", []):
        L.append(f"| {da['id']} | {da['name']} | {'、'.join(da.get('entities', [])[:4])} "
                 f"| {da['store']} | {da['owner_module']} | {da.get('sensitivity', '')} |")
    L += ["", "### 5.3 部署节点", "", "| ID | 节点 | 规格 | 承载 | 协议 |", "|---|---|---|---|---|"]
    for n in arch.get("deploy_nodes", []):
        L.append(f"| {n['id']} | {n['name']} | {n.get('spec', '')} "
                 f"| {'、'.join(n.get('hosts', [])) or '客户端'} | {n.get('protocol', '')} |")
    L += ["", "## 6 业务流程", ""]
    for p in proc.get("processes", []):
        L += [f"### 6.{p['id'].split('-')[1]} {p['name']}（{p['id']}）", "",
              f"触发：{p.get('trigger', '')} ｜ 参与者：{'、'.join(p.get('actors', []))}", "",
              "```mermaid", diagrams[f"process-{p['id'].lower()}"], "```", "",
              "| 步骤 | 执行者 | 动作 | 模块 | 输入 | 输出 | 异常 |", "|---|---|---|---|---|---|---|"]
        for s in p.get("steps", []):
            L.append(f"| {s['id']} | {s['actor']} | {s['action']} | {s.get('module', '—')} "
                     f"| {'、'.join(s.get('inputs', []))} | {'、'.join(s.get('outputs', []))} "
                     f"| {'；'.join(s.get('exceptions', []))} |")
        L.append("")
    L += ["## 7 接口与数据流", "", "### 7.0 接口", "",
          "| ID | 接口 | 提供方 | 消费方 | 风格/协议 | 消息 |", "|---|---|---|---|---|---|"]
    for itf in proc.get("interfaces", []):
        msgs = "；".join(f"{x['name']}({x['direction']})" for x in itf.get("messages", []))
        L.append(f"| {itf['id']} | {itf['name']} | {itf['provider']} "
                 f"| {'、'.join(itf['consumers'])} | {itf.get('style', '')}/{itf.get('protocol', '')} | {msgs} |")
    L += ["", "### 7.1 数据流", "", "| ID | 源 | 目标 | 载荷 | 频率 |", "|---|---|---|---|---|"]
    for df in proc.get("dataflows", []):
        L.append(f"| {df['id']} | {df['from']} | {df['to']} | {df['payload']} | {df.get('frequency', '')} |")
    L += ["", "## 8 需求追踪概览", "",
          f"- 追踪边 {trace_issues['counts']['edges']} 条",
          f"- 孤儿需求 {len(trace_issues['orphan_requirements'])} ｜ "
          f"空模块 {len(trace_issues['modules_without_requirements'])} ｜ "
          f"未分层模块 {len(trace_issues['modules_without_layer'])}",
          "", "```mermaid", diagrams["dataflow-interfaces"], "```", ""]
    open_clar = [(r["id"], r["name"], c["question"]) for r in reqs
                 for c in r.get("clarifications", []) if not c.get("answer")]
    L += ["## 9 待澄清事项", ""]
    if open_clar:
        for rid, name, qq in open_clar:
            L.append(f"- **{rid} {name}**：{qq}（可 `aisi clarify {rid} --answer` 回填，或启用调研）")
    else:
        L.append("无。")
    return "\n".join(L) + "\n"


def viewer_html(ws, diagrams: dict[str, str]) -> str:
    title = html.escape(ws.manifest["name"])
    sections = []
    for name, code in diagrams.items():
        sections.append(
            f"<section><h2>{html.escape(name)}</h2>"
            f"<pre class='mermaid'>{html.escape(code)}</pre></section>")
    body = "\n".join(sections)
    return f"""<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8">
<title>{title} · 系统设计图集</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<style>body{{font-family:'Microsoft YaHei',sans-serif;max-width:1200px;margin:0 auto;
padding:24px;background:#fafbfc}}h1{{color:#1a3c6e}}section{{background:#fff;border:1px solid
#e1e4e8;border-radius:8px;padding:16px;margin:20px 0;box-shadow:0 1px 3px rgba(0,0,0,.06)}}
.mermaid{{display:flex;justify-content:center}}</style></head>
<body><h1>{title} · 系统设计图集</h1>
<p>由 AISI 工具套件生成（{html.escape(datetime.now().isoformat(timespec='seconds'))}）；
首次打开需联网加载 mermaid.js。</p>
{body}
<script>mermaid.initialize({{startOnLoad:true,theme:'default'}});</script>
</body></html>"""
