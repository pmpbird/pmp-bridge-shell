#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "tools/run_pass7_unit3_owner_registration_events_v1.py"
SPEC = importlib.util.spec_from_file_location("p7u3_events", RUNNER_PATH)
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


contract = RUNNER.contract()
equal(contract["contract_version"], "PMP_SECTION_OWNER_CAPABILITY_CONTRACT_V1", "contract")
equal(len(contract["owners"]), 8, "known owners")
equal(RUNNER.EVENT_VERSION, "PMP_SECTION_OWNER_REGISTRATION_EVENT_V1", "event version")
equal(len(RUNNER.REQUIRED_FIELDS), 12, "event fields")
equal(len(RUNNER.AUTHORITY_FIELDS), 6, "authority fields")
equal(len(RUNNER.EVENT_TYPES), 4, "event types")

register = RUNNER.event(
    "evt:test:register",
    "op:test:register",
    1,
    "OWNER_REGISTERED",
    "diagnostics_owner",
    "diagnostics",
    "register_owner",
)
update = RUNNER.event(
    "evt:test:update",
    "op:test:update",
    2,
    "OWNER_UPDATED",
    "diagnostics_owner",
    "diagnostics",
    "update_owner",
    previous_event_digest=RUNNER.digest(register),
)
remove = RUNNER.event(
    "evt:test:remove",
    "op:test:remove",
    3,
    "OWNER_REMOVED",
    "diagnostics_owner",
    "diagnostics",
    "remove_owner",
    previous_event_digest=RUNNER.digest(update),
)
positive = RUNNER.evaluate_events([register, update, remove])
equal(positive["status"], "PASS", "status")
check(RUNNER.verify_result_hash(positive), "result hash")
equal([row["code"] for row in positive["outcomes"]], ["OWNER_REGISTERED", "OWNER_UPDATED", "OWNER_REMOVED"], "lifecycle")
equal(positive["summary"]["accepted"], 3, "accepted")
equal(positive["summary"]["rejected"], 0, "rejected")
equal(positive["summary"]["registered_owners"], 0, "removed")
equal(positive["summary"]["authority_grants"], 0, "events grant no authority")
equal(positive["summary"]["shared_operation_identities"], True, "shared operation identities")
equal(
    [row["operation_id"] for row in positive["snapshot"]["journal"]],
    [row["operation_id"] for row in positive["snapshot"]["diagnostics"]],
    "journal diagnostics operation match",
)
check(all(value is False for value in positive["effects"].values()), "no external effects")
check("grants no authority" in positive["claim_ceiling"], "claim ceiling")

growth_authority = RUNNER.authority(
    "diagnostics_owner",
    "observe_owner_growth",
    decision="OBSERVED_ONLY_NO_AUTHORITY",
    authorizer="diagnostics_owner",
    subject_id="diagnostics_owner",
    capability_id="cap:p7u3:growth-observer",
)
growth = RUNNER.event(
    "evt:test:growth",
    "op:test:growth",
    1,
    "OWNER_GROWTH_OBSERVED",
    "brand_new_owner",
    "brand_new_section",
    "observe_owner_growth",
    event_authority=growth_authority,
)
growth_result = RUNNER.evaluate_events([growth])
equal(growth_result["outcomes"][0]["code"], "OWNER_GROWTH_RECORDED_NO_AUTHORITY", "growth recorded")
equal(growth_result["summary"]["pending_growth"], 1, "growth pending")
equal(growth_result["summary"]["registered_owners"], 0, "growth not registered")
equal(growth_result["summary"]["authority_grants"], 0, "growth no authority")
equal(growth_result["snapshot"]["pending_growth"][0]["status"], "OBSERVED_PENDING_NO_AUTHORITY", "pending status")
equal(growth_result["snapshot"]["pending_growth"][0]["authority_granted"], False, "pending no grant")


def code(events: list[Any]) -> str:
    return RUNNER.evaluate_events(events)["outcomes"][-1]["code"]


unknown_register = copy.deepcopy(register)
unknown_register["event_id"] = "evt:test:unknown"
unknown_register["operation_id"] = "op:test:unknown"
unknown_register["owner_id"] = "unknown_owner"
unknown_register["section_id"] = "unknown"
unknown_register["authority"]["subject_id"] = "unknown_owner"
equal(code([unknown_register]), "REJECTED_UNDECLARED_OWNER", "unknown register denied")

wrong_section = copy.deepcopy(register)
wrong_section["event_id"] = "evt:test:wrong-section"
wrong_section["operation_id"] = "op:test:wrong-section"
wrong_section["section_id"] = "bank"
equal(code([wrong_section]), "REJECTED_OWNER_SECTION_MISMATCH", "wrong section denied")

forged = copy.deepcopy(register)
forged["event_id"] = "evt:test:forged"
forged["operation_id"] = "op:test:forged"
forged["authority"]["authorizer"] = "diagnostics_owner"
equal(code([forged]), "REJECTED_REGISTRATION_AUTHORITY", "forged authority denied")

