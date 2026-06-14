#!/usr/bin/env python3
"""Independently verify Packet 01.5 Batch 003 selection authorization.

This verifier derives the exact next four immutable source addresses after the
verified Batch 002 overlay. It creates no applicability decision and performs no
routing, grouping, closure, implementation, or Packet 04 work.
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
TOOLS = REPO / "tools"

GATE_PATH = APP / "Packet_01.5_Applicability_Batch_003_Selection_Gate_v1.json"
INVENTORY_PATH = ROUTING / "Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
BATCH002_RECEIPT = AUDIT / "Packet_01.5_Applicability_Batch_002_Independent_Verification_v1.json"
BATCH001_OVERLAY = APP / "Packet_01.5_Applicability_Decisions_Batch_001_v1.jsonl"
BATCH002_OVERLAY = APP / "Packet_01.5_Applicability_Decisions_Batch_002_v1.jsonl"
SELECTION_PATH = APP / "Packet_01.5_Applicability_Batch_003_Selection_v1.json"
OUT_JSON = AUDIT / "Packet_01.5_Applicability_Batch_003_Selection_Gate_Independent_Verification_v1.json"
OUT_MD = AUDIT / "Packet_01.5_Applicability_Batch_003_Selection_Gate_Independent_Verification_v1.md"
STATUS_MD = AUDIT / "Packet_01.5_Routing_Status_v81.md"
PRIOR_VERIFIER = TOOLS / "verify_packet_01_5_applicability_batch_002_v1.py"

EXPECTED_INVENTORY_SHA256 = "76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477"
EXPECTED_ADDRESS_SEQUENCE_SHA256 = "3d808e1ec3f163e4cb2ab7a15767563fe7c43b9920bcecde9abe711226220916"
EXPECTED_BATCH001_OVERLAY_SHA256 = "2de246b718e99bae35f18eb2108e5df24e7bcaf240104e17595dcfc6311bba96"
EXPECTED_BATCH002_OVERLAY_SHA256 = "8d629e824d29ab4549e2132a6401c10049d7a3c1476b66dfd52c2dc8849d1000"
EXPECTED_BATCH001 = [f"P01.5::B::{number:04d}" for number in range(1, 5)]
EXPECTED_BATCH002 = [f"P01.5::B::{number:04d}" for number in range(5, 9)]
EXPECTED_SELECTED = [f"P01.5::B::{number:04d}" for number in range(9, 13)]
ALLOWED_RECORD_FIELDS = {
    "composite_address",
    "source_set",
    "source_record_ordinal",
    "original_identifier",
    "envelope_hash",
    "source_block_hash",
}
TOP_FIELDS = {
    "packet",
    "artifact",
    "version",
    "batch_id",
    "status",
    "source_inventory_sha256",
    "address_sequence_sha256",
    "selection_method",
    "batch_size",
    "prior_batch_id",
    "prior_batch_addresses",
    "selected_records",
    "applicability_decisions_performed",
    "routing_performed",
    "grouping_performed",
    "closure_performed",
    "implementation_authorized",
    "packet_04_authorized",
    "gate_author",
    "gate_verifier",
}


class GateError(ValueError):
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


def envelope_hash(envelope: dict[str, Any]) -> str:
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
        require(isinstance(value, dict), f"non-object JSONL record at {path}:{number}")
        records.append(value)
    return records


def verify_prior_chain() -> dict[str, Any]:
    subprocess.run([sys.executable, str(PRIOR_VERIFIER)], cwd=REPO, check=True)
    receipt = load_object(BATCH002_RECEIPT)
    require(receipt.get("status") == "PASS_BATCH_002_APPLICABILITY_VERIFIED", "Batch 002 receipt is not PASS")
    require(receipt.get("watch") == "NONE" and receipt.get("blockers") == "NONE", "Batch 002 has watch or blocker")
    require(receipt.get("batch_addresses") == EXPECTED_BATCH002, "Batch 002 address set changed")
    require(receipt.get("batch_decisions") == 4, "Batch 002 decision count changed")
    require(receipt.get("decision_overlay_sha256") == EXPECTED_BATCH002_OVERLAY_SHA256, "Batch 002 receipt overlay hash changed")
    require(receipt.get("cumulative_applicability_classifications_completed") == 8, "cumulative applicability count changed")
    require(receipt.get("routing_assignments_completed") == 0, "routing already occurred")
    require(receipt.get("semantic_grouping_assignments_completed") == 0, "grouping already occurred")
    require(receipt.get("source_records_removed") == 0 and receipt.get("source_records_closed") == 0, "source record removal or closure occurred")
    require(receipt.get("packet_04_authorized") is False, "Packet 04 became authorized")
    require(receipt.get("next_authorized_work") == "PACKET_01.5_PHASE_E_BATCH_003_SELECTION_AND_AUTHORIZATION_GATE", "next authorized work changed")
    require(receipt.get("batch_003_applicability_decisions_authorized") is False, "Batch 003 decisions were already authorized")
    return receipt


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
        require(isinstance(record, dict), f"source record {number} is not an object")
        address = record.get("composite_address")
        require(isinstance(address, str) and address, f"source address missing at line {number}")
        require(record.get("envelope_hash") == envelope_hash(record), f"envelope hash mismatch at {address}")
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


def verify_overlay(path: Path, expected_hash: str, expected_addresses: list[str], source_by_address: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    require(sha256(path.read_bytes()) == expected_hash, f"overlay bytes changed: {path.name}")
    overlay = load_jsonl(path)
    require(len(overlay) == len(expected_addresses), f"overlay count changed: {path.name}")
    addresses = [item.get("composite_address") for item in overlay]
    require(addresses == expected_addresses, f"overlay addresses changed: {path.name}")
    require(len(set(addresses)) == len(addresses), f"overlay has duplicate addresses: {path.name}")
    for item in overlay:
        address = item["composite_address"]
        source = source_by_address.get(address)
        require(source is not None, f"overlay address missing from source: {address}")
        require(item.get("source_envelope_hash") == source.get("envelope_hash"), f"overlay envelope hash mismatch at {address}")
        require(item.get("source_block_hash") == source.get("source_block_hash"), f"overlay block hash mismatch at {address}")
        require(item.get("primary_destination") is None, f"overlay destination populated at {address}")
        require(item.get("secondary_destinations") == [], f"overlay secondary destinations populated at {address}")
        require(item.get("semantic_cluster_ids") == [], f"overlay grouping populated at {address}")
        require(item.get("closure_state") == "OPEN", f"overlay record closed at {address}")
    return overlay


def build_manifest(selected: list[dict[str, Any]], gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "packet": "01.5",
        "artifact": "applicability_batch_selection",
        "version": 1,
        "batch_id": "PACKET-01.5-APPLICABILITY-BATCH-003",
        "status": "SELECTED_PENDING_APPLICABILITY_DECISIONS",
        "source_inventory_sha256": EXPECTED_INVENTORY_SHA256,
        "address_sequence_sha256": EXPECTED_ADDRESS_SEQUENCE_SHA256,
        "selection_method": gate["selection"]["method"],
        "batch_size": 4,
        "prior_batch_id": "PACKET-01.5-APPLICABILITY-BATCH-002",
        "prior_batch_addresses": EXPECTED_BATCH002,
        "selected_records": [
            {field: item[field] for field in (
                "composite_address",
                "source_set",
                "source_record_ordinal",
                "original_identifier",
                "envelope_hash",
                "source_block_hash",
            )}
            for item in selected
        ],
        "applicability_decisions_performed": False,
        "routing_performed": False,
        "grouping_performed": False,
        "closure_performed": False,
        "implementation_authorized": False,
        "packet_04_authorized": False,
        "gate_author": gate["gate_author"],
        "gate_verifier": gate["gate_verifier"],
    }


def validate_manifest(manifest: dict[str, Any], gate: dict[str, Any], source_by_address: dict[str, dict[str, Any]]) -> None:
    if set(manifest) != TOP_FIELDS:
        raise GateError("selection manifest top-level field set mismatch")
    if manifest["packet"] != "01.5" or manifest["artifact"] != "applicability_batch_selection" or manifest["version"] != 1:
        raise GateError("selection manifest identity mismatch")
    if manifest["batch_id"] != "PACKET-01.5-APPLICABILITY-BATCH-003":
        raise GateError("batch identity mismatch")
    if manifest["status"] != "SELECTED_PENDING_APPLICABILITY_DECISIONS":
        raise GateError("selection status mismatch")
    if manifest["source_inventory_sha256"] != EXPECTED_INVENTORY_SHA256 or manifest["address_sequence_sha256"] != EXPECTED_ADDRESS_SEQUENCE_SHA256:
        raise GateError("selection source anchor mismatch")
    if manifest["selection_method"] != "EXACT_NEXT_CONTIGUOUS_SOURCE_ORDER_AFTER_VERIFIED_PRIOR_BATCH":
        raise GateError("selection method is not source-order neutral")
    if manifest["batch_size"] != 4:
        raise GateError("Batch 003 size is not four")
    if manifest["prior_batch_id"] != "PACKET-01.5-APPLICABILITY-BATCH-002" or manifest["prior_batch_addresses"] != EXPECTED_BATCH002:
        raise GateError("prior batch anchor mismatch")
    if manifest["gate_author"] != gate["gate_author"] or manifest["gate_verifier"] != gate["gate_verifier"]:
        raise GateError("gate identity mismatch")
    if manifest["gate_author"] == manifest["gate_verifier"]:
        raise GateError("gate author and verifier are not distinct")

    selected = manifest["selected_records"]
    if not isinstance(selected, list) or len(selected) != 4:
        raise GateError("selection must contain exactly four records")
    addresses = [item.get("composite_address") for item in selected if isinstance(item, dict)]
    if addresses != EXPECTED_SELECTED:
        raise GateError("selection is not the exact next contiguous set")
    if len(set(addresses)) != 4:
        raise GateError("selection addresses are duplicated")
    if set(addresses) & (set(EXPECTED_BATCH001) | set(EXPECTED_BATCH002)):
        raise GateError("selection overlaps a prior batch")

    for item in selected:
        if not isinstance(item, dict) or set(item) != ALLOWED_RECORD_FIELDS:
            raise GateError("selected record contains missing or prohibited fields")
        source = source_by_address.get(item["composite_address"])
        if source is None:
            raise GateError("selected address is absent from source inventory")
        for field in ALLOWED_RECORD_FIELDS:
            if item[field] != source[field]:
                raise GateError(f"selected identity field mismatch: {field}")

    for field in (
        "applicability_decisions_performed",
        "routing_performed",
        "grouping_performed",
        "closure_performed",
        "implementation_authorized",
        "packet_04_authorized",
    ):
        if manifest[field] is not False:
            raise GateError(f"prohibited action or authority is true: {field}")


def expect_invalid(name: str, candidate: dict[str, Any], gate: dict[str, Any], source_by_address: dict[str, dict[str, Any]]) -> None:
    try:
        validate_manifest(candidate, gate, source_by_address)
    except GateError:
        return
    fail(f"adversarial selection unexpectedly passed: {name}")


def adversarial_tests(manifest: dict[str, Any], gate: dict[str, Any], source_by_address: dict[str, dict[str, Any]]) -> int:
    fixtures: list[tuple[str, dict[str, Any]]] = []

    def mutate(name: str) -> dict[str, Any]:
        value = copy.deepcopy(manifest)
        fixtures.append((name, value))
        return value

    value = mutate("overlap Batch 002")
    value["selected_records"][0] = {field: source_by_address["P01.5::B::0008"][field] for field in ALLOWED_RECORD_FIELDS}
    value = mutate("overlap Batch 001")
    value["selected_records"][0] = {field: source_by_address["P01.5::B::0004"][field] for field in ALLOWED_RECORD_FIELDS}
    value = mutate("skip an address")
    value["selected_records"][2] = {field: source_by_address["P01.5::B::0013"][field] for field in ALLOWED_RECORD_FIELDS}
    value = mutate("reordered selection")
    value["selected_records"][0], value["selected_records"][1] = value["selected_records"][1], value["selected_records"][0]
    value = mutate("duplicate selection")
    value["selected_records"][1] = copy.deepcopy(value["selected_records"][0])
    value = mutate("expanded batch")
    value["selected_records"].append({field: source_by_address["P01.5::B::0013"][field] for field in ALLOWED_RECORD_FIELDS})
    value["batch_size"] = 5
    value = mutate("shortened batch")
    value["selected_records"] = value["selected_records"][:3]
    value["batch_size"] = 3
    value = mutate("content-based selection")
    value["selection_method"] = "SELECT_BY_SEVERITY"
    value = mutate("mutated envelope hash")
    value["selected_records"][0]["envelope_hash"] = "0" * 64
    value = mutate("mutated block hash")
    value["selected_records"][0]["source_block_hash"] = "0" * 64
    value = mutate("missing identity field")
    value["selected_records"][0].pop("source_block_hash")
    value = mutate("applicability field added")
    value["selected_records"][0]["applicability_state"] = "UNKNOWN — HOLD"
    value = mutate("decision performed")
    value["applicability_decisions_performed"] = True
    value = mutate("routing performed")
    value["routing_performed"] = True
    value = mutate("grouping performed")
    value["grouping_performed"] = True
    value = mutate("closure performed")
    value["closure_performed"] = True
    value = mutate("implementation authorized")
    value["implementation_authorized"] = True
    value = mutate("Packet 04 authorized")
    value["packet_04_authorized"] = True
    value = mutate("author equals verifier")
    value["gate_verifier"] = value["gate_author"]
    value = mutate("wrong inventory hash")
    value["source_inventory_sha256"] = "0" * 64

    for name, candidate in fixtures:
        expect_invalid(name, candidate, gate, source_by_address)
    return len(fixtures)


def write_outputs(manifest: dict[str, Any], selected: list[dict[str, Any]], inventory_raw: bytes, address_hash: str, adversarial: int) -> None:
    manifest_raw = SELECTION_PATH.read_bytes()
    selected_summary = [
        {
            "composite_address": item["composite_address"],
            "original_identifier": item["original_identifier"],
            "envelope_hash": item["envelope_hash"],
            "source_block_hash": item["source_block_hash"],
        }
        for item in selected
    ]
    receipt = {
        "packet": "01.5",
        "verification": "batch_003_selection_authorization_gate_independent",
        "version": 1,
        "status": "PASS_BATCH_003_SELECTION_GATE_AUTHORIZED",
        "watch": "NONE",
        "blockers": "NONE",
        "batch_id": "PACKET-01.5-APPLICABILITY-BATCH-003",
        "selection_method": manifest["selection_method"],
        "batch_size": 4,
        "selected_addresses": EXPECTED_SELECTED,
        "selected_records": selected_summary,
        "source_inventory_sha256": sha256(inventory_raw),
        "address_sequence_sha256": address_hash,
        "selection_manifest_path": str(SELECTION_PATH.relative_to(REPO)),
        "selection_manifest_sha256": sha256(manifest_raw),
        "batch_001_overlay_sha256": EXPECTED_BATCH001_OVERLAY_SHA256,
        "batch_002_overlay_sha256": EXPECTED_BATCH002_OVERLAY_SHA256,
        "every_source_envelope_hash_recomputed": True,
        "source_inventory_unchanged": True,
        "source_applicability_fields_remain_blank": True,
        "source_routing_fields_remain_blank": True,
        "selection_content_neutral": True,
        "selection_overlap_count": 0,
        "positive_selection_fixture_passed": 1,
        "adversarial_rejection_fixtures_passed": adversarial,
        "cumulative_applicability_classifications_completed": 8,
        "batch_003_applicability_decisions_completed": 0,
        "routing_assignments_completed": 0,
        "semantic_grouping_assignments_completed": 0,
        "source_records_removed": 0,
        "source_records_closed": 0,
        "batch_003_applicability_decisions_authorized": True,
        "implementation_authorized": False,
        "packet_04_authorized": False,
        "next_authorized_work": "PACKET_01.5_PHASE_E_BATCH_003_APPLICABILITY_ONLY_DECISIONS",
        "stop_before_batch_003_decisions": True,
        "stop_before_routing": True,
    }
    OUT_JSON.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{item['composite_address']}` | `{item['original_identifier']}` | `{item['envelope_hash']}` |"
        for item in selected
    )
    OUT_MD.write_text(
        f"""# Packet 01.5 — Batch 003 Selection Gate Independent Verification v1

