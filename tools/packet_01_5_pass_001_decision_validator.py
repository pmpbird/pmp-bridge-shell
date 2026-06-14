#!/usr/bin/env python3
from __future__ import annotations
from typing import Any
import packet_01_5_scalable_pass_001_policy as policy

class DecisionError(ValueError):
    pass

def need(ok: bool, msg: str) -> None:
    if not ok:
        raise DecisionError(msg)

def validate(item: dict[str, Any], source: dict[str, Any], required: set[str], worker_sha: str, wrangler_sha: str) -> None:
    address = source["composite_address"]
    identifier, state, confidence, rule_id = policy.EXPECTED[address]
    need(set(item) == required, f"fields {address}")
    need(item["composite_address"] == address, f"address {address}")
    need(source["original_identifier"] == identifier, f"identifier {address}")
    need(item["source_inventory_sha256"] == policy.INV_SHA, f"inventory {address}")
    need(item["source_envelope_hash"] == source["envelope_hash"], f"envelope {address}")
    need(item["source_block_hash"] == source["source_block_hash"], f"block {address}")
    need(item["decision_stage"] == "APPLICABILITY_ONLY", f"stage {address}")
    need(item["applicability_state"] == state, f"state {address}")
    need(item["applicability_confidence"] == confidence, f"confidence {address}")
    need(item["applicability_state"] != "UNKNOWN — HOLD", f"hold {address}")
    need(len(item["applicability_reasoning_summary"]) > 80, f"reasoning {address}")
    entries = item["applicability_evidence"]
    need(isinstance(entries, list) and len(entries) >= 6, f"evidence {address}")
    need(all(set(x) == policy.EVIDENCE_FIELDS and all(x.values()) for x in entries), f"evidence fields {address}")
    refs = {x["source_reference"]: x for x in entries}
    need(refs["pmp-worker.js"]["source_hash_or_stable_reference"] == f"sha256:{worker_sha}", f"worker {address}")
    need(refs["wrangler.toml"]["source_hash_or_stable_reference"] == f"sha256:{wrangler_sha}", f"wrangler {address}")
    need(any(rule_id in " ".join(x.values()) for x in entries), f"rule {address}")
    need(any("Supersedes" in x["claim_supported"] for x in entries), f"supersession {address}")
    need(item["primary_destination"] is None, f"destination {address}")
    for key in ("secondary_destinations", "cross_cutting_laws", "semantic_cluster_ids", "routing_evidence", "unresolved_dependencies"):
        need(item[key] == [], f"populated {key} {address}")
    for key in ("routing_rationale", "expected_receiving_work", "expected_completion_evidence", "hold_reason"):
        need(item[key] == "", f"populated {key} {address}")
    need(item["routing_confidence"] is None, f"routing confidence {address}")
    need(len(item["reopening_conditions"]) >= 3, f"reopening {address}")
    need(item["decision_author"] != item["routing_decision_verifier"], f"independence {address}")
    need(item["closure_state"] == "OPEN", f"closure {address}")
