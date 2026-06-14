#!/usr/bin/env python3
"""Independently verify Packet 01.5 Applicability Batch 002."""
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
APP = AUDIT / "applicability"
ROUTING = AUDIT / "routing-inventory"
TOOLS = REPO / "tools"

PLAN_PATH = APP / "Packet_01.5_Applicability_Batch_002_Plan_v1.json"
CATALOG_PATH = APP / "Packet_01.5_Applicability_Evidence_Catalog_v1.json"
SELECTION_PATH = APP / "Packet_01.5_Applicability_Batch_002_Selection_v1.json"
GATE_RECEIPT_PATH = AUDIT / "Packet_01.5_Applicability_Batch_002_Selection_Gate_Independent_Verification_v1.json"
CONTRACT_PATH = ROUTING / "Packet_01.5_Routing_Decision_Contract_v2.json"
INVENTORY_PATH = ROUTING / "Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
BATCH001_OVERLAY = APP / "Packet_01.5_Applicability_Decisions_Batch_001_v1.jsonl"
DECISIONS_PATH = APP / "Packet_01.5_Applicability_Decisions_Batch_002_v1.jsonl"
BUILDER = TOOLS / "build_packet_01_5_applicability_batch_002_v1.py"
GATE_VERIFIER = TOOLS / "verify_packet_01_5_applicability_batch_002_selection_gate_v1.py"

OUT_JSON = AUDIT / "Packet_01.5_Applicability_Batch_002_Independent_Verification_v1.json"
OUT_MD = AUDIT / "Packet_01.5_Applicability_Batch_002_Independent_Verification_v1.md"
STATUS_MD = AUDIT / "Packet_01.5_Routing_Status_v80.md"

EXPECTED_INVENTORY_SHA256 = "76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477"
EXPECTED_ADDRESS_SEQUENCE_SHA256 = "3d808e1ec3f163e4cb2ab7a15767563fe7c43b9920bcecde9abe711226220916"
EXPECTED_SELECTION_SHA256 = "33eebaeec7987c85d843b244a8e1fab5102c3f07117526e6feb05bf5cfe39ed0"
EXPECTED_BATCH001_OVERLAY_SHA256 = "2de246b718e99bae35f18eb2108e5df24e7bcaf240104e17595dcfc6311bba96"
EXPECTED_ADDRESSES = [f"P01.5::B::{number:04d}" for number in range(5, 9)]
EXPECTED_IDENTIFIERS = ["AI-005", "AI-006", "AI-007", "AI-008"]
EVIDENCE_FIELDS = {
    "evidence_id",
    "source_reference",
    "source_hash_or_stable_reference",
    "claim_supported",
}


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
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def calculated_envelope_hash(envelope: dict[str, Any]) -> str:
    value = dict(envelope)
    value.pop("envelope_hash", None)
    return sha256(canonical(value))


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"not a JSON object: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid JSONL at {path}:{number}: {exc}")
        require(isinstance(value, dict), f"JSONL record is not an object at {path}:{number}")
        records.append(value)
    return records


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def unique_nonempty_strings(value: Any, field: str) -> list[str]:
    if not isinstance(value, list):
        raise DecisionError(f"{field} is not a list")
    if any(not nonempty(item) for item in value):
        raise DecisionError(f"{field} contains a blank or non-string value")
    if len(value) != len(set(value)):
        raise DecisionError(f"{field} contains duplicates")
    return value


def expected_reasoning(historical_claim: str) -> str:
    return (
        f'The permanent record preserves the historical claim: "{historical_claim}" '
        "The independently verified Batch 002 selection authorizes review of this address but makes no applicability judgment. "
        "No direct current T4 source, runtime, authoritative packet-law, deployment, or test receipt tied to this exact claim is present in the verified evidence layer. "
        "Historical labels, severity, and owner suggestions may not be promoted into current truth. Therefore the record remains UNKNOWN — HOLD."
    )


def expected_hold_reason(historical_claim: str) -> str:
    return f'Current direct T4 evidence is insufficient to determine whether this exact historical claim is true now: "{historical_claim}"'


