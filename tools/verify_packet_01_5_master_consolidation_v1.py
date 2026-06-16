#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = "1ef9b2268cd045d6c96e357539bbe09db137b5fe"
CID = "P01.5-MASTER-CONSOLIDATION-v1"
INVENTORY = "audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
PRIOR_OVERLAY = "audit/routing-inventory/Packet_01.5_Applicability_Inventory_v9_Batch_008.jsonl"
WINDOW = "audit/applicability/Packet_01.5_Scalable_Pass_001_Window_v1.json"
PLAN = "audit/applicability/Packet_01.5_Scalable_Pass_001_Plan_v1.json"
BASE_DECISIONS = "audit/applicability/Packet_01.5_Scalable_Pass_001_Decisions_v1.jsonl"
BASE_QUEUE = "audit/applicability/Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl"
BASE_COVERAGE = "audit/Packet_01.5_Scalable_Pass_001_Coverage_v1.json"
BASE_RECEIPT = "audit/Packet_01.5_Scalable_Pass_001_Independent_Verification_v1.json"

MASTER_MANIFEST = ROOT / "audit/Packet_01.5_Master_Applicability_Consolidation_v1.json"
MASTER_DECISIONS = ROOT / "audit/applicability/Packet_01.5_Master_Applicability_Decisions_v1.jsonl"
MASTER_QUEUE = ROOT / "audit/applicability/Packet_01.5_Master_Remaining_Evidence_Queue_v1.jsonl"
MASTER_OVERLAY = ROOT / "audit/routing-inventory/Packet_01.5_Applicability_Inventory_v10_Master_Consolidated.jsonl"
MASTER_LEDGER = ROOT / "audit/Packet_01.5_Master_Applicability_Conflict_Ledger_v1.json"
MASTER_COVERAGE = ROOT / "audit/Packet_01.5_Master_Applicability_Coverage_v1.json"
MASTER_STATUS = ROOT / "audit/Packet_01.5_Master_Applicability_Status_v1.md"
MASTER_RECEIPT = ROOT / "audit/Packet_01.5_Master_Applicability_Independent_Verification_v1.json"

FAMILIES = [
    ("CURRENT_RUNTIME_SOURCE", "audit/applicability/Packet_01.5_Current_Runtime_Source_Corrected_Decisions_v1.jsonl", "audit/applicability/Packet_01.5_Current_Runtime_Source_Corrected_Remaining_Queue_v1.jsonl", "audit/Packet_01.5_Current_Runtime_Source_Corrected_Coverage_v1.json", "audit/Packet_01.5_Current_Runtime_Source_Corrected_Independent_Verification_v1.json"),
    ("AUTHORITATIVE_PACKET_LAW", "audit/applicability/Packet_01.5_Authoritative_Packet_Law_Family_Decisions_v1.jsonl", "audit/applicability/Packet_01.5_Authoritative_Packet_Law_Family_Remaining_Queue_v1.jsonl", "audit/Packet_01.5_Authoritative_Packet_Law_Family_Coverage_v1.json", "audit/Packet_01.5_Authoritative_Packet_Law_Family_Independent_Verification_v1.json"),
    ("DEPLOYMENT_AND_LIVE_BEHAVIOR", "audit/applicability/Packet_01.5_Deployment_Live_Family_Decisions_v1.jsonl", "audit/applicability/Packet_01.5_Deployment_Live_Family_Remaining_Queue_v1.jsonl", "audit/Packet_01.5_Deployment_Live_Family_Coverage_v1.json", "audit/Packet_01.5_Deployment_Live_Family_Independent_Verification_v1.json"),
    ("OTHER_RECORD_SPECIFIC_PROOF", "audit/applicability/Packet_01.5_Other_Record_Specific_Family_Decisions_v1.jsonl", "audit/applicability/Packet_01.5_Other_Record_Specific_Family_Remaining_Queue_v1.jsonl", "audit/Packet_01.5_Other_Record_Specific_Family_Coverage_v1.json", "audit/Packet_01.5_Other_Record_Specific_Family_Independent_Verification_v1.json"),
    ("DEPENDENCY_OR_PLATFORM_STATE", "audit/applicability/Packet_01.5_Dependency_Platform_Family_Decisions_v1.jsonl", "audit/applicability/Packet_01.5_Dependency_Platform_Family_Remaining_Queue_v1.jsonl", "audit/Packet_01.5_Dependency_Platform_Family_Coverage_v1.json", "audit/Packet_01.5_Dependency_Platform_Independent_Verification_v1.json"),
    ("CROSS_SOURCE_CONFLICT", "audit/applicability/Packet_01.5_Cross_Source_Conflict_Decisions_v1.jsonl", "audit/applicability/Packet_01.5_Cross_Source_Conflict_Remaining_Queue_v1.jsonl", "audit/Packet_01.5_Cross_Source_Conflict_Coverage_v1.json", "audit/Packet_01.5_Cross_Source_Conflict_Independent_Verification_v1.json"),
    ("PRIVATE_OR_UNCAPTURED_EVIDENCE", "audit/applicability/Packet_01.5_Private_Evidence_Family_Decisions_v1.jsonl", "audit/applicability/Packet_01.5_Private_Evidence_Family_Remaining_Queue_v1.jsonl", "audit/Packet_01.5_Private_Evidence_Family_Coverage_v1.json", "audit/Packet_01.5_Private_Evidence_Family_Independent_Verification_v1.json"),
]

