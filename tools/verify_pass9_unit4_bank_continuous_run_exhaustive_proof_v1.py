#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "834f396de0869d5b1adbcdea5dbbe35722a9f581"
REPORT = ROOT / "audit/pass9/pass9-bank-continuous-run-unit4-exhaustive-proof-v1.json"
RECEIPT = ROOT / "audit/pass9/receipts/RECEIPT_P9_U4_BANK_CONTINUOUS_RUN_EXHAUSTIVE_PROOF_20260726T204000Z_001.json"
UNIT3 = ROOT / "audit/pass9/pass9-bank-continuous-run-unit3-owner-integration-v1.json"
BOUNDARY = ROOT / "pmp-bank-continuous-run-owner-boundary-v1.js"
STATE = ROOT / "pmp-continuous-run-state-bank-v1.js"
ROUTER = ROOT / "pmp-master-bank-inventory-router-v1.js"
DIAGNOSTIC = ROOT / "pmp-bank-continuous-run-owner-split-diagnostic-v1.js"
RUNNER = ROOT / "tools/run_pass9_unit4_bank_continuous_run_exhaustive_proof_v1.js"
TEST = ROOT / "tools/test_pass9_unit4_bank_continuous_run_exhaustive_proof_v1.js"
WORKFLOW = ROOT / ".github/workflows/pass9-unit4-bank-continuous-run-exhaustive-proof-v1.yml"
GATE_RUNNER = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
EXPECTED = {
    ".github/workflows/pass9-unit4-bank-continuous-run-exhaustive-proof-v1.yml",
    "audit/pass9/pass9-bank-continuous-run-unit4-exhaustive-proof-v1.json",
    "audit/pass9/receipts/RECEIPT_P9_U4_BANK_CONTINUOUS_RUN_EXHAUSTIVE_PROOF_20260726T204000Z_001.json",
    "tools/run_pass9_unit4_bank_continuous_run_exhaustive_proof_v1.js",
    "tools/test_pass9_unit4_bank_continuous_run_exhaustive_proof_v1.js",
    "tools/verify_pass9_unit4_bank_continuous_run_exhaustive_proof_v1.py",
}
SOURCE_INPUTS = {
    "unit3_integration_sha256": UNIT3,
    "owner_boundary_sha256": BOUNDARY,
    "continuous_run_state_sha256": STATE,
    "bank_router_sha256": ROUTER,
    "diagnostic_sha256": DIAGNOSTIC,
    "runner_sha256": RUNNER,
    "test_sha256": TEST,
}


