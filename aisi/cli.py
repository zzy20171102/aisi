"""aisi CLI：系统知识拆解工具套件命令入口（JSON in / JSON out，退出码契约化）。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .coverage import analyze as coverage_analyze
from .ingest import ingest_file
from .lint import lint
from .render import all_diagrams, report_markdown, viewer_html
from .research import ingest_findings, plan as research_plan
from .sysml_export import check_balance, export_architecture, export_composition, \
    export_processes, export_requirements
from .trace import analyze, build_edges, render_markdown as trace_md
from .validator import load_schema, validate
from .workspace import VIEW_ORDER, Workspace, find_workspace, init_system

EXIT_OK, EXIT_CONTRACT, EXIT_GATE, EXIT_NOT_FOUND = 0, 2, 3, 4


def emit(obj: dict) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def fail(errors: list[dict], exit_code: int) -> int:
    emit({"ok": False, "errors": errors})
    return exit_code


def cmd_init(a) -> int:
    base, created = init_system(a.id, a.name, a.domain, a.profile, a.description)
    emit({"ok": True, "created": created, "path": str(base),
          "manifest": str(base / "manifest.json"),
          "next_action": "登记资料（M2: aisi ingest）或直接生成 views/requirements.json 草稿"})
    return EXIT_OK


def cmd_status(a) -> int:
    try:
        ws = Workspace(find_workspace(a.path))
    except FileNotFoundError as e:
        return fail([{"code": "workspace_not_found", "message": str(e),
                      "suggestion": "先运行 aisi init 创建系统工作区"}], EXIT_NOT_FOUND)
    s = ws.summary()
    s.update({"ok": True, "version": __version__})
    emit(s)
    return EXIT_OK


def cmd_validate(a) -> int:
    try:
        ws = Workspace(find_workspace(a.path))
    except FileNotFoundError as e:
        return fail([{"code": "workspace_not_found", "message": str(e)}], EXIT_NOT_FOUND)

    src = Path(a.file) if a.file else ws.view_path(a.view)
    if not src.exists():
        return fail([{"code": "artifact_not_found", "view": a.view,
                      "message": f"视图文件不存在: {src}",
                      "suggestion": f"先按契约 aisi.{a.view}/1 生成草稿 JSON"}], EXIT_NOT_FOUND)
    try:
        data = json.loads(src.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return fail([{"code": "json_parse", "view": a.view,
                      "message": f"JSON 解析失败: {e}"}], EXIT_CONTRACT)

    schema_errors = validate(data, load_schema(a.view))
    if schema_errors:
        for e in schema_errors:
            e["view"] = a.view
        return fail(schema_errors, EXIT_CONTRACT)

    pending = ws.previous_approved(a.view)
    if pending:
        if not a.force:
            return fail([{"code": "gate_locked", "view": a.view,
                          "message": f"前置视图尚未 approved: {', '.join(pending)}",
                          "suggestion": "先完成前置视图门禁，或使用 --force --reason <越级原因>"}],
                        EXIT_GATE)
        if not a.reason:
            return fail([{"code": "force_requires_reason", "view": a.view,
                          "message": "--force 必须附带 --reason"}], EXIT_CONTRACT)
        ws.add_force_override(a.view, a.reason)

    issues = lint(a.view, data, ws.base)
    hard = [i for i in issues if i["severity"] == "error"]
    if hard:
        return fail([{"view": a.view, **i} for i in hard], EXIT_CONTRACT)

    ws.mark_validated(a.view)
    report = {"ok": True, "view": a.view, "file": str(src), "schema": f"aisi.{a.view}/1",
              "warnings": [i for i in issues if i["severity"] == "warning"],
              "state": ws.state(a.view),
              "next_action": f"aisi gate review {a.view}",
              "force_override": bool(pending)}
    render_dir = ws.base / "render"
    render_dir.mkdir(exist_ok=True)
    (render_dir / f"validation-{a.view}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    emit(report)
    return EXIT_OK


def cmd_gate(a) -> int:
    try:
        ws = Workspace(find_workspace(a.path))
    except FileNotFoundError as e:
        return fail([{"code": "workspace_not_found", "message": str(e)}], EXIT_NOT_FOUND)

    view, action = a.view, a.action
    st = ws.state(view)
    transitions = {
        "review": {"from": ("validated",), "to": "reviewed",
                   "err": "仅 validated 状态可 review（先 aisi validate）"},
        "approve": {"from": ("reviewed",), "to": "approved",
                    "err": "仅 reviewed 状态可 approve（先 aisi gate review）"},
        "reject": {"from": ("validated", "reviewed", "approved"), "to": "draft",
                   "err": "当前状态无需 reject"},
        "reset": {"from": ("draft", "validated", "reviewed", "approved"), "to": "draft",
                  "err": "工作区为空，无需 reset"},
    }
    tr = transitions[action]
    if st not in tr["from"]:
        return fail([{"code": "gate_invalid_transition", "view": view,
                      "message": f"当前状态 {st}，{tr['err']}"}], EXIT_GATE)
    if action == "reject" and not a.comment:
        return fail([{"code": "comment_required", "view": view,
                      "message": "reject 必须附带 --comment 打回原因"}], EXIT_CONTRACT)
    ws.record(view, f"gate:{action}", tr["to"], a.comment)
    if tr["to"] == "approved" and view != VIEW_ORDER[-1]:
        next_hint = f"开始下一视图：生成 views/{VIEW_ORDER[VIEW_ORDER.index(view) + 1]}.json"
    elif tr["to"] == "approved":
        next_hint = "运行 aisi trace / render / export sysml 产出最终交付物"
    elif tr["to"] == "reviewed":
        next_hint = f"aisi gate approve {view}"
    else:
        next_hint = f"修改 views/{view}.json 后重新 aisi validate --view {view}"
    emit({"ok": True, "view": view, "action": action, "from": st, "to": tr["to"],
          "comment": a.comment, "next_action": next_hint})
    return EXIT_OK


def cmd_clarify(a) -> int:
    """回填待澄清项答案（资料未展开细节的用户决策入口）。"""
    try:
        ws = Workspace(find_workspace(a.path))
    except FileNotFoundError as e:
        return fail([{"code": "workspace_not_found", "message": str(e)}], EXIT_NOT_FOUND)
    p = ws.view_path("requirements")
    if not p.exists():
        return fail([{"code": "artifact_not_found", "view": "requirements",
                      "message": "需求视图不存在"}], EXIT_NOT_FOUND)
    data = json.loads(p.read_text(encoding="utf-8"))
    target = None
    for r in data.get("requirements", []):
        if r["id"] == a.id:
            for c in r.get("clarifications", []):
                if not c.get("answer"):
                    target = (r, c)
                    break
    if target is None:
        return fail([{"code": "clarification_not_found", "view": "requirements",
                      "message": f"{a.id} 不存在未回答的待澄清项"}], EXIT_NOT_FOUND)
    r, c = target
    c["answer"] = a.answer
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    remaining = sum(1 for x in data.get("requirements", [])
                    for y in x.get("clarifications", []) if not y.get("answer"))
    st = ws.state("requirements")
    return_hint = (f"需求视图当前状态 {st}，内容已变更，建议重新 aisi validate --view requirements"
                   if st in ("validated", "reviewed", "approved") else
                   "继续后续视图工作")
    emit({"ok": True, "id": a.id, "question": c["question"], "answer": a.answer,
          "remaining_open": remaining, "next_action": return_hint})
    return EXIT_OK


def _require_all_approved(ws: Workspace, force: bool, reason: str) -> list[dict] | None:
    pending = [v for v in VIEW_ORDER if ws.state(v) != "approved"]
    if not pending:
        return None
    if not force:
        return [{"code": "gate_locked", "message": f"视图尚未全部 approved: {', '.join(pending)}",
                 "suggestion": "先完成门禁，或使用 --force --reason <原因>"}]
    if not reason:
        return [{"code": "force_requires_reason", "message": "--force 必须附带 --reason"}]
    for v in pending:
        ws.add_force_override(v, reason)
    return None


def cmd_trace(a) -> int:
    try:
        ws = Workspace(find_workspace(a.path))
    except FileNotFoundError as e:
        return fail([{"code": "workspace_not_found", "message": str(e)}], EXIT_NOT_FOUND)
    err = _require_all_approved(ws, a.force, a.reason)
    if err:
        return fail(err, EXIT_GATE)
    edges = build_edges(ws)
    issues = analyze(ws, edges)
    trace_data = {"schema": "aisi.trace/1", "system_id": ws.manifest["system_id"],
                  "generated_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
                  "edges": edges}
    (ws.base / "trace.json").write_text(
        json.dumps(trace_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ws.base / "render").mkdir(exist_ok=True)
    (ws.base / "render" / "trace.md").write_text(trace_md(ws, edges, issues), encoding="utf-8")
    emit({"ok": True, "edges": len(edges), "issues": issues,
          "outputs": ["trace.json", "render/trace.md"],
          "next_action": "aisi export sysml && aisi render --format all"})
    return EXIT_OK


def cmd_export(a) -> int:
    try:
        ws = Workspace(find_workspace(a.path))
    except FileNotFoundError as e:
        return fail([{"code": "workspace_not_found", "message": str(e)}], EXIT_NOT_FOUND)
    err = _require_all_approved(ws, a.force, a.reason)
    if err:
        return fail(err, EXIT_GATE)
    exporters = {"requirements": export_requirements, "composition": export_composition,
                 "architecture": export_architecture, "processes": export_processes}
    out_dir = ws.base / "sysml"
    out_dir.mkdir(exist_ok=True)
    results, errors = [], []
    for name, fn in exporters.items():
        text = fn(ws)
        errs = check_balance(text)
        p = out_dir / f"{name}.sysml"
        p.write_text(text, encoding="utf-8")
        results.append(str(p))
        errors += [{"view": name, "message": e} for e in errs]
    if errors:
        return fail(errors, EXIT_CONTRACT)
    emit({"ok": True, "outputs": results,
          "next_action": "用 SysML v2 工具（SysON 等）打开渲染"})
    return EXIT_OK


def cmd_render(a) -> int:
    try:
        ws = Workspace(find_workspace(a.path))
    except FileNotFoundError as e:
        return fail([{"code": "workspace_not_found", "message": str(e)}], EXIT_NOT_FOUND)
    err = _require_all_approved(ws, a.force, a.reason)
    if err:
        return fail(err, EXIT_GATE)
    diagrams = all_diagrams(ws)
    ddir = ws.base / "render" / "diagrams"
    ddir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for name, code in diagrams.items():
        p = ddir / f"{name}.mmd"
        p.write_text(code + "\n", encoding="utf-8")
        outputs.append(str(p))
    if a.format in ("html", "all"):
        p = ws.base / "render" / "viewer.html"
        p.write_text(viewer_html(ws, diagrams), encoding="utf-8")
        outputs.append(str(p))
    if a.format in ("md", "all"):
        issues = analyze(ws, build_edges(ws))
        p = ws.base / "reports" / "system-specification.md"
        p.parent.mkdir(exist_ok=True)
        p.write_text(report_markdown(ws, issues, diagrams), encoding="utf-8")
        outputs.append(str(p))
    emit({"ok": True, "format": a.format, "diagrams": len(diagrams), "outputs": outputs,
          "next_action": "浏览器打开 render/viewer.html 查看图集；报告见 reports/"})
    return EXIT_OK


def cmd_ingest(a) -> int:
    try:
        ws = Workspace(find_workspace(a.path))
    except FileNotFoundError as e:
        return fail([{"code": "workspace_not_found", "message": str(e)}], EXIT_NOT_FOUND)
    try:
        r = ingest_file(ws, a.file, a.title)
    except (FileNotFoundError, ValueError) as e:
        return fail([{"code": "ingest_failed", "message": str(e)}], EXIT_CONTRACT)
    emit({"ok": True, **r,
          "next_action": "aisi coverage 检查证据缺口（需求 source_refs 现在可解析）"})
    return EXIT_OK


def cmd_coverage(a) -> int:
    try:
        ws = Workspace(find_workspace(a.path))
    except FileNotFoundError as e:
        return fail([{"code": "workspace_not_found", "message": str(e)}], EXIT_NOT_FOUND)
    result = coverage_analyze(ws, a.view)
    out = ws.base / "research" / "gaps.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    emit({"ok": True, "summary": result["summary"],
          "by_kind": {k: sum(1 for g in result["gaps"] if g["kind"] == k)
                      for k in {g["kind"] for g in result["gaps"]}},
          "file": str(out),
          "next_action": "aisi research plan 生成调研问题（或先 ingest 补充资料）"})
    return EXIT_OK


def cmd_research_plan(a) -> int:
    try:
        ws = Workspace(find_workspace(a.path))
    except FileNotFoundError as e:
        return fail([{"code": "workspace_not_found", "message": str(e)}], EXIT_NOT_FOUND)
    try:
        r = research_plan(ws)
    except FileNotFoundError as e:
        return fail([{"code": "gaps_not_found", "message": str(e)}], EXIT_NOT_FOUND)
    emit({"ok": True, **r})
    return EXIT_OK


def cmd_research_ingest(a) -> int:
    try:
        ws = Workspace(find_workspace(a.path))
    except FileNotFoundError as e:
        return fail([{"code": "workspace_not_found", "message": str(e)}], EXIT_NOT_FOUND)
    try:
        if a.file == "-":
            data = json.loads(sys.stdin.read())
        else:
            data = json.loads(Path(a.file).read_text(encoding="utf-8"))
        r = ingest_findings(ws, data, a.to_kb)
    except (ValueError, json.JSONDecodeError) as e:
        return fail([{"code": "research_invalid", "message": str(e)}], EXIT_CONTRACT)
    except FileNotFoundError as e:
        return fail([{"code": "file_not_found", "message": str(e)}], EXIT_NOT_FOUND)
    emit({"ok": True, **r})
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="aisi",
                                 description="AISI 系统知识拆解工具套件（契约 v0.1）")
    ap.add_argument("--version", action="version", version=f"aisi {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="初始化系统工作区")
    p.add_argument("--id", required=True, help="系统标识（小写字母数字连字符）")
    p.add_argument("--name", required=True, help="系统中文名")
    p.add_argument("--domain", required=True,
                   choices=["airborne", "aerospace", "information-system", "software", "other"])
    p.add_argument("--profile", default="gjb438c", choices=["gjb438c", "gb8567", "custom"])
    p.add_argument("--description", default="")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("status", help="门禁状态 / 断点续作")
    p.add_argument("--path", default=None, help="工作区路径（缺省自动发现 systems/ 下唯一工作区）")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("validate", help="Schema 校验 + 语义 lint，通过则 draft→validated")
    p.add_argument("--view", required=True, choices=VIEW_ORDER)
    p.add_argument("--file", default=None, help="草稿文件路径（缺省 views/<view>.json）")
    p.add_argument("--path", default=None)
    p.add_argument("--force", action="store_true", help="越级（需 --reason，记入 force_overrides）")
    p.add_argument("--reason", default="")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("gate", help="阶段门禁：review|approve|reject|reset")
    p.add_argument("action", choices=["review", "approve", "reject", "reset"])
    p.add_argument("view", choices=VIEW_ORDER)
    p.add_argument("--comment", default="")
    p.add_argument("--path", default=None)
    p.set_defaults(func=cmd_gate)

    p = sub.add_parser("clarify", help="回填待澄清项答案（资料未展开的细节）")
    p.add_argument("id", help="需求编号，如 REQ-001.8.3")
    p.add_argument("--answer", required=True, help="澄清答案")
    p.add_argument("--path", default=None)
    p.set_defaults(func=cmd_clarify)

    p = sub.add_parser("trace", help="生成四视图追踪矩阵（trace.json + trace.md）")
    p.add_argument("--path", default=None)
    p.add_argument("--force", action="store_true")
    p.add_argument("--reason", default="")
    p.set_defaults(func=cmd_trace)

    p = sub.add_parser("export", help="导出 SysML v2（sysml/*.sysml）")
    p.add_argument("--path", default=None)
    p.add_argument("--force", action="store_true")
    p.add_argument("--reason", default="")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("render", help="渲染图文（mermaid/html/md 报告）")
    p.add_argument("--format", choices=["md", "html", "all"], default="all")
    p.add_argument("--path", default=None)
    p.add_argument("--force", action="store_true")
    p.add_argument("--reason", default="")
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("ingest", help="资料登记+抽取分块（md/txt/html/docx/pdf/url）")
    p.add_argument("--file", required=True, help="资料文件路径，或 http(s):// URL 登记")
    p.add_argument("--title", default="", help="来源标题（缺省用文件名）")
    p.add_argument("--path", default=None)
    p.set_defaults(func=cmd_ingest)

    p = sub.add_parser("coverage", help="证据缺口分析 → research/gaps.json")
    p.add_argument("--view", default="requirements", choices=VIEW_ORDER)
    p.add_argument("--path", default=None)
    p.set_defaults(func=cmd_coverage)

    p = sub.add_parser("research", help="调研闭环（plan / ingest）")
    sub2 = p.add_subparsers(dest="raction", required=True)
    pp = sub2.add_parser("plan", help="由 gaps 生成调研问题清单")
    pp.add_argument("--path", default=None)
    pp.set_defaults(func=cmd_research_plan)
    pi = sub2.add_parser("ingest", help="归档调研结果（--file 或 - stdin）")
    pi.add_argument("--file", required=True)
    pi.add_argument("--to-kb", action="store_true", help="同步生成知识库条目文件")
    pi.add_argument("--path", default=None)
    pi.set_defaults(func=cmd_research_ingest)

    args = ap.parse_args(argv)
    return args.func(args)
