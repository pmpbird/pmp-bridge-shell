#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = "0297a3289de4e12a341a115a58c3fd51489bdcf7"

QUEUE_PATH = "audit/applicability/Packet_01.5_Scalable_Pass_002_Evidence_Queue_v1.jsonl"
WINDOW_PATH = "audit/applicability/Packet_01.5_Scalable_Pass_002_Window_v1.json"
INVENTORY_PATH = "audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
OVERLAY_PATH = "audit/routing-inventory/Packet_01.5_Applicability_Inventory_v11_Pass_002.jsonl"

EXPECTED_HASHES = {
    "inventory_sha256": "76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477",
    "overlay_sha256": "465ed8e338c7d32ce3c460960d8637855c65d7018d7f5c90db12c915a1c88654",
    "queue_sha256": "0c4b9660151448fdb03b328e3fa41d0e98e679d0233759f651e90eae3a5a0e96",
    "window_sha256": "eb75fa865feab6e3017f6d93938fb71ff2740870b618d513cafa86f20382dc28",
}

FAMILIES = [
    {
        "family": "CURRENT_RUNTIME_SOURCE",
        "count": 26,
        "receipt_path": "audit/Packet_01.5_Pass_002_Current_Runtime_Family_Independent_Verification_v1.json",
        "receipt_blob_sha": "5942c78a331d078b11364f46313079df3d9e887f",
        "decisions_path": "audit/applicability/Packet_01.5_Pass_002_Current_Runtime_Family_Decisions_v1.jsonl",
        "remaining_path": "audit/applicability/Packet_01.5_Pass_002_Current_Runtime_Family_Remaining_Queue_v1.jsonl",
    },
    {
        "family": "PRIVATE_OR_UNCAPTURED_EVIDENCE",
        "count": 1,
        "receipt_path": "audit/Packet_01.5_Pass_002_Private_Uncaptured_Family_Independent_Verification_v1.json",
        "receipt_blob_sha": "92045d7fa63839582ec518066033d58fede2ed8c",
        "decisions_path": "audit/applicability/Packet_01.5_Pass_002_Private_Uncaptured_Family_Decisions_v1.jsonl",
        "remaining_path": "audit/applicability/Packet_01.5_Pass_002_Private_Uncaptured_Family_Remaining_Queue_v1.jsonl",
    },
    {
        "family": "DEPLOYMENT_AND_LIVE_BEHAVIOR",
        "count": 2,
        "receipt_path": "audit/Packet_01.5_Pass_002_Deployment_Live_Family_Independent_Verification_v1.json",
        "receipt_blob_sha": "84d580215ee70c3c1e6b0b5a2d606c0c5d690eac",
        "decisions_path": "audit/applicability/Packet_01.5_Pass_002_Deployment_Live_Family_Decisions_v1.jsonl",
        "remaining_path": "audit/applicability/Packet_01.5_Pass_002_Deployment_Live_Family_Remaining_Queue_v1.jsonl",
    },
    {
        "family": "DEPENDENCY_OR_PLATFORM_STATE",
        "count": 4,
        "receipt_path": "audit/Packet_01.5_Pass_002_Dependency_Platform_Family_Independent_Verification_v1.json",
        "receipt_blob_sha": "7ccb9a57451e80ced1a88de47406e92b7dc0b486",
        "decisions_path": "audit/applicability/Packet_01.5_Pass_002_Dependency_Platform_Family_Decisions_v1.jsonl",
        "remaining_path": "audit/applicability/Packet_01.5_Pass_002_Dependency_Platform_Family_Remaining_Queue_v1.jsonl",
    },
    {
        "family": "CROSS_SOURCE_CONFLICT",
        "count": 4,
        "receipt_path": "audit/Packet_01.5_Pass_002_Cross_Source_Conflict_Family_Independent_Verification_v1.json",
        "receipt_blob_sha": "3e7df143344d51b4be07e3cd25cd6d3be78edee9",
        "decisions_path": "audit/applicability/Packet_01.5_Pass_002_Cross_Source_Conflict_Family_Decisions_v1.jsonl",
        "remaining_path": "audit/applicability/Packet_01.5_Pass_002_Cross_Source_Conflict_Family_Remaining_Queue_v1.jsonl",
    },
    {
        "family": "AUTHORITATIVE_PACKET_LAW",
        "count": 6,
        "receipt_path": "audit/Packet_01.5_Pass_002_Authoritative_Packet_Law_Family_Independent_Verification_v1.json",
        "receipt_blob_sha": "10e46b2498a3bff34bbd4a5afd82a125be3fc0b8",
        "decisions_path": "audit/applicability/Packet_01.5_Pass_002_Authoritative_Packet_Law_Family_Decisions_v1.jsonl",
        "remaining_path": "audit/applicability/Packet_01.5_Pass_002_Authoritative_Packet_Law_Family_Remaining_Queue_v1.jsonl",
    },
    {
        "family": "OTHER_RECORD_SPECIFIC_PROOF",
        "count": 79,
        "receipt_path": "audit/Packet_01.5_Pass_002_Other_Record_Specific_Proof_Family_Independent_Verification_v1.json",
        "receipt_blob_sha": "6078c31e0990e7a4d7da04574474807f57e44494",
        "decisions_path": "audit/applicability/Packet_01.5_Pass_002_Other_Record_Specific_Proof_Family_Decisions_v1.jsonl",
        "remaining_path": "audit/applicability/Packet_01.5_Pass_002_Other_Record_Specific_Proof_Family_Remaining_Queue_v1.jsonl",
    },
]

