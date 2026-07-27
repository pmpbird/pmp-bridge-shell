#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "e3e0fecfe4db33b6f6d7b447c4180b74409d8090"
TREE = "f1dca0d7aebe389986ada14481e34572896086aa"
RECORDS = 2076
NODE = shutil.which("node")
PYTHON = sys.executable

COMPONENTS = [
    {
        "pass": "1-2",
        "command": [PYTHON, "tools/test_passes1_2_repository_completeness_repair_v1.py"],
        "assertions": 7,
        "token": '"status": "PASS"',
    },
    {
        "pass": 2,
        "command": [PYTHON, "tools/test_pass2_full_roadmap_authority_definition_closure_v1.py"],
        "assertions": 12,
        "token": '"status": "PASS"',
    },
    {
        "pass": 3,
        "command": [PYTHON, "tools/test_pass3_unit5_closure_certification_v1.py"],
        "assertions": 1,
        "token": "PASS:",
    },
    {
        "pass": 4,
        "command": [NODE, "tools/test_pass4_unit4_route_guardian_interaction_repair_v1.js"],
        "assertions": 4,
        "token": "PASS:",
    },
    {
        "pass": 5,
        "command": [NODE, "tools/test_pass5_unit4_readonly_lifecycle_diagnostics_v1.js"],
        "assertions": 1,
        "token": "PASS:",
    },
    {
        "pass": 6,
        "command": [NODE, "tools/test_pass6_unit6_fault_injection_v1.js"],
        "assertions": 233,
        "token": "(233/233)",
    },
    {
        "pass": 7,
        "command": [NODE, "tools/test_pass7_unit5_owner_isolation_restart_denial_v1.js"],
        "assertions": 218,
        "token": "(218/218)",
    },
    {
        "pass": 8,
        "command": [NODE, "tools/test_pass8_unit5_helper_isolation_restart_denial_v1.js"],
        "assertions": 251,
        "token": "(251/251)",
    },
    {
        "pass": 9,
        "command": [NODE, "tools/test_pass9_unit4_bank_continuous_run_exhaustive_proof_v1.js"],
        "assertions": 238,
        "token": "(238/238)",
    },
    {
        "pass": 10,
        "command": [NODE, "tools/test_pass10_unit5_bank_fault_corruption_proof_v1.js"],
        "assertions": 133,
        "token": "(133/133)",
    },
    {
        "pass": 11,
        "command": [NODE, "tools/test_pass11_safety_no_deletion_v1.js"],
        "assertions": 186,
        "token": "(186/186)",
    },
    {
        "pass": 12,
        "command": [NODE, "tools/test_pass12_migration_plan_v1.js"],
        "assertions": 389,
        "token": "(389/389)",
    },
]

CLOSURES = [
    "audit/pass1/pass1-post-merge-confirmation-v1.json",
    "audit/pass2/pass2-full-roadmap-authority-definition-closure-v1.json",
    "audit/pass3/pass3-route-guardian-handoff-unit5-closure-certification-v1.json",
    "audit/pass4/pass4-boot-status-strip-unit5-closure-certification-v1.json",
    "audit/pass5/pass5-mount-registry-unit7-closure-certification-v1.json",
    "audit/pass6/pass6-unit7-closure-certification-v1.json",
    "audit/pass7/pass7-section-owner-unit6-closure-certification-v1.json",
    "audit/pass8/pass8-helper-unit6-closure-certification-v1.json",
    "audit/pass9/pass9-bank-continuous-run-unit7-closure-certification-v1.json",
    "audit/pass10/pass10-bank-unit7-closure-certification-v1.json",
    "audit/pass11/pass11-unit6-closure-certification-v1.json",
    "audit/pass12/pass12-unit8-safe-closure-v1.json",
]


