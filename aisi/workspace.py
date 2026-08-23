"""系统工作区：目录结构、manifest、gates.json 状态机（12-Factor：状态即文件）。"""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

VIEW_ORDER = ["requirements", "composition", "architecture", "processes"]
PROFILE_STANDARDS = {
    "gjb438c": ["GJB 2786A", "GJB 438C", "ISO/IEC/IEEE 29148", "SysML v2"],
    "gb8567": ["GB/T 8567", "ISO/IEC/IEEE 29148", "SysML v2"],
    "custom": ["ISO/IEC/IEEE 29148", "SysML v2"],
}


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def find_workspace(path_arg: str | None, cwd: Path | None = None) -> Path:
    """定位系统工作区：--path 指定，否则在 <cwd>/systems/ 下自动发现（恰好一个）。"""
    if path_arg:
        p = Path(path_arg).resolve()
        if (p / "manifest.json").exists():
            return p
        raise FileNotFoundError(f"{p} 不是有效工作区（缺 manifest.json）。请先 aisi init。")
    base = (cwd or Path.cwd()) / "systems"
    if not base.exists():
        raise FileNotFoundError("未找到任何系统工作区。请先运行 aisi init 创建。")
    found = [d for d in sorted(base.iterdir()) if d.is_dir() and (d / "manifest.json").exists()]
    if not found:
        raise FileNotFoundError("未找到任何系统工作区。请先运行 aisi init 创建。")
    if len(found) > 1:
        names = "、".join(d.name for d in found)
        raise FileNotFoundError(f"发现多个工作区（{names}），请用 --path 指定。")
    return found[0]


class Workspace:
    def __init__(self, base: Path):
        self.base = base
        self.manifest = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
        self.gates = json.loads((base / "gates.json").read_text(encoding="utf-8"))

    @staticmethod
    def _write(path: Path, data: dict) -> None:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def save_manifest(self) -> None:
        self.manifest["updated"] = date.today().isoformat()
        self._write(self.base / "manifest.json", self.manifest)

    def save_gates(self) -> None:
        self._write(self.base / "gates.json", self.gates)

    def view_path(self, view: str) -> Path:
        return self.base / "views" / f"{view}.json"

    def view_data(self, view: str) -> dict | None:
        p = self.view_path(view)
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def state(self, view: str) -> str:
        return self.gates["views"][view]["state"]

    def record(self, view: str, event: str, to: str, comment: str = "") -> None:
        v = self.gates["views"][view]
        v["history"].append({
            "at": now_iso(), "event": event, "from": v["state"], "to": to,
            "actor": "human-cli", "comment": comment,
        })
        v["state"] = to
        self.save_gates()

    def mark_validated(self, view: str) -> None:
        """validate 通过后调用（仅 empty/draft 前移，不回退更高状态）。"""
        if self.state(view) in ("empty", "draft"):
            self.record(view, "validate", "validated")

    def previous_approved(self, view: str) -> list[str]:
        idx = VIEW_ORDER.index(view)
        return [v for v in VIEW_ORDER[:idx] if self.state(v) != "approved"]

    def add_force_override(self, view: str, reason: str) -> None:
        self.gates.setdefault("force_overrides", []).append(
            {"at": now_iso(), "view": view, "reason": reason})
        self.save_gates()

    def summary(self) -> dict:
        counter = {
            "requirements": lambda d: len(d.get("requirements", [])),
            "composition": lambda d: len(d.get("modules", [])),
            "architecture": lambda d: len(d.get("layers", [])),
            "processes": lambda d: len(d.get("processes", [])),
        }
        views = {}
        for v in VIEW_ORDER:
            data = self.view_data(v)
            views[v] = {
                "state": self.state(v),
                "artifact": self.view_path(v).exists(),
                "count": counter[v](data) if data else 0,
            }
        next_view, next_action = None, None
        for v in VIEW_ORDER:
            st = self.state(v)
            if st != "approved":
                next_view = v
                next_action = {
                    "empty": f"生成 {v} 草稿 JSON 至 views/{v}.json（LLM 依契约产出）",
                    "draft": f"运行 aisi validate --view {v}",
                    "validated": f"人工审阅渲染产物后运行 aisi gate review {v}",
                    "reviewed": f"运行 aisi gate approve {v}",
                }[st]
                break
        if not next_view:
            next_action = "四视图已全部 approved：运行 aisi trace / render / export sysml 产出交付物"
        open_clar = []
        req = self.view_data("requirements") or {}
        for r in req.get("requirements", []):
            for c in r.get("clarifications", []):
                if not c.get("answer"):
                    open_clar.append({"view": "requirements", "id": r["id"],
                                      "name": r["name"], "question": c["question"]})
        return {
            "system_id": self.manifest["system_id"],
            "name": self.manifest["name"],
            "profile": self.manifest["profile"],
            "views": views,
            "force_overrides": self.gates.get("force_overrides", []),
            "next_view": next_view,
            "next_action": next_action,
            "open_clarifications": open_clar,
            "clarification_prompt": (
                f"存在 {len(open_clar)} 处资料未展开的细节："
                "可直接回答（aisi clarify <ID> --answer）或启用搜索调研补充"
                "（aisi research plan，由宿主 Agent 执行搜索）") if open_clar else "",
            "resume_hint": f"aisi status --path {self.base}",
        }


def init_system(system_id: str, name: str, domain: str, profile: str,
                description: str = "", cwd: Path | None = None) -> tuple[Path, bool]:
    """创建工作区。返回 (路径, 是否新建)。幂等：已存在时不覆盖。"""
    base = (cwd or Path.cwd()) / "systems" / system_id
    created = not (base / "manifest.json").exists()
    for sub in ("sources", "research", "views", "sysml", "render", "reports"):
        (base / sub).mkdir(parents=True, exist_ok=True)
    if created:
        today = date.today().isoformat()
        Workspace._write(base / "manifest.json", {
            "schema": "aisi.system.manifest/1",
            "system_id": system_id, "name": name, "description": description,
            "domain": domain, "profile": profile,
            "standards": PROFILE_STANDARDS[profile],
            "created": today, "updated": today,
        })
        Workspace._write(base / "gates.json", {
            "schema": "aisi.gates/1",
            "views": {v: {"state": "empty", "history": []} for v in VIEW_ORDER},
            "force_overrides": [],
        })
    return base, created
