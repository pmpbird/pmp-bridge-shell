#!/usr/bin/env python3
"""Classify Packet 01.5 applicability batch 001 without routing destinations.

Batch 001 contains baseline addresses P01.5::B::0001 through P01.5::B::0100.
The 2750-envelope blank inventory remains preserved as the rollback parent.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "audit"
ROUTING = AUDIT / "routing-inventory"

PARENT = ROUTING / "Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
PARENT_VERIFY = AUDIT / "Packet_01.5_Blank_Routing_Inventory_Independent_Verification_v1.json"
BASELINE = AUDIT / "baseline-source" / "reconstructed" / "pmp-current-permanent-limitation-register-v3-final.json"
CONTACT_CATALOG = AUDIT / "Packet_01.5_Canonical_Project_Contact_Evidence_Catalog_v1.json"
CONTACT_VERIFY = AUDIT / "Packet_01.5_Canonical_Project_Contact_Evidence_Independent_Verification_v1.json"

CHILD = ROUTING / "Packet_01.5_Applicability_Inventory_v2_Batch_001.jsonl"
CHILD_GZ = ROUTING / "Packet_01.5_Applicability_Inventory_v2_Batch_001.jsonl.gz"
MANIFEST = ROUTING / "Packet_01.5_Applicability_Inventory_v2_Batch_001.manifest.json"
DECISIONS = AUDIT / "Packet_01.5_Applicability_Batch_001_Decisions_v1.json"
RECEIPT_JSON = AUDIT / "Packet_01.5_Applicability_Batch_001_Build_v1.json"
RECEIPT_MD = AUDIT / "Packet_01.5_Applicability_Batch_001_Build_v1.md"

DORMANT_STATES = {
    "CURRENT CONFLICT RESOLVED — HISTORY PRESERVED",
    "CURRENT BASELINE PROVEN — REOPENABLE",
    "CURRENT DEPLOYED PATH EXECUTED — REOPENABLE",
}
CONDITIONAL_STATES = {
    "VERIFIED UNKNOWN",
    "CONDITIONAL UNKNOWN",
    "VERIFIED WATCH",
    "VERIFIED BOUNDARY",
    "CONDITIONAL PRODUCT DECISION",
    "CONDITIONAL/OPEN",
    "CONDITIONAL PLATFORM LIMIT",
}
PLANNED_EVIDENCE_STATES = {
    "CONDITIONAL UNKNOWN",
    "CONDITIONAL PRODUCT DECISION",
    "CONDITIONAL/OPEN",
    "CONDITIONAL PLATFORM LIMIT",
}
IMMUTABLE_FIELDS = [
    "composite_address", "source_set", "source_path", "source_pass",
    "source_file_hash", "source_record_ordinal", "original_identifier",
    "original_heading", "original_body", "source_block_hash", "harm_text",
    "overlap_text", "legacy_exception_codes", "normalization_version",
]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def envelope_hash(envelope: dict[str, Any]) -> str:
    value = dict(envelope)
    value.pop("envelope_hash", None)
    return sha256(canonical(value))


def classify(record: dict[str, Any]) -> tuple[str, str]:
    state = record["state"]
    if state in DORMANT_STATES:
        return "DORMANT_FUTURE_RISK", "CURRENT_CONTACT"
    if state in CONDITIONAL_STATES:
        evidence_type = "PLANNED_CONTACT" if state in PLANNED_EVIDENCE_STATES else "CURRENT_CONTACT"
        return "ACTIVE_CONDITIONAL_RISK", evidence_type
    return "CURRENT_DEFECT", "CURRENT_CONTACT"


def explanation(record: dict[str, Any], applicability: str) -> str:
    if applicability == "DORMANT_FUTURE_RISK":
        return (
            f"The permanent register records state '{record['state']}', showing the named current condition was "
            "proven or resolved while reopening remains event-triggered."
        )
    if applicability == "ACTIVE_CONDITIONAL_RISK":
        return (
            f"The permanent register records state '{record['state']}' and coverage '{record['coverage_status']}'. "
            "The risk has an explicit current or approved planned project contact, but occurrence or final product "
            "conditions remain unresolved."
        )
    return (
        f"The permanent register records state '{record['state']}', lifecycle "
        f"'{record['lifecycle_state']}', and evidence '{record['evidence']}', directly identifying an open current "
        "project limitation, gap, absence, conflict, or unproven required control."
    )


def deterministic_gzip(data: bytes) -> bytes:
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", fileobj=buffer, mode="wb", mtime=0, compresslevel=9) as stream:
        stream.write(data)
    return buffer.getvalue()


def main() -> None:
    parent_raw = PARENT.read_bytes()
    parent_verify = json.loads(PARENT_VERIFY.read_text(encoding="utf-8"))
    require(parent_verify.get("status") == "PASS", "parent inventory verification did not pass")
    require(parent_verify.get("inventory_sha256") == sha256(parent_raw), "parent inventory hash mismatch")

    contact_catalog = json.loads(CONTACT_CATALOG.read_text(encoding="utf-8"))
    contact_verify = json.loads(CONTACT_VERIFY.read_text(encoding="utf-8"))
    require(contact_verify.get("status") == "PASS", "project-contact catalog verification did not pass")
    require(contact_verify.get("catalog_sha256") == sha256(CONTACT_CATALOG.read_bytes()), "project-contact catalog hash mismatch")
    require(contact_catalog.get("counts", {}).get("capability_contacts") == 20, "project-contact capability count mismatch")

    baseline_raw = BASELINE.read_bytes()
    require(sha256(baseline_raw) == "ac36b36a38d2ad9ab9f73d69679e0ecc0dae4c2f3340fe505f6ed773c56ba5f4", "baseline source hash mismatch")
    baseline_records = json.loads(baseline_raw)["limitations"]
    require(len(baseline_records) == 122, "baseline source count mismatch")

    parent_lines = parent_raw.splitlines()
    require(len(parent_lines) == 2750, "parent inventory line count mismatch")
    child_lines: list[bytes] = []
    decisions: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()

    for line_number, line in enumerate(parent_lines, 1):
        envelope = json.loads(line)
        address = envelope["composite_address"]
        if line_number <= 100:
            expected_address = f"P01.5::B::{line_number:04d}"
            require(address == expected_address, f"batch address mismatch at line {line_number}")
            require(envelope["source_set"] == "BASELINE", f"batch source set mismatch at {address}")
            require(envelope["applicability_state"] == "UNCLASSIFIED", f"parent applicability not blank at {address}")
            require(envelope["routing_state"] == "UNROUTED", f"parent routing not blank at {address}")
            record = baseline_records[line_number - 1]
            require(record["id"] == envelope["original_identifier"], f"baseline identifier mismatch at {address}")
            applicability, evidence_type = classify(record)
            record_hash = sha256(canonical(record))
            evidence = {
                "evidence_id": f"APP-B001-{line_number:04d}",
                "evidence_type": evidence_type,
                "source_reference": f"archive://Packet_03.5_v4_FINAL_PASS_COMPLETE.zip!/pmp-current-permanent-limitation-register-v3-final.json#limitations[{line_number - 1}]",
                "source_hash_or_stable_reference": f"sha256:ac36b36a38d2ad9ab9f73d69679e0ecc0dae4c2f3340fe505f6ed773c56ba5f4;record-sha256:{record_hash}",
                "contact_path_explanation": explanation(record, applicability),
                "decision_rationale": (
                    f"Classified from the individual permanent-register state '{record['state']}', evidence "
                    f"'{record['evidence']}', coverage '{record['coverage_status']}', and named lifecycle owners. "
                    "No domain-name-only inference was used."
                ),
            }
            before = {field: envelope[field] for field in IMMUTABLE_FIELDS}
            envelope["applicability_state"] = applicability
            envelope["applicability_evidence"] = [evidence]
            envelope["envelope_hash"] = envelope_hash(envelope)
            after = {field: envelope[field] for field in IMMUTABLE_FIELDS}
            require(before == after, f"immutable fields changed at {address}")
            counts[applicability] += 1
            decisions.append({
                "composite_address": address,
                "original_identifier": record["id"],
                "register_state": record["state"],
                "coverage_status": record["coverage_status"],
                "applicability_state": applicability,
                "evidence_type": evidence_type,
                "evidence_id": evidence["evidence_id"],
                "record_sha256": record_hash,
                "child_envelope_hash": envelope["envelope_hash"],
            })
            child_lines.append(canonical(envelope))
        else:
            child_lines.append(line)

    require(len(decisions) == 100, "batch decision count mismatch")
    require(dict(counts) == {
        "CURRENT_DEFECT": 85,
        "ACTIVE_CONDITIONAL_RISK": 12,
        "DORMANT_FUTURE_RISK": 3,
    }, f"classification count mismatch: {dict(counts)}")

    child_raw = b"\n".join(child_lines) + b"\n"
    compressed = deterministic_gzip(child_raw)
    CHILD.write_bytes(child_raw)
    CHILD_GZ.write_bytes(compressed)

    decisions_doc = {
        "packet": "01.5",
        "batch": "001",
        "version": 1,
        "status": "BUILT_PENDING_INDEPENDENT_VERIFICATION",
        "watch": "NONE",
        "blockers": "NONE",
        "parent_inventory_sha256": sha256(parent_raw),
        "child_inventory_sha256": sha256(child_raw),
        "address_first": "P01.5::B::0001",
        "address_last": "P01.5::B::0100",
        "decision_count": 100,
        "classification_counts": dict(counts),
        "final_owner_destinations_populated": 0,
        "decisions": decisions,
    }
    DECISIONS.write_text(json.dumps(decisions_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    manifest = {
        "packet": "01.5",
        "inventory": "applicability_inventory",
        "version": 2,
        "batch": "001",
        "status": "BUILT_PENDING_INDEPENDENT_VERIFICATION",
        "watch": "NONE",
        "blockers": "NONE",
        "parent": {
            "path": str(PARENT.relative_to(REPO)),
            "bytes": len(parent_raw),
            "sha256": sha256(parent_raw),
            "envelopes": 2750,
        },
        "child": {
            "path": str(CHILD.relative_to(REPO)),
            "bytes": len(child_raw),
            "sha256": sha256(child_raw),
            "envelopes": 2750,
        },
        "child_gzip": {
            "path": str(CHILD_GZ.relative_to(REPO)),
            "bytes": len(compressed),
            "sha256": sha256(compressed),
            "mtime": 0,
        },
        "classified_batch": {
            "first": "P01.5::B::0001",
            "last": "P01.5::B::0100",
            "count": 100,
            "classification_counts": dict(counts),
        },
        "remaining_unclassified": 2650,
        "routing_state": "UNROUTED",
        "final_owner_destinations_populated": 0,
        "immutable_fields_preserved": True,
        "source_records_removed": 0,
        "source_records_closed": 0,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    receipt = {
        "packet": "01.5",
        "build": "applicability_batch_001",
        "version": 1,
        "status": "PASS",
        "watch": "NONE",
        "blockers": "NONE",
        "parent_inventory_sha256": sha256(parent_raw),
        "child_inventory_sha256": sha256(child_raw),
        "classified": 100,
        "remaining_unclassified": 2650,
        "classification_counts": dict(counts),
        "routing_assignments_completed": 0,
        "source_records_removed": 0,
        "source_records_closed": 0,
    }
    RECEIPT_JSON.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    RECEIPT_MD.write_text("\n".join([
        "# Packet 01.5 — Applicability Batch 001 Build v1",
        "",
        "STATUS: PASS",
        "WATCH: NONE",
        "BLOCKERS: NONE",
        "FINAL OWNER ROUTING: NOT STARTED",
        "",
        "- Batch addresses: `P01.5::B::0001` through `P01.5::B::0100`",
        "- Classified envelopes: 100",
        "- CURRENT_DEFECT: 85",
        "- ACTIVE_CONDITIONAL_RISK: 12",
        "- DORMANT_FUTURE_RISK: 3",
        "- OUT_OF_SCOPE_CANDIDATE: 0",
        "- Remaining UNCLASSIFIED: 2650",
        "- Final owner destinations populated: 0",
        "- Source records removed: 0",
        "- Source records closed: 0",
        f"- Parent inventory SHA-256: `{sha256(parent_raw)}`",
        f"- Child inventory SHA-256: `{sha256(child_raw)}`",
        "",
        "END PACKET 01.5 — APPLICABILITY BATCH 001 BUILD v1",
        "",
    ]), encoding="utf-8")
    print("PASS — built applicability batch 001 for 100 envelopes")


if __name__ == "__main__":
    main()
