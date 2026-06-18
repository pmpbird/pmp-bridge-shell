#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("controller_base_tests", ROOT / "tools/test_automated_plan_controller_v1.py")
base = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(base)


class ControllerErrorPauseTests(unittest.TestCase):
    def test_backend_error_pauses_same_unit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            runtime = root / "runtime"
            prepared = root / "prepare"
            verified_out = root / "verified"
            base.fixture(root)
            base.prepare(root, runtime, prepared)
            decision = json.loads((prepared / "decision.json").read_text())
            transport = base.controller.transport_result(
                "blocked",
                backend_id=decision["backend_id"],
                request_id=decision["request_id"],
                error="backend rejected request",
                http_status=403,
            )
            base.dump(root / "transport.json", transport)
            base.controller.verify_event(Namespace(
                definition_root=root,
                runtime_root=runtime,
                live_main_sha=base.MAIN_SHA,
                decision=prepared / "decision.json",
                transport=root / "transport.json",
                out_dir=verified_out,
            ))
            candidate = json.loads((verified_out / "verified.json").read_text())["runtime_candidate"]
            self.assertEqual(candidate["status"], "paused")
            self.assertEqual(candidate["pause"]["reason"], "backend_unavailable")
            self.assertEqual(candidate["checkpoint"]["next_unit"], "pass_003")


if __name__ == "__main__":
    unittest.main(verbosity=2)
