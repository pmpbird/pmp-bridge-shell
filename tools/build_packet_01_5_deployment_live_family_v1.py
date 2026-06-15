#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import packet_01_5_deployment_live_policy as policy

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "audit"
APP = AUDIT / "applicability"
ROUTING = AUDIT / "routing-inventory"

PLAN_PATH = APP / "Packet_01.5_Deployment_Live_Family_Pass_v1.json"
QUEUE_PATH = APP / "Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl"
INVENTORY_PATH = ROUTING / "Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
MANIFEST_PATH = APP / "Packet_01.5_Deployment_Live_Family_Manifest_v1.json"
DECISIONS_PATH = APP / "Packet_01.5_Deployment_Live_Family_Decisions_v1.jsonl"
REMAINING_PATH = APP / "Packet_01.5_Deployment_Live_Family_Remaining_Queue_v1.jsonl"
MATRIX_PATH = AUDIT / "Packet_01.5_Deployment_Live_Evidence_Matrix_v1.json"
COVERAGE_PATH = AUDIT / "Packet_01.5_Deployment_Live_Family_Coverage_v1.json"
SUMMARY_PATH = AUDIT / "Packet_01.5_Deployment_Live_Family_v1.md"

QUEUE_SHA = "1b28dbfd69e9af4b51ce5cf4eb4e43d4ed4aaea107129b2e11b7b41c9dfd861a"
INVENTORY_SHA = "76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    need(isinstance(value, dict), f"not an object: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def claim_from_queue(item: dict[str, Any]) -> str:
    return policy.claim_from_queue(item)


def evidence(eid: str, reference: str, stable: str, claim: str) -> dict[str, str]:
    return {
        "evidence_id": eid,
        "source_reference": reference,
        "source_hash_or_stable_reference": stable,
        "claim_supported": claim,
    }


def remaining_entry(item: dict[str, Any], claim: str, predicate: str | None, detail: dict[str, Any]) -> dict[str, Any]:
    result = dict(item)
    if predicate is None:
        missing = "The complete claim depends on untracked cloud, deployment, secret, device, or live-service state that current repository evidence cannot establish."
        method = "Capture the serving revision, platform environment list, bindings, secret scopes, route visibility, and bounded live probes with redacted receipts."
    elif detail.get("error"):
        missing = f"The reviewed repository predicate could not establish the complete claim: {detail['error']}."
        method = "Repair or replace the predicate, then independently rerun it against current main and the exact permanent address."
    else:
        missing = "Current repository evidence does not yet prove the full preserved claim under the reviewed predicate."
        method = "Capture the missing configuration, authoritative proof receipt, or bounded live observation named by the predicate detail."
    result["missing_proof"] = f"{missing} Predicate: {predicate or 'NO_REPOSITORY_ONLY_PREDICATE'}. Detail: {json.dumps(detail, sort_keys=True)}. Preserved claim: {claim}"
    result["recommended_acquisition_method"] = method
    result["decision_blocked_until"] = "The missing repository, platform, or live evidence is captured, hashed, and independently verified against this permanent address."
    result["reopening_trigger"] = "A source, configuration, deployment, cloud setting, audit receipt, or live observation changes the evidence."
    return result


