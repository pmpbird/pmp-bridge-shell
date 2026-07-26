#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "35a0b9793322f97f6d4b6df6f78369aa0d4f8854"
GATE = ROOT / "audit/pass6/pass6-permanent-no-blind-flying-gate-v1.json"
FIXTURE = ROOT / "audit/pass6/fixtures/pass6-unit7-no-blind-flying-positive-v1.json"
REPORT = ROOT / "audit/pass6/pass6-unit7-closure-certification-v1.json"
RECEIPT = ROOT / "audit/pass6/receipts/RECEIPT_P6_U7_PASS6_CLOSURE_20260726T160000Z_001.json"
RUNNER = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
TEST = ROOT / "tools/test_pass6_unit7_no_blind_flying_gate_v1.py"
WORKFLOW = ROOT / ".github/workflows/permanent-no-blind-flying-gate-v1.yml"
P6_U5_POLICY = ROOT / "audit/pass6/pass6-ci-lane-artifact-policy-v1.json"
P6_U6_WORKFLOW = ROOT / ".github/workflows/pass6-unit6-deterministic-fault-injection-v1.yml"
EXPECTED = {
    ".github/workflows/permanent-no-blind-flying-gate-v1.yml",
    "audit/pass6/fixtures/pass6-unit7-no-blind-flying-positive-v1.json",
    "audit/pass6/pass6-permanent-no-blind-flying-gate-v1.json",
    "audit/pass6/pass6-unit7-closure-certification-v1.json",
    "audit/pass6/receipts/RECEIPT_P6_U7_PASS6_CLOSURE_20260726T160000Z_001.json",
    "tools/run_pass6_unit7_no_blind_flying_gate_v1.py",
    "tools/test_pass6_unit7_no_blind_flying_gate_v1.py",
    "tools/verify_pass6_unit7_closure_v1.py",
}
P6_U6_SENTINELS = {
    ".github/workflows/pass6-unit6-deterministic-fault-injection-v1.yml",
    "audit/pass6/pass6-deterministic-fault-injection-unit6-proof-v1.json",
    "audit/pass6/pass6-fault-injection-catalog-v1.json",
    "audit/pass6/receipts/RECEIPT_P6_U6_DETERMINISTIC_FAULT_INJECTION_20260726T154500Z_001.json",
    "tools/run_pass6_unit6_fault_injection_v1.js",
    "tools/test_pass6_unit6_fault_injection_v1.js",
    "tools/verify_pass6_unit6_fault_injection_v1.py",
}
UNIT_STATUSES = {
    "P6-U1": "PURE_CONTRACT_PROVEN",
    "P6-U2": "READONLY_VIEW_EXPORT_PROVEN",
    "P6-U3": "CROSS_SYSTEM_INVARIANT_MATRIX_PROVEN",
    "P6-U4": "DETERMINISTIC_PROOF_HARNESS_PROVEN",
    "P6-U5": "CI_EVIDENCE_POLICY_PROVEN",
    "P6-U6": "DETERMINISTIC_FAULT_PRESERVATION_PROVEN",
}
PROTECTED_PREFIXES = (
    "pmp-",
    "safe-writer",
    "resident",
    "bug-memory",
    "Index.html",
    "index.html",
)


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
    lines = text.splitlines()
    paths: set[str] = set()
    in_paths = False
    for line in lines:
        if line == "    paths:":
            in_paths = True
            continue
        if in_paths and line.startswith("      - "):
            paths.add(line.strip()[2:].strip().strip("'\""))
            continue
        if in_paths:
            break
    return paths


