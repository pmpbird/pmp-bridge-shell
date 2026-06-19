#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SAFE_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")
FORBIDDEN_PAID_ENV = (
    "OPENAI_API_KEY", "AZURE_OPENAI_API_KEY", "AZURE_AI_API_KEY",
    "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY",
    "COHERE_API_KEY", "MISTRAL_API_KEY",
)
STOP_GATES = [
    "execution_disabled", "paid_api_detected", "paid_fallback_detected",
    "spending_ceiling_above_zero", "unsafe_write_authority", "merge_authority_detected",
    "unclear_user_instruction", "authoritative_main_changed", "checkpoint_mismatch",
    "deterministic_verification_failed", "independent_rebuild_mismatch", "manual_stop_requested",
]


class QueueStop(RuntimeError):
    def __init__(self, reason: str, message: str):
        super().__init__(message)
        self.reason = reason


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise QueueStop("schema_invalid", f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise QueueStop("schema_invalid", f"invalid JSON file: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise QueueStop("schema_invalid", f"JSON object required: {path}")
    return value


def reject_paid_environment() -> None:
    present = [name for name in FORBIDDEN_PAID_ENV if os.environ.get(name)]
    if present:
        raise QueueStop("paid_api_detected", "paid-provider credential detected: " + ", ".join(present))


def safe_id(raw: str, label: str) -> str:
    if not isinstance(raw, str) or not SAFE_ID_RE.fullmatch(raw):
        raise QueueStop("schema_invalid", f"unsafe {label}: {raw!r}")
    return raw


def hard_free_gates(definition_root: Path) -> dict[str, Any]:
    state = load_json(definition_root / "automation/state/active-plan.json")
    policy = load_json(definition_root / "automation/engine/v1/engine-policy.json")
    engine = load_json(definition_root / "automation/state/free-in-app-engine-status.json")
    cost = policy.get("cost_policy", {})
    execution = state.get("execution", {})
    reject_paid_environment()
    if cost.get("spending_ceiling_usd") != 0 or engine.get("spending_ceiling_usd") != 0:
        raise QueueStop("spending_ceiling_above_zero", "spending ceiling must remain $0")
    for key in ("paid_api_allowed", "paid_fallback_allowed", "automatic_cost_escalation_allowed"):
        if cost.get(key) is not False:
            raise QueueStop("paid_api_detected", f"policy {key} must be false")
    if engine.get("paid_api_allowed") is not False or engine.get("paid_fallback_allowed") is not False:
        raise QueueStop("paid_api_detected", "engine status permits paid path")
    if execution.get("write_authority") != "none" or engine.get("write_authority") != "none":
        raise QueueStop("unsafe_write_authority", "write authority must remain none before execution enablement")
    if execution.get("merge_authority") != "none" or engine.get("merge_authority") != "none":
        raise QueueStop("merge_authority_detected", "merge authority must remain none")
    return {"state": state, "policy": policy, "engine": engine}


def compile_command(args: argparse.Namespace) -> int:
    definition_root = args.definition_root.resolve()
    bundle = hard_free_gates(definition_root)
    command = (args.command or "").strip()
    if not command:
        raise QueueStop("unclear_user_instruction", "empty command cannot be compiled")
    if len(command) > 2000:
        raise QueueStop("unclear_user_instruction", "command is too large for the free in-app compiler")
    if re.search(r"\b(paid|billing|api key|merge now|force push|delete repo|secret)\b", command, re.I):
        raise QueueStop("unclear_user_instruction", "command contains a blocked paid/unsafe/secret term")
    next_unit = bundle["state"].get("checkpoint", {}).get("next_unit") or "pass_003"
    queue = {
        "type": "PMP_FREE_IN_APP_ENGINE_QUEUE_DRAFT",
        "schema_id": "pmp.automated-plan.free-in-app-queue.v1",
        "schema_version": "1.0.0",
        "status": "draft_not_started",
        "execution_enabled": False,
        "start_requested": False,
        "user_command": command,
        "resume_from": next_unit,
        "queue": [
            {"unit_id": "intake_review", "objective": "Normalize the user instruction and confirm it is free-path safe."},
            {"unit_id": "source_scope", "objective": "Find the smallest relevant app/source scope without changing files."},
            {"unit_id": "compile_units", "objective": "Convert the request into executable units with evidence paths and output allowlists."},
            {"unit_id": "queued_execution_ready", "objective": "Prepare the queue for the existing verified-unit controller without starting it."},
            {"unit_id": "user_enablement_gate", "objective": "Stop until the user explicitly enables execution and free gates pass."}
        ],
        "hard_stop_gates": STOP_GATES,
        "authority": {
            "model_output_authority": "proposal_only",
            "write_authority": "none",
            "merge_authority": "none",
            "paid_api_allowed": False,
            "paid_fallback_allowed": False,
            "spending_ceiling_usd": 0
        }
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": "PASS", "phase": "compile_command", "status": "draft_not_started", "execution_started": False, "out": str(args.out)}, indent=2))
    return 0


def validate_only(args: argparse.Namespace) -> int:
    bundle = hard_free_gates(args.definition_root.resolve())
    print(json.dumps({
        "result": "PASS",
        "phase": "validate_only",
        "engine_status": bundle["engine"].get("engine_status"),
        "execution_enabled": bundle["state"].get("execution_enabled"),
        "requested_action": bundle["state"].get("execution", {}).get("requested_action"),
        "next_unit": bundle["state"].get("checkpoint", {}).get("next_unit"),
        "queue_execution_started": False
    }, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="PMP free in-app queued engine scaffold")
    sub = parser.add_subparsers(dest="command_name", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--definition-root", type=Path, required=True)
    validate = sub.add_parser("validate-only", parents=[common])
    validate.set_defaults(func=validate_only)
    compile_p = sub.add_parser("compile-command", parents=[common])
    compile_p.add_argument("--command", required=True)
    compile_p.add_argument("--out", type=Path, required=True)
    compile_p.set_defaults(func=compile_command)
    args = parser.parse_args()
    try:
        return args.func(args)
    except QueueStop as exc:
        print(json.dumps({"result": "STOP", "reason": exc.reason, "message": str(exc), "execution_started": False}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
