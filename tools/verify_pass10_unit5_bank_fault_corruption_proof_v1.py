#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "d7da9baa10de4492295569c675f95b7ee5d9146b"
REPORT = ROOT / "audit/pass10/pass10-bank-unit5-fault-corruption-proof-v1.json"
RECEIPT = (
    ROOT
    / "audit/pass10/receipts/"
    "RECEIPT_P10_U5_BANK_FAULT_CORRUPTION_PROOF_20260726T233000Z_001.json"
)
WORKFLOW = ROOT / ".github/workflows/pass10-unit5-bank-fault-corruption-proof-v1.yml"
UNIT1 = ROOT / "audit/pass10/pass10-bank-unit1-inventory-reconciliation-v1.json"
UNIT2 = ROOT / "audit/pass10/pass10-bank-unit2-inventory-contract-v1.json"
UNIT3 = ROOT / "audit/pass10/pass10-bank-unit3-readonly-projection-v1.json"
UNIT4 = ROOT / "audit/pass10/pass10-bank-unit4-owner-projection-refresh-v1.json"
BOUNDARY = ROOT / "pmp-bank-continuous-run-owner-boundary-v1.js"
PROJECTION = ROOT / "pmp-bank-inventory-readonly-projection-v1.js"
ADAPTER = ROOT / "pmp-bank-owner-projection-refresh-v1.js"
MASTER = ROOT / "pmp-master-bank-tab-v1.js"
INNER = ROOT / "pmp-current-inner-cleanbug-rgcontrols-v23.html"
RUNNER = ROOT / "tools/run_pass10_unit5_bank_fault_corruption_proof_v1.js"
TEST = ROOT / "tools/test_pass10_unit5_bank_fault_corruption_proof_v1.js"
UNIT4_TEST = ROOT / "tools/test_pass10_unit4_bank_owner_projection_refresh_v1.js"
UNIT3_TEST = ROOT / "tools/test_pass10_unit3_bank_readonly_projection_v1.js"
GATE = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
EXPECTED = {
    ".github/workflows/pass10-unit5-bank-fault-corruption-proof-v1.yml",
    "audit/pass10/pass10-bank-unit5-fault-corruption-proof-v1.json",
    (
        "audit/pass10/receipts/"
        "RECEIPT_P10_U5_BANK_FAULT_CORRUPTION_PROOF_20260726T233000Z_001.json"
    ),
    "tools/run_pass10_unit5_bank_fault_corruption_proof_v1.js",
    "tools/test_pass10_unit5_bank_fault_corruption_proof_v1.js",
    "tools/verify_pass10_unit5_bank_fault_corruption_proof_v1.py",
}
INPUTS = {
    "unit1_report_sha256": UNIT1,
    "unit2_report_sha256": UNIT2,
    "unit3_report_sha256": UNIT3,
    "unit4_report_sha256": UNIT4,
    "owner_boundary_sha256": BOUNDARY,
    "readonly_projection_sha256": PROJECTION,
    "owner_refresh_adapter_sha256": ADAPTER,
    "bank_tab_sha256": MASTER,
    "active_inner_sha256": INNER,
    "runner_sha256": RUNNER,
    "test_sha256": TEST,
}