MANIFEST_PATH = ROOT / "audit/Packet_01.5_Pass_002_Closure_Manifest_v1.json"
COVERAGE_PATH = ROOT / "audit/Packet_01.5_Pass_002_Closure_Coverage_v1.json"
STATUS_PATH = ROOT / "audit/Packet_01.5_Pass_002_Closure_Status_v1.md"


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.decode(errors="replace").strip()


def show(path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{ANCHOR}:{path}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def json_rows(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode().splitlines() if line.strip()]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def identity_fields(record: dict) -> dict:
    keys = (
        "composite_address",
        "inventory_position",
        "source_record_ordinal",
        "original_identifier",
        "preserved_claim",
        "source_path",
        "source_pass",
        "source_set",
        "source_file_hash",
        "source_envelope_hash",
        "source_block_hash",
        "queue_id",
        "evidence_domain",
        "prior_applicability_state",
        "prior_applicability_decision_hash",
        "state_preservation_rule",
    )
    return {key: record[key] for key in keys}


def derive_closure() -> tuple[dict, dict, str]:
    queue_bytes = show(QUEUE_PATH)
    window_bytes = show(WINDOW_PATH)
    inventory_bytes = show(INVENTORY_PATH)
    overlay_bytes = show(OVERLAY_PATH)

    queue = sorted(json_rows(queue_bytes), key=lambda row: row["inventory_position"])
    inventory = json_rows(inventory_bytes)
    overlay = json_rows(overlay_bytes)

    assert len(queue) == 122
    assert len({row["composite_address"] for row in queue}) == 122
    assert len(inventory) == 2750
    assert len(overlay) == 2750
    assert sha256(queue_bytes) == EXPECTED_HASHES["queue_sha256"]
    assert sha256(window_bytes) == EXPECTED_HASHES["window_sha256"]
    assert sha256(inventory_bytes) == EXPECTED_HASHES["inventory_sha256"]
    assert sha256(overlay_bytes) == EXPECTED_HASHES["overlay_sha256"]

    for row in queue:
        assert row["prior_applicability_state"] == "UNCLASSIFIED"
        assert row["prior_applicability_decision_hash"] is None
        assert row["state_preservation_rule"] == "PRESERVE_CURRENT_STATE_UNTIL_DIRECT_MERGED_EVIDENCE_SUPPORTS_A_DECISION"

    authoritative_by_address = {row["composite_address"]: row for row in queue}
    family_entries: list[dict] = []
    covered_addresses: list[str] = []

    for family in FAMILIES:
        receipt_bytes = show(family["receipt_path"])
        receipt = json.loads(receipt_bytes)
        receipt_blob = git("rev-parse", f"{ANCHOR}:{family['receipt_path']}")
        decisions_bytes = show(family["decisions_path"])
        remaining_bytes = show(family["remaining_path"])
        decisions = json_rows(decisions_bytes)
        remaining = sorted(json_rows(remaining_bytes), key=lambda row: row["inventory_position"])
        authoritative_rows = [row for row in queue if row["evidence_domain"] == family["family"]]

        assert receipt_blob == family["receipt_blob_sha"]
        assert receipt["family"] == family["family"]
        assert receipt["family_records"] == family["count"]
        assert receipt["decisions_created"] == 0
        assert receipt["remaining_exact_queues"] == family["count"]
        assert receipt["unknown_hold_created"] == 0
        assert len(authoritative_rows) == family["count"]
        assert decisions == []
        assert len(remaining) == family["count"]
        assert sha256(decisions_bytes) == receipt["decisions_sha256"]
        assert sha256(remaining_bytes) == receipt["remaining_queue_sha256"]

        expected_addresses = [row["composite_address"] for row in authoritative_rows]
        actual_addresses = [row["composite_address"] for row in remaining]
        assert actual_addresses == expected_addresses

        for authoritative, unresolved in zip(authoritative_rows, remaining):
            assert unresolved["family_result"] == "REMAIN_QUEUED"
            assert unresolved["prior_state_preserved"] is True
            for key, value in authoritative.items():
                assert unresolved[key] == value

        covered_addresses.extend(actual_addresses)
        family_entries.append(
            {
                "family": family["family"],
                "family_records": family["count"],
                "decisions": 0,
                "remaining_exact_queues": family["count"],
                "automatic_unknown_hold": 0,
                "receipt_path": family["receipt_path"],
                "receipt_blob_sha": receipt_blob,
                "receipt_sha256": sha256(receipt_bytes),
                "decisions_path": family["decisions_path"],
                "decisions_sha256": sha256(decisions_bytes),
                "remaining_queue_path": family["remaining_path"],
                "remaining_queue_sha256": sha256(remaining_bytes),
                "permanent_addresses": actual_addresses,
            }
        )

    authoritative_addresses = [row["composite_address"] for row in queue]
    assert len(covered_addresses) == 122
    assert len(set(covered_addresses)) == 122
    assert sorted(covered_addresses, key=lambda address: authoritative_by_address[address]["inventory_position"]) == authoritative_addresses
    assert sum(entry["family_records"] for entry in family_entries) == 122
    assert sum(entry["decisions"] for entry in family_entries) == 0
    assert sum(entry["remaining_exact_queues"] for entry in family_entries) == 122
    assert sum(entry["automatic_unknown_hold"] for entry in family_entries) == 0

    manifest = {
        "packet": "01.5",
        "pass": "002",
        "artifact": "closure_manifest",
        "version": 1,
        "authoritative_base": ANCHOR,
        "closure_scope": "PASS_002_PROCESSING_BOUNDARY_ONLY",
        "pass_002_processing_boundary_closed_if_merged": True,
        "remaining_evidence_queues_closed": False,
        "remaining_evidence_queues_preserved": True,
        "pass_003_started": False,
        "authoritative_inputs": {
            "inventory_path": INVENTORY_PATH,
            "inventory_sha256": sha256(inventory_bytes),
            "inventory_records": len(inventory),
            "overlay_path": OVERLAY_PATH,
            "overlay_sha256": sha256(overlay_bytes),
            "overlay_records": len(overlay),
            "evidence_queue_path": QUEUE_PATH,
            "evidence_queue_sha256": sha256(queue_bytes),
            "evidence_queue_records": len(queue),
            "window_path": WINDOW_PATH,
            "window_sha256": sha256(window_bytes),
        },
        "families": family_entries,
        "family_count": 7,
        "processed_permanent_addresses": authoritative_addresses,
        "processed_permanent_address_count": 122,
        "unprocessed_permanent_address_count": 0,
        "decisions": 0,
        "remaining_exact_evidence_queues": 122,
        "automatic_unknown_hold": 0,
        "all_prior_states_unclassified": True,
        "all_prior_decision_hashes_null": True,
        "all_preserved_claims_and_identities_match_authoritative_queue": True,
        "all_remaining_evidence_queues_present_and_unchanged": True,
        "no_duplicate_addresses": True,
        "no_omitted_addresses": True,
    }

    write_json(MANIFEST_PATH, manifest)
    manifest_sha = sha256(MANIFEST_PATH.read_bytes())

    coverage = {
        "packet": "01.5",
        "pass": "002",
        "artifact": "closure_coverage",
        "version": 1,
        "authoritative_base": ANCHOR,
        "closure_manifest_sha256": manifest_sha,
        "family_count": 7,
        "family_record_counts": {entry["family"]: entry["family_records"] for entry in family_entries},
        "family_record_total": 122,
        "processed_records": 122,
        "unprocessed_records": 0,
        "decisions": 0,
        "remaining_exact_evidence_queues": 122,
        "automatic_unknown_hold": 0,
        "unique_addresses": 122,
        "duplicate_addresses": 0,
        "omitted_addresses": 0,
        "all_addresses_covered_once": True,
        "all_prior_states_unclassified": True,
        "all_prior_decision_hashes_null": True,
        "all_remaining_evidence_queues_preserved": True,
        "source_inventory_sha256": sha256(inventory_bytes),
        "source_inventory_count": len(inventory),
        "pass_002_overlay_sha256": sha256(overlay_bytes),
        "pass_002_overlay_count": len(overlay),
        "queue_sha256": sha256(queue_bytes),
        "window_sha256": sha256(window_bytes),
        "pass_002_reconciliation_exact": True,
        "pass_002_processing_boundary_closed_if_merged": True,
        "remaining_evidence_queues_closed": False,
        "pass_003_started": False,
        "records_modified": 0,
        "claims_modified": 0,
        "identities_modified": 0,
        "remaining_queues_modified": 0,
        "application_behavior_modified": False,
        "configuration_modified": False,
        "dependencies_modified": False,
        "deployment_modified": False,
        "runtime_state_modified": False,
        "routing_assignments": 0,
        "destination_assignments": 0,
        "grouping_assignments": 0,
        "source_records_removed_or_closed": 0,
        "evidence_queues_removed_or_closed": 0,
        "applicability_reclassifications": 0,
        "implementation_actions": 0,
        "packet_04_actions": 0,
    }

    write_json(COVERAGE_PATH, coverage)

    status = f"""# Packet 01.5 Scalable Pass 002 Closure v1

STATUS: BUILT — PENDING INDEPENDENT VERIFICATION

- Authoritative base: `{ANCHOR}`
- Closure scope: Pass 002 processing boundary only
- Completed families: 7
- Processed permanent addresses: 122
- Unprocessed permanent addresses: 0
- Decisions: 0
- Exact remaining-evidence queues preserved: 122
- Automatic `UNKNOWN — HOLD`: 0
- Duplicate addresses: 0
- Omitted addresses: 0
- Immutable inventory: 2,750 records unchanged
- Pass 002 overlay: 2,750 records unchanged
- Pass 003 begun: no

This closure does not close, remove, resolve, reclassify, or discard any remaining-evidence queue or source record. It closes only the Pass 002 processing boundary after all seven family subpasses covered all 122 authoritative records exactly once.
"""
    STATUS_PATH.write_text(status)
    return manifest, coverage, status


def main() -> None:
    git("cat-file", "-e", f"{ANCHOR}^{{commit}}")
    manifest, coverage, _ = derive_closure()
    print(
        json.dumps(
            {
                "status": "BUILT",
                "families": manifest["family_count"],
                "processed_records": coverage["processed_records"],
                "unprocessed_records": coverage["unprocessed_records"],
                "decisions": coverage["decisions"],
                "remaining_exact_evidence_queues": coverage["remaining_exact_evidence_queues"],
                "automatic_unknown_hold": coverage["automatic_unknown_hold"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
