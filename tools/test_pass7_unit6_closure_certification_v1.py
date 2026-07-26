#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "audit/pass7/pass7-section-owner-unit6-closure-certification-v1.json"
RECEIPT = (
    ROOT
    / "audit/pass7/receipts/RECEIPT_P7_U6_SECTION_OWNER_CLOSURE_20260726T172000Z_001.json"
)
UNIT_PATHS = {
    "P7-U1": ROOT / "audit/pass7/pass7-section-owner-unit1-inventory-v1.json",
    "P7-U2": ROOT / "audit/pass7/pass7-section-owner-unit2-capability-contract-v1.json",
    "P7-U3": ROOT / "audit/pass7/pass7-section-owner-unit3-registration-events-v1.json",
    "P7-U4": ROOT
    / "audit/pass7/pass7-section-owner-unit4-mount-diagnostics-integration-v1.json",
    "P7-U5": ROOT
    / "audit/pass7/pass7-section-owner-unit5-isolation-restart-denial-proof-v1.json",
}
RECEIPT_PATHS = {
    "P7-U1": ROOT
    / "audit/pass7/receipts/RECEIPT_P7_U1_SECTION_OWNER_INVENTORY_20260726T161500Z_001.json",
    "P7-U2": ROOT
    / "audit/pass7/receipts/RECEIPT_P7_U2_OWNER_CAPABILITY_CONTRACT_20260726T162500Z_001.json",
    "P7-U3": ROOT
    / "audit/pass7/receipts/RECEIPT_P7_U3_OWNER_REGISTRATION_EVENTS_20260726T163500Z_001.json",
    "P7-U4": ROOT
    / "audit/pass7/receipts/RECEIPT_P7_U4_OWNER_MOUNT_DIAGNOSTICS_INTEGRATION_20260726T165000Z_001.json",
    "P7-U5": ROOT
    / "audit/pass7/receipts/RECEIPT_P7_U5_OWNER_ISOLATION_RESTART_DENIAL_20260726T171000Z_001.json",
}
STATUSES = {
    "P7-U1": "SECTION_OWNER_INVENTORY_PROVEN",
    "P7-U2": "SECTION_OWNER_CAPABILITY_CONTRACT_PROVEN",
    "P7-U3": "OWNER_REGISTRATION_EVENTS_PROVEN",
    "P7-U4": "OWNER_MOUNT_DIAGNOSTICS_INTEGRATION_PROVEN",
    "P7-U5": "OWNER_ISOLATION_RESTART_DENIAL_PROVEN",
}
ASSERTION_COUNTS = {
    "P7-U1": 168,
    "P7-U2": 115,
    "P7-U3": 72,
    "P7-U4": 137,
    "P7-U5": 218,
}
ASSERTIONS = 0


def check(condition: Any, message: str) -> None:
    global ASSERTIONS
    ASSERTIONS += 1
    assert condition, message


def equal(actual: Any, expected: Any, message: str) -> None:
    global ASSERTIONS
    ASSERTIONS += 1
    assert actual == expected, f"{message}: {actual!r} != {expected!r}"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


report = json.loads(REPORT.read_text())
receipt = json.loads(RECEIPT.read_text())
units = {unit: json.loads(path.read_text()) for unit, path in UNIT_PATHS.items()}
receipts = {
    unit: json.loads(path.read_text()) for unit, path in RECEIPT_PATHS.items()
}

equal(report["type"], "PMP_PASS7_SECTION_OWNER_UNIT6_CLOSURE_CERTIFICATION_V1", "type")
equal(report["version"], "1.0.0", "version")
equal(report["pass"], 7, "pass")
equal(report["unit_id"], "P7-U6", "unit")
equal(report["status"], "PASS7_SECTION_OWNER_RULES_CERTIFIED", "status")
equal(receipt["status"], report["status"], "receipt status")
equal(receipt["evidence"], REPORT.relative_to(ROOT).as_posix(), "receipt evidence")
equal(report["base_main_commit"], "4a47b47b1aa6739d30adb32425ad3dd8a57ba0b3", "base")

for unit, path in UNIT_PATHS.items():
    item = units[unit]
    prior_receipt = receipts[unit]
    equal(item["unit_id"], unit, f"{unit} identity")
    equal(item["status"], STATUSES[unit], f"{unit} status")
    equal(prior_receipt["status"], STATUSES[unit], f"{unit} receipt status")
    equal(item["verification"]["assertions_passed"], ASSERTION_COUNTS[unit], f"{unit} assertions")
    equal(item["verification"]["assertions_failed"], 0, f"{unit} no assertion failure")
    equal(report["inputs"][f"{unit.lower().replace('-', '_')}_sha256"], sha(path), f"{unit} hash")
    equal(item["effects"]["live_observation_performed"], False, f"{unit} no live observation")
    equal(item["effects"]["formal_proof_performed"], False, f"{unit} no formal proof")
    equal(item["effects"]["persisted_user_data_changed"], False, f"{unit} no data write")
    equal(item["authority"]["special_authority_consumed"], False, f"{unit} no special authority")
    equal(item["no_blind_flying_gate"]["upload_before_enforcement"], True, f"{unit} upload first")
    equal(item["no_blind_flying_gate"]["automatic_retry"], False, f"{unit} no retry")
    equal(
        item["no_blind_flying_gate"]["special_authority"]["consumed"],
        False,
        f"{unit} gate unconsumed",
    )

