(()=>{
'use strict';
const V='2.0.0-authority-rules-passive-foundation';
const OWNER='pmp-authority-rules-v1';
const MODE='passive_authority_map_only';
const RULE='Defines who may do what. It does not fix, move, delete, rebuild, reroute, migrate storage, or write app data.';
const GLOBAL_DENY=['auto_fix','auto_repair','move_file','delete_file','rebuild_bank','reroute_current_app','overwrite_storage','indexeddb_write','unscoped_dom_mount','silent_authority_gain'];
const ROLES={
  route_guardian:{may:['open_current_app_path','read_current_map','show_route_status'],deny:['storage_write','mount_sections','repair','delete','reroute_elsewhere'],boundary:'Outer gate only. Opens the current app path; does not own app structure.'},
  app_orchestrator:{may:['start_app_sequence','coordinate_boot_delay','check_registry_presence','report_boot_status'],deny:['define_slots','own_sections','repair','delete','migrate_storage'],boundary:'Startup coordinator only. It starts the app; it does not reshape it.'},
  mount_registry:{may:['declare_legal_slots','classify_files','publish_expected_mounts','report_missing_expected'],deny:['dom_mount','repair','delete','route_change','storage_migration'],boundary:'Atlas and slot authority only. Presence in repo is not authority.'},
  diagnostics:{may:['observe','prove','copy_report','surface_warnings'],deny:['fix','move','delete','rebuild','reroute','write_app_data'],boundary:'Proof layer only. It watches and reports.'},
  active_path_discovery:{may:['crawl_active_reachable_files','compare_to_atlas','copy_discovery_report'],deny:['fix','move','delete','rebuild','reroute','migrate_storage'],boundary:'Discovery only. A discovered path must be classified before authority.'},
  section_owner:{may:['own_bounded_section','mount_inside_declared_slot','report_section_state'],deny:['global_mount','cross_section_claim','delete','reroute','storage_migration'],boundary:'A section owner controls only its declared section.'},
  panel_module:{may:['register_to_declared_slot','render_inside_assigned_panel'],deny:['self_mount_globally','claim_new_slot','delete','reroute'],boundary:'Panel modules register; they do not create authority.'},
  helper:{may:['assist_assigned_owner','read_assigned_context','report_helper_state'],deny:['global_mount','section_takeover','delete','reroute','storage_migration'],boundary:'Helpers assist only inside assigned boundaries.'},
  bug_watch:{may:['detect_problem','capture_symptom','create_bug_candidate','send_to_bug_bank'],deny:['repair','delete','move','reroute','rebuild_bank'],boundary:'Bug Watch catches problems only.'},
  bug_bank:{may:['store_bug_record','group_bug_family','preserve_bug_evidence'],deny:['repair','delete_app_data','move_files','reroute','rebuild_app'],boundary:'Bug Bank stores bug records; it does not fix the app.'}
};
function clone(x){return JSON.parse(JSON.stringify(x));}
function norm(x){return String(x||'').trim().toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_+|_+$/g,'');}
function role(name){return ROLES[norm(name)]||null;}
function isGloballyDenied(action){return GLOBAL_DENY.indexOf(norm(action))>=0;}
function allowed(roleName,action){const r=role(roleName);const a=norm(action);if(!r)return false;if(isGloballyDenied(a))return false;return (r.may||[]).map(norm).indexOf(a)>=0;}
function denied(roleName,action){const r=role(roleName);const a=norm(action);if(!r)return true;if(isGloballyDenied(a))return true;return (r.deny||[]).map(norm).indexOf(a)>=0;}
function report(){return {type:'PMP_AUTHORITY_RULES_REPORT_V1',version:V,owner:OWNER,mode:MODE,rule:RULE,global_deny:clone(GLOBAL_DENY),roles:clone(ROLES),passive_only:true,storage_write:false,indexeddb_write:false,mutation:false};}
window.PMPAuthorityRulesV1=Object.freeze({version:V,owner:OWNER,mode:MODE,rule:RULE,global_deny:Object.freeze(GLOBAL_DENY.slice()),roles:Object.freeze(clone(ROLES)),role,allowed,denied,report});
})();