def main() -> None:
    base = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else BASE
    assert base == BASE
    changed = changed_paths(base)
    assert changed == EXPECTED, (sorted(changed), sorted(EXPECTED))
    assert not any(path.startswith(PROTECTED_PREFIXES) for path in changed)

    gate = json.loads(GATE.read_text())
    fixture = json.loads(FIXTURE.read_text())
    report = json.loads(REPORT.read_text())
    receipt = json.loads(RECEIPT.read_text())
    policy = json.loads(P6_U5_POLICY.read_text())
    assert gate["type"] == "PMP_PASS6_PERMANENT_NO_BLIND_FLYING_GATE_V1"
    assert gate["version"] == "1.0.0"
    assert gate["status"] == "ACTIVE_ON_MERGE"
    assert gate["applies_to_passes"] == [7, 8, 9, 10, 11, 12, 13]
    assert set(gate["activation_scope"]) == EXPECTED
    assert gate["no_retry_gates"]["retry_authorized"] is False
    assert len(policy["lanes"]) == 5
    assert len(policy["artifact_roles"]) == 9
    assert policy["policy"]["automatic_retry"] == "FORBIDDEN"
    assert policy["policy"]["failed_attempt_erasure"] == "FORBIDDEN"

    assert report["base_main_commit"] == BASE
    assert report["status"] == "PASS6_CLOSED_NO_BLIND_FLYING_GATE_ACTIVE"
    assert set(report["changed_paths"]) == EXPECTED
    assert receipt["status"] == "PASS6_CLOSED_NO_BLIND_FLYING_GATE_ACTIVE"
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["gate"] == GATE.relative_to(ROOT).as_posix()
    assert receipt["evidence"] == REPORT.relative_to(ROOT).as_posix()

    units = report["completed_units"]
    assert [item["unit"] for item in units] == list(UNIT_STATUSES)
    for item in units:
        assert item["status"] == UNIT_STATUSES[item["unit"]]
        record = ROOT / item["record"]
        prior_receipt = ROOT / item["receipt"]
        assert record.is_file() and prior_receipt.is_file()
        assert item["record_sha256"] == sha(record)
        assert item["receipt_sha256"] == sha(prior_receipt)
        payload = json.loads(record.read_text())
        assert payload["unit"] == item["unit"]
        assert payload["status"] == item["status"]

    inputs = report["gate_inputs"]
    for key, path in (
        ("contract_sha256", GATE),
        ("positive_fixture_sha256", FIXTURE),
        ("runner_sha256", RUNNER),
        ("test_sha256", TEST),
    ):
        assert inputs[key] == sha(path), (key, inputs[key], sha(path))

    test_output = output("python3", str(TEST.relative_to(ROOT)))
    assert "permanent no-blind-flying gate (166/166)" in test_output
    fixture_result = json.loads(
        output(
            "python3",
            str(RUNNER.relative_to(ROOT)),
            "--fixture",
            str(FIXTURE.relative_to(ROOT)),
        )
    )
    assert fixture_result["status"] == "PASS"
    assert fixture_result["mode"] == "LATER_IMPLEMENTATION_UNIT"
    assert fixture_result["unit_id"] == "P7-U1"
    assert fixture_result["gate_records"] == 1
    assert fixture_result["errors"] == []
    assert fixture_result["result_sha256"] == inputs["positive_result_sha256"]
    repo_result = json.loads(
        output(
            "python3",
            str(RUNNER.relative_to(ROOT)),
            "--base",
            BASE,
        )
    )
    assert repo_result["status"] == "PASS"
    assert repo_result["mode"] == "ACTIVATION_SCOPE"
    assert repo_result["changed_paths"] == sorted(EXPECTED)
    assert repo_result["errors"] == []

    assert workflow_paths(P6_U6_WORKFLOW.read_text()) == P6_U6_SENTINELS
    workflow = WORKFLOW.read_text()
    assert "  pull_request:" in workflow
    assert "    paths:" not in workflow
    for required in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Run permanent gate and preserve complete attempt",
        "Upload complete no-blind-flying evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert required in workflow
    assert workflow.index("Upload complete no-blind-flying evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )

    coverage = report["closure_coverage"]
    assert coverage["units_required"] == 6
    assert coverage["units_reconciled"] == 6
    assert coverage["records_hash_verified"] == 6
    assert coverage["receipts_hash_verified"] == 6
    assert coverage["gate_assertions_passed"] == 166
    assert coverage["later_passes_gated"] == 7
    assert coverage["ci_lanes_available"] == 5
    assert coverage["artifact_roles_required"] == 9
    assert set(report["exit_criteria"].values()) == {"PASS"}
    assert all(value is False for value in report["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["authority"]["retry_authorized"] is False
    assert report["next_step"]["id"] == "P7-U1"
    assert report["next_step"]["requires_user_app_check"] is False
    assert receipt["next_safe_move"]["step_id"] == "P7-U1"
    assert receipt["next_safe_move"]["requires_user_app_check"] is False
    assert fixture["expected"]["status"] == "PASS"

    print(
        "PASS: exact eight-file P6-U7 closure and permanent no-blind-flying "
        "activation verified (6 units, 166/166 assertions, Passes 7-13 gated)"
    )


if __name__ == "__main__":
    main()
