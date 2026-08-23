"""aisi CLI：系统知识拆解工具套件命令入口（JSON in / JSON out，退出码契约化）。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .lint import lint
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

    args = ap.parse_args(argv)
    return args.func(args)
