#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
from argparse import Namespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("controller", ROOT / "automation/controller/v1/controller.py")
controller = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(controller)
MAIN_SHA = "d" * 40


def main() -> int:
    with tempfile.TemporaryDirectory() as d:
        temp = Path(d)
        runtime = temp / "automation/runtime"
        prepared = temp / "prepared"
        verified = temp / "verified"
        controller.prepare_event(Namespace(
            definition_root=ROOT, runtime_root=runtime, live_main_sha=MAIN_SHA,
            action="status", backend="github_models_free", supervised=False,
            automatic=False, out_dir=prepared,
        ))
        decision = json.loads((prepared / "decision.json").read_text())
        assert decision["should_infer"] is False
        assert not (prepared / "request.json").exists()
        controller.verify_event(Namespace(
            definition_root=ROOT, runtime_root=runtime, live_main_sha=MAIN_SHA,
            decision=prepared / "decision.json", transport=None, out_dir=verified,
        ))
        receipt = json.loads((verified / "verified.json").read_text())
        assert receipt["kind"] == "state_only"
        assert "runtime_candidate" not in receipt
        controller.persist_event(Namespace(
            definition_root=ROOT, runtime_root=runtime, live_main_sha=MAIN_SHA,
            decision=prepared / "decision.json", transport=None,
            verified=verified / "verified.json",
        ))
        status = json.loads((runtime / "status.json").read_text())
        assert status["execution_enabled"] is False
        assert status["checkpoint"]["last_verified_unit"] == "pass_002"
        assert status["checkpoint"]["next_unit"] == "pass_003"
        assert status["checkpoint"]["checkpoint_sequence"] == 0
        assert status["first_run_completed"] is False
        assert status["billing_gate"]["status"] == "unverified"
        plan = json.loads((ROOT / "automation/plans/packet-01-5.v1.json").read_text())
        assert plan["compiled_units"] == []
        assert plan["execution_enabled"] is False
        print(json.dumps({
            "result": "PASS",
            "workflow": "complete_non_executing_controller",
            "model_called": False,
            "checkpoint_unchanged": True,
            "pass_003_started": False,
            "billing_gate": "unverified_hosted_execution_blocked"
        }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
