#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "bf0de4f13a833b86ac830656e88e7dcab6e71d3a"
REPORT = ROOT / "audit/pass7/pass7-section-owner-unit3-registration-events-v1.json"
RECEIPT = ROOT / "audit/pass7/receipts/RECEIPT_P7_U3_OWNER_REGISTRATION_EVENTS_20260726T163500Z_001.json"
RUNNER = ROOT / "tools/run_pass7_unit3_owner_registration_events_v1.py"
TEST = ROOT / "tools/test_pass7_unit3_owner_registration_events_v1.py"
WORKFLOW = ROOT / ".github/workflows/pass7-unit3-owner-registration-events-v1.yml"
GATE_RUNNER = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
EXPECTED = {
    ".github/workflows/pass7-unit3-owner-registration-events-v1.yml",
    "audit/pass7/pass7-section-owner-unit3-registration-events-v1.json",
    "audit/pass7/receipts/RECEIPT_P7_U3_OWNER_REGISTRATION_EVENTS_20260726T163500Z_001.json",
    "tools/run_pass7_unit3_owner_registration_events_v1.py",
    "tools/test_pass7_unit3_owner_registration_events_v1.py",
    "tools/verify_pass7_unit3_owner_registration_events_v1.py",
}
SOURCE_INPUTS = {
    "unit1_inventory_sha256": ROOT / "audit/pass7/pass7-section-owner-unit1-inventory-v1.json",
    "unit2_capability_contract_sha256": ROOT / "audit/pass7/pass7-section-owner-unit2-capability-contract-v1.json",
    "cross_system_invariant_catalog_sha256": ROOT / "audit/pass6/pass6-cross-system-invariant-catalog-v1.json",
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
    event_contract = report["event_contract"]
    assert report["base_main_commit"] == BASE
    assert report["unit_id"] == "P7-U3"
    assert report["status"] == "OWNER_REGISTRATION_EVENTS_PROVEN"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == []
    assert receipt["status"] == report["status"]
    assert set(receipt["changed_paths"]) == EXPECTED
    for key, path in SOURCE_INPUTS.items():
        assert report["inputs"][key] == sha(path), (key, report["inputs"][key], sha(path))

    assert event_contract["event_version"] == "PMP_SECTION_OWNER_REGISTRATION_EVENT_V1"
    assert event_contract["capability_contract_version"] == "PMP_SECTION_OWNER_CAPABILITY_CONTRACT_V1"
    assert len(event_contract["event_types"]) == 4
    assert len(event_contract["required_fields"]) == 12
    assert event_contract["appearance_grants_authority"] is False
    assert event_contract["unknown_owner_policy"] == "GROWTH_OBSERVED_PENDING_NO_AUTHORITY_ONLY"
    assert event_contract["operation_identity"] == "SHARED_BY_REGISTRY_JOURNAL_AND_DIAGNOSTICS"

    test_output = output("python3", str(TEST.relative_to(ROOT)))
    match = re.search(r"owner registration events \((\d+)/(\d+)\)", test_output)
    assert match and match.group(1) == match.group(2)
    assertions = int(match.group(1))
    assert assertions >= 70
    result = json.loads(output("python3", str(RUNNER.relative_to(ROOT))))
    assert result["status"] == "PASS"
    assert result["summary"]["events"] == 3
    assert result["summary"]["accepted"] == 3
    assert result["summary"]["registered_owners"] == 1
    assert result["summary"]["pending_growth"] == 1
    assert result["summary"]["authority_grants"] == 0
    assert result["summary"]["shared_operation_identities"] is True
    assert result["result_sha256"] == report["event_verification"]["result_sha256"]
    assert assertions == report["verification"]["assertions_passed"]
    assert all(value is False for value in result["result"]["effects"].values())

    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "static_contract"
    assert binding["diagnostic_matrix_update"]["status"] == "CONFIRMED_UNCHANGED"
    assert binding["fault_injection"]["status"] == "COVERED"
    assert len(binding["fault_injection"]["cases"]) == 17
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    assert binding["special_authority"]["consumed"] is False
    gate = json.loads(output("python3", str(GATE_RUNNER.relative_to(ROOT)), "--base", BASE))
    assert gate["status"] == "PASS"
    assert gate["unit_id"] == "P7-U3"
    assert gate["gate_records"] == 1
    assert gate["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for required in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete P7-U3 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert required in workflow
    assert workflow.index("Upload complete P7-U3 evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )
    assert all(value is False for value in report["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["next_step"]["id"] == "P7-U4"
    assert report["next_step"]["requires_user_app_check"] is False
    assert receipt["next_safe_move"]["step_id"] == "P7-U4"
    print(
        "PASS: exact six-file P7-U3 owner registration event contract verified "
        f"({assertions}/{assertions} assertions, permanent gate PASS)"
    )


if __name__ == "__main__":
    main()
