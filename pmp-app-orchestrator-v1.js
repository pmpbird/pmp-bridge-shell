(()=>{
'use strict';
const V='2.6.0-fail-isolated-diagnostics-startup-20260730F',OWNER='app_orchestrator_owner';
const SOURCES={
 ownership:{name:'PMPAppOrchestratorOwnershipRuntimeV1',version:'1.0.0-exclusive-owner-runtime-20260727A',src:'pmp-app-orchestrator-ownership-runtime-v1.js?fresh=diagnostics-startup-20260730F'},
 bounded:{name:'PMPActivePathDiscoveryMachineV2',version:'2.2.0-bounded-support-no-v1-alias-20260727A',src:'pmp-active-path-discovery-machine-v2.js?fresh=diagnostics-startup-20260730F'},
 passA:{name:'PMPDiagnosticCoveragePassAV1',version:'1.0.0-pass-a-live-coverage-20260730A',src:'pmp-diagnostic-coverage-pass-a-v1.js?fresh=diagnostics-startup-20260730F'},
 bcd:{name:'PMPDiagnosticCoveragePassesBCDV1',version:'1.0.0-passes-bcd-live-coverage-20260730A',src:'pmp-diagnostic-coverage-passes-bcd-v1.js?fresh=diagnostics-startup-20260730F'},
 diagnostics:{name:'PMPDiagnosticsOwnerV1',version:'2.5.0-truth-confidence-20260729A',src:'pmp-diagnostics-owner-v1.js?fresh=diagnostics-startup-20260730F'},
 consolidated:{name:'PMPDiagnosticsConsolidatedViewV1',version:'2.3.0-native-live-receipts-20260730E',src:'pmp-diagnostics-consolidated-view-v1.js?fresh=diagnostics-startup-20260730F'},
 passE:{name:'PMPDiagnosticCoveragePassEV1',version:'1.0.0-cross-system-integration-20260730A',src:'pmp-diagnostic-coverage-pass-e-integration-v1.js?fresh=diagnostics-startup-20260730F'},
 handoff:{name:'PMPNewChatSafeHandoffV1',version:'2.0.0-full-diagnostics-continuation-20260730A',src:'pmp-new-chat-safe-handoff-v1.js?fresh=diagnostics-startup-20260730F'},
 passF:{name:'PMPDiagnosticCoveragePassFV1',version:'1.0.0-safe-handoff-final-certification-20260730A',src:'pmp-diagnostic-coverage-pass-f-handoff-certification-v1.js?fresh=diagnostics-startup-20260730F'},
 final:{name:'PMPDiagnosticCoverageFinalCertificationV1',version:'1.1.0-final-certification-through-pass-f-20260730A',src:'pmp-diagnostic-coverage-final-certification-v1.js?fresh=diagnostics-startup-20260730F'},
 tab:{name:'PMPDiagnosticsBottomTabForcerV1',version:'1.0.4-single-active-tab-state-20260709A',src:'pmp-diagnostics-bottom-tab-forcer-v1.js?fresh=diagnostics-startup-20260730F'}
};
const KEYS={receipt:'pmp_app_orchestrator_v1_receipt',status:'pmp_app_orchestrator_boot_status_v1',passA:'pmp_diagnostic_coverage_pass_a_v1_receipt',bcd:'pmp_diagnostic_coverage_passes_bcd_v1_receipt',errors:'pmp_app_orchestrator_activation_error_v1'};
let LAST=null,RUNNING=null,RUN_COUNT=0;
function T(){try{return window.top||window}catch(_){return window}}
function now(){return new Date().toISOString()}
function read(k){try{return JSON.parse(T().localStorage.getItem(k)||'null')}catch(_){return null}}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(_){}return v}
function lookup(name){try{return window[name]||T()[name]||null}catch(_){return window[name]||null}}
function version(name){const value=lookup(name);return value&&value.version||null}
function load(spec){return new Promise(resolve=>{try{const current=lookup(spec.name);if(current&&current.version===spec.version)return resolve({status:'already_current',version:current.version});const existing=Array.from(document.querySelectorAll('script[src]')).find(s=>String(s.src||'').includes(spec.src.split('?')[0]));if(existing&&current)return resolve({status:'already_loaded',version:current.version||null});const s=document.createElement('script');s.src=spec.src;s.async=false;s.onload=()=>resolve({status:lookup(spec.name)?'loaded':'loaded_api_missing',version:version(spec.name)});s.onerror=()=>resolve({status:'load_error',version:null});(document.head||document.documentElement).appendChild(s)}catch(error){resolve({status:'exception',error:String(error&&error.message||error),version:null})}})}
async function stage(id,fn){const started=now();try{const value=await fn();return{id,status:'PASS',started_at:started,finished_at:now(),value}}catch(error){return{id,status:'FAIL',started_at:started,finished_at:now(),error:String(error&&error.message||error)}}}
async function loadAndRun(spec,reason){const loaded=await load(spec);const api=lookup(spec.name);let result=null;if(api&&typeof api.run==='function')result=await api.run(reason);return{loaded,result,api_version:api&&api.version||null}}
async function produceCoverage(reason){const a=await stage('pass_a',()=>loadAndRun(SOURCES.passA,reason+'_pass_a'));const b=await stage('passes_bcd',()=>loadAndRun(SOURCES.bcd,reason+'_passes_bcd'));return{pass_a:a,passes_bcd:b,receipts:{pass_a:read(KEYS.passA),passes_bcd:read(KEYS.bcd)}}}
function currentReport(reason,stages){const a=read(KEYS.passA),b=read(KEYS.bcd);LAST={type:'PMP_APP_ORCHESTRATOR_V1_RECEIPT',version:V,owner:OWNER,writer:'pmp-app-orchestrator-v1.js',at:now(),reason:reason||'current_report',run_count:RUN_COUNT,status:a&&b?'CURRENT_DIAGNOSTIC_RECEIPTS_PUBLISHED':'DIAGNOSTIC_RECEIPTS_INCOMPLETE',stages:stages||[],diagnostic_coverage:{pass_a:{loaded_version:version(SOURCES.passA.name),receipt:a||{status:'MISSING'}},passes_bcd:{loaded_version:version(SOURCES.bcd.name),receipt:b||{status:'MISSING'}}},activation:{document_ready_state:document.readyState,fail_isolated:true,repeatable:true},boundaries:{read_only_diagnostics:true,owner_changes:false,helper_changes:false,route_changes:false,bank_rebuild:false,continuous_run_mutation:false,storage_migration:false,persisted_user_data_write:false}};put(KEYS.receipt,LAST);put(KEYS.status,{type:'PMP_APP_ORCHESTRATOR_CURRENT_STATUS_V1',version:V,at:LAST.at,status:LAST.status,run_count:RUN_COUNT,diagnostic_coverage:LAST.diagnostic_coverage});return LAST}
async function execute(reason){RUN_COUNT++;const stages=[];
stages.push(await stage('ownership_runtime',async()=>{const loaded=await load(SOURCES.ownership);const api=lookup(SOURCES.ownership.name);let result=null;if(api&&typeof api.load==='function')result=await api.load();return{loaded,result}}));
stages.push(await stage('bounded_active_path',()=>load(SOURCES.bounded)));
const coverage=await produceCoverage(reason||'orchestrator');stages.push(coverage.pass_a,coverage.passes_bcd);
stages.push(await stage('diagnostics_owner',()=>load(SOURCES.diagnostics)));
stages.push(await stage('consolidated_diagnostics',async()=>{const loaded=await load(SOURCES.consolidated);const api=lookup(SOURCES.consolidated.name);if(api&&typeof api.install==='function')api.install();return loaded}));
stages.push(await stage('pass_e',()=>loadAndRun(SOURCES.passE,(reason||'orchestrator')+'_pass_e')));
stages.push(await stage('safe_handoff',()=>load(SOURCES.handoff)));
stages.push(await stage('pass_f',()=>loadAndRun(SOURCES.passF,(reason||'orchestrator')+'_pass_f')));
stages.push(await stage('final_certification',()=>loadAndRun(SOURCES.final,(reason||'orchestrator')+'_final')));
stages.push(await stage('diagnostics_tab',()=>load(SOURCES.tab)));
const report=currentReport(reason||'api_run',stages);if(!report.diagnostic_coverage.pass_a.receipt||!report.diagnostic_coverage.passes_bcd.receipt)put(KEYS.errors,{type:'PMP_APP_ORCHESTRATOR_ACTIVATION_ERROR_V1',version:V,at:now(),reason,code:'DIAGNOSTIC_RECEIPTS_NOT_PUBLISHED',stages});return report}
function run(reason){if(RUNNING)return RUNNING;RUNNING=execute(reason).catch(error=>{put(KEYS.errors,{type:'PMP_APP_ORCHESTRATOR_ACTIVATION_ERROR_V1',version:V,at:now(),reason:reason||'run',error:String(error&&error.message||error)});return currentReport('execute_error',[{id:'execute',status:'FAIL',error:String(error&&error.message||error)}])}).finally(()=>{RUNNING=null});return RUNNING}
function schedule(reason){setTimeout(()=>run(reason),0)}
const api={version:V,owner:OWNER,run,produceCoverage,currentReport,getLastReceipt:()=>LAST||currentReport('get_last_receipt'),rule:'Fail-isolated, repeatable, read-only diagnostics startup. No failed optional stage may prevent Pass A or Passes B-D receipt publication.'};
window.PMPAppOrchestratorV1=api;try{T().PMPAppOrchestratorV1=api}catch(_){}
currentReport('boot');schedule('immediate_script_activation');
if(document.readyState==='loading')window.addEventListener('DOMContentLoaded',()=>schedule('dom_content_loaded'),{once:true});
window.addEventListener('load',()=>schedule('window_load'),{once:true});
window.addEventListener('pageshow',()=>schedule('pageshow'));
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')schedule('visibility_resume')});
[700,1800,4000,8000,12000].forEach(delay=>setTimeout(()=>run('bounded_activation_'+delay),delay));
try{const observer=new MutationObserver(records=>{if(records.some(r=>Array.from(r.addedNodes||[]).some(n=>n&&n.tagName&&/^(IFRAME|FRAME)$/i.test(n.tagName))))schedule('frame_added')});observer.observe(document.documentElement,{childList:true,subtree:true})}catch(_){}
})();