growth_forged = copy.deepcopy(growth)
growth_forged["event_id"] = "evt:test:growth-forged"
growth_forged["operation_id"] = "op:test:growth-forged"
growth_forged["authority"]["decision"] = "AUTHORIZED"
equal(code([growth_forged]), "REJECTED_GROWTH_OBSERVER_AUTHORITY", "growth authority denied")

malformed = copy.deepcopy(register)
malformed.pop("registry_epoch")
equal(code([malformed]), "REJECTED_MALFORMED_EVENT", "malformed denied")

wrong_version = copy.deepcopy(register)
wrong_version["event_version"] = "V2"
equal(code([wrong_version]), "REJECTED_EVENT_VERSION", "version denied")

wrong_contract = copy.deepcopy(register)
wrong_contract["authority"]["contract_version"] = "V0"
equal(code([wrong_contract]), "REJECTED_CAPABILITY_CONTRACT_VERSION", "contract version denied")

stale = RUNNER.event(
    "evt:test:stale",
    "op:test:stale",
    1,
    "OWNER_UPDATED",
    "diagnostics_owner",
    "diagnostics",
    "update_owner",
    previous_event_digest=RUNNER.digest(register),
)
equal(code([register, stale]), "REJECTED_STALE_SEQUENCE", "stale denied")

gap = RUNNER.event(
    "evt:test:gap",
    "op:test:gap",
    3,
    "OWNER_UPDATED",
    "diagnostics_owner",
    "diagnostics",
    "update_owner",
    previous_event_digest=RUNNER.digest(register),
)
equal(code([register, gap]), "REJECTED_SEQUENCE_GAP", "gap denied")

bad_chain = copy.deepcopy(update)
bad_chain["event_id"] = "evt:test:bad-chain"
bad_chain["operation_id"] = "op:test:bad-chain"
bad_chain["previous_event_digest"] = "0" * 64
equal(code([register, bad_chain]), "REJECTED_EVENT_CHAIN", "bad chain denied")

time_regression = copy.deepcopy(update)
time_regression["event_id"] = "evt:test:time"
time_regression["operation_id"] = "op:test:time"
time_regression["observed_at"] = "2026-07-26T00:00:00Z"
equal(code([register, time_regression]), "REJECTED_TIME_REGRESSION", "time regression")

epoch_gap = copy.deepcopy(update)
epoch_gap["event_id"] = "evt:test:epoch-gap"
epoch_gap["operation_id"] = "op:test:epoch-gap"
epoch_gap["registry_epoch"] = 3
equal(code([register, epoch_gap]), "REJECTED_EPOCH_GAP", "epoch gap")

duplicate = RUNNER.evaluate_events([register, register])
equal(duplicate["outcomes"][1]["code"], "DUPLICATE_EVENT_IGNORED", "exact duplicate")
equal(duplicate["outcomes"][1]["mutated"], False, "duplicate no mutation")

conflict = copy.deepcopy(register)
conflict["operation_id"] = "op:test:register-conflict"
conflict["source_version"] = "source:v2"
equal(code([register, conflict]), "REJECTED_DUPLICATE_EVENT_CONFLICT", "duplicate conflict")

same_operation = copy.deepcopy(growth)
same_operation["event_id"] = "evt:test:same-operation"
same_operation["operation_id"] = register["operation_id"]
equal(code([register, same_operation]), "REJECTED_DUPLICATE_OPERATION", "operation duplicate")

update_missing = copy.deepcopy(update)
update_missing["monotonic_sequence"] = 1
update_missing["previous_event_digest"] = None
equal(code([update_missing]), "REJECTED_OWNER_NOT_REGISTERED", "update missing")

remove_missing = copy.deepcopy(remove)
remove_missing["monotonic_sequence"] = 1
remove_missing["previous_event_digest"] = None
equal(code([remove_missing]), "REJECTED_OWNER_NOT_REGISTERED", "remove missing")

for key in RUNNER.REQUIRED_FIELDS:
    check(key in register, f"required event field {key}")
for key in RUNNER.AUTHORITY_FIELDS:
    check(key in register["authority"], f"required authority field {key}")
for item in positive["outcomes"] + growth_result["outcomes"]:
    equal(item["authority_granted"], False, f"{item['code']}: no grant")

scenario = RUNNER.scenario_result()
equal(scenario["status"], "PASS", "scenario status")
equal(scenario["summary"]["events"], 3, "scenario events")
equal(scenario["summary"]["accepted"], 3, "scenario accepted")
equal(scenario["summary"]["registered_owners"], 1, "scenario registered")
equal(scenario["summary"]["pending_growth"], 1, "scenario pending")
equal(scenario["summary"]["authority_grants"], 0, "scenario grants")
equal(scenario["summary"]["shared_operation_identities"], True, "scenario operations")
check(all(value is False for value in scenario["result"]["effects"].values()), "scenario effects")

tampered = copy.deepcopy(positive)
tampered["summary"]["authority_grants"] = 1
equal(RUNNER.verify_result_hash(tampered), False, "tamper denied")

print(f"PASS: P7-U3 owner registration events ({ASSERTIONS}/{ASSERTIONS})")
