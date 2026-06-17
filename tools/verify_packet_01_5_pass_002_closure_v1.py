#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
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
    ("CURRENT_RUNTIME_SOURCE", 26,
     "audit/Packet_01.5_Pass_002_Current_Runtime_Family_Independent_Verification_v1.json",
     "5942c78a331d078b11364f46313079df3d9e887f",
     "audit/applicability/Packet_01.5_Pass_002_Current_Runtime_Family_Decisions_v1.jsonl",
     "audit/applicability/Packet_01.5_Pass_002_Current_Runtime_Family_Remaining_Queue_v1.jsonl"),
    ("PRIVATE_OR_UNCAPTURED_EVIDENCE", 1,
     "audit/Packet_01.5_Pass_002_Private_Uncaptured_Family_Independent_Verification_v1.json",
     "92045d7fa63839582ec518066033d58fede2ed8c",
     "audit/applicability/Packet_01.5_Pass_002_Private_Uncaptured_Family_Decisions_v1.jsonl",
     "audit/applicability/Packet_01.5_Pass_002_Private_Uncaptured_Family_Remaining_Queue_v1.jsonl"),
    ("DEPLOYMENT_AND_LIVE_BEHAVIOR", 2,
     "audit/Packet_01.5_Pass_002_Deployment_Live_Family_Independent_Verification_v1.json",
     "84d580215ee70c3c1e6b0b5a2d606c0c5d690eac",
     "audit/applicability/Packet_01.5_Pass_002_Deployment_Live_Family_Decisions_v1.jsonl",
     "audit/applicability/Packet_01.5_Pass_002_Deployment_Live_Family_Remaining_Queue_v1.jsonl"),
    ("DEPENDENCY_OR_PLATFORM_STATE", 4,
     "audit/Packet_01.5_Pass_002_Dependency_Platform_Family_Independent_Verification_v1.json",
     "7ccb9a57451e80ced1a88de47406e92b7dc0b486",
     "audit/applicability/Packet_01.5_Pass_002_Dependency_Platform_Family_Decisions_v1.jsonl",
     "audit/applicability/Packet_01.5_Pass_002_Dependency_Platform_Family_Remaining_Queue_v1.jsonl"),
    ("CROSS_SOURCE_CONFLICT", 4,
     "audit/Packet_01.5_Pass_002_Cross_Source_Conflict_Family_Independent_Verification_v1.json",
     "3e7df143344d51b4be07e3cd25cd6d3be78edee9",
     "audit/applicability/Packet_01.5_Pass_002_Cross_Source_Conflict_Family_Decisions_v1.jsonl",
     "audit/applicability/Packet_01.5_Pass_002_Cross_Source_Conflict_Family_Remaining_Queue_v1.jsonl"),
    ("AUTHORITATIVE_PACKET_LAW", 6,
     "audit/Packet_01.5_Pass_002_Authoritative_Packet_Law_Family_Independent_Verification_v1.json",
     "10e46b2498a3bff34bbd4a5afd82a125be3fc0b8",
     "audit/applicability/Packet_01.5_Pass_002_Authoritative_Packet_Law_Family_Decisions_v1.jsonl",
     "audit/applicability/Packet_01.5_Pass_002_Authoritative_Packet_Law_Family_Remaining_Queue_v1.jsonl"),
    ("OTHER_RECORD_SPECIFIC_PROOF", 79,
     "audit/Packet_01.5_Pass_002_Other_Record_Specific_Proof_Family_Independent_Verification_v1.json",
     "6078c31e0990e7a4d7da04574474807f57e44494",
     "audit/applicability/Packet_01.5_Pass_002_Other_Record_Specific_Proof_Family_Decisions_v1.jsonl",
     "audit/applicability/Packet_01.5_Pass_002_Other_Record_Specific_Proof_Family_Remaining_Queue_v1.jsonl"),
]

MANIFEST_PATH = ROOT / "audit/Packet_01.5_Pass_002_Closure_Manifest_v1.json"
COVERAGE_PATH = ROOT / "audit/Packet_01.5_Pass_002_Closure_Coverage_v1.json"
RECEIPT_PATH = ROOT / "audit/Packet_01.5_Pass_002_Closure_Independent_Verification_v1.json"
STATUS_PATH = ROOT / "audit/Packet_01.5_Pass_002_Closure_Status_v1.md"

