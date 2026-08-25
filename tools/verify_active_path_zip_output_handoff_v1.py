#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
EXPORTER = ROOT / 'pmp-active-path-discovery-zip-export-v2.js'
BROWSER = ROOT / 'audit/a002-active-path-zip-output-v1.cjs'
GATE = ROOT / 'audit/pass13/active-path-zip-output-handoff-gate-v1.json'
RECEIPT = ROOT / 'audit/pass13/receipts/RECEIPT_ACTIVE_PATH_ZIP_OUTPUT_HANDOFF_20260825B_001.json'

source = EXPORTER.read_text('utf-8')
browser = BROWSER.read_text('utf-8') if BROWSER.exists() else ''
gate = json.loads(GATE.read_text('utf-8')) if GATE.exists() else {}
receipt = json.loads(RECEIPT.read_text('utf-8')) if RECEIPT.exists() else {}

checks = {
    'exact_exporter_revision': "2.7.0-zip-user-activation-handoff-20260825B" in source,
    'fresh_scan_still_forced': "await runDiscovery('zip_export')" in source,
    'download_link_is_persistent_ui': "data-pmp-discovery-zip-download" in source and 'prepareZipLink' in source,
    'manual_user_gesture_path': 'Download Fresh Atlas ZIP' in source and 'a.download=fn' in source,
    'browser_exercises_real_download_event': "waitForEvent('download')" in browser and "suggestedFilename()" in browser,
    'browser_validates_zip_bytes': "0x50" in browser and "0x4b" in browser and "discovery-report.json" in browser,
    'gate_scope_bounded': gate.get('type') == 'PMP_ACTIVE_PATH_ZIP_OUTPUT_HANDOFF_GATE_V1' and gate.get('unit_id') == 'P13-U106',
    'receipt_boundaries': receipt.get('boundaries', {}).get('owner_changes') is False and receipt.get('boundaries', {}).get('route_changes') is False and receipt.get('boundaries', {}).get('persisted_user_data_write') is False,
    'phone_claim_not_predeclared': receipt.get('verification', {}).get('user_device_proof') == 'REQUIRED_AFTER_DEPLOYMENT',
}
failed = [name for name, ok in checks.items() if not ok]
print({'status': 'PASS' if not failed else 'FAIL', 'checks': len(checks), 'failed': failed})
raise SystemExit(1 if failed else 0)
