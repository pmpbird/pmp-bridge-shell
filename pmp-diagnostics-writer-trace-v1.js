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
const V='3.1.0-retired-trace-current-bcd-bootstrap-20260801A';
const BUTTON_ID='pmpWholeAppHealthLayoutTraceV1';
const BCD_API='PMPDiagnosticCoveragePassesBCDV1';
const REQUIRED_BCD_VERSION='1.1.0-final-two-live-proof-20260801A';
const BCD_RECEIPT_KEY='pmp_diagnostic_coverage_passes_bcd_v1_receipt';
const BOOT_RECEIPT_KEY='pmp_current_bcd_diagnostics_bootstrap_v1_receipt';
let inflight=null;
function T(){try{return window.top||window}catch(_){return window}}
function now(){return new Date().toISOString()}
function store(key,value){try{T().localStorage.setItem(key,JSON.stringify(value,null,2))}catch(_){}return value}
function read(key){try{return JSON.parse(T().localStorage.getItem(key)||'null')}catch(_){return null}}
function removeRetiredControl(doc){
  try{
    const d=doc||document;
    d.querySelectorAll('#'+BUTTON_ID+', [data-pmp-whole-app-health-layout-trace]').forEach(node=>node.remove());
  }catch(_){ }
}
function walk(win,depth,seen){
  if(!win||depth>10||seen.has(win))return;
  seen.add(win);
  try{
    removeRetiredControl(win.document);
    win.document.querySelectorAll('iframe,frame').forEach(frame=>{
      try{walk(frame.contentWindow,depth+1,seen)}catch(_){ }
    });
  }catch(_){ }
}
function retire(){walk(T(),0,new Set())}
function currentApi(){
  try{if(T()[BCD_API])return T()[BCD_API]}catch(_){}
  try{if(window[BCD_API])return window[BCD_API]}catch(_){}
  return null;
}
function receipt(reason,status,extra){
  return store(BOOT_RECEIPT_KEY,Object.assign({
    type:'PMP_CURRENT_BCD_DIAGNOSTICS_BOOTSTRAP_V1',
    version:V,
    owner:'diagnostics_owner',
    at:now(),
    reason:reason||'boot',
    status,
    required_version:REQUIRED_BCD_VERSION,
    observed_api_version:currentApi()&&currentApi().version||null,
    observed_receipt_version:read(BCD_RECEIPT_KEY)&&read(BCD_RECEIPT_KEY).version||null,
    boundaries:{trace_ui:'retired',owner_changes:false,helper_changes:false,route_changes:false,storage_migration:false,persisted_user_data_write:false}
  },extra||{}));
}
function loadCurrentScript(){
  return new Promise(resolve=>{
    try{
      const d=document,s=d.createElement('script');
      s.async=false;
      s.src='pmp-diagnostic-coverage-passes-bcd-v1.js?fresh=current-bcd-bootstrap-20260801A-'+Date.now();
      s.onload=()=>resolve({status:'LOADED'});
      s.onerror=()=>resolve({status:'LOAD_ERROR'});
      (d.head||d.documentElement).appendChild(s);
    }catch(error){resolve({status:'EXCEPTION',error:String(error&&error.message||error)})}
  });
}
async function ensureCurrent(reason){
  retire();
  if(inflight)return inflight;
  inflight=(async()=>{
    let api=currentApi();
    if(api&&api.version===REQUIRED_BCD_VERSION){
      try{if(typeof api.run==='function')await api.run(reason||'current_bcd_bootstrap_existing')}catch(error){return receipt(reason,'RUN_ERROR',{error:String(error&&error.message||error)})}
      const r=read(BCD_RECEIPT_KEY);
      return receipt(reason,r&&r.version===REQUIRED_BCD_VERSION?'PASS':'RECEIPT_VERSION_MISMATCH');
    }
    try{T().localStorage.removeItem(BCD_RECEIPT_KEY)}catch(_){}
    const loaded=await loadCurrentScript();
    if(loaded.status!=='LOADED')return receipt(reason,'LOAD_FAILED',loaded);
    api=currentApi();
    if(!api||api.version!==REQUIRED_BCD_VERSION)return receipt(reason,'API_VERSION_MISMATCH');
    try{if(typeof api.run==='function')await api.run(reason||'current_bcd_bootstrap_loaded')}catch(error){return receipt(reason,'RUN_ERROR',{error:String(error&&error.message||error)})}
    const r=read(BCD_RECEIPT_KEY);
    return receipt(reason,r&&r.version===REQUIRED_BCD_VERSION?'PASS':'RECEIPT_VERSION_MISMATCH');
  })().finally(()=>{inflight=null});
  return inflight;
}
window.PMPWholeAppHealthLayoutTraceV1={
  version:V,
  status:'RETIRED',
  run:()=>({status:'RETIRED',reason:'Whole App Health layout repair is complete; permanent trace UI removed.'}),
  rule:'Compatibility bootstrap only. Creates no trace controls or observers; enforces the current Passes B-D diagnostics version.'
};
window.PMPCurrentBCDDiagnosticsBootstrapV1={version:V,requiredVersion:REQUIRED_BCD_VERSION,run:ensureCurrent,last:()=>read(BOOT_RECEIPT_KEY)};
try{T().PMPWholeAppHealthLayoutTraceV1=window.PMPWholeAppHealthLayoutTraceV1;T().PMPCurrentBCDDiagnosticsBootstrapV1=window.PMPCurrentBCDDiagnosticsBootstrapV1}catch(_){}
retire();
[0,500,1500,3500,7000].forEach(ms=>setTimeout(()=>ensureCurrent('boot_'+ms),ms));
window.addEventListener('pageshow',()=>ensureCurrent('pageshow'));
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')ensureCurrent('visible_resume')});
})();
