#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MACHINE = ROOT / 'pmp-active-path-discovery-machine-v1.js'
EXPORTER = ROOT / 'pmp-active-path-discovery-zip-export-v2.js'

machine = MACHINE.read_text('utf-8')
exporter = EXPORTER.read_text('utf-8')

checks = {
    'machine_version': "1.4.0-fresh-scan-classification-truth-20260825A" in machine,
    'machine_revision': "1.0.0-current-map-http-truth-20260825A" in machine,
    'current_map_policy': "source:'CURRENT_MAP_FETCH'" in machine and 'map.tool_routes' in machine and 'map.recovery_routes' in machine and 'map.historic_routes' in machine,
    'true_missing_only': "row.status===404||row.status===410" in machine and "return'MISSING'" in machine,
    '412_truth': "row.status===412" in machine and "return'PRECONDITION_REJECTED'" in machine,
    'registry_gap_truth': "transport_class==='REACHABLE'&&!x.in_atlas" in machine and 'atlas_registry_gap_count' in machine,
    'hard_missing_required_only': "missingRows.filter(x=>isRequiredLane(x.lane))" in machine,
    'fresh_scan_identity': 'scan_id:requestedScanId' in machine and 'requested_scan_id:requestedScanId' in machine,
    'exporter_exact_machine': "EXPECTED_MACHINE_VERSION='1.4.0-fresh-scan-classification-truth-20260825A'" in exporter and "EXPECTED_MACHINE_REVISION='1.0.0-current-map-http-truth-20260825A'" in exporter,
    'exporter_forces_run': "const r=await m.run(reason||'manual_export',{scan_id:id" in exporter,
    'exporter_binds_scan_id': 'r.scan_id===id&&r.requested_scan_id===id' in exporter,
    'exporter_no_stale_short_circuit': 'if(r)return r' not in exporter and 'findReport' not in exporter,
    'no_forced_pass': 'freeze_gate:{pass:policy.map_fetch_ok&&hard.length===0' in machine,
    'read_only_boundaries': "fix:'not_attempted'" in machine and "persisted_user_data_write:'not_attempted'" in machine,
    'no_destructive_storage': 'localStorage.clear' not in machine + exporter and 'indexedDB.deleteDatabase' not in machine + exporter,
}
failed = [name for name, ok in checks.items() if not ok]
print({'status': 'PASS' if not failed else 'FAIL', 'checks': len(checks), 'failed': failed})
raise SystemExit(1 if failed else 0)
