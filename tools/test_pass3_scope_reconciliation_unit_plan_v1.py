#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "audit/pass3/pass3-scope-reconciliation-unit-plan-v1.json"
UNIT1 = ROOT / "audit/pass3/pass3-route-guardian-handoff-contract-unit1-v1.json"
CURRENT_MAP = ROOT / "pmp-current-map-v12.json"
HISTORICAL_FREEZE = ROOT / "pmp-pass3-route-handoff-freeze-v1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    plan = load(PLAN)
    unit1 = load(UNIT1)
    current_map = load(CURRENT_MAP)
    historical = load(HISTORICAL_FREEZE)

    assert plan["status"] == "AUTHORITATIVE_FOR_CURRENT_ROADMAP_PASS3"
    assert plan["pass"] == 3
    assert plan["pass_name"] == "Route Guardian -> App Orchestrator Handoff"
    assert plan["base_main_commit"] == "e75f48790d56dfa27278f6de969c4c2af132f9cf"

    units = plan["units"]
    assert [unit["unit"] for unit in units] == [1, 2, 3, 4, 5]
    assert units[0]["status"] == "COMPLETE"
    assert all(unit["status"] == "NOT_STARTED" for unit in units[1:])
    assert units[0]["merged_pr"] == 134
    assert units[0]["resulting_main_commit"] == plan["base_main_commit"]

    boundaries = plan["locked_boundaries"]
    assert boundaries["route_authority"] == unit1["route_authority"] == "pmp-current-map-v12.json"
    assert boundaries["resolver"] == unit1["resolver"] == "pmp-current-route-resolver-v1.js"
    assert boundaries["source_role"] == unit1["source_role"] == "route_guardian"
    assert boundaries["destination_role"] == unit1["destination_role"] == "current_app"
    assert boundaries["handoff_type"] == unit1["handoff_type"] == "PMP_ROUTE_HANDOFF_V1"
    assert boundaries["failure_mode"] == current_map["route_contract"]["failure_mode"] == "fail_closed"
    assert boundaries["implicit_fallbacks"] is False
    assert current_map["route_contract"]["implicit_fallbacks"] is False
    assert boundaries["pr_122"] == "OPEN_UNMERGED_UNAUTHORIZED_DO_NOT_TOUCH"
    assert boundaries["pass4"] == "MUST_NOT_BEGIN_UNTIL_PASS3_CLOSURE_UNIT_MERGES"

    precedence = " ".join(plan["authority_precedence"])
    assert "historical active-path evidence only" in precedence
    assert "historical isolated hook-validation evidence only" in precedence
    assert historical["status"] == "FROZEN"
    assert historical["pass"] == 3

    unit2 = units[1]
    assert unit2["name"] == "Passive runtime consumer integration"
    assert len(unit2["required_discovery_before_edit"]) == 3
    assert any("single narrowest existing consumer" in item for item in unit2["required_discovery_before_edit"])
    assert any("Do not change Current Map destination truth" in item for item in unit2["forbidden_behavior"])
    assert any("Do not claim browser or real-app proof" in item for item in unit2["forbidden_behavior"])

    unit3 = units[2]
    assert unit3["name"] == "Isolated runtime handoff proof"
    assert any("zero navigation assignments" in item for item in unit3["required_cases"])
    assert any("Do not use the real production app" in item for item in unit3["forbidden_behavior"])

    unit4 = units[3]
    assert unit4["name"] == "Bounded live current-path observation"
    assert any("deliberately invalid handoff" in unit4["objective"] for _ in [0])
    assert "not a certification of later passes" in unit4["claim_ceiling"]

    unit5 = units[4]
    assert unit5["name"] == "Pass 3 closure certification"
    assert "Pass 3 is complete only when" in unit5["pass3_completion_test"]
    assert unit5["next_after_completion"].startswith("Pass 4/13")

    repair = plan["repair_scope"]
    assert all(repair[key] is False for key in (
        "runtime_behavior_changed",
        "persisted_user_data_changed",
        "current_map_changed",
        "historical_evidence_deleted",
        "pass3_implementation_advanced",
    ))

    print("PASS: Pass 3 authorities reconciled and Units 1-5 deterministically locked")


if __name__ == "__main__":
    main()
