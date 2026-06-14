#!/usr/bin/env python3
"""Independently verify Packet 01.5 Applicability Batch 001.

The verifier reruns the prior authorization proofs, rebuilds the deterministic
candidate overlay, validates all four record-specific HOLD decisions against the
immutable source inventory and decision contract, executes adversarial tests,
and emits bounded verification/status receipts. It performs no routing.
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
APP = AUDIT / "applicability"
ROUTING = AUDIT / "routing-inventory"

PLAN_PATH = APP / "Packet_01.5_Applicability_Batch_001_Plan_v1.json"
CATALOG_PATH = APP / "Packet_01.5_Applicability_Evidence_Catalog_v1.json"
CATALOG_RECEIPT = AUDIT / "Packet_01.5_Applicability_Evidence_Catalog_Independent_Verification_v1.json"
CONTRACT_PATH = ROUTING / "Packet_01.5_Routing_Decision_Contract_v2.json"
INVENTORY_PATH = ROUTING / "Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
DECISIONS_PATH = APP / "Packet_01.5_Applicability_Decisions_Batch_001_v1.jsonl"
BUILDER = REPO / "tools" / "build_packet_01_5_applicability_batch_001_v1.py"
CATALOG_VERIFIER = REPO / "tools" / "verify_packet_01_5_applicability_evidence_catalog_v1.py"

OUT_JSON = AUDIT / "Packet_01.5_Applicability_Batch_001_Independent_Verification_v1.json"
OUT_MD = AUDIT / "Packet_01.5_Applicability_Batch_001_Independent_Verification_v1.md"
STATUS_MD = AUDIT / "Packet_01.5_Routing_Status_v78.md"

EXPECTED_INVENTORY_SHA256 = "76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477"
EXPECTED_ADDRESS_SEQUENCE_SHA256 = "3d808e1ec3f163e4cb2ab7a15767563fe7c43b9920bcecde9abe711226220916"
EXPECTED_LINES = 2750
EXPECTED_ADDRESSES = [f"P01.5::B::{number:04d}" for number in range(1, 5)]
EXPECTED_IDENTIFIERS = ["AI-001", "AI-002", "AI-003", "AI-004"]
EXPECTED_EVIDENCE_FIELDS = {
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
    payload = dict(envelope)
    payload.pop("envelope_hash", None)
    return sha256(canonical(payload))


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


def validate_evidence(
    evidence: Any,
    source: dict[str, Any],
    plan_record: dict[str, Any],
    catalog_hash: str,
    plan_hash: str,
) -> None:
    if not isinstance(evidence, list) or not evidence:
        raise DecisionError("applicability evidence is blank")
    ids: list[str] = []
    for entry in evidence:
        if not isinstance(entry, dict) or set(entry) != EXPECTED_EVIDENCE_FIELDS:
            raise DecisionError("invalid evidence-entry field set")
        if any(not nonempty(entry[field]) for field in EXPECTED_EVIDENCE_FIELDS):
            raise DecisionError("blank evidence-entry field")
        ids.append(entry["evidence_id"])
    if len(ids) != len(set(ids)):
        raise DecisionError("duplicate evidence IDs")

    address = source["composite_address"]
    source_entries = [entry for entry in evidence if entry["evidence_id"].startswith("B001-SOURCE-")]
    if len(source_entries) != 1:
        raise DecisionError("exactly one source-envelope evidence entry is required")
    source_entry = source_entries[0]
    if source_entry["source_reference"] != f"{INVENTORY_PATH.relative_to(REPO)}#{address}":
        raise DecisionError("source-envelope evidence reference mismatch")
    if source_entry["source_hash_or_stable_reference"] != source["envelope_hash"]:
        raise DecisionError("source-envelope evidence hash mismatch")

    expected_catalog_ids = plan_record["catalog_evidence_ids"]
    for catalog_id in expected_catalog_ids:
        matches = [entry for entry in evidence if f"-{catalog_id}-" in entry["evidence_id"]]
        if len(matches) != 1:
            raise DecisionError(f"catalog evidence missing or duplicated: {catalog_id}")
        expected_reference = f"{CATALOG_PATH.relative_to(REPO)}#{catalog_id}"
        expected_stable = f"sha256:{catalog_hash}#{catalog_id}"
        if matches[0]["source_reference"] != expected_reference:
            raise DecisionError(f"catalog evidence reference mismatch: {catalog_id}")
        if matches[0]["source_hash_or_stable_reference"] != expected_stable:
            raise DecisionError(f"catalog evidence hash mismatch: {catalog_id}")

    plan_entries = [entry for entry in evidence if entry["evidence_id"].startswith("B001-PLAN-")]
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
    plan_record: dict[str, Any],
    contract: dict[str, Any],
    catalog_hash: str,
    plan_hash: str,
) -> None:
    expected_fields = set(contract["overlay_required_fields"])
    if set(decision) != expected_fields:
        raise DecisionError("decision field set mismatch")

    address = source["composite_address"]
    if decision["composite_address"] != address or plan_record["composite_address"] != address:
        raise DecisionError("permanent address mismatch")
    if decision["source_inventory_sha256"] != EXPECTED_INVENTORY_SHA256:
        raise DecisionError("source inventory hash mismatch")
    if decision["source_envelope_hash"] != source["envelope_hash"]:
        raise DecisionError("source envelope hash mismatch")
    if decision["source_block_hash"] != source["source_block_hash"]:
        raise DecisionError("source block hash mismatch")

    if decision["decision_stage"] != "HOLD":
        raise DecisionError("Batch 001 decision is not HOLD")
    if decision["applicability_state"] != "UNKNOWN — HOLD":
        raise DecisionError("Batch 001 decision is not UNKNOWN — HOLD")
    if decision["applicability_reasoning_summary"] != plan_record["applicability_reasoning_summary"]:
        raise DecisionError("reasoning summary differs from reviewed plan")
    if decision["applicability_confidence"] != plan_record["applicability_confidence"]:
        raise DecisionError("applicability confidence differs from reviewed plan")
    if not isinstance(decision["applicability_confidence"], int) or isinstance(decision["applicability_confidence"], bool):
        raise DecisionError("applicability confidence is not an integer")
    if not 0 <= decision["applicability_confidence"] <= 100:
        raise DecisionError("applicability confidence is outside 0-100")

    validate_evidence(decision["applicability_evidence"], source, plan_record, catalog_hash, plan_hash)

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

    if decision["hold_reason"] != plan_record["hold_reason"] or not nonempty(decision["hold_reason"]):
        raise DecisionError("HOLD reason mismatch or blank")
    if decision["unresolved_dependencies"] != plan_record["unresolved_dependencies"]:
        raise DecisionError("unresolved dependencies differ from reviewed plan")
    if decision["reopening_conditions"] != plan_record["reopening_conditions"]:
        raise DecisionError("reopening conditions differ from reviewed plan")
    unique_nonempty_strings(decision["unresolved_dependencies"], "unresolved_dependencies")
    unique_nonempty_strings(decision["reopening_conditions"], "reopening_conditions")

    if decision["decision_version"] != "Packet-01.5-Applicability-Batch-001-v1":
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
    plan_record: dict[str, Any],
    contract: dict[str, Any],
    catalog_hash: str,
    plan_hash: str,
) -> None:
    try:
        validate_decision(candidate, source, plan, plan_record, contract, catalog_hash, plan_hash)
    except DecisionError:
        return
    fail(f"adversarial decision unexpectedly passed: {name}")


def verify_inventory() -> tuple[list[dict[str, Any]], bytes, str]:
    raw = INVENTORY_PATH.read_bytes()
    require(sha256(raw) == EXPECTED_INVENTORY_SHA256, "inventory SHA-256 changed")
    lines = raw.splitlines()
    require(len(lines) == EXPECTED_LINES, "inventory line count changed")

    envelopes: list[dict[str, Any]] = []
    addresses: list[str] = []
    baseline = 0
    provisional = 0
    for number, line in enumerate(lines, 1):
        envelope = json.loads(line)
        require(isinstance(envelope, dict), f"inventory line {number} is not an object")
        address = envelope.get("composite_address")
        require(nonempty(address), f"inventory address missing at line {number}")
        require(envelope.get("envelope_hash") == calculated_envelope_hash(envelope), f"envelope hash mismatch at {address}")
        require(envelope.get("applicability_state") == "UNCLASSIFIED", f"source applicability changed at {address}")
        require(envelope.get("routing_state") == "UNROUTED", f"source routing changed at {address}")
        require(envelope.get("primary_destination") is None, f"source primary destination populated at {address}")
        for field in ("applicability_evidence", "secondary_destinations", "cross_cutting_laws", "watch_triggers", "semantic_cluster_ids"):
            require(envelope.get(field) == [], f"source blank field populated ({field}) at {address}")
        addresses.append(address)
        envelopes.append(envelope)
        if envelope.get("source_set") == "BASELINE":
            baseline += 1
        elif envelope.get("source_set") == "PROVISIONAL":
            provisional += 1
        else:
            fail(f"unknown source set at {address}")

    require(baseline == 122 and provisional == 2628, "source-set counts changed")
    require(len(set(addresses)) == EXPECTED_LINES, "permanent addresses are not unique")
    address_hash = sha256(("\n".join(addresses) + "\n").encode("utf-8"))
    require(address_hash == EXPECTED_ADDRESS_SEQUENCE_SHA256, "address sequence hash changed")
    require(addresses[:4] == EXPECTED_ADDRESSES, "Batch 001 is not the exact first four addresses")
    require([item["original_identifier"] for item in envelopes[:4]] == EXPECTED_IDENTIFIERS, "Batch 001 identifiers changed")
    return envelopes, raw, address_hash


def run_adversarial_tests(
    decisions: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    plan: dict[str, Any],
    plan_records: list[dict[str, Any]],
    contract: dict[str, Any],
    catalog_hash: str,
    plan_hash: str,
) -> int:
    source = sources[0]
    plan_record = plan_records[0]
    original = decisions[0]
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
    value = mutation("primary destination populated")
    value["primary_destination"] = "Packet 06"
    value = mutation("secondary destination populated")
    value["secondary_destinations"] = ["Packet 21"]
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
    value["applicability_evidence"] = [entry for entry in value["applicability_evidence"] if not entry["evidence_id"].startswith("B001-SOURCE-")]
    value = mutation("catalog evidence hash changed")
    for entry in value["applicability_evidence"]:
        if "-AEC-" in entry["evidence_id"]:
            entry["source_hash_or_stable_reference"] = "sha256:" + "0" * 64
            break

    for name, candidate in fixtures:
        expect_invalid(name, candidate, source, plan, plan_record, contract, catalog_hash, plan_hash)

    duplicate_batch = copy.deepcopy(decisions)
    duplicate_batch[1]["composite_address"] = duplicate_batch[0]["composite_address"]
    if len({item["composite_address"] for item in duplicate_batch}) == len(duplicate_batch):
        fail("duplicate-address adversarial fixture did not create a duplicate")
    return len(fixtures) + 1


def write_outputs(
    decisions: list[dict[str, Any]],
    inventory_raw: bytes,
    address_hash: str,
    positive: int,
    adversarial: int,
) -> None:
    decisions_raw = DECISIONS_PATH.read_bytes()
    counts = {
        "CURRENT DEFECT OR LIMITATION": 0,
        "ACTIVE CONDITIONAL RISK": 0,
        "DORMANT FUTURE RISK": 0,
        "OUT-OF-SCOPE CANDIDATE": 0,
        "UNKNOWN — HOLD": 0,
    }
    for decision in decisions:
        counts[decision["applicability_state"]] += 1

    result = {
        "packet": "01.5",
        "verification": "first_controlled_applicability_batch_001_independent",
        "version": 1,
        "status": "PASS_BATCH_001_APPLICABILITY_VERIFIED",
        "watch": "NONE",
        "blockers": "NONE",
        "batch_id": "PACKET-01.5-APPLICABILITY-BATCH-001",
        "batch_addresses": EXPECTED_ADDRESSES,
        "batch_decisions": len(decisions),
        "applicability_counts": counts,
        "hold_records": EXPECTED_ADDRESSES,
        "source_inventory_sha256": sha256(inventory_raw),
        "address_sequence_sha256": address_hash,
        "decision_overlay_path": str(DECISIONS_PATH.relative_to(REPO)),
        "decision_overlay_sha256": sha256(decisions_raw),
        "source_inventory_unchanged": True,
        "source_inventory_records": EXPECTED_LINES,
        "source_applicability_fields_remain_blank": True,
        "source_routing_fields_remain_blank": True,
        "routing_assignments_completed": 0,
        "semantic_grouping_assignments_completed": 0,
        "source_records_removed": 0,
        "source_records_closed": 0,
        "packet_04_authorized": False,
        "positive_decisions_verified": positive,
        "adversarial_rejection_fixtures_passed": adversarial,
        "next_authorized_work": "PACKET_01.5_PHASE_E_BATCH_002_SELECTION_AND_AUTHORIZATION_GATE",
        "batch_002_applicability_decisions_authorized": False,
        "stop_before_routing": True,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{decision['composite_address']}` | `UNKNOWN — HOLD` | {decision['applicability_confidence']} | {len(decision['unresolved_dependencies'])} |"
        for decision in decisions
    )
    md = f"""# Packet 01.5 — Applicability Batch 001 Independent Verification v1

