#!/usr/bin/env python3
"""Verify the reusable Packet 01.5 scalable applicability-processing gate."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "audit"
APP = AUDIT / "applicability"
ROUTING = AUDIT / "routing-inventory"

GATE_PATH = APP / "Packet_01.5_Scalable_Applicability_Processing_Gate_v1.json"
INVENTORY_PATH = ROUTING / "Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
STATUS_V81 = AUDIT / "Packet_01.5_Routing_Status_v81.md"
BATCH001_OVERLAY = APP / "Packet_01.5_Applicability_Decisions_Batch_001_v1.jsonl"
BATCH002_OVERLAY = APP / "Packet_01.5_Applicability_Decisions_Batch_002_v1.jsonl"
BATCH003_GATE = AUDIT / "Packet_01.5_Applicability_Batch_003_Selection_Gate_Independent_Verification_v1.json"
OUT_JSON = AUDIT / "Packet_01.5_Scalable_Applicability_Gate_Independent_Verification_v1.json"
OUT_MD = AUDIT / "Packet_01.5_Scalable_Applicability_Gate_Independent_Verification_v1.md"
STATUS_V82 = AUDIT / "Packet_01.5_Routing_Status_v82.md"

INV_SHA = "76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477"
ADDR_SHA = "3d808e1ec3f163e4cb2ab7a15767563fe7c43b9920bcecde9abe711226220916"
B1_SHA = "2de246b718e99bae35f18eb2108e5df24e7bcaf240104e17595dcfc6311bba96"
B2_SHA = "8d629e824d29ab4549e2132a6401c10049d7a3c1476b66dfd52c2dc8849d1000"
FIRST = "P01.5::B::0001"
LAST = "P01.5::B::0122"
ALLOWED_STATES = {
    "CURRENT DEFECT OR LIMITATION",
    "ACTIVE CONDITIONAL RISK",
    "DORMANT FUTURE RISK",
    "OUT-OF-SCOPE CANDIDATE",
    "UNKNOWN — HOLD",
}
QUEUE_DOMAINS = {
    "CURRENT_RUNTIME_SOURCE",
    "DEPLOYMENT_AND_LIVE_BEHAVIOR",
    "AUTHORITATIVE_PACKET_LAW",
    "DEPENDENCY_OR_PLATFORM_STATE",
    "PRIVATE_OR_UNCAPTURED_EVIDENCE",
    "CROSS_SOURCE_CONFLICT",
    "OTHER_RECORD_SPECIFIC_PROOF",
}


class GateError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise GateError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def envelope_hash(record: dict[str, Any]) -> str:
    value = dict(record)
    value.pop("envelope_hash", None)
    return sha256(canonical(value))


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"not an object: {path}")
    return value


def load_inventory() -> tuple[list[dict[str, Any]], bytes, str]:
    raw = INVENTORY_PATH.read_bytes()
    require(sha256(raw) == INV_SHA, "inventory hash changed")
    records = [json.loads(line) for line in raw.splitlines()]
    require(len(records) == 2750, "inventory count changed")
    addresses: list[str] = []
    baseline = 0
    provisional = 0
    for record in records:
        address = record.get("composite_address")
        require(isinstance(address, str) and address, "blank address")
        require(record.get("envelope_hash") == envelope_hash(record), f"bad envelope hash: {address}")
        require(record.get("applicability_state") == "UNCLASSIFIED", f"source applicability changed: {address}")
        require(record.get("routing_state") == "UNROUTED", f"source routing changed: {address}")
        require(record.get("primary_destination") is None, f"source destination populated: {address}")
        for field in ("applicability_evidence", "secondary_destinations", "cross_cutting_laws", "semantic_cluster_ids"):
            require(record.get(field) == [], f"source field populated: {field} {address}")
        addresses.append(address)
        if record.get("source_set") == "BASELINE":
            baseline += 1
        elif record.get("source_set") == "PROVISIONAL":
            provisional += 1
        else:
            raise GateError(f"unknown source set: {address}")
    require(len(set(addresses)) == 2750, "duplicate addresses")
    require(baseline == 122 and provisional == 2628, "source-set counts changed")
    address_sha = sha256(("\n".join(addresses) + "\n").encode("utf-8"))
    require(address_sha == ADDR_SHA, "address sequence changed")
    return records, raw, address_sha


def validate_gate(gate: dict[str, Any], records: list[dict[str, Any]]) -> None:
    require(gate.get("status") == "PROPOSED_PENDING_INDEPENDENT_VERIFICATION", "wrong gate status")
    require(gate.get("supersedes_operating_pattern") == "FOUR_RECORD_GATE_CYCLE", "four-record cycle not superseded")
    source = gate.get("source_inventory", {})
    require(source.get("records") == 2750 and source.get("baseline_records") == 122 and source.get("provisional_records") == 2628, "gate source counts wrong")
    require(source.get("sha256") == INV_SHA and source.get("address_sequence_sha256") == ADDR_SHA, "gate source anchors wrong")

    window = gate.get("window_contract", {})
    require(window.get("minimum_records") == 25, "minimum window wrong")
    require(window.get("maximum_records") == 500, "maximum window wrong")
    require(window.get("selection_rule") == "CONTIGUOUS_IMMUTABLE_SOURCE_ORDER", "selection rule wrong")
    require(window.get("new_gate_required_per_window") is False, "gate repeats per window")
    require(window.get("manifest_required_per_window") is True, "window manifest not required")
    require(window.get("independent_verification_required_per_window") is True, "window verification not required")
    first = window.get("first_authorized_window", {})
    require(first == {
        "pass_id": "SCALABLE-PASS-001",
        "first_address": FIRST,
        "last_address": LAST,
        "records": 122,
        "source_set": "BASELINE",
    }, "first window mismatch")
    require(records[0]["composite_address"] == FIRST and records[121]["composite_address"] == LAST, "first window is not exact baseline block")
    require(all(record["source_set"] == "BASELINE" for record in records[:122]), "first window includes non-baseline record")

    eligibility = gate.get("decision_eligibility", {})
    require(set(eligibility.get("allowed_states", [])) == ALLOWED_STATES, "state vocabulary mismatch")
    for field in (
        "required_record_specific_evidence",
        "required_current_evidence_source_hash",
        "required_reasoning",
        "required_confidence",
        "required_reopening_conditions",
        "required_distinct_author_and_verifier",
        "old_labels_are_not_evidence",
        "old_severity_is_not_evidence",
        "old_owner_suggestions_are_not_evidence",
        "unknown_hold_requires_completed_evidence_attempt",
        "existing_decision_may_be_superseded",
        "supersession_requires_stronger_current_evidence",
        "supersession_must_reference_prior_overlay",
    ):
        require(eligibility.get(field) is True, f"eligibility control disabled: {field}")
    require(eligibility.get("unresolved_without_completed_evidence_attempt") == "QUEUE_ONLY_NO_DECISION", "unresolved records could be mass-HOLD")

    queues = gate.get("evidence_acquisition_queues", {})
    require(queues.get("required_for_every_undecided_record") is True, "queues not mandatory")
    require(queues.get("preserve_permanent_address") is True and queues.get("preserve_source_order") is True, "queue identity/order not preserved")
    require(set(queues.get("allowed_domains", [])) == QUEUE_DOMAINS, "queue domains mismatch")
    require(len(queues.get("required_fields", [])) == 10, "queue field contract incomplete")

    outputs = gate.get("pass_outputs", {})
    require(outputs.get("coverage_rule") == "EVERY_WINDOW_ADDRESS_APPEARS_EXACTLY_ONCE_AS_DECIDED_OR_QUEUED", "coverage rule missing")
    require(all(outputs.get(name) is True for name in ("window_manifest", "decision_overlay", "evidence_queue", "coverage_receipt", "independent_verification_receipt", "status_update")), "required pass output disabled")

    prohibited = gate.get("prohibited_work", {})
    require(all(value is True for value in prohibited.values()), "a prohibited work boundary is disabled")
    require(gate.get("gate_author") != gate.get("gate_verifier"), "gate author equals verifier")
    auth = gate.get("authorization_on_pass", {})
    require(auth.get("scalable_processing_authorized") is True and auth.get("first_pass_authorized") is True, "scalable processing not authorized")
    require(auth.get("first_pass_records") == 122, "first pass size wrong")
    require(auth.get("later_windows_require_new_gate") is False, "later windows require repeated gates")
    require(auth.get("later_windows_require_verified_prior_cursor") is True, "cursor verification missing")
    require(auth.get("routing_authorized") is False and auth.get("implementation_authorized") is False and auth.get("packet_04_authorized") is False, "prohibited authority granted")


def adversarial_tests(gate: dict[str, Any], records: list[dict[str, Any]]) -> int:
    tests: list[dict[str, Any]] = []
    def mutate() -> dict[str, Any]:
        item = copy.deepcopy(gate)
        tests.append(item)
        return item
    mutate()["window_contract"]["maximum_records"] = 2750
    mutate()["window_contract"]["new_gate_required_per_window"] = True
    mutate()["window_contract"]["first_authorized_window"]["records"] = 4
    mutate()["window_contract"]["first_authorized_window"]["last_address"] = "P01.5::B::0004"
    mutate()["decision_eligibility"]["unknown_hold_requires_completed_evidence_attempt"] = False
    mutate()["decision_eligibility"]["unresolved_without_completed_evidence_attempt"] = "UNKNOWN — HOLD"
    mutate()["decision_eligibility"]["old_labels_are_not_evidence"] = False
    mutate()["decision_eligibility"]["supersession_requires_stronger_current_evidence"] = False
    mutate()["evidence_acquisition_queues"]["required_for_every_undecided_record"] = False
    mutate()["evidence_acquisition_queues"]["preserve_source_order"] = False
    mutate()["pass_outputs"]["coverage_rule"] = "PARTIAL_COVERAGE_ALLOWED"
    mutate()["prohibited_work"]["routing"] = False
    mutate()["prohibited_work"]["implementation"] = False
    mutate()["prohibited_work"]["packet_04"] = False
    mutate()["gate_verifier"] = mutate()["gate_author"]
    mutate()["source_inventory"]["sha256"] = "0" * 64

    rejected = 0
    for candidate in tests:
        try:
            validate_gate(candidate, records)
        except GateError:
            rejected += 1
    require(rejected == len(tests), "an adversarial gate mutation passed")
    return rejected


def main() -> None:
    records, raw, address_sha = load_inventory()
    status = STATUS_V81.read_text(encoding="utf-8")
    require("STATUS: BATCH 003 SELECTION AND AUTHORIZATION GATE VERIFIED" in status, "v81 status missing")
    require("ROUTING ASSIGNMENTS COMPLETED: 0" in status, "routing is not zero")
    require("PACKET 04: NOT AUTHORIZED" in status, "Packet 04 boundary missing")
    require(sha256(BATCH001_OVERLAY.read_bytes()) == B1_SHA, "Batch 001 overlay changed")
    require(sha256(BATCH002_OVERLAY.read_bytes()) == B2_SHA, "Batch 002 overlay changed")
    batch003 = load_object(BATCH003_GATE)
    require(batch003.get("status") == "PASS_BATCH_003_SELECTION_GATE_AUTHORIZED", "Batch 003 gate is not PASS")
    require(batch003.get("watch") == "NONE" and batch003.get("blockers") == "NONE", "Batch 003 gate has watch or blocker")
    require(batch003.get("batch_003_applicability_decisions_completed") == 0, "Batch 003 decisions already occurred")
    require(batch003.get("routing_assignments_completed") == 0, "routing already occurred")

    gate = load_object(GATE_PATH)
    validate_gate(gate, records)
    adversarial = adversarial_tests(gate, records)
    require(INVENTORY_PATH.read_bytes() == raw, "inventory changed during verification")

    gate_sha = sha256(GATE_PATH.read_bytes())
    receipt = {
        "packet": "01.5",
        "verification": "scalable_applicability_processing_gate_independent",
        "version": 1,
        "status": "PASS_SCALABLE_APPLICABILITY_PROCESSING_AUTHORIZED",
        "watch": "NONE",
        "blockers": "NONE",
        "gate_sha256": gate_sha,
        "source_inventory_sha256": sha256(raw),
        "address_sequence_sha256": address_sha,
        "source_records": 2750,
        "baseline_records": 122,
        "provisional_records": 2628,
        "minimum_window_records": 25,
        "maximum_window_records": 500,
        "new_gate_required_per_window": False,
        "first_pass_id": "SCALABLE-PASS-001",
        "first_pass_first_address": FIRST,
        "first_pass_last_address": LAST,
        "first_pass_records": 122,
        "mass_unknown_hold_prohibited": True,
        "queue_required_for_undecided": True,
        "complete_decided_or_queued_coverage_required": True,
        "prior_decisions_may_be_superseded_only_by_stronger_evidence": True,
        "adversarial_rejection_fixtures_passed": adversarial,
        "source_inventory_unchanged": True,
        "routing_authorized": False,
        "grouping_authorized": False,
        "closure_authorized": False,
        "implementation_authorized": False,
        "packet_04_authorized": False,
        "next_authorized_work": "PACKET_01.5_SCALABLE_PASS_001_BASELINE_122",
        "stop_before_routing": True
    }
    OUT_JSON.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.write_text(f"""# Packet 01.5 — Scalable Applicability Gate Independent Verification v1