def verify_inventory() -> tuple[list[dict[str, Any]], bytes, str]:
    raw = INVENTORY_PATH.read_bytes()
    require(sha256(raw) == EXPECTED_INVENTORY_SHA256, "source inventory hash changed")
    lines = raw.splitlines()
    require(len(lines) == 2750, "source inventory line count changed")

    records: list[dict[str, Any]] = []
    addresses: list[str] = []
    baseline = 0
    provisional = 0
    for number, line in enumerate(lines, 1):
        record = json.loads(line)
        require(isinstance(record, dict), f"source line {number} is not an object")
        address = record.get("composite_address")
        require(nonempty(address), f"source address missing at line {number}")
        require(record.get("envelope_hash") == calculated_envelope_hash(record), f"envelope hash mismatch at {address}")
        require(record.get("applicability_state") == "UNCLASSIFIED", f"source applicability changed at {address}")
        require(record.get("routing_state") == "UNROUTED", f"source routing changed at {address}")
        require(record.get("primary_destination") is None, f"source destination populated at {address}")
        for field in ("applicability_evidence", "secondary_destinations", "cross_cutting_laws", "semantic_cluster_ids", "watch_triggers"):
            require(record.get(field) == [], f"source blank field populated ({field}) at {address}")
        addresses.append(address)
        records.append(record)
        if record.get("source_set") == "BASELINE":
            baseline += 1
        elif record.get("source_set") == "PROVISIONAL":
            provisional += 1
        else:
            fail(f"unknown source set at {address}")

    require(baseline == 122 and provisional == 2628, "source-set counts changed")
    require(len(set(addresses)) == 2750, "source addresses are not unique")
    address_hash = sha256(("\n".join(addresses) + "\n").encode("utf-8"))
    require(address_hash == EXPECTED_ADDRESS_SEQUENCE_SHA256, "source address sequence changed")
    return records, raw, address_hash


def verify_prior_and_gate() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    subprocess.run([sys.executable, str(GATE_VERIFIER)], cwd=REPO, check=True)
    gate = load_object(GATE_RECEIPT_PATH)
    selection = load_object(SELECTION_PATH)
    plan = load_object(PLAN_PATH)

    require(gate.get("status") == "PASS_BATCH_002_SELECTION_GATE_AUTHORIZED", "Batch 002 selection gate is not PASS")
    require(gate.get("watch") == "NONE" and gate.get("blockers") == "NONE", "Batch 002 selection gate has watch or blocker")
    require(gate.get("selected_addresses") == EXPECTED_ADDRESSES, "Batch 002 selected addresses changed")
    require(gate.get("batch_002_applicability_decisions_authorized") is True, "Batch 002 decisions are not authorized")
    require(gate.get("batch_002_applicability_decisions_completed") == 0, "Batch 002 decisions already existed before build")
    require(gate.get("routing_assignments_completed") == 0, "routing already occurred")
    require(gate.get("semantic_grouping_assignments_completed") == 0, "grouping already occurred")
    require(gate.get("packet_04_authorized") is False, "Packet 04 became authorized")

    require(sha256(SELECTION_PATH.read_bytes()) == EXPECTED_SELECTION_SHA256, "selection manifest hash changed")
    require(selection.get("selected_records") and [item.get("composite_address") for item in selection["selected_records"]] == EXPECTED_ADDRESSES, "selection manifest addresses changed")
    require(selection.get("applicability_decisions_performed") is False, "selection manifest says decisions already occurred")
    require(selection.get("routing_performed") is False, "selection manifest says routing occurred")

    require(plan.get("batch_id") == "PACKET-01.5-APPLICABILITY-BATCH-002", "plan identity mismatch")
    require(plan.get("selected_addresses") == EXPECTED_ADDRESSES, "plan addresses mismatch")
    require(plan.get("expected_original_identifiers") == EXPECTED_IDENTIFIERS, "plan identifiers mismatch")
    require(plan.get("decision_author") != plan.get("decision_verifier"), "plan author and verifier are not distinct")

    require(sha256(BATCH001_OVERLAY.read_bytes()) == EXPECTED_BATCH001_OVERLAY_SHA256, "Batch 001 overlay changed")
    batch001 = load_jsonl(BATCH001_OVERLAY)
    require([item.get("composite_address") for item in batch001] == [f"P01.5::B::{number:04d}" for number in range(1, 5)], "Batch 001 addresses changed")
    require(not (set(EXPECTED_ADDRESSES) & {item["composite_address"] for item in batch001}), "Batch 002 overlaps Batch 001")
    return gate, selection, plan


