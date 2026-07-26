#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "8b389e244913f8727444478ccc9e681795ab0529"
POLICY = ROOT / "audit/pass6/pass6-ci-lane-artifact-policy-v1.json"
FIXTURE = ROOT / "audit/pass6/fixtures/pass6-unit5-ci-evidence-envelope-positive-v1.json"
REPORT = ROOT / "audit/pass6/pass6-ci-lane-artifact-unit5-proof-v1.json"
RECEIPT = ROOT / "audit/pass6/receipts/RECEIPT_P6_U5_CI_EVIDENCE_POLICY_20260726T104000Z_001.json"
RUNNER = ROOT / "tools/run_pass6_unit5_ci_evidence_policy_v1.py"
TEST = ROOT / "tools/test_pass6_unit5_ci_evidence_policy_v1.py"
P6_U4_WORKFLOW = ROOT / ".github/workflows/pass6-unit4-deterministic-proof-harness-v1.yml"
P6_U5_WORKFLOW = ROOT / ".github/workflows/pass6-unit5-ci-evidence-policy-v1.yml"
EXPECTED = {
    ".github/workflows/pass6-unit4-deterministic-proof-harness-v1.yml",
    ".github/workflows/pass6-unit5-ci-evidence-policy-v1.yml",
    "audit/pass6/fixtures/pass6-unit5-ci-evidence-envelope-positive-v1.json",
    "audit/pass6/pass6-ci-lane-artifact-policy-v1.json",
    "audit/pass6/pass6-ci-lane-artifact-unit5-proof-v1.json",
    "audit/pass6/receipts/RECEIPT_P6_U5_CI_EVIDENCE_POLICY_20260726T104000Z_001.json",
    "tools/run_pass6_unit5_ci_evidence_policy_v1.py",
    "tools/test_pass6_unit5_ci_evidence_policy_v1.py",
    "tools/verify_pass6_unit5_ci_evidence_policy_v1.py",
}
EXPECTED_P6_U4_SENTINELS = {
    "audit/pass6/fixtures/pass6-unit4-deterministic-proof-harness-positive-v1.json",
    "audit/pass6/pass6-deterministic-browser-frame-event-unit4-proof-v1.json",
    "audit/pass6/receipts/RECEIPT_P6_U4_DETERMINISTIC_PROOF_HARNESS_20260726T102000Z_001.json",
    "tools/pass6_deterministic_browser_frame_event_harness_v1.js",
    "tools/run_pass6_unit4_deterministic_proof_harness_v1.js",
    "tools/test_pass6_unit4_deterministic_proof_harness_v1.js",
    "tools/verify_pass6_unit4_deterministic_proof_harness_v1.py",
}
PROTECTED_PREFIXES = ("pmp-", "safe-writer", "resident", "bug-memory")


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
    assert not any(path.startswith(PROTECTED_PREFIXES) for path in changed)

    policy = json.loads(POLICY.read_text())
    fixture = json.loads(FIXTURE.read_text())
    report = json.loads(REPORT.read_text())
    receipt = json.loads(RECEIPT.read_text())
    assert report["base_main_commit"] == BASE
    assert report["status"] == "CI_EVIDENCE_POLICY_PROVEN"
    assert set(report["changed_paths"]) == EXPECTED
    assert receipt["status"] == "CI_EVIDENCE_POLICY_PROVEN"
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["policy"] == POLICY.relative_to(ROOT).as_posix()
    assert receipt["evidence"] == REPORT.relative_to(ROOT).as_posix()

    assert report["inputs"]["policy_sha256"] == sha(POLICY)
    assert report["inputs"]["fixture_sha256"] == sha(FIXTURE)
    assert report["inputs"]["runner_sha256"] == sha(RUNNER)
    assert report["inputs"]["test_sha256"] == sha(TEST)
    test_output = output("python3", str(TEST.relative_to(ROOT)))
    assert "CI lane, exact-scope, flake, and artifact policy (469/469)" in test_output
    result = json.loads(output("python3", str(RUNNER.relative_to(ROOT))))
    assert result["status"] == "PASS"
    assert result["lane"] == "deterministic_browser_harness"
    assert result["attempts"] == 1
    assert result["artifacts"] == 9
    assert result["checks_required"] == 6
    assert result["checks_passed"] == 6
    assert result["scope_paths"] == 4
    assert result["flake_detected"] is False
    assert result["errors"] == []
    assert result["result_sha256"] == report["baseline_evaluation"]["result_sha256"]
    assert all(value == 0 for value in result["side_effects"].values())

    assert len(policy["lanes"]) == 5
    assert len(policy["required_checks"]) == 6
    assert len(policy["artifact_roles"]) == 9
    assert all(lane["max_attempts"] == 1 for lane in policy["lanes"].values())
    assert all(lane["required_artifact_roles"] == "ALL" for lane in policy["lanes"].values())
    assert policy["policy"]["automatic_retry"] == "FORBIDDEN"
    assert policy["policy"]["failed_attempt_erasure"] == "FORBIDDEN"
    assert fixture["expected_final_status"] == "PASS"

    assert workflow_paths(P6_U4_WORKFLOW.read_text()) == EXPECTED_P6_U4_SENTINELS
    workflow = P6_U5_WORKFLOW.read_text()
    for required in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
    ):
        assert required in workflow
    assert workflow.index("Upload complete attempt artifacts") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )
    assert report["policy_coverage"]["failure_upload_before_enforcement"] is True
    assert report["ci_routing_repair"]["standing_a003_coverage_preserved"] is True
    assert all(value is False for value in report["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["authority"]["retry_authorized"] is False
    assert report["next_step"]["id"] == "P6-U6"
    assert report["next_step"]["requires_user_app_check"] is False
    assert receipt["next_safe_move"]["step_id"] == "P6-U6"
    assert receipt["next_safe_move"]["requires_user_app_check"] is False

    print(
        "PASS: exact nine-file P6-U5 CI evidence policy and completed-workflow "
        "routing verified (5 lanes, 9 artifacts, 469/469 assertions)"
    )


if __name__ == "__main__":
    main()