STATUS: PASS — SCALABLE APPLICABILITY PROCESSING AUTHORIZED
WATCH: NONE
BLOCKERS: NONE
FOUR-RECORD GATE CYCLE: SUPERSEDED
SOURCE RECORDS VERIFIED: 2,750
FIRST AUTHORIZED PASS: `SCALABLE-PASS-001`
FIRST PASS WINDOW: `{FIRST}` through `{LAST}`
FIRST PASS RECORDS: 122
MAXIMUM LATER WINDOW: 500
ROUTING AUTHORIZED: NO
IMPLEMENTATION AUTHORIZED: NO
PACKET 04 AUTHORIZED: NO

## Verified controls

- Immutable inventory and address sequence: PASS
- Every source envelope hash: PASS
- Source applicability and routing fields remain blank: PASS
- Reusable windows do not require a new gate: PASS
- Each pass still requires a manifest and independent verifier: PASS
- Historical labels, severity, and owner suggestions cannot decide applicability: PASS
- Unsupported records must enter evidence queues: PASS
- Mass `UNKNOWN — HOLD` without a completed evidence attempt is prohibited: PASS
- Existing decisions may be superseded only by stronger current evidence: PASS
- Every window address must appear exactly once as decided or queued: PASS
- Adversarial gate mutations rejected: {adversarial}
- Source inventory unchanged after verification: PASS

