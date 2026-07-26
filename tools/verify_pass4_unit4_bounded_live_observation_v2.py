#!/usr/bin/env python3
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "0bb3a42907ca1a2f864c1a40d1ace3f203cd7e45"
BRANCH = "agent/pass4-unit4-bounded-live-observation-v2"
WORKFLOW = ".github/workflows/pass4-unit4-bounded-live-observation-v2.yml"
AUTH = "audit/pass4/pass4-boot-status-strip-unit4-live-observation-authorization-v2.json"
DIRECTIVE = "audit/pass4/pass4-boot-status-strip-unit4-live-observation-directive-v2.json"
SEAL = "audit/pass4/pass4-boot-status-strip-unit4-live-observation-head-seal-v2.json"
RESULT = "audit/pass4/pass4-boot-status-strip-unit4-live-observation-result-v2.json"
FINALIZATION = "audit/pass4/pass4-boot-status-strip-unit4-live-observation-finalization-v2.json"
RUNNER = "tools/run_pass4_unit4_bounded_live_observation_v2.js"
TEST = "tools/test_pass4_unit4_bounded_live_observation_v2.js"
VERIFIER = "tools/verify_pass4_unit4_bounded_live_observation_v2.py"
HELPER = "tools/pass4_unit4_route_guardian_interaction_boundary_v1.js"
READINESS = "audit/pass4/pass4-boot-status-strip-unit4-route-guardian-interaction-repair-readiness-v1.json"
INITIAL = {WORKFLOW, AUTH, DIRECTIVE, SEAL, RESULT, RUNNER, TEST, VERIFIER}
FINAL = INITIAL | {FINALIZATION}
PROTECTED = {
    "pmp-route-guardian-current-loader-v22.html",
    "pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html",
    "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html",
    "pmp-boot-status-strip-owner-v1.js",
    "pmp-current-map-v12.json",
    "pmp-current-route-resolver-v1.js",
    "pmp-app-current.html",
    "pmp-app-orchestrator-v1.js",
    "pmp-runtime-integrity-manifest-v1.json",
    "audit/a003-manifest-seal.json",
}


def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def read_json(path):
    return json.loads((ROOT / path).read_text())


