#!/usr/bin/env python3
"""Apply Packet 01.5 Applicability Batch 001 as a lossless transaction.

The transaction classifies only the first ten baseline envelopes. It preserves
all source evidence and leaves every routing destination blank.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "audit"
ROUTING = AUDIT / "routing-inventory"
BATCHES = AUDIT / "routing-batches"
EVIDENCE = AUDIT / "routing-evidence"

PARENT = ROUTING / "Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
PARENT_VERIFY = AUDIT / "Packet_01.5_Blank_Routing_Inventory_Independent_Verification_v1.json"
CATALOG = EVIDENCE / "Packet_01.5_Project_Contact_Evidence_Catalog_v1.json"
CATALOG_VERIFY = AUDIT / "Packet_01.5_Project_Contact_Evidence_Catalog_Independent_Verification_v1.json"
PLAN = BATCHES / "Packet_01.5_Applicability_Batch_001_Plan_v1.json"
CHILD = ROUTING / "Packet_01.5_Applicability_Inventory_v2_Batch_001.jsonl"
CHILD_GZ = ROUTING / "Packet_01.5_Applicability_Inventory_v2_Batch_001.jsonl.gz"
CHILD_MANIFEST = ROUTING / "Packet_01.5_Applicability_Inventory_v2_Batch_001.manifest.json"
BUILD_JSON = BATCHES / "Packet_01.5_Applicability_Batch_001_Build_v1.json"
BUILD_MD = BATCHES / "Packet_01.5_Applicability_Batch_001_Build_v1.md"

EXPECTED_PARENT_SHA = "76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477"
IMMUTABLE_FIELDS = [
    "composite_address", "source_set", "source_path", "source_pass",
    "source_file_hash", "source_record_ordinal", "original_identifier",
    "original_heading", "original_body", "source_block_hash", "harm_text",
    "overlap_text", "legacy_exception_codes", "normalization_version",
]


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


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"not a JSON object: {path}")
    return value


def load_jsonl(path: Path) -> tuple[list[dict[str, Any]], bytes]:
    raw = path.read_bytes()
    envelopes: list[dict[str, Any]] = []
    for number, line in enumerate(raw.splitlines(), 1):
        value = json.loads(line)
        require(isinstance(value, dict), f"line {number} is not an object")
        envelopes.append(value)
    return envelopes, raw


def write_gzip(path: Path, data: bytes) -> bytes:
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0, compresslevel=9) as stream:
        stream.write(data)
    compressed = buffer.getvalue()
    path.write_bytes(compressed)
    return compressed


def catalog_index(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    common = catalog["current_capability_rule"]
    summary = catalog["preserved_summary_source"]
    for entry in catalog["current_capabilities"]:
        value = dict(entry)
        value["evidence_type"] = common["evidence_type"]
        value["source_reference"] = summary["path"]
        value["source_hash_or_stable_reference"] = summary["sha256"]
        value["explanation"] = (
            f"Packet 03 verifies {entry['capability_id']} as a current capability. "
            "Applicability still requires a record-specific harm path."
        )
        result[value["evidence_id"]] = value
    boundary_source = catalog["boundary_source"]
    for entry in catalog["boundary_evidence"]:
        value = dict(entry)
        value["source_reference"] = boundary_source["path"]
        value["source_hash_or_stable_reference"] = boundary_source["parent_source_sha256"]
        result[value["evidence_id"]] = value
    require(len(result) == 26, "catalog index count mismatch")
    return result


def main() -> None:
    BATCHES.mkdir(parents=True, exist_ok=True)
    ROUTING.mkdir(parents=True, exist_ok=True)

    parent_envelopes, parent_raw = load_jsonl(PARENT)
    plan = load_json(PLAN)
    catalog = load_json(CATALOG)
    parent_verify = load_json(PARENT_VERIFY)
    catalog_verify = load_json(CATALOG_VERIFY)

    require(sha256(parent_raw) == EXPECTED_PARENT_SHA, "parent inventory hash mismatch")
    require(len(parent_envelopes) == 2750, "parent envelope count mismatch")
    require(parent_verify.get("status") == "PASS", "parent inventory verification is not PASS")
    require(parent_verify.get("watch") == "NONE" and parent_verify.get("blockers") == "NONE", "parent verification is not clean")
    require(catalog_verify.get("status") == "PASS", "contact catalog verification is not PASS")
    require(catalog_verify.get("watch") == "NONE" and catalog_verify.get("blockers") == "NONE", "catalog verification is not clean")
    require(plan.get("batch") == "P01.5-APP-B001", "batch identity mismatch")
    require(plan.get("parent_inventory", {}).get("sha256") == EXPECTED_PARENT_SHA, "plan parent hash mismatch")

    decisions = plan.get("decisions")
    require(isinstance(decisions, list) and len(decisions) == 10, "decision count mismatch")
    decision_by_address = {decision["address"]: decision for decision in decisions}
    require(len(decision_by_address) == 10, "decision addresses are not unique")
    planned_addresses = plan.get("selection", {}).get("addresses")
    require(planned_addresses == [f"P01.5::B::{number:04d}" for number in range(1, 11)], "batch address sequence mismatch")
    require(set(decision_by_address) == set(planned_addresses), "decision address set mismatch")

    evidence_index = catalog_index(catalog)
    catalog_hash = sha256(CATALOG.read_bytes())
    child_envelopes: list[dict[str, Any]] = []
    changed_addresses: list[str] = []

    for parent in parent_envelopes:
        address = parent["composite_address"]
        child = dict(parent)
        decision = decision_by_address.get(address)
        if decision is not None:
            require(parent.get("original_identifier") == decision["original_identifier"], f"identifier mismatch at {address}")
            require(parent.get("applicability_state") == "UNCLASSIFIED", f"parent applicability is not blank at {address}")
            require(parent.get("routing_state") == "UNROUTED", f"parent routing is not blank at {address}")
            evidence_entries: list[dict[str, Any]] = []
            for catalog_id in decision["catalog_evidence_ids"]:
                source = evidence_index.get(catalog_id)
                require(source is not None, f"unknown catalog evidence ID at {address}: {catalog_id}")
                evidence_entries.append({
                    "evidence_id": f"P01.5-APP-B001::{address}::{catalog_id}",
                    "catalog_evidence_id": catalog_id,
                    "evidence_type": source["evidence_type"],
                    "source_reference": source["source_reference"],
                    "source_hash_or_stable_reference": source["source_hash_or_stable_reference"],
                    "contact_path_explanation": f"{decision['contact_path']} Catalog basis: {source['explanation']}",
                    "decision_rationale": decision["rationale"],
                })
            evidence_entries.append({
                "evidence_id": f"P01.5-APP-B001::{address}::SOURCE-RECORD",
                "catalog_evidence_id": None,
                "evidence_type": "PLANNED_CONTACT",
                "source_reference": parent["source_path"],
                "source_hash_or_stable_reference": parent["source_file_hash"],
                "contact_path_explanation": decision["contact_path"],
                "decision_rationale": f"Original source record: {parent['original_heading']}. {decision['rationale']}",
            })
            child["applicability_state"] = decision["state"]
            child["applicability_evidence"] = evidence_entries
            child["applicability_batch_id"] = "P01.5-APP-B001"
            child["applicability_parent_envelope_hash"] = parent["envelope_hash"]
            child["applicability_catalog_hash"] = catalog_hash
            child["applicability_decision_hash"] = sha256(canonical({
                "address": address,
                "state": decision["state"],
                "evidence": evidence_entries,
            }))
            child["envelope_hash"] = envelope_hash(child)
            changed_addresses.append(address)
        child_envelopes.append(child)

    require(changed_addresses == planned_addresses, "changed address sequence mismatch")
    require(len(child_envelopes) == len(parent_envelopes) == 2750, "child count mismatch")
    require([item["composite_address"] for item in child_envelopes] == [item["composite_address"] for item in parent_envelopes], "address order changed")

    changed = 0
    for parent, child in zip(parent_envelopes, child_envelopes):
        address = parent["composite_address"]
        for field in IMMUTABLE_FIELDS:
            require(child.get(field) == parent.get(field), f"immutable field changed ({field}) at {address}")
        require(child.get("routing_state") == "UNROUTED", f"routing state changed at {address}")
        require(child.get("primary_destination") is None, f"primary destination populated at {address}")
        for field in ("secondary_destinations", "cross_cutting_laws", "watch_triggers", "semantic_cluster_ids"):
            require(child.get(field) == [], f"routing field populated ({field}) at {address}")
        require(child["envelope_hash"] == envelope_hash(child), f"child envelope hash mismatch at {address}")
        if parent != child:
            changed += 1
    require(changed == 10, f"changed envelope count is {changed}, expected 10")

    states = Counter(item["applicability_state"] for item in child_envelopes)
    require(states == Counter({"UNCLASSIFIED": 2740, "ACTIVE_CONDITIONAL_RISK": 10}), f"unexpected state counts: {states}")

    raw_child = ("\n".join(json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for item in child_envelopes) + "\n").encode("utf-8")
    CHILD.write_bytes(raw_child)
    compressed = write_gzip(CHILD_GZ, raw_child)
    address_hash = sha256(("\n".join(item["composite_address"] for item in child_envelopes) + "\n").encode("utf-8"))

    manifest = {
        "packet": "01.5",
        "inventory": "applicability_inventory",
        "version": 2,
        "batch": "P01.5-APP-B001",
        "build_date": date.today().isoformat(),
        "status": "BUILT_PENDING_INDEPENDENT_VERIFICATION",
        "watch": "NONE",
        "blockers": "NONE",
        "parent": {"path": str(PARENT.relative_to(REPO)), "sha256": EXPECTED_PARENT_SHA, "envelopes": 2750},
        "child": {"path": str(CHILD.relative_to(REPO)), "bytes": len(raw_child), "sha256": sha256(raw_child), "envelopes": 2750},
        "gzip": {"path": str(CHILD_GZ.relative_to(REPO)), "bytes": len(compressed), "sha256": sha256(compressed), "mtime": 0},
        "address_sequence_sha256": address_hash,
        "changed_envelopes": 10,
        "unchanged_envelopes": 2740,
        "state_counts": dict(states),
        "routing_assignments": 0,
        "immutable_fields": IMMUTABLE_FIELDS,
        "catalog_sha256": catalog_hash,
        "source_records_removed": 0,
        "source_records_closed": 0,
    }
    CHILD_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    receipt = {
        "packet": "01.5",
        "batch": "P01.5-APP-B001",
        "version": 1,
        "status": "PASS",
        "watch": "NONE",
        "blockers": "NONE",
        "parent_inventory_sha256": EXPECTED_PARENT_SHA,
        "child_inventory_sha256": sha256(raw_child),
        "combined_envelopes": 2750,
        "changed_envelopes": 10,
        "unchanged_envelopes": 2740,
        "active_conditional_risk": 10,
        "unclassified": 2740,
        "routing_assignments": 0,
        "source_records_removed": 0,
        "source_records_closed": 0,
    }
    BUILD_JSON.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    BUILD_MD.write_text("\n".join([
        "# Packet 01.5 — Applicability Batch 001 Build v1",
        "",
        "STATUS: PASS",
        "WATCH: NONE",
        "BLOCKERS: NONE",
        "ROUTING ASSIGNMENTS: 0",
        "",
        "- Parent envelopes: 2750",
        "- Child envelopes: 2750",
        "- Classified in Batch 001: 10",
        "- ACTIVE_CONDITIONAL_RISK: 10",
        "- UNCLASSIFIED: 2740",
        "- Immutable source fields changed: 0",
        "- Addresses added, removed, or reordered: 0",
        "- Destination fields populated: 0",
        "- Source records removed: 0",
        "- Source records closed: 0",
        f"- Parent SHA-256: `{EXPECTED_PARENT_SHA}`",
        f"- Child SHA-256: `{sha256(raw_child)}`",
        f"- Deterministic gzip SHA-256: `{sha256(compressed)}`",
        "",
        "Batch 001 remains pending independent verification before acceptance.",
        "",
        "END PACKET 01.5 — APPLICABILITY BATCH 001 BUILD v1",
        "",
    ]), encoding="utf-8")
    print("PASS — applied Packet 01.5 Applicability Batch 001 to ten envelopes")


if __name__ == "__main__":
    main()
