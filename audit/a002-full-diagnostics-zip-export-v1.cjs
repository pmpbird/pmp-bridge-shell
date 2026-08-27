const fs=require('fs');
const {chromium}=require('playwright');
const BASE=process.env.A002_BASE_URL||'http://127.0.0.1:8000/';
const RESULT=process.env.A002_FULL_DIAGNOSTICS_ZIP_RESULT_PATH||'a002-full-diagnostics-zip-export-results.json';
const source=fs.readFileSync('pmp-diagnostics-consolidated-view-v1.js','utf8');
const AKEY='pmp_diagnostic_coverage_pass_a_v1_receipt';
const BKEY='pmp_diagnostic_coverage_passes_bcd_v1_receipt';
const bootVersion='3.4.0-fresh-evaluation-source-identity-20260825A';
const bcdVersion='1.1.0-final-two-live-proof-20260801A';
const bcdRevision='1.4.0-fresh-evaluation-source-identity-20260825A';
const bcdSource='pmp-diagnostic-coverage-passes-bcd-v1-1-1-0-fresh-evaluation-20260825A.js';
function section(type){return{type,status:'PASS',at:new Date().toISOString(),issues:[]}}
(async()=>{
  const browser=await chromium.launch({headless:true});
  const context=await browser.newContext({acceptDownloads:true});
  const page=await context.newPage();
  await page.goto(BASE+'pmp-pages-publish-smoke-v1.html',{waitUntil:'domcontentloaded'});
  await page.evaluate(({AKEY,BKEY,bootVersion,bcdVersion,bcdRevision,bcdSource})=>{
    document.body.innerHTML='<main id="host"></main>';
    window.PMPDiagnosticsOwnerV1={
      owner:'diagnostics_owner',
      renderHome(_w,d){let s=d.getElementById('pmpDiagnosticsScreenV1');if(!s){s=d.createElement('section');s.id='pmpDiagnosticsScreenV1';s.className='screen';d.body.appendChild(s)}return s},
      currentReport(){return{type:'PMP_DIAGNOSTICS_OWNER_REPORT_V1',status:'PASS',diagnostic_confidence:{overall:'HIGH'},warnings:[],reports:{}}}
    };
    window.PMPDiagnosticCoveragePassAV1={run:async()=>{const a={version:'test-pass-a',status:'PASS',at:new Date().toISOString(),app_orchestrator_system:{type:'APP',status:'PASS',issues:[]},active_path_and_routing:{type:'PATH',status:'PASS',issues:[]},runtime_and_mount_lifecycle:{type:'MOUNT',status:'PASS',issues:[]}};localStorage.setItem(AKEY,JSON.stringify(a));return a}};
    window.PMPCurrentBCDDiagnosticsBootstrapV1={version:bootVersion,run:async()=>{await new Promise(r=>setTimeout(r,80));const evaluation_id='full-diagnostics-zip-eval-'+Date.now();const b={version:bcdVersion,revision:bcdRevision,source_identity:bcdSource,evaluation_id,status:'PASS',at:new Date().toISOString(),bridge_system:{type:'BRIDGE',status:'PASS',issues:[]},library_system:{type:'LIBRARY',status:'PASS',issues:[]},bank_system:{type:'BANK',status:'PASS',issues:[]},continuous_run_system:{type:'CONTINUOUS',status:'PASS',issues:[]},errors_bug_watch_visual_stability:{type:'ERRORS',status:'PASS',issues:[]}};localStorage.setItem(BKEY,JSON.stringify(b));return{status:'PASS',evaluation_id}}};
  },{AKEY,BKEY,bootVersion,bcdVersion,bcdRevision,bcdSource});
  await page.addScriptTag({content:source});
  await page.evaluate(()=>{const api=window.PMPDiagnosticsConsolidatedViewV1;if(!api.install())throw new Error('install failed');api.renderDetail(window,document,'full_report',true)});
  const exportButton=page.locator('#pmpDiagZipFull');
  await exportButton.waitFor({state:'visible'});
  await exportButton.click();
  const link=page.locator('[data-pmp-full-diagnostics-zip-download="1"]');
  await link.waitFor({state:'visible'});
  const readyText=await exportButton.textContent();
  const href=await link.getAttribute('href');
  const downloadName=await link.getAttribute('download');
  const [download]=await Promise.all([page.waitForEvent('download'),link.click()]);
  const savedPath=await download.path();
  const bytes=fs.readFileSync(savedPath);
  const latin=bytes.toString('latin1');
  const suggested=download.suggestedFilename();
  const apiState=await page.evaluate(()=>({version:window.PMPDiagnosticsConsolidatedViewV1.version,zipExportRevision:window.PMPDiagnosticsConsolidatedViewV1.zipExportRevision,evidence:window.PMPDiagnosticsConsolidatedViewV1.evidenceState()}));
  const checks={
    diagnostics_version_preserved:apiState.version==='2.9.2-fresh-bcd-evaluation-binding-20260825A',
    zip_revision_exact:apiState.zipExportRevision==='1.0.0-full-diagnostics-zip-handoff-20260826A',
    full_report_copy_retired:((await page.locator('#pmpDiagCopyFull').count())===0)&&((await page.getByText('Copy Full Diagnostics Report',{exact:true}).count())===0),
    section_copy_still_available:(await page.locator('[data-copy-section]').count())===8,
    export_control_visible:await exportButton.isVisible(),
    fresh_evidence_complete:apiState.evidence&&apiState.evidence.status==='COMPLETE'&&apiState.evidence.fresh_evaluation_bound===true,
    persistent_manual_link_visible:await link.isVisible(),
    ready_or_requested_status:/ZIP (?:ready|download requested)/i.test(readyText||''),
    blob_href_present:/^blob:/.test(href||''),
    download_attribute_zip:/\.zip$/i.test(downloadName||''),
    real_browser_download_event:/\.zip$/i.test(suggested||''),
    zip_local_header_signature:bytes.length>4&&bytes[0]===0x50&&bytes[1]===0x4b&&bytes[2]===0x03&&bytes[3]===0x04,
    zip_contains_full_report:latin.includes('full-diagnostics-report.json')&&latin.includes('PMP_FULL_DIAGNOSTICS_REPORT_V2'),
    zip_contains_whole_app_health:latin.includes('whole-app-health.json')&&latin.includes('PMP_WHOLE_APP_HEALTH_V2'),
    zip_contains_metadata:latin.includes('diagnostics-export-metadata.json')&&latin.includes('PMP_FULL_DIAGNOSTICS_ZIP_EXPORT_V1'),
    zip_contains_summary:latin.includes('diagnostics-summary.txt')&&latin.includes('PMP_FULL_DIAGNOSTICS_ZIP_SUMMARY_V1'),
    all_major_sections_present:['app_orchestrator_system','active_path_and_routing','runtime_and_mount_lifecycle','bridge_system','library_system','bank_system','continuous_run_system','errors_bug_watch_visual_stability'].every(x=>latin.includes(x)),
    read_only_boundaries_present:latin.includes('no_owner_change')&&latin.includes('no_route_change')&&latin.includes('no_user_data_write')
  };
  const failed=Object.entries(checks).filter(([,ok])=>!ok).map(([k])=>k);
  const result={type:'PMP_A002_FULL_DIAGNOSTICS_ZIP_EXPORT_RESULT_V1',status:failed.length?'FAIL':'PASS',checks,failed,ready_text:readyText,download_name:downloadName,suggested_filename:suggested,bytes:bytes.length,evidence_state:apiState.evidence};
  fs.writeFileSync(RESULT,JSON.stringify(result,null,2)+'\n');
  await browser.close();
  console.log(JSON.stringify({status:result.status,failed,suggested,bytes:bytes.length}));
  process.exit(failed.length?1:0);
})().catch(error=>{try{fs.writeFileSync(RESULT,JSON.stringify({type:'PMP_A002_FULL_DIAGNOSTICS_ZIP_EXPORT_RESULT_V1',status:'FAIL',error:String(error&&error.stack||error)},null,2)+'\n')}catch(_){};console.error(error);process.exit(1)});
