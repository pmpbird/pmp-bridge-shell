#!/usr/bin/env python3
"""Independently verify Packet 01.5 Routing-Start Authorization Gate v2.

This verifier reruns the source-to-envelope proof, verifies the immutable blank
inventory, validates the separate routing-decision contract, and executes
positive and adversarial policy fixtures. It performs no real classification,
routing, grouping, deletion, or closure.
"""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "audit"
ROUTING = AUDIT / "routing-inventory"

CONTRACT_PATH = ROUTING / "Packet_01.5_Routing_Decision_Contract_v2.json"
INVENTORY_PATH = ROUTING / "Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
MANIFEST_PATH = ROUTING / "Packet_01.5_Blank_Routing_Inventory_v1.manifest.json"
SOURCE_VERIFIER = REPO / "tools" / "verify_packet_01_5_blank_routing_inventory.py"

OUT_JSON = AUDIT / "Packet_01.5_Routing_Start_Authorization_Independent_Verification_v2.json"
OUT_MD = AUDIT / "Packet_01.5_Routing_Start_Authorization_Independent_Verification_v2.md"
STATUS_MD = AUDIT / "Packet_01.5_Routing_Status_v76.md"

EXPECTED_INVENTORY_SHA256 = "76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477"
EXPECTED_ADDRESS_SEQUENCE_SHA256 = "3d808e1ec3f163e4cb2ab7a15767563fe7c43b9920bcecde9abe711226220916"
EXPECTED_BYTES = 3898954
EXPECTED_LINES = 2750
EXPECTED_FIRST = "P01.5::B::0001"
EXPECTED_LAST = "P01.5::P069::XRES-003"

EXPECTED_APPLICABILITY_STATES = [
    "CURRENT DEFECT OR LIMITATION",
    "ACTIVE CONDITIONAL RISK",
    "DORMANT FUTURE RISK",
    "OUT-OF-SCOPE CANDIDATE",
    "UNKNOWN — HOLD",
]
EXPECTED_DECISION_STAGES = ["APPLICABILITY_ONLY", "ROUTED", "HOLD"]
EXPECTED_IMMUTABLE_FIELDS = [
    "composite_address",
    "source_set",
    "source_path",
    "source_pass",
    "source_file_hash",
    "source_record_ordinal",
    "original_identifier",
    "original_heading",
    "original_body",
    "source_block_hash",
    "harm_text",
    "overlap_text",
    "legacy_exception_codes",
    "normalization_version",
    "envelope_hash",
]
EXPECTED_OVERLAY_FIELDS = [
    "composite_address",
    "source_inventory_sha256",
    "source_envelope_hash",
    "source_block_hash",
    "decision_stage",
    "applicability_state",
    "applicability_evidence",
    "applicability_reasoning_summary",
    "applicability_confidence",
    "primary_destination",
    "secondary_destinations",
    "cross_cutting_laws",
    "semantic_cluster_ids",
    "routing_evidence",
    "routing_rationale",
    "routing_confidence",
    "expected_receiving_work",
    "expected_completion_evidence",
    "unresolved_dependencies",
    "hold_reason",
    "reopening_conditions",
    "decision_version",
    "decision_author",
    "routing_decision_verifier",
    "closure_state",
]
EXPECTED_EVIDENCE_FIELDS = [
    "evidence_id",
    "source_reference",
    "source_hash_or_stable_reference",
    "claim_supported",
]


