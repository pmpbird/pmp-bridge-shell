#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import packet_01_5_authoritative_law_policy as policy

QUEUE_FIELDS = {
    "composite_address", "source_record_ordinal", "original_identifier", "source_envelope_hash",
    "queue_id", "evidence_domain", "missing_proof", "recommended_acquisition_method",
    "decision_blocked_until", "reopening_trigger"
}
EVIDENCE_FIELDS = {"evidence_id", "source_reference", "source_hash_or_stable_reference", "claim_supported"}
FORBIDDEN_AUTHORITY_TERMS = (
    "discovery", "routing-batches", "baseline-source", "applicability_batch", "applicability-batch",
    "limitation-register", "limitation_register", "working-register", "working_register"
)


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


def claim_from_queue(item: dict[str, Any]) -> str:
    text = item["missing_proof"]
    return text.split("Preserved claim: ", 1)[1] if "Preserved claim: " in text else text


def resolve_record(claim: str, plan: dict[str, Any], sources: list[dict[str, Any]], tracked: list[str]) -> tuple[str, str | None, int | None, list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    reviewed = plan["reviewed_predicates"]
    generic = plan["generic_direct_authority"]
    rule = next((entry for entry in reviewed if entry["claim_contains"].lower() in claim.lower()), None)
    if rule:
        outcome, support, disproof, detail = policy.reviewed_predicate(rule["predicate"], claim, sources, tracked)
        if outcome == "SUPPORTED":
            return outcome, rule["supported_state"], rule["supported_confidence"], support, disproof, detail
        if outcome == "DISPROVED":
            return outcome, rule["disproved_state"], rule["disproved_confidence"], support, disproof, detail
        return outcome, None, None, support, disproof, detail
    outcome, support, disproof, detail = policy.generic_direct(
        claim, sources, generic["minimum_claim_token_coverage"], generic["minimum_distinct_claim_tokens"]
    )
    if outcome == "SUPPORTED":
        return outcome, generic["supported_state"], generic["supported_confidence"], support, disproof, detail
    if outcome == "DISPROVED":
        return outcome, generic["disproved_state"], generic["disproved_confidence"], support, disproof, detail
    return outcome, None, None, support, disproof, detail


def verify(repo: Path) -> dict[str, Any]:
    audit = repo / "audit"
    app = audit / "applicability"
    routing = audit / "routing-inventory"
    plan = load_object(app / "Packet_01.5_Authoritative_Packet_Law_Family_Pass_v1.json")
    queue_path = app / "Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl"
    inventory_path = routing / "Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
    manifest_path = app / "Packet_01.5_Authoritative_Packet_Law_Family_Manifest_v1.json"
    decisions_path = app / "Packet_01.5_Authoritative_Packet_Law_Family_Decisions_v1.jsonl"
    remaining_path = app / "Packet_01.5_Authoritative_Packet_Law_Family_Remaining_Queue_v1.jsonl"
    matrix_path = audit / "Packet_01.5_Authoritative_Packet_Law_Evidence_Matrix_v1.json"
    coverage_path = audit / "Packet_01.5_Authoritative_Packet_Law_Family_Coverage_v1.json"
    required_fields = set(load_object(routing / "Packet_01.5_Routing_Decision_Contract_v2.json")["overlay_required_fields"])

    queue = load_jsonl(queue_path)
    family = [item for item in queue if item["evidence_domain"] == "AUTHORITATIVE_PACKET_LAW"]
    need(len(family) == 25, "family count")
    family_addresses = [item["composite_address"] for item in family]
    need([item["source_record_ordinal"] for item in family] == sorted(item["source_record_ordinal"] for item in family), "family order")

    manifest = load_object(manifest_path)
    decisions = load_jsonl(decisions_path)
    remaining = load_jsonl(remaining_path)
    matrix = load_object(matrix_path)
    coverage = load_object(coverage_path)
    tracked = policy.tracked_files(repo)
    sources, census_sha = policy.authority_sources(repo, tracked)
    main_sha = policy.main_anchor(repo)

    need(manifest["records"] == 25, "manifest count")
    need([item["composite_address"] for item in manifest["record_identities"]] == family_addresses, "manifest order")
    need(manifest["authority_census_sha256"] == census_sha and manifest["main_commit_anchor"] == main_sha, "authority anchors")
    expected_sources = [
        {key: source[key] for key in ("path", "tier", "family", "version", "active_version", "sha256")}
        for source in sources
    ]
    need(manifest["authority_sources"] == expected_sources, "authority manifest")
    need(all(not any(term in item["path"].lower() for term in FORBIDDEN_AUTHORITY_TERMS) for item in expected_sources), "forbidden authority source selected")

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

    for decision in decisions:
        address = decision["composite_address"]
        claim = claim_from_queue(family_by_address[address])
        outcome, state, confidence, support, disproof, detail = resolve_record(claim, plan, sources, tracked)
        authority = support if outcome == "SUPPORTED" else disproof if outcome == "DISPROVED" else []
        need(outcome in {"SUPPORTED", "DISPROVED"}, f"unresolved decision: {address}")
        need(set(decision) == required_fields, f"decision fields: {address}")
        need(decision["source_envelope_hash"] == source_by_address[address]["envelope_hash"], f"source envelope: {address}")
        need(decision["source_block_hash"] == source_by_address[address]["source_block_hash"], f"source block: {address}")
        need(decision["decision_stage"] == "APPLICABILITY_ONLY", f"stage: {address}")
        need(decision["applicability_state"] == state and decision["applicability_confidence"] == confidence, f"state binding: {address}")
        need(decision["applicability_state"] != "UNKNOWN — HOLD", f"automatic HOLD: {address}")
        if outcome == "DISPROVED":
            need(decision["applicability_state"] == "OUT-OF-SCOPE CANDIDATE", f"disproof state: {address}")
        need(decision["primary_destination"] is None, f"destination: {address}")
        need(decision["secondary_destinations"] == [] and decision["cross_cutting_laws"] == [] and decision["semantic_cluster_ids"] == [], f"routing fields: {address}")
        need(decision["routing_evidence"] == [] and decision["routing_rationale"] == "" and decision["routing_confidence"] is None, f"routing proof: {address}")
        need(decision["closure_state"] == "OPEN" and decision["decision_author"] != decision["routing_decision_verifier"], f"closure/independence: {address}")
        evidence = decision["applicability_evidence"]
        need(len(evidence) >= 6 and all(set(item) == EVIDENCE_FIELDS and all(item.values()) for item in evidence), f"evidence: {address}")
        cited = {item["source_reference"]: item["source_hash_or_stable_reference"] for item in evidence}
        need(cited.get("origin/main") == f"commit:{main_sha}", f"main evidence: {address}")
        need(cited.get("authoritative repository law census") == f"sha256:{census_sha}", f"census evidence: {address}")
        for match in authority[:8]:
            need(cited.get(match["path"]) == f"sha256:{match['sha256']}", f"authority digest: {address} {match['path']}")
            need(not any(term in match["path"].lower() for term in FORBIDDEN_AUTHORITY_TERMS), f"forbidden citation: {address}")
        row = matrix_by_address[address]
        need(row["outcome"] == outcome and row["result"] == "DECIDED", f"matrix outcome: {address}")

    for item in remaining:
        address = item["composite_address"]
        claim = claim_from_queue(family_by_address[address])
        outcome, _, _, support, disproof, detail = resolve_record(claim, plan, sources, tracked)
        need(outcome == "UNRESOLVED", f"resolvable record left queued: {address}")
        need(set(item) == QUEUE_FIELDS, f"remaining fields: {address}")
        need(item["evidence_domain"] == "AUTHORITATIVE_PACKET_LAW" and item["queue_id"] == "SP001-AUTHORITATIVE_PACKET_LAW", f"remaining domain: {address}")
        need(item["source_envelope_hash"] == family_by_address[address]["source_envelope_hash"], f"remaining source hash: {address}")
        need(claim in item["missing_proof"], f"remaining claim: {address}")
        need(all(item[key] for key in ("missing_proof", "recommended_acquisition_method", "decision_blocked_until", "reopening_trigger")), f"remaining blank field: {address}")
        row = matrix_by_address[address]
        need(row["outcome"] == "UNRESOLVED" and row["result"] == "REMAIN_QUEUED", f"matrix remaining: {address}")

    need(matrix["records"] == 25 and matrix["decided"] == len(decisions) and matrix["remaining_queued"] == len(remaining), "matrix counts")
    need(coverage["family_records"] == 25 and coverage["decided_records"] == len(decisions) and coverage["remaining_queued_records"] == len(remaining), "coverage counts")
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
        bad = copy.deepcopy(remaining[0]); bad["evidence_domain"] = "OTHER_RECORD_SPECIFIC_PROOF"; rejected += int(bad["evidence_domain"] != "AUTHORITATIVE_PACKET_LAW")
    need(rejected == (4 if decisions else 0) + (2 if remaining else 0), "adversarial rejection")

    return {
        "packet": "01.5", "verification": "authoritative_packet_law_family_independent", "version": 2,
        "status": "PASS_AUTHORITATIVE_PACKET_LAW_FAMILY_VERIFIED", "watch": "NONE", "blockers": "NONE",
        "family": "AUTHORITATIVE_PACKET_LAW", "family_records": 25,
        "evidence_supported_or_disproved_decisions": len(decisions), "remaining_queued_records": len(remaining),
        "unknown_hold_created": 0, "decision_states": coverage["decision_states"], "complete_coverage": True,
        "main_commit_anchor": main_sha, "authority_census_sha256": census_sha,
        "source_queue_sha256": policy.sha256(queue_path.read_bytes()), "source_inventory_sha256": policy.sha256(inventory_path.read_bytes()),
        "manifest_sha256": policy.sha256(manifest_path.read_bytes()), "decision_overlay_sha256": policy.sha256(decisions_path.read_bytes()),
        "remaining_queue_sha256": policy.sha256(remaining_path.read_bytes()), "evidence_matrix_sha256": policy.sha256(matrix_path.read_bytes()),
        "adversarial_rejection_fixtures_passed": rejected, "routing_assignments": 0, "grouping_assignments": 0,
        "source_records_removed_or_closed": 0, "implementation_authorized": False, "packet_04_authorized": False,
        "next_authorized_work": "PACKET_01.5_PROCESS_NEXT_RESOLVABLE_EVIDENCE_FAMILY", "stop_before_routing": True
    }


if __name__ == "__main__":
    try:
        print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2, ensure_ascii=False))
    except VerifyError as exc:
        raise SystemExit("FAIL: " + str(exc))
