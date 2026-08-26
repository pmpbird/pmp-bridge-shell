#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
m = (ROOT / 'pmp-active-path-discovery-machine-v1.js').read_text('utf-8')
e = (ROOT / 'pmp-active-path-discovery-zip-export-v2.js').read_text('utf-8')

assert re.search(r"const VERSION='1\.5\.0-served-a003-reference-truth-20260826A'", m)
assert "if(row.status===404||row.status===410)return'MISSING'" in m
assert "if(row.status===412)return'PRECONDITION_REJECTED'" in m
assert "const gaps=rows.filter(x=>x.transport_class==='REACHABLE'&&!x.in_atlas" in m
assert "const hard=uniq(missingRows.filter(x=>isRequiredLane(x.lane))" in m
assert "map_policy:{source:policy.source,fetch_ok:policy.map_fetch_ok" in m
assert "freeze_gate:{pass:policy.map_fetch_ok&&integrity.fetch_ok&&!!integrity.manifest_sha256" in m
assert "async function runDiscovery(reason){const id=requestId" in e
assert "const r=await m.run(reason||'manual_export',{scan_id:id" in e
assert "return valid(r,id)?r:missing(id,'FRESH_SCAN_IDENTITY_MISMATCH')" in e
assert 'findReport' not in e
assert 'stored(' not in e
assert "Advanced: Export Fresh Full ZIP" in e
assert "PMP_DISCOVERY_BLOCKER_DETAIL_V1" in e and 'atlas_registry_gap_count' in e and 'precondition_rejected_count' in e
for forbidden in ('localStorage.clear', 'indexedDB.deleteDatabase', 'location.href=', 'history.replaceState'):
    assert forbidden not in m + e, forbidden
print({'status': 'PASS', 'independent_verifier': True})