## Authorization

Authorized next:

- `Packet 01.5 — SCALABLE-PASS-001` over all 122 baseline records

The pass may create evidence-supported applicability decisions and evidence-acquisition queues. It may not route, group, close, implement, or begin Packet 04.

FINAL RESULT: `PASS — SCALABLE APPLICABILITY PROCESSING AUTHORIZED`
""", encoding="utf-8")
    STATUS_V82.write_text(f"""# Packet 01.5 — Routing Status v82

STATUS: SCALABLE APPLICABILITY PROCESSING GATE VERIFIED
WATCH: NONE
BLOCKERS: NONE
FOUR-RECORD GATE CYCLE: SUPERSEDED
CUMULATIVE APPLICABILITY CLASSIFICATIONS COMPLETED: 8
ROUTING ASSIGNMENTS COMPLETED: 0
SEMANTIC GROUPING ASSIGNMENTS COMPLETED: 0
INDIVIDUAL RECORD CLOSURE: NOT AUTHORIZED
PACKET 04: NOT AUTHORIZED

## Scalable processing authority

- reusable contiguous windows: 25–500 records
- new gate required per window: no
- independent pass verification: required
- undecided records: evidence queue, not automatic HOLD
- complete window coverage: every address exactly once as decided or queued

## First authorized pass

- pass: `SCALABLE-PASS-001`
- addresses: `{FIRST}` through `{LAST}`
- records: 122 baseline records

## Preserved source inventory

- records: 2,750
- inventory SHA-256: `{sha256(raw)}`
- address-sequence SHA-256: `{address_sha}`
- source applicability state: `UNCLASSIFIED`
- source routing state: `UNROUTED`

## Next authorized work

`Packet 01.5 — SCALABLE-PASS-001 BASELINE 122`

Stop before routing, grouping, closure, implementation, or Packet 04.
""", encoding="utf-8")
    print("PASS: scalable Packet 01.5 applicability processing gate verified")


if __name__ == "__main__":
    try:
        main()
    except GateError as exc:
        raise SystemExit(f"FAIL: {exc}")
