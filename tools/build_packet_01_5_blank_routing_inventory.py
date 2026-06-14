#!/usr/bin/env python3
"""Build the lossless, blank Packet 01.5 routing inventory.

This script performs normalization only. It preserves source wording and hashes,
assigns stable composite addresses, and leaves applicability and routing blank.
It does not classify, route, semantically merge, delete, or close records.
"""
from __future__ import annotations

import base64
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
BASE_DIR = AUDIT / "baseline-source"
ROUTING_DIR = AUDIT / "routing-inventory"

BASE_TRANSPORT = BASE_DIR / "pmp-current-permanent-limitation-register-v3-final.transport-manifest.json"
BASE_ADDRESS_MANIFEST = AUDIT / "Packet_01.5_Baseline_Address_Manifest_v1.json"
INVENTORY_JSONL = ROUTING_DIR / "Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
INVENTORY_GZ = ROUTING_DIR / "Packet_01.5_Blank_Routing_Inventory_v1.jsonl.gz"
INVENTORY_MANIFEST = ROUTING_DIR / "Packet_01.5_Blank_Routing_Inventory_v1.manifest.json"
BUILD_RECEIPT_JSON = AUDIT / "Packet_01.5_Blank_Routing_Inventory_Build_v1.json"
BUILD_RECEIPT_MD = AUDIT / "Packet_01.5_Blank_Routing_Inventory_Build_v1.md"

PASS_RE = re.compile(r"Packet_01\.5_Discovery_Pass_(\d+)_.*\.md$")
HEADING_RE = re.compile(r"^###\s+([^\n]+)$", re.MULTILINE)
ID_RE = re.compile(r"^([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3})\s+[—-]\s+(.+)$")
RESULT_RE = re.compile(r"^##\s+Pass\s+\d+\s+result\s*$", re.MULTILINE)
NORMALIZATION_VERSION = "1.0.0"
LEGACY_PASS_1_NO_OVERLAP = {f"REG-{number:03d}" for number in range(1, 11)}

REQUIRED_FIELDS = [
    "composite_address",
    "source_set",
    "source_path",
    "source_file_hash",
    "source_record_ordinal",
    "original_identifier",
    "original_heading",
    "original_body",
    "source_block_hash",
    "harm_text",
    "overlap_text",
    "legacy_exception_codes",
    "applicability_state",
    "applicability_evidence",
    "routing_state",
    "primary_destination",
    "secondary_destinations",
    "cross_cutting_laws",
    "watch_triggers",
    "semantic_cluster_ids",
    "normalization_version",
    "envelope_hash",
]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def envelope_hash(envelope: dict[str, Any]) -> str:
    payload = dict(envelope)
    payload.pop("envelope_hash", None)
    return sha256_bytes(canonical_json_bytes(payload))


def pass_number(path: Path) -> int:
    if path.name == "Packet_01.5_Discovery_Working_Register_v1.md":
        return 1
    match = PASS_RE.fullmatch(path.name)
    if not match:
        fail(f"not a discovery source file: {path}")
    return int(match.group(1))


def provisional_source_files() -> list[Path]:
    files: list[Path] = []
    working = AUDIT / "Packet_01.5_Discovery_Working_Register_v1.md"
    if working.is_file():
        files.append(working)
    files.extend(AUDIT.glob("Packet_01.5_Discovery_Pass_*.md"))
    files.sort(key=lambda path: (pass_number(path), path.name))
    pass_counts = Counter(pass_number(path) for path in files)
    duplicate_passes = {number: count for number, count in pass_counts.items() if count != 1}
    if duplicate_passes:
        fail(f"discovery source pass multiplicity is not one: {duplicate_passes}")
    expected = list(range(1, 70))
    actual = [pass_number(path) for path in files]
    if actual != expected:
        fail(f"discovery pass sequence mismatch: expected 1..69, got {actual}")
    return files


def record_area(text: str) -> str:
    result = RESULT_RE.search(text)
    return text[: result.start()] if result else text


def extract_single_line(label: str, body: str) -> str:
    match = re.search(rf"^{re.escape(label)}\s*(.*)$", body, re.MULTILINE)
    return match.group(1).strip() if match else ""