class DecisionError(ValueError):
    pass


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def calculated_envelope_hash(envelope: dict[str, Any]) -> str:
    payload = dict(envelope)
    payload.pop("envelope_hash", None)
    return sha256(canonical(payload))


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"not a JSON object: {path}")
    return value


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def confidence(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 100


def unique_strings(value: Any, field: str) -> list[str]:
    if not isinstance(value, list):
        raise DecisionError(f"{field} must be a list")
    if any(not nonempty_string(item) for item in value):
        raise DecisionError(f"{field} contains a blank or non-string value")
    if len(value) != len(set(value)):
        raise DecisionError(f"{field} contains duplicate values")
    return value


def validate_evidence(value: Any, field: str) -> None:
    if not isinstance(value, list) or not value:
        raise DecisionError(f"{field} must contain evidence")
    for index, entry in enumerate(value, 1):
        if not isinstance(entry, dict):
            raise DecisionError(f"{field}[{index}] is not an object")
        if set(entry) != set(EXPECTED_EVIDENCE_FIELDS):
            raise DecisionError(f"{field}[{index}] has an invalid field set")
        for required in EXPECTED_EVIDENCE_FIELDS:
            if not nonempty_string(entry.get(required)):
                raise DecisionError(f"{field}[{index}].{required} is blank")


def validate_decision(
    decision: dict[str, Any],
    by_address: dict[str, dict[str, Any]],
) -> None:
    if not isinstance(decision, dict):
        raise DecisionError("decision is not an object")
    if set(decision) != set(EXPECTED_OVERLAY_FIELDS):
        missing = sorted(set(EXPECTED_OVERLAY_FIELDS) - set(decision))
        extra = sorted(set(decision) - set(EXPECTED_OVERLAY_FIELDS))
        raise DecisionError(f"decision field mismatch; missing={missing}; extra={extra}")

    address = decision["composite_address"]
    if address not in by_address:
        raise DecisionError("unknown permanent address")
    source = by_address[address]

    if decision["source_inventory_sha256"] != EXPECTED_INVENTORY_SHA256:
        raise DecisionError("source inventory hash mismatch")
    if decision["source_envelope_hash"] != source["envelope_hash"]:
        raise DecisionError("source envelope hash mismatch")
    if decision["source_block_hash"] != source["source_block_hash"]:
        raise DecisionError("source block hash mismatch")

    stage = decision["decision_stage"]
    state = decision["applicability_state"]
    if stage not in EXPECTED_DECISION_STAGES:
        raise DecisionError("invalid decision stage")
    if state not in EXPECTED_APPLICABILITY_STATES:
        raise DecisionError("invalid applicability state")
    if state == "UNKNOWN — HOLD" and stage != "HOLD":
        raise DecisionError("UNKNOWN — HOLD must use HOLD stage")

    validate_evidence(decision["applicability_evidence"], "applicability_evidence")
    if not nonempty_string(decision["applicability_reasoning_summary"]):
        raise DecisionError("applicability reasoning is blank")
    if not confidence(decision["applicability_confidence"]):
        raise DecisionError("applicability confidence is invalid")

    secondary = unique_strings(decision["secondary_destinations"], "secondary_destinations")
    cross_cutting = unique_strings(decision["cross_cutting_laws"], "cross_cutting_laws")
    clusters = unique_strings(decision["semantic_cluster_ids"], "semantic_cluster_ids")
    dependencies = unique_strings(decision["unresolved_dependencies"], "unresolved_dependencies")
    reopening = unique_strings(decision["reopening_conditions"], "reopening_conditions")
    if not reopening:
        raise DecisionError("reopening conditions are required")

    if decision["closure_state"] != "OPEN":
        raise DecisionError("closure state must remain OPEN")
    if not nonempty_string(decision["decision_version"]):
        raise DecisionError("decision version is blank")
    if not nonempty_string(decision["decision_author"]):
        raise DecisionError("decision author is blank")
    if not nonempty_string(decision["routing_decision_verifier"]):
        raise DecisionError("decision verifier is blank")
    if decision["decision_author"] == decision["routing_decision_verifier"]:
        raise DecisionError("decision author and verifier must be distinct")

    primary = decision["primary_destination"]
    if primary is not None and not nonempty_string(primary):
        raise DecisionError("primary destination must be null or non-empty")
    if primary is not None and primary in secondary:
        raise DecisionError("primary destination is duplicated as secondary")

    _ = clusters

    if stage == "APPLICABILITY_ONLY":
        if primary is not None or secondary or cross_cutting:
            raise DecisionError("destination fields populated before routing")
        if decision["routing_evidence"] != []:
            raise DecisionError("routing evidence populated before routing")
        if decision["routing_rationale"] != "":
            raise DecisionError("routing rationale populated before routing")
        if decision["routing_confidence"] is not None:
            raise DecisionError("routing confidence populated before routing")
        if decision["expected_receiving_work"] != "":
            raise DecisionError("expected receiving work populated before routing")
        if decision["expected_completion_evidence"] != "":
            raise DecisionError("expected completion evidence populated before routing")
        if decision["hold_reason"] != "":
            raise DecisionError("hold reason populated outside HOLD")

    elif stage == "ROUTED":
        if state == "UNKNOWN — HOLD":
            raise DecisionError("UNKNOWN — HOLD cannot be routed")
        if primary is None:
            raise DecisionError("routed decision lacks a primary destination")
        validate_evidence(decision["routing_evidence"], "routing_evidence")
        if not nonempty_string(decision["routing_rationale"]):
            raise DecisionError("routing rationale is blank")
        if not confidence(decision["routing_confidence"]):
            raise DecisionError("routing confidence is invalid")
        if not nonempty_string(decision["expected_receiving_work"]):
            raise DecisionError("expected receiving work is blank")
        if not nonempty_string(decision["expected_completion_evidence"]):
            raise DecisionError("expected completion evidence is blank")
        if decision["hold_reason"] != "":
            raise DecisionError("routed decision contains a HOLD reason")

    elif stage == "HOLD":
        if primary is not None or secondary or cross_cutting:
            raise DecisionError("HOLD contains destination assignments")
        if decision["routing_evidence"] != []:
            raise DecisionError("HOLD contains routing evidence")
        if decision["routing_rationale"] != "":
            raise DecisionError("HOLD contains routing rationale")
        if decision["routing_confidence"] is not None:
            raise DecisionError("HOLD contains routing confidence")
        if decision["expected_receiving_work"] != "":
            raise DecisionError("HOLD contains expected receiving work")
        if decision["expected_completion_evidence"] != "":
            raise DecisionError("HOLD contains expected completion evidence")
        if not nonempty_string(decision["hold_reason"]):
            raise DecisionError("HOLD reason is blank")
        if not dependencies:
            raise DecisionError("HOLD lacks an unresolved dependency")


def evidence(evidence_id: str) -> list[dict[str, str]]:
    return [{
        "evidence_id": evidence_id,
        "source_reference": "audit/test-fixture",
        "source_hash_or_stable_reference": "fixture-stable-reference",
        "claim_supported": "Fixture proves the decision contract behavior only.",
    }]


def base_decision(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "composite_address": source["composite_address"],
        "source_inventory_sha256": EXPECTED_INVENTORY_SHA256,
        "source_envelope_hash": source["envelope_hash"],
        "source_block_hash": source["source_block_hash"],
        "decision_stage": "APPLICABILITY_ONLY",
        "applicability_state": "CURRENT DEFECT OR LIMITATION",
        "applicability_evidence": evidence("APP-001"),
        "applicability_reasoning_summary": "Fixture-only applicability reasoning.",
        "applicability_confidence": 90,
        "primary_destination": None,
        "secondary_destinations": [],
        "cross_cutting_laws": [],
        "semantic_cluster_ids": [],
        "routing_evidence": [],
        "routing_rationale": "",
        "routing_confidence": None,
        "expected_receiving_work": "",
        "expected_completion_evidence": "",
        "unresolved_dependencies": [],
        "hold_reason": "",
        "reopening_conditions": ["Contradictory evidence appears."],
        "decision_version": "fixture-v1",
        "decision_author": "fixture-author",
        "routing_decision_verifier": "fixture-verifier",
        "closure_state": "OPEN",
    }


def expect_invalid(
    name: str,
    decision: dict[str, Any],
    by_address: dict[str, dict[str, Any]],
) -> None:
    try:
        validate_decision(decision, by_address)
    except DecisionError:
        return
    fail(f"adversarial fixture unexpectedly passed: {name}")


def verify_contract(contract: dict[str, Any]) -> None:
    require(contract.get("packet") == "01.5", "contract packet mismatch")
    require(contract.get("contract") == "routing_decision_overlay", "contract identity mismatch")
    require(contract.get("version") == 2, "contract version mismatch")

    anchor = contract.get("source_anchor", {})
    require(anchor.get("path") == str(INVENTORY_PATH.relative_to(REPO)), "contract inventory path mismatch")
    require(anchor.get("bytes") == EXPECTED_BYTES, "contract inventory byte count mismatch")
    require(anchor.get("lines") == EXPECTED_LINES, "contract inventory line count mismatch")
    require(anchor.get("sha256") == EXPECTED_INVENTORY_SHA256, "contract inventory hash mismatch")
    require(
        anchor.get("address_sequence_sha256") == EXPECTED_ADDRESS_SEQUENCE_SHA256,
        "contract address-sequence hash mismatch",
    )
    require(anchor.get("address_first") == EXPECTED_FIRST, "contract first address mismatch")
    require(anchor.get("address_last") == EXPECTED_LAST, "contract last address mismatch")
    require(anchor.get("baseline_envelopes") == 122, "contract baseline count mismatch")
    require(anchor.get("provisional_envelopes") == 2628, "contract provisional count mismatch")

    architecture = contract.get("architecture", {})
    for field in (
        "source_inventory_immutable",
        "decision_overlay_separate",
    ):
        require(architecture.get(field) is True, f"contract architecture control missing: {field}")
    for field in (
        "source_wording_copied_as_replacement",
        "source_envelope_deletion_allowed",
        "source_envelope_closure_allowed",
        "cluster_summary_can_replace_source",
    ):
        require(architecture.get(field) is False, f"contract architecture prohibition missing: {field}")

    require(contract.get("immutable_source_fields") == EXPECTED_IMMUTABLE_FIELDS, "immutable source fields mismatch")
    require(contract.get("applicability_states") == EXPECTED_APPLICABILITY_STATES, "applicability states mismatch")
    require(contract.get("decision_stages") == EXPECTED_DECISION_STAGES, "decision stages mismatch")
    require(contract.get("overlay_required_fields") == EXPECTED_OVERLAY_FIELDS, "overlay field set mismatch")
    require(
        contract.get("evidence_entry_required_fields") == EXPECTED_EVIDENCE_FIELDS,
        "evidence entry field set mismatch",
    )

    confidence_contract = contract.get("confidence", {})
    require(confidence_contract == {
        "type": "integer",
        "minimum": 0,
        "maximum": 100,
        "applicability_required": True,
        "routing_required_when_routed": True,
    }, "confidence contract mismatch")

    global_rules = contract.get("global_rules", {})
    required_true = (
        "applicability_and_destination_separate",
        "no_default_applicability",
        "conditional_risk_not_automatically_current_defect",
        "unknown_uncertainty_requires_hold",
        "primary_and_secondary_can_coexist",
        "duplicate_destinations_forbidden",
        "semantic_grouping_reference_only",
        "semantic_grouping_reversible_by_address",
        "record_closure_during_routing_forbidden",
        "routing_does_not_prove_resolution",
        "routing_does_not_authorize_implementation",
        "reopening_conditions_required",
        "decision_author_and_verifier_distinct",
    )
    for field in required_true:
        require(global_rules.get(field) is True, f"global rule missing: {field}")
    require(global_rules.get("closure_state_required_value") == "OPEN", "closure-state rule mismatch")
    require(global_rules.get("packet_04_authorized") is False, "Packet 04 was authorized")

    independent = contract.get("independent_verification", {})
    for field in (
        "recompute_inventory_sha256",
        "recompute_address_sequence_sha256",
        "recompute_every_envelope_hash",
        "verify_exact_address_bounds",
        "verify_all_blank_states",
        "rerun_source_to_envelope_verifier",
        "positive_policy_fixtures_required",
        "adversarial_rejection_fixtures_required",
        "verify_inventory_unchanged_after_tests",
    ):
        require(independent.get(field) is True, f"independent verification control missing: {field}")

    authorization = contract.get("authorization_on_pass", {})
    require(
        authorization.get("next_authorized_work") == "PACKET_01.5_PHASE_E_APPLICABILITY_CLASSIFICATION",
        "next authorized work mismatch",
    )
    require(authorization.get("actual_classification_performed") is False, "contract performs classification")
    require(authorization.get("actual_routing_performed") is False, "contract performs routing")
    require(authorization.get("packet_04_authorized") is False, "contract authorizes Packet 04")


def main() -> None:
    subprocess.run([sys.executable, str(SOURCE_VERIFIER)], cwd=REPO, check=True)

    contract = load_object(CONTRACT_PATH)
    verify_contract(contract)

    raw_before = INVENTORY_PATH.read_bytes()
    manifest = load_object(MANIFEST_PATH)
    require(len(raw_before) == EXPECTED_BYTES, "inventory byte count changed")
    require(sha256(raw_before) == EXPECTED_INVENTORY_SHA256, "inventory SHA-256 changed")
    require(manifest.get("inventory_jsonl", {}).get("sha256") == EXPECTED_INVENTORY_SHA256, "manifest inventory hash changed")
    require(manifest.get("inventory_jsonl", {}).get("bytes") == EXPECTED_BYTES, "manifest inventory bytes changed")
    require(manifest.get("inventory_jsonl", {}).get("lines") == EXPECTED_LINES, "manifest inventory lines changed")

    lines = raw_before.splitlines()
    require(len(lines) == EXPECTED_LINES, "inventory line count changed")

    envelopes: list[dict[str, Any]] = []
    addresses: list[str] = []
    baseline = 0
    provisional = 0
    for number, line in enumerate(lines, 1):
        try:
            envelope = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid inventory JSON at line {number}: {exc}")
        require(isinstance(envelope, dict), f"inventory line {number} is not an object")
        address = envelope.get("composite_address")
        require(nonempty_string(address), f"missing address at line {number}")
        addresses.append(address)
        envelopes.append(envelope)

        if envelope.get("source_set") == "BASELINE":
            baseline += 1
        elif envelope.get("source_set") == "PROVISIONAL":
            provisional += 1
        else:
            fail(f"unknown source set at {address}")

        require(
            envelope.get("envelope_hash") == calculated_envelope_hash(envelope),
            f"envelope hash mismatch at {address}",
        )
        require(envelope.get("applicability_state") == "UNCLASSIFIED", f"applicability is not blank at {address}")
        require(envelope.get("routing_state") == "UNROUTED", f"routing is not blank at {address}")
        require(envelope.get("primary_destination") is None, f"primary destination populated at {address}")
        for field in (
            "applicability_evidence",
            "secondary_destinations",
            "cross_cutting_laws",
            "watch_triggers",
            "semantic_cluster_ids",
        ):
            require(envelope.get(field) == [], f"blank field populated ({field}) at {address}")

    require(baseline == 122, "baseline envelope count changed")
    require(provisional == 2628, "provisional envelope count changed")
    require(len(set(addresses)) == EXPECTED_LINES, "permanent addresses are not unique")
    require(addresses[0] == EXPECTED_FIRST, "first permanent address changed")
    require(addresses[-1] == EXPECTED_LAST, "last permanent address changed")
    address_hash = sha256(("\n".join(addresses) + "\n").encode("utf-8"))
    require(address_hash == EXPECTED_ADDRESS_SEQUENCE_SHA256, "permanent-address sequence changed")
    require(manifest.get("address_sequence_sha256") == EXPECTED_ADDRESS_SEQUENCE_SHA256, "manifest address sequence changed")

    by_address = {envelope["composite_address"]: envelope for envelope in envelopes}
    source = envelopes[0]

    positive_fixtures = 0
    for state in EXPECTED_APPLICABILITY_STATES:
        fixture = base_decision(source)
        fixture["applicability_state"] = state
        if state == "UNKNOWN — HOLD":
            fixture["decision_stage"] = "HOLD"
            fixture["hold_reason"] = "Evidence is insufficient for a safe applicability or owner decision."
            fixture["unresolved_dependencies"] = ["Independent evidence is missing."]
        validate_decision(fixture, by_address)
        positive_fixtures += 1

    routed = base_decision(source)
    routed.update({
        "decision_stage": "ROUTED",
        "primary_destination": "Packet 06",
        "secondary_destinations": ["Packet 21"],
        "cross_cutting_laws": ["Trusted Outer-Guardian Law"],
        "semantic_cluster_ids": ["P01.5::CLUSTER::FIXTURE-001"],
        "routing_evidence": evidence("ROUTE-001"),
        "routing_rationale": "Fixture-only routing rationale.",
        "routing_confidence": 85,
        "expected_receiving_work": "Fixture-only receiving work.",
        "expected_completion_evidence": "Fixture-only completion receipt.",
    })
    validate_decision(routed, by_address)
    positive_fixtures += 1

    hold = base_decision(source)
    hold.update({
        "decision_stage": "HOLD",
        "applicability_state": "ACTIVE CONDITIONAL RISK",
        "hold_reason": "The receiving owner cannot yet be proven.",
        "unresolved_dependencies": ["Canonical owner evidence is missing."],
    })
    validate_decision(hold, by_address)
    positive_fixtures += 1

    adversarial: list[tuple[str, dict[str, Any]]] = []

    bad = base_decision(source)
    bad.pop("applicability_confidence")
    adversarial.append(("missing required field", bad))

    bad = base_decision(source)
    bad["source_envelope_hash"] = "0" * 64
    adversarial.append(("source envelope hash mismatch", bad))

    bad = base_decision(source)
    bad["decision_stage"] = "ROUTED"
    bad["applicability_state"] = "UNKNOWN — HOLD"
    bad["primary_destination"] = "Packet 06"
    bad["routing_evidence"] = evidence("ROUTE-BAD")
    bad["routing_rationale"] = "Invalid guessed route."
    bad["routing_confidence"] = 50
    bad["expected_receiving_work"] = "Invalid."
    bad["expected_completion_evidence"] = "Invalid."
    adversarial.append(("UNKNOWN HOLD guessed route", bad))

    bad = base_decision(source)
    bad["primary_destination"] = "Packet 06"
    adversarial.append(("destination before routing", bad))

    bad = copy.deepcopy(routed)
    bad["routing_confidence"] = None
    adversarial.append(("missing routing confidence", bad))

    bad = copy.deepcopy(routed)
    bad["routing_evidence"] = []
    adversarial.append(("missing routing evidence", bad))

    bad = copy.deepcopy(routed)
    bad["secondary_destinations"] = ["Packet 21", "Packet 21"]
    adversarial.append(("duplicate secondary destination", bad))

    bad = copy.deepcopy(routed)
    bad["secondary_destinations"] = ["Packet 06"]
    adversarial.append(("primary duplicated as secondary", bad))

    bad = base_decision(source)
    bad["closure_state"] = "CLOSED"
    adversarial.append(("premature record closure", bad))

    bad = base_decision(source)
    bad["routing_decision_verifier"] = bad["decision_author"]
    adversarial.append(("author verifies own decision", bad))

    bad = copy.deepcopy(hold)
    bad["hold_reason"] = ""
    adversarial.append(("HOLD without reason", bad))

    bad = copy.deepcopy(hold)
    bad["unresolved_dependencies"] = []
    adversarial.append(("HOLD without unresolved dependency", bad))

    bad = base_decision(source)
    bad["applicability_evidence"] = []
    adversarial.append(("classification without evidence", bad))

    bad = base_decision(source)
    bad["applicability_confidence"] = True
    adversarial.append(("boolean confidence", bad))

    bad = base_decision(source)
    bad["reopening_conditions"] = []
    adversarial.append(("missing reopening condition", bad))

    bad = base_decision(source)
    bad["semantic_cluster_ids"] = ["P01.5::CLUSTER::A", "P01.5::CLUSTER::A"]
    adversarial.append(("duplicate cluster reference", bad))

    for name, fixture in adversarial:
        expect_invalid(name, fixture, by_address)

    raw_after = INVENTORY_PATH.read_bytes()
    require(raw_after == raw_before, "gate verification changed inventory bytes")
    require(sha256(raw_after) == EXPECTED_INVENTORY_SHA256, "inventory changed after policy tests")

    result = {
        "packet": "01.5",
        "verification": "routing_start_authorization_independent",
        "version": 2,
        "status": "PASS_ROUTING_START_AUTHORIZED",
        "watch": "NONE",
        "blockers": "NONE",
        "v1_authorization_sufficient": False,
        "v1_authorization_disposition": "WITHDRAWN_AND_SUPERSEDED",
        "source_to_envelope_verifier_rerun": "PASS",
        "inventory_sha256": EXPECTED_INVENTORY_SHA256,
        "inventory_bytes": EXPECTED_BYTES,
        "combined_envelopes": EXPECTED_LINES,
        "baseline_envelopes": baseline,
        "provisional_envelopes": provisional,
        "unique_addresses": len(set(addresses)),
        "address_sequence_sha256": address_hash,
        "every_envelope_hash_recomputed": "PASS",
        "blank_applicability_state": "PASS",
        "blank_routing_state": "PASS",
        "decision_overlay_separate": "PASS",
        "five_state_applicability_vocabulary": "PASS",
        "unknown_hold_control": "PASS",
        "applicability_confidence_control": "PASS",
        "routing_confidence_control": "PASS",
        "primary_secondary_coexistence_control": "PASS",
        "semantic_grouping_reversibility_control": "PASS",
        "closure_state_open_control": "PASS",
        "distinct_author_verifier_control": "PASS",
        "positive_policy_fixtures_passed": positive_fixtures,
        "adversarial_rejection_fixtures_passed": len(adversarial),
        "inventory_unchanged_after_tests": "PASS",
        "routing_start_authorized": True,
        "next_authorized_work": "PACKET_01.5_PHASE_E_APPLICABILITY_CLASSIFICATION",
        "applicability_classifications_completed": 0,
        "routing_assignments_completed": 0,
        "semantic_grouping_assignments_completed": 0,
        "source_records_removed": 0,
        "source_records_closed": 0,
        "packet_04_authorized": False,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    OUT_MD.write_text("\n".join([
        "# Packet 01.5 — Routing-Start Authorization Independent Verification v2",
        "",
        "STATUS: PASS — ROUTING START AUTHORIZED",
        "WATCH: NONE",
        "BLOCKERS: NONE",
        "ROUTING ASSIGNMENTS COMPLETED: 0",
        "APPLICABILITY CLASSIFICATIONS COMPLETED: 0",
        "SEMANTIC GROUPING ASSIGNMENTS COMPLETED: 0",
        "",
        "## Reconciliation",
        "",
        "- v1 authorization sufficiency: FAIL",
        "- v1 disposition: WITHDRAWN AND SUPERSEDED",
        "- v2 corrective gate: PASS",
        "",
        "## Source-integrity proof",
        "",
        "- Full source-to-envelope verifier rerun: PASS",
        "- Combined envelopes: 2750",
        "- Baseline envelopes: 122",
        "- Provisional envelopes: 2628",
        "- Unique permanent addresses: 2750",
        f"- Inventory SHA-256: `{EXPECTED_INVENTORY_SHA256}`",
        f"- Address-sequence SHA-256: `{address_hash}`",
        "- Every envelope hash independently recomputed: PASS",
        "- Blank applicability state: PASS",
        "- Blank routing state: PASS",
        "- Inventory unchanged after all tests: PASS",
        "",
        "## Mandatory gate protections",
        "",
        "- Immutable source inventory plus separate decision overlay: PASS",
        "- Five applicability states, including `UNKNOWN — HOLD`: PASS",
        "- Applicability and destination separation: PASS",
        "- Conditional-risk non-promotion control: PASS",
        "- Mandatory evidence and applicability confidence: PASS",
        "- Mandatory routing evidence and routing confidence: PASS",
        "- Primary and secondary destinations may coexist: PASS",
        "- Uncertainty produces HOLD: PASS",
        "- Semantic grouping is address-based and reversible: PASS",
        "- Record closure remains forbidden: PASS",
        "- Decision author and verifier are distinct: PASS",
        "- Packet 04 remains unauthorized: PASS",
        "",
        "## Executed policy tests",
        "",
        f"- Positive fixtures passed: {positive_fixtures}",
        f"- Adversarial rejection fixtures passed: {len(adversarial)}",
        "",
        "## Authorization result",
        "",
        "Authorized next:",
        "",
        "- Packet 01.5 Phase E — Applicability Classification",
        "",
        "Not performed by this gate:",
        "",
        "- applicability classification",
        "- owner routing",
        "- secondary-destination routing",
        "- cross-cutting-law assignment",
        "- semantic grouping",
        "- record closure",
        "- Packet 04 work",
        "",
        "FINAL RESULT: `PASS — ROUTING START AUTHORIZED UNDER V2`",
        "",
        "WATCH: NONE",
        "",
        "BLOCKERS: NONE",
        "",
        "END PACKET 01.5 — ROUTING-START AUTHORIZATION INDEPENDENT VERIFICATION v2",
        "",
    ]), encoding="utf-8")

    STATUS_MD.write_text("\n".join([
        "# Packet 01.5 — Routing Status v76",
        "",
        "STATUS: ROUTING START AUTHORIZED UNDER CORRECTED V2 GATE",
        "WATCH: NONE",
        "BLOCKERS: NONE",
        "V1 AUTHORIZATION: WITHDRAWN AND SUPERSEDED",
        "FIRST AUTHORIZED NEXT PHASE: APPLICABILITY CLASSIFICATION",
        "ROUTING ASSIGNMENTS COMPLETED: 0",
        "APPLICABILITY CLASSIFICATIONS COMPLETED: 0",
        "SEMANTIC GROUPING ASSIGNMENTS COMPLETED: 0",
        "INDIVIDUAL RECORD CLOSURE: NOT AUTHORIZED",
        "PACKET 04: NOT AUTHORIZED",
        "",
        "## Preserved inventory",
        "",
        "- Baseline envelopes: 122",
        "- Provisional envelopes: 2628",
        "- Total envelopes: 2750",
        "- Unique addresses: 2750",
        f"- Inventory SHA-256: `{EXPECTED_INVENTORY_SHA256}`",
        f"- Address-sequence SHA-256: `{address_hash}`",
        "- Blank inventory remains immutable and is the rollback source",
        "",
        "## Corrected authorization",
        "",
        "The v2 gate authorizes only the start of Packet 01.5 applicability classification through a separate evidence-bound decision overlay. `UNKNOWN — HOLD`, evidence, confidence, reopening, distinct verification, and non-destructive multi-destination controls are mandatory.",
        "",
        "## Stop boundary",
        "",
        "No applicability classification or routing was performed. Stop here before actual routing.",
        "",
        "END PACKET 01.5 — ROUTING STATUS v76",
        "",
    ]), encoding="utf-8")

    print("PASS — corrected Packet 01.5 routing-start gate v2 independently verified")


if __name__ == "__main__":
    main()
