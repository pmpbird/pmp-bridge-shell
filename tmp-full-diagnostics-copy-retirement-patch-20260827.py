#!/usr/bin/env python3
import json
from pathlib import Path

root=Path('.')
src=root/'pmp-diagnostics-consolidated-view-v1.js'
s=src.read_text('utf-8')
old_controls="controls='<button type=\"button\" class=\"pmpDiagAction\" id=\"pmpDiagCopyFull\">Copy Full Diagnostics Report</button><button type=\"button\" class=\"pmpDiagAction\" id=\"pmpDiagZipFull\">Export Full Diagnostics ZIP</button><span id=\"pmpDiagFullZipLinkHost\"></span>';"
new_controls="controls='<button type=\"button\" class=\"pmpDiagAction\" id=\"pmpDiagZipFull\">Export Full Diagnostics ZIP</button><span id=\"pmpDiagFullZipLinkHost\"></span>';"
handler="const full=d.getElementById('pmpDiagCopyFull');if(full)full.onclick=async()=>{full.disabled=true;full.textContent='Running current live diagnostics…';await produceEvidence('copy_full_diagnostics');const ok=await copyText(JSON.stringify(fullDiagnosticReport(),null,2));full.textContent=ok?'Copied':'Copy unavailable';full.disabled=false};"
assert s.count(old_controls)==1,s.count(old_controls)
assert s.count(handler)==1,s.count(handler)
s=s.replace(old_controls,new_controls,1).replace(handler,'',1)
assert 'Copy Full Diagnostics Report' not in s and 'pmpDiagCopyFull' not in s and 'copy_full_diagnostics' not in s
assert 'Export Full Diagnostics ZIP' in s and 'Download Full Diagnostics ZIP' in s
assert 'Copy This Section' in s and 'Copy Whole App Health Report' in s
src.write_text(s,'utf-8')

(root/'tools/test_full_diagnostics_zip_export_v1.py').write_text('''#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'pmp-diagnostics-consolidated-view-v1.js').read_text('utf-8')
checks={
 'zip_revision':"1.0.0-full-diagnostics-zip-handoff-20260826A" in source,
 'diagnostics_owner_unchanged':"const OWNER='diagnostics_owner';" in source,
 'full_report_truth_path_preserved':"type:'PMP_FULL_DIAGNOSTICS_REPORT_V2'" in source and "function fullDiagnosticReport()" in source,
 'full_report_copy_retired':'Copy Full Diagnostics Report' not in source and 'pmpDiagCopyFull' not in source and 'copy_full_diagnostics' not in source,
 'whole_app_copy_preserved':'Copy Whole App Health Report' in source and 'pmpDiagCopyWhole' in source,
 'section_copy_preserved':'Copy This Section' in source and 'data-copy-section' in source and 'copy_section_' in source,
 'zip_control_present':'Export Full Diagnostics ZIP' in source and 'pmpDiagZipFull' in source,
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
''','utf-8')

browser_path=root/'audit/a002-full-diagnostics-zip-export-v1.cjs'
b=browser_path.read_text('utf-8')
assert b.count("  const copy=page.locator('#pmpDiagCopyFull');\n")==1,b.count("  const copy=page.locator('#pmpDiagCopyFull');\n")
b=b.replace("  const copy=page.locator('#pmpDiagCopyFull');\n",'',1)
assert b.count("    copy_path_preserved:await copy.count()===1,")==1,b.count("    copy_path_preserved:await copy.count()===1,")
b=b.replace("    copy_path_preserved:await copy.count()===1,","    full_report_copy_retired:((await page.locator('#pmpDiagCopyFull').count())===0)&&((await page.getByText('Copy Full Diagnostics Report',{exact:true}).count())===0),\n    section_copy_still_available:(await page.locator('[data-copy-section]').count())===8,",1)
browser_path.write_text(b,'utf-8')

