#!/usr/bin/env python3
"""Build Packet 01.5 Applicability Batch 001 decision overlay.

This builder reads the immutable source inventory and the reviewed Batch 001 plan,
then writes four HOLD decisions into a separate overlay. It does not mutate the
source inventory and does not perform routing, grouping, closure, or implementation.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "audit"
APP = AUDIT / "applicability"
ROUTING = AUDIT / "routing-inventory"

PLAN_PATH = APP / "Packet_01.5_Applicability_Batch_001_Plan_v1.json"
CATALOG_PATH = APP / "Packet_01.5_Applicability_Evidence_Catalog_v1.json"
INVENTORY_PATH = ROUTING / "Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
OUT_JSONL = APP / "Packet_01.5_Applicability_Decisions_Batch_001_v1.jsonl"
OUT_MD = AUDIT / "Packet_01.5_First_Controlled_Applicability_Batch_001_v1.md"

EXPECTED_INVENTORY_SHA256 = "76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477"
EXPECTED_ADDRESSES = [f"P01.5::B::{number:04d}" for number in range(1, 5)]
EXPECTED_IDENTIFIERS = ["AI-001", "AI-002", "AI-003", "AI-004"]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"not a JSON object: {path}")
    return value


def evidence_entry(
    evidence_id: str,
    source_reference: str,
    stable_reference: str,
    claim_supported: str,
) -> dict[str, str]:
    return {
        "evidence_id": evidence_id,
        "source_reference": source_reference,
        "source_hash_or_stable_reference": stable_reference,
        "claim_supported": claim_supported,
    }


def main() -> None:
    raw_before = INVENTORY_PATH.read_bytes()
    require(sha256(raw_before) == EXPECTED_INVENTORY_SHA256, "source inventory hash changed")

    lines = raw_before.splitlines()
    require(len(lines) == 2750, "source inventory line count changed")
    first_four = [json.loads(line) for line in lines[:4]]
    require([item["composite_address"] for item in first_four] == EXPECTED_ADDRESSES, "first four addresses changed")
    require([item["original_identifier"] for item in first_four] == EXPECTED_IDENTIFIERS, "first four identifiers changed")

    plan = load_object(PLAN_PATH)
    catalog = load_object(CATALOG_PATH)
    require(plan.get("batch_id") == "PACKET-01.5-APPLICABILITY-BATCH-001", "batch identity mismatch")
    require(plan.get("source_inventory", {}).get("sha256") == EXPECTED_INVENTORY_SHA256, "plan source hash mismatch")
    require(plan.get("decision_author") != plan.get("decision_verifier"), "author and verifier are not distinct")

    plan_records = plan.get("records")
    require(isinstance(plan_records, list) and len(plan_records) == 4, "plan must contain four records")
    require([record.get("composite_address") for record in plan_records] == EXPECTED_ADDRESSES, "plan address order mismatch")

    catalog_entries = catalog.get("evidence_sources")
    require(isinstance(catalog_entries, list), "catalog evidence sources missing")
    catalog_by_id = {entry["evidence_id"]: entry for entry in catalog_entries}
    catalog_hash = sha256(CATALOG_PATH.read_bytes())
    plan_hash = sha256(PLAN_PATH.read_bytes())

    decisions: list[dict[str, Any]] = []
    summary_rows: list[str] = []

    for index, (source, record) in enumerate(zip(first_four, plan_records), 1):
        address = source["composite_address"]
        require(record.get("expected_original_identifier") == source["original_identifier"], f"identifier mismatch at {address}")
        require(record.get("decision_stage") == "HOLD", f"non-HOLD stage in plan at {address}")
        require(record.get("applicability_state") == "UNKNOWN — HOLD", f"non-HOLD state in plan at {address}")

        catalog_ids = record.get("catalog_evidence_ids")
        require(isinstance(catalog_ids, list) and catalog_ids, f"catalog evidence IDs missing at {address}")
        require(len(catalog_ids) == len(set(catalog_ids)), f"duplicate catalog evidence IDs at {address}")

        evidence: list[dict[str, str]] = [
            evidence_entry(
                f"B001-SOURCE-{index:03d}",
                f"{INVENTORY_PATH.relative_to(REPO)}#{address}",
                source["envelope_hash"],
                "Preserves the exact historical claim, permanent address, source block, and immutable envelope identity without treating its old label as a current applicability decision.",
            )
        ]
        for catalog_id in catalog_ids:
            require(catalog_id in catalog_by_id, f"unknown catalog evidence ID at {address}: {catalog_id}")
            entry = catalog_by_id[catalog_id]
            evidence.append(
                evidence_entry(
                    f"B001-{catalog_id}-{index:03d}",
                    f"{CATALOG_PATH.relative_to(REPO)}#{catalog_id}",
                    f"sha256:{catalog_hash}#{catalog_id}",
                    "Applies the verified evidence-authority, freshness, scope, or claim-limit boundary registered by this catalog entry to the record-specific HOLD decision.",
                )
            )
        evidence.append(
            evidence_entry(
                f"B001-PLAN-{index:03d}",
                f"{PLAN_PATH.relative_to(REPO)}#{address}",
                f"sha256:{plan_hash}#{address}",
                "Records the reviewed record-specific reasoning, unresolved dependencies, HOLD reason, and reopening conditions used to construct this decision.",
            )
        )

        decision = {
            "composite_address": address,
            "source_inventory_sha256": EXPECTED_INVENTORY_SHA256,
            "source_envelope_hash": source["envelope_hash"],
            "source_block_hash": source["source_block_hash"],
            "decision_stage": "HOLD",
            "applicability_state": "UNKNOWN — HOLD",
            "applicability_evidence": evidence,
            "applicability_reasoning_summary": record["applicability_reasoning_summary"],
            "applicability_confidence": record["applicability_confidence"],
            "primary_destination": None,
            "secondary_destinations": [],
            "cross_cutting_laws": [],
            "semantic_cluster_ids": [],
            "routing_evidence": [],
            "routing_rationale": "",
            "routing_confidence": None,
            "expected_receiving_work": "",
            "expected_completion_evidence": "",
            "unresolved_dependencies": record["unresolved_dependencies"],
            "hold_reason": record["hold_reason"],
            "reopening_conditions": record["reopening_conditions"],
            "decision_version": "Packet-01.5-Applicability-Batch-001-v1",
            "decision_author": plan["decision_author"],
            "routing_decision_verifier": plan["decision_verifier"],
            "closure_state": "OPEN",
        }
        decisions.append(decision)
        summary_rows.append(
            f"| `{address}` | `{source['original_identifier']}` | `UNKNOWN — HOLD` | {record['applicability_confidence']} | {record['hold_reason']} |"
        )

    OUT_JSONL.write_text(
        "".join(json.dumps(decision, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for decision in decisions),
        encoding="utf-8",
    )

    md = f"""# Packet 01.5 — First Controlled Applicability Batch 001 v1

