#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import packet_01_5_authoritative_law_policy as policy

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "audit"
APP = AUDIT / "applicability"
ROUTING = AUDIT / "routing-inventory"

PLAN_PATH = APP / "Packet_01.5_Authoritative_Packet_Law_Family_Pass_v1.json"
QUEUE_PATH = APP / "Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl"
INVENTORY_PATH = ROUTING / "Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
MANIFEST_PATH = APP / "Packet_01.5_Authoritative_Packet_Law_Family_Manifest_v1.json"
DECISIONS_PATH = APP / "Packet_01.5_Authoritative_Packet_Law_Family_Decisions_v1.jsonl"
REMAINING_PATH = APP / "Packet_01.5_Authoritative_Packet_Law_Family_Remaining_Queue_v1.jsonl"
MATRIX_PATH = AUDIT / "Packet_01.5_Authoritative_Packet_Law_Evidence_Matrix_v1.json"
COVERAGE_PATH = AUDIT / "Packet_01.5_Authoritative_Packet_Law_Family_Coverage_v1.json"
SUMMARY_PATH = AUDIT / "Packet_01.5_Authoritative_Packet_Law_Family_v1.md"

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
    text = item["missing_proof"]
    return text.split("Preserved claim: ", 1)[1] if "Preserved claim: " in text else text


def evidence(eid: str, reference: str, stable: str, claim: str) -> dict[str, str]:
    return {
        "evidence_id": eid,
        "source_reference": reference,
        "source_hash_or_stable_reference": stable,
        "claim_supported": claim,
    }


def remaining_entry(item: dict[str, Any], claim: str, reason: str, support: list[dict[str, Any]], conflicts: list[dict[str, Any]]) -> dict[str, Any]:
    result = dict(item)
    if conflicts:
        paths = ", ".join(sorted({entry["path"] for entry in conflicts}))
        missing = f"Resolve equal-or-higher-precedence conflict among current authority sources: {paths}."
        method = "Create a digest-bound authority adjudication showing governing tier, version precedence, and the controlling clause."
    elif support:
        paths = ", ".join(sorted({entry["path"] for entry in support}))
        missing = f"The current sources {paths} are related but do not directly prove the complete preserved claim under the required threshold."
        method = "Capture the exact governing clause or a verified completion/status receipt that closes the unsupported part of the claim."
    elif "private" in claim.lower() or "user’s" in claim.lower() or "user's" in claim.lower():
        missing = "Capture a privacy-safe authoritative receipt for the user-specific constraint or private dependency without exposing private values."
        method = "Produce a redacted digest-bound boolean receipt and connect it to the governing packet gate."
    else:
        missing = "No current authoritative governing clause or verified receipt directly proves or disproves the complete preserved claim."
        method = "Add or identify the controlling packet law, current status entry, completion receipt, or conflict-resolution record with commit and content digests."
    result["missing_proof"] = f"{missing} Resolver result: {reason}. Preserved claim: {claim}"
    result["recommended_acquisition_method"] = method
    result["decision_blocked_until"] = "The controlling authority and precedence are captured, hashed, and independently verified against this permanent address."
    result["reopening_trigger"] = "A new packet law, status ledger, completion receipt, merge commit, content digest, or authority conflict changes the controlling evidence."
    return result


