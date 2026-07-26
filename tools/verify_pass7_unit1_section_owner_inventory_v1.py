#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "35a22c1c456d19c18868c87786d462a73aa921d8"
REPORT = ROOT / "audit/pass7/pass7-section-owner-unit1-inventory-v1.json"
RECEIPT = ROOT / "audit/pass7/receipts/RECEIPT_P7_U1_SECTION_OWNER_INVENTORY_20260726T161500Z_001.json"
RUNNER = ROOT / "tools/run_pass7_unit1_section_owner_inventory_v1.py"
TEST = ROOT / "tools/test_pass7_unit1_section_owner_inventory_v1.py"
WORKFLOW = ROOT / ".github/workflows/pass7-unit1-section-owner-inventory-v1.yml"
PERMANENT_WORKFLOW = ROOT / ".github/workflows/permanent-no-blind-flying-gate-v1.yml"
GATE_RUNNER = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
EXPECTED = {
    ".github/workflows/pass7-unit1-section-owner-inventory-v1.yml",
    "audit/pass7/pass7-section-owner-unit1-inventory-v1.json",
    "audit/pass7/receipts/RECEIPT_P7_U1_SECTION_OWNER_INVENTORY_20260726T161500Z_001.json",
    "tools/run_pass7_unit1_section_owner_inventory_v1.py",
    "tools/test_pass7_unit1_section_owner_inventory_v1.py",
    "tools/verify_pass7_unit1_section_owner_inventory_v1.py",
}
SOURCE_INPUTS = {
    "section_owner_registry_sha256": ROOT / "pmp-section-owner-registry-v1.js",
    "legacy_owner_diagnostics_sha256": ROOT / "pmp-owner-diagnostics-foundation-v1.js",
    "diagnostics_owner_sha256": ROOT / "pmp-diagnostics-owner-v1.js",
    "app_orchestrator_sha256": ROOT / "pmp-app-orchestrator-v1.js",
    "mount_lifecycle_runtime_sha256": ROOT / "pmp-mount-lifecycle-runtime-v1.js",
    "runner_sha256": RUNNER,
    "test_sha256": TEST,
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

    report = json.loads(REPORT.read_text())
    receipt = json.loads(RECEIPT.read_text())
    assert report["base_main_commit"] == BASE
    assert report["unit_id"] == "P7-U1"
    assert report["status"] == "SECTION_OWNER_INVENTORY_PROVEN"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == []
    assert receipt["status"] == "SECTION_OWNER_INVENTORY_PROVEN"
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["evidence"] == REPORT.relative_to(ROOT).as_posix()
    for key, path in SOURCE_INPUTS.items():
        assert report["inputs"][key] == sha(path), (key, report["inputs"][key], sha(path))

    test_output = output("python3", str(TEST.relative_to(ROOT)))
    assert "section-owner inventory (168/168)" in test_output
    result = json.loads(output("python3", str(RUNNER.relative_to(ROOT))))
    assert result["status"] == "PASS"
    assert result["summary"] == {
        "owners_declared": 8,
        "sections_inventory": 8,
        "owners_with_source_candidates": 6,
        "owners_without_source_candidates": 2,
        "owner_named_root_sources": 32,
        "unregistered_owner_named_sources": 25,
        "observed_facts": 6,
        "inferred_conclusions": 3,
        "unresolved_cases": 4,
    }
    assert result["result_sha256"] == report["inventory"]["result_sha256"]
    assert result["summary"]["owners_declared"] == report["inventory"]["owners_declared"]
    assert result["summary"]["unresolved_cases"] == len(
        report["inventory"]["unresolved_cases"]
    )
    assert [row["id"] for row in result["owners"]] == [
        row["id"] for row in report["inventory"]["declared_owners"]
    ]
    assert all(value is False for value in result["effects"].values())

    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "static_contract"
    assert binding["diagnostic_matrix_update"]["status"] == "CONFIRMED_UNCHANGED"
    assert binding["fault_injection"]["status"] == "NOT_APPLICABLE"
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    assert binding["special_authority"]["consumed"] is False
    gate_result = json.loads(
        output(
            "python3",
            str(GATE_RUNNER.relative_to(ROOT)),
            "--base",
            BASE,
        )
    )
    assert gate_result["status"] == "PASS"
    assert gate_result["mode"] == "LATER_IMPLEMENTATION_UNIT"
    assert gate_result["unit_id"] == "P7-U1"
    assert gate_result["gate_records"] == 1
    assert gate_result["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for required in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete P7-U1 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert required in workflow
    assert workflow.index("Upload complete P7-U1 evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )
    permanent = PERMANENT_WORKFLOW.read_text()
    assert "  pull_request:" in permanent
    assert "    paths:" not in permanent

    assert report["verification"]["assertions_passed"] == 168
    assert all(value is False for value in report["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["authority"]["retry_authorized"] is False
    assert report["next_step"]["id"] == "P7-U2"
    assert report["next_step"]["requires_user_app_check"] is False
    assert receipt["next_safe_move"]["step_id"] == "P7-U2"
    assert receipt["next_safe_move"]["requires_user_app_check"] is False

    print(
        "PASS: exact six-file P7-U1 section-owner inventory verified "
        "(8 owners, 4 unresolved cases, 168/168 assertions, permanent gate PASS)"
    )


if __name__ == "__main__":
    main()
