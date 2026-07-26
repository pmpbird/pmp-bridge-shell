#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "audit/pass8/pass8-helper-unit6-closure-certification-v1.json"
RECEIPT = ROOT / "audit/pass8/receipts/RECEIPT_P8_U6_HELPER_SAFETY_CLOSURE_20260726T190000Z_001.json"
UNIT_PATHS = {
    "P8-U1": ROOT / "audit/pass8/pass8-helper-unit1-inventory-v1.json",
    "P8-U2": ROOT / "audit/pass8/pass8-helper-unit2-capability-contract-v1.json",
    "P8-U3": ROOT / "audit/pass8/pass8-helper-unit3-registration-events-v1.json",
    "P8-U4": ROOT / "audit/pass8/pass8-helper-unit4-owner-diagnostics-integration-v1.json",
    "P8-U5": ROOT / "audit/pass8/pass8-helper-unit5-isolation-restart-denial-proof-v1.json",
}
RECEIPT_PATHS = {
    "P8-U1": ROOT / "audit/pass8/receipts/RECEIPT_P8_U1_HELPER_INVENTORY_20260726T173500Z_001.json",
    "P8-U2": ROOT / "audit/pass8/receipts/RECEIPT_P8_U2_HELPER_CAPABILITY_CONTRACT_20260726T175000Z_001.json",
    "P8-U3": ROOT / "audit/pass8/receipts/RECEIPT_P8_U3_HELPER_REGISTRATION_EVENTS_20260726T180500Z_001.json",
    "P8-U4": ROOT / "audit/pass8/receipts/RECEIPT_P8_U4_HELPER_OWNER_DIAGNOSTICS_INTEGRATION_20260726T183000Z_001.json",
    "P8-U5": ROOT / "audit/pass8/receipts/RECEIPT_P8_U5_HELPER_ISOLATION_RESTART_DENIAL_20260726T185000Z_001.json",
}
STATUSES = {
    "P8-U1": "HELPER_INVENTORY_PROVEN",
    "P8-U2": "HELPER_CAPABILITY_CONTRACT_PROVEN",
    "P8-U3": "HELPER_REGISTRATION_EVENTS_PROVEN",
    "P8-U4": "HELPER_OWNER_DIAGNOSTICS_INTEGRATION_PROVEN",
    "P8-U5": "HELPER_ISOLATION_RESTART_DENIAL_PROVEN",
}
ASSERTION_COUNTS = {
    "P8-U1": 421,
    "P8-U2": 255,
    "P8-U3": 155,
    "P8-U4": 443,
    "P8-U5": 251,
}
ASSERTIONS = 0


def equal(actual: Any, expected: Any, message: str) -> None:
    global ASSERTIONS
    ASSERTIONS += 1
    assert actual == expected, f"{message}: {actual!r} != {expected!r}"


def check(condition: Any, message: str) -> None:
    global ASSERTIONS
    ASSERTIONS += 1
    assert condition, message


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


report = json.loads(REPORT.read_text())
receipt = json.loads(RECEIPT.read_text())
units = {unit: json.loads(path.read_text()) for unit, path in UNIT_PATHS.items()}
receipts = {unit: json.loads(path.read_text()) for unit, path in RECEIPT_PATHS.items()}

equal(report["type"], "PMP_PASS8_HELPER_UNIT6_CLOSURE_CERTIFICATION_V1", "type")
equal(report["version"], "1.0.0", "version")
equal(report["base_main_commit"], "06a0ad231cba79c52cab349b233e9b28ecdb096b", "base")
equal(report["pass"], 8, "pass")
equal(report["unit_id"], "P8-U6", "unit")
equal(report["status"], "PASS8_HELPER_RULES_CERTIFIED", "status")
equal(receipt["status"], report["status"], "receipt status")
equal(receipt["evidence"], REPORT.relative_to(ROOT).as_posix(), "receipt evidence")

for unit, path in UNIT_PATHS.items():
    item = units[unit]
    prior_receipt = receipts[unit]
    key = unit.lower().replace("-", "_") + "_sha256"
    equal(item["unit_id"], unit, f"{unit} identity")
    equal(item["status"], STATUSES[unit], f"{unit} status")
    equal(prior_receipt["status"], STATUSES[unit], f"{unit} receipt status")
    equal(item["verification"]["assertions_passed"], ASSERTION_COUNTS[unit], f"{unit} assertions")
    equal(item["verification"]["assertions_failed"], 0, f"{unit} no failure")
    equal(report["inputs"][key], sha(path), f"{unit} hash")
    equal(item["effects"]["live_observation_performed"], False, f"{unit} no observation")
    equal(item["effects"]["formal_proof_performed"], False, f"{unit} no formal proof")
    equal(item["effects"]["persisted_user_data_changed"], False, f"{unit} no data change")
    equal(item["authority"]["special_authority_consumed"], False, f"{unit} no authority consumed")
    equal(item["no_blind_flying_gate"]["upload_before_enforcement"], True, f"{unit} upload first")
    equal(item["no_blind_flying_gate"]["automatic_retry"], False, f"{unit} no retry")

