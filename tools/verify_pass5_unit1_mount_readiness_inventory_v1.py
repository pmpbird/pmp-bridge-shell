#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    ".github/workflows/pass5-unit1-mount-readiness-audit-v1.yml",
    "audit/pass5/pass5-mount-registry-diagnostics-unit1-readiness-inventory-v1.json",
    "audit/pass5/receipts/RECEIPT_P5_U1_READINESS_20260726T065204Z_001.json",
    "tools/test_pass5_unit1_mount_readiness_inventory_v1.py",
    "tools/verify_pass5_unit1_mount_readiness_inventory_v1.py",
}
PROTECTED = {
    "pmp-mount-registry-v1.js",
    "pmp-pass2-atlas-adapter-v2.js",
    "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html",
    "pmp-app-orchestrator-v1.js",
    "pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html",
    "pmp-mount-registry-v1-cachelift-20260706b.js",
    "pmp-safe-area-surface-fill-v1.js",
    "pmp-diagnostics-owner-v1.js",
    "pmp-diagnostics-bottom-tab-forcer-v1.js",
    "pmp-section-owner-registry-v1.js",
    "pmp-helper-registry-v1.js",
    "pmp-phase8-atlas-marker-v1.js",
    "pmp-pass1r-version-aligner-v1.js",
    "pmp-active-path-discovery-machine-v1.js",
    "pmp-current-map-v12.json",
    "pmp-runtime-integrity-manifest-v1.json",
    "audit/a003-manifest-seal.json",
    "pmp-app-current.html",
}


def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def main():
    base = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else "HEAD^"
    changed = set(filter(None, output("git", "diff", "--name-only", f"{base}...HEAD").splitlines()))
    assert changed == EXPECTED, (sorted(changed), sorted(EXPECTED))
    assert not changed & PROTECTED

    workflow = (ROOT / ".github/workflows/pass5-unit1-mount-readiness-audit-v1.yml").read_text()
    for forbidden in ("workflow_dispatch", "playwright", "http.server", "npm install", "pip install"):
        assert forbidden not in workflow, forbidden

    receipt = json.loads(
        (ROOT / "audit/pass5/receipts/RECEIPT_P5_U1_READINESS_20260726T065204Z_001.json").read_text()
    )
    assert receipt["schema"] == "PMP_APP_ORCHESTRATOR_STEP_RECEIPT_V1"
    assert receipt["kind"] == "READINESS"
    assert receipt["status"] == "PASS_BOUNDED"
    assert receipt["scope"]["changed_paths"] == sorted(EXPECTED)
    assert receipt["authority"]["special_authority_type"] == "NONE"
    assert receipt["authority"]["special_authority_consumed"] is False
    assert receipt["effects"] == {
        "production_runtime_changed": False,
        "runtime_integrity_changed": False,
        "persisted_user_data_changed": False,
        "historical_evidence_changed": False,
        "github_changed": False,
    }

    subprocess.check_call(["python3", "tools/test_pass5_unit1_mount_readiness_inventory_v1.py"], cwd=ROOT)
    print("PASS: exact five-file read-only P5-U1 readiness scope verified")


if __name__ == "__main__":
    main()