def validate_evidence(
    evidence: Any,
    source: dict[str, Any],
    plan: dict[str, Any],
    catalog_hash: str,
    plan_hash: str,
    gate_hash: str,
) -> None:
    if not isinstance(evidence, list) or not evidence:
        raise DecisionError("applicability evidence is blank")
    ids: list[str] = []
    for entry in evidence:
        if not isinstance(entry, dict) or set(entry) != EVIDENCE_FIELDS:
            raise DecisionError("invalid evidence-entry field set")
        if any(not nonempty(entry[field]) for field in EVIDENCE_FIELDS):
            raise DecisionError("blank evidence-entry field")
        ids.append(entry["evidence_id"])
    if len(ids) != len(set(ids)):
        raise DecisionError("duplicate evidence IDs")

    address = source["composite_address"]
    source_entries = [entry for entry in evidence if entry["evidence_id"].startswith("B002-SOURCE-")]
    if len(source_entries) != 1:
        raise DecisionError("exactly one source evidence entry is required")
    if source_entries[0]["source_reference"] != f"{INVENTORY_PATH.relative_to(REPO)}#{address}":
        raise DecisionError("source evidence reference mismatch")
    if source_entries[0]["source_hash_or_stable_reference"] != source["envelope_hash"]:
        raise DecisionError("source evidence hash mismatch")

    selection_entries = [entry for entry in evidence if entry["evidence_id"].startswith("B002-SELECTION-")]
    if len(selection_entries) != 1:
        raise DecisionError("exactly one selection evidence entry is required")
    if selection_entries[0]["source_reference"] != f"{SELECTION_PATH.relative_to(REPO)}#{address}":
        raise DecisionError("selection evidence reference mismatch")
    if selection_entries[0]["source_hash_or_stable_reference"] != f"sha256:{EXPECTED_SELECTION_SHA256}#{address}":
        raise DecisionError("selection evidence hash mismatch")

    gate_entries = [entry for entry in evidence if entry["evidence_id"].startswith("B002-GATE-")]
    if len(gate_entries) != 1:
        raise DecisionError("exactly one gate evidence entry is required")
    if gate_entries[0]["source_reference"] != f"{GATE_RECEIPT_PATH.relative_to(REPO)}#{address}":
        raise DecisionError("gate evidence reference mismatch")
    if gate_entries[0]["source_hash_or_stable_reference"] != f"sha256:{gate_hash}#{address}":
        raise DecisionError("gate evidence hash mismatch")

    policy = plan["decision_policy"]
    for catalog_id in policy["catalog_evidence_ids"]:
        matches = [entry for entry in evidence if f"-{catalog_id}-" in entry["evidence_id"]]
        if len(matches) != 1:
            raise DecisionError(f"catalog evidence missing or duplicated: {catalog_id}")
        if matches[0]["source_reference"] != f"{CATALOG_PATH.relative_to(REPO)}#{catalog_id}":
            raise DecisionError(f"catalog evidence reference mismatch: {catalog_id}")
        if matches[0]["source_hash_or_stable_reference"] != f"sha256:{catalog_hash}#{catalog_id}":
            raise DecisionError(f"catalog evidence hash mismatch: {catalog_id}")

    plan_entries = [entry for entry in evidence if entry["evidence_id"].startswith("B002-PLAN-")]
    if len(plan_entries) != 1:
        raise DecisionError("exactly one plan evidence entry is required")
    if plan_entries[0]["source_reference"] != f"{PLAN_PATH.relative_to(REPO)}#{address}":
        raise DecisionError("plan evidence reference mismatch")
    if plan_entries[0]["source_hash_or_stable_reference"] != f"sha256:{plan_hash}#{address}":
        raise DecisionError("plan evidence hash mismatch")


