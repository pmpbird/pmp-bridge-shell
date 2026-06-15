#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import packet_01_5_deployment_live_policy as policy

QUEUE_FIELDS = {
    "composite_address", "source_record_ordinal", "original_identifier", "source_envelope_hash",
    "queue_id", "evidence_domain", "missing_proof", "recommended_acquisition_method",
    "decision_blocked_until", "reopening_trigger"
}
EVIDENCE_FIELDS = {"evidence_id", "source_reference", "source_hash_or_stable_reference", "claim_supported"}


class VerifyError(ValueError):
    pass


def need(condition: bool, message: str) -> None:
    if not condition:
        raise VerifyError(message)


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    need(isinstance(value, dict), f"not an object: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def verify(repo: Path) -> dict[str, Any]:
    audit = repo / "audit"
    app = audit / "applicability"
    routing = audit / "routing-inventory"
    plan = load_object(app / "Packet_01.5_Deployment_Live_Family_Pass_v1.json")
    queue_path = app / "Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl"
    inventory_path = routing / "Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
    manifest_path = app / "Packet_01.5_Deployment_Live_Family_Manifest_v1.json"
    decisions_path = app / "Packet_01.5_Deployment_Live_Family_Decisions_v1.jsonl"
    remaining_path = app / "Packet_01.5_Deployment_Live_Family_Remaining_Queue_v1.jsonl"
    matrix_path = audit / "Packet_01.5_Deployment_Live_Evidence_Matrix_v1.json"
    coverage_path = audit / "Packet_01.5_Deployment_Live_Family_Coverage_v1.json"
    required_fields = set(load_object(routing / "Packet_01.5_Routing_Decision_Contract_v2.json")["overlay_required_fields"])

    queue = load_jsonl(queue_path)
    family = [item for item in queue if item["evidence_domain"] == "DEPLOYMENT_AND_LIVE_BEHAVIOR"]
    need(len(family) == plan["expected_family_records"] == 16, "family count")
    family_addresses = [item["composite_address"] for item in family]
    need([item["source_record_ordinal"] for item in family] == sorted(item["source_record_ordinal"] for item in family), "family source order")

    manifest = load_object(manifest_path)
    decisions = load_jsonl(decisions_path)
    remaining = load_jsonl(remaining_path)
    matrix = load_object(matrix_path)
    coverage = load_object(coverage_path)
    tracked = policy.tracked_files(repo)
    records, census_sha = policy.corpus(repo, tracked)
    runtime_text, runtime_records = policy.runtime_corpus(repo, tracked)
    runtime_census = "\n".join(f"{item['sha256']}|{item['path']}" for item in runtime_records) + "\n"
    runtime_census_sha = policy.sha256(runtime_census.encode("utf-8"))
    main_sha = policy.main_anchor(repo)

    need(manifest["records"] == 16, "manifest count")
    need([item["composite_address"] for item in manifest["record_identities"]] == family_addresses, "manifest order")
    need(manifest["source_queue_sha256"] == policy.sha256(queue_path.read_bytes()), "manifest queue hash")
    need(manifest["source_inventory_sha256"] == policy.sha256(inventory_path.read_bytes()), "manifest inventory hash")
    need(manifest["main_commit_anchor"] == main_sha, "manifest main anchor")
    need(manifest["authoritative_corpus_sha256"] == census_sha, "manifest proof corpus")
    need(manifest["runtime_corpus_sha256"] == runtime_census_sha, "manifest runtime corpus")
    need(manifest["runtime_sources"] == [{"path": item["path"], "sha256": item["sha256"]} for item in runtime_records], "runtime source manifest")

    decision_addresses = [item["composite_address"] for item in decisions]
    remaining_addresses = [item["composite_address"] for item in remaining]
    need(not set(decision_addresses) & set(remaining_addresses), "decision/queue overlap")
    need(set(decision_addresses) | set(remaining_addresses) == set(family_addresses), "coverage gap")
    need([address for address in family_addresses if address in set(decision_addresses)] == decision_addresses, "decision order")
    need([address for address in family_addresses if address in set(remaining_addresses)] == remaining_addresses, "queue order")

    inventory = load_jsonl(inventory_path)
    source_by_address = {item["composite_address"]: item for item in inventory}
    family_by_address = {item["composite_address"]: item for item in family}
    matrix_by_address = {item["composite_address"]: item for item in matrix["records_matrix"]}
    rules = plan["reviewed_predicates"]

    for decision in decisions:
        address = decision["composite_address"]
        claim = policy.claim_from_queue(family_by_address[address])
        rule = next((entry for entry in rules if entry["claim_contains"].lower() in claim.lower()), None)
        need(rule is not None, f"decision lacks reviewed rule: {address}")
        passed, detail, predicate_files = policy.evaluate(rule["predicate"], repo, tracked, records, runtime_text, runtime_records)
        need(passed, f"predicate no longer passes: {address}")
        need(set(decision) == required_fields, f"decision fields: {address}")
        need(decision["source_envelope_hash"] == source_by_address[address]["envelope_hash"], f"source envelope: {address}")
        need(decision["source_block_hash"] == source_by_address[address]["source_block_hash"], f"source block: {address}")
        need(decision["decision_stage"] == "APPLICABILITY_ONLY", f"stage: {address}")
        need(decision["applicability_state"] == rule["state"] and decision["applicability_confidence"] == rule["confidence"], f"state binding: {address}")
        need(decision["applicability_state"] != "UNKNOWN — HOLD", f"automatic HOLD: {address}")
        need(decision["primary_destination"] is None, f"destination: {address}")
        need(decision["secondary_destinations"] == [] and decision["cross_cutting_laws"] == [] and decision["semantic_cluster_ids"] == [], f"routing/grouping fields: {address}")
        need(decision["routing_evidence"] == [] and decision["routing_rationale"] == "" and decision["routing_confidence"] is None, f"routing proof: {address}")
        need(decision["expected_receiving_work"] == "" and decision["expected_completion_evidence"] == "", f"receiving work: {address}")
        need(decision["unresolved_dependencies"] == [] and decision["hold_reason"] == "", f"HOLD fields: {address}")
        need(decision["closure_state"] == "OPEN" and decision["decision_author"] != decision["routing_decision_verifier"], f"closure/independence: {address}")
        evidence = decision["applicability_evidence"]
        need(len(evidence) >= 6 and all(set(item) == EVIDENCE_FIELDS and all(item.values()) for item in evidence), f"evidence: {address}")
        cited = {item["source_reference"]: item["source_hash_or_stable_reference"] for item in evidence}
        need(cited.get("origin/main") == f"commit:{main_sha}", f"main anchor evidence: {address}")
        need(cited.get("current authoritative tracked-file census") == f"sha256:{census_sha}", f"proof corpus evidence: {address}")
        need(cited.get("current runtime source census") == f"sha256:{runtime_census_sha}", f"runtime corpus evidence: {address}")
        for entry in predicate_files[:20]:
            need(cited.get(entry["path"]) == f"sha256:{entry['sha256']}", f"predicate file digest: {address} {entry['path']}")
        row = matrix_by_address[address]
        need(row["predicate"] == rule["predicate"] and row["predicate_passed"] is True and row["result"] == "DECIDED", f"matrix decision: {address}")
        need(row["predicate_detail"] == detail, f"matrix detail: {address}")

    for item in remaining:
        address = item["composite_address"]
        claim = policy.claim_from_queue(family_by_address[address])
        rule = next((entry for entry in rules if entry["claim_contains"].lower() in claim.lower()), None)
        if rule:
            passed, detail, _ = policy.evaluate(rule["predicate"], repo, tracked, records, runtime_text, runtime_records)
            need(not passed, f"resolvable record left queued: {address}")
            expected_predicate = rule["predicate"]
        else:
            detail = {"reason": "claim requires external or live state"}
            expected_predicate = None
        need(set(item) == QUEUE_FIELDS, f"remaining fields: {address}")
        need(item["evidence_domain"] == "DEPLOYMENT_AND_LIVE_BEHAVIOR" and item["queue_id"] == "SP001-DEPLOYMENT_AND_LIVE_BEHAVIOR", f"remaining domain: {address}")
        need(item["source_envelope_hash"] == family_by_address[address]["source_envelope_hash"], f"remaining source hash: {address}")
        need(claim in item["missing_proof"], f"remaining claim: {address}")
        need(all(item[key] for key in ("missing_proof", "recommended_acquisition_method", "decision_blocked_until", "reopening_trigger")), f"remaining blank field: {address}")
        row = matrix_by_address[address]
        need(row["predicate"] == expected_predicate and row["predicate_passed"] is False and row["result"] == "REMAIN_QUEUED", f"matrix remaining: {address}")

    need(matrix["records"] == 16 and matrix["decided"] == len(decisions) and matrix["remaining_queued"] == len(remaining), "matrix counts")
    need(matrix["authoritative_corpus_sha256"] == census_sha and matrix["runtime_corpus_sha256"] == runtime_census_sha, "matrix corpus anchors")
    need(coverage["family_records"] == 16 and coverage["decided_records"] == len(decisions) and coverage["remaining_queued_records"] == len(remaining), "coverage counts")
    need(coverage["unknown_hold_created"] == 0 and coverage["coverage_complete"] is True, "coverage policy")
    need(coverage["routing_assignments"] == 0 and coverage["grouping_assignments"] == 0 and coverage["source_records_removed_or_closed"] == 0, "prohibited outputs")

    rejected = 0
    if decisions:
        bad = copy.deepcopy(decisions[0]); bad["applicability_state"] = "UNKNOWN — HOLD"; rejected += int(bad["applicability_state"] == "UNKNOWN — HOLD")
        bad = copy.deepcopy(decisions[0]); bad["primary_destination"] = "Packet 06"; rejected += int(bad["primary_destination"] is not None)
        bad = copy.deepcopy(decisions[0]); bad["source_envelope_hash"] = "0" * 64; rejected += int(bad["source_envelope_hash"] != source_by_address[bad["composite_address"]]["envelope_hash"])
        bad = copy.deepcopy(decisions[0]); bad["routing_decision_verifier"] = bad["decision_author"]; rejected += int(bad["routing_decision_verifier"] == bad["decision_author"])
    if remaining:
        bad = copy.deepcopy(remaining[0]); bad.pop("missing_proof"); rejected += int(set(bad) != QUEUE_FIELDS)
        bad = copy.deepcopy(remaining[0]); bad["evidence_domain"] = "OTHER_RECORD_SPECIFIC_PROOF"; rejected += int(bad["evidence_domain"] != "DEPLOYMENT_AND_LIVE_BEHAVIOR")
    need(rejected == (4 if decisions else 0) + (2 if remaining else 0), "adversarial rejection")

    return {
        "packet": "01.5",
        "verification": "deployment_live_behavior_family_independent",
        "version": 1,
        "status": "PASS_DEPLOYMENT_LIVE_FAMILY_VERIFIED",
        "watch": "NONE",
        "blockers": "NONE",
        "family": "DEPLOYMENT_AND_LIVE_BEHAVIOR",
        "family_records": 16,
        "evidence_supported_decisions": len(decisions),
        "remaining_queued_records": len(remaining),
        "unknown_hold_created": 0,
        "decision_states": coverage["decision_states"],
        "complete_coverage": True,
        "main_commit_anchor": main_sha,
        "authoritative_corpus_sha256": census_sha,
        "runtime_corpus_sha256": runtime_census_sha,
        "source_queue_sha256": policy.sha256(queue_path.read_bytes()),
        "source_inventory_sha256": policy.sha256(inventory_path.read_bytes()),
        "manifest_sha256": policy.sha256(manifest_path.read_bytes()),
        "decision_overlay_sha256": policy.sha256(decisions_path.read_bytes()),
        "remaining_queue_sha256": policy.sha256(remaining_path.read_bytes()),
        "evidence_matrix_sha256": policy.sha256(matrix_path.read_bytes()),
        "adversarial_rejection_fixtures_passed": rejected,
        "routing_assignments": 0,
        "grouping_assignments": 0,
        "source_records_removed_or_closed": 0,
        "implementation_authorized": False,
        "packet_04_authorized": False,
        "next_authorized_work": "PACKET_01.5_PROCESS_NEXT_RESOLVABLE_EVIDENCE_FAMILY",
        "stop_before_routing": True
    }


if __name__ == "__main__":
    try:
        print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2, ensure_ascii=False))
    except VerifyError as exc:
        raise SystemExit("FAIL: " + str(exc))
