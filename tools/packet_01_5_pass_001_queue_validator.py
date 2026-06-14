#!/usr/bin/env python3
from __future__ import annotations
from typing import Any
import packet_01_5_scalable_pass_001_policy as policy

class QueueError(ValueError):
    pass

def need(ok: bool, msg: str) -> None:
    if not ok:
        raise QueueError(msg)

def validate(item: dict[str, Any], source: dict[str, Any]) -> None:
    address = source["composite_address"]
    need(set(item) == policy.QUEUE_FIELDS, f"fields {address}")
    need(item["composite_address"] == address, f"address {address}")
    need(item["source_record_ordinal"] == source["source_record_ordinal"], f"ordinal {address}")
    need(item["original_identifier"] == source["original_identifier"], f"identifier {address}")
    need(item["source_envelope_hash"] == source["envelope_hash"], f"hash {address}")
    need(item["evidence_domain"] == policy.evidence_domain(source), f"domain {address}")
    need(item["queue_id"] == f"SP001-{item['evidence_domain']}", f"queue id {address}")
    need(source["harm_text"] in item["missing_proof"], f"specificity {address}")
    for key in ("missing_proof", "recommended_acquisition_method", "decision_blocked_until", "reopening_trigger"):
        need(isinstance(item[key], str) and bool(item[key].strip()), f"blank {key} {address}")
