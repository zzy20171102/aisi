#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AISI M1 契约层测试：Schema / init / validate / gate / status。"""
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from aisi import cli
from aisi.validator import list_schemas, load_schema, validate


def run_cli(*argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = cli.main(list(argv))
    return rc, json.loads(buf.getvalue())


REQ_VIEW = {
    "schema": "aisi.requirements/1",
    "requirements": [
        {"id": "REQ-001", "name": "档案管理", "text": "系统应支持员工档案增删改查。",
         "type": "functional", "priority": "必须", "verification": "测试",
         "status": "confirmed", "confidence": "high",
         "source_refs": ["SRC-001#3.1"], "parent": ""},
        {"id": "REQ-001.1", "name": "档案导入导出", "text": "系统应支持档案 Excel 批量导入导出。",
         "type": "interface", "priority": "应当", "verification": "演示",
         "status": "confirmed", "confidence": "high",
         "source_refs": ["SRC-001#3.1"], "parent": "REQ-001",
         "allocations": [{"module_id": "MOD-01", "role": "implements"}]},
    ],
}

COMP_VIEW = {
    "schema": "aisi.composition/1",
    "modules": [
        {"id": "MOD-00", "name": "人力资源管理系统", "kind": "subsystem", "parent": "",
         "requirements": ["REQ-001"]},
        {"id": "MOD-01", "name": "员工资料管理", "kind": "module", "parent": "MOD-00",
         "requirements": ["REQ-001.1"], "layer": "LAY-01"},
    ],
}

ARCH_VIEW = {
    "schema": "aisi.architecture/1",
    "layers": [{"id": "LAY-01", "name": "应用层", "order": 1, "modules": ["MOD-01"]}],
    "services": [{"id": "SVC-01", "name": "权限服务", "kind": "business", "module": "MOD-01"}],
    "data_assets": [{"id": "DA-01", "name": "员工档案库", "entities": ["Employee"],
                     "store": "MySQL", "owner_module": "MOD-01"}],
    "deploy_nodes": [{"id": "N-01", "name": "应用服务器", "hosts": ["SVC-01"],
                      "spec": "2C2G", "protocol": "HTTPS"}],
}

PROC_VIEW = {
    "schema": "aisi.processes/1",
    "processes": [{
        "id": "PRC-001", "name": "员工入职建档", "trigger": "新员工入职", "actors": ["HR"],
        "steps": [{"id": "S01", "actor": "HR", "action": "录入基本资料", "module": "MOD-01",
                   "inputs": ["纸质档案"], "outputs": ["DA-01"], "next": ["END"]}],
    }],
    "dataflows": [{"id": "DF-01", "from": "MOD-01", "to": "MOD-01", "payload": "档案数据",
                   "frequency": "实时", "protocol": "内部"}],
    "interfaces": [{"id": "IF-01", "name": "档案查询接口", "provider": "MOD-01",
                    "consumers": ["MOD-00"], "style": "REST", "protocol": "HTTPS",
                    "messages": [{"name": "query", "direction": "request", "fields": ["empId"]}]}],
}


class M1Tests(unittest.TestCase):
    def setUp(self):
        self.old_cwd = os.getcwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="aisi-m1-"))
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self.old_cwd)
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write_view(self, name: str, data: dict) -> Path:
        p = self.tmp / "systems" / "hr" / "views" / f"{name}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return p

    def init_hr(self):
        rc, out = run_cli("init", "--id", "hr", "--name", "人力资源管理系统",
                          "--domain", "information-system", "--profile", "gjb438c")
        self.assertEqual(rc, 0)
        self.assertTrue(out["ok"])
        return out

    def test_schemas_load_and_self_validate(self):
        names = list_schemas()
        self.assertEqual(len(names), 8)
        for n in names:
            s = load_schema(n)
            self.assertIn("$id", s)
            self.assertIn("$schema", s)
            self.assertIn("type", s)

    def test_init_creates_workspace_idempotent(self):
        out = self.init_hr()
        base = Path(out["path"])
        self.assertTrue((base / "manifest.json").exists())
        self.assertTrue((base / "gates.json").exists())
        manifest = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
        self.assertIn("GJB 438C", manifest["standards"])
        rc2, out2 = run_cli("init", "--id", "hr", "--name", "人力资源管理系统",
                            "--domain", "information-system")
        self.assertEqual(rc2, 0)
        self.assertFalse(out2["created"])

    def test_validate_requirements_ok_and_state(self):
        self.init_hr()
        self.write_view("requirements", REQ_VIEW)
        rc, out = run_cli("validate", "--view", "requirements")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["state"], "validated")
        self.assertEqual(out["next_action"], "aisi gate review requirements")
        rc, st = run_cli("status")
        self.assertEqual(st["views"]["requirements"]["state"], "validated")
        self.assertEqual(st["views"]["requirements"]["count"], 2)

    def test_validate_schema_errors(self):
        self.init_hr()
        bad = {"schema": "aisi.requirements/1", "requirements": [{
            "id": "R1", "name": "x", "text": "过短",
            "type": "wrong-type", "priority": "必须", "verification": "测试",
            "status": "confirmed", "confidence": "high", "extra_field": 1}]}
        self.write_view("requirements", bad)
        rc, out = run_cli("validate", "--view", "requirements")
        self.assertEqual(rc, 2)
        codes = {e["code"] for e in out["errors"]}
        self.assertIn("pattern", codes)
        self.assertIn("enum", codes)
        self.assertIn("minLength", codes)
        self.assertIn("additionalProperty", codes)

    def test_validate_lint_duplicate_ids(self):
        self.init_hr()
        dup = json.loads(json.dumps(REQ_VIEW))
        dup["requirements"][1]["id"] = "REQ-001"
        dup["requirements"][1].pop("parent", None)
        self.write_view("requirements", dup)
        rc, out = run_cli("validate", "--view", "requirements")
        self.assertEqual(rc, 2)
        self.assertTrue(any(e["code"] == "REQ_DUP" for e in out["errors"]))

    def test_gate_locked_then_force(self):
        self.init_hr()
        self.write_view("composition", COMP_VIEW)
        rc, out = run_cli("validate", "--view", "composition")
        self.assertEqual(rc, 3)
        self.assertEqual(out["errors"][0]["code"], "gate_locked")
        rc, out = run_cli("validate", "--view", "composition", "--force")
        self.assertEqual(rc, 2)
        rc, out = run_cli("validate", "--view", "composition",
                          "--force", "--reason", "并行起草")
        self.assertEqual(rc, 0, out)
        gates = json.loads((self.tmp / "systems" / "hr" / "gates.json").read_text(encoding="utf-8"))
        self.assertEqual(len(gates["force_overrides"]), 1)

    def test_gate_full_flow_and_reject(self):
        self.init_hr()
        self.write_view("requirements", REQ_VIEW)
        # 顺序错误：未 validate 直接 approve
        rc, out = run_cli("gate", "approve", "requirements")
        self.assertEqual(rc, 3)
        # reject 缺 comment
        run_cli("validate", "--view", "requirements")
        rc, out = run_cli("gate", "reject", "requirements")
        self.assertEqual(rc, 2)
        # validate -> review -> approve
        rc, _ = run_cli("gate", "review", "requirements")
        self.assertEqual(rc, 0)
        rc, out = run_cli("gate", "approve", "requirements")
        self.assertEqual(rc, 0)
        self.assertIn("composition", out["next_action"])
        # 打回：approved -> draft
        rc, out = run_cli("gate", "reject", "requirements", "--comment", "需求拆分过粗")
        self.assertEqual(rc, 0)
        self.assertEqual(out["to"], "draft")

    def test_end_to_end_four_views(self):
        self.init_hr()
        for view, data in (("requirements", REQ_VIEW), ("composition", COMP_VIEW),
                           ("architecture", ARCH_VIEW), ("processes", PROC_VIEW)):
            self.write_view(view, data)
        for view in ("requirements", "composition", "architecture", "processes"):
            rc, out = run_cli("validate", "--view", view)
            self.assertEqual(rc, 0, f"{view}: {out}")
            run_cli("gate", "review", view)
            rc, _ = run_cli("gate", "approve", view)
            self.assertEqual(rc, 0)
        rc, st = run_cli("status")
        self.assertEqual(rc, 0)
        for v in ("requirements", "composition", "architecture", "processes"):
            self.assertEqual(st["views"][v]["state"], "approved")
        self.assertIn("trace", st["next_action"])

    def test_status_clarification_prompt_and_clarify(self):
        self.init_hr()
        data = json.loads(json.dumps(REQ_VIEW))
        data["requirements"][0]["clarifications"] = [
            {"question": "档案字段范围？", "answer": ""}]
        self.write_view("requirements", data)
        rc, out = run_cli("validate", "--view", "requirements")
        self.assertEqual(rc, 0, out)
        rc, st = run_cli("status")
        self.assertEqual(len(st["open_clarifications"]), 1)
        self.assertIn("启用搜索调研补充", st["clarification_prompt"])
        rc, out = run_cli("clarify", "REQ-001", "--answer", "字段以报告4.3.1为准")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["remaining_open"], 0)
        rc, st = run_cli("status")
        self.assertEqual(st["open_clarifications"], [])
        self.assertEqual(st["clarification_prompt"], "")


if __name__ == "__main__":
    unittest.main()