equal(sum(ASSERTION_COUNTS.values()), 1525, "prior assertion total")
equal(report["evidence_summary"]["prior_assertions"], 1525, "reported prior assertions")
equal(len(report["evidence_summary"]["units"]), 5, "five predecessor units")
equal([row["unit_id"] for row in report["evidence_summary"]["units"]], list(UNIT_PATHS), "ordered trace")
for row in report["evidence_summary"]["units"]:
    equal(row["status"], STATUSES[row["unit_id"]], f"{row['unit_id']} trace status")
    equal(row["assertions"], ASSERTION_COUNTS[row["unit_id"]], f"{row['unit_id']} trace assertions")
for head in report["evidence_summary"]["github_heads"].values():
    equal(head["all_required_checks_green"], True, "GitHub head green")

u1 = units["P8-U1"]["inventory"]
equal(u1["declared_helpers"], 14, "declared Helpers")
equal(u1["accepted_helpers"], 12, "eligible Helpers")
equal(u1["legacy_helpers_declared"], 1, "legacy declaration")
equal(u1["growth_helpers"], 1, "growth declaration")
equal(u1["helper_named_undeclared_sources"], 9, "unknown sources")
equal(u1["duplicate_ids"], 0, "no duplicate IDs")
equal(u1["declared_files_missing"], 0, "no missing declared files")

u2 = units["P8-U2"]["helper_contract"]
equal(u2["model"], "EXPLICIT_HELPER_CAPABILITY_FAIL_CLOSED", "capability model")
equal(u2["root_grant_authority"], "app_orchestrator_owner", "root authority")
equal(len(u2["owner_bindings"]), 8, "owner bindings")
equal(u2["owner_bindings"]["bug_bank_owner"]["canonical_owner_id"], "bank_screen_owner", "Bank owner")
equal(u2["owner_bindings"]["continuous_run_owner"]["canonical_owner_id"], "continuous_run_level_owner", "Continuous Run owner")
equal(u2["legacy_policy"], "HOLD_NO_ACTIVE_CAPABILITY", "legacy held")
equal(u2["unknown_source_policy"], "HOLD_NO_CAPABILITY", "unknown held")
equal(len(u2["unknown_helper_sources"]), 9, "nine unknown sources")
equal(u2["growth_policy"], "EXACT_DECLARED_SOURCE_OWNER_SLOT_AND_GROWTH_BINDING", "growth binding")
equal(u2["revocation_policy"], "MONOTONIC_FAIL_CLOSED", "revocation")
check("bank_mutation" in u2["globally_forbidden_actions"], "Bank mutation forbidden")
check("persisted_user_data_write" in u2["globally_forbidden_actions"], "data writes forbidden")

u3 = units["P8-U3"]["registration_contract"]
equal(u3["model"], "APPEND_ONLY_DIGEST_CHAIN_FAIL_CLOSED", "journal model")
equal(len(u3["event_types"]), 5, "five event types")
equal(u3["registration_authorizer"], "app_orchestrator_owner", "registration authority")
equal(u3["growth_observer"], "diagnostics_owner", "growth observer")
equal(u3["growth_policy"], "OBSERVED_PENDING_NO_AUTHORITY", "growth pending")
equal(u3["duplicate_operation_policy"], "DENY", "duplicate operation")
equal(u3["restore_policy"], "ATOMIC_EXACT_PACKAGE_OR_EMPTY", "atomic restore")
equal(u3["held_helper_policy"], "NO_REGISTRATION_EVENT", "held has no event")
equal(u3["unknown_helper_policy"], "NO_REGISTRATION_EVENT", "unknown has no event")

u4 = units["P8-U4"]["integration"]
equal(u4["runtime_mode"], "PASSIVE_EXPLICIT_HELPER_EVENTS_ONLY", "passive integration")
equal(u4["event_digest_algorithm"], "SHA-256_CANONICAL_JSON_MATCHES_P8_U3", "SHA-256 chain")
equal(u4["section_owner_registration_required"], True, "owner required")
equal(u4["declared_helpers"], 14, "integrated declarations")
equal(u4["eligible_static_helpers"], 12, "integrated eligible")
equal(u4["held_declared_helpers"], 2, "integrated holds")
equal(u4["unknown_sources_held"], 9, "unknown held")
equal(u4["helpers_registered_at_boot"], 0, "no boot registration")
equal(u4["helper_behavior_activations"], 0, "no behavior activation")
equal(u4["authority_grants"], 0, "no authority grants")
equal(u4["diagnostics_access"], "READ_ONLY_BOUNDED_REDACTED", "Diagnostics access")
equal(u4["maximum_visible_events"], 128, "Diagnostics bound")
equal(u4["atomic_restart_policy"], "EXACT_SEALED_PACKAGE_OR_EMPTY", "integration restore")

