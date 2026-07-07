(()=>{
'use strict';
const V='1.0.5-pass7-helper-boot-snapshot-first';
const OWNER='pmp-helper-registry-v1';
const SNAP='pmp_helper_registry_snapshot_v1';
const REC='pmp_helper_registry_v1_receipt';
const RUN='pmp_helper_registry_runtime_audit_v1';
const REG='pmp_helper_registry_v1';
const VIOL='pmp_helper_registry_violations_v1';
const RULE='Boot snapshot first. Required helper snapshot is written before owner dependency checks, globals, scans, or DOM work. Helpers assist exactly one parent owner and never become owners.';
function now(){return new Date().toISOString()}
function sset(k,v){let t=JSON.stringify(v,null,2),w=0,e=[];try{localStorage.setItem(k,t);w++}catch(x){e.push(String(x&&x.message||x))}try{if(window.top&&window.top.localStorage&&window.top.localStorage!==localStorage){window.top.localStorage.setItem(k,t);w++}}catch(x){e.push(String(x&&x.message||x))}return{writes:w,errors:e,bytes:t.length}}
const HELPERS=[
{id:'mount_registry_helper',name:'Mount Registry Helper',parent_owner:'app_orchestrator_owner',status:'active'},
{id:'active_path_discovery_helper',name:'Active Path Discovery Helper',parent_owner:'app_orchestrator_owner',status:'active_or_visible_when_loaded'},
{id:'section_owner_registry_helper',name:'Section Owner Registry Helper',parent_owner:'diagnostics_owner',status:'active'},
{id:'bank_transfer_store_helper',name:'Bank Transfer Store Helper',parent_owner:'bank_screen_owner',status:'active_or_visible_when_bank_loaded'},
{id:'bank_zip_importer_helper',name:'Bank ZIP Importer Helper',parent_owner:'bank_screen_owner',status:'active_or_visible_when_bank_loaded'},
{id:'containment_guard_helper',name:'Containment Guard Helper',parent_owner:'continuous_run_level_owner',status:'active_or_visible_when_levels_loaded'},
{id:'level_card_helper',name:'Level Card Helper',parent_owner:'continuous_run_level_owner',status:'active_or_visible_when_levels_loaded'},
{id:'resident_status_reader_helper',name:'Resident Status Reader Helper',parent_owner:'resident_30b_owner',status:'active_or_visible_when_resident_loaded'},
{id:'zip_reader_helper',name:'Source ZIP Reader Helper',parent_owner:'source_gate_owner',status:'active_or_visible_when_source_gate_loaded'},
{id:'text_reader_helper',name:'Source Text Reader Helper',parent_owner:'source_gate_owner',status:'active_or_visible_when_source_gate_loaded'},
{id:'reference_gate_helper',name:'Source Reference Gate Helper',parent_owner:'source_gate_owner',status:'active_or_visible_when_source_gate_loaded'}
];
function makeSnapshot(reason){let rows=HELPERS.map(h=>Object.assign({},h,{detect:[],observed:{present:false,detected_globals:[],parent_owner_known:false,boot_seed:true},health:{present:false,missing:h.status==='active',orphan:true,illegal_owner_claim:false,healthy:false},evidence:{phase:'boot_snapshot_first',last_update:now()}}));let violations=[];rows.forEach(h=>{if(h.health.orphan)violations.push({helper_id:h.id,parent_owner:h.parent_owner,type:'missing_parent_owner_seed'});if(h.health.missing)violations.push({helper_id:h.id,type:'active_helper_missing_seed'})});let summary={helpers_total:rows.length,helpers_present:0,helpers_healthy:0,violations:violations.length,missing_active_helpers:rows.filter(h=>h.health.missing).map(h=>h.id),orphan_helpers:rows.map(h=>h.id)};return{type:'PMP_HELPER_REGISTRY_SNAPSHOT_V1',version:V,owner:OWNER,at:now(),reason:reason||'boot',mode:'boot_snapshot_first',parent_owner_ids_seen:[],helpers:rows,violations,summary,rule:RULE}}
let bootSnap=makeSnapshot('script_boot_first');
let bootWrites={snapshot:sset(SNAP,bootSnap),registry:sset(REG,{type:'PMP_HELPER_REGISTRY_V1',version:V,owner:OWNER,updated_at:now(),helper_count:HELPERS.length,helpers:HELPERS,mode:'boot_snapshot_first',rule:RULE}),violations:sset(VIOL,bootSnap.violations)};
let bootReceipt={type:'PMP_HELPER_REGISTRY_RECEIPT_V1',version:V,owner:OWNER,at:now(),reason:'script_boot_first',mode:'boot_snapshot_first',pass:false,summary:bootSnap.summary,storage_writes:bootWrites,side_effects:{repair_attempted:false,route_change_attempted:false,indexeddb_write_attempted:false,bank_rebuild_attempted:false,storage_migration_attempted:false,section_takeover_attempted:false,helper_takeover_attempted:false},rule:RULE};
bootWrites.receipt=sset(REC,bootReceipt);
let runtime={type:'PMP_HELPER_REGISTRY_RUNTIME_AUDIT_V1',version:V,owner:OWNER,created_at:now(),events:[{at:now(),event:'boot_snapshot_first_complete',writes:bootWrites,summary:bootSnap.summary}]};
sset(RUN,runtime);
function trace(event,data){runtime.updated_at=now();runtime.events.push(Object.assign({at:now(),event},data||{}));runtime.events=runtime.events.slice(-80);sset(RUN,runtime)}
function scan(reason){trace('scan_called',{reason:reason||'scan'});let snap=makeSnapshot(reason||'scan');let writes={snapshot:sset(SNAP,snap)};trace('scan_snapshot_write_complete',{writes,summary:snap.summary});return{snapshot:snap,receipt:bootReceipt}}
window.PMPHelperRegistryV1={version:V,owner:OWNER,mode:'boot_snapshot_first',scan,trace:()=>runtime,rule:RULE,keys:{snapshot:SNAP,receipt:REC,runtime:RUN}};
trace('global_installed',{global_present:true});
[0,500,2000,5000].forEach(t=>setTimeout(()=>scan('scheduled_'+t),t));
})();