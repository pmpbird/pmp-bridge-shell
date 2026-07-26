#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "eb2b40e3023d236bda1a16c0971d92779bfcd225"
REPORT = ROOT / "audit/pass9/pass9-bank-continuous-run-unit5-authority-persisted-data-certification-v1.json"
RECEIPT = ROOT / "audit/pass9/receipts/RECEIPT_P9_U5_AUTHORITY_PERSISTED_DATA_CERTIFICATION_20260726T205000Z_001.json"
UNIT1 = ROOT / "audit/pass9/pass9-bank-continuous-run-unit1-inventory-v1.json"
UNIT2 = ROOT / "audit/pass9/pass9-bank-continuous-run-unit2-owner-contract-v1.json"
UNIT3 = ROOT / "audit/pass9/pass9-bank-continuous-run-unit3-owner-integration-v1.json"
UNIT4 = ROOT / "audit/pass9/pass9-bank-continuous-run-unit4-exhaustive-proof-v1.json"
BOUNDARY = ROOT / "pmp-bank-continuous-run-owner-boundary-v1.js"
STATE = ROOT / "pmp-continuous-run-state-bank-v1.js"
ROUTER = ROOT / "pmp-master-bank-inventory-router-v1.js"
RUNNER = ROOT / "tools/run_pass9_unit5_authority_persisted_data_certification_v1.js"
TEST = ROOT / "tools/test_pass9_unit5_authority_persisted_data_certification_v1.js"
WORKFLOW = ROOT / ".github/workflows/pass9-unit5-authority-persisted-data-certification-v1.yml"
GATE_RUNNER = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
EXPECTED = {
    ".github/workflows/pass9-unit5-authority-persisted-data-certification-v1.yml",
    "audit/pass9/pass9-bank-continuous-run-unit5-authority-persisted-data-certification-v1.json",
    "audit/pass9/receipts/RECEIPT_P9_U5_AUTHORITY_PERSISTED_DATA_CERTIFICATION_20260726T205000Z_001.json",
    "tools/run_pass9_unit5_authority_persisted_data_certification_v1.js",
    "tools/test_pass9_unit5_authority_persisted_data_certification_v1.js",
    "tools/verify_pass9_unit5_authority_persisted_data_certification_v1.py",
}
SOURCE_INPUTS = {
    "unit1_inventory_sha256": UNIT1,
    "unit2_contract_sha256": UNIT2,
    "unit3_integration_sha256": UNIT3,
    "unit4_proof_sha256": UNIT4,
    "owner_boundary_sha256": BOUNDARY,
    "continuous_run_state_sha256": STATE,
    "bank_router_sha256": ROUTER,
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
    assert report["unit_id"] == "P9-U5"
    assert report["status"] == "AUTHORITY_SEPARATION_AND_PERSISTED_DATA_CERTIFIED"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == []
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["status"] == report["status"]
    for key, path in SOURCE_INPUTS.items():
        assert report["inputs"][key] == sha(path), (key, report["inputs"][key], sha(path))

    node = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"certification \((\d+)/(\d+)\)", node)
    assert match and match.group(1) == match.group(2)
    assertions = int(match.group(1))
    assert assertions == report["verification"]["assertions_passed"] == 143
    assert "(238/238)" in output(
        "node", "tools/test_pass9_unit4_bank_continuous_run_exhaustive_proof_v1.js"
    )
    assert "(234/234)" in output(
        "node", "tools/test_pass9_unit3_bank_continuous_run_owner_integration_v1.js"
    )
    assert "(229/229)" in output(
        "node", "tools/test_pass9_unit2_bank_continuous_run_owner_contract_v1.js"
    )

    result = json.loads(output("node", str(RUNNER.relative_to(ROOT))))
    cert = report["certification"]
    assert result["status"] == report["status"]
    assert result["evidence_chain"]["units"][0]["unit"] == "P9-U1"
    assert result["evidence_chain"]["units"][-1]["unit"] == "P9-U4"
    assert result["evidence_chain"]["exact_progression"] == ["P9-U2", "P9-U3", "P9-U4", "P9-U5"]
    assert result["evidence_chain"]["inventory_conflicts_identified"] == cert["original_conflicts_identified"] == 9
    assert result["evidence_chain"]["cumulative_assertions"] == cert["cumulative_prior_assertions"] == 836
    assert result["evidence_chain"]["all_permanent_gates_bound"] is True
    authority = result["authority_separation"]
    assert authority["bank_owner"] == authority["durable_writer"] == cert["bank_owner"]
    assert authority["continuous_run_owner"] == authority["run_state_requester"] == cert["continuous_run_owner"]
    assert authority["owners_distinct"] is True
    assert authority["request_fields"] == cert["request_fields"] == 13
    assert authority["receipt_fields"] == cert["receipt_fields"] == 15
    assert authority["integration_receipt_algorithm"] == cert["receipt_algorithm"]
    assert authority["active_tab_conveys_ownership"] is False
    assert authority["filename_conveys_authority"] is False
    assert authority["copied_cross_frame_apis_convey_authority"] is False
    assert authority["owner_boundary_exact_ids_in_source"] is True
    assert authority["boundary_only_durable_writer_rule"] is True
    assert authority["state_requests_bank_commits"] is True
    assert authority["router_uses_internal_bank_capability"] is True
    assert authority["dependency_bridge_copies_mutable_apis"] is False
    assert authority["bank_shell_open_calls_record_write"] is False
    persisted = result["persisted_data"]
    assert persisted["total_governed_keys"] == cert["governed_persisted_keys"] == 9
    assert len(persisted["bank_keys"]) == cert["bank_governed_keys"] == 4
    assert len(persisted["continuous_run_keys"]) == cert["continuous_run_governed_keys"] == 5
    assert persisted["keys_unique"] is True
    assert persisted["boundary_bank_keys_bound"] is True
    assert persisted["boundary_run_keys_bound"] is True
    assert persisted["state_direct_local_storage_writes"] == 0
    assert persisted["state_direct_local_storage_deletes"] == 0
    assert persisted["router_direct_local_storage_writes"] == 0
    assert persisted["connection_delete_direct_local_storage_writes"] == 0
    assert persisted["first_core_load_calls"] == cert["first_load_storage_calls"]
    assert persisted["repeated_core_load_calls"] == cert["repeated_load_storage_calls"]
    for key in (
        "stale_concurrency_zero_effects",
        "cancellation_gap_zero_effects",
        "cancellation_stale_zero_effects",
        "duplicate_conflict_zero_effects",
        "all_denials_zero_effect",
        "denial_bytes_unchanged",
        "existing_key_rollback_exact",
        "absent_key_rollback_exact",
        "corrupt_restart_raw_bytes_preserved",
        "router_default_delete_zero_effect",
        "router_wrong_delete_zero_effect",
        "bounded_receipt_chain_valid",
        "unrelated_bytes_preserved_across_all_matrices",
    ):
        assert persisted[key] is True, key
    assert persisted["repeated_load_changed_data"] is False
    assert persisted["restart_load_changed_data"] is False
    assert persisted["user_persisted_data_touched"] is False
    assert persisted["storage_migration_performed"] is False
    active = result["active_runtime"]
    assert active["exact_order"] is True
    assert active["boundary_occurrences"] == 1
    assert active["state_occurrences"] == 1
    assert active["router_occurrences"] == 1
    assert active["bank_shell_occurrences"] == 1
    assert active["continuous_owner_occurrences"] == 1
    assert active["legacy_mode_occurrences"] == 0
    assert active["legacy_cleaner_occurrences"] == 0
    assert active["master_recurring_painter"] is False
    assert active["continuous_owner_recurring_painter"] is False
    assert active["loader_recurring_scan"] is False
    assert active["loader_event_driven_mode"] is True
    deletion = result["deletion_authority"]
    assert deletion["router_requires_user_confirmation"] is True
    assert deletion["connections_exact_capability"] is True
    assert deletion["connections_routes_final_index_through_owner"] is True
    assert deletion["connections_opens_indexeddb_only_after_owner_commit"] is True
    assert deletion["default_delete_result"] == "DELETE_DENIED_BY_DEFAULT"
    assert deletion["wrong_capability_result"] == "DELETE_DENIED_BY_DEFAULT"
    assert deletion["exact_confirmed_result"] == "COMMITTED"
    receipts = result["receipt_diagnostics"]
    assert receipts["production_chain_valid_in_unit4"] is True
    assert receipts["bounded_chain_valid_in_unit4"] is True
    assert receipts["retained_receipts"] == cert["bounded_receipts_retained"] == 256
    assert receipts["visible_receipts"] == cert["visible_receipts"] == 32
    assert receipts["diagnostic_snapshot_writes"] == 0
    assert receipts["diagnostic_snapshot_deletes"] == 0
    assert all(value is False for value in result["effects"].values())

    matrix = report["diagnostic_and_proof_matrix"]
    assert len(matrix["invariants"]) == 7
    assert matrix["assertions"] == 143
    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "deterministic_integration"
    assert binding["diagnostic_matrix_update"]["status"] == "ADDED"
    assert binding["diagnostic_matrix_update"]["applicable_matrix"] == REPORT.relative_to(ROOT).as_posix()
    assert binding["fault_injection"]["status"] == "COVERED"
    assert len(binding["fault_injection"]["cases"]) == 18
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    gate = json.loads(output("python3", str(GATE_RUNNER.relative_to(ROOT)), "--base", BASE))
    assert gate["status"] == "PASS", gate
    assert gate["unit_id"] == "P9-U5"
    assert gate["gate_records"] == 1
    assert gate["summary"]["runtime_paths"] == 0
    assert gate["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for required in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete P9-U5 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert required in workflow
    assert workflow.index("Upload complete P9-U5 evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )
    assert all(value is False for value in report["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["next_step"]["id"] == "P9-U6"
    assert report["next_step"]["requires_user_app_check_before_decision"] is False
    assert report["next_step"]["perform_observation_automatically"] is False
    assert receipt["next_safe_move"]["step_id"] == "P9-U6"
    print(
        "PASS: exact six-file P9-U5 Bank/Continuous Run authority and "
        f"persisted-data certification verified ({assertions}/{assertions}, gate PASS)"
    )


if __name__ == "__main__":
    main()
