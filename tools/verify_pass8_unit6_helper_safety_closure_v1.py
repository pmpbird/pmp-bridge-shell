#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "06a0ad231cba79c52cab349b233e9b28ecdb096b"
REPORT = ROOT / "audit/pass8/pass8-helper-unit6-closure-certification-v1.json"
RECEIPT = ROOT / "audit/pass8/receipts/RECEIPT_P8_U6_HELPER_SAFETY_CLOSURE_20260726T190000Z_001.json"
TEST = ROOT / "tools/test_pass8_unit6_helper_safety_closure_v1.py"
WORKFLOW = ROOT / ".github/workflows/pass8-unit6-helper-safety-closure-v1.yml"
GATE_RUNNER = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
EXPECTED = {
    ".github/workflows/pass8-unit6-helper-safety-closure-v1.yml",
    "audit/pass8/pass8-helper-unit6-closure-certification-v1.json",
    "audit/pass8/receipts/RECEIPT_P8_U6_HELPER_SAFETY_CLOSURE_20260726T190000Z_001.json",
    "tools/test_pass8_unit6_helper_safety_closure_v1.py",
    "tools/verify_pass8_unit6_helper_safety_closure_v1.py",
}
SOURCE_INPUTS = {
    "p8_u1_sha256": ROOT / "audit/pass8/pass8-helper-unit1-inventory-v1.json",
    "p8_u2_sha256": ROOT / "audit/pass8/pass8-helper-unit2-capability-contract-v1.json",
    "p8_u3_sha256": ROOT / "audit/pass8/pass8-helper-unit3-registration-events-v1.json",
    "p8_u4_sha256": ROOT / "audit/pass8/pass8-helper-unit4-owner-diagnostics-integration-v1.json",
    "p8_u5_sha256": ROOT / "audit/pass8/pass8-helper-unit5-isolation-restart-denial-proof-v1.json",
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
    assert report["unit_id"] == "P8-U6"
    assert report["status"] == "PASS8_HELPER_RULES_CERTIFIED"
    assert report["pass8_result"] == "PASS"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == []
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["status"] == report["status"]
    assert receipt["pass8_result"] == "PASS"
    for key, path in SOURCE_INPUTS.items():
        assert report["inputs"][key] == sha(path), (key, report["inputs"][key], sha(path))

    test_output = output(sys.executable, str(TEST.relative_to(ROOT)))
    match = re.search(r"certification \((\d+)/(\d+)\)", test_output)
    assert match and match.group(1) == match.group(2)
    assertions = int(match.group(1))
    assert assertions == report["verification"]["assertions_passed"]
    assert report["verification"]["assertions_total"] == assertions
    assert report["verification"]["assertions_failed"] == 0
    assert report["evidence_summary"]["prior_assertions"] == 1525
    assert len(report["evidence_summary"]["units"]) == 5
    assert sum(row["assertions"] for row in report["evidence_summary"]["units"]) == 1525
    assert all(row["all_required_checks_green"] for row in report["evidence_summary"]["github_heads"].values())

    decision = report["observation_sufficiency"]
    assert decision["decision"] == "NEW_SCARCE_OBSERVATION_NOT_REQUIRED"
    assert decision["new_observation_performed"] is False
    assert decision["special_authority_consumed"] is False
    assert decision["retry_of_consumed_observation"] is False
    assert decision["user_app_check_required"] is False
    assert decision["formal_proof_required"] is False
    assert "not a new live observation" in decision["claim_ceiling"]

    assert all(report["exit_criteria"].values())
    boundary = report["pass9_boundary"]
    assert boundary["entry_unit"] == "P9-U1"
    assert boundary["bank_owner"] == "bank_screen_owner"
    assert boundary["continuous_run_owner"] == "continuous_run_level_owner"
    assert boundary["cross_delegation"] == "FORBIDDEN"
    assert boundary["actual_repair_target"] == "P9-U3"

    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "static_contract"
    assert binding["diagnostic_matrix_update"]["status"] == "CONFIRMED_UNCHANGED"
    assert len(binding["diagnostic_evidence_routes"]) == 6
    assert binding["fault_injection"]["status"] == "NOT_APPLICABLE"
    assert binding["fault_injection"]["cases"] == []
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    gate = json.loads(output(sys.executable, str(GATE_RUNNER.relative_to(ROOT)), "--base", BASE))
    assert gate["status"] == "PASS"
    assert gate["unit_id"] == "P8-U6"
    assert gate["gate_records"] == 1
    assert gate["summary"]["runtime_paths"] == 0
    assert gate["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for required in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete P8-U6 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert required in workflow
    assert workflow.index("Upload complete P8-U6 evidence") < workflow.index("Enforce preserved result after upload")
    assert workflow.rstrip().endswith('run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"')

    assert all(value is False for value in report["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["no_retry_gates"]["consumed_observation_prs"] == [149, 150, 152]
    assert report["no_retry_gates"]["formal_proof_pr"] == 122
    assert report["no_retry_gates"]["retry_authorized"] is False
    assert report["next_step"]["id"] == "P9-U1"
    assert report["next_step"]["requires_user_app_check"] is False
    assert report["next_step"]["requires_new_explicit_authority"] is False
    assert receipt["next_safe_move"]["step_id"] == "P9-U1"
    print(
        "PASS: exact five-file P8-U6 Helper safety closure verified "
        f"({assertions}/{assertions}, gate PASS, no scarce observation)"
    )


if __name__ == "__main__":
    main()
