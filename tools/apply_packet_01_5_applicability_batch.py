#!/usr/bin/env python3
"""Apply one Packet 01.5 applicability batch as a lossless transaction.

The plan identifies a verified parent inventory, selected addresses, evidence,
and applicability decisions. This tool changes only the selected applicability
fields. It never assigns routing destinations, combines source envelopes,
removes records, or closes records.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
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
ALLOWED_STATES = {
    "CURRENT_DEFECT", "ACTIVE_CONDITIONAL_RISK",
    "DORMANT_FUTURE_RISK", "OUT_OF_SCOPE_CANDIDATE",
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


def write_deterministic_gzip(path: Path, data: bytes) -> bytes:
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0, compresslevel=9) as stream:
        stream.write(data)
    compressed = buffer.getvalue()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(compressed)
    return compressed


def catalog_index(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    current_rule = catalog["current_capability_rule"]
    summary = catalog["preserved_summary_source"]
    for item in catalog["current_capabilities"]:
        entry = dict(item)
        entry["evidence_type"] = current_rule["evidence_type"]
        entry["source_reference"] = summary["path"]
        entry["source_hash_or_stable_reference"] = summary["sha256"]
        entry["explanation"] = (
            f"Packet 03 verifies {item['capability_id']} as a current capability. "
            "A record-specific harm path is still required."
        )
        result[entry["evidence_id"]] = entry
    boundary_source = catalog["boundary_source"]
    for item in catalog["boundary_evidence"]:
        entry = dict(item)
        entry["source_reference"] = boundary_source["path"]
        entry["source_hash_or_stable_reference"] = boundary_source["parent_source_sha256"]
        result[entry["evidence_id"]] = entry
    require(len(result) == 26, "contact catalog index count mismatch")
    return result


def infer_batch_number(batch_id: str) -> int:
    match = re.fullmatch(r"P01\.5-APP-B(\d{3})", batch_id)
    require(match is not None, f"invalid batch identifier: {batch_id}")
    return int(match.group(1))


def relative_path(value: str) -> Path:
    path = REPO / value
    require(path.resolve().is_relative_to(REPO.resolve()), f"path escapes repository: {value}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, help="Repository-relative batch plan JSON path")
    args = parser.parse_args()

    plan_path = relative_path(args.plan)
    plan = load_json(plan_path)
    batch_id = plan.get("batch")
    require(isinstance(batch_id, str), "batch identifier missing")
    batch_number = infer_batch_number(batch_id)

    parent_meta = plan.get("parent_inventory", {})
    child_meta = plan.get("child_inventory", {})
    parent_path = relative_path(parent_meta["path"])
    child_path = relative_path(child_meta["path"])
    child_gzip_path = child_path.with_suffix(child_path.suffix + ".gz")
    child_manifest_path = child_path.with_name(child_path.stem + ".manifest.json")
    batch_dir = AUDIT / "routing-batches"
    build_json_path = batch_dir / f"Packet_01.5_Applicability_Batch_{batch_number:03d}_Build_v1.json"
    build_md_path = batch_dir / f"Packet_01.5_Applicability_Batch_{batch_number:03d}_Build_v1.md"

    parent_envelopes, parent_raw = load_jsonl(parent_path)
    expected_parent_hash = parent_meta.get("sha256")
    require(sha256(parent_raw) == expected_parent_hash, "parent inventory SHA-256 mismatch")
    require(len(parent_envelopes) == parent_meta.get("envelopes") == 2750, "parent inventory count mismatch")

    catalog = load_json(CATALOG_PATH)
    catalog_verify = load_json(CATALOG_VERIFY_PATH)
    require(catalog_verify.get("status") == "PASS", "contact catalog verification is not PASS")
    require(catalog_verify.get("watch") == "NONE" and catalog_verify.get("blockers") == "NONE", "contact catalog verification is not clean")
    evidence_index = catalog_index(catalog)
    catalog_hash = sha256(CATALOG_PATH.read_bytes())

    decisions = plan.get("decisions")
    selected = plan.get("selection", {}).get("addresses")
    require(isinstance(decisions, list) and isinstance(selected, list), "plan decisions or selection missing")
    require(1 <= len(decisions) <= 100, "batch decision count must be between 1 and 100")
    require(len(decisions) == len(selected) == plan["selection"]["count"], "batch selection count mismatch")
    decision_by_address = {item["address"]: item for item in decisions}
    require(len(decision_by_address) == len(decisions), "decision addresses are not unique")
    require(set(decision_by_address) == set(selected), "decision and selection address sets differ")

    parent_by_address = {item["composite_address"]: item for item in parent_envelopes}
    require(len(parent_by_address) == 2750, "parent addresses are not unique")
    for address in selected:
        require(address in parent_by_address, f"selected address is absent: {address}")
        require(parent_by_address[address].get("applicability_state") == "UNCLASSIFIED", f"selected address is already classified: {address}")

    child_envelopes: list[dict[str, Any]] = []
    changed_addresses: list[str] = []
    for parent in parent_envelopes:
        address = parent["composite_address"]
        child = dict(parent)
        decision = decision_by_address.get(address)
        if decision is not None:
            state = decision.get("state")
            require(state in ALLOWED_STATES, f"invalid applicability state at {address}")
            require(parent.get("original_identifier") == decision.get("original_identifier"), f"identifier mismatch at {address}")
            source_type = decision.get("source_evidence_type")
            require(source_type in ALLOWED_EVIDENCE_TYPES, f"invalid source evidence type at {address}")
            catalog_ids = decision.get("catalog_evidence_ids")
            require(isinstance(catalog_ids, list) and catalog_ids, f"catalog evidence missing at {address}")
            require(len(catalog_ids) == len(set(catalog_ids)), f"duplicate catalog evidence at {address}")

            evidence_entries: list[dict[str, Any]] = []
            for catalog_id in catalog_ids:
                source = evidence_index.get(catalog_id)
                require(source is not None, f"unknown catalog evidence at {address}: {catalog_id}")
                evidence_entries.append({
                    "evidence_id": f"{batch_id}::{address}::{catalog_id}",
                    "catalog_evidence_id": catalog_id,
                    "evidence_type": source["evidence_type"],
                    "source_reference": source["source_reference"],
                    "source_hash_or_stable_reference": source["source_hash_or_stable_reference"],
                    "contact_path_explanation": f"{decision['contact_path']} Catalog basis: {source['explanation']}",
                    "decision_rationale": decision["rationale"],
                })
            evidence_entries.append({
                "evidence_id": f"{batch_id}::{address}::SOURCE-RECORD",
                "catalog_evidence_id": None,
                "evidence_type": source_type,
                "source_reference": parent["source_path"],
                "source_hash_or_stable_reference": parent["source_file_hash"],
                "contact_path_explanation": decision["contact_path"],
                "decision_rationale": f"Original source record: {parent['original_heading']}. {decision['rationale']}",
            })

            child["applicability_state"] = state
            child["applicability_evidence"] = evidence_entries
            child["applicability_batch_id"] = batch_id
            child["applicability_parent_envelope_hash"] = parent["envelope_hash"]
            child["applicability_catalog_hash"] = catalog_hash
            child["applicability_decision_hash"] = sha256(canonical({"address": address, "state": state, "evidence": evidence_entries}))
            child["envelope_hash"] = envelope_hash(child)
            changed_addresses.append(address)
        child_envelopes.append(child)

    require(changed_addresses == selected, "changed address order differs from plan selection")
    require(len(child_envelopes) == 2750, "child envelope count mismatch")
    require([item["composite_address"] for item in child_envelopes] == [item["composite_address"] for item in parent_envelopes], "address order changed")

    changed_count = 0
    for parent, child in zip(parent_envelopes, child_envelopes):
        address = parent["composite_address"]
        for field in IMMUTABLE_FIELDS:
            require(child.get(field) == parent.get(field), f"immutable field changed ({field}) at {address}")
        require(child.get("routing_state") == "UNROUTED", f"routing state changed at {address}")
        require(child.get("primary_destination") is None, f"primary destination populated at {address}")
        for field in ("secondary_destinations", "cross_cutting_laws", "watch_triggers", "semantic_cluster_ids"):
            require(child.get(field) == [], f"routing field populated ({field}) at {address}")
        require(child["envelope_hash"] == envelope_hash(child), f"envelope hash mismatch at {address}")
        if parent != child:
            changed_count += 1
    require(changed_count == len(selected), "changed envelope count mismatch")

    state_counts = Counter(item["applicability_state"] for item in child_envelopes)
    expected_counts = Counter({key: value for key, value in plan["expected_result"].items() if key != "routing_assignments" and value})
    require(state_counts == expected_counts, f"state totals differ from plan: {dict(state_counts)} vs {dict(expected_counts)}")
    require(plan["expected_result"].get("routing_assignments") == 0, "plan expects routing assignments")

    raw_child = ("\n".join(json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for item in child_envelopes) + "\n").encode("utf-8")
    child_path.parent.mkdir(parents=True, exist_ok=True)
    child_path.write_bytes(raw_child)
    compressed = write_deterministic_gzip(child_gzip_path, raw_child)
    address_sequence_hash = sha256(("\n".join(item["composite_address"] for item in child_envelopes) + "\n").encode("utf-8"))

    manifest = {
        "packet": "01.5", "inventory": "applicability_inventory",
        "version": child_meta["version"], "batch": batch_id,
        "build_date": date.today().isoformat(),
        "status": "BUILT_PENDING_INDEPENDENT_VERIFICATION",
        "watch": "NONE", "blockers": "NONE",
        "parent": {"path": parent_meta["path"], "sha256": expected_parent_hash, "envelopes": 2750},
        "child": {"path": child_meta["path"], "bytes": len(raw_child), "sha256": sha256(raw_child), "envelopes": 2750},
        "gzip": {"path": str(child_gzip_path.relative_to(REPO)), "bytes": len(compressed), "sha256": sha256(compressed), "mtime": 0},
        "address_sequence_sha256": address_sequence_hash,
        "changed_envelopes": changed_count,
        "unchanged_envelopes": 2750 - changed_count,
        "state_counts": dict(sorted(state_counts.items())),
        "routing_assignments": 0,
        "immutable_fields": IMMUTABLE_FIELDS,
        "catalog_sha256": catalog_hash,
        "source_count_delta": 0,
        "record_completion_count": 0,
    }
    child_manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    receipt = {
        "packet": "01.5", "batch": batch_id, "version": 1,
        "status": "PASS", "watch": "NONE", "blockers": "NONE",
        "parent_inventory_sha256": expected_parent_hash,
        "child_inventory_sha256": sha256(raw_child),
        "combined_envelopes": 2750,
        "changed_envelopes": changed_count,
        "unchanged_envelopes": 2750 - changed_count,
        "state_counts": dict(sorted(state_counts.items())),
        "routing_assignments": 0,
        "source_count_delta": 0,
        "record_completion_count": 0,
    }
    batch_dir.mkdir(parents=True, exist_ok=True)
    build_json_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    build_md_path.write_text("\n".join([
        f"# Packet 01.5 — Applicability Batch {batch_number:03d} Build v1", "",
        "STATUS: PASS", "WATCH: NONE", "BLOCKERS: NONE", "ROUTING ASSIGNMENTS: 0", "",
        "- Parent envelopes: 2750", "- Child envelopes: 2750",
        f"- Classified in this batch: {changed_count}",
        *[f"- {state}: {count}" for state, count in sorted(state_counts.items())],
        "- Immutable source fields changed: 0",
        "- Addresses added, removed, or reordered: 0",
        "- Destination fields populated: 0",
        "- Source count delta: 0", "- Record completion count: 0",
        f"- Parent SHA-256: `{expected_parent_hash}`",
        f"- Child SHA-256: `{sha256(raw_child)}`",
        f"- Deterministic gzip SHA-256: `{sha256(compressed)}`", "",
        f"Batch {batch_number:03d} remains pending independent verification before acceptance.", "",
    ]), encoding="utf-8")
    print(f"PASS — applied {batch_id} to {changed_count} envelopes")


if __name__ == "__main__":
    main()
