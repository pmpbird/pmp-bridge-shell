#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "094bfa198e9d28296da28985fe513f255a3bd0f1"
CATALOG = ROOT / "audit/pass6/pass6-cross-system-invariant-catalog-v1.json"
REPORT = ROOT / "audit/pass6/pass6-cross-system-invariant-unit3-matrix-v1.json"
RECEIPT = ROOT / "audit/pass6/receipts/RECEIPT_P6_U3_CROSS_SYSTEM_MATRIX_20260726T095500Z_001.json"
RUNNER = ROOT / "tools/run_pass6_unit3_cross_system_invariant_matrix_v1.py"
TEST = ROOT / "tools/test_pass6_unit3_cross_system_invariant_matrix_v1.py"
P6_U2_WORKFLOW = ROOT / ".github/workflows/pass6-unit2-readonly-journal-view-export-v1.yml"
EXPECTED = {
    ".github/workflows/pass6-unit2-readonly-journal-view-export-v1.yml",
    ".github/workflows/pass6-unit3-cross-system-invariant-matrix-v1.yml",
    "audit/pass6/pass6-cross-system-invariant-catalog-v1.json",
    "audit/pass6/pass6-cross-system-invariant-unit3-matrix-v1.json",
    "audit/pass6/receipts/RECEIPT_P6_U3_CROSS_SYSTEM_MATRIX_20260726T095500Z_001.json",
    "tools/run_pass6_unit3_cross_system_invariant_matrix_v1.py",
    "tools/test_pass6_unit3_cross_system_invariant_matrix_v1.py",
    "tools/verify_pass6_unit3_cross_system_invariant_matrix_v1.py",
}
EXPECTED_P6_U2_SENTINELS = {
    "audit/pass6/pass6-diagnostic-journal-unit2-readonly-view-export-v1.json",
    "audit/pass6/receipts/RECEIPT_P6_U2_READONLY_VIEW_EXPORT_20260726T093700Z_001.json",
    "tools/generate_pass6_unit2_integrity_updates_v1.py",
    "tools/test_pass6_unit2_readonly_journal_view_export_v1.js",
    "tools/verify_pass6_unit2_readonly_journal_view_export_v1.py",
}
PROTECTED_PREFIXES = (
    "pmp-",
    "safe-writer",
    "resident",
    "bug-memory",
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

    catalog = json.loads(CATALOG.read_text())
    report = json.loads(REPORT.read_text())
    receipt = json.loads(RECEIPT.read_text())
    assert report["base_main_commit"] == BASE
    assert report["status"] == "CROSS_SYSTEM_INVARIANT_MATRIX_PROVEN"
    assert set(report["changed_paths"]) == EXPECTED
    assert receipt["status"] == "CROSS_SYSTEM_INVARIANT_MATRIX_PROVEN"
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["catalog"] == CATALOG.relative_to(ROOT).as_posix()
    assert receipt["evidence"] == REPORT.relative_to(ROOT).as_posix()

    verification = report["verification"]
    assert verification["assertions_total"] == 316
    assert verification["assertions_passed"] == 316
    assert verification["assertions_failed"] == 0
    assert verification["catalog_sha256"] == sha(CATALOG)
    assert verification["runner_sha256"] == sha(RUNNER)
    assert verification["test_sha256"] == sha(TEST)
    test_output = output("python3", str(TEST.relative_to(ROOT)))
    assert "cross-system invariant and regression matrix (316/316)" in test_output

    matrix_output = output(
        "python3",
        str(RUNNER.relative_to(ROOT)),
        "--catalog",
        str(CATALOG.relative_to(ROOT)),
    )
    matrix = json.loads(matrix_output)
    assert matrix["status"] == "PASS"
    assert matrix["summary"] == {
        "invariants_total": 20,
        "invariants_passed": 20,
        "invariants_failed": 0,
        "required_subsystems": 9,
        "covered_subsystems": 9,
        "required_scenarios": 9,
        "covered_scenarios": 9,
        "errors": 0,
    }
    assert matrix["errors"] == []
    assert matrix["catalog_sha256"] == report["catalog"]["stable_content_sha256"]
    assert set(matrix["subsystem_coverage"]) == set(catalog["required_subsystems"])
    assert set(matrix["scenario_coverage"]) == set(catalog["required_scenarios"])
    assert all(row["pass"] for row in matrix["results"])
    assert matrix["side_effects"] == {
        "production_files_changed": 0,
        "storage_writes": 0,
        "persisted_user_data_writes": 0,
        "network_requests": 0,
        "route_changes": 0,
        "repairs": 0,
        "live_observations": 0,
        "formal_proofs": 0,
    }

    assert workflow_paths(P6_U2_WORKFLOW.read_text()) == EXPECTED_P6_U2_SENTINELS
    assert report["ci_routing_repair"]["standing_a003_coverage_preserved"] is True
    assert report["matrix"]["current_enforcement_and_future_gate_distinguished"] is True
    assert report["matrix"]["later_pass_completion_claimed"] is False
    assert report["failure_policy"]["fail_open_path"] is False
    assert all(value is False for value in report["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["authority"]["retry_authorized"] is False
    assert report["next_step"]["id"] == "P6-U4"
    assert report["next_step"]["requires_user_app_check"] is False
    assert report["next_step"]["requires_new_explicit_authority"] is False
    assert receipt["next_safe_move"]["step_id"] == "P6-U4"
    assert receipt["next_safe_move"]["requires_user_app_check"] is False

    print(
        "PASS: exact eight-file P6-U3 cross-system invariant matrix and "
        "completed-workflow routing verified (20/20 invariants, 316/316 assertions)"
    )


if __name__ == "__main__":
    main()
