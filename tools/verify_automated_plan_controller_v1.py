#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((R / path).read_text(encoding="utf-8"))


def read(path: str):
    return (R / path).read_text(encoding="utf-8")


def need(condition, message):
    if not condition:
        raise SystemExit(message)


policy = load("automation/engine/v1/engine-policy.json")
plan = load("automation/plans/packet-01-5.v1.json")
state = load("automation/state/active-plan.json")
contract = load("automation/controller/v1/controller-contract.json")
status = load("automation/state/controller-status.json")
controller = read("automation/controller/v1/controller.py")
workflow = read(".github/workflows/automated_plan_controller.yml")
ci = read(".github/workflows/automated_plan_controller_ci.yml")
room = read("pmp-automated-plan-room-v1.js")

need(state["checkpoint"]["last_verified_unit"] == "pass_002", "Pass 002 checkpoint lost")
need(state["checkpoint"]["next_unit"] == "pass_003", "Pass 003 is no longer next")
need(state["execution_enabled"] is False, "execution was enabled")
need(state["execution"]["requested_action"] == "none", "a real action was requested")
need(plan["plan_status"] == "registered_not_compiled", "plan status widened")
need(plan["compiled_units"] == [], "Pass 003 was compiled")
need(plan["execution_enabled"] is False, "plan execution was enabled")

need(policy["version"] == "1.3.0", "hardened policy version mismatch")
need(policy["cost_policy"]["assurance_status"] == "unverified_hosted_execution_blocked", "unverified zero-cost state missing")
need(policy["cost_policy"]["hosted_paid_usage_account_setting_must_be_disabled"] is True, "account billing gate missing")
need(policy["authority"]["container_isolation_required"] is True, "container isolation policy missing")
need(policy["controller"]["persistence_reconstructs_checkpoint"] is True, "persistence reconstruction policy missing")
need(policy["controller"]["persistence_trusts_runtime_candidate"] is False, "runtime candidate trust remains")

need(contract["version"] == "1.1.0", "controller contract version mismatch")
need(contract["billing_gate"]["hosted_inference_requires_account_level_paid_usage_disabled"] is True, "hosted billing requirement absent")
need(contract["billing_gate"]["unverified_behavior"] == "block_hosted_inference_and_do_not_claim_zero_cost", "billing fail-closed rule absent")
need(contract["verification_sandbox"]["network"] == "none", "sandbox network is not disabled")
need(contract["verification_sandbox"]["root_filesystem"] == "read_only", "sandbox root is not read-only")
need(contract["verification_sandbox"]["capabilities"] == "drop_all", "sandbox capabilities not dropped")
need(contract["authority_split"]["persistence_job"]["must_reconstruct_checkpoint_independently"] is True, "persistence reconstruction contract absent")
need(contract["write_boundary"]["persistence_accepts_runtime_candidate_from_verifier"] is False, "runtime candidate remains accepted")
need(contract["activation_boundary"]["execution_enabled"] is False, "activation boundary enabled")
need(contract["activation_boundary"]["pass_003_started"] is False, "Pass 003 started")
need(contract["activation_boundary"]["pass_003_compiled"] is False, "Pass 003 compiled")
need(contract["activation_boundary"]["hosted_billing_gate_verified"] is False, "billing gate falsely marked verified")

for token in (
    "paid_usage_setting_unverified",
    "require_hosted_billing_gate",
    "--network", "none", "--read-only", "--pids-limit", "--cap-drop", "ALL",
    "reconstruct_candidate", "ensure_exact_keys", "checkpoint_jump_detected",
    "pmp.automated-plan.verified-result.v2",
):
    need(token in controller, f"controller missing hardening token: {token}")
need('"runtime_candidate"' not in controller, "controller still serializes or accepts runtime_candidate")
need("shell=True" not in controller, "host shell execution enabled")
need("api.openai.com" not in controller, "paid OpenAI endpoint present")

for variable in (
    "PMP_GITHUB_MODELS_PAID_USAGE_DISABLED",
    "PMP_GITHUB_MODELS_BILLING_SCOPE",
    "PMP_GITHUB_MODELS_BILLING_VERIFIED_AT",
):
    need(variable in workflow, f"workflow missing billing variable {variable}")
need("docker pull python:3.13-slim" in workflow, "container verifier image is not prepared")
need("Independently reconstruct and persist exact transition" in workflow, "persistence reconstruction step missing")
need("--decision /tmp/pmp-controller-prepare/decision.json" in workflow, "persistence lacks trusted decision input")
need("pull-requests: write" not in workflow and "merge" not in workflow.lower(), "workflow gained PR or merge authority")

need(status["controller_status"] == "hardened_tested_execution_locked", "controller build status not hardened/locked")
need(status["zero_cost_assurance"] == "unverified", "status falsely claims verified zero cost")
need(status["hosted_execution_blocked_until_account_paid_usage_disabled"] is True, "status does not show hosted block")
need(status["next_unit"] == "pass_003" and status["next_unit_started"] is False, "Pass 003 status widened")
need("Zero-cost assurance" in room, "room does not expose assurance state")
need("$0 additional API usage" not in room, "room still makes unconditional $0 claim")
need("unverified" in room.lower(), "room does not state unverified assurance")

need("test_automated_plan_controller_container_v1.py" in ci, "container adversarial tests absent from CI")
need("test_automated_plan_controller_workflow_v1.py" in ci, "non-executing workflow test absent from CI")
need("contents: write" not in ci and "models: read" not in ci, "CI has execution authority")

legacy = {
    ".github/workflows/packet_015_pass_002_dependency_platform_family.yml": "Pass_002_Dependency_Platform_Family",
    ".github/workflows/packet_015_pass_002_other_record_specific_proof_family.yml": "Pass_002_Other_Record_Specific_Proof_Family",
    ".github/workflows/packet_015_pass_002_private_uncaptured_family.yml": "Pass_002_Private_Uncaptured_Family",
    ".github/workflows/packet_015_scalable_pass_002.yml": "Scalable_Pass_002",
    ".github/workflows/packet_015_pass_002_deployment_live_family.yml": "Pass_002_Deployment_Live_Family",
    ".github/workflows/packet_015_master_consolidation_v2.yml": "Master_",
    ".github/workflows/packet_015_pass_002_current_runtime_family.yml": "Pass_002_Current_Runtime",
    ".github/workflows/packet_015_pass_002_authoritative_packet_law_family.yml": "Pass_002_Authoritative_Packet_Law_Family",
    ".github/workflows/packet_01_5_pass_002_closure.yml": "Pass_002_Closure",
    ".github/workflows/packet_015_pass_002_cross_source_conflict_family.yml": "Pass_002_Cross_Source_Conflict_Family",
}
for path, marker in legacy.items():
    text = read(path)
    need("pull_request:\n    paths:" in text, f"legacy workflow remains unscoped: {path}")
    need(marker in text, f"legacy workflow scope marker missing: {path}")
    need("automation/**" not in text and "pmp-automated-plan" not in text, f"legacy workflow overlaps controller scope: {path}")
    need(path not in text, f"legacy workflow self-trigger remains: {path}")

print(json.dumps({
    "result": "PASS",
    "controller_version": "1.1.0",
    "billing_assurance": "unverified_hosted_execution_blocked",
    "container_isolation": "network_none_read_only_root_process_limited",
    "persistence": "independent_exact_transition_reconstruction",
    "legacy_workflows_scoped": len(legacy),
    "last_verified_unit": "pass_002",
    "next_unit": "pass_003",
    "pass_003_started": False,
    "execution_enabled": False,
}, indent=2))
