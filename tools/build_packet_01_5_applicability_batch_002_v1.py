#!/usr/bin/env python3
"""Build Packet 01.5 Applicability Batch 002 decision overlay.

Reads the verified Batch 002 selection and immutable source envelopes, then
writes four evidence-bound UNKNOWN — HOLD decisions into a separate overlay.
No source record, routing field, grouping, closure, implementation, or Packet 04
state is changed.
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

PLAN_PATH = APP / "Packet_01.5_Applicability_Batch_002_Plan_v1.json"
CATALOG_PATH = APP / "Packet_01.5_Applicability_Evidence_Catalog_v1.json"
SELECTION_PATH = APP / "Packet_01.5_Applicability_Batch_002_Selection_v1.json"
GATE_RECEIPT_PATH = AUDIT / "Packet_01.5_Applicability_Batch_002_Selection_Gate_Independent_Verification_v1.json"
INVENTORY_PATH = ROUTING / "Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
OUT_JSONL = APP / "Packet_01.5_Applicability_Decisions_Batch_002_v1.jsonl"
OUT_MD = AUDIT / "Packet_01.5_Applicability_Batch_002_v1.md"

EXPECTED_INVENTORY_SHA256 = "76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477"
EXPECTED_ADDRESS_SEQUENCE_SHA256 = "3d808e1ec3f163e4cb2ab7a15767563fe7c43b9920bcecde9abe711226220916"
EXPECTED_SELECTION_SHA256 = "33eebaeec7987c85d843b244a8e1fab5102c3f07117526e6feb05bf5cfe39ed0"
EXPECTED_ADDRESSES = [f"P01.5::B::{number:04d}" for number in range(5, 9)]
EXPECTED_IDENTIFIERS = ["AI-005", "AI-006", "AI-007", "AI-008"]


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
    inventory_raw_before = INVENTORY_PATH.read_bytes()
    require(sha256(inventory_raw_before) == EXPECTED_INVENTORY_SHA256, "source inventory hash changed")
    inventory_lines = inventory_raw_before.splitlines()
    require(len(inventory_lines) == 2750, "source inventory line count changed")
    inventory = [json.loads(line) for line in inventory_lines]
    by_address = {item["composite_address"]: item for item in inventory}
    require(len(by_address) == 2750, "source inventory addresses are not unique")

    address_hash = sha256(("\n".join(item["composite_address"] for item in inventory) + "\n").encode("utf-8"))
    require(address_hash == EXPECTED_ADDRESS_SEQUENCE_SHA256, "source address sequence changed")

    plan = load_object(PLAN_PATH)
    catalog = load_object(CATALOG_PATH)
    selection = load_object(SELECTION_PATH)
    gate_receipt = load_object(GATE_RECEIPT_PATH)

    require(sha256(SELECTION_PATH.read_bytes()) == EXPECTED_SELECTION_SHA256, "selection manifest hash changed")
    require(plan.get("batch_id") == "PACKET-01.5-APPLICABILITY-BATCH-002", "plan batch identity mismatch")
    require(plan.get("selected_addresses") == EXPECTED_ADDRESSES, "plan selected addresses mismatch")
    require(plan.get("expected_original_identifiers") == EXPECTED_IDENTIFIERS, "plan identifiers mismatch")
    require(plan.get("decision_author") != plan.get("decision_verifier"), "decision author and verifier are not distinct")
    require(gate_receipt.get("status") == "PASS_BATCH_002_SELECTION_GATE_AUTHORIZED", "selection gate is not PASS")
    require(gate_receipt.get("watch") == "NONE" and gate_receipt.get("blockers") == "NONE", "selection gate has watch or blocker")
    require(gate_receipt.get("selected_addresses") == EXPECTED_ADDRESSES, "selection gate address set changed")
    require(gate_receipt.get("batch_002_applicability_decisions_authorized") is True, "Batch 002 decisions are not authorized")
    require(gate_receipt.get("stop_before_routing") is True, "routing stop boundary missing")

    selected_records = selection.get("selected_records")
    require(isinstance(selected_records, list) and len(selected_records) == 4, "selection must contain four records")
    require([item.get("composite_address") for item in selected_records] == EXPECTED_ADDRESSES, "selection address order mismatch")
    require([item.get("original_identifier") for item in selected_records] == EXPECTED_IDENTIFIERS, "selection identifier order mismatch")

    selected_sources: list[dict[str, Any]] = []
    for selected in selected_records:
        address = selected["composite_address"]
        source = by_address.get(address)
        require(source is not None, f"selected address missing from source inventory: {address}")
        for field in ("source_set", "source_record_ordinal", "original_identifier", "envelope_hash", "source_block_hash"):
            require(selected[field] == source[field], f"selection/source mismatch at {address}: {field}")
        selected_sources.append(source)

    policy = plan.get("decision_policy")
    require(isinstance(policy, dict), "decision policy missing")
    require(policy.get("decision_stage") == "HOLD", "decision policy stage is not HOLD")
    require(policy.get("applicability_state") == "UNKNOWN — HOLD", "decision policy state is not UNKNOWN — HOLD")
    require(isinstance(policy.get("applicability_confidence"), int), "decision confidence is not an integer")

    catalog_entries = catalog.get("evidence_sources")
    require(isinstance(catalog_entries, list), "catalog evidence sources missing")
    catalog_by_id = {entry["evidence_id"]: entry for entry in catalog_entries}
    catalog_ids = policy.get("catalog_evidence_ids")
    require(isinstance(catalog_ids, list) and catalog_ids, "catalog evidence IDs missing")
    require(len(catalog_ids) == len(set(catalog_ids)), "catalog evidence IDs are duplicated")
    require(all(catalog_id in catalog_by_id for catalog_id in catalog_ids), "plan references unknown catalog evidence")

    catalog_hash = sha256(CATALOG_PATH.read_bytes())
    plan_hash = sha256(PLAN_PATH.read_bytes())
    gate_hash = sha256(GATE_RECEIPT_PATH.read_bytes())

    decisions: list[dict[str, Any]] = []
    rows: list[str] = []
    for index, source in enumerate(selected_sources, 1):
        address = source["composite_address"]
        historical_claim = source.get("harm_text")
        require(isinstance(historical_claim, str) and historical_claim.strip(), f"historical claim missing at {address}")

        evidence: list[dict[str, str]] = [
            evidence_entry(
                f"B002-SOURCE-{index:03d}",
                f"{INVENTORY_PATH.relative_to(REPO)}#{address}",
                source["envelope_hash"],
                "Preserves the exact historical claim and immutable source identity without promoting its historical labels into current truth.",
            ),
            evidence_entry(
                f"B002-SELECTION-{index:03d}",
                f"{SELECTION_PATH.relative_to(REPO)}#{address}",
                f"sha256:{EXPECTED_SELECTION_SHA256}#{address}",
                "Proves this permanent address is inside the independently authorized Batch 002 selection.",
            ),
            evidence_entry(
                f"B002-GATE-{index:03d}",
                f"{GATE_RECEIPT_PATH.relative_to(REPO)}#{address}",
                f"sha256:{gate_hash}#{address}",
                "Proves Batch 002 applicability-only decisions are authorized while routing remains prohibited.",
            ),
        ]
        for catalog_id in catalog_ids:
            evidence.append(
                evidence_entry(
                    f"B002-{catalog_id}-{index:03d}",
                    f"{CATALOG_PATH.relative_to(REPO)}#{catalog_id}",
                    f"sha256:{catalog_hash}#{catalog_id}",
                    "Applies the verified authority, freshness, privacy, or claim-limit boundary registered by this catalog entry.",
                )
            )
        evidence.append(
            evidence_entry(
                f"B002-PLAN-{index:03d}",
                f"{PLAN_PATH.relative_to(REPO)}#{address}",
                f"sha256:{plan_hash}#{address}",
                "Records the reviewed HOLD policy, missing-proof dependencies, reopening conditions, and stop boundary.",
            )
        )

        reasoning = (
            f'The permanent record preserves the historical claim: "{historical_claim}" '
            "The independently verified Batch 002 selection authorizes review of this address but makes no applicability judgment. "
            "No direct current T4 source, runtime, authoritative packet-law, deployment, or test receipt tied to this exact claim is present in the verified evidence layer. "
            "Historical labels, severity, and owner suggestions may not be promoted into current truth. Therefore the record remains UNKNOWN — HOLD."
        )
        hold_reason = (
            f'Current direct T4 evidence is insufficient to determine whether this exact historical claim is true now: "{historical_claim}"'
        )

        decision = {
            "composite_address": address,
            "source_inventory_sha256": EXPECTED_INVENTORY_SHA256,
            "source_envelope_hash": source["envelope_hash"],
            "source_block_hash": source["source_block_hash"],
            "decision_stage": "HOLD",
            "applicability_state": "UNKNOWN — HOLD",
            "applicability_evidence": evidence,
            "applicability_reasoning_summary": reasoning,
            "applicability_confidence": policy["applicability_confidence"],
            "primary_destination": None,
            "secondary_destinations": [],
            "cross_cutting_laws": [],
            "semantic_cluster_ids": [],
            "routing_evidence": [],
            "routing_rationale": "",
            "routing_confidence": None,
            "expected_receiving_work": "",
            "expected_completion_evidence": "",
            "unresolved_dependencies": policy["unresolved_dependencies"],
            "hold_reason": hold_reason,
            "reopening_conditions": policy["reopening_conditions"],
            "decision_version": "Packet-01.5-Applicability-Batch-002-v1",
            "decision_author": plan["decision_author"],
            "routing_decision_verifier": plan["decision_verifier"],
            "closure_state": "OPEN",
        }
        decisions.append(decision)
        rows.append(
            f"| `{address}` | `{source['original_identifier']}` | `UNKNOWN — HOLD` | {policy['applicability_confidence']} | {historical_claim} |"
        )

    OUT_JSONL.write_text(
        "".join(json.dumps(decision, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for decision in decisions),
        encoding="utf-8",
    )

    OUT_MD.write_text(
        f"""# Packet 01.5 — Applicability Batch 002 v1