STATUS: BUILT — PENDING INDEPENDENT VERIFICATION
BATCH: `PACKET-01.5-APPLICABILITY-BATCH-001`
SOURCE ADDRESSES: `P01.5::B::0001` through `P01.5::B::0004`
APPLICABILITY DECISIONS BUILT: 4
CURRENT DEFECT OR LIMITATION: 0
ACTIVE CONDITIONAL RISK: 0
DORMANT FUTURE RISK: 0
OUT-OF-SCOPE CANDIDATE: 0
UNKNOWN — HOLD: 4
ROUTING ASSIGNMENTS: 0
SEMANTIC GROUPING ASSIGNMENTS: 0
SOURCE RECORDS REMOVED OR CLOSED: 0
PACKET 04 AUTHORIZED: NO

## Why all four records are HOLD

The four permanent records preserve historical claims and labels. The verified evidence catalog does not yet contain the current T4 source, packet-law, deployed-worker, endpoint, CORS, or runtime receipts required to affirm those claims today. Packet 01.5 law requires uncertainty to become `UNKNOWN — HOLD`, not a guessed current defect.

## Decisions

| Permanent address | Original ID | Applicability | Confidence | HOLD reason |
|---|---|---|---:|---|
{chr(10).join(summary_rows)}

## Preserved boundary

- The immutable 2,750-record source inventory was not changed.
- All destinations and routing-proof fields remain blank.
- No secondary destination, cross-cutting law, or semantic cluster was assigned.
- All four records remain `OPEN` and carry explicit dependencies and reopening conditions.
- This batch does not authorize implementation, routing, closure, Packet 04, or Batch 002.

## Required independent proof

The verifier must independently rerun the routing-start and evidence-catalog proofs, recompute inventory and decision hashes, validate the exact four-address selection, enforce the full decision contract, reject adversarial mutations, and prove the source inventory remains unchanged.

Stop after Batch 001 verification.

END PACKET 01.5 — FIRST CONTROLLED APPLICABILITY BATCH 001 v1
"""
    OUT_MD.write_text(md, encoding="utf-8")

    require(INVENTORY_PATH.read_bytes() == raw_before, "builder changed the immutable source inventory")
    print("PASS: built four Packet 01.5 Batch 001 HOLD decisions without routing or source mutation.")


if __name__ == "__main__":
    main()