STATUS: PASS — BATCH 003 SELECTION GATE AUTHORIZED
WATCH: NONE
BLOCKERS: NONE
BATCH 003 RECORDS SELECTED: 4
BATCH 003 APPLICABILITY DECISIONS COMPLETED: 0
CUMULATIVE APPLICABILITY CLASSIFICATIONS COMPLETED: 8
ROUTING ASSIGNMENTS COMPLETED: 0
SEMANTIC GROUPING ASSIGNMENTS COMPLETED: 0
SOURCE RECORDS REMOVED OR CLOSED: 0
PACKET 04 AUTHORIZED: NO

## Selected records

| Permanent address | Original identifier | Envelope hash |
|---|---|---|
{rows}

## Independent proof

- Batch 002 applicability verifier rerun: PASS
- Batch 001 overlay hash: `{EXPECTED_BATCH001_OVERLAY_SHA256}`
- Batch 002 overlay hash: `{EXPECTED_BATCH002_OVERLAY_SHA256}`
- Immutable source envelopes checked: 2,750
- Inventory SHA-256: `{sha256(inventory_raw)}`
- Address-sequence SHA-256: `{address_hash}`
- Every source-envelope hash recomputed: PASS
- Exact next-four contiguous selection: PASS
- Prior-batch overlap: 0
- Content-neutral selection: PASS
- Selection manifest limited to identity and integrity fields: PASS
- Batch 003 applicability decisions present: 0
- Routing or grouping assignments present: 0
- Adversarial rejection fixtures passed: {adversarial}
- Source inventory unchanged after verification: PASS

