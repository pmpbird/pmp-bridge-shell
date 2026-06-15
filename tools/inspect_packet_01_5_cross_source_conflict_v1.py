#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = "32eb61ff9376a769a23292f4de06c3fdc08236f0"
FAMILY = "CROSS_SOURCE_CONFLICT"
QUEUE = "audit/applicability/Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl"
INVENTORY = "audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
TERMS = [
    r"multi[- ]device", r"multiple devices?", r"concurrent[- ]edit", r"concurrent edits?",
    r"edit conflict", r"conflict policy", r"conflict resolution", r"last[- ]write",
    r"merge policy", r"synchroni[sz]", r"device conflict", r"simultaneous edit",
]
EXCLUDED_PREFIXES = (
    "audit/applicability/Packet_01.5_", ".git/", "node_modules/", "vendor/",
)
TEXT_SUFFIXES = {".md", ".json", ".jsonl", ".txt", ".html", ".js", ".mjs", ".py", ".toml", ".yml", ".yaml", ".css"}


def git(*args: str, binary: bool = False):
    cp = subprocess.run(["git", *args], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cp.stdout if binary else cp.stdout.decode("utf-8", errors="replace")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def show(path: str) -> bytes:
    return git("show", f"{ANCHOR}:{path}", binary=True)


def rows(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]


def last_change(path: str) -> dict:
    out = git("log", "-1", "--format=%H%x09%cI%x09%s", ANCHOR, "--", path).strip()
    if not out:
        return {"commit": None, "date": None, "subject": None}
    commit, date, subject = out.split("\t", 2)
    return {"commit": commit, "date": date, "subject": subject}


def authority(path: str, text: str) -> dict:
    p = path.lower()
    t = text.lower()
    if p.startswith("audit/") and ("independent_verification" in p or "independent verification" in t):
        return {"level": 90, "class": "independently_verified_receipt"}
    if p.startswith("audit/") and ("status" in p or "ledger" in p or "control-spine" in p):
        return {"level": 80, "class": "current_status_or_control_record"}
    if "packet" in p and p.startswith("audit/"):
        return {"level": 70, "class": "packet_or_audit_record"}
    if p.endswith((".js", ".html", ".json", ".toml")) and not p.startswith("audit/"):
        return {"level": 60, "class": "current_runtime_or_configuration_source"}
    if p.startswith("archive/") or "histor" in p or "old" in p or "backup" in p:
        return {"level": 20, "class": "historical_or_backup"}
    return {"level": 40, "class": "tracked_supporting_source"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    git("cat-file", "-e", f"{ANCHOR}^{{commit}}")
    queue_bytes = show(QUEUE)
    inventory_bytes = show(INVENTORY)
    family = [r for r in rows(queue_bytes) if r.get("evidence_domain") == FAMILY]
    inventory = rows(inventory_bytes)
    by_address = {r["composite_address"]: r for r in inventory}

    tracked = [p for p in git("ls-tree", "-r", "--name-only", ANCHOR).splitlines() if p]
    patterns = [re.compile(term, re.I) for term in TERMS]
    sources = []
    for path in tracked:
        if path.startswith(EXCLUDED_PREFIXES) or Path(path).suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            data = show(path)
            if len(data) > 5_000_000:
                continue
            text = data.decode("utf-8")
        except Exception:
            continue
        matches = []
        for n, line in enumerate(text.splitlines(), 1):
            if any(rx.search(line) for rx in patterns):
                matches.append({"line": n, "text": line.strip()[:800]})
                if len(matches) >= 30:
                    break
        if matches:
            sources.append({
                "path": path,
                "sha256": sha256(data),
                "git": last_change(path),
                "authority": authority(path, text),
                "matches": matches,
            })

    sources.sort(key=lambda s: (-s["authority"]["level"], s["git"]["date"] or "", s["path"]))
    result = {
        "packet": "01.5",
        "phase": "cross_source_conflict_discovery",
        "anchor_commit": ANCHOR,
        "family": FAMILY,
        "family_count": len(family),
        "family_records": [
            {
                "queue_record": r,
                "inventory_record": by_address.get(r["composite_address"]),
            }
            for r in family
        ],
        "source_queue_sha256": sha256(queue_bytes),
        "inventory_sha256": sha256(inventory_bytes),
        "inventory_count": len(inventory),
        "search_terms": TERMS,
        "excluded_prefixes": list(EXCLUDED_PREFIXES),
        "candidate_source_count": len(sources),
        "candidate_sources": sources,
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "anchor": ANCHOR,
        "family_count": len(family),
        "addresses": [r["composite_address"] for r in family],
        "inventory_count": len(inventory),
        "candidate_source_count": len(sources),
        "top_sources": [{"path": s["path"], "authority": s["authority"], "date": s["git"]["date"], "sha256": s["sha256"]} for s in sources[:20]],
    }, indent=2))


if __name__ == "__main__":
    main()
