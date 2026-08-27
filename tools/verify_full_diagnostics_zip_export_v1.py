#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'pmp-diagnostics-consolidated-view-v1.js').read_text('utf-8')
browser=(ROOT/'audit/a002-full-diagnostics-zip-export-v1.cjs').read_text('utf-8')
legacy_gate=json.loads((ROOT/'audit/pass13/full-diagnostics-zip-export-gate-v1.json').read_text('utf-8'))
legacy_receipt=json.loads((ROOT/'audit/pass13/receipts/RECEIPT_FULL_DIAGNOSTICS_ZIP_EXPORT_20260826A_001.json').read_text('utf-8'))
retirement_gate=json.loads((ROOT/'audit/pass13/full-diagnostics-copy-retirement-gate-v1.json').read_text('utf-8'))
retirement_receipt=json.loads((ROOT/'audit/pass13/receipts/RECEIPT_FULL_DIAGNOSTICS_COPY_RETIREMENT_20260827A_001.json').read_text('utf-8'))
checks={
 'exact_zip_revision':"1.0.0-full-diagnostics-zip-handoff-20260826A" in source,
 'fresh_diagnostics_generation':"await produceEvidence('zip_full_diagnostics')" in source,
 'full_report_copy_retired':'Copy Full Diagnostics Report' not in source and 'pmpDiagCopyFull' not in source and 'copy_full_diagnostics' not in source,
 'section_copy_preserved':'Copy This Section' in source and 'data-copy-section' in source,
 'whole_app_copy_preserved':'Copy Whole App Health Report' in source and 'pmpDiagCopyWhole' in source,
 'persistent_download_ui':'data-pmp-full-diagnostics-zip-download' in source and 'Download Full Diagnostics ZIP' in source,
 'browser_exercises_real_download_event':"waitForEvent('download')" in browser and 'suggestedFilename()' in browser,
 'browser_validates_zip_bytes':'bytes[0]===0x50' in browser and "full-diagnostics-report.json" in browser,
 'browser_validates_complete_report':'PMP_FULL_DIAGNOSTICS_REPORT_V2' in browser and 'errors_bug_watch_visual_stability' in browser,
 'browser_asserts_copy_retired':'full_report_copy_retired' in browser and 'section_copy_still_available' in browser,
 'legacy_zip_gate_preserved':legacy_gate.get('type')=='PMP_FULL_DIAGNOSTICS_ZIP_EXPORT_GATE_V1' and legacy_gate.get('unit_id')=='P13-U109',
 'legacy_receipt_preserved':legacy_receipt.get('type')=='PMP_FULL_DIAGNOSTICS_ZIP_EXPORT_RECEIPT_V1',
 'retirement_gate_bound':retirement_gate.get('type')=='PMP_FULL_DIAGNOSTICS_COPY_RETIREMENT_GATE_V1' and retirement_gate.get('unit_id')=='P13-U110' and retirement_gate.get('status')=='PASS',
 'device_zip_proof_recorded':retirement_receipt.get('device_proof_before_retirement',{}).get('status')=='PASS' and retirement_receipt.get('device_proof_before_retirement',{}).get('sha256')=='b69f29559ac3153844b87afed1b201bda1f2beee83de259b6e81704e2a9d9c65',
 'post_retirement_phone_confirmation_pending':retirement_receipt.get('verification',{}).get('post_retirement_user_device_confirmation')=='REQUIRED_AFTER_DEPLOYMENT',
 'read_only_boundaries':retirement_receipt.get('boundaries',{}).get('owner_changes') is False and retirement_receipt.get('boundaries',{}).get('route_changes') is False and retirement_receipt.get('boundaries',{}).get('persisted_user_data_write') is False,
}
failed=[k for k,v in checks.items() if not v]
print({'status':'PASS' if not failed else 'FAIL','checks':len(checks),'failed':failed})
raise SystemExit(1 if failed else 0)
