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
controller_contract = load("automation/controller/v1/controller-contract.json")
build_status = load("automation/state/controller-status.json")
controller = read("automation/controller/v1/controller.py")
workflow = read(".github/workflows/automated_plan_controller.yml")
ci = read(".github/workflows/automated_plan_controller_ci.yml")
room = read("pmp-automated-plan-room-v1.js")

need(state["active_plan_id"] == "packet_01_5", "active plan identity changed")
need(state["checkpoint"]["last_verified_unit"] == "pass_002", "Pass 002 checkpoint lost")
need(state["checkpoint"]["next_unit"] == "pass_003", "Pass 003 is no longer next")
need(state["execution_enabled"] is False, "execution was enabled")
need(state["execution"]["requested_action"] == "none", "a real action was requested")
need(state["execution"]["write_authority"] == "none", "state granted write authority")
need(state["execution"]["merge_authority"] == "none", "state granted merge authority")
need(plan["plan_status"] == "registered_not_compiled", "Pass 003 was compiled early")
need(plan["compiled_units"] == [], "real executable units were added")
need(plan["execution_enabled"] is False, "plan execution was enabled")

need(policy["version"] == "1.2.0", "controller policy version mismatch")
need(policy["cost_policy"]["spending_ceiling_usd"] == 0, "spending ceiling changed")
for name in ("paid_api_allowed", "paid_fallback_allowed", "automatic_cost_escalation_allowed"):
    need(policy["cost_policy"][name] is False, f"{name} must stay false")
need(policy["controller"]["implementation_status"] == "built_tested_execution_locked", "controller status is not locked")
need(policy["controller"]["one_work_unit_per_event"] is True, "one-unit rule missing")
need(policy["controller"]["first_real_run_requires_supervision"] is True, "supervised first run missing")
need(policy["controller"]["runtime_branch"] == "automation-runtime", "wrong runtime branch")
need(policy["controller"]["runtime_write_root"] == "automation/runtime", "wrong runtime write root")
need(policy["controller"]["github_models_endpoint"] == "https://models.github.ai/inference/chat/completions", "wrong Hosted Free endpoint")
need(policy["controller"]["hosted_model_job_repository_write"] is False, "model job can write")
need(policy["controller"]["persistence_job_model_access"] is False, "write job can access a model")
need(policy["controller"]["persistence_job_main_write"] is False, "controller can write main")

need(controller_contract["write_boundary"]["allowed_branch"] == "automation-runtime", "controller branch boundary changed")
need(controller_contract["write_boundary"]["allowed_paths"] == ["automation/runtime/**"], "controller path boundary changed")
need(controller_contract["write_boundary"]["main_direct_write_allowed"] is False, "main direct write allowed")
need(controller_contract["write_boundary"]["pull_request_merge_allowed"] is False, "merge allowed")
need(controller_contract["authority_split"]["inference_job"]["may_write_repository"] is False, "inference job can write")
need(controller_contract["authority_split"]["verification_job"]["may_write_repository"] is False, "verification job can write")
need(controller_contract["authority_split"]["persistence_job"]["models"] == "none", "persistence job has model access")
need(controller_contract["activation_boundary"]["execution_enabled"] is False, "controller activation boundary enabled")
need(controller_contract["activation_boundary"]["pass_003_started"] is False, "Pass 003 started")
need(controller_contract["activation_boundary"]["pass_003_compiled"] is False, "Pass 003 compiled")

need(build_status["controller_status"] == "built_tested_execution_locked", "room build status incorrect")
need(build_status["last_verified_main_before_build"] == "dc1c2dcbe35374532f581c62c3996648ad34e088", "verified base main changed")
need(build_status["next_unit"] == "pass_003" and build_status["next_unit_started"] is False, "room falsely reports Pass 003 progress")
need(build_status["execution_enabled"] is False, "room falsely reports execution enabled")
need(build_status["model_write_authority"] == "none" and build_status["model_merge_authority"] == "none", "room authority status widened")
need(build_status["spending_ceiling_usd"] == 0 and build_status["paid_fallback_allowed"] is False, "room cost status widened")

