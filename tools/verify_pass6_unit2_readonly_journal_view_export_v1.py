#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "97d4e7447810de4db8bd62a54e74b738f90f269f"
VIEW_EXPORT = ROOT / "pmp-diagnostic-journal-readonly-view-export-v1.js"
OWNER = ROOT / "pmp-diagnostics-owner-v1.js"
INNER = ROOT / "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html"
TEST = ROOT / "tools/test_pass6_unit2_readonly_journal_view_export_v1.js"
REPORT = ROOT / "audit/pass6/pass6-diagnostic-journal-unit2-readonly-view-export-v1.json"
RECEIPT = ROOT / "audit/pass6/receipts/RECEIPT_P6_U2_READONLY_VIEW_EXPORT_20260726T093700Z_001.json"
MANIFEST = ROOT / "pmp-runtime-integrity-manifest-v1.json"
SEAL = ROOT / "audit/a003-manifest-seal.json"
BOOTSTRAP = ROOT / "pmp-app-current.html"
P6_U1_WORKFLOW = ROOT / ".github/workflows/pass6-unit1-diagnostic-journal-contract-v1.yml"
EXPECTED = {
    ".github/workflows/pass6-unit1-diagnostic-journal-contract-v1.yml",
    ".github/workflows/pass6-unit2-readonly-journal-view-export-v1.yml",
    "audit/a003-manifest-seal.json",
    "audit/pass6/pass6-diagnostic-journal-unit2-readonly-view-export-v1.json",
    "audit/pass6/receipts/RECEIPT_P6_U2_READONLY_VIEW_EXPORT_20260726T093700Z_001.json",
    "pmp-app-current.html",
    "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html",
    "pmp-diagnostic-journal-readonly-view-export-v1.js",
    "pmp-diagnostics-owner-v1.js",
    "pmp-runtime-integrity-manifest-v1.json",
    "tools/generate_pass6_unit2_integrity_updates_v1.py",
    "tools/test_pass6_unit2_readonly_journal_view_export_v1.js",
    "tools/verify_pass6_unit2_readonly_journal_view_export_v1.py",
}
PROTECTED = {
    "pmp-diagnostic-journal-contract-v1.js",
    "pmp-mount-lifecycle-contract-v1.js",
    "pmp-mount-lifecycle-runtime-v1.js",
    "pmp-mount-registry-v1.js",
    "pmp-mount-lifecycle-diagnostics-view-v1.js",
    "pmp-authority-rules-v1.js",
    "pmp-bug-watch-passive-capture-v1.js",
    "pmp-safe-writer-current-return-fix-v1.js",
    "pmp-current-map-v12.json",
}
EXPECTED_P6_U1_SENTINELS = {
    "audit/pass6/pass6-diagnostic-journal-unit1-contract-v1.json",
    "audit/pass6/receipts/RECEIPT_P6_U1_CONTRACT_20260726T090200Z_001.json",
    "tools/generate_pass6_unit1_integrity_updates_v1.py",
    "tools/test_pass6_unit1_diagnostic_journal_contract_v1.js",
    "tools/verify_pass6_unit1_diagnostic_journal_contract_v1.py",
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
    assert base == BASE, base
    changed = changed_paths(base)
    assert changed == EXPECTED, (sorted(changed), sorted(EXPECTED))
    assert not changed & PROTECTED

    report = json.loads(REPORT.read_text())
    receipt = json.loads(RECEIPT.read_text())
    assert report["base_main_commit"] == BASE
    assert report["status"] == "READONLY_VIEW_EXPORT_PROVEN"
    assert set(report["changed_paths"]) == EXPECTED
    assert receipt["status"] == "READONLY_VIEW_EXPORT_PROVEN"
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["evidence"] == REPORT.relative_to(ROOT).as_posix()

    verification = report["verification"]
    assert verification["assertions_total"] == 226
    assert verification["assertions_passed"] == 226
    assert verification["assertions_failed"] == 0
    assert verification["view_export_sha256"] == sha(VIEW_EXPORT)
    assert verification["diagnostics_owner_sha256"] == sha(OWNER)
    assert verification["current_inner_sha256"] == sha(INNER)
    assert verification["test_sha256"] == sha(TEST)
    test_output = output("node", str(TEST.relative_to(ROOT)))
    assert "read-only diagnostic journal view and bounded export (226/226)" in test_output

    module_source = VIEW_EXPORT.read_text()
    owner_source = OWNER.read_text()
    inner_source = INNER.read_text()
    for forbidden in (
        "localStorage",
        "sessionStorage",
        "indexedDB",
        "document.",
        "window.",
        "location.",
        "fetch(",
        "XMLHttpRequest",
        "WebSocket",
        "navigator.",
        "setTimeout(",
        "setInterval(",
        ".append(",
        ".restore(",
    ):
        assert forbidden not in module_source, forbidden
    assert "diagnosticJournal.append" not in owner_source
    assert "diagnosticJournal.restore" not in owner_source
    assert "diagnosticJournal.snapshot" not in owner_source
    assert "readDiagnosticJournal:journalView" in owner_source
    assert "exportDiagnosticJournal:journalExport" in owner_source
    assert "Copy Bounded Journal Export" in owner_source
    contract_pos = inner_source.index("pmp-diagnostic-journal-contract-v1.js?fresh=pass6-unit2")
    view_pos = inner_source.index(
        "pmp-diagnostic-journal-readonly-view-export-v1.js?fresh=pass6-unit2"
    )
    orchestrator_pos = inner_source.index("pmp-app-orchestrator-v1.js?fresh=")
    assert contract_pos < view_pos < orchestrator_pos

    manifest = json.loads(MANIFEST.read_text())
    records = {row["path"]: row for row in manifest["records"]}
    for path in (
        INNER.relative_to(ROOT).as_posix(),
        VIEW_EXPORT.relative_to(ROOT).as_posix(),
        OWNER.relative_to(ROOT).as_posix(),
    ):
        assert records[path]["sha256_hex"] == sha(ROOT / path), path
    assert manifest["counts"]["runtime_records"] == len(manifest["records"]) == 705
    assert manifest["runtime_source_set_sha256"] == verification["runtime_source_set_sha256"]
    assert sha(MANIFEST) == verification["manifest_sha256"]
    seal = json.loads(SEAL.read_text())
    assert seal["manifest_sha256"] == sha(MANIFEST)
    assert seal["runtime_source_set_sha256"] == manifest["runtime_source_set_sha256"]
    assert seal["sealed_branch"] == report["branch"]
    assert "Pass 6 Unit 2" in seal["pass6_context"]
    bootstrap_match = re.search(
        r"const MANIFEST_SHA256='([0-9a-f]{64})';", BOOTSTRAP.read_text()
    )
    assert bootstrap_match and bootstrap_match.group(1) == sha(MANIFEST)

    assert workflow_paths(P6_U1_WORKFLOW.read_text()) == EXPECTED_P6_U1_SENTINELS
    assert report["ci_routing_repair"]["standing_a003_coverage_preserved"] is True
    assert report["source_contract"]["changed"] is False
    assert report["diagnostics_integration"]["append_path_exposed"] is False
    assert report["diagnostics_integration"]["restore_path_exposed"] is False
    assert report["diagnostics_integration"]["journal_storage_key"] is None
    assert report["diagnostics_integration"]["persisted_user_data_authority"] is False
    assert report["privacy_and_authority"]["persisted_user_data_included_in_export"] is False
    assert report["compatibility_boundary"]["consumer_exposure"] == "ZERO"
    assert report["effects"]["journal_persisted"] is False
    assert report["effects"]["synthetic_journal_events_added"] is False
    assert report["effects"]["live_observation_performed"] is False
    assert report["effects"]["formal_proof_performed"] is False
    assert report["effects"]["persisted_user_data_changed"] is False
    assert report["authority"]["special_authority_consumed"] is False
    assert report["authority"]["retry_authorized"] is False
    assert report["next_step"]["id"] == "P6-U3"
    assert report["next_step"]["requires_user_app_check"] is False
    assert report["next_step"]["requires_new_explicit_authority"] is False
    assert receipt["next_safe_move"]["step_id"] == "P6-U3"
    assert receipt["next_safe_move"]["requires_user_app_check"] is False

    print(
        "PASS: exact thirteen-file P6-U2 read-only journal view/export, "
        "integrity binding, and CI routing verified (226/226)"
    )


if __name__ == "__main__":
    main()
