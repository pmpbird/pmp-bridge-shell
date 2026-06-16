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
ORDINAL_KEYS = ("source_record_ordinal", "record_ordinal", "source_ordinal", "ordinal")


def git(*args: str, binary: bool = False):
    cp = subprocess.run(["git", *args], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cp.stdout if binary else cp.stdout.decode("utf-8", errors="replace")


def show(path: str) -> bytes:
    return git("show", f"{ANCHOR}:{path}", binary=True)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rows(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]


def ordinal_field(record: dict) -> tuple[str | None, int | None]:
    for key in ORDINAL_KEYS:
        value = record.get(key)
        if isinstance(value, int):
            return key, value
    return None, None


def text_fields(record: dict) -> dict:
    result = {}
    for key, value in record.items():
        if isinstance(value, str) and value.strip():
            result[key] = value
        elif isinstance(value, (int, float, bool)) or value is None:
            result[key] = value
        elif isinstance(value, list) and len(value) <= 20:
            result[key] = value
        elif isinstance(value, dict) and len(value) <= 20:
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
    detected_inventory_ordinal_keys = set()
    detected_overlay_ordinal_keys = set()
    for expected_ordinal, (source, current) in enumerate(zip(selected_inventory, selected_overlay), start=FIRST):
        expected_address = f"P01.5::B::{expected_ordinal:04d}"
        assert source.get("composite_address") == expected_address, (expected_ordinal, source.get("composite_address"))
        assert current.get("composite_address") == expected_address, (expected_ordinal, current.get("composite_address"))

        source_ordinal_key, source_ordinal = ordinal_field(source)
        overlay_ordinal_key, overlay_ordinal = ordinal_field(current)
        if source_ordinal_key:
            detected_inventory_ordinal_keys.add(source_ordinal_key)
            assert source_ordinal == expected_ordinal
        if overlay_ordinal_key:
            detected_overlay_ordinal_keys.add(overlay_ordinal_key)
            assert overlay_ordinal == expected_ordinal

        source_envelope_hash = source.get("envelope_hash") or source.get("source_envelope_hash")
        overlay_envelope_hash = current.get("envelope_hash") or current.get("source_envelope_hash")
        assert source_envelope_hash == overlay_envelope_hash
        assert source.get("source_block_hash") == current.get("source_block_hash")

        records.append({
            "composite_address": expected_address,
            "source_record_ordinal": expected_ordinal,
            "ordinal_validation": {
                "inventory_line_position": expected_ordinal,
                "inventory_ordinal_key": source_ordinal_key,
                "inventory_ordinal_value": source_ordinal,
                "overlay_ordinal_key": overlay_ordinal_key,
                "overlay_ordinal_value": overlay_ordinal,
                "address_suffix_matches_ordinal": expected_address.endswith(f"{expected_ordinal:04d}"),
            },
            "original_identifier": source.get("original_identifier"),
            "source_envelope_hash": source_envelope_hash,
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
            "inventory_ordinal_keys_detected": sorted(detected_inventory_ordinal_keys),
            "overlay_ordinal_keys_detected": sorted(detected_overlay_ordinal_keys),
            "line_position_is_authoritative_ordinal_when_no_explicit_key": True,
        },
        "record_schema": {
            "inventory_keys": sorted(selected_inventory[0].keys()),
            "overlay_keys": sorted(selected_overlay[0].keys()),
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
        "inventory_ordinal_keys": sorted(detected_inventory_ordinal_keys),
        "overlay_ordinal_keys": sorted(detected_overlay_ordinal_keys),
        "inventory_sha256": result["inventory"]["sha256"],
        "overlay_sha256": result["starting_overlay"]["sha256"],
    }, indent=2))


if __name__ == "__main__":
    main()
