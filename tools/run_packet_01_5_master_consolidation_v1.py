#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_packet_01_5_master_consolidation_v1.py"

spec = importlib.util.spec_from_file_location("packet015_master_builder", BUILDER)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def schema_aware_claim(record):
    direct = record.get("preserved_claim")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    missing = record.get("missing_proof")
    marker = "Preserved claim: "
    if isinstance(missing, str) and marker in missing:
        return missing.split(marker, 1)[1].strip()
    for key in (
        "source_claim",
        "claim_text",
        "historical_claim",
        "harm_text",
        "finding",
        "statement",
        "record_text",
        "source_text",
        "claim",
        "overlap_text",
        "original_body",
    ):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


module.claim = schema_aware_claim
module.main()

# The family decision artifacts do not all repeat ordinal and original identifier.
# Add those immutable identity fields explicitly from the authoritative window.
window = module.js(module.WIN)
identity = {
    item["composite_address"]: {
        "source_record_ordinal": item["source_record_ordinal"],
        "original_identifier": item["original_identifier"],
        "source_envelope_hash": item["envelope_hash"],
        "source_block_hash": item["source_block_hash"],
    }
    for item in window["record_identities"]
}
rows = [json.loads(line) for line in module.OD.read_text(encoding="utf-8").splitlines() if line.strip()]
for row in rows:
    for key, value in identity[row["composite_address"]].items():
        row[key] = value
module.wl(module.OD, rows)
