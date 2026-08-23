#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AISI M4 交付物测试：trace / export sysml / render。"""
import json
import os
import tempfile
import unittest
from pathlib import Path

from aisi import cli
from aisi.validator import load_schema, validate
from tests.test_aisi_m1 import ARCH_VIEW, COMP_VIEW, PROC_VIEW, REQ_VIEW, run_cli


class M4Tests(unittest.TestCase):
    def setUp(self):
        self.old_cwd = os.getcwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="aisi-m4-"))
        os.chdir(self.tmp)
        run_cli("init", "--id", "hr", "--name", "人力资源管理系统",
                "--domain", "information-system")
        for name, data in (("requirements", REQ_VIEW), ("composition", COMP_VIEW),
                           ("architecture", ARCH_VIEW), ("processes", PROC_VIEW)):
            p = self.tmp / "systems" / "hr" / "views" / f"{name}.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            run_cli("validate", "--view", name)
            run_cli("gate", "review", name)
            run_cli("gate", "approve", name)

    def tearDown(self):
        os.chdir(self.old_cwd)
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_trace(self):
        rc, out = run_cli("trace")
        self.assertEqual(rc, 0, out)
        self.assertGreater(out["edges"], 0)
        tj = json.loads((self.tmp / "systems" / "hr" / "trace.json").read_text(encoding="utf-8"))
        self.assertEqual(validate(tj, load_schema("trace")), [])
        self.assertIn("satisfy", {e["relation"] for e in tj["edges"]})
        md = (self.tmp / "systems" / "hr" / "render" / "trace.md").read_text(encoding="utf-8")
        self.assertIn("追踪矩阵", md)

    def test_trace_locked_without_approval(self):
        run_cli("gate", "reset", "processes")
        rc, out = run_cli("trace")
        self.assertEqual(rc, 3)
        self.assertEqual(out["errors"][0]["code"], "gate_locked")
        run_cli("validate", "--view", "processes")
        run_cli("gate", "review", "processes")
        run_cli("gate", "approve", "processes")

    def test_export_sysml(self):
        rc, out = run_cli("export")
        self.assertEqual(rc, 0, out)
        sysml_dir = self.tmp / "systems" / "hr" / "sysml"
        for f in ("requirements", "composition", "architecture", "processes"):
            text = (sysml_dir / f"{f}.sysml").read_text(encoding="utf-8")
            self.assertEqual(text.count("{"), text.count("}"))
            self.assertIn("package", text)
        req_text = (sysml_dir / "requirements.sysml").read_text(encoding="utf-8")
        self.assertIn("requirement <'REQ-001'>", req_text)

    def test_render(self):
        rc, out = run_cli("render", "--format", "all")
        self.assertEqual(rc, 0, out)
        render = self.tmp / "systems" / "hr" / "render"
        mmds = list((render / "diagrams").glob("*.mmd"))
        self.assertGreaterEqual(len(mmds), 4)
        html = (render / "viewer.html").read_text(encoding="utf-8")
        self.assertIn("mermaid", html)
        report = (self.tmp / "systems" / "hr" / "reports" / "system-specification.md").read_text(encoding="utf-8")
        self.assertIn("系统规格说明", report)
        self.assertIn("REQ-001", report)
        self.assertIn("```mermaid", report)


if __name__ == "__main__":
    unittest.main()
