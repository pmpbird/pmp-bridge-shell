#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import packet_01_5_other_specific_policy as policy

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "audit"
APP = AUDIT / "applicability"
ROUTING = AUDIT / "routing-inventory"
PLAN = APP / "Packet_01.5_Other_Record_Specific_Family_Pass_v1.json"
QUEUE = APP / "Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl"
INVENTORY = ROUTING / "Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
MANIFEST = APP / "Packet_01.5_Other_Record_Specific_Family_Manifest_v1.json"
DECISIONS = APP / "Packet_01.5_Other_Record_Specific_Family_Decisions_v1.jsonl"
REMAINING = APP / "Packet_01.5_Other_Record_Specific_Family_Remaining_Queue_v1.jsonl"
MATRIX = AUDIT / "Packet_01.5_Other_Record_Specific_Evidence_Matrix_v1.json"
COVERAGE = AUDIT / "Packet_01.5_Other_Record_Specific_Family_Coverage_v1.json"
SUMMARY = AUDIT / "Packet_01.5_Other_Record_Specific_Family_v1.md"
QUEUE_SHA = "1b28dbfd69e9af4b51ce5cf4eb4e43d4ed4aaea107129b2e11b7b41c9dfd861a"
INVENTORY_SHA = "76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477"


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit("FAIL: " + message)


