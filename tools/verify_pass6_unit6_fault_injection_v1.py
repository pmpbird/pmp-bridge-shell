#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "d66f8a32aae8b4c26699032a2dce18d6d41c6e8c"
FAULTS = ROOT / "audit/pass6/pass6-fault-injection-catalog-v1.json"
CATALOG = ROOT / "audit/pass6/pass6-cross-system-invariant-catalog-v1.json"
SCENARIO = ROOT / "audit/pass6/fixtures/pass6-unit4-deterministic-proof-harness-positive-v1.json"
POLICY = ROOT / "audit/pass6/pass6-ci-lane-artifact-policy-v1.json"
HARNESS = ROOT / "tools/pass6_deterministic_browser_frame_event_harness_v1.js"
RUNNER = ROOT / "tools/run_pass6_unit6_fault_injection_v1.js"
TEST = ROOT / "tools/test_pass6_unit6_fault_injection_v1.js"
REPORT = ROOT / "audit/pass6/pass6-deterministic-fault-injection-unit6-proof-v1.json"
RECEIPT = ROOT / "audit/pass6/receipts/RECEIPT_P6_U6_DETERMINISTIC_FAULT_INJECTION_20260726T154500Z_001.json"
WORKFLOW = ROOT / ".github/workflows/pass6-unit6-deterministic-fault-injection-v1.yml"
P6_U5_WORKFLOW = ROOT / ".github/workflows/pass6-unit5-ci-evidence-policy-v1.yml"
EXPECTED = {
    ".github/workflows/pass6-unit6-deterministic-fault-injection-v1.yml",
    "audit/pass6/pass6-deterministic-fault-injection-unit6-proof-v1.json",
    "audit/pass6/pass6-fault-injection-catalog-v1.json",
    "audit/pass6/receipts/RECEIPT_P6_U6_DETERMINISTIC_FAULT_INJECTION_20260726T154500Z_001.json",
    "tools/run_pass6_unit6_fault_injection_v1.js",
    "tools/test_pass6_unit6_fault_injection_v1.js",
    "tools/verify_pass6_unit6_fault_injection_v1.py",
}
P6_U5_SENTINELS = {
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
PROTECTED_PREFIXES = (
    "pmp-",
    "safe-writer",
    "resident",
    "bug-memory",
    "Index.html",
    "index.html",
)
REQUIRED_CATEGORIES = [
    "timeout",
    "animation",
    "nested_frames",
    "malformed_state",
    "missing_dependencies",
    "duplicate_events",
    "restart",
    "partial_failure",
]


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

    faults = json.loads(FAULTS.read_text())
    policy = json.loads(POLICY.read_text())
    report = json.loads(REPORT.read_text())
    receipt = json.loads(RECEIPT.read_text())
    assert faults["type"] == "PMP_PASS6_DETERMINISTIC_FAULT_INJECTION_CATALOG_V1"
    assert faults["required_categories"] == REQUIRED_CATEGORIES
    assert [item["category"] for item in faults["faults"]] == REQUIRED_CATEGORIES
    assert len({item["id"] for item in faults["faults"]}) == 8
    assert faults["execution"]["attempts"] == 1
    assert faults["execution"]["automatic_retry"] is False
    assert faults["execution"]["special_authority_required"] is False
    assert faults["execution"]["failed_attempt_erasure"] is False

    assert report["base_main_commit"] == BASE
    assert report["status"] == "DETERMINISTIC_FAULT_PRESERVATION_PROVEN"
    assert set(report["changed_paths"]) == EXPECTED
    assert receipt["status"] == "DETERMINISTIC_FAULT_PRESERVATION_PROVEN"
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["catalog"] == FAULTS.relative_to(ROOT).as_posix()
    assert receipt["evidence"] == REPORT.relative_to(ROOT).as_posix()
    inputs = report["inputs"]
    for key, path in (
        ("fault_catalog_sha256", FAULTS),
        ("invariant_catalog_sha256", CATALOG),
        ("baseline_scenario_sha256", SCENARIO),
        ("ci_evidence_policy_sha256", POLICY),
        ("harness_sha256", HARNESS),
        ("runner_sha256", RUNNER),
        ("test_sha256", TEST),
    ):
        assert inputs[key] == sha(path), (key, inputs[key], sha(path))

    test_output = output("node", str(TEST.relative_to(ROOT)))
    assert "deterministic fault injection (233/233)" in test_output
    result = json.loads(output("node", str(RUNNER.relative_to(ROOT))))
    assert result["status"] == "PASS"
    assert result["attempts"] == 1
    assert result["automatic_retry_performed"] is False
    assert result["special_authority_required"] is False
    assert result["special_authority_consumed"] is False
    assert [item["category"] for item in result["cases"]] == REQUIRED_CATEGORIES
    assert all(item["status"] == "FAULT_PRESERVED" for item in result["cases"])
    assert all(item["original_failure_preserved"] is True for item in result["cases"])
    assert all(item["harness_result_hash_valid"] is True for item in result["cases"])
    assert all(item["restart_result_hash_valid"] is True for item in result["cases"])
    assert all(item["forbidden_effects_observed"] is False for item in result["cases"])
    assert result["summary"] == {
        "faults_required": 8,
        "faults_executed": 8,
        "faults_preserved": 8,
        "primary_failures_preserved": 8,
        "secondary_failures_preserved": 8,
        "restart_sequences": 1,
        "retries": 0,
        "forbidden_effects": 0,
    }
    assert result["result_sha256"] == report["baseline_evaluation"]["result_sha256"]

    assert policy["policy"]["automatic_retry"] == "FORBIDDEN"
    assert policy["policy"]["failed_attempt_erasure"] == "FORBIDDEN"
    assert policy["artifact_contract"]["upload_even_when_test_fails"] is True
    assert policy["artifact_contract"]["enforce_result_after_upload"] is True
    assert len(policy["artifact_roles"]) == 9
    assert workflow_paths(P6_U5_WORKFLOW.read_text()) == P6_U5_SENTINELS

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for required in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete fault evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert required in workflow
    assert workflow.index("Upload complete fault evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )

    assert report["fault_coverage"]["preserved"] == 8
    assert report["fault_coverage"]["automatic_retries"] == 0
    assert report["evidence_policy"]["artifact_roles"] == 9
    assert report["evidence_policy"]["failure_upload_before_enforcement"] is True
    assert all(value is False for value in report["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["authority"]["retry_authorized"] is False
    assert report["next_step"]["id"] == "P6-U7"
    assert report["next_step"]["requires_user_app_check"] is False
    assert receipt["next_safe_move"]["step_id"] == "P6-U7"
    assert receipt["next_safe_move"]["requires_user_app_check"] is False

    print(
        "PASS: exact seven-file P6-U6 deterministic fault injection verified "
        "(8/8 faults, 233/233 assertions, 9 artifact roles)"
    )


if __name__ == "__main__":
    main()
