#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = "32eb61ff9376a769a23292f4de06c3fdc08236f0"
TARGET = "P01.5::B::0043"
FAMILY = "CROSS_SOURCE_CONFLICT"
CLAIM = "No multi-device or concurrent-edit conflict policy exists."
QUEUE_SOURCE = "audit/applicability/Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl"
INVENTORY = "audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
CURRENT = "audit/routing-inventory/Packet_01.5_Applicability_Inventory_v9_Batch_008.jsonl"
MATRIX_PATH = ROOT / "audit/Packet_01.5_Cross_Source_Conflict_Source_Matrix_v1.json"
DECISIONS_PATH = ROOT / "audit/applicability/Packet_01.5_Cross_Source_Conflict_Decisions_v1.jsonl"
QUEUE_PATH = ROOT / "audit/applicability/Packet_01.5_Cross_Source_Conflict_Remaining_Queue_v1.jsonl"
COVERAGE_PATH = ROOT / "audit/Packet_01.5_Cross_Source_Conflict_Coverage_v1.json"
STATUS_PATH = ROOT / "audit/Packet_01.5_Cross_Source_Conflict_Status_v1.md"
RECEIPT_PATH = ROOT / "audit/Packet_01.5_Cross_Source_Conflict_Independent_Verification_v1.json"

EXPECTED_QUEUE_SHA = "1b28dbfd69e9af4b51ce5cf4eb4e43d4ed4aaea107129b2e11b7b41c9dfd861a"
EXPECTED_INVENTORY_SHA = "76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477"
EXPECTED_SOURCE_PATHS = [
    QUEUE_SOURCE,
    INVENTORY,
    CURRENT,
    "audit/routing-batches/Packet_01.5_Applicability_Batch_005_Independent_Verification_v1.json",
    "audit/routing-batches/Packet_01.5_Applicability_Batch_005_Plan_v1.json",
    "control-pack/pmp-control-pack-conflict-resolver-v1.json",
    "audit/routing-evidence/Packet_03_Current_Capability_Summary_Source_v1.md",
    "audit/control-spine/PMP_Control_Spine_03_authority-matrix_v1.json",
    "audit/baseline-source/reconstructed/pmp-current-permanent-limitation-register-v3-final.json",
    "audit/Packet_01.5_Discovery_Pass_03_Reliability_Recovery_and_Platform_v1.md",
]
ALLOWED_DIFF = {
    ".github/workflows/packet_015_cross_source_conflict_discovery.yml",
    "tools/verify_packet_01_5_cross_source_conflict_v1.py",
    "audit/Packet_01.5_Cross_Source_Conflict_Source_Matrix_v1.json",
    "audit/applicability/Packet_01.5_Cross_Source_Conflict_Decisions_v1.jsonl",
    "audit/applicability/Packet_01.5_Cross_Source_Conflict_Remaining_Queue_v1.jsonl",
    "audit/Packet_01.5_Cross_Source_Conflict_Coverage_v1.json",
    "audit/Packet_01.5_Cross_Source_Conflict_Status_v1.md",
    "audit/Packet_01.5_Cross_Source_Conflict_Independent_Verification_v1.json",
}

