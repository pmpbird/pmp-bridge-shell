#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import pathlib
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
WORKFLOW_PATH = REPO_ROOT / ".github/workflows/pass2-p2c-receipt038-static-preflight.yml"
CURRENT_AUTHORITY_PATH = pathlib.Path(__file__).resolve().parent / "P2C_POST_FAILURE_STATIC_PREFLIGHT_CURRENT_AUTHORITY_RECEIPT_001.json"
MODE_CONTRACT_PATH = pathlib.Path(__file__).resolve().parent / "P2C_STATIC_PREFLIGHT_MODE_CONTRACT_001.json"


import static_preflight_modes_001 as checker
contract = json.loads(MODE_CONTRACT_PATH.read_text(encoding="utf-8"))
trigger_path = contract["formal_proof_trigger_path"]
descriptor = contract["allowed_exact_head_seals"][0]


def valid_seal() -> dict:
    return {
        "status": "SEALED_EXACT_FINAL_PR_HEAD",
        "sealed_parent_commit": descriptor["sealed_parent_commit"],
        "directive_path": descriptor["directive_path"],
        "directive_git_blob_sha": descriptor["directive_git_blob_sha"],
        "directive_sha256": descriptor["directive_sha256"],
        "authorization_receipt_sha256": descriptor["authorization_receipt_sha256"],
        "proof_run_count_authorized": 1,
        "proof_run_count_executed": 0,
        "rerun_authorized": False,
        "second_proof_run_authorized": False,
        "merge_authorized": False,
        "production_activation_authorized": False,
    }


