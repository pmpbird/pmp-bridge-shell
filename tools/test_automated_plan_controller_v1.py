#!/usr/bin/env python3
from __future__ import annotations

import copy
import datetime as dt
import importlib.util
import json
import os
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("controller", ROOT / "automation/controller/v1/controller.py")
controller = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(controller)
MAIN_SHA = "b" * 40


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def fixture(root: Path, *, enabled: bool = True, compiled: bool = True, next_unit: str = "pass_003") -> None:
    contract = json.loads((ROOT / "automation/controller/v1/controller-contract.json").read_text())
    policy = json.loads((ROOT / "automation/engine/v1/engine-policy.json").read_text())
    dump(root / "automation/controller/v1/controller-contract.json", contract)
    dump(root / "automation/engine/v1/engine-policy.json", policy)
    dump(root / "automation/engine/v1/universal-contract.json", {
        "schema_registry": {"result_envelope": {"required_fields": ["schema_id", "plan_id", "unit_id", "request_id", "backend_id", "status", "proposal_only", "output_paths", "evidence_used", "usage", "verification_claims"], "allowed_statuses": ["proposed", "needs_more_evidence", "blocked", "failed"]}}
    })
    unit = {
        "unit_id": "pass_003",
        "objective": "Produce one verified fixture file.",
        "evidence_paths": ["evidence.txt"],
        "output_allowlist": ["generated"],
        "verification_artifact_allowlist": [],
        "verification_commands": [["python3", "-c", "from pathlib import Path; assert Path('generated/result.txt').read_text() == 'verified\\n'"]],
        "next_unit": "pass_004"
    }
    dump(root / "automation/plans/packet-01-5.v1.json", {
        "plan_id": "packet_01_5", "plan_version": "1.0.0",
        "backend_policy": {"paid_fallback_allowed": False},
        "execution_enabled": enabled,
        "compiled_units": [unit] if compiled else []
    })
    dump(root / "automation/state/active-plan.json", {
        "contract_path": "automation/engine/v1/universal-contract.json",
        "active_plan_id": "packet_01_5", "active_plan_version": "1.0.0",
        "active_plan_path": "automation/plans/packet-01-5.v1.json",
        "execution_enabled": enabled,
        "checkpoint": {"schema_id": "pmp.automated-plan.checkpoint.v1", "authoritative_main_at_registration": "a" * 40, "last_completed_boundary": "pass_002", "last_verified_unit": "pass_002", "next_unit": next_unit, "checkpoint_sequence": 0, "resume_requires_live_main_reverification": True},
        "execution": {"selected_backend": "github_models_free", "allowed_backends": ["github_models_free", "local_ollama"], "auto_resume_enabled": False}
    })
    (root / "evidence.txt").write_text("fixture evidence\n", encoding="utf-8")


def billing_env() -> dict[str, str]:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "PMP_GITHUB_MODELS_PAID_USAGE_DISABLED": "true",
        "PMP_GITHUB_MODELS_BILLING_SCOPE": "personal:pmpbird",
        "PMP_GITHUB_MODELS_BILLING_VERIFIED_AT": now,
    }


def prepare(root: Path, runtime: Path, out: Path, *, action: str = "run_one", backend: str = "github_models_free", supervised: bool = True, automatic: bool = False, sha: str = MAIN_SHA, env: dict[str, str] | None = None):
    with mock.patch.dict(os.environ, env if env is not None else billing_env(), clear=False):
        return controller.prepare_event(Namespace(definition_root=root, runtime_root=runtime, live_main_sha=sha, action=action, backend=backend, supervised=supervised, automatic=automatic, out_dir=out))


def successful_transport(decision: dict) -> dict:
    result = {
        "schema_id": controller.RESULT_SCHEMA, "plan_id": decision["plan_id"], "unit_id": decision["unit_id"],
        "request_id": decision["request_id"], "backend_id": decision["backend_id"], "status": "proposed",
        "proposal_only": True, "output_paths": ["generated/result.txt"], "evidence_used": [], "usage": {},
        "verification_claims": ["fixture"], "proposals": [{"path": "generated/result.txt", "content": "verified\n"}]
    }
    return controller.transport_result("ok", backend_id=decision["backend_id"], request_id=decision["request_id"], content=json.dumps(result), usage={"input_tokens": 10, "output_tokens": 5}, http_status=200)