def output(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed_paths(base: str) -> set[str]:
    rows: set[str] = set()
    for command in (
        ("git", "diff", "--name-only", f"{base}...HEAD"),
        ("git", "diff", "--name-only", base),
        ("git", "ls-files", "--others", "--exclude-standard"),
    ):
        rows.update(filter(None, output(*command).splitlines()))
    return rows


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
    actual = changed_paths(base)
    assert actual == EXPECTED, (sorted(actual), sorted(EXPECTED))

    report = json.loads(REPORT.read_text())
    receipt = json.loads(RECEIPT.read_text())
    assert report["base_main_commit"] == BASE
    assert report["unit_id"] == "P10-U5"
    assert report["status"] == (
        "BANK_FAULT_ROLLBACK_AND_CORRUPTION_CONTAINMENT_PROVEN"
    )
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == []
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["status"] == report["status"]
    for key, path in INPUTS.items():
        assert report["inputs"][key] == sha(path), (
            key,
            report["inputs"][key],
            sha(path),
        )

    test_output = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"containment \((\d+)/(\d+)\)", test_output)
    assert match and match.group(1) == match.group(2) == "133", test_output
    assertions = int(match.group(1))
    assert report["verification"]["assertions_total"] == assertions
    assert report["verification"]["assertions_passed"] == assertions
    assert report["verification"]["assertions_failed"] == 0
    assert receipt["coverage"]["assertions"] == assertions
    assert "(121/121)" in output("node", str(UNIT4_TEST.relative_to(ROOT)))
    assert "(125/125)" in output("node", str(UNIT3_TEST.relative_to(ROOT)))

    result = json.loads(output("node", str(RUNNER.relative_to(ROOT))))
    assert result["status"] == report["status"]
    chain = result["evidence_chain"]
    assert [row["unit"] for row in chain["units"]] == [
        "P10-U1",
        "P10-U2",
        "P10-U3",
        "P10-U4",
    ]
    assert chain["exact_progression"] == [
        "P10-U2",
        "P10-U3",
        "P10-U4",
        "P10-U5",
    ]
    assert chain["assertions_by_unit"] == [110, 187, 125, 121]
    assert chain["cumulative_prior_assertions"] == 543
    assert chain["all_permanent_gates_bound"] is True

    large = result["large_inventory"]
    assert large["fixture_records"] == 2048
    assert large["projected_items_first"] == 2048
    assert large["projected_items_second"] == 2048
    assert large["unique_ids"] == 2048
    assert large["stable_ids"] is True
    assert large["exact_bytes_after_first"] is True
    assert large["exact_bytes_after_second"] is True
    assert large["unrelated_bytes_preserved"] is True
    assert large["load_calls"] == {
        "get": 0,
        "set": 0,
        "remove": 0,
        "key": 0,
    }
    assert large["first_effects"]["storage_writes"] == 0
    assert large["first_effects"]["storage_deletes"] == 0
    assert large["second_effects"]["storage_writes"] == 0
    assert large["second_effects"]["storage_deletes"] == 0
    assert large["raw_payloads_exposed"] == 0

    duplicate = result["duplicate_and_collision"]
    assert duplicate["projected_collision_items"] == 2
    assert duplicate["all_quarantined"] is True
    assert duplicate["all_collision_marked"] is True
    assert duplicate["payload_hashes_distinct"] == 2
    assert duplicate["duplicate_owner_event_denied"] is True
    assert duplicate["duplicate_projection_refreshes"] == 1
    assert duplicate["duplicate_bytes_unchanged"] is True

    fault = result["orphan_and_corruption"]
    assert fault["corrupt_items"] == 1
    assert fault["corrupt_quarantined"] is True
    assert fault["corrupt_raw_bytes_preserved"] is True
    assert fault["orphan_items"] == 1
    assert fault["orphan_quarantined"] is True
    assert fault["orphan_owner_null"] is True
    assert fault["orphan_raw_bytes_preserved"] is True
    assert fault["snapshot_zero_writes"] is True
    assert fault["snapshot_zero_deletes"] is True
    assert fault["all_fault_bytes_preserved"] is True
    assert fault["unrelated_bytes_preserved"] is True

    unavailable = result["stale_and_unavailable"]
    assert unavailable["stale_commit_denied"] is True
    assert unavailable["stale_code"] == "DENIED_EXPECTED_VERSION"
    assert all(
        unavailable["stale_effects"][key] in (0, False)
        for key in (
            "storage_writes",
            "storage_deletes",
            "persisted_user_data_changed",
        )
    )
    assert unavailable["stale_bytes_unchanged"] is True
    assert unavailable["unavailable_projection_items"] == 0
    assert unavailable["unavailable_commit_denied"] is True
    assert unavailable["unavailable_commit_code"] == "DENIED_STORAGE_UNAVAILABLE"
    assert all(
        unavailable["unavailable_commit_effects"][key] in (0, False)
        for key in (
            "storage_writes",
            "storage_deletes",
            "persisted_user_data_changed",
        )
    )
    assert unavailable["unavailable_storage_calls"] == {
        "get": 0,
        "set": 0,
        "remove": 0,
        "key": 0,
    }

    rollback = result["atomic_rollback"]
    assert rollback["result_code"] == "DENIED_ATOMIC_WRITE_FAILED"
    assert rollback["exact_bytes_restored"] is True
    assert rollback["existing_first_key_restored"] is True
    assert rollback["existing_second_key_preserved"] is True
    assert rollback["unrelated_bytes_preserved"] is True
    assert rollback["resource_version"] == 0
    assert rollback["receipt_count"] == 0

    restart = result["accepted_and_restart"]
    assert restart["accepted_code"] == "COMMITTED"
    assert restart["accepted_refreshes"] == 1
    assert restart["accepted_item_visible"] is True
    assert restart["restart_load_delta"] == {
        "get": 0,
        "set": 0,
        "remove": 0,
        "key": 0,
    }
    assert restart["restart_snapshot_items"] == 1
    assert restart["restart_item_visible"] is True
    assert restart["restart_item_id_matches"] is True
    assert restart["restart_snapshot_zero_writes"] is True
    assert restart["restart_snapshot_zero_deletes"] is True
    assert restart["restart_bytes_unchanged"] is True
    assert restart["restart_adapter_refreshes"] == 0

    safety = result["active_safety"]
    for key in (
        "boundary_only_writer_rule",
        "projection_unknown_policy",
        "projection_historic_policy",
        "adapter_receipt_hash_validation",
        "adapter_boundary_receipt_validation",
        "adapter_duplicate_denial",
        "adapter_stale_denial",
        "tab_raw_owner_listener_absent",
        "tab_sanitized_listener_present",
        "tab_cached_projection",
    ):
        assert safety[key] is True, key
    for key in (
        "one_boundary_load",
        "one_projection_load",
        "one_adapter_load",
        "one_tab_load",
    ):
        assert safety[key] == 1, key
    assert safety["recurring_timers"] == 0
    assert safety["adapter_write_api"] is False
    assert safety["adapter_delete_api"] is False
    assert safety["adapter_migration_api"] is False

    decision = result["observation_decision_input"]
    assert len(decision["deterministic_fault_cases"]) == 12
    assert decision["unresolved_deterministic_failures"] == 0
    assert decision["user_app_check_required_now"] is False
    assert decision["bounded_observation_performed"] is False
    assert decision["bounded_observation_authority_consumed"] is False
    assert decision["next_unit_may_decide_rehearsal_without_observation"] is True
    assert all(value is False for value in result["effects"].values())

    proof = report["proof"]
    assert proof["assertions"] == assertions
    assert proof["large_inventory_records"] == 2048
    assert proof["large_inventory_unique_stable_identities"] == 2048
    assert proof["atomic_rollback_exact_bytes_restored"] is True
    assert proof["restart_identity_stable"] is True
    assert proof["unresolved_deterministic_failures"] == 0
    assert len(report["fault_matrix"]) == 12
    assert all(row["result"] == "PASS" for row in report["fault_matrix"])

    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "deterministic_integration"
    assert binding["diagnostic_matrix_update"]["status"] == "ADDED"
    assert len(binding["fault_injection"]["cases"]) == 12
    assert len(binding["observed_facts"]) == 1
    assert len(binding["inferred_conclusions"]) == 1
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    assert binding["special_authority"] == {
        "required": False,
        "granted": False,
        "consumed": False,
    }
    gate = json.loads(
        output("python3", str(GATE.relative_to(ROOT)), "--base", BASE)
    )
    assert gate["status"] == "PASS", gate
    assert gate["unit_id"] == "P10-U5"
    assert gate["summary"]["runtime_paths"] == 0
    assert gate["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for token in (
        "actions/setup-node@v4",
        "node-version: '22'",
        "actions/setup-python@v5",
        "python-version: '3.12'",
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete P10-U5 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert token in workflow
    assert workflow.index("Upload complete P10-U5 evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )

    assert all(value is False for value in report["effects"].values())
    assert all(value is False for value in receipt["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["next_step"]["id"] == "P10-U6"
    assert report["next_step"]["requires_user_app_check"] is False
    assert report["next_step"]["persisted_user_data_change_allowed"] is False
    assert report["next_step"]["production_migration_allowed"] is False
    assert receipt["next_safe_move"]["step_id"] == "P10-U6"
    assert receipt["next_safe_move"]["requires_user_app_check"] is False
    print(
        "PASS: exact six-file P10-U5 Bank fault, rollback, restart, and "
        "corruption-containment proof verified "
        "(133/133, P10-U4 121/121, P10-U3 125/125, gate PASS, P10-U6 ready)"
    )


if __name__ == "__main__":
    main()
