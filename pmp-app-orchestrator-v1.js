(()=>{
'use strict';
const V='2.2.0-diagnostics-consolidated-view-loader-20260729A';
const OWNER='app_orchestrator_owner';
const DIAGNOSTICS_VERSION='2.5.0-truth-confidence-20260729A';
const DIAGNOSTICS_SRC='pmp-diagnostics-owner-v1.js?fresh=truth-confidence-20260729A';
const DIAGNOSTICS_TAB_SRC='pmp-diagnostics-bottom-tab-forcer-v1.js?fresh=one-button-handoff-entry-20260727A';
const DIAGNOSTICS_CONSOLIDATED_VERSION='1.0.0-whole-app-orchestrator-system-20260729A';
const DIAGNOSTICS_CONSOLIDATED_SRC='pmp-diagnostics-consolidated-view-v1.js?fresh=whole-app-orchestrator-system-20260729A';
const BOUNDED_DISCOVERY_SRC='pmp-active-path-discovery-machine-v2.js?fresh=bounded-support-no-v1-alias-20260727A';
const OWNERSHIP_RUNTIME_VERSION='1.0.0-exclusive-owner-runtime-20260727A';
const OWNERSHIP_RUNTIME_SRC='pmp-app-orchestrator-ownership-runtime-v1.js?fresh=ownership-runtime-loader-20260729A';
const KEYS={
  receipt:'pmp_app_orchestrator_v1_receipt',
  status:'pmp_app_orchestrator_boot_status_v1',
  diagnosticsOwner:'pmp_diagnostics_owner_v1_receipt',
  ownershipRuntime:'pmp_app_orchestrator_ownership_runtime_v1_receipt',
  handoff:'pmp_new_chat_safe_handoff_v1_receipt'
};
const EXPECTED={map:'pmp-current-map-v12.json',guardian:'pmp-route-guardian-current-loader-v22.html',current:'pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html',inner:'pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html'};
let LAST=null;
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function read(k){try{return JSON.parse(T().localStorage.getItem(k)||'null')}catch(e){return null}}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function hasScript(path){try{return Array.from(document.querySelectorAll('script[src]')).some(s=>String(s.getAttribute('src')||'').includes(path))}catch(e){return false}}
function load(path,src,apiName,reason,expectedVersion){
  return new Promise(resolve=>{
    try{
      const api=window[apiName]||T()[apiName];
      const versionMatches=!expectedVersion||(api&&api.version===expectedVersion);
      if(api&&versionMatches){resolve('already_present_current');return}
      if(api&&expectedVersion&&api.version!==expectedVersion){
        const script=document.createElement('script');script.src=src;script.async=true;
        script.onload=()=>{try{const loaded=window[apiName]||T()[apiName];if(loaded&&typeof loaded.run==='function')loaded.run(reason||'orchestrator_loaded');if(loaded&&typeof loaded.install==='function')loaded.install()}catch(e){}resolve(loadedVersion(apiName)===expectedVersion?'reloaded_current':'reloaded_version_mismatch')};
        script.onerror=()=>resolve('reload_error');
        (document.head||document.documentElement).appendChild(script);
        return;
      }
      if(hasScript(path)){resolve('script_present_waiting_for_api');return}
      const script=document.createElement('script');script.src=src;script.async=true;
      script.onload=()=>{try{const loaded=window[apiName]||T()[apiName];if(loaded&&typeof loaded.run==='function')loaded.run(reason||'orchestrator_loaded');if(loaded&&typeof loaded.install==='function')loaded.install()}catch(e){}resolve('loaded')};
      script.onerror=()=>resolve('load_error');
      (document.head||document.documentElement).appendChild(script);
    }catch(error){resolve('exception_'+String(error&&error.message||error))}
  });
}
function loadedVersion(apiName){try{const api=window[apiName]||T()[apiName];return api&&api.version||null}catch(e){return null}}
function compact(report){
  if(!report)return{status:'not_ready'};
  return{
    type:report.type||null,
    version:report.version||null,
    owner:report.owner||null,
    status:report.status||null,
    hard_missing_count:Number.isFinite(report.hard_missing_count)?report.hard_missing_count:null,
    support_reachable_missing_count:Number.isFinite(report.support_reachable_missing_count)?report.support_reachable_missing_count:null,
    dead_reference_count:Number.isFinite(report.dead_reference_count)?report.dead_reference_count:null,
    freeze_gate_pass:!!(report.freeze_gate&&report.freeze_gate.pass)
  };
}
function currentReport(reason){
  const canonical=read('pmp_active_path_discovery_report_v1');
  const bounded=read('pmp_active_path_discovery_bounded_report_v2');
  const ownership=read(KEYS.ownershipRuntime);
  const sectionOwners=read('pmp_section_owner_registry_snapshot_v1');
  const helpers=read('pmp_helper_registry_snapshot_v1');
  const diagnosticsVersion=loadedVersion('PMPDiagnosticsOwnerV1');
  const consolidatedVersion=loadedVersion('PMPDiagnosticsConsolidatedViewV1');
  const ownershipRuntimeVersion=loadedVersion('PMPAppOrchestratorOwnershipRuntimeV1');
  LAST={
    type:'PMP_APP_ORCHESTRATOR_V1_RECEIPT',
    version:V,
    owner:OWNER,
    writer:'pmp-app-orchestrator-v1.js',
    at:now(),
    reason:reason||'current_report',
    status:'CURRENT_ORCHESTRATOR_REPORT_READY',
    expected:{route_guardian:EXPECTED.guardian,current_reload:EXPECTED.current,current_inner:EXPECTED.inner,map:EXPECTED.map,diagnostics_version:DIAGNOSTICS_VERSION,diagnostics_consolidated_version:DIAGNOSTICS_CONSOLIDATED_VERSION,ownership_runtime_version:OWNERSHIP_RUNTIME_VERSION},
    diagnostics_runtime:{expected_version:DIAGNOSTICS_VERSION,loaded_version:diagnosticsVersion,status:diagnosticsVersion===DIAGNOSTICS_VERSION?'CURRENT':'NEEDS_RELOAD'},
    diagnostics_consolidated_view:{expected_version:DIAGNOSTICS_CONSOLIDATED_VERSION,loaded_version:consolidatedVersion,status:consolidatedVersion===DIAGNOSTICS_CONSOLIDATED_VERSION?'CURRENT':'NEEDS_LOAD',scope:'presentation_and_reporting_only',owner_changes:false,helper_changes:false,registry_changes:false},
    ownership_runtime_loader:{expected_version:OWNERSHIP_RUNTIME_VERSION,loaded_version:ownershipRuntimeVersion,receipt_status:ownership&&ownership.status||'not_ready',resources_checked:Number.isFinite(ownership&&ownership.resources_checked)?ownership.resources_checked:null,status:ownershipRuntimeVersion===OWNERSHIP_RUNTIME_VERSION&&ownership?'CURRENT':'NEEDS_LOAD'},
    ownership:{
      registry:'pmp-app-orchestrator-ownership-registry-v1.json',
      runtime:ownership||{status:'not_ready'},
      canonical_writer_rule:'one canonical writer per protected resource',
      helper_rule:'helpers may read or request but may not independently commit owner state',
      section_owner_legacy_snapshot:{authority:'historical_diagnostic_only',summary:sectionOwners&&sectionOwners.summary||{status:'not_ready'}},
      helper_legacy_snapshot:{authority:'historical_diagnostic_only',summary:helpers&&helpers.summary||{status:'not_ready'}},
      current_authority:'pmp-app-orchestrator-ownership-registry-v1.json'
    },
    active_path:{
      canonical_detailed:compact(canonical),
      bounded_support:compact(bounded),
      display_copy_export_source:'canonical_detailed_only',
      schemas_separate:true
    },
    new_chat_handoff:{
      button:'Diagnostics → App Orchestrator System → Copy New Chat Safe Handoff',
      owner:OWNER,
      api:'PMPNewChatSafeHandoffV1.run',
      behavior:'copies one complete packet when bounded; otherwise downloads one small verified ZIP',
      receipt:read(KEYS.handoff)||{status:'not_used_yet'}
    },
    protected_boundaries:{
      route_authority:'pmp-current-map-v12.json only',
      bank_owner:'bank_screen_owner',
      continuous_run_owner:'continuous_run_level_owner',
      diagnostics_owner:'diagnostics_owner',
      persisted_user_data:'no mutation or migration by App Orchestrator',
      production_activation:'not_attempted'
    },
    required_maintenance_gates:[
      'App Orchestrator Ownership Maintenance',
      'Runtime Integrity Seal',
      'Permanent No-Blind-Flying Gate'
    ],
    safe_claim:'App Orchestrator reports current architecture and ownership state and creates a safe new-chat handoff. It does not own Bank data, Continuous Run lifecycle, routes, user data, or production activation.',
    side_effects:{route_change:'not_attempted',bank_rebuild:'not_attempted',indexeddb_write:'not_attempted',storage_migration:'not_attempted',persisted_user_data_write:'not_attempted',ownership_takeover:'not_attempted'}
  };
  put(KEYS.receipt,LAST);
  put(KEYS.status,{type:'PMP_APP_ORCHESTRATOR_CURRENT_STATUS_V1',version:V,owner:OWNER,at:now(),status:LAST.status,diagnostics_runtime:LAST.diagnostics_runtime,diagnostics_consolidated_view:LAST.diagnostics_consolidated_view,ownership_runtime_loader:LAST.ownership_runtime_loader,ownership:LAST.ownership,active_path:LAST.active_path,new_chat_handoff:LAST.new_chat_handoff});
  return LAST;
}
async function run(reason){
  await load('pmp-app-orchestrator-ownership-runtime-v1.js',OWNERSHIP_RUNTIME_SRC,'PMPAppOrchestratorOwnershipRuntimeV1','orchestrator_ownership_runtime',OWNERSHIP_RUNTIME_VERSION);
  const ownershipApi=window.PMPAppOrchestratorOwnershipRuntimeV1||T().PMPAppOrchestratorOwnershipRuntimeV1;
  if(ownershipApi&&typeof ownershipApi.load==='function')await ownershipApi.load();
  await load('pmp-active-path-discovery-machine-v2.js',BOUNDED_DISCOVERY_SRC,'PMPActivePathDiscoveryMachineV2','orchestrator_bounded_support');
  const bounded=window.PMPActivePathDiscoveryMachineV2||T().PMPActivePathDiscoveryMachineV2;
  if(bounded&&typeof bounded.run==='function')bounded.run('orchestrator_bounded_support');
  await load('pmp-diagnostics-owner-v1.js',DIAGNOSTICS_SRC,'PMPDiagnosticsOwnerV1','orchestrator_diagnostics',DIAGNOSTICS_VERSION);
  await load('pmp-diagnostics-consolidated-view-v1.js',DIAGNOSTICS_CONSOLIDATED_SRC,'PMPDiagnosticsConsolidatedViewV1','orchestrator_diagnostics_consolidated',DIAGNOSTICS_CONSOLIDATED_VERSION);
  const consolidated=window.PMPDiagnosticsConsolidatedViewV1||T().PMPDiagnosticsConsolidatedViewV1;
  if(consolidated&&typeof consolidated.install==='function')consolidated.install();
  await load('pmp-diagnostics-bottom-tab-forcer-v1.js',DIAGNOSTICS_TAB_SRC,'PMPDiagnosticsBottomTabForcerV1','orchestrator_diagnostics_tab');
  return currentReport(reason||'api_run');
}
async function copySafeHandoff(){
  const api=window.PMPNewChatSafeHandoffV1||T().PMPNewChatSafeHandoffV1;
  if(!api||typeof api.run!=='function')return{status:'HANDOFF_API_NOT_READY'};
  const receipt=await api.run();
  currentReport('safe_handoff_created');
  return receipt;
}
const api={version:V,owner:OWNER,keys:KEYS,run,currentReport,copySafeHandoff,getLastReceipt:()=>LAST||currentReport('get_last_receipt'),rule:'Observe and hand off only. One canonical writer per protected resource. No route, Bank, Continuous Run, persisted-data, or production ownership.'};
window.PMPAppOrchestratorV1=api;
try{T().PMPAppOrchestratorV1=api}catch(e){}
currentReport('boot');
window.addEventListener('load',()=>run('window_load'),{once:true});
})();
