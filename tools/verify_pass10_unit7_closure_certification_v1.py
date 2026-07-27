#!/usr/bin/env python3
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "09e78630cb9865a6817f460ef28a4dc455dcc036"
REPORT = ROOT / "audit/pass10/pass10-bank-unit7-closure-certification-v1.json"
RECEIPT = ROOT / "audit/pass10/receipts/RECEIPT_P10_U7V_PASS10_BANK_INVENTORY_COMPLETE_20260727T062000Z_001.json"
WORKFLOW = ROOT / ".github/workflows/pass10-unit7-closure-certification-v1.yml"
RUNNER = ROOT / "tools/run_pass10_unit7_closure_certification_v1.js"
TEST = ROOT / "tools/test_pass10_unit7_closure_certification_v1.js"
GATE = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
EXPECTED = {
    ".github/workflows/pass10-unit7-closure-certification-v1.yml",
    "audit/pass10/pass10-bank-unit7-closure-certification-v1.json",
    "audit/pass10/receipts/RECEIPT_P10_U7V_PASS10_BANK_INVENTORY_COMPLETE_20260727T062000Z_001.json",
    "tools/run_pass10_unit7_closure_certification_v1.js",
    "tools/test_pass10_unit7_closure_certification_v1.js",
    "tools/verify_pass10_unit7_closure_certification_v1.py",
}
INPUTS = {
    "p10_u1_sha256": ROOT / "audit/pass10/pass10-bank-unit1-inventory-reconciliation-v1.json",
    "p10_u2_sha256": ROOT / "audit/pass10/pass10-bank-unit2-inventory-contract-v1.json",
    "p10_u3_sha256": ROOT / "audit/pass10/pass10-bank-unit3-readonly-projection-v1.json",
    "p10_u4_sha256": ROOT / "audit/pass10/pass10-bank-unit4-owner-projection-refresh-v1.json",
    "p10_u5_sha256": ROOT / "audit/pass10/pass10-bank-unit5-fault-corruption-proof-v1.json",
    "p10_u6_sha256": ROOT / "audit/pass10/pass10-bank-unit6-reversible-migration-rehearsal-v1.json",
    "p10_u7a_sha256": ROOT / "audit/pass10/pass10-bank-unit7-hands-on-readiness-v1.json",
    "p10_u7r_sha256": ROOT / "audit/pass10/pass10-bank-unit7-level-owner-stability-repair-v1.json",
    "p10_u7s_sha256": ROOT / "audit/pass10/pass10-bank-unit7-legacy-level-alias-single-stack-repair-v1.json",
    "p10_u7t_sha256": ROOT / "audit/pass10/pass10-bank-unit7-single-card-presentation-v1.json",
    "p10_u7u_sha256": ROOT / "audit/pass10/pass10-bank-unit7-uniform-title-weight-v1.json",
    "runner_sha256": RUNNER,
    "test_sha256": TEST,
}


def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def sha(item):
    return hashlib.sha256(item.read_bytes()).hexdigest()


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
    assert report["unit_id"] == "P10-U7"
    assert report["substep"] == "P10-U7V"
    assert report["status"] == "PASS10_BANK_INVENTORY_REBUILD_COMPLETE"
    assert report["pass10_result"] == "PASS"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == []
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["status"] == report["status"]
    assert receipt["pass10_result"] == "PASS"
    for key, item in INPUTS.items():
        assert report["inputs"][key] == sha(item), key

    text = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"certification \((\d+)/(\d+)\)", text)
    assert match and match.group(1) == match.group(2)
    assertion_total = int(match.group(1))
    assert report["verification"]["assertions_total"] == assertion_total
    assert report["verification"]["assertions_passed"] == assertion_total
    assert report["verification"]["assertions_failed"] == 0
    result = json.loads(output("node", str(RUNNER.relative_to(ROOT))))
    assert result["status"] == report["status"]
    assert result["pass10_result"] == "PASS"
    assert result["evidence_records"] == 11
    assert result["cumulative_predecessor_assertions"] == 1674
    assert [row["assertions"] for row in result["evidence_rows"]] == [110, 187, 125, 121, 133, 102, 75, 106, 151, 478, 86]
    assert all(row["assertions_failed"] == 0 for row in result["evidence_rows"])
    assert all(result["exit_criteria"].values())
    assert all(report["exit_criteria"].values())
    assert report["evidence_summary"]["predecessor_assertions"] == 1674
    assert report["evidence_summary"]["predecessor_assertions_failed"] == 0
    assert report["hands_on_confirmation"]["exact_statement"] == "It worked."
    assert report["hands_on_confirmation"]["result"] == "PASS"
    assert report["hands_on_confirmation"]["confirmed_main"] == BASE
    assert report["closure"]["pass10_complete"] is True
    assert report["closure"]["bank_tab_independent_mutation_allowed"] is False
    assert report["closure"]["unknown_or_orphan_policy"] == "QUARANTINE_PRESERVE_EXACT_BYTES_NEVER_SILENTLY_DELETE"
    assert report["closure"]["production_migration_performed"] is False
    assert report["closure"]["persisted_user_data_changed"] is False

    boundary = report["pass11_boundary"]
    assert boundary["entry_unit"] == "P11-U1"
    assert boundary["mode"] == "STATIC_SAFETY_CONTRACT_CONSOLIDATION"
    assert boundary["persisted_user_data_change_allowed"] is False
    assert boundary["production_migration_allowed"] is False
    assert boundary["hands_on_app_check_required"] is False
    assert result["next_step"]["id"] == "P11-U1"
    assert receipt["next_safe_move"]["step_id"] == "P11-U1"

    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "static_contract"
    assert binding["diagnostic_matrix_update"]["status"] == "CONFIRMED_UNCHANGED"
    assert len(binding["diagnostic_evidence_routes"]) == 12
    assert binding["fault_injection"]["status"] == "NOT_APPLICABLE"
    assert binding["fault_injection"]["cases"] == []
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    gate = json.loads(output("python3", str(GATE.relative_to(ROOT)), "--base", BASE))
    assert gate["status"] == "PASS", gate
    assert gate["unit_id"] == "P10-U7"
    assert gate["summary"]["runtime_paths"] == 0
    assert gate["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for token in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete P10-U7V evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert token in workflow
    assert workflow.index("Upload complete P10-U7V evidence") < workflow.index("Enforce preserved result after upload")
    assert workflow.rstrip().endswith('run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"')
    assert all(value is False for value in report["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["no_retry_gates"]["consumed_failed_formal_proof_pr"] == 122
    assert report["no_retry_gates"]["retry_authorized"] is False
    print(f"PASS: exact six-file P10-U7V Bank inventory closure verified ({assertion_total}/{assertion_total}, gate PASS, P11-U1 ready)")


if __name__ == "__main__":
    main()
