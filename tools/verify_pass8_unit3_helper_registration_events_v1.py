#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "74c969586918cb2ee82122d184294a28e9b92edb"
REPORT = ROOT / "audit/pass8/pass8-helper-unit3-registration-events-v1.json"
RECEIPT = (
    ROOT
    / "audit/pass8/receipts/RECEIPT_P8_U3_HELPER_REGISTRATION_EVENTS_20260726T180500Z_001.json"
)
RUNNER = ROOT / "tools/run_pass8_unit3_helper_registration_events_v1.js"
TEST = ROOT / "tools/test_pass8_unit3_helper_registration_events_v1.js"
WORKFLOW = ROOT / ".github/workflows/pass8-unit3-helper-registration-events-v1.yml"
GATE_RUNNER = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
EXPECTED = {
    ".github/workflows/pass8-unit3-helper-registration-events-v1.yml",
    "audit/pass8/pass8-helper-unit3-registration-events-v1.json",
    "audit/pass8/receipts/RECEIPT_P8_U3_HELPER_REGISTRATION_EVENTS_20260726T180500Z_001.json",
    "tools/run_pass8_unit3_helper_registration_events_v1.js",
    "tools/test_pass8_unit3_helper_registration_events_v1.js",
    "tools/verify_pass8_unit3_helper_registration_events_v1.py",
}
SOURCE_INPUTS = {
    "unit2_contract_sha256": ROOT / "audit/pass8/pass8-helper-unit2-capability-contract-v1.json",
    "unit2_runner_sha256": ROOT / "tools/run_pass8_unit2_helper_capability_contract_v1.js",
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
    assert report["base_main_commit"] == BASE
    assert report["unit_id"] == "P8-U3"
    assert report["status"] == "HELPER_REGISTRATION_EVENTS_PROVEN"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == []
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["status"] == report["status"]
    for key, path in SOURCE_INPUTS.items():
        assert report["inputs"][key] == sha(path), (key, report["inputs"][key], sha(path))

    scenario = json.loads(output("node", str(RUNNER.relative_to(ROOT))))
    result = scenario["result"]
    assert scenario["status"] == "PASS"
    assert result["status"] == "PASS"
    assert result["summary"] == {
        "events": 3,
        "accepted": 3,
        "mutated": 3,
        "rejected": 0,
        "registered_helpers": 1,
        "pending_growth": 1,
        "revoked_helpers": 0,
        "authority_grants": 0,
        "shared_operation_identities": True,
    }
    assert result["result_sha256"] == report["event_verification"]["result_sha256"]
    assert scenario["restore"]["status"] == "RESTORED"
    assert scenario["restore"]["result"]["snapshot"] == result["snapshot"]
    assert scenario["journal_package"]["entry_count"] == 3
    assert all(value is False for value in result["effects"].values())

    test_output = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"events \((\d+)/(\d+)\)", test_output)
    assert match and match.group(1) == match.group(2)
    assertions = int(match.group(1))
    assert assertions == report["verification"]["assertions_passed"] == 155
    assert report["verification"]["assertions_failed"] == 0
    assert receipt["coverage"]["assertions"] == assertions

    contract = report["registration_contract"]
    assert contract["event_version"] == "PMP_HELPER_REGISTRATION_EVENT_V1"
    assert contract["journal_version"] == "PMP_HELPER_REGISTRATION_JOURNAL_V1"
    assert contract["model"] == "APPEND_ONLY_DIGEST_CHAIN_FAIL_CLOSED"
    assert len(contract["event_types"]) == 5
    assert len(contract["required_event_fields"]) == 16
    assert len(contract["required_authority_fields"]) == 6
    assert contract["growth_policy"] == "OBSERVED_PENDING_NO_AUTHORITY"
    assert contract["restore_policy"] == "ATOMIC_EXACT_PACKAGE_OR_EMPTY"
    assert contract["denial_policy"] == "REJECT_BEFORE_JOURNAL_OR_STATE_MUTATION"
    assert report["event_verification"] == {
        "eligible_helpers": 12,
        "event_types": 5,
        "required_event_fields": 16,
        "required_authority_fields": 6,
        "held_declared_helpers": 2,
        "unknown_sources_held": 9,
        "scenario_events": 3,
        "scenario_registered_helpers": 1,
        "scenario_pending_growth": 1,
        "result_sha256": result["result_sha256"],
    }

    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "static_contract"
    assert binding["diagnostic_matrix_update"]["status"] == "CONFIRMED_UNCHANGED"
    assert binding["fault_injection"]["status"] == "COVERED"
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    gate = json.loads(output("python3", str(GATE_RUNNER.relative_to(ROOT)), "--base", BASE))
    assert gate["status"] == "PASS"
    assert gate["unit_id"] == "P8-U3"
    assert gate["gate_records"] == 1
    assert gate["summary"]["runtime_paths"] == 0
    assert gate["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for required in (
        "actions/setup-node@v4",
        "actions/setup-python@v5",
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete P8-U3 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "retention-days: 90",
    ):
        assert required in workflow
    assert workflow.index("Upload complete P8-U3 evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )
    assert all(value is False for value in report["effects"].values())
    assert all(value is False for value in receipt["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["next_step"]["id"] == "P8-U4"
    assert report["next_step"]["requires_user_app_check"] is False
    assert receipt["next_safe_move"]["step_id"] == "P8-U4"
    print(
        "PASS: exact six-file P8-U3 Helper registration events verified "
        f"({assertions}/{assertions}, atomic restore, gate PASS, zero effects)"
    )


if __name__ == "__main__":
    main()