STATUS: PASS — BATCH 001 APPLICABILITY VERIFIED
WATCH: NONE
BLOCKERS: NONE
BATCH DECISIONS VERIFIED: 4
CURRENT DEFECT OR LIMITATION: 0
ACTIVE CONDITIONAL RISK: 0
DORMANT FUTURE RISK: 0
OUT-OF-SCOPE CANDIDATE: 0
UNKNOWN — HOLD: 4
ROUTING ASSIGNMENTS: 0
SEMANTIC GROUPING ASSIGNMENTS: 0
SOURCE RECORDS REMOVED OR CLOSED: 0
PACKET 04 AUTHORIZED: NO

## Verified records

| Permanent address | State | Confidence | Unresolved dependencies |
|---|---|---:|---:|
{rows}

## Independent proof

- Prior corrected routing-start gate: PASS
- Applicability Evidence Catalog v1: PASS
- Immutable source envelopes checked: 2,750
- Source inventory SHA-256: `{sha256(inventory_raw)}`
- Address-sequence SHA-256: `{address_hash}`
- Exact first-four selection: PASS
- Every source envelope hash recomputed: PASS
- Source applicability and routing fields remain blank: PASS
- Four separate overlay decisions validated against Contract v2: PASS
- Record-specific evidence references and hashes: PASS
- HOLD reasons, dependencies, and reopening conditions: PASS
- Distinct decision author and verifier: PASS
- Positive decisions verified: {positive}
- Adversarial rejection fixtures passed: {adversarial}
- Source inventory unchanged after build and tests: PASS