def sha256(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def git_blob(path):
    return output("git", "hash-object", path)


def changed(base, head="HEAD"):
    return set(filter(None, output("git", "diff", "--name-only", f"{base}...{head}").splitlines()))


def verify_bindings(seal):
    bindings = seal["bindings"]
    for path, identity in bindings.items():
        assert (ROOT / path).is_file(), path
        assert sha256(path) == identity["sha256"], path
        assert git_blob(path) == identity["git_blob_sha"], path


def verify_common_records():
    auth = read_json(AUTH)
    directive = read_json(DIRECTIVE)
    assert auth["status"] == "AUTHORIZED_UNCONSUMED"
    assert auth["authorized_base_main_commit"] == BASE
    assert auth["authorized_branch"] == BRANCH
    assert auth["observation_runs_authorized"] == 1
    assert auth["observation_runs_previously_executed_under_this_authorization"] == 0
    assert auth["authorization_consumed"] is False
    assert auth["formal_proof_authorized"] is False
    assert directive["status"] == "SEALED_STATIC_ONLY_UNCONSUMED"
    assert directive["authorized_base_main_commit"] == BASE
    assert directive["authorized_branch"] == BRANCH
    assert directive["authorized_event"] == "pull_request.opened"
    assert directive["authorized_observation_count"] == 1
    assert directive["previously_executed_count"] == 0
    assert directive["authorization_consumed"] is False
    assert directive["forbidden_pull_requests"] == [122, 149, 150]
    readiness = read_json(READINESS)
    assert readiness["status"] == "DETERMINISTIC_REPAIR_READY"
    assert readiness["live_observation_performed"] is False
    assert readiness["new_live_observation_authorized"] is False
    return auth, directive


def verify_source_safety():
    workflow = (ROOT / WORKFLOW).read_text()
    runner = (ROOT / RUNNER).read_text()
    helper = (ROOT / HELPER).read_text()
    assert "workflow_dispatch" not in workflow
    assert "reopened" not in workflow
    assert "github.event.action == 'opened'" in workflow
    assert "github.event.action == 'synchronize'" in workflow
    assert workflow.count("Consume exactly one authorized observation") == 1
    assert runner.count("chromium.launch(") == 1
    assert runner.count("page.goto(") == 1
    assert runner.count("activateInstalledRunButton(page)") == 1
    for forbidden in ("locator.click(", "force: true", "location.assign(", "location.replace(", ".src="):
        assert forbidden not in runner, forbidden
    assert "locator.evaluate" in helper
    assert "button.click()" in helper
    for forbidden in ("force: true", ".goto(", "location.assign(", "location.replace(", ".src=", "launch("):
        assert forbidden not in helper, forbidden


def verify_preflight():
    seal = read_json(SEAL)
    head = output("git", "rev-parse", "HEAD")
    parent = output("git", "rev-parse", "HEAD^")
    assert os.environ.get("BASE_SHA") == BASE
    assert os.environ.get("PR_HEAD_SHA") == head
    assert os.environ.get("PR_HEAD_REF") == BRANCH
    assert os.environ.get("EVENT_ACTION") == "opened"
    assert int(os.environ.get("PR_NUMBER", "0")) not in {122, 149, 150}
    assert seal["status"] == "SEALED_EXACT_FINAL_PREOBSERVATION_HEAD"
    assert seal["authorized_base_main_commit"] == BASE
    assert seal["authorized_branch"] == BRANCH
    assert seal["sealed_parent_commit"] == parent
    assert output("git", "rev-parse", f"{parent}^") == BASE
    assert output("git", "merge-base", BASE, head) == BASE
    assert output("git", "diff", "--name-only", parent, head).splitlines() == [SEAL]
    assert changed(BASE, head) == INITIAL
    assert not changed(BASE, head) & PROTECTED
    verify_bindings(seal)
    verify_common_records()
    verify_source_safety()
    result = read_json(RESULT)
    assert result["status"] == "AWAITING_AUTHORIZED_OBSERVATION"
    assert result["authorization_consumed"] is False
    assert result["observation_consumed"] is False
    assert result["observation_count"] == 0
    print("PASS: fresh authorization is unconsumed and bound to the exact base, branch, workflow, runner, helper, and sealed head")
    print("PASS: exact eight-file pre-observation scope and protected production boundary verified")


def verify_result(result):
    assert result["status"] in {"PASS", "FAIL_PRESERVED"}
    assert result["authorized_base_main_commit"] == BASE
    assert result["authorized_branch"] == BRANCH
    assert result["authorization_consumed"] is True
    assert result["observation_consumed"] is True
    assert result["observation_count"] == 1
    assert result["browser_launch_count"] == 1
    assert result["browser_navigation_count"] == 1
    assert result["production_runtime_changed"] is False
    assert result["runtime_integrity_changed"] is False
    assert result["persisted_user_data_changed"] is False
    assert result["unit5_started"] is False
    assert result["pass5_started"] is False
    assert result["formal_proof_run"] is False
    assert result["pr122_touched"] is False
    assert result["retry_authorized"] is False
    if result["status"] == "PASS":
        assert result["booting_observed"] is True
        assert result["ready_acknowledged_observed"] is True
        assert result["boot_status_strip_api_assigned"] is True
        assert result["app_orchestrator_acknowledged"] is True
        assert {
            "top",
            "route_guardian_v22",
            "reload_owner_v30",
            "current_inner_v30",
        } <= set(result["frame_roles_observed"])
        assert result["zero_effect_evidence"]["strip_declared_side_effects"] == {
            "routeAssignments": 0,
            "persistedUserDataWrites": 0,
            "appOrchestratorOwnershipTransfers": 0,
            "startupRepairs": 0,
        }


def verify_working_result(enforce_pass=False):
    verify_preflight()
    result = read_json(RESULT)
    verify_result(result)
    if enforce_pass:
        assert result["status"] == "PASS", result.get("failure_reason")
    print(f"PASS: exactly one consumed observation result is truthfully preserved as {result['status']}")


def commit_adding(path):
    return output("git", "log", "--diff-filter=A", "-1", "--format=%H", "--", path)


def commit_touching(path):
    return output("git", "log", "-1", "--format=%H", "--", path)


def verify_post_observation():
    head = output("git", "rev-parse", "HEAD")
    assert os.environ.get("BASE_SHA") == BASE
    assert os.environ.get("PR_HEAD_SHA") == head
    assert os.environ.get("PR_HEAD_REF") == BRANCH
    assert os.environ.get("EVENT_ACTION") == "synchronize"
    assert int(os.environ.get("PR_NUMBER", "0")) not in {122, 149, 150}
    paths = changed(BASE, head)
    assert paths in (INITIAL, FINAL), sorted(paths)
    assert not paths & PROTECTED
    seal_commit = commit_adding(SEAL)
    result_seed_commit = commit_adding(RESULT)
    result_commit = commit_touching(RESULT)
    assert result_commit != result_seed_commit
    assert output("git", "rev-parse", f"{result_commit}^") == seal_commit
    assert output("git", "diff", "--name-only", f"{result_commit}^", result_commit).splitlines() == [RESULT]
    result = read_json(RESULT)
    verify_result(result)
    if FINALIZATION in paths:
        assert head == commit_adding(FINALIZATION)
        assert output("git", "rev-parse", "HEAD^") == result_commit
        assert output("git", "diff", "--name-only", "HEAD^", "HEAD").splitlines() == [FINALIZATION]
        finalization = read_json(FINALIZATION)
        assert finalization["status"] == ("PASS_BOUNDED" if result["status"] == "PASS" else "FAIL_PRESERVED")
        assert finalization["authorized_base_main_commit"] == BASE
        assert finalization["sealed_preobservation_head_commit"] == seal_commit
        assert finalization["observation_result_commit"] == result_commit
        assert finalization["observation_status"] == result["status"]
        assert finalization["observation_count"] == 1
        assert finalization["retry_authorized"] is False
    print(f"PASS: immutable exactly-once commit chain and {result['status']} result verified")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "preflight":
        verify_preflight()
    elif mode == "working-result":
        verify_working_result(False)
    elif mode == "enforce-pass":
        verify_working_result(True)
    elif mode == "post-observation":
        verify_post_observation()
    else:
        raise SystemExit("usage: verifier preflight|working-result|enforce-pass|post-observation")


if __name__ == "__main__":
    main()