## Authorization result

Authorized next:

- Packet 01.5 Phase E — Batch 003 Applicability-Only Decisions

Not performed or authorized in this gate:

- any Batch 003 applicability decision
- owner routing
- secondary destinations
- cross-cutting laws
- semantic grouping
- record closure
- implementation
- Packet 04

FINAL RESULT: `PASS — BATCH 003 SELECTION GATE AUTHORIZED`

END PACKET 01.5 — BATCH 003 SELECTION GATE INDEPENDENT VERIFICATION v1
""",
        encoding="utf-8",
    )

    STATUS_MD.write_text(
        f"""# Packet 01.5 — Routing Status v81

STATUS: BATCH 003 SELECTION AND AUTHORIZATION GATE VERIFIED
WATCH: NONE
BLOCKERS: NONE
ROUTING START AUTHORIZATION: PASS UNDER CORRECTED V2 GATE
APPLICABILITY EVIDENCE CATALOG: PASS
BATCH 001: PASS — 4 `UNKNOWN — HOLD`
BATCH 002: PASS — 4 `UNKNOWN — HOLD`
BATCH 003 SELECTION GATE: PASS
CUMULATIVE APPLICABILITY CLASSIFICATIONS COMPLETED: 8
BATCH 003 APPLICABILITY DECISIONS COMPLETED: 0
ROUTING ASSIGNMENTS COMPLETED: 0
SEMANTIC GROUPING ASSIGNMENTS COMPLETED: 0
INDIVIDUAL RECORD CLOSURE: NOT AUTHORIZED
PACKET 04: NOT AUTHORIZED

