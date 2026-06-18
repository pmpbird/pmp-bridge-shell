#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("pmp_controller", ROOT / "automation/controller/v1/controller.py")
controller = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(controller)

MAIN_SHA = "a" * 40


def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def fixture(root: Path, *, enabled: bool = True, compiled: bool = True, bad_verifier: bool = False):
    contract = {
        "type": "PMP_UNIVERSAL_AUTOMATED_PLAN_CONTRACT",
        "version": "1.0.0",
        "schema_registry": {
            "result_envelope": {
                "schema_id": "pmp.automated-plan.result.v1",
                "required_fields": ["schema_id", "plan_id", "unit_id", "request_id", "backend_id", "status", "proposal_only", "output_paths", "evidence_used", "usage", "verification_claims"],
                "allowed_statuses": ["proposed", "needs_more_evidence", "blocked", "failed"]
            }
        }
    }
    policy = {
        "cost_policy": {
            "spending_ceiling_usd": 0,
            "paid_api_allowed": False,
            "paid_fallback_allowed": False,
            "automatic_cost_escalation_allowed": False
        },
        "execution_backends": [
            {"backend_id": "github_models_free"},
            {"backend_id": "local_ollama"}
        ]
    }
    state = {
        "type": "PMP_AUTOMATED_PLAN_ACTIVE_STATE",
        "schema_id": "pmp.automated-plan.state.v1",
        "schema_version": "1.0.0",
        "contract_path": "automation/engine/v1/universal-contract.json",
        "active_plan_id": "packet_01_5",
        "active_plan_path": "automation/plans/packet-01-5.v1.json",
        "active_plan_version": "1.0.0",
        "status": "ready" if enabled else "setup",
        "execution_enabled": enabled,
        "checkpoint": {
            "schema_id": "pmp.automated-plan.checkpoint.v1",
            "authoritative_main_at_registration": "b" * 40,
            "last_completed_boundary": "pass_002",
            "last_verified_unit": "pass_002",
            "next_unit": "pass_003",
            "checkpoint_sequence": 0,
            "resume_requires_live_main_reverification": True
        },
        "execution": {
            "selected_backend": "github_models_free",
            "allowed_backends": ["github_models_free", "local_ollama"],
            "auto_resume_enabled": enabled,
            "paid_fallback_allowed": False,
            "spending_ceiling_usd": 0
        }
    }
    commands = [["python3", "-c", "from pathlib import Path; assert Path('generated/result.txt').read_text() == 'verified\\n'"]]
    if bad_verifier:
        commands = [["python3", "-c", "from pathlib import Path; Path('outside.txt').write_text('bad')"]]
    units = []
    if compiled:
        units = [{
            "unit_id": "pass_003",
            "objective": "Create one verified fixture output.",
            "evidence_paths": ["evidence/input.txt"],
            "output_allowlist": ["generated/result.txt"],
            "verification_commands": commands,
            "next_unit": "pass_004"
        }, {
            "unit_id": "pass_004",
            "objective": "Second unit must not run in the same event.",
            "evidence_paths": ["generated/result.txt"],
            "output_allowlist": ["generated/second.txt"],
            "verification_commands": [["python3", "-c", "from pathlib import Path; assert Path('generated/second.txt').exists()"]],
            "next_unit": None
        }]
    plan = {
        "type": "PMP_UNIVERSAL_AUTOMATED_PLAN",
        "schema_id": "pmp.automated-plan.plan.v1",
        "schema_version": "1.0.0",
        "contract_path": "automation/engine/v1/universal-contract.json",
        "plan_id": "packet_01_5",
        "plan_version": "1.0.0",
        "internal_name": "Packet 01.5",
        "user_facing_main_entry": "Automated Plan",
        "plan_status": "compiled" if compiled else "registered_not_compiled",
        "execution_enabled": enabled,
        "continuity": {"last_completed_boundary": "pass_002", "next_declared_boundary": "pass_003"},
        "backend_policy": {"allowed_backends": ["github_models_free", "local_ollama"], "paid_fallback_allowed": False},
        "result_schema_id": "pmp.automated-plan.result.v1",
        "compiled_units": units,
        "stop_conditions": [],
        "foundation_rule": "fixture"
    }
    dump(root / "automation/engine/v1/universal-contract.json", contract)
    dump(root / "automation/engine/v1/engine-policy.json", policy)
    dump(root / "automation/state/active-plan.json", state)
    dump(root / "automation/plans/packet-01-5.v1.json", plan)
    (root / "automation/controller/v1").mkdir(parents=True, exist_ok=True)
    (root / "automation/controller/v1/controller-contract.json").write_text((ROOT / "automation/controller/v1/controller-contract.json").read_text(), encoding="utf-8")
    (root / "evidence").mkdir(parents=True, exist_ok=True)
    (root / "evidence/input.txt").write_text("source evidence\n", encoding="utf-8")