STATUS: BUILT — PENDING INDEPENDENT VERIFICATION
BATCH: `PACKET-01.5-APPLICABILITY-BATCH-002`
SOURCE ADDRESSES: `P01.5::B::0005` through `P01.5::B::0008`
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

## Decisions

| Permanent address | Original ID | Applicability | Confidence | Preserved historical claim |
|---|---|---|---:|---|
{chr(10).join(rows)}

## Decision basis

Each selected envelope contains a historical claim, but the verified evidence layer does not yet contain direct current T4 proof or disproof tied to that exact claim. The old state, severity, and owner fields remain historical data rather than current applicability evidence. Each record therefore receives an evidence-bound `UNKNOWN — HOLD` decision with explicit dependencies and reopening conditions.

## Preserved boundary

- The immutable 2,750-record source inventory was not changed.
- All destinations and routing-proof fields remain blank.
- No secondary destination, cross-cutting law, or semantic cluster was assigned.
- All four records remain `OPEN`.
- This batch does not authorize routing, closure, implementation, Packet 04, or Batch 003 decisions.

Stop after independent verification of Batch 002.

END PACKET 01.5 — APPLICABILITY BATCH 002 v1
""",
        encoding="utf-8",
    )

    require(INVENTORY_PATH.read_bytes() == inventory_raw_before, "builder changed the immutable source inventory")
    print("PASS: built four Packet 01.5 Batch 002 HOLD decisions without routing or source mutation.")


if __name__ == "__main__":
    main()
