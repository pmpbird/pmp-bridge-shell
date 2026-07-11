#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def read(path: str):
    return (ROOT / path).read_text(encoding="utf-8")


def require(condition: bool, message: str):
    if not condition:
        raise SystemExit(message)


def main() -> None:
    policy = load("automation/engine/v1/engine-policy.json")
    plan = load("automation/plans/packet-01-5.v1.json")
    state = load("automation/state/active-plan.json")
    room = read("pmp-automated-plan-room-v1.js")
    native_match = read("pmp-automated-plan-native-match-v1.js")
    legacy_wrapper = read("pmp-current-inner-cleanbug-rgcontrols-v6.html")
    current_map = load("pmp-current-map-v12.json")

    # Preserve the original non-executable foundation contract.
    require(policy["user_facing_entry_label"] == "Automated Plan", "historical foundation entry identity changed")
    require(policy["cost_policy"]["spending_ceiling_usd"] == 0, "spending ceiling must be zero")
    require(policy["cost_policy"]["paid_api_allowed"] is False, "paid API must be forbidden")
    require(policy["cost_policy"]["paid_fallback_allowed"] is False, "paid fallback must be forbidden")
    require({b["backend_id"] for b in policy["execution_backends"]} == {"github_models_free", "local_ollama"}, "backend set changed")
    require(policy["backend_switching"]["redesign_required"] is False, "backend switch must not require redesign")
    require(policy["interface"]["inherit_global_theme"] is True, "theme inheritance required")
    require(policy["interface"]["inherit_global_contrast"] is True, "contrast inheritance required")

    require(plan["plan_id"] == "packet_01_5", "registered plan identity changed")
    require(plan["execution_enabled"] is False, "plan must remain disabled")
    require(plan["last_completed_boundary"] == "pass_002", "last completed boundary changed")
    require(plan["next_declared_boundary"] == "pass_003", "next boundary changed")
    require(plan["compiled_units"] == [], "foundation must not invent executable units")

    require(state["active_plan_id"] == plan["plan_id"], "state/plan identity mismatch")
    require(state["execution_enabled"] is False, "state must remain disabled")
    require(state["checkpoint"]["last_completed_boundary"] == "pass_002", "checkpoint lost Pass 002")
    require(state["checkpoint"]["next_unit"] == "pass_003", "checkpoint lost next unit")
    require(state["execution"]["spending_ceiling_usd"] == 0, "state spending ceiling must be zero")
    require(state["execution"]["paid_fallback_allowed"] is False, "state paid fallback must be false")

    # Formal retirement truth: the old Automated Plan UI route was superseded.
    require("Continuous Run Dashboard" in room, "superseding Continuous Run Dashboard owner missing")
    require("pmpAutomatedPlanEntryV1" in room, "shared historical entry anchor missing")
    require("Continuous Run Dashboard" in native_match, "native matcher is not aligned to the superseding owner")
    require("pmp-automated-plan-room-v1.js" in legacy_wrapper, "legacy v6 wrapper no longer preserves the historical room loader")
    require(current_map["app_version"] == "PMP-CURRENT-1-A003", "current map is not the certified A-003 contract")
    require(current_map["route_contract"]["runtime_integrity_required"] is True, "A-003 integrity is not required")
    require(current_map["current_app"]["path"] == "pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html", "unexpected current app authority")
    runtime_paths = {item["path"] for item in current_map["runtime_chain"].values() if isinstance(item, dict) and "path" in item}
    require("pmp-current-inner-cleanbug-rgcontrols-v6.html" not in runtime_paths, "retired v6 wrapper incorrectly remains in the current runtime chain")

    prohibited = ["OPENAI_API_KEY", "api.openai.com", 'paid_fallback_allowed\": true', 'spending_ceiling_usd\": 1']
    combined = "\n".join(read(p) for p in [
        "automation/engine/v1/engine-policy.json",
        "automation/plans/packet-01-5.v1.json",
        "automation/state/active-plan.json",
        "pmp-automated-plan-room-v1.js",
        "pmp-automated-plan-native-match-v1.js",
        "pmp-current-inner-cleanbug-rgcontrols-v6.html",
    ])
    for token in prohibited:
        require(token not in combined, f"prohibited paid-path token found: {token}")

    print(json.dumps({
        "type": "PMP_AUTOMATED_PLAN_FOUNDATION_RETIREMENT_VERIFICATION_V1",
        "result": "PASS",
        "historical_foundation_preserved": True,
        "historical_entry_label": "Automated Plan",
        "superseding_ui_owner": "Continuous Run Dashboard",
        "legacy_wrapper": "pmp-current-inner-cleanbug-rgcontrols-v6.html",
        "legacy_wrapper_current_authority": False,
        "current_app": current_map["current_app"]["path"],
        "runtime_integrity_required": True,
        "active_plan_id": state["active_plan_id"],
        "execution_enabled": False,
        "last_completed_boundary": "pass_002",
        "next_unit": "pass_003",
        "spending_ceiling_usd": 0,
        "paid_fallback_allowed": False,
        "backends": ["github_models_free", "local_ollama"],
        "pass_003_started": False,
        "retirement_truth": "The old Automated Plan v6 UI assertion is retired; its non-executable zero-cost contract remains preserved."
    }, indent=2))


if __name__ == "__main__":
    main()
