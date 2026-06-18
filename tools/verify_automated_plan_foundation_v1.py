#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def require(condition: bool, message: str):
    if not condition:
        raise SystemExit(message)

def main() -> None:
    policy = load("automation/engine/v1/engine-policy.json")
    plan = load("automation/plans/packet-01-5.v1.json")
    state = load("automation/state/active-plan.json")
    room = (ROOT / "pmp-automated-plan-room-v1.js").read_text(encoding="utf-8")
    wrapper = (ROOT / "pmp-current-inner-cleanbug-rgcontrols-v6.html").read_text(encoding="utf-8")
    current_map = load("pmp-current-map-v9.json")

    require(policy["user_facing_entry_label"] == "Automated Plan", "wrong universal entry label")
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

    require("const MAIN_LABEL='Automated Plan'" in room, "room label missing")
    require("pmpAutomatedPlanEntryV1" in room and "pmpAutomatedPlanOverlayV1" in room, "entry or room missing")
    require("var(--floor" in room and "var(--card" in room and "var(--line" in room and "var(--a" in room, "room does not inherit app variables")
    require("pmp-current-inner-cleanbug-rgcontrols-v4.html" in wrapper, "v6 must wrap current v4")
    require("pmp-automated-plan-room-v1.js" in wrapper, "v6 must load Automated Plan room")
    require(current_map["current_app"]["path"] == "pmp-current-inner-cleanbug-rgcontrols-v6.html", "current map does not point to v6")
    require(current_map["fallback_app"]["path"] == "pmp-current-inner-cleanbug-rgcontrols-v6.html", "fallback map does not point to v6")

    prohibited = ["OPENAI_API_KEY", "api.openai.com", "paid_fallback_allowed\": true", "spending_ceiling_usd\": 1"]
    combined = "\n".join((ROOT / p).read_text(encoding="utf-8") for p in [
        "automation/engine/v1/engine-policy.json",
        "automation/plans/packet-01-5.v1.json",
        "automation/state/active-plan.json",
        "pmp-automated-plan-room-v1.js",
        "pmp-current-inner-cleanbug-rgcontrols-v6.html",
    ])
    for token in prohibited:
        require(token not in combined, f"prohibited paid-path token found: {token}")

    print(json.dumps({
        "type": "PMP_AUTOMATED_PLAN_FOUNDATION_VERIFICATION",
        "result": "PASS",
        "entry_label": "Automated Plan",
        "active_plan_id": state["active_plan_id"],
        "execution_enabled": False,
        "last_completed_boundary": "pass_002",
        "next_unit": "pass_003",
        "spending_ceiling_usd": 0,
        "paid_fallback_allowed": False,
        "backends": ["github_models_free", "local_ollama"],
        "theme_inheritance": True,
        "pass_003_started": False,
    }, indent=2))

if __name__ == "__main__":
    main()