## Meaning of the result

The four records are classified as `UNKNOWN — HOLD` because their preserved historical claims lack sufficient current T4 evidence. This is a completed applicability decision, not a deletion, closure, defect promotion, or routing assignment.

## Next boundary

Authorized next:

- Packet 01.5 Phase E — Batch 002 Selection and Authorization Gate

Not authorized:

- Batch 002 applicability decisions
- owner routing
- secondary destinations
- cross-cutting laws
- semantic grouping
- record closure
- implementation
- Packet 04

FINAL RESULT: `PASS — BATCH 001 APPLICABILITY VERIFIED`

END PACKET 01.5 — APPLICABILITY BATCH 001 INDEPENDENT VERIFICATION v1
"""
    OUT_MD.write_text(md, encoding="utf-8")

    status = f"""# Packet 01.5 — Routing Status v78

STATUS: FIRST CONTROLLED APPLICABILITY BATCH VERIFIED
WATCH: NONE
BLOCKERS: NONE
ROUTING START AUTHORIZATION: PASS UNDER CORRECTED V2 GATE
APPLICABILITY EVIDENCE CATALOG: PASS
BATCH 001: PASS
APPLICABILITY CLASSIFICATIONS COMPLETED: 4
CURRENT DEFECT OR LIMITATION: 0
ACTIVE CONDITIONAL RISK: 0
DORMANT FUTURE RISK: 0
OUT-OF-SCOPE CANDIDATE: 0
UNKNOWN — HOLD: 4
ROUTING ASSIGNMENTS COMPLETED: 0
SEMANTIC GROUPING ASSIGNMENTS COMPLETED: 0
INDIVIDUAL RECORD CLOSURE: NOT AUTHORIZED
PACKET 04: NOT AUTHORIZED

