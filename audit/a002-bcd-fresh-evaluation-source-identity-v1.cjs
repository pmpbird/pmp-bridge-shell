'use strict';
const fs = require('fs');
const { chromium } = require('playwright');

const BASE = process.env.A002_BASE_URL || 'http://127.0.0.1:8000/';
const RESULT_PATH = process.env.A002_BCD_FRESHNESS_RESULT_PATH || 'a002-bcd-fresh-evaluation-results.json';
const CURRENT = 'pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html';
const INNER = 'pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html';
const BOOT_VERSION = '3.4.0-fresh-evaluation-source-identity-20260825A';
const BCD_VERSION = '1.1.0-final-two-live-proof-20260801A';
const BCD_REVISION = '1.4.0-fresh-evaluation-source-identity-20260825A';
const BCD_SOURCE = 'pmp-diagnostic-coverage-passes-bcd-v1-1-1-0-fresh-evaluation-20260825A.js';
const VIEW_VERSION = '2.9.2-fresh-bcd-evaluation-binding-20260825A';
const results = [];
const runtimeErrors = [];
let fatalError = null;

function errorValue(error) { return {name:String(error?.name||'Error'),message:String(error?.message||error),stack:String(error?.stack||'')}; }
function record(name, pass, detail={}) { results.push({name,pass:!!pass,detail,at:new Date().toISOString()}); console.log(`${pass?'PASS':'FAIL'} ${name} ${JSON.stringify(detail)}`); }
function writeOutput() {
  const output = {type:'PMP_A002_BCD_FRESH_EVALUATION_SOURCE_IDENTITY_V1',generated_at:new Date().toISOString(),base_url:BASE,
    tests_total:results.length,tests_passed:results.filter(x=>x.pass).length,tests_failed:results.filter(x=>!x.pass).length,
    runtime_errors:runtimeErrors,fatal_error:fatalError,results};
  fs.writeFileSync(RESULT_PATH, JSON.stringify(output,null,2));
  console.log(`A002_BCD_FRESHNESS_RESULT_WRITTEN ${RESULT_PATH} ${JSON.stringify({tests_total:output.tests_total,tests_passed:output.tests_passed,tests_failed:output.tests_failed,runtime_errors:runtimeErrors.length})}`);
}
async function waitForFrame(page, pattern, timeout=65000) {
  const deadline=Date.now()+timeout;
  while(Date.now()<deadline) {
    const frame=page.frames().find(f=>pattern.test(f.url()));
    if(frame) return frame;
    await page.waitForTimeout(250);
  }
  throw new Error(`frame not found: ${pattern}`);
}
async function waitForApiFrame(page, name, timeout=65000) {
  const deadline=Date.now()+timeout;
  while(Date.now()<deadline) {
    for(const frame of page.frames()) {
      try { if(await frame.evaluate(n=>!!(window[n]&&typeof window[n].run==='function'),name)) return frame; } catch {}
    }
    await page.waitForTimeout(250);
  }
  throw new Error(`API frame not found: ${name}`);
}
async function waitForScreenFrame(page, timeout=65000) {
  const deadline=Date.now()+timeout;
  while(Date.now()<deadline) {
    for(const frame of page.frames()) {
      try { if(await frame.evaluate(()=>!!document.getElementById('pmpDiagnosticsScreenV1'))) return frame; } catch {}
    }
    await page.waitForTimeout(250);
  }
  throw new Error('Diagnostics screen frame not found');
}
async function enterCurrentApp(page) {
  await page.goto(BASE+'pmp-app-current.html#control',{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>{try{return JSON.parse(localStorage.getItem('pmp_a003_bootstrap_receipt_v1')||'null')?.status==='PASS'}catch{return false}},null,{timeout:40000});
  const guardian=await waitForFrame(page,/pmp-route-guardian-current-loader-v22\.html/,40000);
  await guardian.click('#openBtn',{force:true});
  await page.waitForURL(url=>url.pathname.endsWith('/'+CURRENT)&&url.hash==='#control',{timeout:40000});
  const runButton=page.locator('#pmpPass75ReloadRuntimePlatformGateV1 [data-run="1"]');
  await runButton.waitFor({state:'visible',timeout:30000});
  await runButton.click({force:true});
  await page.waitForFunction(()=>{try{return JSON.parse(localStorage.getItem('pmp_pass75_reload_runtime_platform_gate_v1_receipt')||'null')?.released===true}catch{return false}},null,{timeout:15000});
  await waitForFrame(page,new RegExp(INNER.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')),65000);
  await page.waitForTimeout(7000);
}
async function locateView(frame) {
  return frame.evaluate(()=>{
    const seen=new Set(),wins=[];
    function add(w){try{if(w&&w.document&&!seen.has(w)){seen.add(w);wins.push(w);w.document.querySelectorAll('iframe,frame').forEach(f=>{try{add(f.contentWindow)}catch{}})}}catch{}}
    let top=window;try{top=window.top||window}catch{}
    add(top);add(window);
    const api=wins.map(w=>{try{return w.PMPDiagnosticsConsolidatedViewV1}catch{return null}}).find(Boolean);
    return api?{version:api.version||null}:null;
  });
}

(async()=>{ let browser=null; try {
  browser=await chromium.launch({headless:true});
  const context=await browser.newContext({serviceWorkers:'allow'});
  const page=await context.newPage();
  page.setDefaultTimeout(50000);
  page.on('pageerror',e=>runtimeErrors.push({type:'pageerror',...errorValue(e)}));
  page.on('console',m=>{if(m.type()==='error')runtimeErrors.push({type:'console',message:m.text()})});
  await enterCurrentApp(page);
  const apiFrame=await waitForApiFrame(page,'PMPCurrentBCDDiagnosticsBootstrapV1');
  const screenFrame=await waitForScreenFrame(page);
  const viewInfo=await locateView(screenFrame);
  record('current-view-loaded',viewInfo?.version===VIEW_VERSION,{observed:viewInfo?.version||null,required:VIEW_VERSION});

  const setup=await apiFrame.evaluate(({bootVersion,bcdVersion,bcdRevision,bcdSource})=>{
    const boot=window.PMPCurrentBCDDiagnosticsBootstrapV1;
    const before=boot.currentReceipt&&boot.currentReceipt();
    const storage=window.top.localStorage;
    const key='pmp_diagnostic_coverage_passes_bcd_v1_receipt';
    const stale={type:'PMP_DIAGNOSTIC_COVERAGE_PASSES_BCD_V1',version:bcdVersion,revision:'1.2.0-accessible-runtime-context-20260803G',
      source_identity:'pmp-diagnostic-coverage-passes-bcd-v1-1-1-0.js',evaluation_id:'stale-boot-0',owner:'diagnostics_owner',
      at:'2026-08-25T03:04:32.428Z',reason:'boot_0',status:'FAIL',
      bridge_system:{type:'PMP_BRIDGE_LIVE_DIAGNOSTIC_V1',status:'FAIL',checks:{accessible_document_count:3,diagnostics_active:false},issues:[{code:'BRIDGE_TAB_NOT_FOUND'}]},
      library_system:{type:'PMP_LIBRARY_LIVE_DIAGNOSTIC_V1',status:'FAIL',checks:{accessible_document_count:3,diagnostics_active:false},issues:[{code:'LIBRARY_TAB_NOT_FOUND'}]},
      bank_system:{type:'PMP_BANK_LIVE_DIAGNOSTIC_V1',status:'FAIL',checks:{accessible_document_count:3,diagnostics_active:false},issues:[{code:'BANK_TAB_NOT_FOUND'}]},
      continuous_run_system:{type:'PMP_CONTINUOUS_RUN_LIVE_DIAGNOSTIC_V1',status:'PASS',checks:{},issues:[]},
      errors_bug_watch_visual_stability:{type:'PMP_ERRORS_VISUAL_LIVE_DIAGNOSTIC_V1',status:'PASS',checks:{},issues:[]},
      boundaries:{read_only:true}};
    try{storage.setItem(key,JSON.stringify(stale))}catch{}
    const proto=Object.getPrototypeOf(storage),original=proto.setItem;
    const wrapped=function(k,v){if(this===storage&&String(k)===key){const error=new Error('The quota has been exceeded.');error.name='QuotaExceededError';throw error}return original.call(this,k,v)};
    Object.defineProperty(proto,'setItem',{value:wrapped,writable:true,configurable:true});
    window.__restoreBcdSetItem=()=>Object.defineProperty(proto,'setItem',{value:original,writable:true,configurable:true});
    return {bootVersion:boot.version||null,requiredRevision:boot.requiredRevision||null,requiredSourceIdentity:boot.requiredSourceIdentity||null,
      beforeEvaluationId:before&&before.evaluation_id||null,staleEvaluationId:stale.evaluation_id,bcdRevision,bcdSource};
  },{bootVersion:BOOT_VERSION,bcdVersion:BCD_VERSION,bcdRevision:BCD_REVISION,bcdSource:BCD_SOURCE});
  record('bootstrap-exact-source-contract',setup.bootVersion===BOOT_VERSION&&setup.requiredRevision===BCD_REVISION&&setup.requiredSourceIdentity===BCD_SOURCE,setup);

  await screenFrame.evaluate(()=>{
    const seen=new Set(),wins=[];
    function add(w){try{if(w&&w.document&&!seen.has(w)){seen.add(w);wins.push(w);w.document.querySelectorAll('iframe,frame').forEach(f=>{try{add(f.contentWindow)}catch{}})}}catch{}}
    let top=window;try{top=window.top||window}catch{}
    add(top);add(window);
    const api=wins.map(w=>{try{return w.PMPDiagnosticsConsolidatedViewV1}catch{return null}}).find(Boolean);
    if(!api)throw new Error('Consolidated view API missing');
    api.renderHome(window,document);
    const card=document.querySelector('[data-diag-consolidated="whole_app"]');
    if(!card)throw new Error('Whole App Health card missing');
    card.click();
  });
  await screenFrame.locator('#pmpDiagCopyWhole').waitFor({state:'visible',timeout:50000});
  const openState=await screenFrame.evaluate(()=>{
    const api=window.top.PMPDiagnosticsConsolidatedViewV1||window.PMPDiagnosticsConsolidatedViewV1;
    return {state:api.evidenceState(),receipt:api.fullDiagnosticReport().live_receipts.passes_bcd};
  });
  await screenFrame.click('#pmpDiagCopyWhole',{force:true});
  await screenFrame.waitForFunction(()=>{
    const b=document.getElementById('pmpDiagCopyWhole');
    return !!b&&!b.disabled&&!/Running current live diagnostics/i.test(b.textContent||'');
  },null,{timeout:50000});
  const finalState=await screenFrame.evaluate(()=>{
    const api=window.top.PMPDiagnosticsConsolidatedViewV1||window.PMPDiagnosticsConsolidatedViewV1;
    const full=api.fullDiagnosticReport(),receipt=full.live_receipts.passes_bcd;
    return {state:api.evidenceState(),receipt,whole:api.wholeAppHealth(),full};
  });
  const bootReceipt=await apiFrame.evaluate(()=>{try{return JSON.parse(window.top.localStorage.getItem('pmp_current_bcd_diagnostics_bootstrap_v1_receipt')||'null')}catch{return null}});
  await apiFrame.evaluate(()=>{try{window.__restoreBcdSetItem&&window.__restoreBcdSetItem()}catch{}});

  const openId=openState.receipt?.evaluation_id||null,finalId=finalState.receipt?.evaluation_id||null;
  record('whole-app-open-replaces-prior-evidence',!!openId&&openId!==setup.beforeEvaluationId&&openId!==setup.staleEvaluationId,
    {before:setup.beforeEvaluationId,stale:setup.staleEvaluationId,open:openId,reason:openState.receipt?.reason});
  record('copy-button-produces-new-bound-evaluation',finalState.state?.status==='COMPLETE'&&finalState.state?.fresh_evaluation_bound===true&&
    !!finalId&&finalId!==openId&&finalState.state?.observed_evaluation_id===finalId&&finalState.state?.requested_evaluation_id===finalId,
    {open:openId,final:finalId,state:finalState.state});
  record('exact-revision-and-source-preserved',finalState.receipt?.version===BCD_VERSION&&finalState.receipt?.revision===BCD_REVISION&&
    finalState.receipt?.source_identity===BCD_SOURCE,{version:finalState.receipt?.version,revision:finalState.receipt?.revision,source:finalState.receipt?.source_identity});
  const ctx=finalState.receipt?.runtime_context||{},docs=Array.isArray(ctx.accessible_documents)?ctx.accessible_documents:[];
  record('settled-runtime-context-observed',ctx.diagnostics_active===true&&docs.length>=6,{diagnostics_active:ctx.diagnostics_active,documents:docs});
  const bridge=finalState.receipt?.bridge_system,library=finalState.receipt?.library_system,bank=finalState.receipt?.bank_system;
  record('bridge-library-bank-first-open-pass',[bridge,library,bank].every(x=>x?.status==='PASS')&&
    [bridge,library,bank].every(x=>x?.checks?.surface_validation==='DEFERRED_WHILE_DIAGNOSTICS_ACTIVE'),
    {bridge,library,bank});
  record('quota-path-keeps-current-evaluation',bootReceipt?.status==='PASS'&&bootReceipt?.evaluation_id===finalId&&
    bootReceipt?.publication_persistence_status==='QUOTA_UNAVAILABLE'&&bootReceipt?.observed_receipt_evaluation_id===finalId,
    {bootReceipt});
  const relevantErrors=runtimeErrors.filter(e=>/diagnostic|passes[- _]?bcd|journal|syntaxerror|fresh evaluation/i.test(String(e.message||'')+' '+String(e.stack||'')));
  record('no-current-diagnostics-runtime-errors',relevantErrors.length===0,relevantErrors);
  if(results.some(x=>!x.pass))throw new Error('B-D fresh evaluation/source identity certification failed');
} catch(error) {
  fatalError=errorValue(error); console.error(error?.stack||error); process.exitCode=1;
} finally {
  try{if(browser)await browser.close()}catch(error){if(!fatalError)fatalError=errorValue(error);process.exitCode=1}
  try{writeOutput()}catch(error){console.error(error?.stack||error);process.exitCode=1}
} })();
