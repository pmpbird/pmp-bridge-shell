#!/usr/bin/env python3
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'pmp-diagnostics-consolidated-view-v1.js').read_text('utf-8')
browser=(ROOT/'audit/a002-full-diagnostics-zip-export-v1.cjs').read_text('utf-8') if (ROOT/'audit/a002-full-diagnostics-zip-export-v1.cjs').exists() else ''
gate_path=ROOT/'audit/pass13/full-diagnostics-zip-export-gate-v1.json'
receipt_path=ROOT/'audit/pass13/receipts/RECEIPT_FULL_DIAGNOSTICS_ZIP_EXPORT_20260826A_001.json'
gate=json.loads(gate_path.read_text('utf-8')) if gate_path.exists() else {}
receipt=json.loads(receipt_path.read_text('utf-8')) if receipt_path.exists() else {}
checks={
 'exact_zip_revision':"1.0.0-full-diagnostics-zip-handoff-20260826A" in source,
 'fresh_diagnostics_generation':"await produceEvidence('zip_full_diagnostics')" in source,
 'copy_behavior_retained':'Copy Full Diagnostics Report' in source,
 'persistent_download_ui':'data-pmp-full-diagnostics-zip-download' in source and 'Download Full Diagnostics ZIP' in source,
 'browser_exercises_real_download_event':"waitForEvent('download')" in browser and 'suggestedFilename()' in browser,
 'browser_validates_zip_bytes':'bytes[0]===0x50' in browser and "full-diagnostics-report.json" in browser,
 'browser_validates_complete_report':'PMP_FULL_DIAGNOSTICS_REPORT_V2' in browser and 'errors_bug_watch_visual_stability' in browser,
 'gate_scope_bounded':gate.get('type')=='PMP_FULL_DIAGNOSTICS_ZIP_EXPORT_GATE_V1' and gate.get('unit_id')=='P13-U109',
 'receipt_read_only':receipt.get('boundaries',{}).get('owner_changes') is False and receipt.get('boundaries',{}).get('route_changes') is False and receipt.get('boundaries',{}).get('persisted_user_data_write') is False,
 'phone_claim_pending':receipt.get('verification',{}).get('user_device_proof')=='REQUIRED_AFTER_DEPLOYMENT',
}
failed=[k for k,v in checks.items() if not v]
print({'status':'PASS' if not failed else 'FAIL','checks':len(checks),'failed':failed})
raise SystemExit(1 if failed else 0)