def obj(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    need(isinstance(value, dict), str(path))
    return value


def rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def ev(eid: str, reference: str, stable: str, claim: str) -> dict[str, str]:
    return {
        "evidence_id": eid,
        "source_reference": reference,
        "source_hash_or_stable_reference": stable,
        "claim_supported": claim,
    }


def refine_queue(item: dict[str, Any], claim: str, predicate: str | None, outcome: str, detail: dict[str, Any], evidence_files: list[dict[str, str]]) -> dict[str, Any]:
    result = dict(item)
    if predicate is None:
        missing = "No reviewed repository-only predicate yet covers the complete preserved claim."
        method = "Define the smallest claim-specific source, document, configuration, or runtime test and bind it to this address with a stable receipt."
    elif outcome == "UNRESOLVED":
        paths = ", ".join(sorted({entry["path"] for entry in evidence_files}))
        missing = "Current evidence is partial and cannot prove or disprove the complete claim."
        if paths:
            missing += f" Relevant current sources: {paths}."
        method = "Close the missing predicate components shown in the detail, then independently rerun the same rule."
    else:
        missing = "The reviewed predicate did not produce a valid decision."
        method = "Repair the predicate or gather stronger direct current evidence before reconsidering the record."
    result["missing_proof"] = f"{missing} Predicate: {predicate or 'UNREVIEWED'}. Outcome: {outcome}. Detail: {json.dumps(detail, sort_keys=True)}. Preserved claim: {claim}"
    result["recommended_acquisition_method"] = method
    result["decision_blocked_until"] = "The complete record-specific predicate is satisfied and independently verified against this permanent address."
    result["reopening_trigger"] = "A current source, governing record, proof receipt, runtime result, or predicate component changes."
    return result


def main() -> None:
    plan = obj(PLAN)
    need(plan["family"] == "OTHER_RECORD_SPECIFIC_PROOF", "wrong family")
    need(plan["decision_author"] != plan["decision_verifier"], "author equals verifier")
    queue_raw = QUEUE.read_bytes()
    inventory_raw = INVENTORY.read_bytes()
    need(policy.sha256(queue_raw) == QUEUE_SHA, "queue hash changed")
    need(policy.sha256(inventory_raw) == INVENTORY_SHA, "inventory hash changed")

    all_queue = rows(QUEUE)
    family = [item for item in all_queue if item["evidence_domain"] == "OTHER_RECORD_SPECIFIC_PROOF"]
    need(len(family) == plan["expected_family_records"] == 31, "family count changed")
    need([item["source_record_ordinal"] for item in family] == sorted(item["source_record_ordinal"] for item in family), "family order changed")
    inventory = rows(INVENTORY)
    source = {item["composite_address"]: item for item in inventory}

    files = policy.tracked_files(REPO)
    records, corpus_sha = policy.corpus(REPO, files)
    runtime_text, runtime_records = policy.effective_runtime(REPO, files)
    runtime_census = "\n".join(f"{item['sha256']}|{item['path']}" for item in runtime_records) + "\n"
    runtime_sha = policy.sha256(runtime_census.encode("utf-8"))
    main_sha = policy.main_anchor(REPO)
    plan_sha = policy.sha256(PLAN.read_bytes())
    rules = plan["reviewed_predicates"]

    decisions: list[dict[str, Any]] = []
    remaining: list[dict[str, Any]] = []
    matrix: list[dict[str, Any]] = []

    for item in family:
        address = item["composite_address"]
        claim = policy.claim_from_queue(item)
        src = source[address]
        need(item["source_envelope_hash"] == src["envelope_hash"], f"source mismatch: {address}")
        rule = next((entry for entry in rules if entry["claim_contains"].lower() in claim.lower()), None)
        if rule:
            predicate = rule["predicate"]
            outcome, detail, evidence_files = policy.evaluate(predicate, REPO, files, records, runtime_text, runtime_records)
            if outcome == "SUPPORTED":
                state, confidence = rule["supported_state"], rule["supported_confidence"]
            elif outcome == "DISPROVED":
                state, confidence = rule["disproved_state"], rule["disproved_confidence"]
            else:
                state, confidence = None, None
        else:
            predicate = None
            outcome, detail, evidence_files = "UNRESOLVED", {"reason": "no reviewed predicate"}, []
            state, confidence = None, None

        matrix.append({
            "composite_address": address,
            "original_identifier": item["original_identifier"],
            "claim": claim,
            "predicate": predicate,
            "outcome": outcome,
            "state_if_decided": state,
            "confidence_if_decided": confidence,
            "predicate_detail": detail,
            "predicate_files": evidence_files,
            "result": "DECIDED" if outcome in {"SUPPORTED", "DISPROVED"} else "REMAIN_QUEUED",
        })

        if outcome == "UNRESOLVED":
            remaining.append(refine_queue(item, claim, predicate, outcome, detail, evidence_files))
            continue

        evidence_entries = [
            ev(f"OSF-SOURCE-{address}", f"{INVENTORY.relative_to(REPO)}#{address}", src["envelope_hash"], "Preserves the immutable source claim and permanent address."),
            ev(f"OSF-QUEUE-{address}", f"{QUEUE.relative_to(REPO)}#{address}", f"sha256:{QUEUE_SHA}#{address}", "Proves membership in the complete other-record-specific evidence family."),
            ev(f"OSF-PLAN-{address}", f"{PLAN.relative_to(REPO)}#{predicate}", f"sha256:{plan_sha}#{predicate}", "Binds the address to the reviewed three-way predicate, state, and confidence."),
            ev(f"OSF-CORPUS-{address}", "current filtered authoritative corpus", f"sha256:{corpus_sha}", "Commits the complete filtered current source, governing, and proof corpus used by the predicate."),
            ev(f"OSF-RUNTIME-{address}", "effective current runtime corpus", f"sha256:{runtime_sha}", "Commits the effective current route and configuration used by runtime predicates."),
            ev(f"OSF-MAIN-{address}", "origin/main", f"commit:{main_sha}", "Anchors evaluation to current main."),
        ]
        for index, evidence_file in enumerate(evidence_files[:20], 1):
            evidence_entries.append(ev(
                f"OSF-FILE-{index:02d}-{address}", evidence_file["path"], f"sha256:{evidence_file['sha256']}",
                f"Current source or verified record used by predicate {predicate}."
            ))

        if outcome == "SUPPORTED":
            reasoning = policy.REASONS[predicate]
        else:
            cited = ", ".join(entry["path"] for entry in evidence_files[:8])
            reasoning = f"Current complete verified evidence disproves the historical limitation claim, so it is an out-of-scope candidate. Controlling evidence: {cited}."
        decisions.append({
            "composite_address": address,
            "source_inventory_sha256": INVENTORY_SHA,
            "source_envelope_hash": src["envelope_hash"],
            "source_block_hash": src["source_block_hash"],
            "decision_stage": "APPLICABILITY_ONLY",
            "applicability_state": state,
            "applicability_evidence": evidence_entries,
            "applicability_reasoning_summary": reasoning,
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
                "The reviewed predicate gains or loses a complete verified component.",
                "A newer current source, governing record, proof receipt, or runtime result supersedes the cited evidence.",
                "The main commit, corpus digest, or source-envelope anchor changes."
            ],
            "decision_version": "Packet-01.5-Other-Record-Specific-Family-v1",
            "decision_author": plan["decision_author"],
            "routing_decision_verifier": plan["decision_verifier"],
            "closure_state": "OPEN",
        })

    MANIFEST.write_text(json.dumps({
        "packet": "01.5",
        "family": "OTHER_RECORD_SPECIFIC_PROOF",
        "records": len(family),
        "source_queue_sha256": QUEUE_SHA,
        "source_inventory_sha256": INVENTORY_SHA,
        "main_commit_anchor": main_sha,
        "filtered_corpus_sha256": corpus_sha,
        "effective_runtime_corpus_sha256": runtime_sha,
        "effective_runtime_sources": [{"path": item["path"], "sha256": item["sha256"]} for item in runtime_records],
        "record_identities": [
            {"composite_address": item["composite_address"], "source_record_ordinal": item["source_record_ordinal"], "original_identifier": item["original_identifier"], "source_envelope_hash": item["source_envelope_hash"]}
            for item in family
        ],
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    DECISIONS.write_text("".join(json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n" for item in decisions), encoding="utf-8")
    REMAINING.write_text("".join(json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n" for item in remaining), encoding="utf-8")
    MATRIX.write_text(json.dumps({
        "packet": "01.5",
        "family": "OTHER_RECORD_SPECIFIC_PROOF",
        "records": len(family),
        "decided": len(decisions),
        "remaining_queued": len(remaining),
        "main_commit_anchor": main_sha,
        "filtered_corpus_sha256": corpus_sha,
        "effective_runtime_corpus_sha256": runtime_sha,
        "records_matrix": matrix,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    state_counts: dict[str, int] = {}
    for decision in decisions:
        state_counts[decision["applicability_state"]] = state_counts.get(decision["applicability_state"], 0) + 1
    COVERAGE.write_text(json.dumps({
        "packet": "01.5",
        "family": "OTHER_RECORD_SPECIFIC_PROOF",
        "family_records": len(family),
        "decided_records": len(decisions),
        "remaining_queued_records": len(remaining),
        "unknown_hold_created": 0,
        "coverage_complete": len(decisions) + len(remaining) == len(family),
        "decision_states": state_counts,
        "routing_assignments": 0,
        "grouping_assignments": 0,
        "source_records_removed_or_closed": 0,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    SUMMARY.write_text(f"""# Packet 01.5 — Other Record-Specific Evidence Family v1

STATUS: BUILT — PENDING INDEPENDENT VERIFICATION
FAMILY RECORDS: {len(family)}
SUPPORTED OR DISPROVED DECISIONS: {len(decisions)}
REMAINING QUEUED: {len(remaining)}
UNKNOWN — HOLD CREATED: 0
ROUTING ASSIGNMENTS: 0
GROUPING ASSIGNMENTS: 0

The complete heterogeneous family was processed in permanent source order. Only reviewed claim-specific predicates may decide a record. Partial or unmatched evidence remains queued with exact missing predicate components.

Stop before routing, destinations, grouping, closure, implementation, or Packet 04.
""", encoding="utf-8")
    need(INVENTORY.read_bytes() == inventory_raw, "inventory changed")
    print(f"PASS: other-specific family built with {len(decisions)} decisions and {len(remaining)} queued")


if __name__ == "__main__":
    main()
