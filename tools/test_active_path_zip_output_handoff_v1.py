#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPORTER = ROOT / 'pmp-active-path-discovery-zip-export-v2.js'
source = EXPORTER.read_text('utf-8')

checks = {
    'exporter_version': "2.7.0-zip-user-activation-handoff-20260825B" in source,
    'fresh_scan_contract_preserved': "EXPECTED_MACHINE_VERSION='1.5.0-served-a003-reference-truth-20260826A'" in source and "EXPECTED_MACHINE_REVISION='1.1.0-served-a003-reference-truth-20260826A'" in source,
    'real_download_anchor': "data-pmp-discovery-zip-download" in source and "a.download=fn" in source,
    'zip_prepared_after_fresh_scan': "let r=await runDiscovery('zip_export')" in source and 'prepareZipLink(d,out,blob,fn,r)' in source,
    'direct_second_gesture_supported': "Download Fresh Atlas ZIP" in source and "nav.userActivation&&nav.userActivation.isActive" in source,
    'blocked_auto_download_not_terminal': "tap Download Fresh Atlas ZIP if it did not start automatically" in source,
    'prepared_blob_not_immediately_revoked': "setTimeout(()=>{try{URL.revokeObjectURL" not in source,
    'old_prepared_blob_cleaned_on_replacement': 'clearPreparedZip(d)' in source and 'revokeObjectURL(href)' in source,
    'three_file_zip_preserved': "name:'discovery-report.json'" in source and "name:'freeze-proof.txt'" in source and "name:'blocker-detail.txt'" in source,
    'export_api_exposed_for_browser_test': ',exportZip};' in source,
    'no_stale_report_short_circuit': 'findReport' not in source and 'if(r)return r' not in source,
    'no_destructive_storage': 'localStorage.clear' not in source and 'indexedDB.deleteDatabase' not in source,
}
failed = [name for name, ok in checks.items() if not ok]
print({'status': 'PASS' if not failed else 'FAIL', 'checks': len(checks), 'failed': failed})
raise SystemExit(1 if failed else 0)
