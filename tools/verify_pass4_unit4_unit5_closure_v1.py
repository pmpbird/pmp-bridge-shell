#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    ".github/workflows/pass4-unit4-unit5-closure-v1.yml",
    "audit/pass4/pass4-boot-status-strip-unit4-hands-on-reconciliation-v1.json",
    "audit/pass4/pass4-boot-status-strip-unit5-closure-certification-v1.json",
    "audit/pass4/receipts/RECEIPT_P4_U4_UNIT_CLOSURE_20260726T063514Z_001.json",
    "audit/pass4/receipts/RECEIPT_P4_U5_PASS_CLOSURE_20260726T063514Z_001.json",
    "tools/test_pass4_unit4_unit5_closure_v1.py",
    "tools/verify_pass4_unit4_unit5_closure_v1.py",
}
PROTECTED = {
    "pmp-boot-status-strip-owner-v1.js",
    "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html",
    "pmp-current-map-v12.json",
    "pmp-current-route-resolver-v1.js",
    "pmp-route-guardian-current-loader-v22.html",
    "pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html",
    "pmp-app-orchestrator-v1.js",
    "pmp-app-current.html",
    "pmp-runtime-integrity-manifest-v1.json",
    "audit/a003-manifest-seal.json",
}
RECEIPTS = (
    "audit/pass4/receipts/RECEIPT_P4_U4_UNIT_CLOSURE_20260726T063514Z_001.json",
    "audit/pass4/receipts/RECEIPT_P4_U5_PASS_CLOSURE_20260726T063514Z_001.json",
)


def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def main():
    base = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else "HEAD^"
    changed = set(filter(None, output("git", "diff", "--name-only", f"{base}...HEAD").splitlines()))
    assert changed == EXPECTED, (sorted(changed), sorted(EXPECTED))
    assert not changed & PROTECTED

    workflow = (ROOT / ".github/workflows/pass4-unit4-unit5-closure-v1.yml").read_text()
    for forbidden in (
        "workflow_dispatch",
        "playwright",
        "http.server",
        "run_pass4_unit4_bounded_live_observation",
        "run_pass4_unit4_replacement_observation",
    ):
        assert forbidden not in workflow, forbidden

    for relative in RECEIPTS:
        receipt = json.loads((ROOT / relative).read_text())
        assert receipt["schema"] == "PMP_APP_ORCHESTRATOR_STEP_RECEIPT_V1"
        assert receipt["status"] == "PASS_BOUNDED"
        assert receipt["authority"]["special_authority_type"] == "NONE"
        assert receipt["authority"]["special_authority_consumed"] is False
        assert receipt["scope"]["changed_paths"] == sorted(EXPECTED)
        assert receipt["effects"] == {
            "production_runtime_changed": False,
            "runtime_integrity_changed": False,
            "persisted_user_data_changed": False,
            "historical_evidence_changed": False,
            "github_changed": False,
        }

    subprocess.check_call(["python3", "tools/test_pass4_unit4_unit5_closure_v1.py"], cwd=ROOT)
    print("PASS: exact seven-file evidence-only Pass 4 closure scope verified")


if __name__ == "__main__":
    main()
