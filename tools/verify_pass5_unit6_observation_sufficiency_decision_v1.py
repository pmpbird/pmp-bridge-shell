#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "audit/pass5/pass5-mount-registry-unit6-observation-sufficiency-decision-v1.json"
RECEIPT = ROOT / "audit/pass5/receipts/RECEIPT_P5_U6_OBSERVATION_DECISION_20260726T083800Z_001.json"
BASE = "da45468bb06ded75aa847b335cce6fdd5dd1e987"
P5_U4_SEALED_MAIN = "6f19ca6594b6a8950caed60d027075d2ba30eb46"
EXPECTED = {
    ".github/workflows/pass5-unit6-observation-sufficiency-decision-v1.yml",
    "audit/pass5/pass5-mount-registry-unit6-observation-sufficiency-decision-v1.json",
    "audit/pass5/receipts/RECEIPT_P5_U6_OBSERVATION_DECISION_20260726T083800Z_001.json",
    "tools/verify_pass5_unit6_observation_sufficiency_decision_v1.py",
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
REPORTS = {
    "P5-U1": "audit/pass5/pass5-mount-registry-diagnostics-unit1-readiness-inventory-v1.json",
    "P5-U2": "audit/pass5/pass5-mount-registry-diagnostics-unit2-lifecycle-contract-v1.json",
    "P5-U3": "audit/pass5/pass5-mount-registry-diagnostics-unit3-passive-integration-v1.json",
    "P5-U4": "audit/pass5/pass5-mount-registry-diagnostics-unit4-readonly-view-v1.json",
    "P5-U5": "audit/pass5/pass5-mount-registry-unit5-isolated-transition-failure-proof-v1.json",
}


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

    decision = json.loads(DECISION.read_text())
    assert decision["base_main_commit"] == BASE
    assert decision["status"] == "PASS_DECISION"
    assert decision["decision"] == "NEW_CURRENT_PATH_OBSERVATION_NOT_REQUIRED"
    assert decision["roadmap_rule"] == {
        "unit": "P5-U6",
        "name": "Bounded current-path observation if authorized and required",
        "authorized": False,
        "required": False,
        "performed": False,
        "condition_result": "SKIPPED_BY_DESIGN_BECAUSE_NOT_REQUIRED",
    }
    assert len(decision["pass5_exit_criteria"]) == 4
    assert all(row["result"] == "PROVEN" for row in decision["pass5_exit_criteria"])
    assert decision["counterfactual_observation"]["new_claim_that_would_be_proven"] is None
    assert decision["counterfactual_observation"]["material_evidence_gain"] == "NONE"
    assert decision["counterfactual_observation"]["decision"] == "DO_NOT_RUN"
    assert decision["next_step"]["id"] == "P5-U7"
    assert decision["next_step"]["requires_user_app_check"] is False
    assert decision["next_step"]["requires_new_explicit_authority"] is False

    for field, value in decision["effects"].items():
        assert value is False, (field, value)
    assert decision["authority"]["special_authority_type"] == "NONE"
    assert decision["authority"]["special_authority_consumed"] is False
    assert decision["authority"]["new_live_authority_required"] is False
    assert decision["authority"]["retry_authorized"] is False
    assert decision["authority"]["consumed_observation_prs"] == [149, 150, 152]
    assert decision["authority"]["formal_proof_pr"] == 122

    reports = {unit: json.loads((ROOT / path).read_text()) for unit, path in REPORTS.items()}
    assert reports["P5-U1"]["status"] == "READINESS_AUDIT_PASS"
    assert reports["P5-U2"]["status"] == "PURE_CONTRACT_PROVEN_PENDING_MERGE"
    assert reports["P5-U3"]["status"] == "PASSIVE_INTEGRATION_PROVEN_PENDING_MERGE"
    assert reports["P5-U4"]["status"] == "READ_ONLY_DIAGNOSTICS_PROVEN_PENDING_MERGE"
    assert reports["P5-U5"]["status"] == "PASS_ISOLATED_PROOF"
    assert reports["P5-U5"]["coverage"]["assertions_total"] == 138
    assert reports["P5-U5"]["coverage"]["assertions_passed"] == 138
    assert reports["P5-U5"]["coverage"]["assertions_failed"] == 0
    assert sha(ROOT / REPORTS["P5-U5"]) == (
        decision["evidence"]["isolated"][-1]["proof_report_sha256"]
    )

    source_hashes = reports["P5-U5"]["components"]["source_sha256"]
    for rel, digest in source_hashes.items():
        assert sha(ROOT / rel) == digest, rel

    live = decision["evidence"]["live_current_path"]
    assert [(row["run"], row["conclusion"]) for row in live] == [
        (30193705682, "success"),
        (30194281350, "success"),
        (30194701694, "success"),
        (30194760893, "success"),
    ]
    assert live[0]["live_runtime_job"] == 89771368042
    assert live[1]["live_runtime_job"] == 89772885979
    assert live[2]["live_runtime_job"] == 89774026371
    assert live[3]["deploy_job"] == 89774227722

    changed_after_seal = set(filter(
        None,
        output("git", "diff", "--name-only", f"{P5_U4_SEALED_MAIN}...{BASE}").splitlines(),
    ))
    assert changed_after_seal == {
        ".github/workflows/pass5-unit5-isolated-lifecycle-proof-v1.yml",
        "audit/pass5/pass5-mount-registry-unit5-isolated-transition-failure-proof-v1.json",
        "audit/pass5/receipts/RECEIPT_P5_U5_ISOLATED_PROOF_20260726T082400Z_001.json",
        "tools/run_pass5_unit5_isolated_lifecycle_failure_proof_v1.js",
        "tools/verify_pass5_unit5_isolated_lifecycle_failure_proof_v1.py",
    }
    assert not changed_after_seal & PRODUCTION

    receipt = json.loads(RECEIPT.read_text())
    assert receipt["schema"] == "PMP_APP_ORCHESTRATOR_STEP_RECEIPT_V1"
    assert receipt["status"] == "PASS_BOUNDED"
    assert receipt["decision"] == "NEW_CURRENT_PATH_OBSERVATION_NOT_REQUIRED"
    assert receipt["scope"]["changed_paths"] == sorted(EXPECTED)
    assert receipt["verification"]["pass5_exit_criteria_proven"] == 4
    assert receipt["verification"]["p5_u5_assertions_passed"] == 138
    assert receipt["verification"]["production_source_changes_after_p5_u4_seal"] == 0
    assert receipt["effects"]["live_observation_performed"] is False
    assert receipt["effects"]["formal_proof_performed"] is False

    workflow = (
        ROOT / ".github/workflows/pass5-unit6-observation-sufficiency-decision-v1.yml"
    ).read_text()
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
    print("PASS: P5-U6 evidence proves a new current-path observation is not required")


if __name__ == "__main__":
    main()
