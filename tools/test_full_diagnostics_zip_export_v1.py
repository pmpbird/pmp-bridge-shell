#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'pmp-diagnostics-consolidated-view-v1.js').read_text('utf-8')
checks={
 'zip_revision':"1.0.0-full-diagnostics-zip-handoff-20260826A" in source,
 'diagnostics_owner_unchanged':"const OWNER='diagnostics_owner';" in source,
 'full_report_truth_path_preserved':"type:'PMP_FULL_DIAGNOSTICS_REPORT_V2'" in source and "function fullDiagnosticReport()" in source,
 'copy_control_preserved':'Copy Full Diagnostics Report' in source and 'pmpDiagCopyFull' in source,
 'zip_control_added':'Export Full Diagnostics ZIP' in source and 'pmpDiagZipFull' in source,
 'fresh_evidence_before_zip':"await produceEvidence('zip_full_diagnostics')" in source,
 'persistent_download_link':'data-pmp-full-diagnostics-zip-download' in source and 'Download Full Diagnostics ZIP' in source,
 'download_attribute':'a.download=filename' in source,
 'manual_second_gesture_supported':'tap Download Full Diagnostics ZIP if it did not start automatically' in source,
 'auto_click_only_with_activation':'nav.userActivation&&nav.userActivation.isActive' in source,
 'prepared_blob_not_immediately_revoked':'setTimeout(()=>{try{URL.revokeObjectURL' not in source,
 'prior_blob_revoked_on_replacement':'clearDiagnosticsZipLink(d)' in source and 'revokeObjectURL(href)' in source,
 'four_zip_members':all(x in source for x in ["name:'full-diagnostics-report.json'","name:'whole-app-health.json'","name:'diagnostics-export-metadata.json'","name:'diagnostics-summary.txt'"]),
 'export_api_exposed':'exportFullDiagnosticsZip' in source and 'zipExportRevision:ZIP_EXPORT_REVISION' in source,
 'read_only_metadata':all(x in source for x in ['owner_changes:false','helper_changes:false','route_changes:false','bank_rebuild:false','continuous_run_mutation:false','storage_migration:false','persisted_user_data_write:false','persisted_user_data_delete:false']),
 'no_destructive_storage':'localStorage.clear' not in source and 'indexedDB.deleteDatabase' not in source,
}
failed=[k for k,v in checks.items() if not v]
print({'status':'PASS' if not failed else 'FAIL','checks':len(checks),'failed':failed})
raise SystemExit(1 if failed else 0)
