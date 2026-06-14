#!/usr/bin/env python3
"""Independently verify one Packet 01.5 applicability batch."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "audit"
CATALOG_PATH = AUDIT / "routing-evidence/Packet_01.5_Project_Contact_Evidence_Catalog_v1.json"
CATALOG_VERIFY_PATH = AUDIT / "Packet_01.5_Project_Contact_Evidence_Catalog_Independent_Verification_v1.json"

IMMUTABLE_FIELDS = [
    "composite_address", "source_set", "source_path", "source_pass",
    "source_file_hash", "source_record_ordinal", "original_identifier",
    "original_heading", "original_body", "source_block_hash", "harm_text",
    "overlap_text", "legacy_exception_codes", "normalization_version",
]
REQUIRED_EVIDENCE_FIELDS = {
    "evidence_id", "evidence_type", "source_reference",
    "source_hash_or_stable_reference", "contact_path_explanation",
    "decision_rationale",
}
ALLOWED_EVIDENCE_TYPES = {
    "CURRENT_CONTACT", "PLANNED_CONTACT", "ABSENT_CONTACT", "SCOPE_EXCLUSION",
}


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


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"not a JSON object: {path}")
    return value


def load_jsonl(path: Path) -> tuple[list[dict[str, Any]], bytes]:
    raw = path.read_bytes()
    values: list[dict[str, Any]] = []
    for number, line in enumerate(raw.splitlines(), 1):
        value = json.loads(line)
        require(isinstance(value, dict), f"line {number} is not an object: {path}")
        values.append(value)
    return values, raw


def repository_path(value: str) -> Path:
    path = REPO / value
    require(path.resolve().is_relative_to(REPO.resolve()), f"path escapes repository: {value}")
    return path


def batch_number(batch_id: str) -> int:
    match = re.fullmatch(r"P01\.5-APP-B(\d{3})", batch_id)
    require(match is not None, f"invalid batch identifier: {batch_id}")
    return int(match.group(1))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True)
    args = parser.parse_args()

    plan_path = repository_path(args.plan)
    plan = load_json(plan_path)
    batch_id = plan["batch"]
    number = batch_number(batch_id)
    parent_path = repository_path(plan["parent_inventory"]["path"])
    child_path = repository_path(plan["child_inventory"]["path"])
    child_gzip_path = child_path.with_suffix(child_path.suffix + ".gz")
    child_manifest_path = child_path.with_name(child_path.stem + ".manifest.json")
    batch_dir = AUDIT / "routing-batches"
    output_json = batch_dir / f"Packet_01.5_Applicability_Batch_{number:03d}_Independent_Verification_v1.json"
    output_md = batch_dir / f"Packet_01.5_Applicability_Batch_{number:03d}_Independent_Verification_v1.md"
    status_version = 76 + number
    status_path = AUDIT / f"Packet_01.5_Applicability_Classification_Status_v{status_version}.md"

    parent, parent_raw = load_jsonl(parent_path)
    child, child_raw = load_jsonl(child_path)
    manifest = load_json(child_manifest_path)
    catalog = load_json(CATALOG_PATH)
    catalog_verify = load_json(CATALOG_VERIFY_PATH)

    expected_parent_sha = plan["parent_inventory"]["sha256"]
    require(sha256(parent_raw) == expected_parent_sha, "parent inventory hash mismatch")
    require(len(parent) == len(child) == 2750, "parent/child count mismatch")
    require(catalog_verify.get("status") == "PASS", "contact catalog verification is not PASS")
    require(catalog_verify.get("watch") == "NONE" and catalog_verify.get("blockers") == "NONE", "contact catalog verification is not clean")
    require(manifest.get("batch") == batch_id, "manifest batch mismatch")
    require(manifest.get("parent", {}).get("sha256") == expected_parent_sha, "manifest parent hash mismatch")
    require(manifest.get("child", {}).get("sha256") == sha256(child_raw), "manifest child hash mismatch")
    require(manifest.get("child", {}).get("bytes") == len(child_raw), "manifest child byte count mismatch")
    compressed = child_gzip_path.read_bytes()
    require(manifest.get("gzip", {}).get("sha256") == sha256(compressed), "manifest gzip hash mismatch")
    require(gzip.decompress(compressed) == child_raw, "gzip reverse reconstruction mismatch")

    parent_addresses = [item["composite_address"] for item in parent]
    child_addresses = [item["composite_address"] for item in child]
    require(parent_addresses == child_addresses, "address order changed")
    require(len(set(child_addresses)) == 2750, "child addresses are not unique")

    selected = plan["selection"]["addresses"]
    decisions = plan["decisions"]
    decision_by_address = {item["address"]: item for item in decisions}
    require(len(selected) == len(decisions) == plan["selection"]["count"], "selection count mismatch")
    require(len(decision_by_address) == len(decisions), "decision addresses are not unique")
    require(set(selected) == set(decision_by_address), "decision and selection sets differ")

    catalog_ids = {
        item["evidence_id"] for item in catalog["current_capabilities"]
    } | {
        item["evidence_id"] for item in catalog["boundary_evidence"]
    }
    require(len(catalog_ids) == 26, "catalog evidence identifier count mismatch")

    changed: list[str] = []
    for before, after in zip(parent, child):
        address = before["composite_address"]
        require(after["envelope_hash"] == envelope_hash(after), f"envelope hash mismatch at {address}")
        for field in IMMUTABLE_FIELDS:
            require(after.get(field) == before.get(field), f"immutable field changed ({field}) at {address}")
        require(after.get("routing_state") == "UNROUTED", f"routing state changed at {address}")
        require(after.get("primary_destination") is None, f"primary destination populated at {address}")
        for field in ("secondary_destinations", "cross_cutting_laws", "watch_triggers", "semantic_cluster_ids"):
            require(after.get(field) == [], f"routing field populated ({field}) at {address}")

        if before != after:
            changed.append(address)
            decision = decision_by_address.get(address)
            require(decision is not None, f"unplanned envelope changed: {address}")
            require(before.get("applicability_state") == "UNCLASSIFIED", f"selected parent was already classified: {address}")
            require(after.get("original_identifier") == decision["original_identifier"], f"identifier mismatch at {address}")
            require(after.get("applicability_state") == decision["state"], f"state mismatch at {address}")
            require(after.get("applicability_batch_id") == batch_id, f"batch identifier mismatch at {address}")
            require(after.get("applicability_parent_envelope_hash") == before["envelope_hash"], f"parent envelope hash mismatch at {address}")
            evidence = after.get("applicability_evidence")
            require(isinstance(evidence, list) and len(evidence) >= 2, f"insufficient evidence at {address}")
            evidence_ids: list[str] = []
            catalog_references: set[str] = set()
            source_entries = 0
            for entry in evidence:
                require(REQUIRED_EVIDENCE_FIELDS <= set(entry), f"evidence schema incomplete at {address}")
                require(entry["evidence_type"] in ALLOWED_EVIDENCE_TYPES, f"invalid evidence type at {address}")
                for field in REQUIRED_EVIDENCE_FIELDS:
                    require(bool(entry[field]), f"empty evidence field {field} at {address}")
                evidence_ids.append(entry["evidence_id"])
                catalog_id = entry.get("catalog_evidence_id")
                if catalog_id is None:
                    source_entries += 1
                    require(entry["evidence_type"] == decision["source_evidence_type"], f"source evidence type mismatch at {address}")
                else:
                    require(catalog_id in catalog_ids, f"unknown catalog evidence at {address}: {catalog_id}")
                    catalog_references.add(catalog_id)
            require(len(evidence_ids) == len(set(evidence_ids)), f"duplicate evidence identifiers at {address}")
            require(source_entries == 1, f"source-record evidence count mismatch at {address}")
            require(catalog_references == set(decision["catalog_evidence_ids"]), f"catalog evidence set mismatch at {address}")
        else:
            require(address not in decision_by_address, f"planned envelope was unchanged: {address}")

    require(changed == selected, "changed address order differs from selection")
    state_counts = Counter(item["applicability_state"] for item in child)
    expected_counts = Counter({key: value for key, value in plan["expected_result"].items() if key != "routing_assignments" and value})
    require(state_counts == expected_counts, f"state totals mismatch: {dict(state_counts)} vs {dict(expected_counts)}")
    require(manifest.get("changed_envelopes") == len(selected), "manifest changed-envelope count mismatch")
    require(manifest.get("unchanged_envelopes") == 2750 - len(selected), "manifest unchanged-envelope count mismatch")
    require(manifest.get("routing_assignments") == 0, "manifest routing assignments are not zero")
    require(manifest.get("source_count_delta") == 0 and manifest.get("record_completion_count") == 0, "manifest preservation counts are not zero")

    child_sha = sha256(child_raw)
    classified = 2750 - state_counts.get("UNCLASSIFIED", 0)
    result = {
        "packet": "01.5", "verification": "applicability_batch_independent",
        "version": 1, "verification_date": date.today().isoformat(),
        "status": "PASS_ACCEPTED", "watch": "NONE", "blockers": "NONE",
        "batch": batch_id, "parent_inventory_sha256": expected_parent_sha,
        "child_inventory_sha256": child_sha, "combined_envelopes": 2750,
        "unique_addresses": 2750, "changed_envelopes": len(selected),
        "classified_envelopes_total": classified,
        "state_counts": dict(sorted(state_counts.items())),
        "immutable_field_match": "PASS", "address_sequence_match": "PASS",
        "evidence_schema_match": "PASS", "catalog_reference_match": "PASS",
        "routing_fields_blank": "PASS", "gzip_reverse_reconstruction": "PASS",
        "routing_assignments": 0, "source_count_delta": 0,
        "record_completion_count": 0, "next_batch_ready": True,
    }
    batch_dir.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    state_lines = [f"- {state}: {count}" for state, count in sorted(state_counts.items())]
    output_md.write_text("\n".join([
        f"# Packet 01.5 — Applicability Batch {number:03d} Independent Verification v1", "",
        "STATUS: PASS — BATCH ACCEPTED", "WATCH: NONE", "BLOCKERS: NONE",
        "ROUTING ASSIGNMENTS: 0", "", "## Transaction result", "",
        "- Parent envelopes: 2750", "- Child envelopes: 2750", "- Unique addresses: 2750",
        f"- Changed envelopes: {len(selected)}", f"- Classified envelopes total: {classified}",
        *state_lines, f"- Parent SHA-256: `{expected_parent_sha}`", f"- Child SHA-256: `{child_sha}`", "",
        "## Lossless proof", "", "- Immutable source-field equality: PASS",
        "- Address-sequence equality: PASS", "- Evidence schema and catalog references: PASS",
        "- Destination fields remain blank: PASS", "- Deterministic gzip reconstruction: PASS",
        "- Source count delta: 0", "- Record completion count: 0", "",
        f"FINAL RESULT: `PASS — APPLICABILITY BATCH {number:03d} ACCEPTED`", "",
        "WATCH: NONE", "", "BLOCKERS: NONE", "",
    ]), encoding="utf-8")

    next_number = number + 1
    last_ordinal = int(selected[-1].rsplit("::", 1)[-1]) if selected[-1].rsplit("::", 1)[-1].isdigit() else None
    if last_ordinal is not None:
        next_start = last_ordinal + 1
        next_end = next_start + 9
        next_action = (
            f"Prepare and independently verify Applicability Batch {next_number:03d} for "
            f"`P01.5::B::{next_start:04d}` through `P01.5::B::{next_end:04d}`, using the accepted "
            f"Batch {number:03d} child inventory as the parent and keeping destination fields blank."
        )
    else:
        next_action = f"Prepare the next verified applicability batch from the accepted Batch {number:03d} child inventory."

    full_states = ["CURRENT_DEFECT", "ACTIVE_CONDITIONAL_RISK", "DORMANT_FUTURE_RISK", "OUT_OF_SCOPE_CANDIDATE", "UNCLASSIFIED"]
    status_path.write_text("\n".join([
        f"# Packet 01.5 — Applicability Classification Status v{status_version}", "",
        f"STATUS: BATCH {number:03d} ACCEPTED", "WATCH: NONE", "BLOCKERS: NONE",
        "ROUTING START: AUTHORIZED", f"APPLICABILITY CLASSIFICATIONS COMPLETED: {classified} OF 2750",
        "ROUTING ASSIGNMENTS COMPLETED: 0", "SEMANTIC COMBINATION: NOT AUTHORIZED",
        "INDIVIDUAL RECORD CLOSURE: NOT AUTHORIZED", "PACKET 04: NOT AUTHORIZED", "",
        "## Accepted state counts", "",
        *[f"- {state}: {state_counts.get(state, 0)}" for state in full_states], "",
        "## Preservation", "", "- Total envelopes: 2750", "- Unique addresses: 2750",
        "- Source wording and hashes preserved: PASS", "- Destination fields populated: 0",
        "- Source count delta: 0", "- Record completion count: 0", "",
        "## Next required action", "", next_action, "",
    ]), encoding="utf-8")
    print(f"PASS — {batch_id} independently accepted")


if __name__ == "__main__":
    main()
