#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "fa5758d63927647244722882efd092f3a59548e3"
REPORT = ROOT / "audit/pass10/pass10-bank-unit6-reversible-migration-rehearsal-v1.json"
RECEIPT = (
    ROOT
    / "audit/pass10/receipts/"
    "RECEIPT_P10_U6_BANK_REVERSIBLE_MIGRATION_REHEARSAL_20260726T234500Z_001.json"
)
WORKFLOW = ROOT / ".github/workflows/pass10-unit6-bank-reversible-migration-rehearsal-v1.yml"
UNIT2 = ROOT / "audit/pass10/pass10-bank-unit2-inventory-contract-v1.json"
UNIT5 = ROOT / "audit/pass10/pass10-bank-unit5-fault-corruption-proof-v1.json"
BOUNDARY = ROOT / "pmp-bank-continuous-run-owner-boundary-v1.js"
PROJECTION = ROOT / "pmp-bank-inventory-readonly-projection-v1.js"
ADAPTER = ROOT / "pmp-bank-owner-projection-refresh-v1.js"
MASTER = ROOT / "pmp-master-bank-tab-v1.js"
RUNNER = ROOT / "tools/run_pass10_unit6_bank_reversible_migration_rehearsal_v1.js"
TEST = ROOT / "tools/test_pass10_unit6_bank_reversible_migration_rehearsal_v1.js"
UNIT5_TEST = ROOT / "tools/test_pass10_unit5_bank_fault_corruption_proof_v1.js"
GATE = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
EXPECTED = {
    ".github/workflows/pass10-unit6-bank-reversible-migration-rehearsal-v1.yml",
    "audit/pass10/pass10-bank-unit6-reversible-migration-rehearsal-v1.json",
    (
        "audit/pass10/receipts/"
        "RECEIPT_P10_U6_BANK_REVERSIBLE_MIGRATION_REHEARSAL_20260726T234500Z_001.json"
    ),
    "tools/run_pass10_unit6_bank_reversible_migration_rehearsal_v1.js",
    "tools/test_pass10_unit6_bank_reversible_migration_rehearsal_v1.js",
    "tools/verify_pass10_unit6_bank_reversible_migration_rehearsal_v1.py",
}
INPUTS = {
    "unit2_contract_sha256": UNIT2,
    "unit5_proof_sha256": UNIT5,
    "owner_boundary_sha256": BOUNDARY,
    "readonly_projection_sha256": PROJECTION,
    "owner_refresh_adapter_sha256": ADAPTER,
    "bank_tab_sha256": MASTER,
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
    assert report["unit_id"] == "P10-U6"
    assert report["status"] == "BANK_REVERSIBLE_MIGRATION_REHEARSAL_PROVEN"
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
    match = re.search(r"rehearsal \((\d+)/(\d+)\)", test_output)
    assert match and match.group(1) == match.group(2) == "102", test_output
    assertions = int(match.group(1))
    assert report["verification"]["assertions_total"] == assertions
    assert report["verification"]["assertions_passed"] == assertions
    assert report["verification"]["assertions_failed"] == 0
    assert receipt["coverage"]["assertions"] == assertions
    assert "(133/133)" in output("node", str(UNIT5_TEST.relative_to(ROOT)))

    result = json.loads(output("node", str(RUNNER.relative_to(ROOT))))
    assert result["status"] == report["status"]
    authority = result["authority"]
    assert authority["target"] == "DISPOSABLE_FIXTURE_STAGING_ONLY"
    assert authority["production_migration_allowed"] is False
    assert authority["persisted_user_data_change_allowed"] is False
    assert authority["special_authority_required"] is False
    assert authority["special_authority_consumed"] is False

    preflight = result["preflight"]
    assert preflight["contract_status"] == "BANK_INVENTORY_CONTRACT_PROVEN"
    assert preflight["unit5_status"] == (
        "BANK_FAULT_ROLLBACK_AND_CORRUPTION_CONTAINMENT_PROVEN"
    )
    assert preflight["unit5_unresolved_failures"] == 0
    assert preflight["plan_valid"] is True
    assert re.fullmatch(r"[0-9a-f]{64}", preflight["plan_sha256"])
    assert re.fullmatch(r"[0-9a-f]{64}", preflight["source_digest"])
    assert preflight["source_namespaces"] == 5
    assert preflight["source_bytes_preserved"] == 4
    assert preflight["plan_changed_source_workspace"] is False

    mapping = result["forward_mapping"]
    assert mapping["items"] == 8
    assert mapping["active"] == 2
    assert mapping["reference_only"] == 1
    assert mapping["quarantined"] == 4
    assert mapping["unavailable"] == 1
    assert mapping["stable_identities"] is True
    assert mapping["provenance_complete"] is True
    assert mapping["delete_authority_denied"] is True
    assert mapping["collision_rows"] == 2
    assert mapping["collision_quarantined"] is True
    assert mapping["collision_payloads_preserved"] == 2
    assert mapping["orphan_rows"] == 1
    assert mapping["orphan_quarantined"] is True
    assert mapping["corrupt_rows"] == 1
    assert mapping["corrupt_quarantined"] is True
    assert mapping["unavailable_rows"] == 1
    assert mapping["unavailable_preserved"] is True
    assert mapping["historic_rows"] == 1
    assert mapping["historic_reference_only"] is True

    applied = result["disposable_apply"]
    assert applied["code"] == "DISPOSABLE_STAGING_APPLIED"
    assert applied["changed_writes"] == 9
    assert applied["deletes"] == 0
    assert applied["receipt_valid"] is True
    assert applied["receipt_target"] == "DISPOSABLE_FIXTURE_STAGING_ONLY"
    assert applied["staging_entries"] == 9
    assert applied["source_bytes_unchanged"] is True
    assert applied["unrelated_bytes_unchanged"] is True

    idempotence = result["idempotence"]
    assert idempotence == {
        "code": "ALREADY_APPLIED",
        "changed_writes": 0,
        "deletes": 0,
        "state_unchanged": True,
        "plan_sha256_unchanged": True,
    }
    interruption = result["interruption_recovery"]
    assert interruption["code"] == "DENIED_INTERRUPTED_ROLLED_BACK"
    assert interruption["writes_attempted"] == 3
    assert interruption["deletes"] == 0
    assert interruption["rollback_completed"] is True
    assert interruption["exact_baseline_restored"] is True
    assert interruption["staging_entries_after"] == 0
    assert interruption["receipt_emitted"] is False
    rollback = result["explicit_rollback"]
    assert all(value in (True, 0) for value in rollback.values())
    assert rollback["exact_baseline_restored"] is True

    denial = result["denial_matrix"]
    assert denial["production_code"] == "DENIED_PRODUCTION_TARGET"
    assert denial["production_zero_effect"] is True
    assert denial["source_tamper_code"] == "DENIED_SOURCE_PREIMAGE_CHANGED"
    assert denial["source_tamper_zero_effect"] is True
    assert denial["plan_tamper_code"] == "DENIED_PLAN_INTEGRITY"
    assert denial["plan_tamper_zero_effect"] is True
    assert denial["deletes_across_denials"] == 0

    decision = result["observation_decision_input"]
    assert decision["rehearsal_failures"] == 0
    assert decision["production_migration_performed"] is False
    assert decision["real_user_storage_accessed"] is False
    assert decision["user_app_check_required_now"] is False
    assert decision["bounded_observation_performed"] is False
    assert decision["bounded_observation_authority_consumed"] is False
    assert decision["pass10_closure_unit_ready"] is True

    rehearsal = report["rehearsal"]
    assert rehearsal["assertions"] == assertions
    assert rehearsal["planned_items"] == 8
    assert rehearsal["staging_writes"] == 9
    assert rehearsal["idempotent_repeat_writes"] == 0
    assert rehearsal["interruption_exact_rollback"] is True
    assert rehearsal["explicit_rollback_exact"] is True
    assert rehearsal["source_bytes_unchanged"] is True
    assert rehearsal["rehearsal_failures"] == 0
    boundary = report["migration_boundary"]
    assert boundary["target"] == "DISPOSABLE_FIXTURE_STAGING_ONLY"
    assert boundary["production_migration_allowed"] is False
    assert boundary["real_user_storage_accessed"] is False
    assert boundary["fixture_workspace_restored"] is True

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
    assert gate["unit_id"] == "P10-U6"
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
        "Upload complete P10-U6 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert token in workflow
    assert workflow.index("Upload complete P10-U6 evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )

    effects = report["effects"]
    assert effects["disposable_fixture_writes_performed"] is True
    assert effects["disposable_fixture_rollback_completed"] is True
    for key, value in effects.items():
        if key not in (
            "disposable_fixture_writes_performed",
            "disposable_fixture_rollback_completed",
        ):
            assert value is False, key
    assert receipt["effects"]["disposable_fixture_writes_performed"] is True
    assert receipt["effects"]["disposable_fixture_rollback_completed"] is True
    assert report["authority"]["special_authority_consumed"] is False
    assert report["next_step"]["id"] == "P10-U7"
    assert report["next_step"]["requires_user_app_check_before_decision"] is False
    assert report["next_step"]["perform_observation_automatically"] is False
    assert report["next_step"]["persisted_user_data_change_allowed"] is False
    assert report["next_step"]["production_migration_allowed"] is False
    assert receipt["next_safe_move"]["step_id"] == "P10-U7"
    print(
        "PASS: exact six-file P10-U6 Bank reversible migration rehearsal "
        "verified (102/102, P10-U5 133/133, gate PASS, P10-U7 ready)"
    )


if __name__ == "__main__":
    main()
