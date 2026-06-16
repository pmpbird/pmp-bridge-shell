#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = "15f99fab2fea10f2cb62c1885eb403030060a7b7"
INVENTORY = "audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
OVERLAY = "audit/routing-inventory/Packet_01.5_Applicability_Inventory_v10_Master_Consolidated.jsonl"
OUTPUT = ROOT / "audit/Packet_01.5_Scalable_Pass_002_Discovery_v1.json"
FIRST = 123
LAST = 244


def git(*args: str, binary: bool = False):
    cp = subprocess.run(["git", *args], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cp.stdout if binary else cp.stdout.decode("utf-8", errors="replace")


def show(path: str) -> bytes:
    return git("show", f"{ANCHOR}:{path}", binary=True)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rows(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]


def text_fields(record: dict) -> dict:
    result = {}
    for key, value in record.items():
        if isinstance(value, str) and value.strip():
            result[key] = value
        elif isinstance(value, (int, float, bool)) or value is None:
            result[key] = value
        elif isinstance(value, list) and len(value) <= 12:
            result[key] = value
        elif isinstance(value, dict) and len(value) <= 12:
            result[key] = value
    return result


def main() -> None:
    git("cat-file", "-e", f"{ANCHOR}^{{commit}}")
    inventory_bytes = show(INVENTORY)
    overlay_bytes = show(OVERLAY)
    inventory = rows(inventory_bytes)
    overlay = rows(overlay_bytes)
    assert len(inventory) == len(overlay) == 2750

    selected_inventory = inventory[FIRST - 1:LAST]
    selected_overlay = overlay[FIRST - 1:LAST]
    assert len(selected_inventory) == len(selected_overlay) == 122

    records = []
    for expected_ordinal, (source, current) in enumerate(zip(selected_inventory, selected_overlay), start=FIRST):
        expected_address = f"P01.5::B::{expected_ordinal:04d}"
        assert source.get("source_record_ordinal") == expected_ordinal
        assert source.get("composite_address") == expected_address
        assert current.get("source_record_ordinal") == expected_ordinal
        assert current.get("composite_address") == expected_address
        assert source.get("envelope_hash") == current.get("envelope_hash")
        assert source.get("source_block_hash") == current.get("source_block_hash")
        records.append({
            "composite_address": expected_address,
            "source_record_ordinal": expected_ordinal,
            "original_identifier": source.get("original_identifier"),
            "source_envelope_hash": source.get("envelope_hash"),
            "source_block_hash": source.get("source_block_hash"),
            "inventory_fields": text_fields(source),
            "overlay_fields": text_fields(current),
        })

    result = {
        "packet": "01.5",
        "pass": "002",
        "authoritative_anchor": ANCHOR,
        "inventory": {"path": INVENTORY, "sha256": sha256(inventory_bytes), "records": len(inventory)},
        "starting_overlay": {"path": OVERLAY, "sha256": sha256(overlay_bytes), "records": len(overlay)},
        "window": {
            "first_address": records[0]["composite_address"],
            "last_address": records[-1]["composite_address"],
            "first_ordinal": FIRST,
            "last_ordinal": LAST,
            "records": len(records),
        },
        "records": records,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS_002_DISCOVERY_READY",
        "first_address": records[0]["composite_address"],
        "last_address": records[-1]["composite_address"],
        "records": len(records),
        "inventory_sha256": result["inventory"]["sha256"],
        "overlay_sha256": result["starting_overlay"]["sha256"],
    }, indent=2))


if __name__ == "__main__":
    main()
