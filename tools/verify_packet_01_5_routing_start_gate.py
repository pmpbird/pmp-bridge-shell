#!/usr/bin/env python3
"""Independently verify the Packet 01.5 Routing-Start Authorization Gate.

This verifier checks the already verified blank inventory and the gate-control
schema. It does not classify, route, combine, remove, or close any record.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "audit"
ROUTING = AUDIT / "routing-inventory"

GATE_JSON = AUDIT / "Packet_01.5_Routing_Start_Authorization_Gate_v1.json"
INVENTORY_VERIFY_JSON = AUDIT / "Packet_01.5_Blank_Routing_Inventory_Independent_Verification_v1.json"
INVENTORY_JSONL = ROUTING / "Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
INVENTORY_MANIFEST = ROUTING / "Packet_01.5_Blank_Routing_Inventory_v1.manifest.json"
OUT_JSON = AUDIT / "Packet_01.5_Routing_Start_Authorization_Independent_Verification_v1.json"
OUT_MD = AUDIT / "Packet_01.5_Routing_Start_Authorization_Independent_Verification_v1.md"
STATUS_MD = AUDIT / "Packet_01.5_Routing_Status_v75.md"

EXPECTED_STATES = [
    "CURRENT_DEFECT",
    "ACTIVE_CONDITIONAL_RISK",
    "DORMANT_FUTURE_RISK",
    "OUT_OF_SCOPE_CANDIDATE",
]
EXPECTED_EVIDENCE_TYPES = [
    "CURRENT_CONTACT",
    "PLANNED_CONTACT",
    "ABSENT_CONTACT",
    "SCOPE_EXCLUSION",
]
EXPECTED_PHASES = [
    "PHASE_A_APPLICABILITY_CLASSIFICATION",
    "PHASE_B_DESTINATION_PREPARATION",
    "PHASE_C_OWNER_ROUTING_VERIFICATION",
]
EXPECTED_IMMUTABLE = [
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
]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"not a JSON object: {path}")
    return value


def main() -> None:
    gate = load_json(GATE_JSON)
    verified = load_json(INVENTORY_VERIFY_JSON)
    manifest = load_json(INVENTORY_MANIFEST)
    raw = INVENTORY_JSONL.read_bytes()

    require(gate.get("packet") == "01.5", "gate packet mismatch")
    require(gate.get("gate") == "routing_start_authorization", "gate identity mismatch")
    require(gate.get("version") == 1, "gate version mismatch")
    require(gate.get("watch") == "NONE", "gate contains a watch")
    require(gate.get("blockers") == "NONE_KNOWN", "gate contains a known blocker")

    require(verified.get("status") == "PASS", "blank inventory verification did not pass")
    require(verified.get("watch") == "NONE", "blank inventory verification has a watch")
    require(verified.get("blockers") == "NONE", "blank inventory verification has a blocker")
    require(verified.get("routing_start_ready") is True, "blank inventory is not routing-start ready")
    require(verified.get("baseline_records") == 122, "baseline count mismatch")
    require(verified.get("provisional_records") == 2628, "provisional count mismatch")
    require(verified.get("combined_records") == 2750, "combined count mismatch")
    require(verified.get("unique_addresses") == 2750, "unique-address count mismatch")
    require(verified.get("source_to_envelope_bijection") == "PASS", "bijection proof missing")

    inventory_meta = manifest.get("inventory_jsonl", {})
    require(inventory_meta.get("bytes") == len(raw), "inventory byte count mismatch")
    require(inventory_meta.get("sha256") == sha256(raw), "inventory hash mismatch")
    require(inventory_meta.get("lines") == 2750, "inventory manifest line count mismatch")

    lines = raw.splitlines()
    require(len(lines) == 2750, "inventory line count mismatch")
    addresses: list[str] = []
    for number, line in enumerate(lines, 1):
        envelope = json.loads(line)
        require(isinstance(envelope, dict), f"inventory line {number} is not an object")
        address = envelope.get("composite_address")
        require(isinstance(address, str) and address, f"address missing at line {number}")
        addresses.append(address)
        require(envelope.get("applicability_state") == "UNCLASSIFIED", f"applicability already set at {address}")
        require(envelope.get("routing_state") == "UNROUTED", f"routing already set at {address}")
        require(envelope.get("primary_destination") is None, f"primary destination already set at {address}")
        for field in (
            "applicability_evidence",
            "secondary_destinations",
            "cross_cutting_laws",
            "watch_triggers",
            "semantic_cluster_ids",
        ):
            require(envelope.get(field) == [], f"field {field} is not blank at {address}")
    require(len(set(addresses)) == 2750, "inventory addresses are not unique")

    required_inventory = gate.get("required_inventory", {})
    require(required_inventory.get("baseline") == 122, "gate baseline requirement mismatch")
    require(required_inventory.get("provisional") == 2628, "gate provisional requirement mismatch")
    require(required_inventory.get("combined") == 2750, "gate combined requirement mismatch")
    require(required_inventory.get("unique_addresses") == 2750, "gate unique-address requirement mismatch")
    for field in (
        "source_to_envelope_bijection",
        "exact_original_heading_match",
        "exact_original_body_match",
        "source_file_hash_match",
        "source_block_hash_match",
        "envelope_hash_match",
        "gzip_reverse_reconstruction",
    ):
        require(required_inventory.get(field) == "PASS", f"gate proof requirement missing: {field}")

    blank = gate.get("required_blank_state", {})
    require(blank.get("applicability_state") == "UNCLASSIFIED", "gate applicability blank state mismatch")
    require(blank.get("routing_state") == "UNROUTED", "gate routing blank state mismatch")
    for field in (
        "primary_destinations_populated",
        "secondary_destinations_populated",
        "cross_cutting_laws_populated",
        "watch_triggers_populated",
        "semantic_cluster_references_populated",
        "source_records_removed",
        "source_records_closed",
    ):
        require(blank.get(field) == 0, f"gate blank-state count is not zero: {field}")

    require(gate.get("immutable_fields") == EXPECTED_IMMUTABLE, "immutable-field list mismatch")
    require(gate.get("applicability_states") == EXPECTED_STATES, "applicability-state vocabulary mismatch")
    require(gate.get("evidence_types") == EXPECTED_EVIDENCE_TYPES, "evidence-type vocabulary mismatch")
    require(gate.get("authorized_sequence") == EXPECTED_PHASES, "authorized phase order mismatch")

    evidence_fields = gate.get("required_evidence_fields", [])
    require(len(evidence_fields) == 6 and len(set(evidence_fields)) == 6, "evidence-field schema mismatch")
    batch = gate.get("batch_transaction", {})
    require(batch.get("maximum_envelopes") == 100, "batch maximum mismatch")
    for field in (
        "verified_parent_hash_required",
        "versioned_child_inventory_required",
        "parent_preserved",
        "count_equality_required",
        "address_equality_required",
        "immutable_field_equality_required",
        "hash_chain_required",
        "partial_acceptance_prohibited",
        "blank_inventory_is_rollback_point",
    ):
        require(batch.get(field) is True, f"batch control missing: {field}")

    semantic = gate.get("semantic_comparison", {})
    for field in (
        "references_only",
        "source_envelopes_remain_individual",
        "counts_remain_unchanged",
        "original_wording_remains_unchanged",
        "source_records_remain_preserved",
        "records_remain_open",
        "clusters_are_not_destinations",
    ):
        require(semantic.get(field) is True, f"semantic control missing: {field}")

    result = {
        "packet": "01.5",
        "verification": "routing_start_authorization_independent",
        "version": 1,
        "verification_date": date.today().isoformat(),
        "status": "PASS_ROUTING_START_AUTHORIZED",
        "watch": "NONE",
        "blockers": "NONE",
        "inventory_sha256": sha256(raw),
        "combined_envelopes": 2750,
        "unique_addresses": 2750,
        "source_to_envelope_bijection": "PASS",
        "blank_applicability_state": "PASS",
        "blank_routing_state": "PASS",
        "immutable_source_controls": "PASS",
        "applicability_vocabulary": "PASS",
        "evidence_schema": "PASS",
        "phase_order": "PASS",
        "batch_transaction_controls": "PASS",
        "non_loss_semantic_controls": "PASS",
        "routing_start_authorized": True,
        "first_authorized_phase": "PHASE_A_APPLICABILITY_CLASSIFICATION",
        "routing_assignments_completed": 0,
        "applicability_classifications_completed": 0,
        "source_records_removed": 0,
        "source_records_closed": 0,
        "packet_04_authorized": False,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join([
        "# Packet 01.5 — Routing-Start Authorization Independent Verification v1",
        "",
        "STATUS: PASS — ROUTING START AUTHORIZED",
        "WATCH: NONE",
        "BLOCKERS: NONE",
        "ROUTING ASSIGNMENTS COMPLETED: 0",
        "APPLICABILITY CLASSIFICATIONS COMPLETED: 0",
        "",
        "## Preconditions",
        "",
        "- Verified blank inventory: PASS",
        "- Combined envelopes: 2750",
        "- Unique addresses: 2750",
        "- Source-to-envelope bijection: PASS",
        "- Blank applicability state: PASS",
        "- Blank routing state: PASS",
        "- Source records removed: 0",
        "- Source records closed: 0",
        "",
        "## Control verification",
        "",
        "- Immutable source fields: PASS",
        "- Four-state applicability vocabulary: PASS",
        "- Record-specific evidence schema: PASS",
        "- Classification-before-routing order: PASS",
        "- Maximum 100-envelope batch transaction: PASS",
        "- Parent inventory preservation and rollback: PASS",
        "- Non-loss semantic references: PASS",
        "",
        "## Authorization result",
        "",
        "Authorized now:",
        "",
        "- Phase A applicability classification",
        "- evidence-backed destination-candidate preparation after classification",
        "- non-loss semantic-cluster references",
        "- independent verification of every batch",
        "",
        "Still not authorized:",
        "",
        "- source-record combination or removal",
        "- individual record closure",
        "- Packet 04",
        "- blanket treatment of all records as current defects",
        "- routing without applicability evidence",
        "",
        "FINAL RESULT: `PASS — ROUTING START AUTHORIZED`",
        "",
        "WATCH: NONE",
        "",
        "BLOCKERS: NONE",
        "",
        "END PACKET 01.5 — ROUTING-START AUTHORIZATION INDEPENDENT VERIFICATION v1",
        "",
    ]), encoding="utf-8")

    STATUS_MD.write_text("\n".join([
        "# Packet 01.5 — Routing Status v75",
        "",
        "STATUS: ROUTING START AUTHORIZED",
        "WATCH: NONE",
        "BLOCKERS: NONE",
        "FIRST ACTIVE PHASE: APPLICABILITY CLASSIFICATION",
        "ROUTING ASSIGNMENTS COMPLETED: 0",
        "APPLICABILITY CLASSIFICATIONS COMPLETED: 0",
        "SEMANTIC COMBINATION: NOT AUTHORIZED",
        "INDIVIDUAL RECORD CLOSURE: NOT AUTHORIZED",
        "PACKET 04: NOT AUTHORIZED",
        "",
        "## Preserved inventory",
        "",
        "- Baseline envelopes: 122",
        "- Provisional envelopes: 2628",
        "- Total envelopes: 2750",
        "- Unique addresses: 2750",
        "- Blank inventory remains the rollback point",
        "",
        "## Authorized work",
        "",
        "Applicability classification may now begin in verified batches of no more than 100 envelopes. Every decision requires record-specific current-contact, planned-contact, absent-contact, or scope-exclusion evidence.",
        "",
        "Destination candidates may be prepared only after the relevant envelope has an accepted applicability classification. Source wording, source hashes, addresses, and the individual envelope count remain immutable.",
        "",
        "## Next required action",
        "",
        "Build and verify the canonical project-contact evidence catalog, then classify the first applicability batch without assigning final owner destinations.",
        "",
        "END PACKET 01.5 — ROUTING STATUS v75",
        "",
    ]), encoding="utf-8")
    print("PASS — Packet 01.5 routing start authorized with no watch or blockers")


if __name__ == "__main__":
    main()
