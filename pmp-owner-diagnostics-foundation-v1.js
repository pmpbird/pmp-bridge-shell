(()=>{
'use strict';
const V='2.0.0-read-only-canonical-inputs-20260727A';
const OWNER='diagnostics_owner';
const KEYS={view:'pmp_owner_diagnostics_foundation_v1_view',receipt:'pmp_owner_diagnostics_foundation_v1_receipt'};
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function read(k){try{return JSON.parse(T().localStorage.getItem(k)||'null')}catch(e){return null}}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function model(reason){
  const owners=read('pmp_section_owner_registry_snapshot_v1');
  const helpers=read('pmp_helper_registry_snapshot_v1');
  const growth=read('pmp_universal_growth_awareness_v1_snapshot');
  const coverage=read('pmp_pass7_coverage_lock_snapshot_v1');
  const certification=read('pmp_pass7_certification_gate_v1_decision');
  return{
    type:'PMP_OWNER_DIAGNOSTICS_FOUNDATION_VIEW_V1',
    version:V,
    owner:OWNER,
    at:now(),
    reason:reason||'read',
    mode:'read_only_legacy_summary',
    owner_summary:owners&&owners.summary||{status:'not_ready'},
    helper_summary:helpers&&helpers.summary||{status:'not_ready'},
    growth_summary:growth&&growth.pressure||{status:'not_ready'},
    coverage_summary:coverage?{coverage_state:coverage.coverage_state,issue_count:coverage.issue_count||0}:{status:'not_ready'},
    certification_summary:certification?{status:certification.status,blocker_count:(certification.blockers||[]).length}:{status:'not_ready'},
    source_present:!!owners,
    helper_source_present:!!helpers,
    growth_source_present:!!growth,
    coverage_source_present:!!coverage,
    cert_source_present:!!certification,
    canonical_writes:{owner_registry:false,helper_registry:false,coverage_lock:false,certification:false},
    visible_rendering:false,
    dom_mutation:false,
    storage_delete:false,
    rule:'Legacy diagnostics foundation reads canonical owner, helper, coverage, certification, and growth records and writes only its own bounded summary.'
  };
}
function scan(reason){
  const view=model(reason),receipt={type:'PMP_OWNER_DIAGNOSTICS_FOUNDATION_RECEIPT_V1',version:V,owner:OWNER,at:now(),reason:reason||'scan',mode:view.mode,source_present:view.source_present,helper_source_present:view.helper_source_present,growth_source_present:view.growth_source_present,coverage_source_present:view.coverage_source_present,cert_source_present:view.cert_source_present,canonical_writes:view.canonical_writes,visible_rendering:false,dom_mutation:false,storage_delete:false,rule:view.rule};
  put(KEYS.view,view);put(KEYS.receipt,receipt);return{view,receipt};
}
window.PMPOwnerDiagnosticsFoundationV1={version:V,owner:OWNER,scan,model,keys:KEYS,rule:'read_only_legacy_summary'};
window.addEventListener('load',()=>scan('window_load'),{once:true});scan('initial');
})();
