#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "625bdc869b57b5da1496577d9b3688d5bc122632"
REPORT = ROOT / "audit/pass8/pass8-helper-unit1-inventory-v1.json"
RECEIPT = (
    ROOT
    / "audit/pass8/receipts/RECEIPT_P8_U1_HELPER_INVENTORY_20260726T173500Z_001.json"
)
RUNNER = ROOT / "tools/run_pass8_unit1_helper_inventory_v1.js"
TEST = ROOT / "tools/test_pass8_unit1_helper_inventory_v1.js"
WORKFLOW = ROOT / ".github/workflows/pass8-unit1-helper-inventory-v1.yml"
GATE_RUNNER = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
EXPECTED = {
    ".github/workflows/pass8-unit1-helper-inventory-v1.yml",
    "audit/pass8/pass8-helper-unit1-inventory-v1.json",
    "audit/pass8/receipts/RECEIPT_P8_U1_HELPER_INVENTORY_20260726T173500Z_001.json",
    "tools/run_pass8_unit1_helper_inventory_v1.js",
    "tools/test_pass8_unit1_helper_inventory_v1.js",
    "tools/verify_pass8_unit1_helper_inventory_v1.py",
}
SOURCE_INPUTS = {
    "helper_rules_sha256": ROOT / "pmp-pass8-helper-rules-v1.js",
    "legacy_helper_registry_sha256": ROOT / "pmp-helper-registry-v1.js",
    "pass7_owner_inventory_sha256": ROOT
    / "audit/pass7/pass7-section-owner-unit1-inventory-v1.json",
    "pass7_closure_sha256": ROOT
    / "audit/pass7/pass7-section-owner-unit6-closure-certification-v1.json",
    "runner_sha256": RUNNER,
    "test_sha256": TEST,
}
EXPECTED_COUNTS = {
    "tracked_files": 1877,
    "declared_helpers": 14,
    "declared_unique_ids": 14,
    "declared_unique_files": 14,
    "declared_files_present": 14,
    "declared_files_missing": 0,
    "accepted_helpers": 12,
    "diagnostic_only_helpers": 1,
    "legacy_helpers_declared": 1,
    "growth_helpers": 1,
    "declared_owner_labels": 8,
    "exact_p7_owner_label_matches": 0,
    "unresolved_owner_labels": 8,
    "legacy_registry_helpers": 11,
    "helper_named_root_sources": 12,
    "helper_named_undeclared_sources": 9,
    "storage_keys": 24,
    "panel_ids": 3,
    "duplicate_ids": 0,
    "duplicate_files": 0,
}
EXPECTED_OWNER_CONFLICTS = [
    "active_path_discovery_owner",
    "app_orchestrator",
    "bug_bank_owner",
    "continuous_run_owner",
    "mount_registry",
    "runtime_health_monitor",
    "runtime_version_manager",
    "safe_writer_owner",
]
EXPECTED_UNDECLARED = [
    "pmp-continuous-run-helper-conflict-blocker-v1.js",
    "pmp-helper-bank-live-inspector-v1.js",
    "pmp-helper-bank-live-inspector-v2.js",
    "pmp-helper-problem-display-sync-v1.js",
    "pmp-helper-problem-memory-v1.js",
    "pmp-helper-problem-type-only-v1.js",
    "pmp-helper-problem-type-seeds-v1.js",
    "pmp-helper-symptom-watcher-v1.js",
    "pmp-p15-helper-tidy-v1.js",
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

    report = json.loads(REPORT.read_text())
    receipt = json.loads(RECEIPT.read_text())
    assert report["base_main_commit"] == BASE
    assert report["unit_id"] == "P8-U1"
    assert report["status"] == "HELPER_INVENTORY_PROVEN"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == []
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["status"] == report["status"]
    for key, path in SOURCE_INPUTS.items():
        assert report["inputs"][key] == sha(path), (
            key,
            report["inputs"][key],
            sha(path),
        )

    runtime = json.loads(output("node", str(RUNNER.relative_to(ROOT))))
    assert runtime["type"] == "PMP_PASS8_UNIT1_HELPER_INVENTORY_RESULT_V1"
    assert runtime["status"] == "PASS"
    assert runtime["counts"] == EXPECTED_COUNTS
    assert runtime["result_sha256"] == report["inventory"]["result_sha256"]
    assert runtime["conflicts"]["owner_labels_not_exact_p7_ids"] == (
        EXPECTED_OWNER_CONFLICTS
    )
    assert runtime["conflicts"]["helper_named_sources_without_pass8_declaration"] == (
        EXPECTED_UNDECLARED
    )
    assert runtime["conflicts"]["missing_declared_files"] == []
    assert runtime["conflicts"]["duplicate_ids"] == []
    assert runtime["conflicts"]["duplicate_files"] == []
    assert runtime["conflicts"]["disposition"] == (
        "HOLD_AS_OBSERVED_CONFLICT_NO_AUTHORITY_UNTIL_P8_U2_CONTRACT"
    )
    assert all(value is False for value in runtime["effects"].values())

    test_output = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"inventory \((\d+)/(\d+)\)", test_output)
    assert match and match.group(1) == match.group(2)
    assertions = int(match.group(1))
    assert assertions == report["verification"]["assertions_passed"] == 421
    assert report["verification"]["assertions_failed"] == 0
    expected_report_inventory = {
        **EXPECTED_COUNTS,
        "result_sha256": runtime["result_sha256"],
    }
    expected_report_inventory["exact_pass7_owner_label_matches"] = (
        expected_report_inventory.pop("exact_p7_owner_label_matches")
    )
    assert report["inventory"] == expected_report_inventory
    assert report["conflicts"]["owner_labels_not_exact_pass7_ids"] == (
        EXPECTED_OWNER_CONFLICTS
    )
    assert report["conflicts"]["helper_named_sources_without_pass8_declaration"] == (
        EXPECTED_UNDECLARED
    )

    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "static_contract"
    assert binding["diagnostic_matrix_update"]["status"] == "CONFIRMED_UNCHANGED"
    assert binding["fault_injection"]["status"] == "NOT_APPLICABLE"
    assert binding["fault_injection"]["cases"] == []
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    assert binding["special_authority"] == {
        "required": False,
        "granted": False,
        "consumed": False,
    }
    gate = json.loads(
        output(
            "python3",
            str(GATE_RUNNER.relative_to(ROOT)),
            "--base",
            BASE,
        )
    )
    assert gate["status"] == "PASS"
    assert gate["unit_id"] == "P8-U1"
    assert gate["gate_records"] == 1
    assert gate["summary"]["runtime_paths"] == 0
    assert gate["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for required in (
        "actions/setup-node@v4",
        "node-version: '22'",
        "actions/setup-python@v5",
        "python-version: '3.12'",
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete P8-U1 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert required in workflow
    assert workflow.index("Upload complete P8-U1 evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )

    assert all(value is False for value in report["effects"].values())
    assert all(value is False for value in receipt["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["next_step"]["id"] == "P8-U2"
    assert report["next_step"]["requires_user_app_check"] is False
    assert report["next_step"]["requires_new_explicit_authority"] is False
    assert receipt["next_safe_move"]["step_id"] == "P8-U2"
    print(
        "PASS: exact six-file P8-U1 Helper inventory verified "
        f"({assertions}/{assertions}, gate PASS, zero effects)"
    )


if __name__ == "__main__":
    main()