equal(sum(ASSERTION_COUNTS.values()), 710, "prior deterministic assertion total")
equal(report["evidence_summary"]["prior_assertions"], 710, "reported assertion total")
equal(len(report["evidence_summary"]["units"]), 5, "five predecessor units")
equal(
    [row["unit_id"] for row in report["evidence_summary"]["units"]],
    list(UNIT_PATHS),
    "ordered unit trace",
)
for row in report["evidence_summary"]["units"]:
    equal(row["status"], STATUSES[row["unit_id"]], f"{row['unit_id']} trace status")
    equal(
        row["assertions"],
        ASSERTION_COUNTS[row["unit_id"]],
        f"{row['unit_id']} trace assertions",
    )

u1 = units["P7-U1"]
equal(u1["inventory"]["owners_declared"], 8, "eight owners inventoried")
equal(u1["inventory"]["sections_inventory"], 8, "eight sections inventoried")
equal(len(u1["inventory"]["unresolved_cases"]), 4, "four unresolved categories")
equal(
    [row["kind"] for row in u1["inventory"]["unresolved_cases"]][-1],
    "BANK_CONTINUOUS_RUN_OVERLAP",
    "Bank overlap preserved for Pass 9",
)

u2 = units["P7-U2"]
contract = u2["capability_contract"]
equal(contract["model"], "EXPLICIT_CAPABILITY_FAIL_CLOSED", "explicit capability model")
equal(contract["root_grant_authority"], "app_orchestrator_owner", "root authority")
equal(len(contract["owners"]), 8, "eight capability owners")
equal(contract["delegation"]["same_owner_required"], True, "same owner delegation")
equal(contract["delegation"]["same_section_required"], True, "same section delegation")
equal(contract["delegation"]["maximum_depth"], 2, "bounded delegation")
equal(contract["duplicate_owner_policy"], "FAIL_CLOSED_AND_DIAGNOSE", "duplicate policy")
equal(contract["unknown_owner_policy"], "REJECT_BEFORE_SIDE_EFFECT", "unknown policy")
equal(
    contract["bank_continuous_run_policy"],
    "SEPARATE_OWNERS_AND_SECTIONS_NO_CROSS_DELEGATION_PASS9_REMAINS_REQUIRED",
    "Pass 9 split retained",
)

u3 = units["P7-U3"]
events = u3["event_contract"]
equal(len(events["event_types"]), 4, "four owner event types")
equal(events["appearance_grants_authority"], False, "appearance no authority")
equal(events["operation_identity"], "SHARED_BY_REGISTRY_JOURNAL_AND_DIAGNOSTICS", "shared identity")
equal(events["restart"], "REPLAY_ONLY_VALIDATED_CHAINED_JOURNAL", "restart contract")
equal(events["duplicates"]["exact_event"], "IGNORE_NO_MUTATION", "exact duplicate policy")
equal(events["duplicates"]["conflicting_event"], "REJECT_FAIL_CLOSED", "conflict policy")

u4 = units["P7-U4"]
integration = u4["integration"]
equal(integration["runtime_owner"], "mount_registry_owner", "integration owner")
equal(integration["runtime_mode"], "PASSIVE_EXPLICIT_OWNER_EVENTS_ONLY", "passive mode")
equal(integration["known_owners"], 8, "eight integrated owners")
equal(integration["known_sections"], 8, "eight integrated sections")
equal(integration["appearance_grants_authority"], False, "integration no implicit authority")
equal(integration["shared_operation_identities"], True, "integration shared identity")
equal(integration["capability_ids_exposed"], False, "capability IDs redacted")
equal(integration["raw_authority_payloads_exposed"], False, "authority redacted")
equal(integration["source_versions_exposed"], False, "source versions redacted")
equal(integration["maximum_visible_events"], 128, "Diagnostics bounded")
equal(u4["effects"]["bank_mutations"], False, "U4 no Bank mutation")
equal(u4["effects"]["storage_writes"], False, "U4 no storage write")

u5 = units["P7-U5"]
hardening = u5["hardening"]
equal(hardening["capability_after"], "EXACT_CAPABILITY_ID_FOR_EVENT_OWNER", "exact binding")
equal(hardening["cross_owner_capability_result"], "REJECTED_REGISTRATION_AUTHORITY", "cross owner denied")
equal(hardening["restart_api"], "restore", "restart API")
equal(
    hardening["restart_policy"],
    "ATOMIC_REPLAY_ONLY_VALIDATED_CHAINED_JOURNAL",
    "atomic restart",
)
equal(hardening["partial_restart_state_exposed"], False, "no partial restart")
equal(hardening["replay_operation_identities_preserved"], True, "replay identities")
equal(hardening["appearance_grants_authority"], False, "hardening no implicit authority")
equal(u5["proof_matrix"]["cross_owner_capability_denials"], 8, "eight cross capability denials")
equal(u5["proof_matrix"]["cross_section_denials"], 8, "eight cross section denials")
equal(u5["effects"]["bank_mutations"], False, "U5 no Bank mutation")
equal(u5["effects"]["production_behavior_activated"], False, "U5 no activation")

