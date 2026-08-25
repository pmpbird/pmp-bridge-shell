'use strict';
const fs = require('fs');
const { chromium } = require('playwright');

const BASE = process.env.A002_BASE_URL || 'http://127.0.0.1:8000/';
const RESULT_PATH = process.env.A002_DIAGNOSTICS_RESULT_PATH || 'a002-whole-app-diagnostics-results.json';
const CURRENT = 'pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html';
const INNER = 'pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html';
const REQUIRED_BOOT_VERSION = '3.4.0-fresh-evaluation-source-identity-20260825A';
const REQUIRED_BCD_VERSION = '1.1.0-final-two-live-proof-20260801A';
const REQUIRED_BCD_REVISION = '1.4.0-fresh-evaluation-source-identity-20260825A';
const REQUIRED_BCD_SOURCE = 'pmp-diagnostic-coverage-passes-bcd-v1-1-1-0-fresh-evaluation-20260825A.js';
const SECTIONS = ['bridge_system','library_system','bank_system','continuous_run_system','errors_bug_watch_visual_stability'];

const results=[];const runtimeErrors=[];let fatalError=null;
function errorValue(error){return{name:String(error?.name||'Error'),message:String(error?.message||error),stack:String(error?.stack||'')}}
function record(name,pass,detail={}){results.push({name,pass:!!pass,detail,at:new Date().toISOString()});console.log(`${pass?'PASS':'FAIL'} ${name} ${JSON.stringify(detail)}`)}
function writeOutput(){const output={type:'PMP_A002_WHOLE_APP_DIAGNOSTICS_CERTIFICATION_V7',generated_at:new Date().toISOString(),base_url:BASE,required_bootstrap_version:REQUIRED_BOOT_VERSION,required_bcd_version:REQUIRED_BCD_VERSION,required_bcd_revision:REQUIRED_BCD_REVISION,required_bcd_source_identity:REQUIRED_BCD_SOURCE,required_sections:SECTIONS,tests_total:results.length,tests_passed:results.filter(x=>x.pass).length,tests_failed:results.filter(x=>!x.pass).length,runtime_errors:runtimeErrors,fatal_error:fatalError,results};fs.writeFileSync(RESULT_PATH,JSON.stringify(output,null,2));console.log(`A002_DIAGNOSTICS_RESULT_WRITTEN ${RESULT_PATH} ${JSON.stringify({tests_total:output.tests_total,tests_passed:output.tests_passed,tests_failed:output.tests_failed,runtime_errors:output.runtime_errors.length,fatal_error:!!fatalError})}`)}
async function waitForFrame(page,pattern,timeout=65000){const deadline=Date.now()+timeout;while(Date.now()<deadline){const frame=page.frames().find(f=>pattern.test(f.url()));if(frame)return frame;await page.waitForTimeout(250)}throw new Error(`frame not found: ${pattern}`)}
async function waitForApiFrame(page,name,timeout=65000){const deadline=Date.now()+timeout;while(Date.now()<deadline){for(const frame of page.frames()){try{if(await frame.evaluate(n=>!!(window[n]&&typeof window[n].run==='function'),name))return frame}catch{}}await page.waitForTimeout(250)}throw new Error(`API frame not found: ${name}`)}
async function enterCurrentApp(page){
  await page.goto(BASE+'pmp-app-current.html#control',{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>{try{return JSON.parse(localStorage.getItem('pmp_a003_bootstrap_receipt_v1')||'null')?.status==='PASS'}catch{return false}},null,{timeout:40000});
  const guardian=await waitForFrame(page,/pmp-route-guardian-current-loader-v22\.html/,40000);
  await guardian.click('#openBtn',{force:true});
  await page.waitForURL(url=>url.pathname.endsWith('/'+CURRENT)&&url.hash==='#control',{timeout:40000});
  const runButton=page.locator('#pmpPass75ReloadRuntimePlatformGateV1 [data-run="1"]');
  await runButton.waitFor({state:'visible',timeout:30000});
  const gateReceipt=await page.evaluate(()=>{try{return JSON.parse(localStorage.getItem('pmp_pass75_reload_runtime_platform_gate_v1_receipt')||'null')}catch{return null}});
  record('runtime-platform-certified-before-governed-entry',gateReceipt?.certified===true&&gateReceipt?.released===false,{receipt:gateReceipt});
  await runButton.click({force:true});
  await page.waitForFunction(()=>{try{return JSON.parse(localStorage.getItem('pmp_pass75_reload_runtime_platform_gate_v1_receipt')||'null')?.released===true}catch{return false}},null,{timeout:15000});
  const inner=await waitForFrame(page,new RegExp(INNER.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')),65000);
  const apiFrame=await waitForApiFrame(page,'PMPCurrentBCDDiagnosticsBootstrapV1',65000);
  await page.waitForTimeout(6000);
  return{inner,apiFrame};
}
async function retiredTraceControls(page){const found=[];for(const frame of page.frames()){try{const count=await frame.locator('#pmpWholeAppHealthLayoutTraceV1, [data-pmp-whole-app-health-layout-trace]').count();if(count)found.push({url:frame.url(),count})}catch{}}return found}

(async()=>{let browser=null;try{
  browser=await chromium.launch({headless:true});const context=await browser.newContext({serviceWorkers:'allow'});const page=await context.newPage();page.setDefaultTimeout(45000);
  page.on('pageerror',e=>runtimeErrors.push({type:'pageerror',...errorValue(e)}));page.on('console',m=>{if(m.type()==='error')runtimeErrors.push({type:'console',message:m.text()})});
  const{inner,apiFrame}=await enterCurrentApp(page);
  const governedExport=apiFrame===page.mainFrame()||apiFrame.url().includes(INNER);
  record('current-inner-v30-diagnostics-owner-frame-ready',inner.url().includes(INNER)&&governedExport,{outer_url:page.url(),inner_url:inner.url(),api_frame_url:apiFrame.url(),api_export_scope:apiFrame===page.mainFrame()?'top_window_export':'inner_v30_frame',frame_urls:page.frames().map(f=>f.url())});

  const state=await apiFrame.evaluate(async contracts=>{
    const parse=k=>{try{return JSON.parse(window.top.localStorage.getItem(k)||'null')}catch{return null}};
    const api=window.PMPCurrentBCDDiagnosticsBootstrapV1;
    const runResult=await api.run('a002_whole_app_diagnostics_certification_v7');
    return{
      apiVersion:api.version||null,
      apiRequiredVersion:api.requiredVersion||null,
      apiRequiredRevision:api.requiredRevision||null,
      apiRequiredSourceIdentity:api.requiredSourceIdentity||null,
      runResult,
      bootstrapReceipt:parse('pmp_current_bcd_diagnostics_bootstrap_v1_receipt'),
      bcdReceipt:parse('pmp_diagnostic_coverage_passes_bcd_v1_receipt'),
      journalReceipt:parse('pmp_diagnostic_journal_v1_receipt'),
      journalViewReceipt:parse('pmp_diagnostic_journal_view_v1_receipt'),
      continuousReceipt:parse('pmp_continuous_run_canonical_level_receipt_v1'),
      contracts
    };
  },{boot:REQUIRED_BOOT_VERSION,version:REQUIRED_BCD_VERSION,revision:REQUIRED_BCD_REVISION,source:REQUIRED_BCD_SOURCE,sections:SECTIONS});

  record('transactional-bootstrap-api-current',
    state.apiVersion===REQUIRED_BOOT_VERSION&&
    state.apiRequiredVersion===REQUIRED_BCD_VERSION&&
    state.apiRequiredRevision===REQUIRED_BCD_REVISION&&
    state.apiRequiredSourceIdentity===REQUIRED_BCD_SOURCE,
    {observed:{version:state.apiVersion,required_version:state.apiRequiredVersion,required_revision:state.apiRequiredRevision,required_source_identity:state.apiRequiredSourceIdentity},required:state.contracts});

  const completed=Array.isArray(state.bootstrapReceipt?.complete_sections)?state.bootstrapReceipt.complete_sections:[];
  const evaluationId=state.runResult?.evaluation_id||null;
  record('transactional-bootstrap-published-fresh-exact-receipt',
    state.runResult?.status==='PASS'&&
    state.bootstrapReceipt?.status==='PASS'&&
    state.bootstrapReceipt?.evaluation_id===evaluationId&&
    state.bootstrapReceipt?.observed_receipt_evaluation_id===evaluationId&&
    state.bcdReceipt?.evaluation_id===evaluationId&&
    state.bcdReceipt?.version===REQUIRED_BCD_VERSION&&
    state.bcdReceipt?.revision===REQUIRED_BCD_REVISION&&
    state.bcdReceipt?.source_identity===REQUIRED_BCD_SOURCE&&
    SECTIONS.every(s=>completed.includes(s)),
    {run_result:state.runResult,bootstrap_receipt:state.bootstrapReceipt,bcd_identity:state.bcdReceipt&&{version:state.bcdReceipt.version,revision:state.bcdReceipt.revision,source_identity:state.bcdReceipt.source_identity,evaluation_id:state.bcdReceipt.evaluation_id,at:state.bcdReceipt.at,reason:state.bcdReceipt.reason}});

  record('passes-bcd-receipt-exact-current-source',
    state.bcdReceipt?.version===REQUIRED_BCD_VERSION&&state.bcdReceipt?.revision===REQUIRED_BCD_REVISION&&state.bcdReceipt?.source_identity===REQUIRED_BCD_SOURCE,
    {observed:{version:state.bcdReceipt?.version||null,revision:state.bcdReceipt?.revision||null,source_identity:state.bcdReceipt?.source_identity||null},required:{version:REQUIRED_BCD_VERSION,revision:REQUIRED_BCD_REVISION,source_identity:REQUIRED_BCD_SOURCE}});

  for(const section of SECTIONS){const value=state.bcdReceipt?.[section]||null;record(`whole-app-section-pass:${section}`,value?.status==='PASS',{status:value?.status||'MISSING',type:value?.type||null,issues:Array.isArray(value?.issues)?value.issues:null,backlog:Array.isArray(value?.backlog)?value.backlog:null,checks:value?.checks||null})}
  record('passes-bcd-overall-pass',state.bcdReceipt?.status==='PASS',{status:state.bcdReceipt?.status||'MISSING',reason:state.bcdReceipt?.reason||null,evaluation_id:state.bcdReceipt?.evaluation_id||null,runtime_context:state.bcdReceipt?.runtime_context||null});
  record('diagnostic-journal-current-session-proof',state.journalReceipt?.status==='PASS'&&state.journalViewReceipt?.available===true,{journal:state.journalReceipt,journal_view:state.journalViewReceipt});
  record('continuous-run-canonical-32-level-proof',state.continuousReceipt?.status==='PASS'&&state.continuousReceipt?.expected_level_count===32&&Array.isArray(state.continuousReceipt?.expected_levels)&&state.continuousReceipt.expected_levels.length===32,{continuous:state.continuousReceipt});
  const traces=await retiredTraceControls(page);record('retired-layout-trace-control-absent',traces.length===0,traces);
  const relevantErrors=runtimeErrors.filter(e=>/diagnostic|passes[- _]?bcd|journal|continuous|syntaxerror|pmp-diagnostic-coverage-passes-bcd-v1-1-1-0/i.test(String(e.message||'')+' '+String(e.stack||'')));record('no-diagnostics-runtime-errors',relevantErrors.length===0,relevantErrors);
  if(results.some(x=>!x.pass))throw new Error('Whole App diagnostics certification failed');
}catch(error){fatalError=errorValue(error);console.error(error?.stack||error);process.exitCode=1}finally{try{if(browser)await browser.close()}catch(error){if(!fatalError)fatalError=errorValue(error);process.exitCode=1}try{writeOutput()}catch(error){console.error(error?.stack||error);process.exitCode=1}}})();
