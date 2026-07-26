#!/usr/bin/env python3
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "1e4576f4f5e0f74448fc3ed846574d852edfea65"
REPORT = ROOT / "audit/pass10/pass10-bank-unit1-inventory-reconciliation-v1.json"
RECEIPT = ROOT / "audit/pass10/receipts/RECEIPT_P10_U1_BANK_INVENTORY_RECONCILIATION_20260726T212000Z_001.json"
WORKFLOW = ROOT / ".github/workflows/pass10-unit1-bank-inventory-reconciliation-v1.yml"
RUNNER = ROOT / "tools/run_pass10_unit1_bank_inventory_reconciliation_v1.js"
TEST = ROOT / "tools/test_pass10_unit1_bank_inventory_reconciliation_v1.js"
GATE = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
INPUTS = {
    "pass9_closure_sha256": ROOT / "audit/pass9/pass9-bank-continuous-run-unit7-closure-certification-v1.json",
    "owner_boundary_sha256": ROOT / "pmp-bank-continuous-run-owner-boundary-v1.js",
    "inventory_router_sha256": ROOT / "pmp-master-bank-inventory-router-v1.js",
    "bank_tab_sha256": ROOT / "pmp-master-bank-tab-v1.js",
    "continuous_run_state_sha256": ROOT / "pmp-continuous-run-state-bank-v1.js",
    "continuous_run_owner_sha256": ROOT / "pmp-bank-screen-owner-v1.js",
    "runner_sha256": RUNNER,
    "test_sha256": TEST,
}
EXPECTED = {
    ".github/workflows/pass10-unit1-bank-inventory-reconciliation-v1.yml",
    "audit/pass10/pass10-bank-unit1-inventory-reconciliation-v1.json",
    "audit/pass10/receipts/RECEIPT_P10_U1_BANK_INVENTORY_RECONCILIATION_20260726T212000Z_001.json",
    "tools/run_pass10_unit1_bank_inventory_reconciliation_v1.js",
    "tools/test_pass10_unit1_bank_inventory_reconciliation_v1.js",
    "tools/verify_pass10_unit1_bank_inventory_reconciliation_v1.py",
}


def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed(base):
    rows = set()
    for command in (
        ("git", "diff", "--name-only", f"{base}...HEAD"),
        ("git", "diff", "--name-only", base),
        ("git", "ls-files", "--others", "--exclude-standard"),
    ):
        rows.update(filter(None, output(*command).splitlines()))
    return rows


def workflow_paths(text):
    match = re.search(r"(?m)^    paths:\n(?P<rows>(?:      - [^\n]+\n)+)", text)
    assert match
    return {
        row.strip()[2:].strip().strip("'\"")
        for row in match.group("rows").splitlines()
    }


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else BASE
    assert base == BASE
    assert changed(base) == EXPECTED, (sorted(changed(base)), sorted(EXPECTED))
    report = json.loads(REPORT.read_text())
    receipt = json.loads(RECEIPT.read_text())
    assert report["base_main_commit"] == BASE
    assert report["unit_id"] == "P10-U1"
    assert report["status"] == "BANK_INVENTORY_RECONCILIATION_PROVEN"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == []
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["status"] == report["status"]
    for key, path in INPUTS.items():
        assert report["inputs"][key] == sha(path), key

    text = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"reconciliation \((\d+)/(\d+)\)", text)
    assert match and match.group(1) == match.group(2) == "110"
    assert report["verification"]["assertions_total"] == 110
    assert report["verification"]["assertions_passed"] == 110
    assert report["verification"]["assertions_failed"] == 0
    result = json.loads(output("node", str(RUNNER.relative_to(ROOT))))
    assert result["status"] == report["status"]
    assert result["source_counts"] == {
        "total": 63,
        "js": 45,
        "html": 15,
        "json": 3,
        "canonical_owner_chain": 5,
        "diagnostic_or_rehearsal": 23,
        "historical_compatibility_or_auxiliary": 35,
    }
    assert result["source_catalog_sha256"] == report["inventory"]["source_catalog_sha256"]
    assert len(result["source_records"]) == 63
    assert len({row["path"] for row in result["source_records"]}) == 63
    assert all(re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) for row in result["source_records"])
    assert result["governed_local_storage"]["total"] == 9
    assert len(result["declared_schemas"]["master_inventory"]["canonical_banks"]) == 13
    assert len(result["declared_schemas"]["master_inventory"]["record_required_fields"]) == 12
    assert len(result["declared_schemas"]["master_inventory"]["record_optional_fields"]) == 3
    assert len(result["declared_schemas"]["helper_index"]["item_fields"]) == 8
    assert len(result["declared_schemas"]["project_registry"]["project_fields"]) == 7
    assert result["declared_schemas"]["staging_transfer_store"]["status"].endswith("REQUIRES_P10_CONTRACT_CLASSIFICATION")
    assert result["declared_schemas"]["historic_inventory_output"]["status"] == "HISTORIC_READ_SCAN_OUTPUT_NOT_CANONICAL_INVENTORY"
    assert len(result["conflicts"]) == 6
    assert result["policy"]["unknown_or_orphan_policy"] == "QUARANTINE_PRESERVE_EXACT_BYTES_NEVER_SILENTLY_DELETE"
    assert result["policy"]["historic_namespace_policy"] == "CLASSIFY_AND_REFERENCE_NEVER_SILENTLY_MERGE"
    assert result["reconciliation"]["live_user_inventory_read"] is False
    assert result["reconciliation"]["persisted_user_data_changed"] is False
    assert all(value is False for value in result["effects"].values())

    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "static_contract"
    assert binding["diagnostic_matrix_update"]["status"] == "ADDED"
    assert len(binding["fault_injection"]["cases"]) == 10
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    gate = json.loads(output("python3", str(GATE.relative_to(ROOT)), "--base", BASE))
    assert gate["status"] == "PASS", gate
    assert gate["unit_id"] == "P10-U1"
    assert gate["summary"]["runtime_paths"] == 0
    assert gate["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for token in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete P10-U1 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert token in workflow
    assert workflow.index("Upload complete P10-U1 evidence") < workflow.index("Enforce preserved result after upload")
    assert workflow.rstrip().endswith('run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"')
    assert all(value is False for value in report["effects"].values())
    assert report["next_step"]["id"] == "P10-U2"
    assert receipt["next_safe_move"]["step_id"] == "P10-U2"
    print("PASS: exact six-file P10-U1 Bank inventory reconciliation verified (110/110, gate PASS, P10-U2 ready)")


if __name__ == "__main__":
    main()