def main() -> None:
    plan = load_object(PLAN_PATH)
    need(plan["family"] == "AUTHORITATIVE_PACKET_LAW", "wrong family")
    need(plan["decision_author"] != plan["decision_verifier"], "author equals verifier")
    queue_raw = QUEUE_PATH.read_bytes()
    inventory_raw = INVENTORY_PATH.read_bytes()
    need(policy.sha256(queue_raw) == QUEUE_SHA, "source queue hash changed")
    need(policy.sha256(inventory_raw) == INVENTORY_SHA, "source inventory hash changed")

    queue = load_jsonl(QUEUE_PATH)
    family = [item for item in queue if item["evidence_domain"] == "AUTHORITATIVE_PACKET_LAW"]
    need(len(family) == plan["expected_family_records"] == 25, "law-family count changed")
    need([item["source_record_ordinal"] for item in family] == sorted(item["source_record_ordinal"] for item in family), "family order changed")

    inventory = load_jsonl(INVENTORY_PATH)
    source_by_address = {item["composite_address"]: item for item in inventory}
    tracked = policy.tracked_files(REPO)
    sources, census_sha = policy.authority_sources(REPO, tracked)
    main_sha = policy.main_anchor(REPO)
    plan_sha = policy.sha256(PLAN_PATH.read_bytes())
    reviewed = plan["reviewed_predicates"]
    generic = plan["generic_direct_support"]

    decisions: list[dict[str, Any]] = []
    remaining: list[dict[str, Any]] = []
    matrix: list[dict[str, Any]] = []

    for item in family:
        address = item["composite_address"]
        claim = claim_from_queue(item)
        source = source_by_address[address]
        need(item["source_envelope_hash"] == source["envelope_hash"], f"queue/source mismatch: {address}")
        rule = next((entry for entry in reviewed if entry["claim_contains"].lower() in claim.lower()), None)
        if rule:
            passed, support, conflicts, detail = policy.reviewed_predicate(rule["predicate"], claim, sources, tracked)
            state = rule["state"]
            confidence = rule["confidence"]
            predicate = rule["predicate"]
        else:
            passed, support, conflicts, detail = policy.generic_direct(
                claim, sources, generic["minimum_claim_token_coverage"], generic["minimum_distinct_claim_tokens"]
            )
            state = generic["allowed_state"]
            confidence = generic["confidence"]
            predicate = "GENERIC_DIRECT_CURRENT_AUTHORITY_SUPPORT"

        matrix.append({
            "composite_address": address,
            "original_identifier": item["original_identifier"],
            "claim": claim,
            "predicate": predicate,
            "predicate_passed": passed,
            "state_if_passed": state,
            "confidence_if_passed": confidence,
            "support": support,
            "conflicts": conflicts,
            "detail": detail,
            "result": "DECIDED" if passed else "REMAIN_QUEUED",
        })

        if not passed:
            remaining.append(remaining_entry(item, claim, detail.get("reason", "insufficient_current_authority"), support, conflicts))
            continue

        evidence_entries = [
            evidence(f"ALF-SOURCE-{address}", f"{INVENTORY_PATH.relative_to(REPO)}#{address}", source["envelope_hash"], "Preserves the immutable source claim and permanent address."),
            evidence(f"ALF-QUEUE-{address}", f"{QUEUE_PATH.relative_to(REPO)}#{address}", f"sha256:{QUEUE_SHA}#{address}", "Proves membership in the complete authoritative-packet-law evidence family."),
            evidence(f"ALF-PLAN-{address}", f"{PLAN_PATH.relative_to(REPO)}#{predicate}", f"sha256:{plan_sha}#{predicate}", "Binds the record to the reviewed predicate, precedence rules, state, and confidence."),
            evidence(f"ALF-CENSUS-{address}", "authoritative repository law census", f"sha256:{census_sha}", "Commits the complete precedence-filtered authority-source census used for this decision."),
            evidence(f"ALF-MAIN-{address}", "origin/main", f"commit:{main_sha}", "Anchors the authority evaluation to the current main commit."),
        ]
        for index, match in enumerate(sorted(support, key=lambda entry: (entry["tier"], -entry["version"], entry["path"]))[:8], 1):
            evidence_entries.append(evidence(
                f"ALF-AUTH-{index:02d}-{address}", match["path"], f"sha256:{match['sha256']}",
                f"Tier {match['tier']} current authority directly supports the preserved claim; matched passage coverage={match.get('coverage')}."
            ))

        reasoning_sources = ", ".join(match["path"] for match in sorted(support, key=lambda entry: (entry["tier"], entry["path"]))[:5])
        decision = {
            "composite_address": address,
            "source_inventory_sha256": INVENTORY_SHA,
            "source_envelope_hash": source["envelope_hash"],
            "source_block_hash": source["source_block_hash"],
            "decision_stage": "APPLICABILITY_ONLY",
            "applicability_state": state,
            "applicability_evidence": evidence_entries,
            "applicability_reasoning_summary": f"Current precedence-filtered governing evidence directly supports the preserved claim at this address. Controlling sources: {reasoning_sources}. No equal-or-higher-precedence contradictory source blocked the decision.",
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
                "A newer governing packet law or current status record supersedes the cited authority.",
                "An equal-or-higher-precedence conflict is introduced or discovered.",
                "The cited completion receipt, merge commit, or content digest is invalidated or replaced."
            ],
            "decision_version": "Packet-01.5-Authoritative-Law-Family-v1",
            "decision_author": plan["decision_author"],
            "routing_decision_verifier": plan["decision_verifier"],
            "closure_state": "OPEN",
        }
        decisions.append(decision)

    manifest = {
        "packet": "01.5",
        "family": "AUTHORITATIVE_PACKET_LAW",
        "records": len(family),
        "source_queue_sha256": QUEUE_SHA,
        "source_inventory_sha256": INVENTORY_SHA,
        "main_commit_anchor": main_sha,
        "authority_census_sha256": census_sha,
        "authority_sources": [
            {key: source[key] for key in ("path", "tier", "family", "version", "active_version", "sha256")}
            for source in sources
        ],
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
        "packet": "01.5", "family": "AUTHORITATIVE_PACKET_LAW", "records": len(family),
        "decided": len(decisions), "remaining_queued": len(remaining), "main_commit_anchor": main_sha,
        "authority_census_sha256": census_sha, "records_matrix": matrix
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    state_counts: dict[str, int] = {}
    for item in decisions:
        state_counts[item["applicability_state"]] = state_counts.get(item["applicability_state"], 0) + 1
    COVERAGE_PATH.write_text(json.dumps({
        "packet": "01.5", "family": "AUTHORITATIVE_PACKET_LAW", "family_records": len(family),
        "decided_records": len(decisions), "remaining_queued_records": len(remaining),
        "unknown_hold_created": 0, "coverage_complete": len(decisions) + len(remaining) == len(family),
        "decision_states": state_counts, "routing_assignments": 0, "grouping_assignments": 0,
        "source_records_removed_or_closed": 0
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    SUMMARY_PATH.write_text(f"""# Packet 01.5 — Authoritative Packet Law Evidence Family v1

STATUS: BUILT — PENDING INDEPENDENT VERIFICATION
FAMILY RECORDS: {len(family)}
EVIDENCE-SUPPORTED DECISIONS: {len(decisions)}
REMAINING QUEUED: {len(remaining)}
UNKNOWN — HOLD CREATED: 0
ROUTING ASSIGNMENTS: 0
GROUPING ASSIGNMENTS: 0

The complete authoritative-packet-law family was processed in permanent source order. Decisions require direct current authority after tier and version precedence. Missing authority, private dependency, partial support, and equal-precedence conflict remain queued with exact resolution requirements.

Stop before routing, grouping, closure, implementation, or Packet 04.
""", encoding="utf-8")
    need(INVENTORY_PATH.read_bytes() == inventory_raw, "source inventory changed")
    print(f"PASS: authoritative-law family built with {len(decisions)} decisions and {len(remaining)} queued")


if __name__ == "__main__":
    main()