boundaries={'owner_changes':False,'helper_changes':False,'route_changes':False,'bank_rebuild':False,'continuous_run_mutation':False,'dom_repair':False,'storage_migration':False,'persisted_user_data_write':False,'persisted_user_data_delete':False,'diagnostics_truth_changes':False,'atlas_changes':False}
gate={
 'type':'PMP_FULL_DIAGNOSTICS_COPY_RETIREMENT_GATE_V1','version':'1.0.0','revision':'1.0.0-zip-only-full-report-handoff-20260827A','unit_id':'P13-U110','status':'PASS',
 'claim_ceiling':'Retires only the unusable full-report clipboard action after successful iPhone ZIP handoff proof. ZIP export, per-section copy, Whole App Health copy, diagnostics truth, owner/helper authority, routes, Bank, Continuous Run, storage, and persisted user data are unchanged. Fresh iPhone post-deployment confirmation is still required.',
 'proven_defect':{'control':'Copy Full Diagnostics Report','reason':'The complete Full Diagnostics JSON is too large for the user to paste into chat, so the full-report clipboard action has no usable handoff path.','replacement':'Export Full Diagnostics ZIP','replacement_device_proof':'PASS'},
 'device_zip_proof':{'filename':'pmp-full-diagnostics-2026-08-27T13-39-10-455Z.zip','sha256':'b69f29559ac3153844b87afed1b201bda1f2beee83de259b6e81704e2a9d9c65','bytes':698058,'generated_at':'2026-08-27T13:39:10.446Z','evidence_status':'COMPLETE','members':['full-diagnostics-report.json','whole-app-health.json','diagnostics-export-metadata.json','diagnostics-summary.txt'],'whole_app_health':{'failures':0,'warnings':0,'not_proven':0},'native_bootstrap_status':'COMPLETE'},
 'harness_history':{'initial_run':'33078852828','initial_result':'STOPPED_BEFORE_COMMIT','diagnostic_run':'33079143338','classification':'TEMPORARY_A003_OUTPUT_FILES_POLLUTED_WORKING_RUNTIME_SCAN','runtime_repair_failure':False},
 'scope':{'changed_paths':['.github/workflows/a002-full-diagnostics-zip-export.yml','audit/a002-full-diagnostics-zip-export-v1.cjs','audit/a003-manifest-seal.json','audit/pass13/full-diagnostics-copy-retirement-gate-v1.json','audit/pass13/receipts/RECEIPT_FULL_DIAGNOSTICS_COPY_RETIREMENT_20260827A_001.json','pmp-app-current.html','pmp-diagnostics-consolidated-view-v1.js','pmp-runtime-integrity-manifest-v1.json','tools/test_full_diagnostics_zip_export_v1.py','tools/verify_full_diagnostics_zip_export_v1.py'],'implementation_paths':['pmp-diagnostics-consolidated-view-v1.js','pmp-app-current.html']},
 'boundaries':boundaries,
 'required_current_behavior':{'full_report_copy_control':False,'zip_export_control':True,'persistent_zip_download_link':True,'section_copy_controls':True,'whole_app_health_copy_control':True},
 'post_deployment_phone_confirmation':'REQUIRED'
}
(root/'audit/pass13/full-diagnostics-copy-retirement-gate-v1.json').write_text(json.dumps(gate,indent=2,sort_keys=True)+'\n','utf-8')

receipt={
 'type':'PMP_FULL_DIAGNOSTICS_COPY_RETIREMENT_RECEIPT_V1','version':'1.0.0','revision':'1.0.0-zip-only-full-report-handoff-20260827A','status':'PASS',
 'observed_problem':{'surface':'Diagnostics → Full Diagnostics','unusable_control':'Copy Full Diagnostics Report','reason':'Complete report output is too large for the user to paste into chat.','user_authorization':'Explicitly requested deletion of the unusable copy option after successful ZIP export.'},
 'device_proof_before_retirement':{'status':'PASS','filename':'pmp-full-diagnostics-2026-08-27T13-39-10-455Z.zip','sha256':'b69f29559ac3153844b87afed1b201bda1f2beee83de259b6e81704e2a9d9c65','bytes':698058,'generated_at':'2026-08-27T13:39:10.446Z','zip_export_revision':'1.0.0-full-diagnostics-zip-handoff-20260826A','report_type':'PMP_FULL_DIAGNOSTICS_REPORT_V2','report_version':'2.9.2-fresh-bcd-evaluation-binding-20260825A','evidence_status':'COMPLETE','native_bootstrap_status':'COMPLETE','whole_app_failures':0,'whole_app_warnings':0,'whole_app_not_proven':0,'members':['full-diagnostics-report.json','whole-app-health.json','diagnostics-export-metadata.json','diagnostics-summary.txt']},
 'repair':{'removed':['Copy Full Diagnostics Report control','pmpDiagCopyFull handler','copy_full_diagnostics evidence request path'],'preserved':['Export Full Diagnostics ZIP','Download Full Diagnostics ZIP','Copy This Section controls','Copy Whole App Health Report','fullDiagnosticReport truth generation'],'zip_revision_unchanged':'1.0.0-full-diagnostics-zip-handoff-20260826A'},
 'verification':{'deterministic_test':'tools/test_full_diagnostics_zip_export_v1.py','independent_verifier':'tools/verify_full_diagnostics_zip_export_v1.py','browser_path':'audit/a002-full-diagnostics-zip-export-v1.cjs','ci_workflow':'.github/workflows/a002-full-diagnostics-zip-export.yml','successful_branch_certification_run':'RUNTIME_SET_BY_WORKFLOW','failed_harness_run':'33078852828','a003_diagnostic_run':'33079143338','user_device_proof_before_retirement':'PASS','post_retirement_user_device_confirmation':'REQUIRED_AFTER_DEPLOYMENT'},
 'boundaries':boundaries,
 'claim_ceiling':'Repository/browser proof plus successful pre-retirement iPhone ZIP handoff. Do not claim post-retirement phone UI complete until merged, main is automatically A-003 resealed and deployed, and the user confirms the Copy Full Diagnostics Report control is gone while ZIP export remains usable.'
}
(root/'audit/pass13/receipts/RECEIPT_FULL_DIAGNOSTICS_COPY_RETIREMENT_20260827A_001.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n','utf-8')

(root/'tools/verify_full_diagnostics_zip_export_v1.py').write_text('''#!/usr/bin/env python3
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
''','utf-8')