def git(*args: str, binary: bool = False):
    cp = subprocess.run(["git", *args], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cp.stdout if binary else cp.stdout.decode("utf-8", errors="replace")

def show(path: str) -> bytes:
    return git("show", f"{ANCHOR}:{path}", binary=True)

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def json_rows(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]

def file_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def exact_record(rows: list[dict], address: str) -> dict:
    found = [row for row in rows if row.get("composite_address") == address]
    assert len(found) == 1
    return found[0]

def source_metadata(path: str) -> dict:
    data = show(path)
    log = git("log", "-1", "--format=%H%x09%cI%x09%s", ANCHOR, "--", path).strip().split("\t", 2)
    assert len(log) == 3
    return {
        "content_sha256": sha256(data),
        "git_blob_sha": git("rev-parse", f"{ANCHOR}:{path}").strip(),
        "last_change_commit": log[0],
        "last_change_date": log[1],
        "last_change_subject": log[2],
    }

def check_partition(decisions: list[dict], queues: list[dict], family_addresses: list[str]) -> None:
    d = [row.get("composite_address") for row in decisions]
    q = [row.get("composite_address") for row in queues]
    assert d == []
    assert q == family_addresses
    assert len(set(d + q)) == len(family_addresses)

def check_queue(row: dict) -> None:
    required = {
        "composite_address", "source_record_ordinal", "original_identifier", "claim",
        "result", "resolution_state", "current_applicability_state",
        "resolved_conflict_pair_ids", "unresolved_authoritative_path", "missing_proof",
        "runtime_behavior_to_test", "required_environment_and_configuration",
        "smallest_test_and_receipt", "decision_blocker", "reopening_condition",
        "source_matrix_path",
    }
    assert required <= set(row)
    assert all(row[key] not in ("", None, [], {}) for key in required)
    assert row["composite_address"] == TARGET
    assert row["source_record_ordinal"] == 43
    assert row["original_identifier"] == "DATA-010"
    assert row["claim"] == CLAIM
    assert row["result"] == "REMAIN_QUEUED"
    assert row["resolution_state"] == "CONFLICT_RESOLVED_CLAIM_UNRESOLVED"
    assert row["current_applicability_state"] == "ACTIVE_CONDITIONAL_RISK"
    assert row["resolved_conflict_pair_ids"] == ["CSC-0043-01", "CSC-0043-02", "CSC-0043-03"]
    joined = json.dumps(row, ensure_ascii=False).upper()
    assert "UNKNOWN — HOLD" not in joined and "UNKNOWN - HOLD" not in joined

def check_matrix_shape(matrix: dict) -> None:
    assert matrix["packet"] == "01.5"
    assert matrix["family"] == FAMILY
    assert matrix["authoritative_anchor"] == ANCHOR
    assert matrix["family_count"] == 1
    assert matrix["family_addresses_in_source_order"] == [TARGET]
    assert matrix["source_queue_sha256"] == EXPECTED_QUEUE_SHA
    assert matrix["source_inventory_sha256"] == EXPECTED_INVENTORY_SHA
    assert matrix["source_inventory_count"] == 2750
    assert matrix["record"]["composite_address"] == TARGET
    assert matrix["record"]["source_record_ordinal"] == 43
    assert matrix["record"]["original_identifier"] == "DATA-010"
    assert matrix["record"]["claim"] == CLAIM
    assert matrix["record"]["source_envelope_hash"] == "40b009a20fb71788f6535b641ac14e0420b42111d98886d4d9e89650808efe77"
    assert matrix["record"]["source_block_hash"] == "4ce0aa35fc364bb45afcfef1a933e6a3639cb1dbd06fd518cd1d59a5dd380486"
    assert matrix["record"]["current_applicability_state"] == "ACTIVE_CONDITIONAL_RISK"
    assert matrix["record"]["current_applicability_batch_id"] == "P01.5-APP-B005"
    assert matrix["record"]["current_applicability_decision_hash"] == "c16ea8d565c50fe1a599be420b50b8fd169f0c4cb287af700c06a9fe31271d81"
    assert [item["path"] for item in matrix["sources"]] == EXPECTED_SOURCE_PATHS
    assert [pair["pair_id"] for pair in matrix["conflict_pairs"]] == ["CSC-0043-01", "CSC-0043-02", "CSC-0043-03"]
    assert [pair["resolution"] for pair in matrix["conflict_pairs"]] == [
        "NO_SAME_SCOPE_CONFLICT", "ROLE_SPECIFIC_PRECEDENCE", "NO_COMPLETION_CONFLICT"
    ]
    assert matrix["adjudication"]["conflict_resolution"] == "COMPLETE"
    assert matrix["adjudication"]["claim_resolution"] == "UNRESOLVED"
    assert matrix["adjudication"]["result"] == "REMAIN_QUEUED"
    assert matrix["adjudication"]["decision_created"] is False
    assert matrix["adjudication"]["unknown_hold_created"] is False

def expect_reject(fn) -> None:
    try:
        fn()
    except (AssertionError, KeyError, TypeError):
        return
    raise AssertionError("adversarial mutation was accepted")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()

    git("cat-file", "-e", f"{ANCHOR}^{commit}")
    queue_source_bytes = show(QUEUE_SOURCE)
    inventory_bytes = show(INVENTORY)
    assert sha256(queue_source_bytes) == EXPECTED_QUEUE_SHA
    assert sha256(inventory_bytes) == EXPECTED_INVENTORY_SHA

    source_queue = json_rows(queue_source_bytes)
    inventory = json_rows(inventory_bytes)
    assert len(inventory) == 2750
    family = [row for row in source_queue if row.get("evidence_domain") == FAMILY]
    assert len(family) == 1
    assert [row["composite_address"] for row in family] == [TARGET]
    assert family[0]["source_record_ordinal"] == 43
    assert family[0]["original_identifier"] == "DATA-010"
    assert family[0]["source_envelope_hash"] == "40b009a20fb71788f6535b641ac14e0420b42111d98886d4d9e89650808efe77"
    assert family[0]["missing_proof"].endswith("Preserved claim: " + CLAIM)

    source_record = exact_record(inventory, TARGET)
    assert source_record["source_record_ordinal"] == 43
    assert source_record["original_identifier"] == "DATA-010"
    assert source_record["harm_text"] == CLAIM
    assert source_record["envelope_hash"] == family[0]["source_envelope_hash"]
    assert source_record["source_block_hash"] == "4ce0aa35fc364bb45afcfef1a933e6a3639cb1dbd06fd518cd1d59a5dd380486"

    current = exact_record(json_rows(show(CURRENT)), TARGET)
    assert current["applicability_state"] == "ACTIVE_CONDITIONAL_RISK"
    assert current["applicability_batch_id"] == "P01.5-APP-B005"
    assert current["applicability_decision_hash"] == "c16ea8d565c50fe1a599be420b50b8fd169f0c4cb287af700c06a9fe31271d81"
    refs = {item["source_reference"] for item in current["applicability_evidence"]}
    assert refs == {"audit/routing-evidence/Packet_03_Current_Capability_Summary_Source_v1.md"}

    resolver = json.loads(show("control-pack/pmp-control-pack-conflict-resolver-v1.json"))
    assert resolver["version"] == "1.0"
    assert resolver["status"] == "active_conflict_resolver"
    assert resolver["created_for"] == "PMP app cleanup/remodel safety"
    assert "block cleanup" in resolver["conflict_policy"]
    resolver_text = json.dumps(resolver).lower()
    for forbidden in ("multi-device", "concurrent-edit", "etag", "if-match", "version vector"):
        assert forbidden not in resolver_text

    capability = show("audit/routing-evidence/Packet_03_Current_Capability_Summary_Source_v1.md").decode("utf-8")
    assert "**Map version:** 4.0.0-final-pass" in capability
    assert "**Packet 04:** **NOT AUTHORIZED**" in capability
    for capability_id in ("RC-003", "RC-007", "RC-014", "RC-017"):
        assert capability_id in capability

    authority = json.loads(show("audit/control-spine/PMP_Control_Spine_03_authority-matrix_v1.json"))
    assert authority["version"] == "1.0.0-baseline"
    assert "does not implement or close" in authority["do_not_claim"]

    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    decisions = file_rows(DECISIONS_PATH)
    remaining = file_rows(QUEUE_PATH)
    coverage = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))
    status = STATUS_PATH.read_text(encoding="utf-8")

    check_matrix_shape(matrix)
    for entry in matrix["sources"]:
        actual = source_metadata(entry["path"])
        for key, value in actual.items():
            assert entry[key] == value
        assert isinstance(entry["authority_level"], int)
        assert entry["authority_role"] and entry["scope"] and entry["identity"]
        assert entry["declared_date"] and entry["declared_version"]

    check_partition(decisions, remaining, [TARGET])
    assert len(remaining) == 1
    check_queue(remaining[0])

    assert coverage["family_records"] == 1
    assert coverage["decided_records"] == 0
    assert coverage["remaining_queued_records"] == 1
    assert coverage["unknown_hold_created"] == 0
    assert coverage["family_addresses_in_source_order"] == [TARGET]
    assert coverage["decided_addresses"] == []
    assert coverage["queued_addresses"] == [TARGET]
    assert coverage["complete_decided_or_queued_coverage"] is True
    assert coverage["conflict_pairs_verified"] == 3
    assert coverage["source_inventory_count"] == 2750
    assert coverage["source_inventory_sha256"] == EXPECTED_INVENTORY_SHA
    assert coverage["source_inventory_unchanged"] is True
    for key in ("routing_assignments", "destination_assignments", "grouping_assignments",
                "source_records_removed_or_closed", "implementation_actions", "packet_04_actions"):
        assert coverage[key] == 0
    assert "UNKNOWN — HOLD created: 0" in status
    assert "No routing, destinations, grouping, source-record closure, implementation, or Packet 04 work occurred." in status

    changed = {line for line in git("diff", "--name-only", ANCHOR, "HEAD").splitlines() if line}
    assert changed <= ALLOWED_DIFF
    assert INVENTORY not in changed
    assert CURRENT not in changed

    mutations = 0
    bad = copy.deepcopy(matrix)
    bad["sources"][0]["content_sha256"] = "0" * 64
    expect_reject(lambda: [(_ for _ in ()).throw(AssertionError()) if
                          bad["sources"][0]["content_sha256"] != source_metadata(bad["sources"][0]["path"])["content_sha256"]
                          else None])
    mutations += 1
    bad = copy.deepcopy(matrix)
    bad["conflict_pairs"][0]["resolution"] = "POLICY_PROVEN"
    expect_reject(lambda: check_matrix_shape(bad))
    mutations += 1
    bad_queue = copy.deepcopy(remaining[0])
    del bad_queue["smallest_test_and_receipt"]
    expect_reject(lambda: check_queue(bad_queue))
    mutations += 1
    expect_reject(lambda: check_partition([{"composite_address": TARGET}], remaining, [TARGET]))
    mutations += 1
    expect_reject(lambda: check_partition([], [{"composite_address": "P01.5::B::0044"}], [TARGET]))
    mutations += 1

    receipt = {
        "packet": "01.5",
        "verification": "cross_source_conflict_independent",
        "version": 1,
        "status": "PASS_CROSS_SOURCE_CONFLICT_FAMILY_VERIFIED",
        "authoritative_anchor": ANCHOR,
        "family": FAMILY,
        "family_records": 1,
        "family_addresses_in_source_order": [TARGET],
        "decisions_created": 0,
        "remaining_exact_queues": 1,
        "unknown_hold_created": 0,
        "conflict_pairs_verified": 3,
        "current_applicability_state_preserved": "ACTIVE_CONDITIONAL_RISK",
        "source_queue_sha256": EXPECTED_QUEUE_SHA,
        "source_inventory_sha256": EXPECTED_INVENTORY_SHA,
        "source_inventory_count": 2750,
        "source_matrix_sha256": sha256(MATRIX_PATH.read_bytes()),
        "decisions_sha256": sha256(DECISIONS_PATH.read_bytes()),
        "remaining_queue_sha256": sha256) QUEUE_PATH.read_bytes()),
        "coverage_sha256": sha256(COVERAGE_PATH.read_bytes()),
        "status_sha256": sha256(STATUS_PATH.read_bytes()),
        "source_metadata_entries_verified": len(matrix["sources"]),
        "adversarial_rejection_fixtures_passed": mutations,
        "complete_decided_or_queued_coverage": True,
        "source_inventory_unchanged": True,
        "routing_assignments": 0,
        "destination_assignments": 0,
        "grouping_assignments": 0,
        "source_records_removed_or_closed": 0,
        "implementation_actions": 0,
        "packet_04_actions": 0,
    }

    if args.write_receipt:
        RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    else:
        committed = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
        assert committed == receipt

    print("STATUS: PASS — CROSS_SOURCE_CONFLICT FAMILY INDEPENDENTLY VERIFIED")
    print(json.dumps(receipt, indent=2))

if __name__ == "__main__":
    main()