def main() -> None:
    plan = load_object(PLAN_PATH)
    need(plan["family"] == "DEPLOYMENT_AND_LIVE_BEHAVIOR", "wrong family")
    need(plan["decision_author"] != plan["decision_verifier"], "author equals verifier")
    queue_raw = QUEUE_PATH.read_bytes()
    inventory_raw = INVENTORY_PATH.read_bytes()
    need(policy.sha256(queue_raw) == QUEUE_SHA, "source queue hash changed")
    need(policy.sha256(inventory_raw) == INVENTORY_SHA, "source inventory hash changed")

    queue = load_jsonl(QUEUE_PATH)
    family = [item for item in queue if item["evidence_domain"] == "DEPLOYMENT_AND_LIVE_BEHAVIOR"]
    need(len(family) == plan["expected_family_records"] == 16, "family count changed")
    need([item["source_record_ordinal"] for item in family] == sorted(item["source_record_ordinal"] for item in family), "family order changed")

    inventory = load_jsonl(INVENTORY_PATH)
    source_by_address = {item["composite_address"]: item for item in inventory}
    tracked = policy.tracked_files(REPO)
    records, census_sha = policy.corpus(REPO, tracked)
    runtime_text, runtime_records = policy.runtime_corpus(REPO, tracked)
    runtime_census = "\n".join(f"{item['sha256']}|{item['path']}" for item in runtime_records) + "\n"
    runtime_census_sha = policy.sha256(runtime_census.encode("utf-8"))
    main_sha = policy.main_anchor(REPO)
    plan_sha = policy.sha256(PLAN_PATH.read_bytes())
    rules = plan["reviewed_predicates"]

    decisions: list[dict[str, Any]] = []
    remaining: list[dict[str, Any]] = []
    matrix: list[dict[str, Any]] = []

    for item in family:
        address = item["composite_address"]
        claim = claim_from_queue(item)
        source = source_by_address[address]
        need(item["source_envelope_hash"] == source["envelope_hash"], f"queue/source mismatch: {address}")
        rule = next((entry for entry in rules if entry["claim_contains"].lower() in claim.lower()), None)
        if rule:
            predicate = rule["predicate"]
            passed, detail, predicate_files = policy.evaluate(predicate, REPO, tracked, records, runtime_text, runtime_records)
            state, confidence = rule["state"], rule["confidence"]
        else:
            predicate = None
            passed, detail, predicate_files = False, {"reason": "claim requires external or live state"}, []
            state, confidence = None, None

        matrix.append({
            "composite_address": address,
            "original_identifier": item["original_identifier"],
            "claim": claim,
            "predicate": predicate,
            "predicate_passed": passed,
            "state_if_passed": state,
            "confidence_if_passed": confidence,
            "predicate_detail": detail,
            "predicate_files": [{"path": entry["path"], "sha256": entry["sha256"]} for entry in predicate_files],
            "result": "DECIDED" if passed else "REMAIN_QUEUED",
        })

        if not passed:
            remaining.append(remaining_entry(item, claim, predicate, detail))
            continue

        evidence_entries = [
            evidence(f"DLF-SOURCE-{address}", f"{INVENTORY_PATH.relative_to(REPO)}#{address}", source["envelope_hash"], "Preserves the immutable source claim and permanent address."),
            evidence(f"DLF-QUEUE-{address}", f"{QUEUE_PATH.relative_to(REPO)}#{address}", f"sha256:{QUEUE_SHA}#{address}", "Proves membership in the complete deployment-and-live-behavior evidence family."),
            evidence(f"DLF-PLAN-{address}", f"{PLAN_PATH.relative_to(REPO)}#{predicate}", f"sha256:{plan_sha}#{predicate}", "Binds the record to the reviewed predicate, state, confidence, and repository-only evidence boundary."),
            evidence(f"DLF-CENSUS-{address}", "current authoritative tracked-file census", f"sha256:{census_sha}", "Commits the complete filtered repository proof corpus used for proof-existence predicates."),
            evidence(f"DLF-RUNTIME-{address}", "current runtime source census", f"sha256:{runtime_census_sha}", "Commits the current tracked runtime and configuration corpus used for implementation predicates."),
            evidence(f"DLF-MAIN-{address}", "origin/main", f"commit:{main_sha}", "Anchors the evaluation to current main."),
        ]
        for index, entry in enumerate(predicate_files[:20], 1):
            evidence_entries.append(evidence(
                f"DLF-FILE-{index:02d}-{address}", entry["path"], f"sha256:{entry['sha256']}",
                f"Current tracked source or configuration used by predicate {predicate}."
            ))

        decision = {
            "composite_address": address,
            "source_inventory_sha256": INVENTORY_SHA,
            "source_envelope_hash": source["envelope_hash"],
            "source_block_hash": source["source_block_hash"],
            "decision_stage": "APPLICABILITY_ONLY",
            "applicability_state": state,
            "applicability_evidence": evidence_entries,
            "applicability_reasoning_summary": policy.REASONS[predicate],
            "applicability_confidence": confidence,
            "primary_destination": None,
            "secondary_destinations": [],
            "cross_cutting_laws": [],
            "semantic_cluster_ids": [],
            "routing_evidence": [],
            "routing_rationale": "",
            "routing_confidence": None,
            "expected_receiving_work": "",
            "expected_completion_evidence": "",
            "unresolved_dependencies": [],
            "hold_reason": "",
            "reopening_conditions": [
                "A current implementation, governing proof receipt, or deployment configuration satisfies the previously absent control.",
                "A bounded live observation contradicts the repository-only evidence result.",
                "The cited main commit, source files, configuration, or proof corpus changes."
            ],
            "decision_version": "Packet-01.5-Deployment-Live-Family-v1",
            "decision_author": plan["decision_author"],
            "routing_decision_verifier": plan["decision_verifier"],
            "closure_state": "OPEN",
        }
        decisions.append(decision)

    manifest = {
        "packet": "01.5",
        "family": "DEPLOYMENT_AND_LIVE_BEHAVIOR",
        "records": len(family),
        "source_queue_sha256": QUEUE_SHA,
        "source_inventory_sha256": INVENTORY_SHA,
        "main_commit_anchor": main_sha,
        "authoritative_corpus_sha256": census_sha,
        "runtime_corpus_sha256": runtime_census_sha,
        "runtime_sources": [{"path": item["path"], "sha256": item["sha256"]} for item in runtime_records],
        "record_identities": [
            {
                "composite_address": item["composite_address"],
                "source_record_ordinal": item["source_record_ordinal"],
                "original_identifier": item["original_identifier"],
                "source_envelope_hash": item["source_envelope_hash"],
            }
            for item in family
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    DECISIONS_PATH.write_text("".join(json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n" for item in decisions), encoding="utf-8")
    REMAINING_PATH.write_text("".join(json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n" for item in remaining), encoding="utf-8")
    MATRIX_PATH.write_text(json.dumps({
        "packet": "01.5",
        "family": "DEPLOYMENT_AND_LIVE_BEHAVIOR",
        "records": len(family),
        "decided": len(decisions),
        "remaining_queued": len(remaining),
        "main_commit_anchor": main_sha,
        "authoritative_corpus_sha256": census_sha,
        "runtime_corpus_sha256": runtime_census_sha,
        "records_matrix": matrix,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    state_counts: dict[str, int] = {}
    for item in decisions:
        state_counts[item["applicability_state"]] = state_counts.get(item["applicability_state"], 0) + 1
    coverage = {
        "packet": "01.5",
        "family": "DEPLOYMENT_AND_LIVE_BEHAVIOR",
        "family_records": len(family),
        "decided_records": len(decisions),
        "remaining_queued_records": len(remaining),
        "unknown_hold_created": 0,
        "coverage_complete": len(decisions) + len(remaining) == len(family),
        "decision_states": state_counts,
        "routing_assignments": 0,
        "grouping_assignments": 0,
        "source_records_removed_or_closed": 0,
    }
    COVERAGE_PATH.write_text(json.dumps(coverage, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    SUMMARY_PATH.write_text(f"""# Packet 01.5 — Deployment and Live-Behavior Evidence Family v1

STATUS: BUILT — PENDING INDEPENDENT VERIFICATION
FAMILY RECORDS: {len(family)}
EVIDENCE-SUPPORTED DECISIONS: {len(decisions)}
REMAINING QUEUED: {len(remaining)}
UNKNOWN — HOLD CREATED: 0
ROUTING ASSIGNMENTS: 0
GROUPING ASSIGNMENTS: 0

The complete family was processed in permanent source order. Repository-proven implementation, configuration, and proof-status claims may be decided. Claims requiring untracked cloud settings or actual live behavior remain queued with exact acquisition instructions.

Stop before routing, grouping, closure, implementation, or Packet 04.
""", encoding="utf-8")
    need(INVENTORY_PATH.read_bytes() == inventory_raw, "source inventory changed")
    print(f"PASS: deployment/live family built with {len(decisions)} decisions and {len(remaining)} queued")


if __name__ == "__main__":
    main()