for token in (
    "https://models.github.ai/inference/chat/completions",
    "http://127.0.0.1:11434/api/chat",
    "one_work_unit_only",
    "proposal_only",
    "runtime_lock",
    "independent_rebuild_mismatch",
    "changed_file_outside_allowlist",
    "free_limit_reached",
    "pinned_main_sha",
):
    need(token in controller, f"controller missing safety token: {token}")
need("api.openai.com" not in controller, "paid OpenAI endpoint present")
need("subprocess.run(command" in controller and "shell=True" not in controller, "verification command boundary weakened")

need("workflow_dispatch:" in workflow, "manual event missing")
need("repository_dispatch:" in workflow, "resume event missing")
need("schedule:" in workflow, "scheduled resume event missing")
need("vars.PMP_AUTOMATION_ENABLED == 'true'" in workflow, "scheduled/repository resume is not activation-gated")
need("cancel-in-progress: false" in workflow, "concurrency may cancel a checkpointing run")
need("models: read" in workflow, "Hosted Free model permission missing")
need("contents: write" in workflow, "runtime persistence permission missing")
need("persist-credentials: false" in workflow, "read-only jobs retain credentials")
need("automation/runtime" in workflow and "automation-runtime" in workflow, "runtime-only persistence missing")
need("Write outside automation/runtime was blocked." in workflow, "runtime path enforcement missing")
need("git push origin \"HEAD:$RUNTIME_BRANCH\"" in workflow, "runtime branch push missing")
need("merge" not in workflow.lower(), "runtime workflow contains merge behavior")
need("pull-requests: write" not in workflow, "workflow can write pull requests")
need("OPENAI_API_KEY" not in workflow and "api.openai.com" not in workflow, "paid API path present in workflow")

# Permission split: the Hosted Free block must be read-only; the write block must not expose models.
hosted = workflow.split("  infer-hosted-free:", 1)[1].split("  infer-laptop:", 1)[0]
persist = workflow.split("  persist-runtime-only:", 1)[1]
verify = workflow.split("  verify:", 1)[1].split("  persist-runtime-only:", 1)[0]
need("contents: read" in hosted and "models: read" in hosted and "contents: write" not in hosted, "Hosted Free job can write")
need("contents: write" in persist and "models: read" not in persist and "GITHUB_TOKEN:" not in persist, "persistence job can access model credentials")
need("contents: read" in verify and "contents: write" not in verify and "models: read" not in verify, "verification job authority widened")
need("python3 automation/controller/v1/controller.py persist" in persist, "persistence does not use deterministic controller")
need("verification" not in persist.lower().replace("verified", ""), "persistence job appears to execute verification")

need("permissions:\n  contents: read" in ci, "controller CI is not read-only")
need("models: read" not in ci and "contents: write" not in ci, "controller CI has execution authority")
need("CONTROLLER_STATUS_URL" in room and "controller-status.json" in room, "Control Room does not read controller status")
need("packet_01_5" not in room and "Packet 01.5" not in room, "plan identity leaked into room source")

print(json.dumps({
    "type": "PMP_AUTOMATED_PLAN_CONTROLLER_VERIFICATION",
    "result": "PASS",
    "verified_main_before_build": build_status["last_verified_main_before_build"],
    "controller_status": build_status["controller_status"],
    "last_completed": "pass_002",
    "next_unit": "pass_003",
    "pass_003_started": False,
    "pass_003_compiled": False,
    "execution_enabled": False,
    "hosted_backend": "github_models_free",
    "laptop_backend": "local_ollama",
    "maximum_units_per_event": 1,
    "runtime_branch": "automation-runtime",
    "runtime_write_root": "automation/runtime",
    "model_write_authority": "none",
    "model_merge_authority": "none",
    "spending_ceiling_usd": 0
}, indent=2))
