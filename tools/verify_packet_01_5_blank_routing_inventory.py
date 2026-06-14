#!/usr/bin/env python3
"""Independent verifier for the Packet 01.5 blank routing inventory.

The verifier independently reads the protected sources and the generated inventory.
It performs no classification, routing, merge, deletion, or closure.
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
import re
from collections import Counter, defaultdict
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
VERIFY_JSON = AUDIT / "Packet_01.5_Blank_Routing_Inventory_Independent_Verification_v1.json"
VERIFY_MD = AUDIT / "Packet_01.5_Blank_Routing_Inventory_Independent_Verification_v1.md"
STATUS_MD = AUDIT / "Packet_01.5_Routing_Inventory_Status_v74.md"

PASS_RE = re.compile(r"Packet_01\.5_Discovery_Pass_(\d+)_.*\.md$")
HEADING_RE = re.compile(r"^###\s+([^\n]+)$", re.MULTILINE)
ID_RE = re.compile(r"^([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3})\s+[—-]\s+(.+)$")
RESULT_RE = re.compile(r"^##\s+Pass\s+\d+\s+result\s*$", re.MULTILINE)
LEGACY_PASS_1_NO_OVERLAP = {f"REG-{number:03d}" for number in range(1, 11)}

REQUIRED_FIELDS = {
    "composite_address", "source_set", "source_path", "source_file_hash",
    "source_record_ordinal", "original_identifier", "original_heading",
    "original_body", "source_block_hash", "harm_text", "overlap_text",
    "legacy_exception_codes", "applicability_state", "applicability_evidence",
    "routing_state", "primary_destination", "secondary_destinations",
    "cross_cutting_laws", "watch_triggers", "semantic_cluster_ids",
    "normalization_version", "envelope_hash",
}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def calculated_envelope_hash(envelope: dict[str, Any]) -> str:
    value = dict(envelope)
    value.pop("envelope_hash", None)
    return sha256(canonical(value))


def source_pass(path: Path) -> int:
    if path.name == "Packet_01.5_Discovery_Working_Register_v1.md":
        return 1
    match = PASS_RE.fullmatch(path.name)
    if not match:
        fail(f"unexpected discovery source path: {path}")
    return int(match.group(1))


def discovery_files() -> list[Path]:
    files = [AUDIT / "Packet_01.5_Discovery_Working_Register_v1.md"]
    files.extend(AUDIT.glob("Packet_01.5_Discovery_Pass_*.md"))
    if not files[0].is_file():
        fail("working register is missing")
    files.sort(key=lambda path: (source_pass(path), path.name))
    pass_numbers = [source_pass(path) for path in files]
    if pass_numbers != list(range(1, 70)):
        fail(f"expected one source for every pass 1..69, got {pass_numbers}")
    return files


def record_area(text: str) -> str:
    result = RESULT_RE.search(text)
    return text[:result.start()] if result else text


def reconstruct_baseline() -> tuple[bytes, dict[str, Any]]:
    transport = json.loads(BASE_TRANSPORT.read_text(encoding="utf-8"))
    pieces: list[bytes] = []
    for part in sorted(transport["parts"], key=lambda item: item["part"]):
        raw = (REPO / part["path"]).read_bytes()
        if len(raw) != part["characters"]:
            fail(f"baseline part length mismatch: {part['path']}")
        if sha256(raw) != part["sha256"]:
            fail(f"baseline part hash mismatch: {part['path']}")
        pieces.append(raw)
    encoded = b"".join(pieces)
    if len(encoded) != transport["base64"]["characters"] or sha256(encoded) != transport["base64"]["sha256"]:
        fail("baseline combined transport mismatch")
    compressed = base64.b64decode(encoded, validate=True)
    if len(compressed) != transport["gzip"]["bytes"] or sha256(compressed) != transport["gzip"]["sha256"]:
        fail("baseline compressed source mismatch")
    source = gzip.decompress(compressed)
    if len(source) != transport["source_bytes"] or sha256(source) != transport["source_sha256"]:
        fail("baseline raw source mismatch")
    return source, transport


def exact_object_blocks(source: bytes, key: str) -> list[str]:
    text = source.decode("utf-8")
    match = re.search(rf'"{re.escape(key)}"\s*:\s*\[', text)
    if not match:
        fail(f"baseline array not found: {key}")
    index = match.end()
    blocks: list[str] = []
    while True:
        while index < len(text) and (text[index].isspace() or text[index] == ","):
            index += 1
        if index >= len(text):
            fail("unterminated baseline array")
        if text[index] == "]":
            return blocks
        if text[index] != "{":
            fail(f"unexpected baseline array token at {index}")
        start = index
        depth = 0
        in_string = False
        escaped = False
        while index < len(text):
            character = text[index]
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
                        index += 1
                        blocks.append(text[start:index])
                        break
            index += 1
        else:
            fail("unterminated baseline object")


def load_inventory() -> tuple[list[dict[str, Any]], bytes, dict[str, Any]]:
    raw = INVENTORY_JSONL.read_bytes()
    manifest = json.loads(INVENTORY_MANIFEST.read_text(encoding="utf-8"))
    if len(raw) != manifest["inventory_jsonl"]["bytes"] or sha256(raw) != manifest["inventory_jsonl"]["sha256"]:
        fail("inventory JSONL does not match manifest")
    compressed = INVENTORY_GZ.read_bytes()
    if len(compressed) != manifest["inventory_gzip"]["bytes"] or sha256(compressed) != manifest["inventory_gzip"]["sha256"]:
        fail("inventory gzip does not match manifest")
    if gzip.decompress(compressed) != raw:
        fail("inventory gzip reverse reconstruction failed")
    lines = raw.splitlines()
    if len(lines) != 2750:
        fail(f"inventory line count is {len(lines)}, expected 2750")
    envelopes: list[dict[str, Any]] = []
    for number, line in enumerate(lines, 1):
        try:
            envelope = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid JSONL at line {number}: {exc}")
        if not isinstance(envelope, dict):
            fail(f"inventory line {number} is not an object")
        envelopes.append(envelope)
    return envelopes, raw, manifest


def verify_blank_fields(envelope: dict[str, Any]) -> None:
    address = envelope.get("composite_address", "<missing>")
    if REQUIRED_FIELDS - set(envelope):
        fail(f"missing required fields at {address}: {sorted(REQUIRED_FIELDS - set(envelope))}")
    if envelope["envelope_hash"] != calculated_envelope_hash(envelope):
        fail(f"envelope hash mismatch at {address}")
    if envelope["applicability_state"] != "UNCLASSIFIED" or envelope["routing_state"] != "UNROUTED":
        fail(f"classification or routing is not blank at {address}")
    if envelope["primary_destination"] is not None:
        fail(f"primary destination populated at {address}")
    for field in ("applicability_evidence", "secondary_destinations", "cross_cutting_laws", "watch_triggers", "semantic_cluster_ids"):
        if envelope[field] != []:
            fail(f"field {field} is populated at {address}")


def expected_provisional_blocks() -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    expected: dict[str, dict[str, Any]] = {}
    source_summary: list[dict[str, Any]] = []
    for path in discovery_files():
        number = source_pass(path)
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        area = record_area(text)
        matches = list(HEADING_RE.finditer(area))
        relative = str(path.relative_to(REPO))
        file_hash = sha256(raw)
        source_summary.append({"pass": number, "path": relative, "records": len(matches), "sha256": file_hash})
        for ordinal, heading_match in enumerate(matches, 1):
            heading = heading_match.group(1).strip()
            parsed = ID_RE.fullmatch(heading)
            if not parsed:
                fail(f"source heading is malformed in {relative}: {heading}")
            identifier = parsed.group(1)
            end = matches[ordinal].start() if ordinal < len(matches) else len(area)
            body = area[heading_match.end():end]
            full_block = area[heading_match.start():end]
            address = f"P01.5::P{number:03d}::{identifier}"
            if address in expected:
                fail(f"duplicate expected provisional address: {address}")
            harm_match = re.search(r"^HARM:\s*(.*)$", body, re.MULTILINE)
            overlap_match = re.search(r"^OVERLAP TO CHECK:\s*(.*)$", body, re.MULTILINE)
            exceptions: list[str] = []
            if not harm_match:
                fail(f"source HARM missing at {address}")
            if not overlap_match:
                if number == 1 and identifier in LEGACY_PASS_1_NO_OVERLAP:
                    exceptions.append("LEGACY-P01-NO-OVERLAP")
                else:
                    fail(f"source OVERLAP TO CHECK missing at {address}")
            expected[address] = {
                "source_set": "PROVISIONAL",
                "source_path": relative,
                "source_pass": number,
                "source_file_hash": file_hash,
                "source_record_ordinal": ordinal,
                "original_identifier": identifier,
                "original_heading": heading,
                "original_body": body,
                "source_block_hash": sha256(full_block.encode("utf-8")),
                "harm_text": harm_match.group(1).strip(),
                "overlap_text": overlap_match.group(1).strip() if overlap_match else "",
                "legacy_exception_codes": exceptions,
            }
    if len(expected) != 2628:
        fail(f"expected provisional source count is {len(expected)}, expected 2628")
    return expected, source_summary


def verify_sources(envelopes: list[dict[str, Any]]) -> dict[str, Any]:
    baseline_source, transport = reconstruct_baseline()
    baseline_payload = json.loads(baseline_source)
    baseline_records = baseline_payload[transport["source_record_array"]]
    baseline_blocks = exact_object_blocks(baseline_source, transport["source_record_array"])
    baseline_addresses = json.loads(BASE_ADDRESS_MANIFEST.read_text(encoding="utf-8"))["records"]
    if len(baseline_records) != 122 or len(baseline_blocks) != 122 or len(baseline_addresses) != 122:
        fail("baseline source/address count mismatch")

    by_address = {envelope["composite_address"]: envelope for envelope in envelopes}
    if len(by_address) != len(envelopes):
        duplicates = [address for address, count in Counter(envelope["composite_address"] for envelope in envelopes).items() if count > 1]
        fail(f"duplicate inventory addresses: {duplicates[:20]}")

    baseline_source_hash = sha256(baseline_source)
    for ordinal, (record, block, address_entry) in enumerate(zip(baseline_records, baseline_blocks, baseline_addresses), 1):
        address = f"P01.5::B::{ordinal:04d}"
        envelope = by_address.get(address)
        if envelope is None:
            fail(f"baseline envelope missing: {address}")
        identifier = record["id"]
        expected = {
            "source_set": "BASELINE",
            "source_path": "archive://Packet_03.5_v4_FINAL_PASS_COMPLETE.zip!/pmp-current-permanent-limitation-register-v3-final.json",
            "source_pass": None,
            "source_file_hash": baseline_source_hash,
            "source_record_ordinal": ordinal,
            "original_identifier": identifier,
            "original_heading": f"{identifier} — {record['limitation']}",
            "original_body": block,
            "source_block_hash": sha256(block.encode("utf-8")),
            "harm_text": record["limitation"],
            "overlap_text": "",
            "legacy_exception_codes": ["BASELINE-STRUCTURED-JSON"],
        }
        if address_entry["address"] != address or address_entry["id"] != identifier:
            fail(f"baseline address manifest mismatch at {address}")
        for field, value in expected.items():
            if envelope.get(field) != value:
                fail(f"baseline field mismatch ({field}) at {address}")

    provisional_expected, source_summary = expected_provisional_blocks()
    for address, expected in provisional_expected.items():
        envelope = by_address.get(address)
        if envelope is None:
            fail(f"provisional envelope missing: {address}")
        for field, value in expected.items():
            if envelope.get(field) != value:
                fail(f"provisional field mismatch ({field}) at {address}")

    baseline_inventory = [envelope for envelope in envelopes if envelope["source_set"] == "BASELINE"]
    provisional_inventory = [envelope for envelope in envelopes if envelope["source_set"] == "PROVISIONAL"]
    if len(baseline_inventory) != 122 or len(provisional_inventory) != 2628:
        fail("inventory source-set counts are incorrect")
    if set(by_address) != {f"P01.5::B::{ordinal:04d}" for ordinal in range(1, 123)} | set(provisional_expected):
        fail("inventory contains missing or unexpected addresses")

    return {
        "baseline_source_sha256": baseline_source_hash,
        "baseline_records": len(baseline_inventory),
        "provisional_records": len(provisional_inventory),
        "combined_records": len(envelopes),
        "provisional_source_files": len(source_summary),
        "provisional_source_summary": source_summary,
    }


def main() -> None:
    envelopes, raw_inventory, manifest = load_inventory()
    for envelope in envelopes:
        verify_blank_fields(envelope)
    source_result = verify_sources(envelopes)

    addresses = [envelope["composite_address"] for envelope in envelopes]
    address_sequence_hash = sha256(("\n".join(addresses) + "\n").encode("utf-8"))
    if manifest.get("address_sequence_sha256") != address_sequence_hash:
        fail("address-sequence hash mismatch")
    if manifest["counts"] != {"baseline": 122, "provisional": 2628, "combined": 2750, "source_files_provisional": 69}:
        fail("inventory manifest count block mismatch")

    result = {
        "packet": "01.5",
        "verification": "blank_routing_inventory_independent",
        "version": 1,
        "verification_date": date.today().isoformat(),
        "status": "PASS",
        "watch": "NONE",
        "blockers": "NONE",
        "inventory_sha256": sha256(raw_inventory),
        "address_sequence_sha256": address_sequence_hash,
        "baseline_records": source_result["baseline_records"],
        "provisional_records": source_result["provisional_records"],
        "combined_records": source_result["combined_records"],
        "provisional_source_files": source_result["provisional_source_files"],
        "unique_addresses": len(set(addresses)),
        "source_to_envelope_bijection": "PASS",
        "exact_original_heading_match": "PASS",
        "exact_original_body_match": "PASS",
        "source_file_hash_match": "PASS",
        "source_block_hash_match": "PASS",
        "envelope_hash_match": "PASS",
        "gzip_reverse_reconstruction": "PASS",
        "routing_state": "UNROUTED",
        "applicability_state": "UNCLASSIFIED",
        "primary_destinations_populated": 0,
        "secondary_destinations_populated": 0,
        "cross_cutting_laws_populated": 0,
        "semantic_merges": 0,
        "deleted_records": 0,
        "closed_records": 0,
        "routing_start_ready": True,
    }
    VERIFY_JSON.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    VERIFY_MD.write_text("\n".join([
        "# Packet 01.5 — Blank Routing Inventory Independent Verification v1",
        "",
        "STATUS: PASS",
        "WATCH: NONE",
        "BLOCKERS: NONE",
        "ROUTING: NOT STARTED",
        "",
        "## Verified inventory",
        "",
        "- Baseline envelopes: 122",
        "- Provisional envelopes: 2628",
        "- Combined envelopes: 2750",
        "- Provisional source files: 69",
        "- Unique composite addresses: 2750",
        f"- Inventory SHA-256: `{sha256(raw_inventory)}`",
        f"- Address-sequence SHA-256: `{address_sequence_hash}`",
        "",
        "## Lossless proof",
        "",
        "- Source-to-envelope bijection: PASS",
        "- Exact original heading match: PASS",
        "- Exact original body match: PASS",
        "- Source-file hash match: PASS",
        "- Source-block hash match: PASS",
        "- Envelope hash match: PASS",
        "- Deterministic gzip reverse reconstruction: PASS",
        "",
        "## Blank-state proof",
        "",
        "- Routing state: UNROUTED",
        "- Applicability state: UNCLASSIFIED",
        "- Primary destinations populated: 0",
        "- Secondary destinations populated: 0",
        "- Cross-cutting laws populated: 0",
        "- Semantic merges: 0",
        "- Deleted records: 0",
        "- Closed records: 0",
        "",
        "FINAL RESULT: `PASS — 2750-RECORD BLANK ROUTING INVENTORY VERIFIED`",
        "",
        "WATCH: NONE",
        "",
        "BLOCKERS: NONE",
        "",
        "END PACKET 01.5 — BLANK ROUTING INVENTORY INDEPENDENT VERIFICATION v1",
        "",
    ]), encoding="utf-8")

    STATUS_MD.write_text("\n".join([
        "# Packet 01.5 — Routing Inventory Status v74",
        "",
        "STATUS: BLANK ROUTING INVENTORY BUILT AND INDEPENDENTLY VERIFIED",
        "WATCH: NONE",
        "BLOCKERS: NONE",
        "ROUTING START: READY FOR SEPARATE AUTHORIZATION",
        "ROUTING ASSIGNMENTS: NOT STARTED",
        "APPLICABILITY CLASSIFICATION: NOT STARTED",
        "SEMANTIC DEDUPLICATION: NOT STARTED",
        "INDIVIDUAL RECORD CLOSURE: NOT STARTED",
        "PACKET 04: NOT AUTHORIZED",
        "",
        "## Verified count",
        "",
        "- Baseline records: 122",
        "- Provisional records: 2628",
        "- Combined envelopes: 2750",
        "- Unique addresses: 2750",
        "- Source-to-envelope bijection: PASS",
        "",
        "## Preservation",
        "",
        "- Exact original headings: preserved and verified",
        "- Exact original bodies: preserved and verified",
        "- Source-file hashes: preserved and verified",
        "- Source-block hashes: preserved and verified",
        "- Envelope hashes: verified",
        "- Deterministic compressed reconstruction: verified",
        "",
        "## Blank routing state",
        "",
        "- Applicability state: UNCLASSIFIED for all 2750 envelopes",
        "- Routing state: UNROUTED for all 2750 envelopes",
        "- Populated destinations: 0",
        "- Semantic merges: 0",
        "- Deleted records: 0",
        "- Closed records: 0",
        "",
        "## Next required action",
        "",
        "Run the Packet 01.5 Routing-Start Authorization Gate. That gate may authorize applicability classification and owner routing, but it must preserve every source envelope and keep semantic grouping non-destructive.",
        "",
        "END PACKET 01.5 — ROUTING INVENTORY STATUS v74",
        "",
    ]), encoding="utf-8")
    print("PASS — independently verified all 2750 blank routing envelopes")


if __name__ == "__main__":
    main()
