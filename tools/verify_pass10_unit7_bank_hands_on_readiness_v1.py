#!/usr/bin/env python3
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "bfba6e36272cb98ffe1e2b28b8d881be4e537304"
REPORT = ROOT / "audit/pass10/pass10-bank-unit7-hands-on-readiness-v1.json"
RECEIPT = ROOT / "audit/pass10/receipts/RECEIPT_P10_U7A_BANK_HANDS_ON_READINESS_20260726T233200Z_001.json"
WORKFLOW = ROOT / ".github/workflows/pass10-unit7-bank-hands-on-readiness-v1.yml"
RUNNER = ROOT / "tools/run_pass10_unit7_bank_hands_on_readiness_v1.js"
TEST = ROOT / "tools/test_pass10_unit7_bank_hands_on_readiness_v1.js"
GATE = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
INPUTS = {
    "p10_u1_sha256": ROOT / "audit/pass10/pass10-bank-unit1-inventory-reconciliation-v1.json",
    "p10_u2_sha256": ROOT / "audit/pass10/pass10-bank-unit2-inventory-contract-v1.json",
    "p10_u3_sha256": ROOT / "audit/pass10/pass10-bank-unit3-readonly-projection-v1.json",
    "p10_u4_sha256": ROOT / "audit/pass10/pass10-bank-unit4-owner-projection-refresh-v1.json",
    "p10_u5_sha256": ROOT / "audit/pass10/pass10-bank-unit5-fault-corruption-proof-v1.json",
    "p10_u6_sha256": ROOT / "audit/pass10/pass10-bank-unit6-reversible-migration-rehearsal-v1.json",
    "bank_tab_sha256": ROOT / "pmp-master-bank-tab-v1.js",
    "owner_refresh_sha256": ROOT / "pmp-bank-owner-projection-refresh-v1.js",
    "continuous_run_owner_sha256": ROOT / "pmp-bank-screen-owner-v1.js",
    "runner_sha256": RUNNER,
    "test_sha256": TEST,
}
EXPECTED = {
    ".github/workflows/pass10-unit7-bank-hands-on-readiness-v1.yml",
    "audit/pass10/pass10-bank-unit7-hands-on-readiness-v1.json",
    "audit/pass10/receipts/RECEIPT_P10_U7A_BANK_HANDS_ON_READINESS_20260726T233200Z_001.json",
    "tools/run_pass10_unit7_bank_hands_on_readiness_v1.js",
    "tools/test_pass10_unit7_bank_hands_on_readiness_v1.js",
    "tools/verify_pass10_unit7_bank_hands_on_readiness_v1.py",
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
    assert report["unit"] == "P10-U7"
    assert report["substep"] == "P10-U7A"
    assert report["status"] == "HANDS_ON_APP_CHECK_REQUIRED"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == []
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["status"] == report["status"]
    for key, path in INPUTS.items():
        assert report["inputs"][key] == sha(path), key

    text = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"readiness \((\d+)/(\d+)\)", text)
    assert match and match.group(1) == match.group(2) == "75"
    assert report["verification"]["assertions_total"] == 75
    assert report["verification"]["assertions_passed"] == 75
    assert report["verification"]["assertions_failed"] == 0
    assert "(102/102)" in output(
        "node", "tools/test_pass10_unit6_bank_reversible_migration_rehearsal_v1.js"
    )

    result = json.loads(output("node", str(RUNNER.relative_to(ROOT))))
    assert result["status"] == report["status"]
    assert result["deterministic_readiness"]["ready"] is True
    assert result["deterministic_readiness"]["completed_units"] == 6
    assert result["deterministic_readiness"]["cumulative_prior_assertions"] == 778
    assert result["deterministic_readiness"]["unresolved_assertion_failures"] == 0
    assert result["deterministic_readiness"]["all_effect_boundaries_preserved"] is True
    assert [row["assertions"] for row in result["deterministic_readiness"]["unit_rows"]] == [
        110,
        187,
        125,
        121,
        133,
        102,
    ]
    assert result["decision"]["bounded_hands_on_check_required"] is True
    assert len(result["decision"]["unresolved_live_only_claims"]) == 3
    assert result["decision"]["pass10_complete"] is False
    assert result["decision"]["observation_performed"] is False
    assert result["decision"]["automated_observation_performed"] is False
    assert result["decision"]["observation_authority_consumed"] is False
    assert result["decision"]["formal_proof_performed"] is False
    assert result["decision"]["next_step"] == (
        "USER_HANDS_ON_CHECK_THEN_P10_U7B_RECONCILIATION_AND_CLOSURE"
    )
    assert result["hands_on_check"]["mode"] == "USER_HANDS_ON_READ_ONLY_APP_CHECK"
    assert len(result["hands_on_check"]["steps"]) == 6
    assert result["hands_on_check"]["changes_user_data"] is False
    assert result["hands_on_check"]["automated_observation"] is False
    assert result["hands_on_check"]["consumes_scarce_observation_authority"] is False
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
    assert gate["unit_id"] == "P10-U7"
    assert gate["summary"]["runtime_paths"] == 0
    assert gate["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for token in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete P10-U7A evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert token in workflow
    assert workflow.index("Upload complete P10-U7A evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )
    assert all(value is False for value in report["effects"].values())
    assert report["next_step"]["id"] == "P10-U7B"
    assert report["next_step"]["requires_user_app_check"] is True
    assert receipt["next_safe_move"]["step_id"] == "P10-U7B"
    assert receipt["next_safe_move"]["requires_user_app_check"] is True
    assert report["no_retry_gates"]["consumed_observation_prs"] == [149, 150, 152]
    assert report["no_retry_gates"]["consumed_failed_formal_proof_pr"] == 122
    assert report["no_retry_gates"]["retry_authorized"] is False
    print(
        "PASS: exact six-file P10-U7A Bank hands-on readiness verified "
        "(75/75, P10-U6 102/102, gate PASS)"
    )


if __name__ == "__main__":
    main()
