#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = "8cf485bba1f89684edcd3c8429cefdd4c1dc0e83"
FAMILY = "PRIVATE_OR_UNCAPTURED_EVIDENCE"
QUEUE = "audit/applicability/Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl"
INVENTORY = "audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
CURRENT = "audit/routing-inventory/Packet_01.5_Applicability_Inventory_v9_Batch_008.jsonl"
OUTPUT = ROOT / "audit/Packet_01.5_Private_Evidence_Census_v1.json"
TEXT_SUFFIXES = {".md", ".json", ".jsonl", ".txt", ".html", ".js", ".mjs", ".py", ".toml", ".yml", ".yaml", ".css"}
EXCLUDE = (
    ".git/", "node_modules/", "vendor/",
    "audit/Packet_01.5_Private_Evidence_Census_v1.json",
)
STOP = {
    "about", "after", "again", "against", "being", "between", "could", "current", "directly", "does", "every",
    "exists", "from", "have", "into", "largely", "needed", "only", "preserved", "proof", "record", "records",
    "should", "their", "there", "these", "those", "through", "under", "until", "values", "where", "which",
    "without", "would", "private", "uncaptured", "evidence", "implemented", "proven", "claim", "policy",
}


def git(*args: str, binary: bool = False):
    cp = subprocess.run(["git", *args], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cp.stdout if binary else cp.stdout.decode("utf-8", errors="replace")


def show(path: str) -> bytes:
    return git("show", f"{ANCHOR}:{path}", binary=True)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rows(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]


def claim_from_queue(record: dict) -> str:
    marker = "Preserved claim: "
    text = record["missing_proof"]
    if marker not in text:
        raise RuntimeError(f"missing preserved-claim marker for {record['composite_address']}")
    return text.split(marker, 1)[1]


def terms(claim: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", claim.lower())
    result = []
    for word in words:
        if word not in STOP and word not in result:
            result.append(word)
    return result[:10]


def exact(records: list[dict], address: str) -> dict | None:
    found = [record for record in records if record.get("composite_address") == address]
    if len(found) > 1:
        raise RuntimeError(f"duplicate address {address}")
    return found[0] if found else None


def main() -> None:
    git("cat-file", "-e", f"{ANCHOR}^{{commit}}")
    queue_bytes = show(QUEUE)
    inventory_bytes = show(INVENTORY)
    current_bytes = show(CURRENT)
    queue = rows(queue_bytes)
    inventory = rows(inventory_bytes)
    current = rows(current_bytes)
    family = [record for record in queue if record.get("evidence_domain") == FAMILY]
    family.sort(key=lambda record: record["source_record_ordinal"])

    tracked = [path for path in git("ls-tree", "-r", "--name-only", ANCHOR).splitlines() if path]
    public_sources = []
    for path in tracked:
        if path.startswith(EXCLUDE) or Path(path).suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            data = show(path)
            if len(data) > 7_000_000:
                continue
            text = data.decode("utf-8", errors="replace")
        except Exception:
            continue
        public_sources.append((path, sha256(data), text.lower()))

    records = []
    for queue_record in family:
        address = queue_record["composite_address"]
        claim = claim_from_queue(queue_record)
        keywords = terms(claim)
        candidates = []
        for path, digest, text in public_sources:
            matched = [keyword for keyword in keywords if keyword in text]
            if len(matched) >= 2:
                candidates.append({"path": path, "content_sha256": digest, "matched_terms": matched})
        candidates.sort(key=lambda item: (-len(item["matched_terms"]), item["path"]))
        source = exact(inventory, address)
        overlay = exact(current, address)
        records.append({
            "queue_record": queue_record,
            "preserved_claim": claim,
            "inventory_identity": {
                "composite_address": source["composite_address"] if source else None,
                "source_record_ordinal": source["source_record_ordinal"] if source else None,
                "original_identifier": source["original_identifier"] if source else None,
                "envelope_hash": source["envelope_hash"] if source else None,
                "source_block_hash": source.get("source_block_hash") if source else None,
            },
            "current_applicability": None if overlay is None else {
                "state": overlay.get("applicability_state"),
                "batch_id": overlay.get("applicability_batch_id"),
                "decision_hash": overlay.get("applicability_decision_hash"),
                "evidence": overlay.get("applicability_evidence", []),
            },
            "public_search_terms": keywords,
            "public_candidate_sources": candidates[:30],
        })

    result = {
        "packet": "01.5",
        "phase": "private_or_uncaptured_evidence_census",
        "authoritative_anchor": ANCHOR,
        "family": FAMILY,
        "family_count": len(records),
        "family_addresses_in_source_order": [record["queue_record"]["composite_address"] for record in records],
        "source_queue_sha256": sha256(queue_bytes),
        "source_inventory_sha256": sha256(inventory_bytes),
        "source_inventory_count": len(inventory),
        "current_applicability_sha256": sha256(current_bytes),
        "privacy_rule": "Only repository-public metadata, hashes, claims already preserved in the immutable inventory, and privacy-safe receipts may be emitted. No raw private value is read or written.",
        "records": records,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "anchor": ANCHOR,
        "family_count": len(records),
        "addresses": result["family_addresses_in_source_order"],
        "identifiers": [record["queue_record"]["original_identifier"] for record in records],
        "claims": [record["preserved_claim"] for record in records],
        "applicability_states": [None if record["current_applicability"] is None else record["current_applicability"]["state"] for record in records],
        "inventory_count": len(inventory),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