ALLOWED_FILES = {
    ".github/workflows/packet_01_5_pass_002_closure.yml",
    "tools/build_packet_01_5_pass_002_closure_v1.py",
    "tools/verify_packet_01_5_pass_002_closure_v1.py",
    str(MANIFEST_PATH.relative_to(ROOT)),
    str(COVERAGE_PATH.relative_to(ROOT)),
    str(RECEIPT_PATH.relative_to(ROOT)),
    str(STATUS_PATH.relative_to(ROOT)),
}

PRIVATE_FIELD_NAMES = {
    "private_value",
    "private_values",
    "raw_private_data",
    "private_memory_contents",
    "personal_data",
}


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


def rows(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode().splitlines() if line.strip()]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def scan_private_fields(value) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            assert key.lower() not in PRIVATE_FIELD_NAMES
            scan_private_fields(child)
    elif isinstance(value, list):
        for child in value:
            scan_private_fields(child)


def derive_expected() -> tuple[dict, dict, str, list[dict]]:
    queue_bytes = show(QUEUE_PATH)
    window_bytes = show(WINDOW_PATH)
    inventory_bytes = show(INVENTORY_PATH)
    overlay_bytes = show(OVERLAY_PATH)
    queue = sorted(rows(queue_bytes), key=lambda row: row["inventory_position"])
    inventory = rows(inventory_bytes)
    overlay = rows(overlay_bytes)

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

    by_address = {row["composite_address"]: row for row in queue}
    family_entries = []
    covered = []

    for family_name, count, receipt_path, receipt_blob, decisions_path, remaining_path in FAMILIES:
        receipt_bytes = show(receipt_path)
        receipt = json.loads(receipt_bytes)
        actual_receipt_blob = git("rev-parse", f"{ANCHOR}:{receipt_path}")
        decisions_bytes = show(decisions_path)
        remaining_bytes = show(remaining_path)
        decisions = rows(decisions_bytes)
        remaining = sorted(rows(remaining_bytes), key=lambda row: row["inventory_position"])
        authoritative = [row for row in queue if row["evidence_domain"] == family_name]

        assert actual_receipt_blob == receipt_blob
        assert receipt["family"] == family_name
        assert receipt["family_records"] == count
        assert receipt["decisions_created"] == 0
        assert receipt["remaining_exact_queues"] == count
        assert receipt["unknown_hold_created"] == 0
        assert decisions == []
        assert len(authoritative) == len(remaining) == count
        assert sha256(decisions_bytes) == receipt["decisions_sha256"]
        assert sha256(remaining_bytes) == receipt["remaining_queue_sha256"]

        addresses = [row["composite_address"] for row in remaining]
        assert addresses == [row["composite_address"] for row in authoritative]
        for source, unresolved in zip(authoritative, remaining):
            assert unresolved["family_result"] == "REMAIN_QUEUED"
            assert unresolved["prior_state_preserved"] is True
            for key, value in source.items():
                assert unresolved[key] == value

        covered.extend(addresses)
        family_entries.append(
            {
                "family": family_name,
                "family_records": count,
                "decisions": 0,
                "remaining_exact_queues": count,
                "automatic_unknown_hold": 0,
                "receipt_path": receipt_path,
                "receipt_blob_sha": actual_receipt_blob,
                "receipt_sha256": sha256(receipt_bytes),
                "decisions_path": decisions_path,
                "decisions_sha256": sha256(decisions_bytes),
                "remaining_queue_path": remaining_path,
                "remaining_queue_sha256": sha256(remaining_bytes),
                "permanent_addresses": addresses,
            }
        )

    authoritative_addresses = [row["composite_address"] for row in queue]
    assert len(covered) == len(set(covered)) == 122
    assert sorted(covered, key=lambda address: by_address[address]["inventory_position"]) == authoritative_addresses

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

    manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode()
    manifest_hash = sha256(manifest_bytes)

    coverage = {
        "packet": "01.5",
        "pass": "002",
        "artifact": "closure_coverage",
        "version": 1,
        "authoritative_base": ANCHOR,
        "closure_manifest_sha256": manifest_hash,
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

    status = f"""# Packet 01.5 Scalable Pass 002 Closure v1

STATUS: INDEPENDENTLY VERIFIED

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
    return manifest, coverage, status, family_entries


def validate_invariants(manifest: dict, coverage: dict) -> None:
    assert manifest["authoritative_base"] == ANCHOR
    assert manifest["closure_scope"] == "PASS_002_PROCESSING_BOUNDARY_ONLY"
    assert manifest["remaining_evidence_queues_closed"] is False
    assert manifest["remaining_evidence_queues_preserved"] is True
    assert manifest["pass_003_started"] is False
    assert manifest["family_count"] == 7
    assert len(manifest["families"]) == 7
    assert sum(item["family_records"] for item in manifest["families"]) == 122
    assert sum(item["decisions"] for item in manifest["families"]) == 0
    assert sum(item["remaining_exact_queues"] for item in manifest["families"]) == 122
    assert sum(item["automatic_unknown_hold"] for item in manifest["families"]) == 0
    addresses = [address for family in manifest["families"] for address in family["permanent_addresses"]]
    assert len(addresses) == 122
    assert len(set(addresses)) == 122
    assert addresses != []
    assert manifest["processed_permanent_address_count"] == 122
    assert manifest["unprocessed_permanent_address_count"] == 0
    assert manifest["decisions"] == 0
    assert manifest["remaining_exact_evidence_queues"] == 122
    assert manifest["automatic_unknown_hold"] == 0
    assert manifest["all_prior_states_unclassified"] is True
    assert manifest["all_prior_decision_hashes_null"] is True
    assert manifest["all_remaining_evidence_queues_present_and_unchanged"] is True
    assert coverage["processed_records"] == 122
    assert coverage["unprocessed_records"] == 0
    assert coverage["decisions"] == 0
    assert coverage["remaining_exact_evidence_queues"] == 122
    assert coverage["automatic_unknown_hold"] == 0
    assert coverage["duplicate_addresses"] == 0
    assert coverage["omitted_addresses"] == 0
    assert coverage["all_addresses_covered_once"] is True
    assert coverage["remaining_evidence_queues_closed"] is False
    assert coverage["pass_003_started"] is False
    for key in (
        "records_modified",
        "claims_modified",
        "identities_modified",
        "remaining_queues_modified",
        "routing_assignments",
        "destination_assignments",
        "grouping_assignments",
        "source_records_removed_or_closed",
        "evidence_queues_removed_or_closed",
        "applicability_reclassifications",
        "implementation_actions",
        "packet_04_actions",
    ):
        assert coverage[key] == 0
    for key in (
        "application_behavior_modified",
        "configuration_modified",
        "dependencies_modified",
        "deployment_modified",
        "runtime_state_modified",
    ):
        assert coverage[key] is False


def require(value: bool) -> None:
    assert value


def reject(fn) -> None:
    try:
        fn()
    except (AssertionError, KeyError, TypeError, ValueError):
        return
    raise AssertionError("invalid closure fixture was accepted")


def run_rejection_fixtures(manifest: dict, coverage: dict) -> int:
    count = 0

    mutated = copy.deepcopy(manifest)
    mutated["families"] = mutated["families"][:-1]
    reject(lambda: validate_invariants(mutated, coverage)); count += 1

    mutated = copy.deepcopy(manifest)
    mutated["families"][0]["permanent_addresses"].append(mutated["families"][0]["permanent_addresses"][0])
    reject(lambda: validate_invariants(mutated, coverage)); count += 1

    mutated = copy.deepcopy(manifest)
    mutated["families"][0]["permanent_addresses"] = mutated["families"][0]["permanent_addresses"][1:]
    reject(lambda: validate_invariants(mutated, coverage)); count += 1

    mutated = copy.deepcopy(manifest)
    mutated["families"][0]["receipt_blob_sha"] = "invalid"
    reject(lambda: require(mutated == manifest)); count += 1

    mutated = copy.deepcopy(manifest)
    mutated["decisions"] = 1
    reject(lambda: validate_invariants(mutated, coverage)); count += 1

    mutated = copy.deepcopy(manifest)
    mutated["remaining_exact_evidence_queues"] = 121
    reject(lambda: validate_invariants(mutated, coverage)); count += 1

    mutated = copy.deepcopy(manifest)
    mutated["automatic_unknown_hold"] = 1
    reject(lambda: validate_invariants(mutated, coverage)); count += 1

    mutated = copy.deepcopy(manifest)
    mutated["remaining_evidence_queues_closed"] = True
    reject(lambda: validate_invariants(mutated, coverage)); count += 1

    mutated = copy.deepcopy(manifest)
    mutated["pass_003_started"] = True
    reject(lambda: validate_invariants(mutated, coverage)); count += 1

    mutated_coverage = copy.deepcopy(coverage)
    mutated_coverage["source_inventory_sha256"] = "invalid"
    reject(lambda: require(mutated_coverage == coverage)); count += 1

    mutated_coverage = copy.deepcopy(coverage)
    mutated_coverage["applicability_reclassifications"] = 1
    reject(lambda: validate_invariants(manifest, mutated_coverage)); count += 1

    mutated_coverage = copy.deepcopy(coverage)
    mutated_coverage["routing_assignments"] = 1
    reject(lambda: validate_invariants(manifest, mutated_coverage)); count += 1

    mutated_coverage = copy.deepcopy(coverage)
    mutated_coverage["evidence_queues_removed_or_closed"] = 1
    reject(lambda: validate_invariants(manifest, mutated_coverage)); count += 1

    mutated = copy.deepcopy(manifest)
    mutated["all_prior_states_unclassified"] = False
    reject(lambda: validate_invariants(mutated, coverage)); count += 1

    return count


def final_status(rejection_count: int) -> str:
    return f"""# Packet 01.5 Scalable Pass 002 Closure v1

STATUS: INDEPENDENTLY VERIFIED

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
- Rejection fixtures executed and passed: {rejection_count}
- Pass 003 begun: no

This closure does not close, remove, resolve, reclassify, or discard any remaining-evidence queue or source record. It closes only the Pass 002 processing boundary after all seven family subpasses covered all 122 authoritative records exactly once.
"""


def verify_core(receipt_may_be_missing: bool) -> dict:
    expected_manifest, expected_coverage, _, family_entries = derive_expected()
    actual_manifest = load_json(MANIFEST_PATH)
    actual_coverage = load_json(COVERAGE_PATH)
    assert actual_manifest == expected_manifest
    assert actual_coverage == expected_coverage
    validate_invariants(actual_manifest, actual_coverage)
    rejection_count = run_rejection_fixtures(actual_manifest, actual_coverage)
    verified_status = final_status(rejection_count)

    scan_private_fields(actual_manifest)
    scan_private_fields(actual_coverage)

    changed = {line for line in git("diff", "--name-only", ANCHOR, "HEAD").splitlines() if line}
    untracked = {line for line in git("ls-files", "--others", "--exclude-standard").splitlines() if line}
    observed = changed | untracked
    expected_files = ALLOWED_FILES if RECEIPT_PATH.exists() else ALLOWED_FILES - {str(RECEIPT_PATH.relative_to(ROOT))}
    assert observed == expected_files

    receipt = {
        "packet": "01.5",
        "pass": "002",
        "verification": "pass_002_closure_independent",
        "version": 1,
        "status": "PASS_PASS_002_CLOSURE_VERIFIED",
        "authoritative_base": ANCHOR,
        "closure_scope": "PASS_002_PROCESSING_BOUNDARY_ONLY",
        "closure_manifest_sha256": sha256(MANIFEST_PATH.read_bytes()),
        "closure_coverage_sha256": sha256(COVERAGE_PATH.read_bytes()),
        "closure_status_sha256": sha256(verified_status.encode()),
        "family_count": 7,
        "families": [
            {
                "family": item["family"],
                "family_records": item["family_records"],
                "decisions": item["decisions"],
                "remaining_exact_queues": item["remaining_exact_queues"],
                "automatic_unknown_hold": item["automatic_unknown_hold"],
                "receipt_path": item["receipt_path"],
                "receipt_blob_sha": item["receipt_blob_sha"],
                "remaining_queue_sha256": item["remaining_queue_sha256"],
            }
            for item in family_entries
        ],
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
        "inventory_sha256": EXPECTED_HASHES["inventory_sha256"],
        "inventory_records": 2750,
        "overlay_sha256": EXPECTED_HASHES["overlay_sha256"],
        "overlay_records": 2750,
        "queue_sha256": EXPECTED_HASHES["queue_sha256"],
        "window_sha256": EXPECTED_HASHES["window_sha256"],
        "pass_002_reconciliation_exact": True,
        "remaining_evidence_queues_closed": False,
        "pass_003_started": False,
        "rejection_fixtures_executed_and_passed": rejection_count,
        "private_values_exposed": False,
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
    scan_private_fields(receipt)
    if not receipt_may_be_missing:
        assert load_json(RECEIPT_PATH) == receipt
        assert STATUS_PATH.read_text() == verified_status
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()

    receipt = verify_core(receipt_may_be_missing=args.write_receipt)
    if args.write_receipt:
        STATUS_PATH.write_text(final_status(receipt["rejection_fixtures_executed_and_passed"]))
        RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
        receipt = verify_core(receipt_may_be_missing=False)

    print("STATUS: PASS — PACKET 01.5 PASS 002 CLOSURE VERIFIED")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
