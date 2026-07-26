#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "tools/run_pass7_unit2_owner_capability_contract_v1.py"
SPEC = importlib.util.spec_from_file_location("p7u2_contract", RUNNER_PATH)
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)
ASSERTIONS = 0


def check(condition: Any, message: str) -> None:
    global ASSERTIONS
    ASSERTIONS += 1
    assert condition, message


def equal(actual: Any, expected: Any, message: str) -> None:
    global ASSERTIONS
    ASSERTIONS += 1
    assert actual == expected, f"{message}: {actual!r} != {expected!r}"


contract = RUNNER.load_contract()
equal(contract["contract_version"], "PMP_SECTION_OWNER_CAPABILITY_CONTRACT_V1", "contract")
equal(contract["model"], "EXPLICIT_CAPABILITY_FAIL_CLOSED", "model")
equal(contract["root_grant_authority"], "app_orchestrator_owner", "root authority")
equal(contract["delegation"]["maximum_depth"], 2, "delegation depth")
equal(contract["delegation"]["authority_expansion"], "FORBIDDEN", "no expansion")
equal(contract["delegation"]["revocation"], "MONOTONIC_CASCADING", "revocation")
equal(contract["unresolved_owner_policy"], "NO_CAPABILITY_UNTIL_EXPLICITLY_RESOLVED", "unresolved")
equal(contract["unknown_owner_policy"], "REJECT_BEFORE_SIDE_EFFECT", "unknown")
equal(contract["duplicate_owner_policy"], "FAIL_CLOSED_AND_DIAGNOSE", "duplicate")
equal(contract["stale_capability_policy"], "REJECT_BEFORE_SIDE_EFFECT", "stale")
equal(len(contract["owners"]), 8, "eight owner contracts")
equal(len(contract["required_capability_fields"]), 14, "exact fields")
check(len(contract["globally_forbidden_actions"]) >= 8, "global denials")
check("route_mutation" in contract["globally_forbidden_actions"], "route denied")
check("bank_mutation" in contract["globally_forbidden_actions"], "bank mutation denied")
check("storage_migration" in contract["globally_forbidden_actions"], "migration denied")
check("persisted_user_data_write" in contract["globally_forbidden_actions"], "user data denied")
check("ownership_takeover" in contract["globally_forbidden_actions"], "takeover denied")

sections = set()
for owner_id, owner in contract["owners"].items():
    check(owner_id.endswith("_owner"), f"{owner_id}: identity")
    check(owner["section_id"], f"{owner_id}: section")
    check(owner["allowed_actions"], f"{owner_id}: actions")
    check(owner["allowed_resources"], f"{owner_id}: resources")
    equal(owner["allowed_resources"], [f"section:{owner['section_id']}"], f"{owner_id}: resource")
    check(not (set(owner["allowed_actions"]) & set(contract["globally_forbidden_actions"])), f"{owner_id}: bounded actions")
    check(owner["section_id"] not in sections, f"{owner_id}: isolated section")
    sections.add(owner["section_id"])
equal(len(sections), 8, "eight isolated sections")

bank = RUNNER.capability(
    "cap:test:bank-root",
    "bank_screen_owner",
    "bank",
    "bank_screen_owner",
    ["read_bank", "render_bank_detail"],
    ["section:bank"],
)
delegate = RUNNER.capability(
    "cap:test:bank-delegate",
    "bank_screen_owner",
    "bank",
    "bank_reader",
    ["read_bank"],
    ["section:bank"],
    granted_by="bank_screen_owner",
    parent_capability_id=bank["capability_id"],
    delegation_depth=1,
    delegable=False,
)
events = [
    RUNNER.event("GRANT", "op:test:grant", capability=bank),
    RUNNER.event("DELEGATE", "op:test:delegate", capability=delegate),
    RUNNER.event(
        "AUTHORIZE",
        "op:test:authorize",
        capability_id=delegate["capability_id"],
        subject_id="bank_reader",
        owner_id="bank_screen_owner",
        section_id="bank",
        action="read_bank",
        resource="section:bank",
        revocation_epoch=0,
    ),
]
first = RUNNER.evaluate_events(events)
second = RUNNER.evaluate_events(events)
equal(first, second, "deterministic evaluation")
check(RUNNER.verify_result_hash(first), "result digest")
equal(first["status"], "PASS", "status")
equal(first["summary"]["accepted"], 3, "positive accepted")
equal(first["summary"]["authorized"], 1, "positive authorized")
equal(first["summary"]["rejected"], 0, "positive rejected")
equal([row["code"] for row in first["outcomes"]], ["CAPABILITY_GRANTED", "CAPABILITY_GRANTED", "AUTHORIZED"], "codes")
check(all(value is False for value in first["effects"].values()), "no external effects")
check("no owner is registered" in first["claim_ceiling"], "claim ceiling")


def last_code(candidate_events: list[Any]) -> str:
    return RUNNER.evaluate_events(candidate_events)["outcomes"][-1]["code"]


