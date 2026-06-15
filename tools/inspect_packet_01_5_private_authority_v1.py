#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = "8cf485bba1f89684edcd3c8429cefdd4c1dc0e83"
TARGET = "P01.5::B::0056"
PLAN = "audit/routing-batches/Packet_01.5_Applicability_Batch_006_Plan_v1.json"
CURRENT = "audit/routing-inventory/Packet_01.5_Applicability_Inventory_v9_Batch_008.jsonl"
OUTPUT = ROOT / "audit/Packet_01.5_Private_Evidence_Authority_Locator_v1.json"
PHRASES = [
    "record-class-specific ACTIVE pointers",
    "evidence precedence",
    "Apple Notes",
    "File Library",
    "status ledger",
]
TEXT_SUFFIXES = {".md", ".json", ".jsonl", ".txt", ".html", ".js", ".mjs", ".py", ".toml", ".yml", ".yaml"}


def git(*args: str, binary: bool = False):
    cp = subprocess.run(["git", *args], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cp.stdout if binary else cp.stdout.decode("utf-8", errors="replace")


def show(path: str) -> bytes:
    return git("show", f"{ANCHOR}:{path}", binary=True)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def jsonl(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]


def metadata(path: str) -> dict:
    data = show(path)
    log = git("log", "-1", "--format=%H%x09%cI%x09%s", ANCHOR, "--", path).strip().split("\t", 2)
    return {
        "path": path,
        "content_sha256": sha256(data),
        "git_blob_sha": git("rev-parse", f"{ANCHOR}:{path}").strip(),
        "last_change_commit": log[0] if len(log) == 3 else None,
        "last_change_date": log[1] if len(log) == 3 else None,
        "last_change_subject": log[2] if len(log) == 3 else None,
    }


def redact_record(record: dict) -> dict:
    return {
        "composite_address": record.get("composite_address"),
        "applicability_state": record.get("applicability_state"),
        "applicability_batch_id": record.get("applicability_batch_id"),
        "applicability_decision_hash": record.get("applicability_decision_hash"),
        "reasoning_summary": record.get("applicability_reasoning_summary"),
        "evidence_references": [
            {
                "evidence_id": item.get("evidence_id"),
                "catalog_evidence_id": item.get("catalog_evidence_id"),
                "source_reference": item.get("source_reference"),
                "source_hash_or_stable_reference": item.get("source_hash_or_stable_reference"),
            }
            for item in record.get("applicability_evidence", [])
        ],
    }


def main() -> None:
    git("cat-file", "-e", f"{ANCHOR}^{{commit}}")
    plan = json.loads(show(PLAN))
    current = jsonl(show(CURRENT))
    target = next(record for record in current if record.get("composite_address") == TARGET)

    tracked = [path for path in git("ls-tree", "-r", "--name-only", ANCHOR).splitlines() if path]
    matches = []
    for path in tracked:
        if Path(path).suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            data = show(path)
            if len(data) > 7_000_000:
                continue
            lines = data.decode("utf-8", errors="replace").splitlines()
        except Exception:
            continue
        phrase_hits = []
        for phrase in PHRASES:
            hit_lines = [index + 1 for index, line in enumerate(lines) if phrase.lower() in line.lower()]
            if hit_lines:
                phrase_hits.append({"phrase": phrase, "line_numbers": hit_lines[:20]})
        if phrase_hits:
            matches.append({**metadata(path), "phrase_hits": phrase_hits})

    result = {
        "packet": "01.5",
        "authoritative_anchor": ANCHOR,
        "target_address": TARGET,
        "privacy_boundary": "Metadata, hashes, public audit reasoning, and line numbers only. No private values or matched line contents are emitted.",
        "batch_plan_metadata": metadata(PLAN),
        "batch_plan_public_fields": {
            "packet": plan.get("packet"),
            "batch_id": plan.get("batch_id"),
            "status": plan.get("status"),
            "records": [
                {
                    "composite_address": item.get("composite_address"),
                    "applicability_state": item.get("applicability_state"),
                    "applicability_reasoning_summary": item.get("applicability_reasoning_summary"),
                    "source_references": [e.get("source_reference") for e in item.get("applicability_evidence", [])],
                }
                for item in plan.get("records", [])
                if item.get("composite_address") == TARGET
            ],
        },
        "current_overlay_metadata": metadata(CURRENT),
        "current_overlay": redact_record(target),
        "authority_candidates": sorted(matches, key=lambda item: item["path"]),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "target": TARGET,
        "state": result["current_overlay"]["applicability_state"],
        "batch": result["current_overlay"]["applicability_batch_id"],
        "decision_hash": result["current_overlay"]["applicability_decision_hash"],
        "candidate_paths": [item["path"] for item in result["authority_candidates"]],
    }, indent=2))


if __name__ == "__main__":
    main()
