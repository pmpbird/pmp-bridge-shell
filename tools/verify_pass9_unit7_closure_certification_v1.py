#!/usr/bin/env python3
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "af568da490374d10be3acb069f1225f728e5c02f"
REPORT = ROOT / "audit/pass9/pass9-bank-continuous-run-unit7-closure-certification-v1.json"
RECEIPT = ROOT / "audit/pass9/receipts/RECEIPT_P9_U7_PASS9_BANK_CONTINUOUS_RUN_COMPLETE_20260726T212500Z_001.json"
WORKFLOW = ROOT / ".github/workflows/pass9-unit7-closure-certification-v1.yml"
RUNNER = ROOT / "tools/run_pass9_unit7_closure_certification_v1.js"
TEST = ROOT / "tools/test_pass9_unit7_closure_certification_v1.js"
GATE = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
INPUTS = {
    "p9_u1_sha256": ROOT / "audit/pass9/pass9-bank-continuous-run-unit1-inventory-v1.json",
    "p9_u2_sha256": ROOT / "audit/pass9/pass9-bank-continuous-run-unit2-owner-contract-v1.json",
    "p9_u3_sha256": ROOT / "audit/pass9/pass9-bank-continuous-run-unit3-owner-integration-v1.json",
    "p9_u4_sha256": ROOT / "audit/pass9/pass9-bank-continuous-run-unit4-exhaustive-proof-v1.json",
    "p9_u5_sha256": ROOT / "audit/pass9/pass9-bank-continuous-run-unit5-authority-persisted-data-certification-v1.json",
    "p9_u6_sha256": ROOT / "audit/pass9/pass9-bank-continuous-run-unit6-bounded-observation-decision-v1.json",
    "runner_sha256": RUNNER,
    "test_sha256": TEST,
}
EXPECTED = {
    ".github/workflows/pass9-unit7-closure-certification-v1.yml",
    "audit/pass9/pass9-bank-continuous-run-unit7-closure-certification-v1.json",
    "audit/pass9/receipts/RECEIPT_P9_U7_PASS9_BANK_CONTINUOUS_RUN_COMPLETE_20260726T212500Z_001.json",
    "tools/run_pass9_unit7_closure_certification_v1.js",
    "tools/test_pass9_unit7_closure_certification_v1.js",
    "tools/verify_pass9_unit7_closure_certification_v1.py",
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
    assert report["unit_id"] == "P9-U7"
    assert report["status"] == "PASS9_BANK_CONTINUOUS_RUN_COMPLETE"
    assert report["pass9_result"] == "PASS"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == []
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["status"] == report["status"]
    assert receipt["pass9_result"] == "PASS"
    for key, path in INPUTS.items():
        assert report["inputs"][key] == sha(path), key

    text = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"certification \((\d+)/(\d+)\)", text)
    assert match and match.group(1) == match.group(2) == "102"
    assert report["verification"]["assertions_total"] == 102
    assert report["verification"]["assertions_passed"] == 102
    assert report["verification"]["assertions_failed"] == 0
    result = json.loads(output("node", str(RUNNER.relative_to(ROOT))))
    assert result["status"] == report["status"]
    assert result["pass9_result"] == "PASS"
    assert result["completed_units"] == 6
    assert result["cumulative_prior_assertions"] == 1038
    assert [row["assertions"] for row in result["unit_rows"]] == [135, 229, 234, 238, 143, 59]
    assert all(row["assertions_failed"] == 0 for row in result["unit_rows"])
    assert all(row["effects_bounded"] for row in result["unit_rows"])
    assert all(result["exit_criteria"].values())
    assert all(report["exit_criteria"].values())
    assert report["evidence_summary"]["prior_assertions"] == 1038
    assert report["evidence_summary"]["prior_assertions_failed"] == 0
    assert report["closure"]["bank_and_continuous_run_repair_complete"] is True
    assert report["closure"]["bank_owner"] == "bank_screen_owner"
    assert report["closure"]["continuous_run_owner"] == "continuous_run_level_owner"
    assert report["closure"]["durable_writer"] == "bank_screen_owner"
    assert report["closure"]["owners_distinct"] is True
    assert report["closure"]["observation_performed"] is False
    assert report["closure"]["observation_authority_consumed"] is False

    boundary = report["pass10_boundary"]
    assert boundary["entry_unit"] == "P10-U1"
    assert boundary["mode"] == "READ_ONLY_INVENTORY_RECONCILIATION"
    assert boundary["bank_tab_change_allowed"] is False
    assert boundary["persisted_user_data_change_allowed"] is False
    assert boundary["storage_migration_allowed"] is False
    assert boundary["hands_on_app_check_required"] is False
    assert result["next_step"]["id"] == "P10-U1"
    assert receipt["next_safe_move"]["step_id"] == "P10-U1"

    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "static_contract"
    assert binding["diagnostic_matrix_update"]["status"] == "CONFIRMED_UNCHANGED"
    assert len(binding["diagnostic_evidence_routes"]) == 7
    assert binding["fault_injection"]["status"] == "NOT_APPLICABLE"
    assert binding["fault_injection"]["cases"] == []
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    gate = json.loads(output("python3", str(GATE.relative_to(ROOT)), "--base", BASE))
    assert gate["status"] == "PASS", gate
    assert gate["unit_id"] == "P9-U7"
    assert gate["summary"]["runtime_paths"] == 0
    assert gate["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for token in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete P9-U7 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert token in workflow
    assert workflow.index("Upload complete P9-U7 evidence") < workflow.index("Enforce preserved result after upload")
    assert workflow.rstrip().endswith('run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"')
    assert all(value is False for value in report["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["no_retry_gates"]["consumed_observation_prs"] == [149, 150, 152]
    assert report["no_retry_gates"]["consumed_failed_formal_proof_pr"] == 122
    assert report["no_retry_gates"]["retry_authorized"] is False
    print("PASS: exact six-file P9-U7 Bank and Continuous Run closure verified (102/102, gate PASS, P10-U1 ready)")


if __name__ == "__main__":
    main()