## Batch 003 authorized selection

- Addresses: `P01.5::B::0009` through `P01.5::B::0012`
- Selection manifest SHA-256: `{sha256(manifest_raw)}`
- Selection method: exact next contiguous immutable source order
- Selection is content-neutral and contains identity/integrity fields only
- No Batch 003 applicability decision has been made

## Preserved source inventory

- Total source envelopes: 2,750
- Inventory SHA-256: `{sha256(inventory_raw)}`
- Address-sequence SHA-256: `{address_hash}`
- Source applicability state remains `UNCLASSIFIED`
- Source routing state remains `UNROUTED`
- Source records removed or closed: 0

## Next authorized work

`Packet 01.5 Phase E — Batch 003 Applicability-Only Decisions`

Stop before making those decisions in this gate task. Routing remains unauthorized.

END PACKET 01.5 — ROUTING STATUS v81
""",
        encoding="utf-8",
    )


def main() -> None:
    verify_prior_chain()
    records, raw_before, address_hash = verify_inventory()
    source_by_address = {item["composite_address"]: item for item in records}
    verify_overlay(BATCH001_OVERLAY, EXPECTED_BATCH001_OVERLAY_SHA256, EXPECTED_BATCH001, source_by_address)
    verify_overlay(BATCH002_OVERLAY, EXPECTED_BATCH002_OVERLAY_SHA256, EXPECTED_BATCH002, source_by_address)

    gate = load_object(GATE_PATH)
    require(gate.get("status") == "PROPOSED_PENDING_INDEPENDENT_VERIFICATION", "gate status mismatch")
    require(gate.get("gate_author") != gate.get("gate_verifier"), "gate author and verifier are not distinct")
    require(gate.get("selection", {}).get("expected_addresses") == EXPECTED_SELECTED, "gate selected addresses mismatch")
    require(gate.get("selection", {}).get("batch_size") == 4, "gate batch size mismatch")
    require(gate.get("authorization_on_pass", {}).get("batch_003_applicability_decisions_authorized") is True, "gate does not authorize later Batch 003 decisions")
    require(gate.get("authorization_on_pass", {}).get("actual_batch_003_applicability_decisions_performed") is False, "gate performs Batch 003 decisions")

    addresses = [item["composite_address"] for item in records]
    prior_end_index = addresses.index(EXPECTED_BATCH002[-1])
    derived = records[prior_end_index + 1 : prior_end_index + 5]
    require([item["composite_address"] for item in derived] == EXPECTED_SELECTED, "derived source-order selection mismatch")

    manifest = build_manifest(derived, gate)
    validate_manifest(manifest, gate, source_by_address)
    adversarial = adversarial_tests(manifest, gate, source_by_address)

    SELECTION_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    persisted = load_object(SELECTION_PATH)
    validate_manifest(persisted, gate, source_by_address)
    require(INVENTORY_PATH.read_bytes() == raw_before, "source inventory changed during gate verification")

    write_outputs(persisted, derived, raw_before, address_hash, adversarial)
    print("PASS: Packet 01.5 Batch 003 selection and authorization gate independently verified.")
    print("Selected addresses: P01.5::B::0009 through P01.5::B::0012")
    print("Batch 003 applicability decisions completed: 0")
    print("Routing assignments completed: 0")
    print(f"Adversarial rejections: {adversarial}")


if __name__ == "__main__":
    main()
