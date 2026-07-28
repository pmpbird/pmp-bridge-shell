(()=>{
'use strict';
const V='3.0.0-ownership-registry-enforced';
const OWNER='app_orchestrator_owner';
const KEYS={
  receipt:'pmp_pass8_helper_rules_receipt_v1',
  registry:'pmp_pass8_helper_rules_registry_v1',
  unknown:'pmp_pass8_unknown_helpers_v1'
};
const DECLARED=[
  ['pmp-pass2-atlas-adapter-v2.js','mount_registry_owner','read_only_runtime_adapter'],
  ['pmp-authority-rules-v1.js','app_orchestrator_owner','read_only_authority_diagnostic'],
  ['pmp-active-bug-found-contract-v1.js','bug_bank_owner','read_only_contract'],
  ['pmp-bug-watch-passive-capture-v1.js','bug_bank_owner','bounded_owner_requester'],
  ['pmp-safe-writer-current-return-fix-v1.js','safe_writer_owner','assigned_owner_guard'],
  ['pmp-phase8-atlas-marker-v1.js','mount_registry_owner','read_only_marker'],
  ['pmp-pass1r-version-aligner-v1.js','mount_registry_owner','read_only_alignment_diagnostic'],
  ['pmp-pass1w-live-proof-reader-v1.js','diagnostics_owner','read_only_proof_reader'],
  ['pmp-active-path-discovery-machine-v1.js','active_path_discovery_owner','canonical_report_writer'],
  ['pmp-active-path-discovery-machine-v2.js','active_path_discovery_owner','separate_bounded_report_writer'],
  ['pmp-active-path-discovery-zip-export-v2.js','active_path_discovery_owner','canonical_report_reader_exporter'],
  ['pmp-continuous-run-bank-order-frame-loader-v1.js','continuous_run_level_owner','single_owner_frame_loader'],
  ['pmp-top-lossless-injector.js','reload_current_owner','idempotent_loader_requester'],
  ['pmp-top-lossless-loader.js','reload_current_owner','idempotent_assigned_loader'],
  ['pmp-helper-bank-live-inspector-v2.js','bank_screen_owner','owner_requested_read_only_presenter'],
  ['pmp-helper-problem-type-seeds-v1.js','diagnostics_owner','read_only_analyzer'],
  ['pmp-helper-problem-type-only-v1.js','diagnostics_owner','pure_normalizer'],
  ['pmp-hidden-safe-writer-surface-cleaner-v1.js','safe_writer_owner','inactive_read_only_compatibility'],
  ['pmp-private-source-loader-v1.js','source_gate_owner','explicit_source_intake'],
  ['pmp-phase2-private-window-adapter-v1.js','source_gate_owner','explicit_idempotent_module_loader'],
  ['pmp-resident-continuous-run-status-reader-v1.js','resident_30b_owner','canonical_status_reader'],
  ['pmp-resident-cr-status-router-v1.js','resident_30b_owner','read_only_delegate'],
  ['pmp-source-text-reader-level3-v1.js','source_gate_owner','owner_event_driven_reader']
].map(row=>({file:row[0],owner:row[1],role:row[2],registration:'accepted',allowed_to_act_freely:'no',authority:'only_through_declared_owner_role'}));
function topWindow(){try{return window.top||window}catch(e){return window}}
function put(key,value){try{topWindow().localStorage.setItem(key,JSON.stringify(value,null,2))}catch(e){}return value}
function documents(root,out,depth){
  out=out||[];depth=depth||0;
  if(!root||depth>8)return out;
  try{
    out.push(root);
    root.querySelectorAll('iframe,frame').forEach(frame=>{
      try{let doc=frame.contentDocument||(frame.contentWindow&&frame.contentWindow.document);if(doc)documents(doc,out,depth+1)}catch(e){}
    });
  }catch(e){}
  return out;
}
function loadedScripts(){
  const files=new Set();
  documents(topWindow().document).forEach(doc=>{
    try{doc.querySelectorAll('script[src]').forEach(script=>{let file=String(script.getAttribute('src')||'').split('?')[0].split('/').pop();if(file)files.add(file)})}catch(e){}
  });
  return Array.from(files).sort();
}
function helperLike(file){return /helper|adapter|reader|writer|capture|aligner|discovery|loader|marker|contract|rules|cleaner|router/i.test(file)}
function classify(){
  const declared=new Set(DECLARED.map(row=>row.file));
  const loaded=loadedScripts();
  const held=loaded.filter(file=>helperLike(file)&&!declared.has(file)&&file!=='pmp-app-orchestrator-v1.js'&&file!=='pmp-mount-registry-v1.js').map(file=>({
    file,
    registration:'held',
    reason:'helper_like_script_without_current_declaration',
    allowed_to_act_freely:'no',
    required_resolution:'declare_exact_owner_role_or_remove_from_active_chain'
  }));
  return{loaded,held};
}
function run(reason){
  const result=classify(),at=new Date().toISOString();
  const receipt={
    type:'PMP_PASS8_HELPER_RULES_RECEIPT_V1',
    version:V,
    owner:OWNER,
    at,
    reason:String(reason||'manual'),
    status:result.held.length?'HELD_UNKNOWN_HELPERS_REQUIRE_REVIEW':'HELPER_OWNERSHIP_DECLARATIONS_GREEN',
    enforcement:'machine_readable_registry_plus_static_CI_plus_owner_broker',
    counts:{declared_helpers:DECLARED.length,held_unknown_helpers:result.held.length},
    rule:'Helpers assist owners; helpers do not become owners.',
    unknown_helper:'held_by_app_orchestrator_shown_in_diagnostics_not_allowed_to_act_freely',
    helpers_do_not_mount_panels:'owner_mounts_panel_in_legal_slot',
    side_effects:{route_change:'not_attempted',bank_rebuild:'not_attempted',indexeddb_write:'not_attempted',storage_migration:'not_attempted',ownership_takeover:'not_attempted',panel_mount:'not_attempted'}
  };
  put(KEYS.registry,{type:'PMP_PASS8_HELPER_RULES_REGISTRY_V1',version:V,owner:OWNER,at,helpers:DECLARED});
  put(KEYS.unknown,{type:'PMP_PASS8_UNKNOWN_HELPERS_V1',version:V,owner:OWNER,at,held:result.held});
  put(KEYS.receipt,receipt);
  return receipt;
}
window.PMPPass8HelperRulesV1={version:V,owner:OWNER,run,getRegistry:()=>DECLARED.slice(),keys:KEYS,rule:'Helpers assist owners; helpers do not become owners.'};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>run('document_ready'),{once:true});else run('script_load');
})();
