#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / "audit/pass5/pass5-mount-registry-unit7-closure-certification-v1.json"
RECEIPT = ROOT / "audit/pass5/receipts/RECEIPT_P5_U7_CLOSURE_20260726T084800Z_001.json"
BASE = "f3401b9183e48ecc2855d6579dd0600c1905b5f9"
EXPECTED = {
    ".github/workflows/pass5-unit7-closure-certification-v1.yml",
    "audit/pass5/pass5-mount-registry-unit7-closure-certification-v1.json",
    "audit/pass5/receipts/RECEIPT_P5_U7_CLOSURE_20260726T084800Z_001.json",
    "tools/verify_pass5_unit7_closure_certification_v1.py",
}
PRODUCTION = {
    "pmp-app-current.html",
    "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html",
    "pmp-current-map-v12.json",
    "pmp-runtime-integrity-manifest-v1.json",
    "audit/a003-manifest-seal.json",
    "pmp-mount-lifecycle-contract-v1.js",
    "pmp-mount-lifecycle-runtime-v1.js",
    "pmp-mount-lifecycle-diagnostics-view-v1.js",
    "pmp-mount-registry-v1.js",
    "pmp-diagnostics-owner-v1.js",
    "pmp-diagnostics-bottom-tab-forcer-v1.js",
    "pmp-app-orchestrator-v1.js",
}
MERGED = [
    "8ca3ea78d51f69ebec0c1a445bf895dd6d1be812",
    "820af994d4ae38ab3190318780d82d1f3715decd",
    "bb556d956b9d46095513651419d07e367caaaec6",
    "6f47790517b68e53626d0646f66ffa22b01aeab5",
    "cf26518b4e1946f79e12b81b3126726625189208",
    "da45468bb06ded75aa847b335cce6fdd5dd1e987",
    "f3401b9183e48ecc2855d6579dd0600c1905b5f9",
]


def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    base = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else "HEAD^"
    changed = set(filter(None, output("git", "diff", "--name-only", f"{base}...HEAD").splitlines()))
    assert changed == EXPECTED, (sorted(changed), sorted(EXPECTED))
    assert not changed & PRODUCTION
    assert all(Path(path).parts[0] in {".github", "audit", "tools"} for path in changed)

    cert = json.loads(CERT.read_text())
    assert cert["base_main_commit"] == BASE
    assert cert["status"] == "PASS5_COMPLETE"
    assert cert["completion"]["pass5_complete"] is True
    assert cert["completion"]["remaining_pass5_implementation"] == []
    assert cert["completion"]["next_pass"] == 6
    assert [row["id"] for row in cert["units"]] == [
        "P5-U1", "P5-U2", "P5-U3", "P5-U4", "P5-U5", "P5-U6", "P5-U7"
    ]
    assert len(cert["exit_criteria"]) == 4
    assert all(row["result"] == "PASS" for row in cert["exit_criteria"])
    assert cert["next_step"]["id"] == "P6-U1"
    assert cert["next_step"]["requires_user_app_check"] is False
    assert cert["next_step"]["requires_new_explicit_authority"] is False

    for commit in MERGED:
        subprocess.check_call(["git", "merge-base", "--is-ancestor", commit, BASE], cwd=ROOT)

    reports = {}
    receipts = {}
    for unit in cert["units"][:-1]:
        reports[unit["id"]] = json.loads((ROOT / unit["record"]).read_text())
        receipts[unit["id"]] = json.loads((ROOT / unit["receipt"]).read_text())
        assert receipts[unit["id"]]["schema"] == "PMP_APP_ORCHESTRATOR_STEP_RECEIPT_V1"
        assert receipts[unit["id"]]["status"] in {"PASS_BOUNDED", "PASS_COMPLETE"}

    assert reports["P5-U1"]["status"] == "READINESS_AUDIT_PASS"
    assert reports["P5-U2"]["status"] == "PURE_CONTRACT_PROVEN_PENDING_MERGE"
    assert reports["P5-U3"]["status"] == "PASSIVE_INTEGRATION_PROVEN_PENDING_MERGE"
    assert reports["P5-U4"]["status"] == "READ_ONLY_DIAGNOSTICS_PROVEN_PENDING_MERGE"
    assert reports["P5-U5"]["status"] == "PASS_ISOLATED_PROOF"
    assert reports["P5-U6"]["decision"] == "NEW_CURRENT_PATH_OBSERVATION_NOT_REQUIRED"
    assert reports["P5-U5"]["coverage"]["assertions_total"] == 138
    assert reports["P5-U5"]["coverage"]["assertions_passed"] == 138
    assert reports["P5-U5"]["coverage"]["assertions_failed"] == 0
    assert all(row["result"] == "PROVEN" for row in reports["P5-U6"]["pass5_exit_criteria"])

    for rel, digest in reports["P5-U5"]["components"]["source_sha256"].items():
        assert sha(ROOT / rel) == digest, rel

    identity = cert["production_identity"]
    assert identity["source_hashes_match_p5_u5_proof"] is True
    assert identity["exact_source_integrity_green"] is True
    safety = cert["safety"]
    assert all(value is False for value in safety.values())
    effects = cert["effects"]
    assert all(value is False for value in effects.values())
    authority = cert["authority"]
    assert authority["special_authority_type"] == "NONE"
    assert authority["special_authority_consumed"] is False
    assert authority["consumed_observation_prs"] == [149, 150, 152]
    assert authority["consumed_failed_formal_proof_pr"] == 122
    assert authority["retry_authorized"] is False
    assert cert["github"]["all_unit_pull_requests_merged"] is True
    assert cert["github"]["all_required_workflows_green"] is True

    receipt = json.loads(RECEIPT.read_text())
    assert receipt["schema"] == "PMP_APP_ORCHESTRATOR_STEP_RECEIPT_V1"
    assert receipt["status"] == "PASS_COMPLETE"
    assert receipt["scope"]["changed_paths"] == sorted(EXPECTED)
    assert receipt["verification"]["units_certified"] == 7
    assert receipt["verification"]["exit_criteria_passed"] == 4
    assert receipt["verification"]["result"] == "PASS5_COMPLETE"
    assert receipt["effects"]["production_runtime_changed"] is False

    workflow = (ROOT / ".github/workflows/pass5-unit7-closure-certification-v1.yml").read_text()
    for forbidden in (
        "workflow_dispatch",
        "playwright",
        "http.server",
        "npm install",
        "pip install",
        "pmp-app-current.html",
        "pmp-runtime-integrity-manifest-v1.json",
    ):
        assert forbidden not in workflow, forbidden

    assert not output("git", "status", "--porcelain"), "verification changed the worktree"
    print("PASS: Pass 5 closure certified; P6-U1 is the exact next move")


if __name__ == "__main__":
    main()
