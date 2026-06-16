#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
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
