#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "9fccfd5200b91d1352739d5f62aadd5d7e075814"
CONTRACT = ROOT / "pmp-diagnostic-journal-contract-v1.js"
TEST = ROOT / "tools/test_pass6_unit1_diagnostic_journal_contract_v1.js"
REPORT = ROOT / "audit/pass6/pass6-diagnostic-journal-unit1-contract-v1.json"
RECEIPT = ROOT / "audit/pass6/receipts/RECEIPT_P6_U1_CONTRACT_20260726T090200Z_001.json"
EXPECTED = {
    ".github/workflows/pass6-unit1-diagnostic-journal-contract-v1.yml",
    "audit/pass6/pass6-diagnostic-journal-unit1-contract-v1.json",
    "audit/pass6/receipts/RECEIPT_P6_U1_CONTRACT_20260726T090200Z_001.json",
    "pmp-diagnostic-journal-contract-v1.js",
    "pmp-app-current.html",
    "pmp-runtime-integrity-manifest-v1.json",
    "audit/a003-manifest-seal.json",
    "tools/generate_pass6_unit1_integrity_updates_v1.py",
    "tools/test_pass6_unit1_diagnostic_journal_contract_v1.js",
    "tools/verify_pass6_unit1_diagnostic_journal_contract_v1.py",
}
PROTECTED = {
    "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html",
    "pmp-current-map-v12.json",
    "pmp-diagnostics-owner-v1.js",
    "pmp-diagnostics-bottom-tab-forcer-v1.js",
    "pmp-mount-lifecycle-contract-v1.js",
    "pmp-mount-lifecycle-runtime-v1.js",
    "pmp-mount-lifecycle-diagnostics-view-v1.js",
    "pmp-bug-catalog-engine-v1.js",
}


def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    base = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else "HEAD^"
    changed = set(filter(None, output("git", "diff", "--name-only", f"{base}...HEAD").splitlines()))
    assert changed == EXPECTED, (sorted(changed), sorted(EXPECTED))
    assert not changed & PROTECTED

    report = json.loads(REPORT.read_text())
    assert report["base_main_commit"] == BASE
    assert report["status"] == "PURE_CONTRACT_PROVEN"
    inventory = report["readiness_inventory"]
    base_paths = output("git", "ls-tree", "-r", "--name-only", BASE).splitlines()
    assert inventory["base_repository_records"] == len(base_paths) == 1788
    assert inventory["diagnostic_named_paths"] == sum("diagnostic" in p.lower() for p in base_paths) == 28
    assert inventory["receipt_named_paths"] == sum("receipt" in p.lower() for p in base_paths) == 165
    assert inventory["journal_named_paths"] == sum("journal" in p.lower() for p in base_paths) == 0
    assert inventory["export_named_paths"] == sum("export" in p.lower() for p in base_paths) == 5
    assert inventory["audit_json_paths"] == sum(
        p.startswith("audit/") and p.endswith(".json") for p in base_paths
    ) == 348

    verification = report["verification"]
    assert verification["assertions_total"] == 116
    assert verification["assertions_passed"] == 116
    assert verification["assertions_failed"] == 0
    assert verification["contract_sha256"] == sha(CONTRACT)
    assert verification["test_sha256"] == sha(TEST)
    assert report["next_step"]["id"] == "P6-U2"
    assert report["next_step"]["requires_user_app_check"] is False
    assert report["next_step"]["requires_new_explicit_authority"] is False
    assert report["effects"]["runtime_integrity_changed"] is True
    assert all(
        value is False
        for key, value in report["effects"].items()
        if key != "runtime_integrity_changed"
    )
    assert report["authority"]["special_authority_type"] == "NONE"
    assert report["authority"]["special_authority_consumed"] is False
    assert report["authority"]["retry_authorized"] is False

    source = CONTRACT.read_text()
    for required in (
        "OBSERVED_FACT",
        "DERIVED_FACT",
        "INFERRED_CONCLUSION",
        "OWNER_ATTESTED",
        "OBSERVER_REPORTED",
        "INFERENCE_BASIS_REQUIRED",
        "SENSITIVE_KEY",
        "CONFLICTING_DUPLICATE",
        "SNAPSHOT_INTEGRITY_MISMATCH",
        "FAIL_PASSIVE_VIOLATION",
    ):
        assert required in source, required
    for forbidden in (
        "localStorage.setItem",
        "indexedDB",
        "fetch(",
        "XMLHttpRequest",
        "document.",
        "location.",
        "postMessage(",
        "applyOwnerEvent",
    ):
        assert forbidden not in source, forbidden

    for loader in (
        "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html",
        "pmp-current-map-v12.json",
        "pmp-diagnostics-owner-v1.js",
    ):
        assert CONTRACT.name not in (ROOT / loader).read_text(), loader

    manifest = json.loads((ROOT / "pmp-runtime-integrity-manifest-v1.json").read_text())
    records = {row["path"]: row for row in manifest["records"]}
    assert CONTRACT.name in records
    assert records[CONTRACT.name]["sha256_hex"] == sha(CONTRACT)
    seal = json.loads((ROOT / "audit/a003-manifest-seal.json").read_text())
    manifest_sha = sha(ROOT / "pmp-runtime-integrity-manifest-v1.json")
    assert seal["manifest_sha256"] == manifest_sha
    assert seal["sealed_branch"] == "agent/pass6-unit1-diagnostic-journal-contract-v1"
    assert seal["runtime_source_set_sha256"] == manifest["runtime_source_set_sha256"]
    bootstrap = (ROOT / "pmp-app-current.html").read_text()
    assert f"const MANIFEST_SHA256='{manifest_sha}';" in bootstrap
    assert CONTRACT.name not in bootstrap

    output("python3", "tools/generate_pass6_unit1_integrity_updates_v1.py")
    assert not output(
        "git",
        "diff",
        "--name-only",
        "--",
        "pmp-runtime-integrity-manifest-v1.json",
        "pmp-app-current.html",
        "audit/a003-manifest-seal.json",
    ), "integrity identities are not deterministic"

    result = output("node", str(TEST))
    assert result == "PASS: P6-U1 diagnostic journal contract (116 assertions)", result

    receipt = json.loads(RECEIPT.read_text())
    assert receipt["schema"] == "PMP_APP_ORCHESTRATOR_STEP_RECEIPT_V1"
    assert receipt["status"] == "PASS_BOUNDED"
    assert receipt["scope"]["changed_paths"] == sorted(EXPECTED)
    assert receipt["verification"]["assertions_total"] == 116
    assert receipt["verification"]["assertions_failed"] == 0
    assert receipt["verification"]["production_load_references"] == 0
    assert receipt["effects"]["production_runtime_changed"] is False
    assert receipt["effects"]["runtime_integrity_changed"] is True

    workflow = (
        ROOT / ".github/workflows/pass6-unit1-diagnostic-journal-contract-v1.yml"
    ).read_text()
    for forbidden in (
        "workflow_dispatch",
        "playwright",
        "http.server",
        "npm install",
        "pip install",
    ):
        assert forbidden not in workflow, forbidden

    assert not output("git", "status", "--porcelain"), "verification changed the worktree"
    print("PASS: exact ten-file P6-U1 diagnostic journal contract and integrity seal verified (116/116)")


if __name__ == "__main__":
    main()