def prepare(root: Path, runtime: Path, out: Path, *, action="run_one", backend="github_models_free", supervised=True, sha=MAIN_SHA):
    return controller.prepare_event(Namespace(
        definition_root=root,
        runtime_root=runtime,
        live_main_sha=sha,
        action=action,
        backend=backend,
        supervised=supervised,
        automatic=False,
        out_dir=out,
    ))


def successful_transport(decision: dict):
    result = {
        "schema_id": "pmp.automated-plan.result.v1",
        "plan_id": decision["plan_id"],
        "unit_id": decision["unit_id"],
        "request_id": decision["request_id"],
        "backend_id": decision["backend_id"],
        "status": "proposed",
        "proposal_only": True,
        "output_paths": ["generated/result.txt"],
        "evidence_used": ["evidence/input.txt"],
        "usage": {},
        "verification_claims": ["fixture verifier"],
        "proposals": [{"path": "generated/result.txt", "content": "verified\n"}]
    }
    return controller.transport_result("ok", backend_id=decision["backend_id"], request_id=decision["request_id"], content=json.dumps(result), usage={"input_tokens": 10, "output_tokens": 5}, http_status=200)


class ControllerTests(unittest.TestCase):
    def test_real_boundary_stays_locked_and_uncompiled(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); fixture(root, enabled=False, compiled=False)
            with self.assertRaises(controller.ControllerError) as ctx:
                prepare(root, root / "runtime", root / "out")
            self.assertEqual(ctx.exception.reason, "execution_disabled")

    def test_automatic_event_cannot_run_first_unit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); fixture(root)
            with self.assertRaises(controller.ControllerError) as ctx:
                controller.prepare_event(Namespace(definition_root=root, runtime_root=root / "runtime", live_main_sha=MAIN_SHA, action="resume", backend="github_models_free", supervised=False, automatic=True, out_dir=root / "out"))
            self.assertEqual(ctx.exception.reason, "manual_stop_requested")

    def test_first_real_unit_requires_supervision(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); fixture(root)
            with self.assertRaises(controller.ControllerError) as ctx:
                prepare(root, root / "runtime", root / "out", supervised=False)
            self.assertEqual(ctx.exception.reason, "manual_stop_requested")

    def test_one_unit_verified_and_checkpoint_advances_once(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); runtime = root / "runtime"; out = root / "prepare"; verified_out = root / "verified"
            fixture(root)
            prepare(root, runtime, out)
            decision = json.loads((out / "decision.json").read_text())
            self.assertEqual(decision["unit_id"], "pass_003")
            transport_path = root / "transport.json"
            dump(transport_path, successful_transport(decision))
            controller.verify_event(Namespace(definition_root=root, runtime_root=runtime, live_main_sha=MAIN_SHA, decision=out / "decision.json", transport=transport_path, out_dir=verified_out))
            verified = json.loads((verified_out / "verified.json").read_text())
            self.assertEqual(verified["runtime_candidate"]["checkpoint"]["last_verified_unit"], "pass_003")
            self.assertEqual(verified["runtime_candidate"]["checkpoint"]["next_unit"], "pass_004")
            self.assertEqual(verified["runtime_candidate"]["checkpoint"]["checkpoint_sequence"], 1)
            controller.persist_event(Namespace(definition_root=root, runtime_root=runtime, live_main_sha=MAIN_SHA, verified=verified_out / "verified.json"))
            persisted = json.loads((runtime / "status.json").read_text())
            self.assertEqual(persisted["checkpoint"]["next_unit"], "pass_004")
            self.assertTrue((runtime / persisted["verified_overlay"]["generated/result.txt"]["runtime_path"]).is_file())
            self.assertFalse((root / "generated/result.txt").exists(), "proposal must not be applied to authoritative main")

    def test_rate_limit_pauses_same_unit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); runtime = root / "runtime"; out = root / "prepare"; verified_out = root / "verified"
            fixture(root); prepare(root, runtime, out)
            decision = json.loads((out / "decision.json").read_text())
            transport = controller.transport_result("rate_limited", backend_id=decision["backend_id"], request_id=decision["request_id"], error="limit", retry_after_seconds=60, http_status=429)
            dump(root / "transport.json", transport)
            controller.verify_event(Namespace(definition_root=root, runtime_root=runtime, live_main_sha=MAIN_SHA, decision=out / "decision.json", transport=root / "transport.json", out_dir=verified_out))
            candidate = json.loads((verified_out / "verified.json").read_text())["runtime_candidate"]
            self.assertEqual(candidate["status"], "paused")
            self.assertEqual(candidate["pause"]["reason"], "free_limit_reached")
            self.assertEqual(candidate["checkpoint"]["next_unit"], "pass_003")

    def test_backend_switch_preserves_checkpoint(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); runtime = root / "runtime"; out = root / "prepare"; verified_out = root / "verified"
            fixture(root)
            prepare(root, runtime, out, action="switch_backend", backend="local_ollama", supervised=False)
            controller.verify_event(Namespace(definition_root=root, runtime_root=runtime, live_main_sha=MAIN_SHA, decision=out / "decision.json", transport=None, out_dir=verified_out))
            controller.persist_event(Namespace(definition_root=root, runtime_root=runtime, live_main_sha=MAIN_SHA, verified=verified_out / "verified.json"))
            status = json.loads((runtime / "status.json").read_text())
            self.assertEqual(status["selected_backend"], "local_ollama")
            self.assertEqual(status["checkpoint"]["next_unit"], "pass_003")
            self.assertEqual(status["checkpoint"]["checkpoint_sequence"], 0)

    def test_paid_provider_credential_stops(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"OPENAI_API_KEY": "forbidden"}, clear=False):
            root = Path(d); fixture(root)
            with self.assertRaises(controller.ControllerError) as ctx:
                prepare(root, root / "runtime", root / "out")
            self.assertEqual(ctx.exception.reason, "paid_path_detected")

    def test_proposal_path_traversal_stops(self):
        decision = {"plan_id": "packet_01_5", "unit_id": "pass_003", "request_id": "r", "backend_id": "github_models_free", "unit": {"output_allowlist": ["generated"]}}
        result = {
            "schema_id": "pmp.automated-plan.result.v1", "plan_id": "packet_01_5", "unit_id": "pass_003", "request_id": "r", "backend_id": "github_models_free", "status": "proposed", "proposal_only": True,
            "output_paths": ["../escape.txt"], "evidence_used": [], "usage": {}, "verification_claims": [], "proposals": [{"path": "../escape.txt", "content": "x"}]
        }
        with self.assertRaises(controller.ControllerError) as ctx:
            controller.validate_model_result(json.dumps(result), decision, {"usage": {}})
        self.assertEqual(ctx.exception.reason, "changed_file_outside_allowlist")

    def test_verifier_cannot_change_outside_allowlist(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); runtime = root / "runtime"; out = root / "prepare"; verified_out = root / "verified"
            fixture(root, bad_verifier=True); prepare(root, runtime, out)
            decision = json.loads((out / "decision.json").read_text())
            dump(root / "transport.json", successful_transport(decision))
            with self.assertRaises(controller.ControllerError) as ctx:
                controller.verify_event(Namespace(definition_root=root, runtime_root=runtime, live_main_sha=MAIN_SHA, decision=out / "decision.json", transport=root / "transport.json", out_dir=verified_out))
            self.assertEqual(ctx.exception.reason, "changed_file_outside_allowlist")

    def test_main_change_after_pin_stops(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); runtime = root / "runtime"; fixture(root)
            bundle = controller.load_bundle(root)
            status = controller.initial_runtime(bundle)
            status["pinned_main_sha"] = MAIN_SHA
            status["first_run_completed"] = True
            dump(runtime / "status.json", status)
            with self.assertRaises(controller.ControllerError) as ctx:
                prepare(root, runtime, root / "out", sha="c" * 40)
            self.assertEqual(ctx.exception.reason, "authoritative_main_changed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