cross_section = copy.deepcopy(bank)
cross_section["capability_id"] = "cap:test:cross-section"
cross_section["section_id"] = "continuous_run"
equal(
    last_code([RUNNER.event("GRANT", "op:test:cross-section", capability=cross_section)]),
    "REJECTED_OWNER_SECTION_MISMATCH",
    "cross section denied",
)

cross_resource = copy.deepcopy(bank)
cross_resource["capability_id"] = "cap:test:cross-resource"
cross_resource["resources"] = ["section:continuous_run"]
equal(
    last_code([RUNNER.event("GRANT", "op:test:cross-resource", capability=cross_resource)]),
    "REJECTED_RESOURCE_OUTSIDE_SECTION",
    "cross resource denied",
)

forbidden = copy.deepcopy(bank)
forbidden["capability_id"] = "cap:test:forbidden-action"
forbidden["actions"] = ["route_mutation"]
equal(
    last_code([RUNNER.event("GRANT", "op:test:forbidden-action", capability=forbidden)]),
    "REJECTED_ACTION_OUTSIDE_OWNER",
    "forbidden action denied",
)

unknown = copy.deepcopy(bank)
unknown["capability_id"] = "cap:test:unknown"
unknown["owner_id"] = "unknown_owner"
unknown["subject_id"] = "unknown_owner"
equal(
    last_code([RUNNER.event("GRANT", "op:test:unknown", capability=unknown)]),
    "REJECTED_UNDECLARED_OWNER",
    "unknown owner denied",
)

wrong_root = copy.deepcopy(bank)
wrong_root["capability_id"] = "cap:test:wrong-root"
wrong_root["granted_by"] = "bank_screen_owner"
equal(
    last_code([RUNNER.event("GRANT", "op:test:wrong-root", capability=wrong_root)]),
    "REJECTED_ROOT_GRANT_AUTHORITY",
    "wrong root denied",
)

wrong_subject = copy.deepcopy(bank)
wrong_subject["capability_id"] = "cap:test:wrong-subject"
wrong_subject["subject_id"] = "bank_reader"
equal(
    last_code([RUNNER.event("GRANT", "op:test:wrong-subject", capability=wrong_subject)]),
    "REJECTED_ROOT_SUBJECT",
    "root subject denied",
)

nondelegable = copy.deepcopy(bank)
nondelegable["capability_id"] = "cap:test:nondelegable"
nondelegable["delegable"] = False
child = copy.deepcopy(delegate)
child["capability_id"] = "cap:test:nondelegable-child"
child["parent_capability_id"] = nondelegable["capability_id"]
equal(
    last_code([
        RUNNER.event("GRANT", "op:test:nondelegable-root", capability=nondelegable),
        RUNNER.event("DELEGATE", "op:test:nondelegable-child", capability=child),
    ]),
    "REJECTED_PARENT_NOT_DELEGABLE",
    "nondelegable parent denied",
)

expanded = copy.deepcopy(delegate)
expanded["capability_id"] = "cap:test:expanded"
expanded["actions"] = ["read_bank", "render_bank_detail", "request_bank_mutation"]
equal(
    last_code([
        RUNNER.event("GRANT", "op:test:expanded-root", capability=bank),
        RUNNER.event("DELEGATE", "op:test:expanded-child", capability=expanded),
    ]),
    "REJECTED_ACTION_OUTSIDE_OWNER",
    "delegated owner expansion denied",
)

depth1 = copy.deepcopy(delegate)
depth1["capability_id"] = "cap:test:depth1"
depth1["delegable"] = True
depth2 = copy.deepcopy(depth1)
depth2["capability_id"] = "cap:test:depth2"
depth2["subject_id"] = "bank_reader_2"
depth2["granted_by"] = "bank_reader"
depth2["parent_capability_id"] = depth1["capability_id"]
depth2["delegation_depth"] = 2
depth3 = copy.deepcopy(depth2)
depth3["capability_id"] = "cap:test:depth3"
depth3["subject_id"] = "bank_reader_3"
depth3["granted_by"] = "bank_reader_2"
depth3["parent_capability_id"] = depth2["capability_id"]
depth3["delegation_depth"] = 3
equal(
    last_code([
        RUNNER.event("GRANT", "op:test:depth-root", capability=bank),
        RUNNER.event("DELEGATE", "op:test:depth1", capability=depth1),
        RUNNER.event("DELEGATE", "op:test:depth2", capability=depth2),
        RUNNER.event("DELEGATE", "op:test:depth3", capability=depth3),
    ]),
    "REJECTED_DELEGATION_DEPTH",
    "depth expansion denied",
)

cross_owner = copy.deepcopy(delegate)
cross_owner["capability_id"] = "cap:test:cross-owner"
cross_owner["owner_id"] = "continuous_run_level_owner"
cross_owner["section_id"] = "continuous_run"
cross_owner["resources"] = ["section:continuous_run"]
cross_owner["actions"] = ["read_run"]
equal(
    last_code([
        RUNNER.event("GRANT", "op:test:cross-owner-root", capability=bank),
        RUNNER.event("DELEGATE", "op:test:cross-owner-child", capability=cross_owner),
    ]),
    "REJECTED_CROSS_OWNER_DELEGATION",
    "bank to run delegation denied",
)

