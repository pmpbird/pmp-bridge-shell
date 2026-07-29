#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "pmp-active-bug-found-contract-v1.js"
text = TARGET.read_text(encoding="utf-8")

required = [
    "pmp_bug_bank_active_bugs_v1",
    "pmp_bug_watch_receipt_lineage_v2",
    "pmp_bug_watch_dedupe_index_v2",
    "pmp_bug_watch_handoff_lineage_v2",
    "pmp_bug_watch_session_durable_v1_receipt",
    "pmp_bug_watch_passive_capture_v1_receipt",
    "pmp_active_bug_found_contract_v1_receipt",
    "ACTIVE_SESSION_MONITORING",
    "setInterval(heartbeat,2000)",
    "existing_rows_rewritten:false",
    "existing_rows_deleted:false",
    "automatic_repair:false",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("FAIL missing durable bug-watch requirements: " + ", ".join(missing))

for forbidden in ["localStorage.removeItem", ".splice(", "clearCatalog("]:
    if forbidden in text:
        raise SystemExit(f"FAIL destructive token present: {forbidden}")

print("PASS durable bug watch Diagnostics repair")
