#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = "9a91fb5b848f52a7422644cfe3556e7c93ed0314"
QUEUE = "audit/applicability/Packet_01.5_Scalable_Pass_002_Evidence_Queue_v1.jsonl"
WINDOW = "audit/applicability/Packet_01.5_Scalable_Pass_002_Window_v1.json"
OVERLAY = "audit/routing-inventory/Packet_01.5_Applicability_Inventory_v11_Pass_002.jsonl"
INVENTORY = "audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
OUTPUT = ROOT / "audit/Packet_01.5_Pass_002_Current_Runtime_Discovery_v1.json"

TEXT_EXTENSIONS = {
    ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".json", ".html", ".css", ".scss",
    ".py", ".sh", ".yml", ".yaml", ".toml", ".ini", ".conf", ".md", ".txt", ".xml",
}
EXCLUDED_PREFIXES = ("audit/", ".git/")
EXCLUDED_NAMES = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock"}
STOPWORDS = {
    "that", "this", "with", "from", "into", "when", "where", "which", "while", "have", "has",
    "does", "not", "only", "must", "should", "would", "could", "their", "there", "being", "been",
    "record", "claim", "current", "runtime", "source", "system", "packet", "problem", "issue", "risk",
    "without", "because", "through", "using", "used", "within", "across", "after", "before", "still",
}


def git(*args: str, binary: bool = False) -> bytes | str:
    cp = subprocess.run(["git", *args], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cp.stdout if binary else cp.stdout.decode("utf-8", errors="replace")


def show(path: str) -> bytes:
    return git("show", f"{ANCHOR}:{path}", binary=True)  # type: ignore[return-value]


def jsonl(data: bytes) -> list[dict[str, Any]]:
    return [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tracked_source_files() -> list[str]:
    paths = git("ls-tree", "-r", "--name-only", ANCHOR).splitlines()  # type: ignore[union-attr]
    result = []
    for path in paths:
        if path.startswith(EXCLUDED_PREFIXES) or Path(path).name in EXCLUDED_NAMES:
            continue
        if path.startswith("tools/inspect_packet_01_5_pass_002_current_runtime_v1.py"):
            continue
        if Path(path).suffix.lower() in TEXT_EXTENSIONS or Path(path).name in {"Dockerfile", "Procfile"}:
            result.append(path)
    return result


def tokens(claim: str, identifier: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_.:/-]{3,}", claim)
    ranked: list[str] = []
    for word in [identifier, *words]:
        normalized = word.strip(".,:;()[]{}\"'")
        if len(normalized) < 4 or normalized.lower() in STOPWORDS:
            continue
        if normalized not in ranked:
            ranked.append(normalized)
    return ranked[:18]


def source_hits(path: str, content: str, terms: list[str]) -> list[dict[str, Any]]:
    hits = []
    lines = content.splitlines()
    for line_number, line in enumerate(lines, start=1):
        matched = [term for term in terms if term.lower() in line.lower()]
        if matched:
            excerpt = line.strip()
            if len(excerpt) > 500:
                excerpt = excerpt[:500]
            hits.append({"line": line_number, "terms": matched, "excerpt": excerpt})
            if len(hits) >= 20:
                break
    return hits


def main() -> None:
    git("cat-file", "-e", f"{ANCHOR}^{{commit}}")
    queue_bytes = show(QUEUE)
    queue = jsonl(queue_bytes)
    selected = [row for row in queue if row.get("evidence_domain") == "CURRENT_RUNTIME_SOURCE"]
    assert len(selected) == 26
    assert len({row["composite_address"] for row in selected}) == 26

    inventory_bytes = show(INVENTORY)
    overlay_bytes = show(OVERLAY)
    window_bytes = show(WINDOW)
    assert len(jsonl(inventory_bytes)) == len(jsonl(overlay_bytes)) == 2750

    files = tracked_source_files()
    file_contents: dict[str, tuple[bytes, str]] = {}
    for path in files:
        raw = show(path)
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        file_contents[path] = (raw, text)

    records = []
    for row in selected:
        address = row["composite_address"]
        claim = row["preserved_claim"]
        identifier = row["original_identifier"]
        search_terms = tokens(claim, identifier)
        evidence_files = []
        for path, (raw, text) in file_contents.items():
            hits = source_hits(path, text, search_terms)
            if hits:
                evidence_files.append({
                    "path": path,
                    "sha256": sha256(raw),
                    "hits": hits,
                })
        evidence_files.sort(key=lambda item: (-sum(len(hit["terms"]) for hit in item["hits"]), item["path"]))
        records.append({
            "composite_address": address,
            "inventory_position": row["inventory_position"],
            "source_record_ordinal": row["source_record_ordinal"],
            "original_identifier": identifier,
            "preserved_claim": claim,
            "source_envelope_hash": row["source_envelope_hash"],
            "source_block_hash": row["source_block_hash"],
            "prior_applicability_state": row.get("prior_applicability_state"),
            "prior_applicability_decision_hash": row.get("prior_applicability_decision_hash"),
            "search_terms": search_terms,
            "candidate_evidence_files": evidence_files[:25],
            "candidate_evidence_file_count": len(evidence_files),
        })

    result = {
        "packet": "01.5",
        "pass": "002",
        "family": "CURRENT_RUNTIME_SOURCE",
        "authoritative_anchor": ANCHOR,
        "family_records": len(records),
        "queue_path": QUEUE,
        "queue_sha256": sha256(queue_bytes),
        "window_path": WINDOW,
        "window_sha256": sha256(window_bytes),
        "inventory_path": INVENTORY,
        "inventory_sha256": sha256(inventory_bytes),
        "inventory_records": 2750,
        "overlay_path": OVERLAY,
        "overlay_sha256": sha256(overlay_bytes),
        "overlay_records": 2750,
        "inspected_repository_files": len(file_contents),
        "records": records,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS_002_CURRENT_RUNTIME_DISCOVERY_READY",
        "family_records": len(records),
        "inspected_repository_files": len(file_contents),
        "records_with_candidate_files": sum(bool(record["candidate_evidence_files"]) for record in records),
        "inventory_sha256": result["inventory_sha256"],
        "overlay_sha256": result["overlay_sha256"],
    }, indent=2))


if __name__ == "__main__":
    main()