duplicate = copy.deepcopy(bank)
equal(
    last_code([
        RUNNER.event("GRANT", "op:test:dup-a", capability=bank),
        RUNNER.event("GRANT", "op:test:dup-b", capability=duplicate),
    ]),
    "REJECTED_DUPLICATE_CAPABILITY",
    "duplicate capability denied",
)

equal(
    last_code([
        RUNNER.event("GRANT", "op:test:duplicate-operation", capability=bank),
        RUNNER.event(
            "AUTHORIZE",
            "op:test:duplicate-operation",
            capability_id=bank["capability_id"],
            subject_id="bank_screen_owner",
            owner_id="bank_screen_owner",
            section_id="bank",
            action="read_bank",
            resource="section:bank",
            revocation_epoch=0,
        ),
    ]),
    "REJECTED_DUPLICATE_OPERATION",
    "duplicate operation denied",
)

expired = copy.deepcopy(bank)
expired["capability_id"] = "cap:test:expired"
expired["expires_at"] = "2026-07-27T00:00:00Z"
equal(
    last_code([
        RUNNER.event("GRANT", "op:test:expired-grant", capability=expired),
        RUNNER.event(
            "AUTHORIZE",
            "op:test:expired-auth",
            capability_id=expired["capability_id"],
            subject_id="bank_screen_owner",
            owner_id="bank_screen_owner",
            section_id="bank",
            action="read_bank",
            resource="section:bank",
            revocation_epoch=0,
        ),
    ]),
    "REJECTED_EXPIRED",
    "expiry denied",
)

revoked_result = RUNNER.evaluate_events([
    RUNNER.event("GRANT", "op:test:revoke-root", capability=bank),
    RUNNER.event("DELEGATE", "op:test:revoke-child", capability=delegate),
    RUNNER.event(
        "REVOKE",
        "op:test:revoke",
        capability_id=bank["capability_id"],
        actor_id="app_orchestrator_owner",
        revocation_epoch=1,
    ),
    RUNNER.event(
        "AUTHORIZE",
        "op:test:revoked-auth",
        capability_id=delegate["capability_id"],
        subject_id="bank_reader",
        owner_id="bank_screen_owner",
        section_id="bank",
        action="read_bank",
        resource="section:bank",
        revocation_epoch=0,
    ),
])
equal(revoked_result["outcomes"][-1]["code"], "REJECTED_CAPABILITY_REVOKED", "revoked denied")
equal(revoked_result["summary"]["capabilities_revoked"], 2, "cascade revocation")
equal(set(revoked_result["state"]["revoked"]), {bank["capability_id"], delegate["capability_id"]}, "cascade members")

stale_revoke = RUNNER.evaluate_events([
    RUNNER.event("GRANT", "op:test:stale-root", capability=bank),
    RUNNER.event(
        "REVOKE",
        "op:test:stale-revoke",
        capability_id=bank["capability_id"],
        actor_id="app_orchestrator_owner",
        revocation_epoch=0,
    ),
])
equal(stale_revoke["outcomes"][-1]["code"], "REJECTED_STALE_REVOCATION", "stale revoke")

unauthorized_revoke = RUNNER.evaluate_events([
    RUNNER.event("GRANT", "op:test:unauth-root", capability=bank),
    RUNNER.event(
        "REVOKE",
        "op:test:unauth-revoke",
        capability_id=bank["capability_id"],
        actor_id="continuous_run_level_owner",
        revocation_epoch=1,
    ),
])
equal(unauthorized_revoke["outcomes"][-1]["code"], "REJECTED_REVOCATION_AUTHORITY", "unauthorized revoke")

tampered = copy.deepcopy(first)
tampered["outcomes"][0]["code"] = "AUTHORIZED"
equal(RUNNER.verify_result_hash(tampered), False, "tampered digest rejected")

scenario = RUNNER.scenario_results()
equal(scenario["status"], "PASS", "scenario status")
equal(scenario["summary"]["owners_contract_bound"], 8, "scenario owners")
equal(scenario["summary"]["positive_events"], 5, "scenario events")
equal(scenario["summary"]["positive_accepted"], 4, "scenario accepted")
equal(scenario["summary"]["revocation_cascade_members"], 2, "scenario cascade")
equal(scenario["summary"]["denial_scenarios"], 4, "scenario denials")
equal(scenario["summary"]["denial_scenarios_matched"], 4, "scenario matches")
check(all(row["expected"] == row["actual"] for row in scenario["denial_scenarios"]), "all denials matched")
check(all(value is False for value in scenario["effects"].values()), "scenario no external effects")

# The contract must list every stable failure code exercised by this unit.
codes = set(contract["failure_codes"])
for result in (
    first,
    revoked_result,
    stale_revoke,
    unauthorized_revoke,
):
    for outcome in result["outcomes"]:
        if outcome["code"].startswith("REJECTED_"):
            check(outcome["code"] in codes, f"documented failure code {outcome['code']}")

print(f"PASS: P7-U2 owner capability contract ({ASSERTIONS}/{ASSERTIONS})")