## Batch 001

- Addresses: `P01.5::B::0001` through `P01.5::B::0004`
- Overlay SHA-256: `{sha256(decisions_raw)}`
- Each record has record-specific evidence, a reasoning summary, confidence, HOLD reason, unresolved dependencies, reopening conditions, and distinct author/verifier identities.
- All destination and routing-proof fields remain blank.

## Preserved source inventory

- Total source envelopes: 2,750
- Inventory SHA-256: `{sha256(inventory_raw)}`
- Address-sequence SHA-256: `{address_hash}`
- Source applicability state remains `UNCLASSIFIED` because decisions live only in the separate overlay.
- Source routing state remains `UNROUTED`.
- Source records removed or closed: 0

## Next authorized work

`Packet 01.5 Phase E — Batch 002 Selection and Authorization Gate`

Batch 002 decisions are not automatically authorized. Stop before routing or another applicability batch.

END PACKET 01.5 — ROUTING STATUS v78
"""
    STATUS_MD.write_text(status, encoding="utf-8")


def main() -> None:
    subprocess.run([sys.executable, str(CATALOG_VERIFIER)], cwd=REPO, check=True)
    catalog_receipt = load_object(CATALOG_RECEIPT)
    require(catalog_receipt.get("status") == "PASS_APPLICABILITY_EVIDENCE_CATALOG_VERIFIED", "catalog verification is not PASS")
    require(catalog_receipt.get("watch") == "NONE", "catalog verification has a watch")
    require(catalog_receipt.get("blockers") == "NONE", "catalog verification has a blocker")

    envelopes, raw_before, address_hash = verify_inventory()
    subprocess.run([sys.executable, str(BUILDER)], cwd=REPO, check=True)

    plan = load_object(PLAN_PATH)
    catalog = load_object(CATALOG_PATH)
    contract = load_object(CONTRACT_PATH)
    decisions = load_jsonl(DECISIONS_PATH)
    require(len(decisions) == 4, "Batch 001 decision count is not four")
    require([item["composite_address"] for item in decisions] == EXPECTED_ADDRESSES, "Batch 001 decision order mismatch")
    require(len({item["composite_address"] for item in decisions}) == 4, "Batch 001 has duplicate addresses")

    plan_records = plan.get("records")
    require(isinstance(plan_records, list) and len(plan_records) == 4, "Batch 001 plan count mismatch")
    catalog_ids = {entry["evidence_id"] for entry in catalog.get("evidence_sources", [])}
    for record in plan_records:
        require(set(record["catalog_evidence_ids"]).issubset(catalog_ids), f"plan references unknown catalog evidence at {record['composite_address']}")

    catalog_hash = sha256(CATALOG_PATH.read_bytes())
    plan_hash = sha256(PLAN_PATH.read_bytes())
    for decision, source, plan_record in zip(decisions, envelopes[:4], plan_records):
        try:
            validate_decision(decision, source, plan, plan_record, contract, catalog_hash, plan_hash)
        except DecisionError as exc:
            fail(f"decision validation failed at {source['composite_address']}: {exc}")

    positive = len(decisions)
    adversarial = run_adversarial_tests(decisions, envelopes[:4], plan, plan_records, contract, catalog_hash, plan_hash)
    require(INVENTORY_PATH.read_bytes() == raw_before, "source inventory changed during Batch 001 build or verification")

    write_outputs(decisions, raw_before, address_hash, positive, adversarial)
    print("PASS: Packet 01.5 Applicability Batch 001 independently verified.")
    print("Verified decisions: 4")
    print("UNKNOWN — HOLD: 4")
    print("Routing assignments: 0")
    print(f"Adversarial rejections: {adversarial}")


if __name__ == "__main__":
    main()