def fake_container(workspace: Path, commands, timeout, contract):
    for command in commands:
        proc = __import__('subprocess').run(command, cwd=workspace, text=True, capture_output=True, timeout=timeout)
        if proc.returncode:
            raise controller.ControllerError("deterministic_verification_failed", proc.stderr)
    return [{"containerized": True, "network": "none", "root_filesystem": "read_only", "exit_code": 0} for _ in commands]


def verified_cycle(root: Path, runtime: Path, prepared: Path, verified_out: Path):
    decision = json.loads((prepared / "decision.json").read_text())
    transport = successful_transport(decision)
    transport_path = root / "transport.json"
    dump(transport_path, transport)
    with mock.patch.object(controller, "run_verification_commands", fake_container):
        controller.verify_event(Namespace(definition_root=root, runtime_root=runtime, live_main_sha=MAIN_SHA, decision=prepared / "decision.json", transport=transport_path, out_dir=verified_out))
    return decision, transport_path


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
                prepare(root, root / "runtime", root / "out", action="resume", supervised=False, automatic=True)
            self.assertEqual(ctx.exception.reason, "manual_stop_requested")

    def test_first_real_unit_requires_supervision(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); fixture(root)
            with self.assertRaises(controller.ControllerError) as ctx:
                prepare(root, root / "runtime", root / "out", supervised=False)
            self.assertEqual(ctx.exception.reason, "manual_stop_requested")

    def test_hosted_run_requires_account_billing_attestation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); fixture(root)
            with self.assertRaises(controller.ControllerError) as ctx:
                prepare(root, root / "runtime", root / "out", env={
                    "PMP_GITHUB_MODELS_PAID_USAGE_DISABLED": "false",
                    "PMP_GITHUB_MODELS_BILLING_SCOPE": "personal:pmpbird",
                    "PMP_GITHUB_MODELS_BILLING_VERIFIED_AT": dt.datetime.now(dt.timezone.utc).isoformat(),
                })
            self.assertEqual(ctx.exception.reason, "paid_usage_setting_unverified")

    def test_stale_billing_attestation_stops(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); fixture(root)
            stale = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=40)).isoformat()
            with self.assertRaises(controller.ControllerError) as ctx:
                prepare(root, root / "runtime", root / "out", env={
                    "PMP_GITHUB_MODELS_PAID_USAGE_DISABLED": "true",
                    "PMP_GITHUB_MODELS_BILLING_SCOPE": "personal:pmpbird",
                    "PMP_GITHUB_MODELS_BILLING_VERIFIED_AT": stale,
                })
            self.assertEqual(ctx.exception.reason, "paid_usage_setting_unverified")

    def test_malformed_billing_attestation_stops_cleanly(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); fixture(root)
            with self.assertRaises(controller.ControllerError) as ctx:
                prepare(root, root / "runtime", root / "out", env={
                    "PMP_GITHUB_MODELS_PAID_USAGE_DISABLED": "true",
                    "PMP_GITHUB_MODELS_BILLING_SCOPE": "personal:pmpbird",
                    "PMP_GITHUB_MODELS_BILLING_VERIFIED_AT": "not-a-time",
                })
            self.assertEqual(ctx.exception.reason, "paid_usage_setting_unverified")

    def test_inference_rechecks_full_billing_attestation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); fixture(root); prepared = root / "prepared"
            prepare(root, root / "runtime", prepared)
            request = json.loads((prepared / "request.json").read_text())
            self.assertEqual(request["billing_gate"]["status"], "verified")
            out = root / "transport.json"
            changed = billing_env() | {"PMP_GITHUB_MODELS_BILLING_SCOPE": "personal:someone-else", "GITHUB_TOKEN": "never-used"}
            with mock.patch.dict(os.environ, changed, clear=False), mock.patch.object(controller, "post_json") as post:
                controller.infer_event(Namespace(definition_root=root, request=prepared / "request.json", out=out))
            post.assert_not_called()
            transport = json.loads(out.read_text())
            self.assertEqual(transport["status"], "blocked")
            self.assertIn("paid_usage_setting_unverified", transport["error"])

    def test_one_unit_advances_exactly_once_by_reconstruction(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); runtime = root / "runtime"; prepared = root / "prepared"; verified = root / "verified"
            fixture(root); prepare(root, runtime, prepared)
            _, transport = verified_cycle(root, runtime, prepared, verified)
            controller.persist_event(Namespace(definition_root=root, runtime_root=runtime, live_main_sha=MAIN_SHA, decision=prepared / "decision.json", transport=transport, verified=verified / "verified.json"))
            status = json.loads((runtime / "status.json").read_text())
            self.assertEqual(status["checkpoint"]["last_verified_unit"], "pass_003")
            self.assertEqual(status["checkpoint"]["next_unit"], "pass_004")
            self.assertEqual(status["checkpoint"]["checkpoint_sequence"], 1)
            self.assertFalse((root / "generated/result.txt").exists())

    def test_rate_limit_pauses_same_unit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); runtime = root / "runtime"; prepared = root / "prepared"; verified = root / "verified"
            fixture(root); prepare(root, runtime, prepared)
            decision = json.loads((prepared / "decision.json").read_text())
            transport = controller.transport_result("rate_limited", backend_id=decision["backend_id"], request_id=decision["request_id"], error="limit", retry_after_seconds=60, http_status=429)
            dump(root / "transport.json", transport)
            controller.verify_event(Namespace(definition_root=root, runtime_root=runtime, live_main_sha=MAIN_SHA, decision=prepared / "decision.json", transport=root / "transport.json", out_dir=verified))
            controller.persist_event(Namespace(definition_root=root, runtime_root=runtime, live_main_sha=MAIN_SHA, decision=prepared / "decision.json", transport=root / "transport.json", verified=verified / "verified.json"))
            status = json.loads((runtime / "status.json").read_text())
            self.assertEqual(status["checkpoint"]["next_unit"], "pass_003")
            self.assertEqual(status["checkpoint"]["checkpoint_sequence"], 0)
            self.assertEqual(status["pause"]["reason"], "free_limit_reached")

    def test_backend_switch_preserves_checkpoint(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); runtime = root / "runtime"; prepared = root / "prepared"; verified = root / "verified"
            fixture(root); prepare(root, runtime, prepared, action="switch_backend", backend="local_ollama", supervised=False, env={})
            controller.verify_event(Namespace(definition_root=root, runtime_root=runtime, live_main_sha=MAIN_SHA, decision=prepared / "decision.json", transport=None, out_dir=verified))
            controller.persist_event(Namespace(definition_root=root, runtime_root=runtime, live_main_sha=MAIN_SHA, decision=prepared / "decision.json", transport=None, verified=verified / "verified.json"))
            status = json.loads((runtime / "status.json").read_text())
            self.assertEqual(status["selected_backend"], "local_ollama")
            self.assertEqual(status["checkpoint"]["next_unit"], "pass_003")
            self.assertEqual(status["checkpoint"]["checkpoint_sequence"], 0)

    def test_paid_provider_credential_stops(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); fixture(root)
            env = billing_env() | {"OPENAI_API_KEY": "forbidden"}
            with self.assertRaises(controller.ControllerError) as ctx:
                prepare(root, root / "runtime", root / "out", env=env)
            self.assertEqual(ctx.exception.reason, "paid_path_detected")

    def test_proposal_path_traversal_stops(self):
        decision = {"plan_id": "packet_01_5", "unit_id": "pass_003", "request_id": "r", "backend_id": "github_models_free", "unit": {"output_allowlist": ["generated"]}}
        result = {"schema_id": controller.RESULT_SCHEMA, "plan_id": "packet_01_5", "unit_id": "pass_003", "request_id": "r", "backend_id": "github_models_free", "status": "proposed", "proposal_only": True, "output_paths": ["../escape.txt"], "evidence_used": [], "usage": {}, "verification_claims": [], "proposals": [{"path": "../escape.txt", "content": "x"}]}
        with self.assertRaises(controller.ControllerError) as ctx:
            controller.validate_model_result(json.dumps(result), decision, {"usage": {}})
        self.assertEqual(ctx.exception.reason, "changed_file_outside_allowlist")

    def test_tampered_proposal_is_rejected_before_persist(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); runtime = root / "runtime"; prepared = root / "prepared"; verified = root / "verified"
            fixture(root); prepare(root, runtime, prepared)
            _, transport = verified_cycle(root, runtime, prepared, verified)
            (verified / "proposals/generated/result.txt").write_text("tampered\n")
            with self.assertRaises(controller.ControllerError) as ctx:
                controller.persist_event(Namespace(definition_root=root, runtime_root=runtime, live_main_sha=MAIN_SHA, decision=prepared / "decision.json", transport=transport, verified=verified / "verified.json"))
            self.assertEqual(ctx.exception.reason, "artifact_tampering_detected")

    def test_runtime_candidate_in_receipt_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); runtime = root / "runtime"; prepared = root / "prepared"; verified = root / "verified"
            fixture(root); prepare(root, runtime, prepared, action="status", supervised=False, env={})
            controller.verify_event(Namespace(definition_root=root, runtime_root=runtime, live_main_sha=MAIN_SHA, decision=prepared / "decision.json", transport=None, out_dir=verified))
            receipt = json.loads((verified / "verified.json").read_text())
            receipt["runtime_candidate"] = {"checkpoint": {"next_unit": "pass_999"}}
            dump(verified / "verified.json", receipt)
            with self.assertRaises(controller.ControllerError) as ctx:
                controller.persist_event(Namespace(definition_root=root, runtime_root=runtime, live_main_sha=MAIN_SHA, decision=prepared / "decision.json", transport=None, verified=verified / "verified.json"))
            self.assertEqual(ctx.exception.reason, "artifact_tampering_detected")

    def test_checkpoint_jump_is_rejected_even_with_rehashed_receipt(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); runtime = root / "runtime"; prepared = root / "prepared"; verified = root / "verified"
            fixture(root); prepare(root, runtime, prepared)
            _, transport_path = verified_cycle(root, runtime, prepared, verified)
            decision = json.loads((prepared / "decision.json").read_text())
            decision["unit_id"] = "pass_999"
            decision["unit"] = copy.deepcopy(decision["unit"])
            decision["unit"]["unit_id"] = "pass_999"
            dump(prepared / "decision.json", decision)
            receipt = json.loads((verified / "verified.json").read_text())
            receipt["decision_sha256"] = controller.sha256_json(decision)
            dump(verified / "verified.json", receipt)
            with self.assertRaises(controller.ControllerError) as ctx:
                controller.persist_event(Namespace(definition_root=root, runtime_root=runtime, live_main_sha=MAIN_SHA, decision=prepared / "decision.json", transport=transport_path, verified=verified / "verified.json"))
            self.assertEqual(ctx.exception.reason, "checkpoint_jump_detected")

    def test_container_command_has_required_isolation(self):
        with tempfile.TemporaryDirectory() as d:
            contract = json.loads((ROOT / "automation/controller/v1/controller-contract.json").read_text())
            argv = controller.container_argv(Path(d), ["python3", "-c", "print('ok')"], contract)
            joined = " ".join(argv)
            for token in ("--network none", "--read-only", "--pids-limit 64", "--cap-drop ALL", "no-new-privileges:true", "--user 65534:65534"):
                self.assertIn(token, joined)


if __name__ == "__main__":
    unittest.main(verbosity=2)