class StaticPreflightModeTests(unittest.TestCase):
    def assert_code(self, expected_code: str, function, *args, **kwargs) -> None:
        with self.assertRaises(checker.StaticPreflightError) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.code, expected_code)

    def test_mode_selection_is_explicit_from_diff(self) -> None:
        self.assertEqual(checker.select_mode(["README.md"], trigger_path), checker.MODE_MAINTENANCE)
        self.assertEqual(checker.select_mode([trigger_path], trigger_path), checker.MODE_EXACT_HEAD_SEAL)

    def test_maintenance_mode_accepts_trigger_absent(self) -> None:
        checker.validate_mode_shape(checker.MODE_MAINTENANCE, ["README.md"], trigger_path)

    def test_exact_head_seal_mode_accepts_one_allowed_path(self) -> None:
        checker.validate_mode_shape(checker.MODE_EXACT_HEAD_SEAL, [trigger_path], trigger_path)

    def test_extra_changed_path_fails_closed(self) -> None:
        self.assert_code(
            "EXACT_HEAD_SEAL_DIFF_NOT_EXACTLY_ONE_ALLOWED_PATH",
            checker.validate_mode_shape,
            checker.MODE_EXACT_HEAD_SEAL,
            [trigger_path, "README.md"],
            trigger_path,
        )

    def test_unexpected_mode_fails_closed(self) -> None:
        self.assert_code("UNEXPECTED_STATIC_PREFLIGHT_MODE", checker.validate_mode_shape, "unexpected", ["README.md"], trigger_path)

    def test_wrong_parent_fails_closed(self) -> None:
        self.assert_code(
            "EXACT_HEAD_SEAL_PARENT_NOT_PULL_REQUEST_BASE",
            checker.validate_seal_document,
            valid_seal(),
            descriptor,
            base_sha=descriptor["sealed_parent_commit"],
            head_parent="0" * 40,
            actual_sha256=descriptor["sha256"],
            actual_git_blob_sha=descriptor["git_blob_sha"],
            actual_directive_sha256=descriptor["directive_sha256"],
            actual_directive_git_blob_sha=descriptor["directive_git_blob_sha"],
            actual_authorization_sha256=descriptor["authorization_receipt_sha256"],
        )

    def test_stale_receipt_binding_fails_closed(self) -> None:
        self.assert_code(
            "STALE_AUTHORIZATION_RECEIPT_SHA256_BINDING",
            checker.validate_seal_document,
            valid_seal(),
            descriptor,
            base_sha=descriptor["sealed_parent_commit"],
            head_parent=descriptor["sealed_parent_commit"],
            actual_sha256=descriptor["sha256"],
            actual_git_blob_sha=descriptor["git_blob_sha"],
            actual_directive_sha256=descriptor["directive_sha256"],
            actual_directive_git_blob_sha=descriptor["directive_git_blob_sha"],
            actual_authorization_sha256="f" * 64,
        )

    def test_stale_directive_blob_fails_closed(self) -> None:
        self.assert_code(
            "STALE_DIRECTIVE_GIT_BLOB_BINDING",
            checker.validate_seal_document,
            valid_seal(),
            descriptor,
            base_sha=descriptor["sealed_parent_commit"],
            head_parent=descriptor["sealed_parent_commit"],
            actual_sha256=descriptor["sha256"],
            actual_git_blob_sha=descriptor["git_blob_sha"],
            actual_directive_sha256=descriptor["directive_sha256"],
            actual_directive_git_blob_sha="f" * 40,
            actual_authorization_sha256=descriptor["authorization_receipt_sha256"],
        )

    def test_incorrect_seal_fails_closed(self) -> None:
        seal = valid_seal()
        seal["status"] = "NOT_A_VALID_SEAL"
        self.assert_code(
            "INCORRECT_HEAD_SEAL_STATUS",
            checker.validate_seal_document,
            seal,
            descriptor,
            base_sha=descriptor["sealed_parent_commit"],
            head_parent=descriptor["sealed_parent_commit"],
            actual_sha256=descriptor["sha256"],
            actual_git_blob_sha=descriptor["git_blob_sha"],
            actual_directive_sha256=descriptor["directive_sha256"],
            actual_directive_git_blob_sha=descriptor["directive_git_blob_sha"],
            actual_authorization_sha256=descriptor["authorization_receipt_sha256"],
        )

    def test_attempted_controller_invocation_is_rejected_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            reader = checker.GitReader(pathlib.Path(temporary), contract["static_command_policy"]["allowed_git_subcommands"])
            self.assert_code("NON_GIT_STATIC_COMMAND_REJECTED", reader.run_command, ["bash", "formal-controller.sh"])

    def test_workflow_with_formal_invocation_token_fails_closed(self) -> None:
        malicious = "jobs:\n  bad:\n    steps:\n      - run: python3 run_receipt082_exactly_one_formal_proof.sh\n"
        self.assert_code(
            "FORBIDDEN_FORMAL_EXECUTION_TOKEN_IN_STATIC_WORKFLOW",
            checker.validate_static_workflow_text,
            malicious,
            contract["forbidden_workflow_tokens"],
        )

    def test_current_authority_must_remain_consumed(self) -> None:
        current = json.loads(CURRENT_AUTHORITY_PATH.read_text(encoding="utf-8"))
        current["authorization_consumed"] = False
        self.assert_code("CURRENT_POST_FAILURE_AUTHORITY_STATE_INVALID", checker.validate_current_authority_state, current)

    def test_real_workflow_is_static_only(self) -> None:
        checker.validate_static_workflow_text(WORKFLOW_PATH.read_text(encoding="utf-8"), contract["forbidden_workflow_tokens"])


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(StaticPreflightModeTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    evidence_dir = pathlib.Path(os.environ.get("EVIDENCE_DIR", "/tmp/p2c-receipt038-static-preflight"))
    evidence_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "type": "PMP_APP_ORCHESTRATOR_P2C_STATIC_PREFLIGHT_MODE_TEST_RESULT_001",
        "status": "PASS" if result.wasSuccessful() else "FAIL",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "formal_proof_executed": False,
        "controller_invoked": False,
        "authorization_consumed": True,
        "proof_run_count_executed": 1,
    }
    (evidence_dir / "static-preflight-mode-tests-001.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    raise SystemExit(0 if result.wasSuccessful() else 1)
