#!/usr/bin/env python3
from __future__ import annotations
import copy
import packet_01_5_pass_001_decision_validator as dv
import packet_01_5_pass_001_queue_validator as qv

def run(decision, decision_source, queue, queue_source, required, worker_sha, wrangler_sha) -> int:
    decision_cases = []
    for name in ("hold", "destination", "bad_hash", "same_author", "missing_evidence", "closed"):
        item = copy.deepcopy(decision)
        if name == "hold": item["applicability_state"] = "UNKNOWN — HOLD"
        elif name == "destination": item["primary_destination"] = "Packet 06"
        elif name == "bad_hash": item["source_envelope_hash"] = "0" * 64
        elif name == "same_author": item["routing_decision_verifier"] = item["decision_author"]
        elif name == "missing_evidence": item["applicability_evidence"] = []
        elif name == "closed": item["closure_state"] = "CLOSED"
        decision_cases.append(item)
    queue_cases = []
    for name in ("missing_field", "wrong_domain", "bad_hash", "blank_proof"):
        item = copy.deepcopy(queue)
        if name == "missing_field": item.pop("missing_proof")
        elif name == "wrong_domain": item["evidence_domain"] = "CROSS_SOURCE_CONFLICT"
        elif name == "bad_hash": item["source_envelope_hash"] = "0" * 64
        elif name == "blank_proof": item["missing_proof"] = ""
        queue_cases.append(item)
    rejected = 0
    for item in decision_cases:
        try: dv.validate(item, decision_source, required, worker_sha, wrangler_sha)
        except dv.DecisionError: rejected += 1
    for item in queue_cases:
        try: qv.validate(item, queue_source)
        except qv.QueueError: rejected += 1
    if rejected != len(decision_cases) + len(queue_cases):
        raise ValueError("an adversarial mutation passed")
    return rejected
