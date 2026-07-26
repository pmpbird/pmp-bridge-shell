#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "dbf80f16ca11c3a09309931176d80e2b97549b3a"
REPORT = ROOT / "audit/pass8/pass8-helper-unit5-isolation-restart-denial-proof-v1.json"
RECEIPT = ROOT / "audit/pass8/receipts/RECEIPT_P8_U5_HELPER_ISOLATION_RESTART_DENIAL_20260726T185000Z_001.json"
UNIT4 = ROOT / "audit/pass8/pass8-helper-unit4-owner-diagnostics-integration-v1.json"
RUNTIME = ROOT / "pmp-helper-owner-integration-v1.js"
VIEW = ROOT / "pmp-helper-owner-diagnostics-view-v1.js"
RUNNER = ROOT / "tools/run_pass8_unit5_helper_isolation_restart_denial_v1.js"
TEST = ROOT / "tools/test_pass8_unit5_helper_isolation_restart_denial_v1.js"
WORKFLOW = ROOT / ".github/workflows/pass8-unit5-helper-isolation-restart-denial-v1.yml"
GATE_RUNNER = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
EXPECTED = {
    ".github/workflows/pass8-unit5-helper-isolation-restart-denial-v1.yml",
    "audit/pass8/pass8-helper-unit5-isolation-restart-denial-proof-v1.json",
    "audit/pass8/receipts/RECEIPT_P8_U5_HELPER_ISOLATION_RESTART_DENIAL_20260726T185000Z_001.json",
    "tools/run_pass8_unit5_helper_isolation_restart_denial_v1.js",
    "tools/test_pass8_unit5_helper_isolation_restart_denial_v1.js",
    "tools/verify_pass8_unit5_helper_isolation_restart_denial_v1.py",
}
SOURCE_INPUTS = {
    "unit4_integration_sha256": UNIT4,
    "production_runtime_sha256": RUNTIME,
    "production_diagnostics_view_sha256": VIEW,
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
    assert report["unit_id"] == "P8-U5"
    assert report["status"] == "HELPER_ISOLATION_RESTART_DENIAL_PROVEN"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == []
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["status"] == report["status"]
    for key, path in SOURCE_INPUTS.items():
        assert report["inputs"][key] == sha(path), (key, report["inputs"][key], sha(path))

    node = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"proof \((\d+)/(\d+)\)", node)
    assert match and match.group(1) == match.group(2)
    assertions = int(match.group(1))
    assert assertions == report["verification"]["assertions_passed"] == 251
    regression = output(
        "node", "tools/test_pass8_unit4_helper_owner_diagnostics_integration_v1.js"
    )
    assert "(443/443)" in regression
    result = json.loads(output("node", str(RUNNER.relative_to(ROOT))))
    proof = report["proof"]
    assert result["status"] == "PASS"
    assert result["registration"]["registered_count"] == proof["eligible_registration_successes"] == 12
    assert result["registration"]["authority_grants"] == proof["authority_grants"] == 0
    assert result["registration"]["behavior_authorizations"] == proof["behavior_authorizations"] == 0
    assert len(result["held"]) == proof["held_declared_denials"] == 2
    assert len(result["unknown"]) == proof["unknown_helper_denials"] == 9
    assert len(result["owner_absence"]) == proof["missing_section_owner_denials"] == 12
    assert len(result["binding_denials"]) == proof["binding_faults_denied"] == 96
    assert all(row["code"] == row["expected"] for row in result["binding_denials"])
    growth = [row for row in result["growth"] if row["accepted"]]
    assert len(growth) == proof["growth_observations_accepted_no_authority"] == 1
    assert growth[0]["authority_granted"] is False
    assert growth[0]["behavior_authorized"] is False
    assert sum(not row["accepted"] for row in result["growth"]) == proof["non_growth_observation_denials"] == 11
    assert result["duplicate_sequence"]["duplicate"] == "DUPLICATE_EVENT_IGNORED"
    assert result["duplicate_sequence"]["conflicting"] == "REJECTED_DUPLICATE_EVENT_CONFLICT"
    assert result["duplicate_sequence"]["stale"] == proof["stale_sequence_result"]
    assert result["duplicate_sequence"]["gap"] == proof["sequence_gap_result"]
    assert result["duplicate_sequence"]["chain"] == proof["chain_mismatch_result"]
    assert result["revocation"]["snapshot"]["revoked"]["pass2_atlas_adapter"] == 1
    assert result["revocation"]["snapshot"]["registered"][0]["status"] == "REVOKED_STATIC_EVENT_ONLY"
    assert result["revocation"]["snapshot"]["registered"][0]["behavior_authorized"] is False
    assert result["restart"]["package"]["entry_count"] == proof["restart_entries"] == 12
    assert result["restart"]["exact"]["restored"] is True
    assert len(result["restart"]["exact"]["operation_ids"]) == 12
    assert len(result["restart"]["exact"]["registered"]) == 12
    assert len(result["restart"]["tamper_cases"]) == proof["restart_tamper_cases"] == 4
    for row in result["restart"]["tamper_cases"]:
        assert row["restored"] is False
        assert row["registered_after"] == row["journal_after"] == 0
    assert result["restart"]["missing_owner"]["restored"] is False
    assert result["restart"]["missing_owner"]["registered_after"] == 0
    assert result["restart"]["missing_owner"]["journal_after"] == 0
    bounded = result["bounded_diagnostics"]
    assert bounded["visible_event_count"] == proof["diagnostic_visible_events"] == 128
    assert bounded["events_truncated"] is True
    for key in (
        "capability_ids_exposed",
        "helper_source_hashes_exposed",
        "raw_authority_payloads_exposed",
        "source_versions_exposed",
    ):
        assert bounded["disclosure"][key] is False, key
    assert all(value == 0 for value in bounded["side_effects"].values())
    assert all(value is False for value in result["effects"].values())

    matrix = report["diagnostic_and_proof_matrix"]
    assert len(matrix["invariants"]) == 7
    assert matrix["assertions"] == 251
    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "deterministic_integration"
    assert binding["diagnostic_matrix_update"]["status"] == "ADDED"
    assert binding["diagnostic_matrix_update"]["applicable_matrix"] == REPORT.relative_to(ROOT).as_posix()
    assert binding["fault_injection"]["status"] == "COVERED"
    assert len(binding["fault_injection"]["cases"]) == 17
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    gate = json.loads(output("python3", str(GATE_RUNNER.relative_to(ROOT)), "--base", BASE))
    assert gate["status"] == "PASS", gate
    assert gate["unit_id"] == "P8-U5"
    assert gate["gate_records"] == 1
    assert gate["summary"]["runtime_paths"] == 0
    assert gate["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for required in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete P8-U5 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert required in workflow
    assert workflow.index("Upload complete P8-U5 evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )
    assert all(value is False for value in report["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["next_step"]["id"] == "P8-U6"
    assert report["next_step"]["requires_user_app_check"] is False
    assert receipt["next_safe_move"]["step_id"] == "P8-U6"
    print(
        "PASS: exact six-file P8-U5 Helper isolation, restart, growth, "
        f"revocation, and denial proof verified ({assertions}/{assertions}, gate PASS)"
    )


if __name__ == "__main__":
    main()