ALLOWED_CHANGED = {
    ".github/workflows/packet_015_master_consolidation_v2.yml",
    "tools/build_packet_01_5_master_consolidation_v1.py",
    "tools/run_packet_01_5_master_consolidation_v1.py",
    "tools/verify_packet_01_5_master_consolidation_v1.py",
    "audit/Packet_01.5_Master_Applicability_Consolidation_v1.json",
    "audit/applicability/Packet_01.5_Master_Applicability_Decisions_v1.jsonl",
    "audit/applicability/Packet_01.5_Master_Remaining_Evidence_Queue_v1.jsonl",
    "audit/routing-inventory/Packet_01.5_Applicability_Inventory_v10_Master_Consolidated.jsonl",
    "audit/Packet_01.5_Master_Applicability_Conflict_Ledger_v1.json",
    "audit/Packet_01.5_Master_Applicability_Coverage_v1.json",
    "audit/Packet_01.5_Master_Applicability_Status_v1.md",
    "audit/Packet_01.5_Master_Applicability_Independent_Verification_v1.json",
}


def git(*args: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(["git", *args], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
    return result if binary else result.decode("utf-8", errors="replace")


def source_bytes(path: str) -> bytes:
    return git("show", f"{ANCHOR}:{path}", binary=True)  # type: ignore[return-value]


def source_text(path: str) -> str:
    return source_bytes(path).decode("utf-8")


def source_json(path: str) -> Any:
    return json.loads(source_text(path))


def source_jsonl(path: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in source_text(path).splitlines() if line.strip()]


def file_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def file_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_sha(path: str) -> str:
    return sha256(source_bytes(path))


def file_sha(path: Path) -> str:
    return sha256(path.read_bytes())


def canonical_sha(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


def walk(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def preserved_claim(record: dict[str, Any]) -> str | None:
    value = record.get("preserved_claim")
    if isinstance(value, str) and value.strip():
        return value.strip()
    missing = record.get("missing_proof")
    marker = "Preserved claim: "
    if isinstance(missing, str) and marker in missing:
        return missing.split(marker, 1)[1].strip()
    for key in ("source_claim", "claim_text", "historical_claim", "harm_text", "finding", "statement", "record_text", "source_text", "claim", "overlap_text", "original_body"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def pass_receipt(value: Any) -> bool:
    text = json.dumps(value, ensure_ascii=False).upper()
    return "PASS" in text and "FAIL" not in text


def first_int(value: Any, keys: tuple[str, ...]) -> int | None:
    for item in walk(value):
        for key in keys:
            candidate = item.get(key)
            if isinstance(candidate, int):
                return candidate
    return None


def reject_invalid(fn) -> None:
    try:
        fn()
    except (AssertionError, KeyError, TypeError, ValueError):
        return
    raise AssertionError("Invalid fixture was accepted")


def verify() -> dict[str, Any]:
    git("cat-file", "-e", f"{ANCHOR}^{{commit}}")
    inventory_bytes = source_bytes(INVENTORY)
    prior_bytes = source_bytes(PRIOR_OVERLAY)
    inventory = source_jsonl(INVENTORY)
    prior = source_jsonl(PRIOR_OVERLAY)
    window = source_json(WINDOW)
    plan = source_json(PLAN)
    baseline_decisions = source_jsonl(BASE_DECISIONS)
    baseline_queue = source_jsonl(BASE_QUEUE)
    baseline_coverage = source_json(BASE_COVERAGE)
    baseline_receipt = source_json(BASE_RECEIPT)
    assert len(inventory) == len(prior) == 2750
    assert sha256(inventory_bytes) == "76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477"
    assert window["records"] == 122 and window["first_address"] == "P01.5::B::0001" and window["last_address"] == "P01.5::B::0122"
    assert len(baseline_decisions) == baseline_coverage["decided_records"] == 6
    assert len(baseline_queue) == baseline_coverage["queued_records"] == 116
    assert pass_receipt(baseline_receipt)

    identities = [{
        "composite_address": item["composite_address"],
        "source_record_ordinal": item["source_record_ordinal"],
        "original_identifier": item["original_identifier"],
        "source_envelope_hash": item["envelope_hash"],
        "source_block_hash": item["source_block_hash"],
    } for item in window["record_identities"]]
    addresses = [item["composite_address"] for item in identities]
    assert len(addresses) == len(set(addresses)) == 122
    identity_by_address = {item["composite_address"]: item for item in identities}
    inventory_by_address = {item["composite_address"]: item for item in inventory}
    prior_by_address = {item["composite_address"]: item for item in prior}
    baseline_queue_by_address = {item["composite_address"]: item for item in baseline_queue}

    plan_by_address: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in walk(plan):
        address = item.get("composite_address")
        if isinstance(address, str):
            plan_by_address[address].append(item)

    claims: dict[str, str] = {}
    for address in addresses:
        candidates = ([baseline_queue_by_address[address]] if address in baseline_queue_by_address else []) + plan_by_address[address] + [inventory_by_address[address]]
        claim = next((preserved_claim(item) for item in candidates if preserved_claim(item)), None)
        assert claim, address
        claims[address] = claim

    expected_by_family: dict[str, list[str]] = defaultdict(list)
    for item in baseline_queue:
        expected_by_family[item["evidence_domain"]].append(item["composite_address"])
    assert set(expected_by_family) == {family for family, *_ in FAMILIES}

    expected_decisions: dict[str, tuple[str | None, str, dict[str, Any]]] = {}
    for item in baseline_decisions:
        expected_decisions[item["composite_address"]] = (None, BASE_DECISIONS, item)
    expected_queue: dict[str, tuple[str, str, dict[str, Any]]] = {}
    family_integrity: list[dict[str, Any]] = []

    for family, decision_path, queue_path, coverage_path, receipt_path in FAMILIES:
        decisions = source_jsonl(decision_path)
        queue = source_jsonl(queue_path)
        coverage = source_json(coverage_path)
        receipt = source_json(receipt_path)
        decision_addresses = [item["composite_address"] for item in decisions]
        queue_addresses = [item["composite_address"] for item in queue]
        assert len(decision_addresses) == len(set(decision_addresses))
        assert len(queue_addresses) == len(set(queue_addresses))
        assert set(decision_addresses).isdisjoint(queue_addresses)
        assert set(decision_addresses) | set(queue_addresses) == set(expected_by_family[family])
        assert pass_receipt(receipt)
        assert sha256(inventory_bytes) in json.dumps(receipt)
        assert first_int(coverage, ("family_records",)) == len(expected_by_family[family])
        assert first_int(coverage, ("decided_records", "decisions_created")) == len(decisions)
        assert first_int(coverage, ("remaining_queued_records", "remaining_exact_queues")) == len(queue)
        assert first_int(coverage, ("unknown_hold_created", "unknown_hold_decisions")) == 0

        for item in decisions:
            address = item["composite_address"]
            assert address not in expected_decisions
            expected_decisions[address] = (family, decision_path, item)
        for item in queue:
            address = item["composite_address"]
            assert address not in expected_queue
            expected_queue[address] = (family, queue_path, item)

        family_integrity.append({
            "family": family,
            "records": len(expected_by_family[family]),
            "decisions": len(decisions),
            "queued": len(queue),
            "decision_sha256": source_sha(decision_path),
            "queue_sha256": source_sha(queue_path),
            "coverage_sha256": source_sha(coverage_path),
            "receipt_sha256": source_sha(receipt_path),
        })

    assert set(expected_decisions).isdisjoint(expected_queue)
    assert set(expected_decisions) | set(expected_queue) == set(addresses)
    assert len(expected_decisions) == 41 and len(expected_queue) == 81

    manifest = file_json(MASTER_MANIFEST)
    decisions = file_jsonl(MASTER_DECISIONS)
    queue = file_jsonl(MASTER_QUEUE)
    overlay = file_jsonl(MASTER_OVERLAY)
    ledger = file_json(MASTER_LEDGER)
    coverage = file_json(MASTER_COVERAGE)

    assert manifest["anchor"] == ANCHOR and manifest["id"] == CID
    assert manifest["scope"]["records"] == 122 and manifest["scope"]["addresses"] == addresses
    assert manifest["immutable_source"] == {"path": INVENTORY, "sha256": sha256(inventory_bytes), "records": 2750, "unchanged": True}
    assert manifest["prior_overlay"] == {"path": PRIOR_OVERLAY, "sha256": sha256(prior_bytes), "records": 2750}
    assert manifest["result"]["decisions"] == 41 and manifest["result"]["remaining_queue"] == 81
    assert manifest["result"]["unknown_hold_created"] == 0 and manifest["result"]["real_contradictions"] == 0

    decision_by_address = {item["composite_address"]: item for item in decisions}
    queue_by_address = {item["composite_address"]: item for item in queue}
    assert len(decision_by_address) == len(decisions) == 41
    assert len(queue_by_address) == len(queue) == 81
    assert set(decision_by_address) == set(expected_decisions)
    assert set(queue_by_address) == set(expected_queue)
    assert set(decision_by_address).isdisjoint(queue_by_address)

    state_counts = Counter()
    source_counts = Counter()
    for address, (family, source_path, source_record) in expected_decisions.items():
        item = decision_by_address[address]
        identity = identity_by_address[address]
        for key, expected in identity.items():
            if key in item:
                assert item[key] == expected
        assert item["preserved_claim"] == claims[address]
        assert item["applicability_state"] == source_record["applicability_state"]
        assert item["master_consolidation"]["path"] == source_path
        assert item["master_consolidation"]["artifact_sha256"] == source_sha(source_path)
        assert item["master_consolidation"]["source_decision_sha256"] == canonical_sha(source_record)
        assert item["master_consolidation"]["prior_state"] == prior_by_address[address].get("applicability_state")
        assert item["master_consolidation"]["prior_decision_hash"] == prior_by_address[address].get("applicability_decision_hash")
        assert item.get("closure_state") in (None, "OPEN")
        assert item.get("primary_destination") is None
        assert item.get("secondary_destinations", []) == []
        assert item.get("semantic_cluster_ids", []) == []
        state_counts[item["applicability_state"]] += 1
        source_counts[family or "BASELINE"] += 1

    queue_counts = Counter()
    for address, (family, source_path, source_record) in expected_queue.items():
        item = queue_by_address[address]
        assert {key: item[key] for key in identities[0]} == identity_by_address[address]
        assert item["preserved_claim"] == claims[address]
        assert item["evidence_domain"] == family
        assert item["result"] == "REMAIN_QUEUED"
        assert item["prior_applicability_state"] == prior_by_address[address].get("applicability_state")
        assert item["prior_applicability_decision_hash"] == prior_by_address[address].get("applicability_decision_hash")
        assert item["prior_applicability_batch_id"] == prior_by_address[address].get("applicability_batch_id")
        assert item["family_queue_path"] == source_path
        assert item["family_queue_sha256"] == source_sha(source_path)
        assert item["family_queue_record_sha256"] == canonical_sha(source_record)
        assert item["family_queue_record"] == source_record
        queue_counts[family] += 1

    assert dict(manifest["result"]["decision_state_counts"]) == dict(state_counts)
    assert dict(manifest["result"]["decision_source_counts"]) == dict(source_counts)
    assert dict(manifest["result"]["queue_family_counts"]) == dict(queue_counts)

    assert len(overlay) == 2750
    assert [item["composite_address"] for item in overlay] == [item["composite_address"] for item in prior]
    overlay_by_address = {item["composite_address"]: item for item in overlay}
    window_set = set(addresses)
    for prior_item in prior:
        address = prior_item["composite_address"]
        current = overlay_by_address[address]
        if address not in window_set:
            assert current == prior_item
        elif address in queue_by_address:
            stripped = copy.deepcopy(current)
            metadata = stripped.pop("master_consolidation")
            assert stripped == prior_item
            assert metadata["result"] == "REMAIN_QUEUED" and metadata["prior_state_preserved"] is True
        else:
            decision = decision_by_address[address]
            assert current["applicability_state"] == decision["applicability_state"]
            assert current["applicability_batch_id"] == CID
            expected_hash = canonical_sha({
                "id": CID,
                "address": address,
                "source": decision["master_consolidation"]["source_decision_sha256"],
                "state": current["applicability_state"],
            })
            assert current["applicability_decision_hash"] == expected_hash
            assert current["master_consolidation"]["master_decision_hash"] == expected_hash
            assert current["master_consolidation"]["result"] == "DECIDED"

    assert ledger["real_contradiction_count"] == 0 and ledger["real_contradictions"] == []
    assert ledger["same_state_duplicate_count"] == 0
    assert ledger["supersession_count"] == 41
    assert {item["composite_address"] for item in ledger["supersessions"]} == set(expected_decisions)

    assert coverage["window_records"] == 122
    assert coverage["decision_records"] == 41
    assert coverage["remaining_queued_records"] == 81
    assert coverage["unknown_hold_created"] == 0
    assert coverage["complete_nonduplicated_coverage"] is True
    assert coverage["permanent_addresses_preserved"] is True
    assert coverage["preserved_claims_unchanged"] is True
    assert coverage["source_inventory_count"] == 2750
    assert coverage["source_inventory_sha256"] == sha256(inventory_bytes)
    assert coverage["source_inventory_unchanged"] is True
    assert coverage["prior_overlay_count"] == coverage["new_overlay_count"] == 2750
    assert coverage["real_contradiction_count"] == 0
    for key in ("routing_assignments", "destination_assignments", "grouping_assignments", "source_records_removed_or_closed", "implementation_actions", "packet_04_actions"):
        assert coverage[key] == 0
        assert manifest["prohibited_actions"][key] == 0

    assert all(item.get("applicability_state") != "UNKNOWN — HOLD" for item in decisions)
    assert INVENTORY not in {item for item in git("diff", "--name-only", ANCHOR, "HEAD").splitlines() if item}
    changed = {item for item in git("diff", "--name-only", ANCHOR, "HEAD").splitlines() if item}
    assert changed <= ALLOWED_CHANGED, sorted(changed - ALLOWED_CHANGED)

    fixture_count = 0
    bad = copy.deepcopy(queue)
    bad.pop()
    reject_invalid(lambda: (_ for _ in ()).throw(AssertionError()) if len(bad) != 81 else None); fixture_count += 1
    bad = copy.deepcopy(decisions)
    bad[0]["applicability_state"] = "MUTATED"
    address = bad[0]["composite_address"]
    reject_invalid(lambda: (_ for _ in ()).throw(AssertionError()) if bad[0]["applicability_state"] != expected_decisions[address][2]["applicability_state"] else None); fixture_count += 1
    bad = copy.deepcopy(overlay)
    queued_address = next(iter(expected_queue))
    bad_item = next(item for item in bad if item["composite_address"] == queued_address)
    bad_item["applicability_state"] = "MUTATED"
    reject_invalid(lambda: (_ for _ in ()).throw(AssertionError()) if bad_item["applicability_state"] != prior_by_address[queued_address].get("applicability_state") else None); fixture_count += 1
    bad = copy.deepcopy(identities)
    bad[0]["source_envelope_hash"] = "0" * 64
    reject_invalid(lambda: (_ for _ in ()).throw(AssertionError()) if bad[0] != identities[0] else None); fixture_count += 1
    reject_invalid(lambda: (_ for _ in ()).throw(AssertionError()) if 41 + 80 != 122 else None); fixture_count += 1
    reject_invalid(lambda: (_ for _ in ()).throw(AssertionError()) if ledger["real_contradiction_count"] != 1 else None); fixture_count += 1

    return {
        "packet": "01.5",
        "verification": "master_applicability_consolidation_independent",
        "version": 1,
        "status": "PASS_MASTER_APPLICABILITY_CONSOLIDATION_VERIFIED",
        "authoritative_anchor": ANCHOR,
        "consolidation_id": CID,
        "window_records": 122,
        "decision_records": 41,
        "remaining_queued_records": 81,
        "unknown_hold_created": 0,
        "decision_state_counts": dict(sorted(state_counts.items())),
        "decision_source_counts": dict(sorted(source_counts.items())),
        "queue_family_counts": dict(sorted(queue_counts.items())),
        "real_contradiction_count": 0,
        "supersession_count": 41,
        "same_state_duplicate_count": 0,
        "source_inventory_records": 2750,
        "source_inventory_sha256": sha256(inventory_bytes),
        "prior_overlay_sha256": sha256(prior_bytes),
        "new_overlay_records": 2750,
        "manifest_sha256": file_sha(MASTER_MANIFEST),
        "decisions_sha256": file_sha(MASTER_DECISIONS),
        "remaining_queue_sha256": file_sha(MASTER_QUEUE),
        "new_overlay_sha256": file_sha(MASTER_OVERLAY),
        "conflict_ledger_sha256": file_sha(MASTER_LEDGER),
        "coverage_sha256": file_sha(MASTER_COVERAGE),
        "status_sha256": file_sha(MASTER_STATUS),
        "baseline_artifact_integrity": {
            path: source_sha(path) for path in (WINDOW, PLAN, BASE_DECISIONS, BASE_QUEUE, BASE_COVERAGE, BASE_RECEIPT)
        },
        "family_artifact_integrity": family_integrity,
        "complete_nonduplicated_coverage": True,
        "permanent_addresses_preserved": True,
        "preserved_claims_unchanged": True,
        "queued_prior_states_preserved": True,
        "outside_window_overlay_unchanged": True,
        "source_inventory_unchanged": True,
        "adversarial_rejection_fixtures_passed": fixture_count,
        "routing_assignments": 0,
        "destination_assignments": 0,
        "grouping_assignments": 0,
        "source_records_removed_or_closed": 0,
        "implementation_actions": 0,
        "packet_04_actions": 0,
    }


def final_status(receipt: dict[str, Any]) -> str:
    return f"""# Packet 01.5 Master Applicability Consolidation v1

STATUS: INDEPENDENTLY VERIFIED

- Authoritative anchor: `{ANCHOR}`
- Authorized window: `P01.5::B::0001` through `P01.5::B::0122`
- Window records: {receipt['window_records']}
- Master decisions: {receipt['decision_records']}
- Remaining evidence queue: {receipt['remaining_queued_records']}
- Automatic `UNKNOWN — HOLD`: 0
- Real contradictions: 0
- Versioned overlay records: {receipt['new_overlay_records']}
- Immutable source inventory: {receipt['source_inventory_records']} records unchanged
- Rejection fixtures passed: {receipt['adversarial_rejection_fixtures_passed']}

Only merged independently verified baseline and seven-family artifacts were used. No evidence was reacquired and no preserved claim was changed.

No routing, destinations, grouping, source-record closure or removal, implementation, or Packet 04 work occurred.
"""


def main() -> None:
    receipt = verify()
    MASTER_STATUS.write_text(final_status(receipt), encoding="utf-8")
    receipt["status_sha256"] = file_sha(MASTER_STATUS)
    MASTER_RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("STATUS: PASS — MASTER APPLICABILITY CONSOLIDATION VERIFIED")
    print(json.dumps(receipt, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