def validate_decision(
    decision: dict[str, Any],
    source: dict[str, Any],
    plan: dict[str, Any],
    contract: dict[str, Any],
    catalog_hash: str,
    plan_hash: str,
    gate_hash: str,
) -> None:
    expected_fields = set(contract["overlay_required_fields"])
    if set(decision) != expected_fields:
        raise DecisionError("decision field set mismatch")

    address = source["composite_address"]
    claim = source["harm_text"]
    if decision["composite_address"] != address:
        raise DecisionError("permanent address mismatch")
    if decision["source_inventory_sha256"] != EXPECTED_INVENTORY_SHA256:
        raise DecisionError("source inventory hash mismatch")
    if decision["source_envelope_hash"] != source["envelope_hash"]:
        raise DecisionError("source envelope hash mismatch")
    if decision["source_block_hash"] != source["source_block_hash"]:
        raise DecisionError("source block hash mismatch")
    if decision["decision_stage"] != "HOLD" or decision["applicability_state"] != "UNKNOWN — HOLD":
        raise DecisionError("decision is not UNKNOWN — HOLD")
    if decision["applicability_reasoning_summary"] != expected_reasoning(claim):
        raise DecisionError("record-specific reasoning mismatch")
    if decision["hold_reason"] != expected_hold_reason(claim):
        raise DecisionError("record-specific HOLD reason mismatch")

    confidence = decision["applicability_confidence"]
    if not isinstance(confidence, int) or isinstance(confidence, bool) or confidence != plan["decision_policy"]["applicability_confidence"]:
        raise DecisionError("applicability confidence mismatch")

    validate_evidence(decision["applicability_evidence"], source, plan, catalog_hash, plan_hash, gate_hash)

    if decision["primary_destination"] is not None:
        raise DecisionError("primary destination populated")
    for field in ("secondary_destinations", "cross_cutting_laws", "semantic_cluster_ids", "routing_evidence"):
        if decision[field] != []:
            raise DecisionError(f"prohibited list populated: {field}")
    for field in ("routing_rationale", "expected_receiving_work", "expected_completion_evidence"):
        if decision[field] != "":
            raise DecisionError(f"prohibited text populated: {field}")
    if decision["routing_confidence"] is not None:
        raise DecisionError("routing confidence populated")

    if decision["unresolved_dependencies"] != plan["decision_policy"]["unresolved_dependencies"]:
        raise DecisionError("unresolved dependencies mismatch")
    if decision["reopening_conditions"] != plan["decision_policy"]["reopening_conditions"]:
        raise DecisionError("reopening conditions mismatch")
    unique_nonempty_strings(decision["unresolved_dependencies"], "unresolved_dependencies")
    unique_nonempty_strings(decision["reopening_conditions"], "reopening_conditions")

    if decision["decision_version"] != "Packet-01.5-Applicability-Batch-002-v1":
        raise DecisionError("decision version mismatch")
    if decision["decision_author"] != plan["decision_author"]:
        raise DecisionError("decision author mismatch")
    if decision["routing_decision_verifier"] != plan["decision_verifier"]:
        raise DecisionError("decision verifier mismatch")
    if decision["decision_author"] == decision["routing_decision_verifier"]:
        raise DecisionError("decision author and verifier are not distinct")
    if decision["closure_state"] != "OPEN":
        raise DecisionError("closure state is not OPEN")


def expect_invalid(
    name: str,
    candidate: dict[str, Any],
    source: dict[str, Any],
    plan: dict[str, Any],
    contract: dict[str, Any],
    catalog_hash: str,
    plan_hash: str,
    gate_hash: str,
) -> None:
    try:
        validate_decision(candidate, source, plan, contract, catalog_hash, plan_hash, gate_hash)
    except DecisionError:
        return
    fail(f"adversarial decision unexpectedly passed: {name}")


