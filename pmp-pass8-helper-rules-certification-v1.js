(()=>{
'use strict';
const V='1.0.0-pass8-helper-rules-certification-gate-20260709A';
const OWNER='pmp-pass8-helper-rules-certification-v1';
const KEY='pmp_pass8_helper_rules_certification_v1';
const RECEIPT='pmp_pass8_helper_rules_certification_receipt_v1';
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function read(k){try{return JSON.parse(T().localStorage.getItem(k)||'null')}catch(e){return null}}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function state(ok,yes,no){return ok?yes:no}
function num(x){return typeof x==='number'?x:null}
function run(reason){
  let helper=read('pmp_pass8_helper_rules_receipt_v1');
  let unknown=read('pmp_pass8_unknown_helpers_v1');
  let discovery=read('pmp_active_path_discovery_receipt_v1');
  let discoveryReport=read('pmp_active_path_discovery_report_v1');
  let atlas=read('pmp_mount_registry_v1_receipt');
  let orch=read('pmp_app_orchestrator_v1_receipt');
  let held=unknown&&Array.isArray(unknown.held)?unknown.held:[];
  let helperCounts=helper&&helper.counts?helper.counts:{};
  let helperActive=!!(helper&&helper.status==='PASS8_HELPER_RULES_ACTIVE');
  let helperNoUnknown=held.length===0&&helperCounts.held_unknown_helpers===0;
  let helperClassified=!!(helperCounts.declared_helpers&&helperCounts.classified_helpers&&helperCounts.declared_helpers===helperCounts.classified_helpers);
  let atlasClean=!!(discovery&&discovery.freeze_gate_pass===true&&discovery.hard_missing_count===0&&discovery.dead_reference_count===0);
  let liveClean=!!(!discoveryReport||(discoveryReport.live_runtime_missing_count===0&&discoveryReport.direct_current_missing_count===0));
  let oldRootClean=!!(!discovery||discovery.historic_reference_current_boot_root_count===0);
  let atlasPresent=!!(atlas&&atlas.version);
  let copyStable=!!(!orch||!orch.copy_contract||(orch.copy_contract.pass_specific==='no'&&orch.copy_contract.works_after_future_passes==='yes'));
  let pass=helperActive&&helperNoUnknown&&helperClassified&&atlasClean&&liveClean&&oldRootClean&&atlasPresent&&copyStable;
  let report={
    type:'PMP_PASS8_HELPER_RULES_CERTIFICATION_V1',
    version:V,
    owner:OWNER,
    at:now(),
    reason:reason||'certification_scan',
    status:state(pass,'PASS8_HELPER_RULES_CERTIFIED_MOVE_ON','PASS8_HELPER_RULES_NEEDS_REVIEW'),
    move_on_from_pass8:state(pass,'yes','needs_review'),
    scope:'Pass 8 helper rules certification for current runtime helper registry plus clean Atlas/Discovery freeze gate.',
    checks:{
      helper_rules_status:state(helperActive,'active','needs_review'),
      helper_unknowns:state(helperNoUnknown,'zero_held_unknown_helpers','needs_review'),
      helper_classification:state(helperClassified,'declared_helpers_equal_classified_helpers','needs_review'),
      atlas_discovery_freeze_gate:state(atlasClean,'passed','needs_review'),
      live_runtime_missing:state(liveClean,'zero','needs_review'),
      old_current_root_refs:state(oldRootClean,'zero','needs_review'),
      atlas_registry:state(atlasPresent,'present','needs_review'),
      copy_contract:state(copyStable,'stable_pass_independent_or_not_required_for_pass8','needs_review')
    },
    evidence_summary:{
      helper_rules:{
        version:helper&&helper.version||'missing',
        status:helper&&helper.status||'missing',
        declared_helpers:num(helperCounts.declared_helpers),
        classified_helpers:num(helperCounts.classified_helpers),
        accepted_helpers:num(helperCounts.accepted_helpers),
        diagnostic_only_helpers:num(helperCounts.diagnostic_only_helpers),
        legacy_helpers:num(helperCounts.legacy_helpers),
        held_unknown_helpers:held.length
      },
      atlas_discovery:{
        receipt_version:discovery&&discovery.version||'missing',
        report_version:discoveryReport&&discoveryReport.version||'missing',
        freeze_gate_pass:discovery&&discovery.freeze_gate_pass===true?'true':'needs_review',
        hard_missing_count:discovery&&typeof discovery.hard_missing_count==='number'?discovery.hard_missing_count:'missing',
        live_runtime_missing_count:discoveryReport&&typeof discoveryReport.live_runtime_missing_count==='number'?discoveryReport.live_runtime_missing_count:'missing',
        direct_current_missing_count:discoveryReport&&typeof discoveryReport.direct_current_missing_count==='number'?discoveryReport.direct_current_missing_count:'missing',
        support_reachable_missing_count:discoveryReport&&typeof discoveryReport.support_reachable_missing_count==='number'?discoveryReport.support_reachable_missing_count:'not_blocking_current_boot',
        dead_reference_count:discovery&&typeof discovery.dead_reference_count==='number'?discovery.dead_reference_count:'missing'
      },
      atlas_registry:{
        version:atlas&&atlas.version||'missing',
        active_file_count:atlas&&atlas.active_file_count||'missing',
        support_file_count:atlas&&atlas.support_file_count||'missing',
        missing_expected_count:atlas&&typeof atlas.missing_expected_count==='number'?atlas.missing_expected_count:'missing'
      },
      app_orchestrator_copy_contract:{
        version:orch&&orch.version||'missing',
        binding:orch&&orch.copy_contract&&orch.copy_contract.binding||'missing',
        pass_specific:orch&&orch.copy_contract&&orch.copy_contract.pass_specific||'missing',
        works_after_future_passes:orch&&orch.copy_contract&&orch.copy_contract.works_after_future_passes||'missing'
      }
    },
    side_effects:{
      route_change:'not_attempted',
      bank_rebuild:'not_attempted',
      indexeddb_write:'not_attempted',
      storage_migration:'not_attempted',
      ownership_takeover:'not_attempted',
      panel_mount:'not_attempted'
    },
    safe_claim:state(pass,'Pass 8 Helper Rules are certified for the current runtime: declared helpers are classified, unknown helpers are zero, and Atlas/Discovery freeze gate is clean.','Pass 8 Helper Rules certification report was generated, but one or more checks need review.'),
    do_not_claim:['not full source acceptance','not Bank rebuild','not Pass 9 certification','not future version certification','not full app feature certification']
  };
  put(KEY,report);
  put(RECEIPT,{type:'PMP_PASS8_HELPER_RULES_CERTIFICATION_RECEIPT_V1',version:V,owner:OWNER,at:now(),status:report.status,move_on_from_pass8:report.move_on_from_pass8,checks:report.checks,side_effects:report.side_effects});
  return report;
}
window.PMPPass8HelperRulesCertificationV1={version:V,owner:OWNER,run,keys:{report:KEY,receipt:RECEIPT},rule:'Passive certification gate only; no route mutation, Bank rebuild, storage migration, ownership takeover, or panel mount.'};
try{run('boot_certification_scan');[900,2200,4200,7000,11000].forEach(t=>setTimeout(()=>run('settled_certification_scan_'+t),t))}catch(e){put(KEY,{type:'PMP_PASS8_HELPER_RULES_CERTIFICATION_V1',version:V,owner:OWNER,at:now(),status:'ERROR',error:String(e&&e.message||e),side_effects:{route_change:'not_attempted',bank_rebuild:'not_attempted',indexeddb_write:'not_attempted',storage_migration:'not_attempted',ownership_takeover:'not_attempted',panel_mount:'not_attempted'}})}
})();