def reconstruct_baseline() -> tuple[bytes, dict[str, Any]]:
    manifest = json.loads(BASE_TRANSPORT.read_text(encoding="utf-8"))
    parts: list[str] = []
    for part in sorted(manifest["parts"], key=lambda item: item["part"]):
        path = REPO / part["path"]
        raw = path.read_bytes()
        if len(raw) != part["characters"] or sha256_bytes(raw) != part["sha256"]:
            fail(f"baseline transport part failed verification: {part['path']}")
        try:
            text = raw.decode("ascii")
        except UnicodeDecodeError as exc:
            fail(f"baseline transport part is not ASCII: {part['path']}: {exc}")
        if any(character.isspace() for character in text):
            fail(f"baseline transport part contains whitespace: {part['path']}")
        parts.append(text)

    encoded = "".join(parts).encode("ascii")
    if len(encoded) != manifest["base64"]["characters"]:
        fail("baseline combined base64 length mismatch")
    if sha256_bytes(encoded) != manifest["base64"]["sha256"]:
        fail("baseline combined base64 hash mismatch")
    compressed = base64.b64decode(encoded, validate=True)
    if len(compressed) != manifest["gzip"]["bytes"]:
        fail("baseline gzip length mismatch")
    if sha256_bytes(compressed) != manifest["gzip"]["sha256"]:
        fail("baseline gzip hash mismatch")
    source = gzip.decompress(compressed)
    if len(source) != manifest["source_bytes"]:
        fail("baseline source length mismatch")
    if sha256_bytes(source) != manifest["source_sha256"]:
        fail("baseline source hash mismatch")
    return source, manifest


def extract_json_array_object_blocks(source: bytes, key: str) -> list[str]:
    text = source.decode("utf-8")
    match = re.search(rf'"{re.escape(key)}"\s*:\s*\[', text)
    if not match:
        fail(f"JSON array key not found: {key}")
    cursor = match.end()
    blocks: list[str] = []

    while cursor < len(text):
        while cursor < len(text) and (text[cursor].isspace() or text[cursor] == ","):
            cursor += 1
        if cursor >= len(text):
            fail(f"unterminated JSON array: {key}")
        if text[cursor] == "]":
            return blocks
        if text[cursor] != "{":
            fail(f"expected object at character {cursor} in array {key}")

        start = cursor
        depth = 0
        in_string = False
        escaped = False
        while cursor < len(text):
            character = text[cursor]
            if in_string:
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == '"':
                    in_string = False
            else:
                if character == '"':
                    in_string = True
                elif character == "{":
                    depth += 1
                elif character == "}":
                    depth -= 1
                    if depth == 0:
                        cursor += 1
                        blocks.append(text[start:cursor])
                        break
            cursor += 1
        else:
            fail(f"unterminated object in JSON array {key}")
    fail(f"unterminated JSON array {key}")


def blank_fields() -> dict[str, Any]:
    return {
        "applicability_state": "UNCLASSIFIED",
        "applicability_evidence": [],
        "routing_state": "UNROUTED",
        "primary_destination": None,
        "secondary_destinations": [],
        "cross_cutting_laws": [],
        "watch_triggers": [],
        "semantic_cluster_ids": [],
        "normalization_version": NORMALIZATION_VERSION,
    }


def baseline_envelopes() -> list[dict[str, Any]]:
    source, manifest = reconstruct_baseline()
    payload = json.loads(source)
    records = payload.get(manifest["source_record_array"])
    blocks = extract_json_array_object_blocks(source, manifest["source_record_array"])
    if not isinstance(records, list) or len(records) != 122 or len(blocks) != 122:
        fail("baseline count is not exactly 122")

    address_manifest = json.loads(BASE_ADDRESS_MANIFEST.read_text(encoding="utf-8"))
    address_records = address_manifest.get("records")
    if not isinstance(address_records, list) or len(address_records) != 122:
        fail("baseline address manifest count mismatch")

    source_path = "archive://Packet_03.5_v4_FINAL_PASS_COMPLETE.zip!/pmp-current-permanent-limitation-register-v3-final.json"
    source_hash = sha256_bytes(source)
    output: list[dict[str, Any]] = []

    for ordinal, (record, block, address_entry) in enumerate(zip(records, blocks, address_records), 1):
        record_from_block = json.loads(block)
        if record_from_block != record:
            fail(f"baseline exact block parse mismatch at ordinal {ordinal}")
        identifier = record.get("id")
        limitation = record.get("limitation")
        if not isinstance(identifier, str) or not identifier:
            fail(f"baseline identifier missing at ordinal {ordinal}")
        if not isinstance(limitation, str) or not limitation:
            fail(f"baseline limitation missing at ordinal {ordinal}")
        address = f"P01.5::B::{ordinal:04d}"
        if address_entry.get("address") != address or address_entry.get("id") != identifier:
            fail(f"baseline address manifest mismatch at ordinal {ordinal}")
        if address_entry.get("record_sha256") != sha256_bytes(canonical_json_bytes(record)):
            fail(f"baseline canonical record hash mismatch at ordinal {ordinal}")

        envelope: dict[str, Any] = {
            "composite_address": address,
            "source_set": "BASELINE",
            "source_path": source_path,
            "source_pass": None,
            "source_file_hash": source_hash,
            "source_record_ordinal": ordinal,
            "original_identifier": identifier,
            "original_heading": f"{identifier} — {limitation}",
            "original_body": block,
            "source_block_hash": sha256_bytes(block.encode("utf-8")),
            "harm_text": limitation,
            "overlap_text": "",
            "legacy_exception_codes": ["BASELINE-STRUCTURED-JSON"],
            **blank_fields(),
        }
        envelope["envelope_hash"] = envelope_hash(envelope)
        output.append(envelope)
    return output