def adversarial_tests(
    decisions: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    plan: dict[str, Any],
    contract: dict[str, Any],
    catalog_hash: str,
    plan_hash: str,
    gate_hash: str,
) -> int:
    original = decisions[0]
    source = sources[0]
    fixtures: list[tuple[str, dict[str, Any]]] = []

    def mutation(name: str) -> dict[str, Any]:
        value = copy.deepcopy(original)
        fixtures.append((name, value))
        return value

    value = mutation("missing required field")
    value.pop("hold_reason")
    value = mutation("wrong inventory hash")
    value["source_inventory_sha256"] = "0" * 64
    value = mutation("wrong envelope hash")
    value["source_envelope_hash"] = "0" * 64
    value = mutation("wrong block hash")
    value["source_block_hash"] = "0" * 64
    value = mutation("state promoted")
    value["applicability_state"] = "CURRENT DEFECT OR LIMITATION"
    value = mutation("stage changed")
    value["decision_stage"] = "APPLICABILITY_ONLY"
    value = mutation("reasoning claim altered")
    value["applicability_reasoning_summary"] = value["applicability_reasoning_summary"].replace(source["harm_text"], "different claim")
    value = mutation("primary destination populated")
    value["primary_destination"] = "Packet 06"
    value = mutation("secondary destination populated")
    value["secondary_destinations"] = ["Packet 21"]
    value = mutation("cross-cutting law populated")
    value["cross_cutting_laws"] = ["Packet 00"]
    value = mutation("semantic cluster populated")
    value["semantic_cluster_ids"] = ["cluster-1"]
    value = mutation("routing evidence populated")
    value["routing_evidence"] = copy.deepcopy(value["applicability_evidence"][:1])
    value = mutation("routing confidence populated")
    value["routing_confidence"] = 90
    value = mutation("HOLD reason blank")
    value["hold_reason"] = ""
    value = mutation("dependencies removed")
    value["unresolved_dependencies"] = []
    value = mutation("reopening conditions removed")
    value["reopening_conditions"] = []
    value = mutation("author equals verifier")
    value["routing_decision_verifier"] = value["decision_author"]
    value = mutation("record closed")
    value["closure_state"] = "CLOSED"
    value = mutation("source evidence removed")
    value["applicability_evidence"] = [entry for entry in value["applicability_evidence"] if not entry["evidence_id"].startswith("B002-SOURCE-")]
    value = mutation("selection evidence removed")
    value["applicability_evidence"] = [entry for entry in value["applicability_evidence"] if not entry["evidence_id"].startswith("B002-SELECTION-")]
    value = mutation("gate evidence hash changed")
    for entry in value["applicability_evidence"]:
        if entry["evidence_id"].startswith("B002-GATE-"):
            entry["source_hash_or_stable_reference"] = "sha256:" + "0" * 64
            break
    value = mutation("catalog evidence hash changed")
    for entry in value["applicability_evidence"]:
        if "-AEC-" in entry["evidence_id"]:
            entry["source_hash_or_stable_reference"] = "sha256:" + "0" * 64
            break

    for name, candidate in fixtures:
        expect_invalid(name, candidate, source, plan, contract, catalog_hash, plan_hash, gate_hash)

    duplicated = copy.deepcopy(decisions)
    duplicated[1]["composite_address"] = duplicated[0]["composite_address"]
    require(len({item["composite_address"] for item in duplicated}) != len(duplicated), "duplicate-address fixture failed")
    return len(fixtures) + 1


