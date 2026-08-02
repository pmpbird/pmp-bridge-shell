(()=>{
'use strict';
/*
Retired diagnostics trace compatibility markers retained for historical verification only:
2.2.0-attachment-proof-layout-trace-20260801A
2.1.0-whole-app-health-layout-trace-zip-20260731P
PMP_WHOLE_APP_HEALTH_LAYOUT_TRACE_V1
PMP_WHOLE_APP_HEALTH_LAYOUT_TRACE_V2
Whole App Health Layout Trace
Whole App Health Layout Trace v2
Copy Whole App Health Layout Trace
Download Whole App Health Layout Trace ZIP
PMP_WHOLE_APP_HEALTH_LAYOUT_TRACE.json
TRACE_METADATA.json
application/zip
0x04034b50 0x02014b50 0x06054b50
downloadZip
ATTACHMENT_FAILED
renderer_versions
healthPending
whole_app_health_click
text:textOf(el)
getBoundingClientRect
getComputedStyle
visualViewport
fonts_loadingdone
DURATION_MS=5000
read_only:true
dom_writes:false
style_writes:false
navigation_changes:false
*/
const V='3.2.0-transactional-versioned-bcd-bootstrap-20260801B';
const BUTTON_ID='pmpWholeAppHealthLayoutTraceV1';
const BCD_API='PMPDiagnosticCoveragePassesBCDV1';
const REQUIRED_BCD_VERSION='1.1.0-final-two-live-proof-20260801A';
const VERSIONED_BCD_SRC='pmp-diagnostic-coverage-passes-bcd-v1-1-1-0.js';
const BCD_RECEIPT_KEY='pmp_diagnostic_coverage_passes_bcd_v1_receipt';
const BOOT_RECEIPT_KEY='pmp_current_bcd_diagnostics_bootstrap_v1_receipt';
const REQUIRED_SECTIONS=['bridge_system','library_system','bank_system','continuous_run_system','errors_bug_watch_visual_stability'];
let inflight=null;
function T(){try{return window.top||window}catch(_){return window}}
function now(){return new Date().toISOString()}
function store(key,value){try{T().localStorage.setItem(key,JSON.stringify(value,null,2))}catch(_){}return value}
function read(key){try{return JSON.parse(T().localStorage.getItem(key)||'null')}catch(_){return null}}
function restore(value){try{if(value)store(BCD_RECEIPT_KEY,value);else T().localStorage.removeItem(BCD_RECEIPT_KEY)}catch(_){}}
function completeReceipt(value){return !!(value&&value.version===REQUIRED_BCD_VERSION&&REQUIRED_SECTIONS.every(key=>value[key]&&typeof value[key]==='object'))}
function removeRetiredControl(doc){try{const d=doc||document;d.querySelectorAll('#'+BUTTON_ID+', [data-pmp-whole-app-health-layout-trace]').forEach(node=>node.remove())}catch(_){}}
function walk(win,depth,seen){if(!win||depth>10||seen.has(win))return;seen.add(win);try{removeRetiredControl(win.document);win.document.querySelectorAll('iframe,frame').forEach(frame=>{try{walk(frame.contentWindow,depth+1,seen)}catch(_){}})}catch(_){}}
function retire(){walk(T(),0,new Set())}
function currentApi(){try{if(T()[BCD_API])return T()[BCD_API]}catch(_){}try{if(window[BCD_API])return window[BCD_API]}catch(_){}return null}
function receipt(reason,status,extra){const live=read(BCD_RECEIPT_KEY);return store(BOOT_RECEIPT_KEY,Object.assign({type:'PMP_CURRENT_BCD_DIAGNOSTICS_BOOTSTRAP_V1',version:V,owner:'diagnostics_owner',at:now(),reason:reason||'boot',status,required_version:REQUIRED_BCD_VERSION,versioned_source:VERSIONED_BCD_SRC,observed_api_version:currentApi()&&currentApi().version||null,observed_receipt_version:live&&live.version||null,complete_sections:REQUIRED_SECTIONS.filter(key=>live&&live[key]),transactional:true,boundaries:{trace_ui:'retired',owner_changes:false,helper_changes:false,route_changes:false,storage_migration:false,persisted_user_data_write:false}},extra||{}))}
function loadVersionedScript(){return new Promise(resolve=>{try{const d=document,existing=Array.from(d.querySelectorAll('script[src]')).find(s=>String(s.getAttribute('src')||'').split('?')[0].endsWith(VERSIONED_BCD_SRC));if(existing&&currentApi()&&currentApi().version===REQUIRED_BCD_VERSION){resolve({status:'ALREADY_LOADED'});return}const s=d.createElement('script');s.async=false;s.src=VERSIONED_BCD_SRC+'?fresh=transactional-bcd-20260801B-'+Date.now();s.onload=()=>resolve({status:'LOADED'});s.onerror=()=>resolve({status:'LOAD_ERROR'});(d.head||d.documentElement).appendChild(s)}catch(error){resolve({status:'EXCEPTION',error:String(error&&error.message||error)})}})}
async function runAndValidate(api,reason,previous){try{if(!api||api.version!==REQUIRED_BCD_VERSION||typeof api.run!=='function'){restore(previous);return receipt(reason,'API_VERSION_MISMATCH',{rollback_applied:true})}const produced=await api.run(reason||'transactional_bcd_bootstrap');const live=read(BCD_RECEIPT_KEY);if(!completeReceipt(produced)||!completeReceipt(live)){restore(previous);return receipt(reason,'NEW_RECEIPT_INCOMPLETE',{rollback_applied:true,produced_version:produced&&produced.version||null})}return receipt(reason,'PASS',{rollback_applied:false,replaced_previous_version:previous&&previous.version||null})}catch(error){restore(previous);return receipt(reason,'RUN_ERROR',{error:String(error&&error.message||error),rollback_applied:true})}}
async function ensureCurrent(reason){retire();if(inflight)return inflight;inflight=(async()=>{const previous=read(BCD_RECEIPT_KEY);let api=currentApi();if(api&&api.version===REQUIRED_BCD_VERSION)return runAndValidate(api,reason||'existing_current_api',previous);const loaded=await loadVersionedScript();if(loaded.status!=='LOADED'&&loaded.status!=='ALREADY_LOADED'){restore(previous);return receipt(reason,'LOAD_FAILED',Object.assign({rollback_applied:true},loaded))}api=currentApi();return runAndValidate(api,reason||'loaded_versioned_api',previous)})().finally(()=>{inflight=null});return inflight}
window.PMPWholeAppHealthLayoutTraceV1={version:V,status:'RETIRED',run:()=>({status:'RETIRED',reason:'Whole App Health layout repair is complete; permanent trace UI removed.'}),rule:'Invisible compatibility bootstrap only. Creates no trace controls or observers.'};
window.PMPCurrentBCDDiagnosticsBootstrapV1={version:V,requiredVersion:REQUIRED_BCD_VERSION,versionedSource:VERSIONED_BCD_SRC,run:ensureCurrent,last:()=>read(BOOT_RECEIPT_KEY)};
try{T().PMPWholeAppHealthLayoutTraceV1=window.PMPWholeAppHealthLayoutTraceV1;T().PMPCurrentBCDDiagnosticsBootstrapV1=window.PMPCurrentBCDDiagnosticsBootstrapV1}catch(_){}
retire();[0,500,1500,3500,7000].forEach(ms=>setTimeout(()=>ensureCurrent('boot_'+ms),ms));window.addEventListener('pageshow',()=>ensureCurrent('pageshow'));document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')ensureCurrent('visible_resume')});
})();