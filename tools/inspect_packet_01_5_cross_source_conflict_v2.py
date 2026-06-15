#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = "32eb61ff9376a769a23292f4de06c3fdc08236f0"
FAMILY = "CROSS_SOURCE_CONFLICT"
QUEUE = "audit/applicability/Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl"
INVENTORY = "audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
CURRENT_APPLICABILITY = "audit/routing-inventory/Packet_01.5_Applicability_Inventory_v9_Batch_008.jsonl"
TARGET_ADDRESS = "P01.5::B::0043"
TERMS = [
    r"multi[- ]device", r"multiple devices?", r"concurrent[- ]edit", r"concurrent edits?",
    r"edit conflict", r"conflict policy", r"conflict resolution", r"last[- ]write",
    r"merge policy", r"synchroni[sz]", r"device conflict", r"simultaneous edit",
    r"version vectors?", r"\bETags?\b", r"If-Match", r"compare[- ]and[- ]swap",
    r"optimistic concurrency", r"single[- ]device", r"single device", r"never silently overwrite",
    r"divergent edit", r"clock skew", r"conflict detected", r"quarantine uncertain data",
    r"content revision", r"expected version", r"revision mismatch", r"stale write",
]
TEXT_SUFFIXES = {".md", ".json", ".jsonl", ".txt", ".html", ".js", ".mjs", ".py", ".toml", ".yml", ".yaml", ".css"}
EXCLUDED_PREFIXES = (".git/", "node_modules/", "vendor/")


def git(*args: str, binary: bool = False):
    cp = subprocess.run(["git", *args], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cp.stdout if binary else cp.stdout.decode("utf-8", errors="replace")


def show(path: str) -> bytes:
    return git("show", f"{ANCHOR}:{path}", binary=True)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rows(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]


def last_change(path: str) -> dict:
    out = git("log", "-1", "--format=%H%x09%cI%x09%s", ANCHOR, "--", path).strip()
    if not out:
        return {"commit": None, "date": None, "subject": None}
    commit, date, subject = out.split("\t", 2)
    return {"commit": commit, "date": date, "subject": subject}


def classify(path: str, text: str) -> dict:
    p = path.lower()
    t = text.lower()
    if p.startswith("audit/baseline-source/"):
        return {"level": 30, "class": "reconstructed_baseline_source"}
    if "applicability_inventory" in p or "applicability_batch" in p:
        return {"level": 95, "class": "later_verified_applicability_record"}
    if "independent_verification" in p:
        return {"level": 90, "class": "independent_verification_receipt"}
    if "control-spine" in p or "authority-matrix" in p or "status" in p:
        return {"level": 80, "class": "current_control_or_status_record"}
    if "packet_04" in p or "packet_20" in p or "packet 04" in t or "packet 20" in t:
        return {"level": 75, "class": "packet_design_or_governing_record"}
    if p.startswith("audit/packet_01.5_discovery_pass"):
        return {"level": 60, "class": "discovery_risk_record"}
    if p.startswith("audit/"):
        return {"level": 55, "class": "tracked_audit_support"}
    if p.endswith((".js", ".html", ".json", ".toml")):
        return {"level": 50, "class": "runtime_or_configuration_source"}
    return {"level": 40, "class": "tracked_supporting_source"}


def exact_record(path: str, address: str) -> dict | None:
    for record in rows(show(path)):
        if record.get("composite_address") == address:
            return record
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    git("cat-file", "-e", f"{ANCHOR}^{{commit}}")
    queue_bytes = show(QUEUE)
    inventory_bytes = show(INVENTORY)
    queue_rows = rows(queue_bytes)
    inventory_rows = rows(inventory_bytes)
    family = [r for r in queue_rows if r.get("evidence_domain") == FAMILY]
    source_record = next(r for r in inventory_rows if r["composite_address"] == TARGET_ADDRESS)
    current_applicability = exact_record(CURRENT_APPLICABILITY, TARGET_ADDRESS)

    patterns = [re.compile(term, re.I) for term in TERMS]
    tracked = [p for p in git("ls-tree", "-r", "--name-only", ANCHOR).splitlines() if p]
    sources = []
    for path in tracked:
        if path.startswith(EXCLUDED_PREFIXES) or Path(path).suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            data = show(path)
            if len(data) > 7_000_000:
                continue
            text = data.decode("utf-8")
        except Exception:
            continue
        matches = []
        for n, line in enumerate(text.splitlines(), 1):
            hit_terms = [term for term, rx in zip(TERMS, patterns) if rx.search(line)]
            if hit_terms:
                matches.append({"line": n, "text": line.strip()[:1600], "terms": hit_terms})
                if len(matches) >= 60:
                    break
        if matches:
            sources.append({
                "path": path,
                "sha256": sha256(data),
                "git": last_change(path),
                "authority": classify(path, text),
                "matches": matches,
            })

    sources.sort(key=lambda s: (-s["authority"]["level"], s["git"]["date"] or "", s["path"]))
    named_candidates = [
        p for p in tracked
        if any(token in p.lower() for token in (
            "packet_04", "packet-04", "packet_20", "packet-20", "storage", "sync", "conflict",
            "authority-matrix", "applicability_inventory", "applicability_batch_005"
        ))
    ]

    result = {
        "packet": "01.5",
        "phase": "cross_source_conflict_discovery_v2",
        "anchor_commit": ANCHOR,
        "family": FAMILY,
        "family_count": len(family),
        "family_addresses": [r["composite_address"] for r in family],
        "queue_record": family[0] if len(family) == 1 else None,
        "immutable_source_record": source_record,
        "later_current_applicability_record": current_applicability,
        "source_queue_sha256": sha256(queue_bytes),
        "inventory_sha256": sha256(inventory_bytes),
        "inventory_count": len(inventory_rows),
        "current_applicability_path": CURRENT_APPLICABILITY,
        "current_applicability_sha256": sha256(show(CURRENT_APPLICABILITY)),
        "search_terms": TERMS,
        "candidate_source_count": len(sources),
        "candidate_sources": sources,
        "named_candidate_paths": named_candidates,
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "anchor": ANCHOR,
        "family_count": len(family),
        "family_addresses": [r["composite_address"] for r in family],
        "inventory_count": len(inventory_rows),
        "current_applicability_state": None if current_applicability is None else current_applicability.get("applicability_state"),
        "candidate_source_count": len(sources),
        "top_sources": [
            {"path": s["path"], "authority": s["authority"], "date": s["git"]["date"], "sha256": s["sha256"]}
            for s in sources[:30]
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