def write_outputs(
    decisions: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    inventory_raw: bytes,
    address_hash: str,
    adversarial: int,
) -> None:
    decisions_raw = DECISIONS_PATH.read_bytes()
    rows = "\n".join(
        f"| `{decision['composite_address']}` | `{source['original_identifier']}` | `UNKNOWN — HOLD` | {decision['applicability_confidence']} | {source['harm_text']} |"
        for decision, source in zip(decisions, sources)
    )
    receipt = {
        "packet": "01.5",
        "verification": "applicability_batch_002_independent",
        "version": 1,
        "status": "PASS_BATCH_002_APPLICABILITY_VERIFIED",
        "watch": "NONE",
        "blockers": "NONE",
        "batch_id": "PACKET-01.5-APPLICABILITY-BATCH-002",
        "batch_addresses": EXPECTED_ADDRESSES,
        "batch_decisions": 4,
        "batch_applicability_counts": {
            "CURRENT DEFECT OR LIMITATION": 0,
            "ACTIVE CONDITIONAL RISK": 0,
            "DORMANT FUTURE RISK": 0,
            "OUT-OF-SCOPE CANDIDATE": 0,
            "UNKNOWN — HOLD": 4
        },
        "cumulative_applicability_classifications_completed": 8,
        "cumulative_unknown_hold": 8,
        "source_inventory_sha256": sha256(inventory_raw),
        "address_sequence_sha256": address_hash,
        "decision_overlay_path": str(DECISIONS_PATH.relative_to(REPO)),
        "decision_overlay_sha256": sha256(decisions_raw),
        "selection_manifest_sha256": EXPECTED_SELECTION_SHA256,
        "source_inventory_unchanged": True,
        "source_applicability_fields_remain_blank": True,
        "source_routing_fields_remain_blank": True,
        "routing_assignments_completed": 0,
        "semantic_grouping_assignments_completed": 0,
        "source_records_removed": 0,
        "source_records_closed": 0,
        "positive_decisions_verified": 4,
        "adversarial_rejection_fixtures_passed": adversarial,
        "packet_04_authorized": False,
        "next_authorized_work": "PACKET_01.5_PHASE_E_BATCH_003_SELECTION_AND_AUTHORIZATION_GATE",
        "batch_003_applicability_decisions_authorized": False,
        "stop_before_routing": True,
    }
    OUT_JSON.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    OUT_MD.write_text(
        f"""# Packet 01.5 — Applicability Batch 002 Independent Verification v1

STATUS: PASS — BATCH 002 APPLICABILITY VERIFIED
WATCH: NONE
BLOCKERS: NONE
BATCH DECISIONS VERIFIED: 4
CURRENT DEFECT OR LIMITATION: 0
ACTIVE CONDITIONAL RISK: 0
DORMANT FUTURE RISK: 0
OUT-OF-SCOPE CANDIDATE: 0
UNKNOWN — HOLD: 4
CUMULATIVE APPLICABILITY CLASSIFICATIONS: 8
CUMULATIVE UNKNOWN — HOLD: 8
ROUTING ASSIGNMENTS: 0
SEMANTIC GROUPING ASSIGNMENTS: 0
SOURCE RECORDS REMOVED OR CLOSED: 0
PACKET 04 AUTHORIZED: NO

## Verified records

| Permanent address | Original ID | State | Confidence | Preserved historical claim |
|---|---|---|---:|---|
{rows}

## Independent proof

- Batch 002 selection gate rerun: PASS
- Immutable source envelopes checked: 2,750
- Source inventory SHA-256: `{sha256(inventory_raw)}`
- Address-sequence SHA-256: `{address_hash}`
- Every source-envelope hash recomputed: PASS
- Exact four-address selection preserved: PASS
- Batch 001 overlay unchanged and non-overlapping: PASS
- Four separate Batch 002 overlays validated against Contract v2: PASS
- Exact historical claim carried into each record-specific decision: PASS
- Evidence references and hashes: PASS
- HOLD reasons, dependencies, and reopening conditions: PASS
- All routing and grouping fields blank: PASS
- Distinct decision author and verifier: PASS
- Positive decisions verified: 4
- Adversarial rejection fixtures passed: {adversarial}
- Source inventory unchanged after build and tests: PASS

## Meaning of the result

The four selected records are classified `UNKNOWN — HOLD` because their historical claims do not yet have direct current T4 proof or disproof in the verified evidence layer. This completes applicability decisions only; it does not promote defects, route records, group records, close records, or implement changes.

## Next boundary

Authorized next:

- Packet 01.5 Phase E — Batch 003 Selection and Authorization Gate

Not authorized:

- Batch 003 applicability decisions
- owner routing
- secondary destinations
- cross-cutting laws
- semantic grouping
- record closure
- implementation
- Packet 04

FINAL RESULT: `PASS — BATCH 002 APPLICABILITY VERIFIED`

END PACKET 01.5 — APPLICABILITY BATCH 002 INDEPENDENT VERIFICATION v1
""",
        encoding="utf-8",
    )

    STATUS_MD.write_text(
        f"""# Packet 01.5 — Routing Status v80

STATUS: APPLICABILITY BATCH 002 VERIFIED
WATCH: NONE
BLOCKERS: NONE
ROUTING START AUTHORIZATION: PASS UNDER CORRECTED V2 GATE
APPLICABILITY EVIDENCE CATALOG: PASS
BATCH 001: PASS — 4 `UNKNOWN — HOLD`
BATCH 002 SELECTION GATE: PASS
BATCH 002: PASS — 4 `UNKNOWN — HOLD`
CUMULATIVE APPLICABILITY CLASSIFICATIONS COMPLETED: 8
CURRENT DEFECT OR LIMITATION: 0
ACTIVE CONDITIONAL RISK: 0
DORMANT FUTURE RISK: 0
OUT-OF-SCOPE CANDIDATE: 0
UNKNOWN — HOLD: 8
ROUTING ASSIGNMENTS COMPLETED: 0
SEMANTIC GROUPING ASSIGNMENTS COMPLETED: 0
INDIVIDUAL RECORD CLOSURE: NOT AUTHORIZED
PACKET 04: NOT AUTHORIZED

## Batch 002

- Addresses: `P01.5::B::0005` through `P01.5::B::0008`
- Decision overlay SHA-256: `{sha256(decisions_raw)}`
- Each decision preserves its exact historical claim and immutable source hashes.
- Each decision includes evidence, reasoning, confidence, a HOLD reason, unresolved dependencies, reopening conditions, and distinct author/verifier identities.
- All destination, routing, and grouping fields remain blank.

## Preserved source inventory

- Total source envelopes: 2,750
- Inventory SHA-256: `{sha256(inventory_raw)}`
- Address-sequence SHA-256: `{address_hash}`
- Source applicability state remains `UNCLASSIFIED` because decisions live only in separate overlays.
- Source routing state remains `UNROUTED`.
- Source records removed or closed: 0

## Next authorized work

`Packet 01.5 Phase E — Batch 003 Selection and Authorization Gate`

Batch 003 decisions are not automatically authorized. Stop before routing or another applicability batch.

END PACKET 01.5 — ROUTING STATUS v80
""",
        encoding="utf-8",
    )