def provisional_envelopes() -> tuple[list[dict[str, Any]], dict[int, int], list[dict[str, Any]]]:
    output: list[dict[str, Any]] = []
    per_pass: dict[int, int] = {}
    source_manifests: list[dict[str, Any]] = []

    for path in provisional_source_files():
        number = pass_number(path)
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        area = record_area(text)
        matches = list(HEADING_RE.finditer(area))
        per_pass[number] = len(matches)
        relative_path = str(path.relative_to(REPO))
        file_hash = sha256_bytes(raw)
        source_manifests.append({
            "pass": number,
            "path": relative_path,
            "source_file_hash": file_hash,
            "record_count": len(matches),
        })

        for ordinal, heading_match in enumerate(matches, 1):
            heading = heading_match.group(1).strip()
            parsed = ID_RE.fullmatch(heading)
            if not parsed:
                fail(f"malformed provisional heading in {relative_path}: {heading}")
            identifier, _title = parsed.groups()
            record_end = matches[ordinal].start() if ordinal < len(matches) else len(area)
            full_block = area[heading_match.start():record_end]
            body = area[heading_match.end():record_end]
            harm = extract_single_line("HARM:", body)
            overlap = extract_single_line("OVERLAP TO CHECK:", body)
            exceptions: list[str] = []
            if not harm:
                fail(f"missing HARM in {relative_path}: {identifier}")
            if not overlap:
                if number == 1 and identifier in LEGACY_PASS_1_NO_OVERLAP:
                    exceptions.append("LEGACY-P01-NO-OVERLAP")
                else:
                    fail(f"missing OVERLAP TO CHECK in {relative_path}: {identifier}")

            envelope: dict[str, Any] = {
                "composite_address": f"P01.5::P{number:03d}::{identifier}",
                "source_set": "PROVISIONAL",
                "source_path": relative_path,
                "source_pass": number,
                "source_file_hash": file_hash,
                "source_record_ordinal": ordinal,
                "original_identifier": identifier,
                "original_heading": heading,
                "original_body": body,
                "source_block_hash": sha256_bytes(full_block.encode("utf-8")),
                "harm_text": harm,
                "overlap_text": overlap,
                "legacy_exception_codes": exceptions,
                **blank_fields(),
            }
            envelope["envelope_hash"] = envelope_hash(envelope)
            output.append(envelope)

    return output, per_pass, source_manifests


def write_deterministic_gzip(path: Path, data: bytes) -> bytes:
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0, compresslevel=9) as stream:
        stream.write(data)
    compressed = buffer.getvalue()
    path.write_bytes(compressed)
    return compressed


def validate_blank_inventory(envelopes: list[dict[str, Any]]) -> None:
    if len(envelopes) != 2750:
        fail(f"combined envelope count is {len(envelopes)}, expected 2750")
    addresses = [envelope["composite_address"] for envelope in envelopes]
    if len(set(addresses)) != len(addresses):
        duplicates = [value for value, count in Counter(addresses).items() if count > 1]
        fail(f"duplicate composite addresses: {duplicates[:20]}")
    for index, envelope in enumerate(envelopes, 1):
        missing = [field for field in REQUIRED_FIELDS if field not in envelope]
        if missing:
            fail(f"envelope {index} missing fields: {missing}")
        if envelope["envelope_hash"] != envelope_hash(envelope):
            fail(f"envelope hash mismatch: {envelope['composite_address']}")
        if envelope["applicability_state"] != "UNCLASSIFIED":
            fail(f"applicability is not blank: {envelope['composite_address']}")
        if envelope["routing_state"] != "UNROUTED":
            fail(f"routing state is not UNROUTED: {envelope['composite_address']}")
        if envelope["primary_destination"] is not None:
            fail(f"primary destination populated: {envelope['composite_address']}")
        for field in ("secondary_destinations", "cross_cutting_laws", "watch_triggers", "semantic_cluster_ids", "applicability_evidence"):
            if envelope[field] != []:
                fail(f"blank list field populated ({field}): {envelope['composite_address']}")