decision = report["observation_sufficiency"]
equal(decision["decision"], "NEW_SCARCE_OBSERVATION_NOT_REQUIRED", "observation decision")
equal(decision["new_observation_performed"], False, "no new observation")
equal(decision["special_authority_consumed"], False, "no special authority consumed")
equal(decision["retry_of_consumed_observation"], False, "no consumed retry")
equal(decision["user_app_check_required"], False, "no app check")
equal(decision["formal_proof_required"], False, "no formal proof")
equal(decision["basis"]["p7_u4_deterministic_assertions"], 137, "U4 deterministic basis")
equal(decision["basis"]["p7_u5_deterministic_assertions"], 218, "U5 deterministic basis")
equal(decision["basis"]["p7_u4_ci_live_runtime_run"], 30211347508, "U4 runtime CI")
equal(decision["basis"]["p7_u4_ci_real_app_visual_run"], 30211347557, "U4 visual CI")
equal(decision["basis"]["p7_u5_ci_live_runtime_run"], 30212082678, "U5 runtime CI")
equal(decision["basis"]["p7_u5_ci_real_app_visual_run"], 30212082709, "U5 visual CI")
equal(decision["basis"]["p7_u5_a003_integrity_run"], 30212082694, "U5 A003 CI")
equal(decision["basis"]["p7_u5_permanent_gate_run"], 30212082736, "U5 permanent gate")
equal(decision["prior_hands_on_evidence"]["used_as_pass7_specific_proof"], False, "hands-on not overclaimed")
equal(decision["prior_hands_on_evidence"]["new_execution"], False, "no hands-on execution")

criteria = report["exit_criteria"]
for key in (
    "inventory_locked",
    "explicit_capabilities_fail_closed",
    "delegation_bounded_and_revocable",
    "owner_events_versioned_and_chained",
    "growth_visible_pending_no_authority",
    "production_integration_passive",
    "mount_registry_single_owner_preserved",
    "diagnostics_read_only_and_redacted",
    "exact_owner_capability_binding_enforced",
    "duplicate_and_stale_inputs_fail_closed",
    "restart_replay_atomic",
    "shared_operation_identities_preserved",
    "bank_and_continuous_run_separate",
    "zero_persisted_user_data_writes",
    "permanent_gate_green",
    "all_required_github_checks_green",
):
    equal(criteria[key], True, f"exit criterion {key}")

effects = report["effects"]
for key, value in effects.items():
    equal(value, False, f"closure effect {key}")
equal(report["authority"]["special_authority_type"], "NONE", "closure authority type")
equal(report["authority"]["special_authority_consumed"], False, "closure authority unconsumed")
equal(report["authority"]["retry_authorized"], False, "closure retry unauthorized")
equal(report["no_retry_gates"]["consumed_observation_prs"], [149, 150, 152], "preserved observations")
equal(report["no_retry_gates"]["formal_proof_pr"], 122, "formal proof preserved")
equal(report["no_retry_gates"]["retry_authorized"], False, "no retry")

binding = report["no_blind_flying_gate"]
equal(binding["ci_lane"], "static_contract", "closure lane")
equal(binding["diagnostic_matrix_update"]["status"], "CONFIRMED_UNCHANGED", "matrix unchanged")
equal(len(binding["diagnostic_evidence_routes"]), 6, "six diagnostic routes")
equal(len(binding["deterministic_test_paths"]), 1, "one closure test")
equal(len(binding["verifier_paths"]), 1, "one closure verifier")
equal(len(binding["receipt_paths"]), 1, "one closure receipt")
equal(binding["fault_injection"]["status"], "NOT_APPLICABLE", "closure no fault injection")
equal(binding["fault_injection"]["cases"], [], "closure fault cases empty")
equal(len(binding["required_artifact_roles"]), 9, "nine artifact roles")
equal(binding["upload_before_enforcement"], True, "closure upload first")
equal(binding["automatic_retry"], False, "closure no retry")
equal(binding["special_authority"]["required"], False, "closure no special authority")
equal(binding["special_authority"]["consumed"], False, "closure consumes nothing")

equal(report["pass7_result"], "PASS", "Pass 7 result")
equal(report["next_step"]["id"], "P8-U1", "next step")
equal(report["next_step"]["requires_user_app_check"], False, "next no app check")
equal(report["next_step"]["requires_new_explicit_authority"], False, "next no authority")
equal(report["next_step"]["stop_after"], False, "continue")
equal(receipt["pass7_result"], "PASS", "receipt Pass 7 result")
equal(receipt["next_safe_move"]["step_id"], "P8-U1", "receipt next")
check(report["verification"]["assertions_passed"] >= 140, "closure assertion count recorded")
equal(report["verification"]["assertions_failed"], 0, "closure no assertion failures")

print(f"PASS: P7-U6 Section Owner closure certification ({ASSERTIONS}/{ASSERTIONS})")