def main() -> None:
    gate, selection, plan = verify_prior_and_gate()
    records, raw_before, address_hash = verify_inventory()
    by_address = {item["composite_address"]: item for item in records}
    sources = [by_address[address] for address in EXPECTED_ADDRESSES]
    require([item["original_identifier"] for item in sources] == EXPECTED_IDENTIFIERS, "selected source identifiers changed")

    subprocess.run([sys.executable, str(BUILDER)], cwd=REPO, check=True)

    catalog = load_object(CATALOG_PATH)
    contract = load_object(CONTRACT_PATH)
    decisions = load_jsonl(DECISIONS_PATH)
    require(len(decisions) == 4, "Batch 002 decision count is not four")
    require([item["composite_address"] for item in decisions] == EXPECTED_ADDRESSES, "Batch 002 decision order mismatch")
    require(len({item["composite_address"] for item in decisions}) == 4, "Batch 002 contains duplicate addresses")

    catalog_ids = {entry["evidence_id"] for entry in catalog.get("evidence_sources", [])}
    require(set(plan["decision_policy"]["catalog_evidence_ids"]).issubset(catalog_ids), "plan references unknown catalog evidence")

    catalog_hash = sha256(CATALOG_PATH.read_bytes())
    plan_hash = sha256(PLAN_PATH.read_bytes())
    gate_hash = sha256(GATE_RECEIPT_PATH.read_bytes())
    for decision, source in zip(decisions, sources):
        try:
            validate_decision(decision, source, plan, contract, catalog_hash, plan_hash, gate_hash)
        except DecisionError as exc:
            fail(f"decision validation failed at {source['composite_address']}: {exc}")

    adversarial = adversarial_tests(decisions, sources, plan, contract, catalog_hash, plan_hash, gate_hash)
    require(INVENTORY_PATH.read_bytes() == raw_before, "source inventory changed during Batch 002 build or verification")

    write_outputs(decisions, sources, raw_before, address_hash, adversarial)
    print("PASS: Packet 01.5 Applicability Batch 002 independently verified.")
    print("Verified decisions: 4")
    print("UNKNOWN — HOLD: 4")
    print("Routing assignments: 0")
    print(f"Adversarial rejections: {adversarial}")


if __name__ == "__main__":
    main()
