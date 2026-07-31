#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
text=(ROOT/'pmp-app-orchestrator-v1.js').read_text('utf-8')
required=[
"2.6.0-fail-isolated-diagnostics-startup-20260730F",
"async function stage(id,fn)",
"async function produceCoverage(reason)",
"PMPDiagnosticCoveragePassAV1",
"PMPDiagnosticCoveragePassesBCDV1",
"DIAGNOSTIC_RECEIPTS_NOT_PUBLISHED",
"visibility_resume",
"frame_added",
"fail_isolated:true",
"owner_changes:false",
"bank_rebuild:false",
"persisted_user_data_write:false"
]
missing=[x for x in required if x not in text]
for forbidden in ["localStorage.clear(","indexedDB.deleteDatabase(","location.replace("]:
    if forbidden in text: missing.append('FORBIDDEN:'+forbidden)
if missing:
    raise SystemExit('FAIL '+repr(missing))
print('PASS deterministic diagnostics startup source contract')