u5 = units["P8-U5"]["proof"]
equal(u5["eligible_registration_successes"], 12, "all eligible proven")
equal(u5["held_declared_denials"], 2, "held denied")
equal(u5["unknown_helper_denials"], 9, "unknown denied")
equal(u5["missing_section_owner_denials"], 12, "missing owner denied")
equal(u5["binding_faults"], 96, "binding faults")
equal(u5["binding_faults_denied"], 96, "binding faults denied")
equal(u5["growth_observations_accepted_no_authority"], 1, "growth no authority")
equal(u5["non_growth_observation_denials"], 11, "non-growth denied")
equal(u5["revoked_behavior_authorized"], False, "revoked behavior denied")
equal(u5["restart_entries"], 12, "restart entries")
equal(u5["restart_tamper_cases"], 4, "restart tamper cases")
equal(u5["restart_tamper_result"], "FAIL_CLOSED_EMPTY", "tamper fail closed")
equal(u5["restart_missing_owner_result"], "FAIL_CLOSED_EMPTY", "owner restore fail closed")
equal(u5["diagnostic_source_events"], 130, "diagnostic source count")
equal(u5["diagnostic_visible_events"], 128, "diagnostic visible count")
equal(u5["diagnostic_events_truncated"], True, "diagnostic truncation")
equal(u5["authority_grants"], 0, "proof authority grants")
equal(u5["behavior_authorizations"], 0, "proof behavior authority")
equal(u5["external_effects"], 0, "zero external effects")

decision = report["observation_sufficiency"]
equal(decision["decision"], "NEW_SCARCE_OBSERVATION_NOT_REQUIRED", "observation decision")
equal(decision["new_observation_performed"], False, "no new observation")
equal(decision["special_authority_consumed"], False, "no special authority")
equal(decision["retry_of_consumed_observation"], False, "no consumed retry")
equal(decision["user_app_check_required"], False, "no app check")
equal(decision["formal_proof_required"], False, "no formal proof")

equal(len(report["exit_criteria"]), 18, "exit criteria count")
check(all(report["exit_criteria"].values()), "all exit criteria pass")
boundary = report["pass9_boundary"]
equal(boundary["entry_unit"], "P9-U1", "Pass 9 entry")
equal(boundary["bank_owner"], "bank_screen_owner", "Pass 9 Bank owner")
equal(boundary["continuous_run_owner"], "continuous_run_level_owner", "Pass 9 Continuous Run owner")
equal(boundary["cross_delegation"], "FORBIDDEN", "no cross delegation")
equal(boundary["actual_repair_target"], "P9-U3", "actual repair target")

binding = report["no_blind_flying_gate"]
equal(binding["ci_lane"], "static_contract", "closure lane")
equal(binding["diagnostic_matrix_update"]["status"], "CONFIRMED_UNCHANGED", "matrix unchanged")
equal(len(binding["diagnostic_evidence_routes"]), 6, "six evidence routes")
equal(binding["fault_injection"]["status"], "NOT_APPLICABLE", "closure no fault injection")
equal(binding["fault_injection"]["cases"], [], "closure fault cases empty")
equal(len(binding["required_artifact_roles"]), 9, "artifact roles")
equal(binding["upload_before_enforcement"], True, "upload first")
equal(binding["automatic_retry"], False, "no retry")
equal(binding["special_authority"]["required"], False, "no special authority required")
equal(binding["special_authority"]["consumed"], False, "no special authority consumed")

check(all(value is False for value in report["effects"].values()), "closure has no effects")
equal(report["authority"]["special_authority_type"], "NONE", "authority type")
equal(report["authority"]["special_authority_consumed"], False, "authority unconsumed")
equal(report["no_retry_gates"]["consumed_observation_prs"], [149, 150, 152], "preserved observations")
equal(report["no_retry_gates"]["formal_proof_pr"], 122, "preserved formal proof")
equal(report["no_retry_gates"]["retry_authorized"], False, "no retry")
equal(report["pass8_result"], "PASS", "Pass 8 result")
equal(report["next_step"]["id"], "P9-U1", "next step")
equal(report["next_step"]["requires_user_app_check"], False, "next no app check")
equal(report["next_step"]["requires_new_explicit_authority"], False, "next no authority")
equal(report["next_step"]["stop_after"], False, "continue")
equal(receipt["pass8_result"], "PASS", "receipt Pass 8 result")
equal(receipt["next_safe_move"]["step_id"], "P9-U1", "receipt next")

print(f"PASS: Pass 8 Helper closure certification ({ASSERTIONS}/{ASSERTIONS})")