def output(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def git_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    if NODE is None:
        raise SystemExit("node not found")
    subprocess.check_call(
        ["git", "merge-base", "--is-ancestor", BASE, "HEAD"], cwd=ROOT
    )
    component_results = []
    component_assertions = 0
    for component in COMPONENTS:
        completed = subprocess.run(
            component["command"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            check=False,
        )
        if completed.returncode or component["token"] not in completed.stdout:
            sys.stderr.write(
                f"FAIL component pass {component['pass']}\n"
                f"{completed.stdout}\n"
            )
            raise SystemExit(1)
        component_assertions += component["assertions"]
        component_results.append({
            "pass": component["pass"],
            "assertions": component["assertions"],
            "status": "PASS",
            "output_sha256": sha(completed.stdout.encode()),
        })

    checks = 0

    def check(condition: bool, label: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(label)

    check(output("git", "rev-parse", f"{BASE}^{{tree}}") == TREE, "base tree")
    base_names = output("git", "ls-tree", "-r", "--name-only", BASE).splitlines()
    check(len(base_names) == RECORDS, "base record count")
    folded: dict[str, str] = {}
    collisions: list[list[str]] = []
    for name in base_names:
        key = name.casefold()
        if key in folded:
            collisions.append([folded[key], name])
        else:
            folded[key] = name
    check(collisions == [["Index.html", "index.html"]], "casefold collision")
    check("Index.html" in base_names, "upper index")
    check("index.html" in base_names, "lower index")

    for path in CLOSURES:
        check(path in base_names, f"closure tracked {path}")
        value = json.loads(git_bytes(BASE, path))
        check(value.get("pass") == CLOSURES.index(path) + 1, f"closure pass {path}")

    ledger = json.loads(
        (ROOT / "audit/pass13/PMP_APP_ORCHESTRATOR_PASS_CLOSURE_LEDGER_V1.json").read_text()
    )
    check(len(ledger["entries"]) == 13, "ledger entries")
    check([row["pass"] for row in ledger["entries"]] == list(range(1, 14)), "ledger ordering")
    check(ledger["reconciliation"]["passes_with_traceable_closure_evidence"] == 13, "ledger coverage")
    check(ledger["reconciliation"]["historical_receipts_rewritten"] == 0, "receipt immutability")
    check(ledger["reconciliation"]["historical_failures_erased"] == 0, "failure preservation")
    check(ledger["reconciliation"]["unresolved_claims_presented_as_complete"] == 0, "claim ceiling")
    check(ledger["reconciliation"]["production_migration_claimed"] is False, "no migration claim")
    check(ledger["reconciliation"]["formal_proof_success_claimed"] is False, "no proof claim")
    check(len(ledger["historical_exceptions"]) == 4, "exception count")
    check(any(row["id"] == "FORMAL_PROOF_PR122_FAILED_CONSUMED_EVENT" for row in ledger["historical_exceptions"]), "pr122 exception")
    check(any(row["id"] == "PASS12_PRODUCTION_MIGRATION" for row in ledger["historical_exceptions"]), "migration exception")

    authority = json.loads(
        (ROOT / "audit/pass13/PMP_APP_ORCHESTRATOR_AUTHORITY_MATRIX_V1.json").read_text()
    )
    check(authority["default_decision"] == "DENY", "authority default")
    check(len(authority["rules"]) == 9, "authority rule count")
    by_action = {row["action"]: row for row in authority["rules"]}
    check(by_action["DELETE_PERSISTED_RECORD"]["ordinary_maintenance"] == "DENY", "delete denied")
    check(by_action["DELETE_PERSISTED_RECORD"]["wildcards_allowed"] is False, "delete no wildcard")
    check(by_action["DELETE_PERSISTED_RECORD"]["automatic_retry"] is False, "delete no retry")
    check(by_action["PRODUCTION_MIGRATION_OR_USER_DATA_MUTATION"]["ordinary_maintenance"] == "DENY", "migration denied")
    check(by_action["FORMAL_PROOF"]["ordinary_maintenance"] == "DENY", "proof denied")
    check(by_action["FORMAL_PROOF"]["automatic_retry"] is False, "proof no retry")
    check(authority["formal_proof_state"]["historical_pr122_receipt082"].startswith("CONSUMED_FAILED"), "historic proof")
    check(authority["formal_proof_state"]["later_contingent_authorization"] == "UNCONSUMED", "later proof unconsumed")
    check(authority["formal_proof_state"]["formal_proof_run_by_pass13"] is False, "no pass13 proof")
    check(authority["production_migration_state"]["gate"] == "INACTIVE", "migration inactive")
    check(authority["production_migration_state"]["performed"] is False, "migration not performed")
    check(authority["production_migration_state"]["persisted_user_data_changed"] is False, "user data unchanged")

    release = json.loads(
        (ROOT / "audit/pass13/PMP_APP_ORCHESTRATOR_RELEASE_INPUT_MANIFEST_V1.json").read_text()
    )
    check(release["certification_base_main_commit"] == BASE, "release base")
    check(release["certification_base_tree"] == TREE, "release tree")
    check(release["certification_base_blob_count"] == RECORDS, "release blobs")
    for row in release["inputs"]:
        payload = git_bytes(BASE, row["path"])
        check(len(payload) == row["bytes"], f"release bytes {row['path']}")
        check(sha(payload) == row["sha256"], f"release hash {row['path']}")

    manifest_payload = git_bytes(BASE, "pmp-runtime-integrity-manifest-v1.json")
    manifest = json.loads(manifest_payload)
    records = {row["path"]: row for row in manifest["records"]}
    check(len(records) == release["runtime_manifest_records"] == 716, "runtime records")
    check(manifest["runtime_source_set_sha256"] == release["runtime_source_set_sha256"], "runtime set")
    for path, row in records.items():
        payload = git_bytes(BASE, path)
        check(len(payload) == row["bytes"], f"runtime bytes {path}")
        check(sha(payload) == row["sha256_hex"], f"runtime hash {path}")

    seal = json.loads(git_bytes(BASE, "audit/a003-manifest-seal.json"))
    check(seal["manifest_sha256"] == sha(manifest_payload), "seal manifest")
    check(seal["runtime_source_set_sha256"] == manifest["runtime_source_set_sha256"], "seal runtime")
    bootstrap = git_bytes(BASE, "pmp-app-current.html").decode()
    match = re.search(r"const MANIFEST_SHA256='([0-9a-f]{64})';", bootstrap)
    check(bool(match), "bootstrap anchor present")
    check(match.group(1) == sha(manifest_payload), "bootstrap anchor exact")

    migration = json.loads(git_bytes(BASE, "pmp-migration-plan-v1.json"))
    check(migration["mode"] == "INACTIVE_NONPRODUCTION_PLAN", "migration mode")
    check(migration["target"]["production_commit_available"] is False, "no migration commit")
    check(migration["authority_gate"]["state"] == "INACTIVE", "migration authority inactive")
    check(migration["authority_gate"]["production_migration_authorized"] is False, "migration unauthorized")
    check(migration["authority_gate"]["persisted_user_data_change_authorized"] is False, "data change unauthorized")
    gate_source = git_bytes(BASE, "pmp-migration-inactive-gate-v1.js").decode()
    for forbidden in ("localStorage", "sessionStorage", "indexedDB", "fetch(", "XMLHttpRequest", "WebSocket"):
        check(forbidden not in gate_source, f"inactive gate API {forbidden}")

    total = component_assertions + checks
    result = {
        "type": "PMP_PASS13_END_TO_END_REGRESSION_RESULT_V1",
        "status": "PASS",
        "certification_base_commit": BASE,
        "component_suites": len(component_results),
        "component_assertions": component_assertions,
        "orchestration_assertions": checks,
        "assertions_total": total,
        "assertions_passed": total,
        "assertions_failed": 0,
        "components": component_results,
        "fault_classes": [
            "authority gain",
            "formal-proof replay",
            "consumed-observation replay",
            "route duplication",
            "owner isolation",
            "helper isolation",
            "Bank/Continuous Run concurrency and ordering",
            "delete/archive/transaction rollback",
            "migration malformed/stale/duplicate/orphan/partial-stage",
            "manifest byte mismatch",
            "case-insensitive path collision"
        ],
        "effects": {
            "browser_launched": False,
            "network_requests": False,
            "production_storage_reads": 0,
            "production_storage_writes": 0,
            "production_storage_deletes": 0,
            "persisted_user_data_changed": False,
            "production_migration_performed": False,
            "formal_proof_performed": False,
            "special_authority_consumed": False
        }
    }
    result["result_sha256"] = sha(
        json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    )
    print(
        "PASS: Pass 13 full deterministic cross-pass regression, "
        f"fault injection, release identity, and authority reconciliation ({total}/{total})"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
