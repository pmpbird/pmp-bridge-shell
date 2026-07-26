#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    ".github/workflows/pass5-unit2-mount-lifecycle-contract-v1.yml",
    "audit/pass5/pass5-mount-registry-diagnostics-unit2-lifecycle-contract-v1.json",
    "audit/pass5/receipts/RECEIPT_P5_U2_CONTRACT_20260726T070211Z_001.json",
    "pmp-mount-lifecycle-contract-v1.js",
    "tools/test_pass5_unit2_mount_lifecycle_contract_v1.js",
    "tools/verify_pass5_unit2_mount_lifecycle_contract_v1.py",
}
PROTECTED = {
    "pmp-mount-registry-v1.js",
    "pmp-pass2-atlas-adapter-v2.js",
    "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html",
    "pmp-app-orchestrator-v1.js",
    "pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html",
    "pmp-safe-area-surface-fill-v1.js",
    "pmp-diagnostics-owner-v1.js",
    "pmp-diagnostics-bottom-tab-forcer-v1.js",
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

    source = (ROOT / "pmp-mount-lifecycle-contract-v1.js").read_text()
    for forbidden in (
        "localStorage",
        "sessionStorage",
        "indexedDB",
        "document.",
        "fetch(",
        "setTimeout(",
        "setInterval(",
        "location.",
        ".src=",
    ):
        assert forbidden not in source, forbidden

    workflow = (ROOT / ".github/workflows/pass5-unit2-mount-lifecycle-contract-v1.yml").read_text()
    for forbidden in ("workflow_dispatch", "playwright", "http.server", "npm install", "pip install"):
        assert forbidden not in workflow, forbidden

    audit = json.loads(
        (ROOT / "audit/pass5/pass5-mount-registry-diagnostics-unit2-lifecycle-contract-v1.json").read_text()
    )
    assert audit["status"] == "PURE_CONTRACT_PROVEN_PENDING_MERGE"
    assert audit["implementation"]["production_loaded"] is False
    assert audit["implementation"]["storage_access"] is False
    assert audit["legacy_compatibility_facade"]["storage_migration"] is False
    assert audit["next_step"]["id"] == "P5-U3"
    assert audit["next_step"]["requires_user_app_check"] is False

    receipt = json.loads(
        (ROOT / "audit/pass5/receipts/RECEIPT_P5_U2_CONTRACT_20260726T070211Z_001.json").read_text()
    )
    assert receipt["schema"] == "PMP_APP_ORCHESTRATOR_STEP_RECEIPT_V1"
    assert receipt["kind"] == "CONTRACT"
    assert receipt["status"] == "PASS_BOUNDED"
    assert receipt["scope"]["changed_paths"] == sorted(EXPECTED)
    assert receipt["authority"]["special_authority_type"] == "NONE"
    assert receipt["authority"]["special_authority_consumed"] is False

    subprocess.check_call(["node", "tools/test_pass5_unit2_mount_lifecycle_contract_v1.js"], cwd=ROOT)
    print("PASS: exact six-file pure P5-U2 contract scope verified")


if __name__ == "__main__":
    main()
