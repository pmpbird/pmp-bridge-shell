#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "pmp-diagnostics-owner-v1.js"
text = path.read_text(encoding="utf-8")

required = [
    "2.5.0-truth-confidence-20260729A",
    "diagnostic_policy",
    "diagnostic_confidence",
    "CONTEXT_NOT_VISIBLE",
    "SNAPSHOT_ONLY_RUNTIME_NOT_PUBLISHED",
    "HISTORICAL_RECEIPT_NOT_CURRENT_CHAIN",
    "pmp_bug_watch_session_durable_v1_receipt",
    "SOURCE_NOT_PUBLISHED",
    "owner_conflict_pass",
    "dom_integrity_pass",
    "One Diagnostics Owner reports proof-labelled evidence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("FAIL missing Diagnostics truth requirements: " + ", ".join(missing))

for forbidden in [
    "new Worker(",
    "localStorage.removeItem",
    "indexedDB.deleteDatabase",
    "data-pmp-section-owner=\"diagnostics_helper",
]:
    if forbidden in text:
        raise SystemExit(f"FAIL forbidden Diagnostics behavior present: {forbidden}")

if text.count("const OWNER='diagnostics_owner'") != 1:
    raise SystemExit("FAIL Diagnostics owner identity changed or duplicated")

print("PASS Diagnostics truth repair")