def output(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed_paths(base: str) -> set[str]:
    changed: set[str] = set()
    for command in (
        ("git", "diff", "--name-only", f"{base}...HEAD"),
        ("git", "diff", "--name-only", base),
        ("git", "ls-files", "--others", "--exclude-standard"),
    ):
        changed.update(filter(None, output(*command).splitlines()))
    return changed


def workflow_paths(text: str) -> set[str]:
    match = re.search(r"(?m)^    paths:\n(?P<rows>(?:      - [^\n]+\n)+)", text)
    assert match
    return {
        row.strip()[2:].strip().strip("'\"")
        for row in match.group("rows").splitlines()
    }


def main() -> None:
    base = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else BASE
    assert base == BASE
    changed = changed_paths(base)
    assert changed == EXPECTED, (sorted(changed), sorted(EXPECTED))
    report = json.loads(REPORT.read_text())
    receipt = json.loads(RECEIPT.read_text())
    assert report["base_main_commit"] == BASE
    assert report["unit_id"] == "P9-U4"
    assert report["status"] == "BANK_CONTINUOUS_RUN_EXHAUSTIVE_BEHAVIOR_PROVEN"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == []
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["status"] == report["status"]
    for key, path in SOURCE_INPUTS.items():
        assert report["inputs"][key] == sha(path), (key, report["inputs"][key], sha(path))

    node = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"proof \((\d+)/(\d+)\)", node)
    assert match and match.group(1) == match.group(2)
    assertions = int(match.group(1))
    assert assertions == report["verification"]["assertions_passed"] == 238
    assert "(234/234)" in output(
        "node", "tools/test_pass9_unit3_bank_continuous_run_owner_integration_v1.js"
    )
    assert "(229/229)" in output(
        "node", "tools/test_pass9_unit2_bank_continuous_run_owner_contract_v1.js"
    )
    assert "(443/443)" in output(
        "node", "tools/test_pass8_unit4_helper_owner_diagnostics_integration_v1.js"
    )

    result = json.loads(output("node", str(RUNNER.relative_to(ROOT))))
    proof = report["proof"]
    assert result["status"] == "PASS"
    assert result["boot_repeated_load"]["first_calls"] == {"get": 0, "set": 0, "remove": 0}
    assert result["boot_repeated_load"]["second_calls"] == {"get": 0, "set": 0, "remove": 0}
    assert result["boot_repeated_load"]["persisted_user_data_changed"] is False
    assert result["concurrency"]["competing_code"] == proof["stale_concurrent_result"]
    assert result["concurrency"]["competing_zero_effects"] is True
    assert result["concurrency"]["receipt_chain_valid"] is True
    assert result["cancellation"]["gap_code"] == proof["cancellation_gap_result"]
    assert result["cancellation"]["stale_code"] == proof["cancellation_stale_result"]
    assert result["cancellation"]["gap_zero_effects"] is True
    assert result["cancellation"]["stale_zero_effects"] is True
    assert result["duplicate"]["conflict_code"] == proof["conflicting_duplicate_result"]
    assert result["duplicate"]["identical_replay_equal"] is True
    assert result["duplicate"]["replay_new_writes"] == proof["identical_duplicate_new_writes"] == 0
    assert result["duplicate"]["replay_new_receipts"] == proof["identical_duplicate_new_receipts"] == 0
    assert len(result["denial"]["authorize_cases"]) == proof["authorization_denial_cases"] == 16
    assert len(result["denial"]["commit_cases"]) + 1 == proof["commit_denial_cases"] == 5
    assert result["denial"]["all_codes_exact"] is True
    assert result["denial"]["all_denials_zero_effect"] is True
    assert result["denial"]["persisted_bytes_unchanged"] is True
    assert result["atomic_rollback"]["existing_keys_exact_restore"] is True
    assert result["atomic_rollback"]["new_key_exact_restore"] is True
    assert result["atomic_rollback"]["absent_key_remains_absent"] is True
    assert result["restart_handoff"]["restart_load_reads"] == 0
    assert result["restart_handoff"]["restart_load_writes"] == 0
    assert result["restart_handoff"]["restart_load_deletes"] == 0
    assert result["restart_handoff"]["persisted_bytes_unchanged_by_restart_load"] is True
    assert result["restart_handoff"]["resume_code"] == "COMMITTED"
    assert result["restart_handoff"]["corrupted_read_fails_closed_in_memory"] is True
    assert result["restart_handoff"]["corrupted_raw_bytes_preserved"] is True
    assert result["router_diagnostics"]["default_delete_code"] == proof["default_delete_result"]
    assert result["router_diagnostics"]["wrong_delete_code"] == proof["wrong_capability_delete_result"]
    assert result["router_diagnostics"]["exact_delete_code"] == proof["exact_confirmed_delete_result"]
    assert result["router_diagnostics"]["diagnostic_writes"] == 0
    assert result["router_diagnostics"]["diagnostic_report_auto_written"] is False
    assert result["bounded_receipts"]["commits"] == proof["bounded_receipt_commits"] == 260
    assert result["bounded_receipts"]["receipt_count"] == proof["retained_receipts"] == 256
    assert result["bounded_receipts"]["visible_receipts"] == proof["visible_diagnostic_receipts"] == 32
    assert result["bounded_receipts"]["visible_chain_valid"] is True
    assert result["source_policy"]["all_pass"] is True
    assert len(result["source_policy"]["policies"]) == proof["source_policy_checks"] == 14
    assert all(value is False for value in result["effects"].values())

    matrix = report["diagnostic_and_proof_matrix"]
    assert len(matrix["invariants"]) == 10
    assert matrix["assertions"] == 238
    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "deterministic_integration"
    assert binding["diagnostic_matrix_update"]["status"] == "ADDED"
    assert binding["diagnostic_matrix_update"]["applicable_matrix"] == REPORT.relative_to(ROOT).as_posix()
    assert binding["fault_injection"]["status"] == "COVERED"
    assert len(binding["fault_injection"]["cases"]) == 31
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    gate = json.loads(output("python3", str(GATE_RUNNER.relative_to(ROOT)), "--base", BASE))
    assert gate["status"] == "PASS", gate
    assert gate["unit_id"] == "P9-U4"
    assert gate["gate_records"] == 1
    assert gate["summary"]["runtime_paths"] == 0
    assert gate["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for required in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete P9-U4 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert required in workflow
    assert workflow.index("Upload complete P9-U4 evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )
    assert all(value is False for value in report["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["next_step"]["id"] == "P9-U5"
    assert report["next_step"]["requires_user_app_check"] is False
    assert receipt["next_safe_move"]["step_id"] == "P9-U5"
    print(
        "PASS: exact six-file P9-U4 Bank/Continuous Run exhaustive "
        f"behavior proof verified ({assertions}/{assertions}, gate PASS)"
    )


if __name__ == "__main__":
    main()
