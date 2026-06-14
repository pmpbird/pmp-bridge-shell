#!/usr/bin/env python3
"""Verify and reconstruct the exact Packet 01.5 122-record baseline source.

This tool is mechanical. It does not classify, route, merge, rewrite, delete, or
close any limitation record. It generates the address manifest directly from the
verified source so no hand-copied record hash can control the result.
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BASE = REPO / "audit" / "baseline-source"
MANIFEST = BASE / "pmp-current-permanent-limitation-register-v3-final.transport-manifest.json"
ADDRESS_MANIFEST = REPO / "audit" / "Packet_01.5_Baseline_Address_Manifest_v2.json"
OUT_DIR = BASE / "reconstructed"
OUT_SOURCE = OUT_DIR / "pmp-current-permanent-limitation-register-v3-final.json"
RECEIPT_JSON = REPO / "audit" / "Packet_01.5_Baseline_Source_Verification_v1.json"
RECEIPT_MD = REPO / "audit" / "Packet_01.5_Baseline_Source_Verification_v1.md"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_record_bytes(record: object) -> bytes:
    return json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    encoded_parts: list[str] = []
    verified_parts: list[dict] = []

    for expected in manifest["parts"]:
        path = REPO / expected["path"]
        if not path.is_file():
            fail(f"missing transport part: {expected['path']}")
        raw_part = path.read_bytes()
        if len(raw_part) != expected["characters"]:
            fail(f"part length mismatch: {expected['path']}")
        if sha256(raw_part) != expected["sha256"]:
            fail(f"part SHA-256 mismatch: {expected['path']}")
        try:
            text = raw_part.decode("ascii")
        except UnicodeDecodeError as exc:
            fail(f"part is not ASCII base64: {expected['path']}: {exc}")
        if any(ch.isspace() for ch in text):
            fail(f"transport part contains whitespace: {expected['path']}")
        encoded_parts.append(text)
        verified_parts.append({
            "part": expected["part"],
            "path": expected["path"],
            "characters": len(text),
            "sha256": sha256(raw_part),
        })

    encoded = "".join(encoded_parts).encode("ascii")
    if len(encoded) != manifest["base64"]["characters"]:
        fail("combined base64 character count mismatch")
    if sha256(encoded) != manifest["base64"]["sha256"]:
        fail("combined base64 SHA-256 mismatch")

    try:
        compressed = base64.b64decode(encoded, validate=True)
    except Exception as exc:
        fail(f"strict base64 decode failed: {exc}")
    if len(compressed) != manifest["gzip"]["bytes"]:
        fail("gzip byte count mismatch")
    if sha256(compressed) != manifest["gzip"]["sha256"]:
        fail("gzip SHA-256 mismatch")

    try:
        source = gzip.decompress(compressed)
    except Exception as exc:
        fail(f"gzip decompression failed: {exc}")
    if len(source) != manifest["source_bytes"]:
        fail("raw source byte count mismatch")
    if sha256(source) != manifest["source_sha256"]:
        fail("raw source SHA-256 mismatch")

    try:
        payload = json.loads(source)
    except json.JSONDecodeError as exc:
        fail(f"reconstructed source is not valid JSON: {exc}")
    records = payload.get(manifest["source_record_array"])
    if not isinstance(records, list):
        fail("baseline record array is missing")
    if len(records) != manifest["source_record_count"]:
        fail("baseline record count mismatch")

    identifiers = [record.get("id") for record in records]
    if any(not isinstance(value, str) or not value for value in identifiers):
        fail("one or more baseline identifiers are missing")
    if len(set(identifiers)) != len(identifiers):
        fail("baseline identifiers are not unique")

    addresses = [f"P01.5::B::{index:04d}" for index in range(1, len(records) + 1)]
    if len(set(addresses)) != len(addresses):
        fail("baseline addresses are not unique")
    if addresses[0] != "P01.5::B::0001" or addresses[-1] != "P01.5::B::0122":
        fail("baseline address bounds are incorrect")

    address_manifest = {
        "packet": "01.5",
        "version": 2,
        "supersedes": "audit/Packet_01.5_Baseline_Address_Manifest_v1.json",
        "generation": "mechanically_generated_from_verified_source",
        "source_filename": manifest["source_filename"],
        "source_sha256": sha256(source),
        "source_bytes": len(source),
        "record_count": len(records),
        "address_first": addresses[0],
        "address_last": addresses[-1],
        "address_unique": True,
        "original_identifier_unique": True,
        "routing_state": "UNROUTED",
        "destination_fields_blank": True,
        "records": [
            {
                "address": address,
                "ordinal": index,
                "id": record["id"],
                "record_sha256": sha256(canonical_record_bytes(record)),
            }
            for index, (address, record) in enumerate(zip(addresses, records), 1)
        ],
    }
    ADDRESS_MANIFEST.write_text(json.dumps(address_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    generated = json.loads(ADDRESS_MANIFEST.read_text(encoding="utf-8"))
    generated_records = generated.get("records")
    if not isinstance(generated_records, list) or len(generated_records) != len(records):
        fail("generated address manifest count mismatch")
    for index, (record, entry, address) in enumerate(zip(records, generated_records, addresses), 1):
        if entry.get("address") != address:
            fail(f"generated address mismatch at ordinal {index}")
        if entry.get("ordinal") != index:
            fail(f"generated ordinal mismatch at ordinal {index}")
        if entry.get("id") != record.get("id"):
            fail(f"generated identifier mismatch at ordinal {index}")
        if entry.get("record_sha256") != sha256(canonical_record_bytes(record)):
            fail(f"generated canonical record hash mismatch at ordinal {index}")
    if generated.get("routing_state") != "UNROUTED":
        fail("generated address manifest routing state is not blank/unrouted")
    if generated.get("destination_fields_blank") is not True:
        fail("generated address manifest destination fields are not certified blank")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_SOURCE.write_bytes(source)
    if OUT_SOURCE.read_bytes() != source:
        fail("reverse reconstruction write/read mismatch")

    receipt = {
        "packet": "01.5",
        "verification": "baseline_source",
        "version": 1,
        "status": "PASS",
        "source_filename": manifest["source_filename"],
        "source_bytes": len(source),
        "source_sha256": sha256(source),
        "gzip_bytes": len(compressed),
        "gzip_sha256": sha256(compressed),
        "base64_characters": len(encoded),
        "base64_sha256": sha256(encoded),
        "transport_parts": verified_parts,
        "baseline_record_count": len(records),
        "baseline_identifier_unique": True,
        "address_manifest": str(ADDRESS_MANIFEST.relative_to(REPO)),
        "address_manifest_sha256": sha256(ADDRESS_MANIFEST.read_bytes()),
        "address_first": addresses[0],
        "address_last": addresses[-1],
        "address_count": len(addresses),
        "address_unique": True,
        "reverse_reconstruction": "PASS",
        "routing_state": "UNROUTED",
        "destination_fields_blank": True,
        "watch": "NONE",
        "blockers": "NONE",
    }
    RECEIPT_JSON.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    RECEIPT_MD.write_text("\n".join([
        "# Packet 01.5 — Baseline Source Verification v1",
        "",
        "STATUS: PASS",
        "WATCH: NONE",
        "BLOCKERS: NONE",
        "ROUTING: NOT STARTED",
        "",
        f"- Exact raw bytes: {len(source)}",
        f"- Exact raw SHA-256: `{sha256(source)}`",
        f"- Baseline records: {len(records)}",
        f"- Unique original identifiers: {len(set(identifiers))}",
        f"- Stable addresses: `{addresses[0]}` through `{addresses[-1]}`",
        f"- Generated address manifest: `{ADDRESS_MANIFEST.relative_to(REPO)}`",
        "- Address uniqueness: PASS",
        "- Reverse reconstruction: PASS",
        "- Routing state: UNROUTED",
        "- Destination fields: BLANK",
        "",
        "END PACKET 01.5 — BASELINE SOURCE VERIFICATION v1",
        "",
    ]), encoding="utf-8")
    print("PASS — exact Packet 01.5 baseline source verified")


if __name__ == "__main__":
    main()