def main() -> None:
    ROUTING_DIR.mkdir(parents=True, exist_ok=True)
    baseline = baseline_envelopes()
    provisional, per_pass, source_manifests = provisional_envelopes()
    if len(baseline) != 122:
        fail(f"baseline envelope count is {len(baseline)}, expected 122")
    if len(provisional) != 2628:
        fail(f"provisional envelope count is {len(provisional)}, expected 2628")

    envelopes = baseline + provisional
    validate_blank_inventory(envelopes)

    lines = [json.dumps(envelope, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for envelope in envelopes]
    raw_inventory = ("\n".join(lines) + "\n").encode("utf-8")
    INVENTORY_JSONL.write_bytes(raw_inventory)
    compressed = write_deterministic_gzip(INVENTORY_GZ, raw_inventory)

    address_hash = sha256_bytes(("\n".join(envelope["composite_address"] for envelope in envelopes) + "\n").encode("utf-8"))
    manifest: dict[str, Any] = {
        "packet": "01.5",
        "inventory": "blank_routing_inventory",
        "version": 1,
        "build_date": date.today().isoformat(),
        "normalization_version": NORMALIZATION_VERSION,
        "status": "BUILT_PENDING_INDEPENDENT_VERIFICATION",
        "watch": "NONE",
        "blockers": "NONE",
        "counts": {
            "baseline": len(baseline),
            "provisional": len(provisional),
            "combined": len(envelopes),
            "source_files_provisional": len(source_manifests),
        },
        "address_first": envelopes[0]["composite_address"],
        "address_last": envelopes[-1]["composite_address"],
        "address_unique": True,
        "address_sequence_sha256": address_hash,
        "inventory_jsonl": {
            "path": str(INVENTORY_JSONL.relative_to(REPO)),
            "bytes": len(raw_inventory),
            "sha256": sha256_bytes(raw_inventory),
            "lines": len(envelopes),
        },
        "inventory_gzip": {
            "path": str(INVENTORY_GZ.relative_to(REPO)),
            "bytes": len(compressed),
            "sha256": sha256_bytes(compressed),
            "mtime": 0,
        },
        "provisional_source_manifest": source_manifests,
        "per_pass_counts": {str(number): count for number, count in sorted(per_pass.items())},
        "required_fields": REQUIRED_FIELDS,
        "blank_state": {
            "applicability_state": "UNCLASSIFIED",
            "routing_state": "UNROUTED",
            "primary_destination": None,
            "destination_lists_empty": True,
            "semantic_clusters_empty": True,
        },
        "source_preservation": {
            "exact_original_heading": True,
            "exact_original_body": True,
            "source_file_hash": True,
            "source_block_hash": True,
            "envelope_hash": True,
            "deleted_records": 0,
            "closed_records": 0,
        },
    }
    INVENTORY_MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    receipt = {
        "packet": "01.5",
        "build": "blank_routing_inventory",
        "version": 1,
        "status": "PASS",
        "watch": "NONE",
        "blockers": "NONE",
        "baseline_envelopes": len(baseline),
        "provisional_envelopes": len(provisional),
        "combined_envelopes": len(envelopes),
        "unique_addresses": len(set(envelope["composite_address"] for envelope in envelopes)),
        "inventory_sha256": sha256_bytes(raw_inventory),
        "gzip_sha256": sha256_bytes(compressed),
        "routing_state": "UNROUTED",
        "applicability_state": "UNCLASSIFIED",
        "destinations_populated": 0,
        "semantic_merges": 0,
        "deleted_records": 0,
        "closed_records": 0,
    }
    BUILD_RECEIPT_JSON.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    BUILD_RECEIPT_MD.write_text("\n".join([
        "# Packet 01.5 — Blank Routing Inventory Build v1",
        "",
        "STATUS: PASS",
        "WATCH: NONE",
        "BLOCKERS: NONE",
        "ROUTING: NOT STARTED",
        "",
        f"- Baseline envelopes: {len(baseline)}",
        f"- Provisional envelopes: {len(provisional)}",
        f"- Combined envelopes: {len(envelopes)}",
        f"- Unique addresses: {len(set(envelope['composite_address'] for envelope in envelopes))}",
        f"- Inventory SHA-256: `{sha256_bytes(raw_inventory)}`",
        f"- Deterministic gzip SHA-256: `{sha256_bytes(compressed)}`",
        "- Exact original headings preserved: PASS",
        "- Exact original bodies preserved: PASS",
        "- Source-file hashes preserved: PASS",
        "- Source-block hashes preserved: PASS",
        "- Routing state: UNROUTED",
        "- Applicability state: UNCLASSIFIED",
        "- Populated destinations: 0",
        "- Semantic merges: 0",
        "- Deleted records: 0",
        "- Closed records: 0",
        "",
        "END PACKET 01.5 — BLANK ROUTING INVENTORY BUILD v1",
        "",
    ]), encoding="utf-8")
    print("PASS — built 2750-record blank routing inventory")


if __name__ == "__main__":
    main()
