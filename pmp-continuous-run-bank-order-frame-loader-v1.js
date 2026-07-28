(()=>{
'use strict';
const V='3.0.0-single-owner-frame-event-driven-20260727A';
const OWNER='app_orchestrator_owner';
const RECEIPT='pmp_continuous_run_bank_order_frame_loader_v1_receipt';
const TRACE='pmp_pass7_startup_execution_audit_trace_v1';
const SCRIPTS=[
  {id:'pmpSafeAreaSurfaceFillV1DirectFrame',src:'pmp-safe-area-surface-fill-v1.js',fresh:'ownership-safe-area-20260727A',role:'presentation_local'},
  {id:'pmpBankZeroLoadingFlashGuardV1DirectFrame',src:'pmp-bank-zero-loading-flash-guard-v1.js',fresh:'ownership-css-only-20260727A',role:'presentation_local'},
  {id:'pmpPassRevalidationGate001V1DirectFrame',src:'pmp-pass-revalidation-gate-001-v1.js',fresh:'ownership-single-frame-20260727A',role:'stateful_owner_frame'},
  {id:'pmpSectionOwnerRegistryV1DirectFrame',src:'pmp-section-owner-registry-v1.js',fresh:'ownership-single-frame-20260727A',role:'stateful_owner_frame'},
  {id:'pmpOwnerDiagnosticsHostV1DirectFrame',src:'pmp-owner-diagnostics-host-v1.js',fresh:'ownership-single-frame-20260727A',role:'diagnostic_host'},
  {id:'pmpOwnerDiagnosticsFoundationV1DirectFrame',src:'pmp-owner-diagnostics-foundation-v1.js',fresh:'ownership-readonly-20260727A',role:'read_only_diagnostic'},
  {id:'pmpPass75RuntimePlatformV1DirectFrame',src:'pmp-pass75-runtime-platform-v1.js',fresh:'ownership-single-frame-20260727A',role:'stateful_owner_frame'},
  {id:'pmpHelperRegistryV1DirectFrame',src:'pmp-helper-registry-v1.js',fresh:'ownership-single-frame-20260727A',role:'stateful_owner_frame'},
  {id:'pmpPass7RegistryRuntimeProbeV1DirectFrame',src:'pmp-pass7-registry-runtime-probe-v1.js',fresh:'ownership-single-frame-20260727A',role:'read_only_probe'},
  {id:'pmpUniversalGrowthAwarenessV1DirectFrame',src:'pmp-universal-growth-awareness-v1.js',fresh:'ownership-single-frame-20260727A',role:'read_only_growth'},
  {id:'pmpPass7CoverageLockV1DirectFrame',src:'pmp-pass7-coverage-lock-v1.js',fresh:'ownership-single-frame-20260727A',role:'stateful_owner_frame'},
  {id:'pmpPass7CertificationGateV1DirectFrame',src:'pmp-pass7-certification-gate-v1.js',fresh:'ownership-single-frame-20260727A',role:'stateful_owner_frame'}
];
function now(){return new Date().toISOString()}
function read(k){try{return JSON.parse(localStorage.getItem(k)||'null')}catch(e){return null}}
function put(k,v){try{localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function trace(event,data){
  const value=read(TRACE)||{type:'PMP_PASS7_STARTUP_EXECUTION_AUDIT_TRACE_V1',version:V,owner:OWNER,created_at:now(),events:[]};
  value.version=V;value.updated_at=now();value.events=(value.events||[]).concat([Object.assign({at:now(),event},data||{})]).slice(-160);
  return put(TRACE,value);
}
function injectOne(def){
  if(document.getElementById(def.id)){trace('script_existing',{id:def.id,src:def.src,role:def.role});return'present'}
  const script=document.createElement('script');script.id=def.id;script.src=def.src+'?fresh='+def.fresh;
  script.onload=()=>trace('script_loaded',{id:def.id,src:def.src,role:def.role});
  script.onerror=()=>trace('script_load_error',{id:def.id,src:def.src,role:def.role});
  (document.body||document.documentElement).appendChild(script);
  trace('script_injected',{id:def.id,src:def.src,role:def.role});
  return'injected';
}
function status(){
  return{
    section_owner_global:!!window.PMPSectionOwnerRegistryV1,
    helper_registry_global:!!window.PMPHelperRegistryV1,
    registry_runtime_probe_global:!!window.PMPPass7RegistryRuntimeProbeV1,
    pass75_runtime_platform_global:!!window.PMPPass75RuntimePlatformV1,
    section_owner_snapshot_present:!!read('pmp_section_owner_registry_snapshot_v1'),
    helper_snapshot_present:!!read('pmp_helper_registry_snapshot_v1'),
    coverage_receipt_present:!!read('pmp_pass7_coverage_lock_receipt_v1'),
    certification_receipt_present:!!read('pmp_pass7_certification_gate_v1_receipt')
  };
}
function scan(reason){
  const outcomes=SCRIPTS.map(def=>({id:def.id,src:def.src,role:def.role,result:injectOne(def)}));
  const receipt={type:'PMP_CONTINUOUS_RUN_BANK_ORDER_FRAME_LOADER_V3',version:V,owner:OWNER,at:now(),reason:reason||'scan',mode:'EVENT_DRIVEN_NEW_DOCUMENT_ONCE_SINGLE_OWNER_FRAME',frame_path:String(location.pathname||''),documents_seen:1,child_frames_injected:0,scripts:SCRIPTS.map(x=>x.src),outcomes,status:status(),side_effects:{route_change_attempted:false,indexeddb_write_attempted:false,bank_rebuild_attempted:false,storage_migration_attempted:false,section_takeover_attempted:false,helper_takeover_attempted:false,child_frame_stateful_injection_attempted:false,stale_script_removal_attempted:false,recurring_scan_attempted:false,bank_owner_duplicate_injection_attempted:false}};
  put(RECEIPT,receipt);trace('loader_scan_complete',{reason:reason||'scan',documents_seen:1,child_frames_injected:0});return receipt;
}
window.PMPContinuousRunBankOrderFrameLoaderV1={version:V,owner:OWNER,scan,scriptStatus:status,rule:'Initializes the named App Orchestrator owner frame once. Never injects stateful owners into child frames, replaces scripts, or scans on a timer.'};
window.addEventListener('load',()=>scan('window_load'),{once:true});scan('initial');
})();
