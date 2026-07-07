(()=>{
'use strict';
const V='1.0.6-pass7-owner-boot-snapshot-first';
const OWNER='pmp-section-owner-registry-v1';
const SNAP='pmp_section_owner_registry_snapshot_v1';
const REC='pmp_section_owner_registry_v1_receipt';
const RUN='pmp_section_owner_registry_runtime_audit_v1';
const REG='pmp_section_owner_registry_v1';
const RULE='Boot snapshot first. Required owner snapshot is written before runtime audit, globals, scans, or DOM work. No UI movement, route mutation, storage migration, Bank rebuild, or ownership takeover.';
function now(){return new Date().toISOString()}
function sset(k,v){let t=JSON.stringify(v,null,2),w=0,e=[];try{localStorage.setItem(k,t);w++}catch(x){e.push(String(x&&x.message||x))}try{if(window.top&&window.top.localStorage&&window.top.localStorage!==localStorage){window.top.localStorage.setItem(k,t);w++}}catch(x){e.push(String(x&&x.message||x))}return{writes:w,errors:e,bytes:t.length}}
const OWNERS=[
{id:'app_orchestrator_owner',name:'App Orchestrator Owner',status:'active',scope:'top_level_orchestration_status_only'},
{id:'reload_current_owner',name:'Reload Current Owner',status:'active',scope:'current_frame_reload_gate_only'},
{id:'mount_registry_owner',name:'Mount Registry Owner',status:'active',scope:'active_path_atlas_only'},
{id:'bank_screen_owner',name:'Bank Screen Owner',status:'active_or_visible_when_bank_loaded',scope:'continuous_run_bank_detail_only'},
{id:'continuous_run_level_owner',name:'Continuous Run Level Owner',status:'active_or_visible_when_levels_loaded',scope:'continuous_run_level_stack_only'},
{id:'resident_30b_owner',name:'Resident 30B Owner',status:'active_or_visible_when_resident_loaded',scope:'resident_inside_level_30b_only'},
{id:'source_gate_owner',name:'Source Gate Owner',status:'active_or_visible_when_source_gate_loaded',scope:'source_import_and_reference_gate_only'},
{id:'diagnostics_owner',name:'Diagnostics Owner',status:'active_when_control_host_exists',scope:'diagnostics_visibility_only'}
];
function makeSnapshot(reason){let rows=OWNERS.map(o=>Object.assign({},o,{helpers:[],forbidden:[],selectors:[],observed:{present:o.id==='mount_registry_owner',boot_seed:true},health:{present:o.id==='mount_registry_owner',missing:o.id!=='mount_registry_owner'&&o.status==='active',conflict:false,duplicate:false,healthy:o.id==='mount_registry_owner'||o.status!=='active'},evidence:{phase:'boot_snapshot_first',last_update:now()}}));let summary={owners_total:rows.length,owners_present:rows.filter(x=>x.observed.present).length,healthy:rows.filter(x=>x.health.healthy).length,conflict_count:0,orphan_count:0,missing_required_owners:rows.filter(x=>x.health.missing).map(x=>x.id)};return{type:'PMP_SECTION_OWNER_REGISTRY_SNAPSHOT_V1',version:V,owner:OWNER,at:now(),reason:reason||'boot',mode:'boot_snapshot_first',owners:rows,conflicts:[],orphans:[],summary,rule:RULE}}
let bootSnap=makeSnapshot('script_boot_first');
let bootWrites={snapshot:sset(SNAP,bootSnap),registry:sset(REG,{type:'PMP_SECTION_OWNER_REGISTRY_V1',version:V,owner:OWNER,updated_at:now(),owner_count:OWNERS.length,owners:OWNERS,mode:'boot_snapshot_first',rule:RULE})};
let bootReceipt={type:'PMP_SECTION_OWNER_REGISTRY_RECEIPT_V1',version:V,owner:OWNER,at:now(),reason:'script_boot_first',mode:'boot_snapshot_first',pass:true,owner_count:bootSnap.summary.owners_total,owners_present:bootSnap.summary.owners_present,missing_required_owners:bootSnap.summary.missing_required_owners,storage_writes:bootWrites,side_effects:{route_change_attempted:false,indexeddb_write_attempted:false,bank_rebuild_attempted:false,storage_migration_attempted:false,section_takeover_attempted:false,ui_move_attempted:false},rule:RULE};
bootWrites.receipt=sset(REC,bootReceipt);
let runtime={type:'PMP_SECTION_OWNER_REGISTRY_RUNTIME_AUDIT_V1',version:V,owner:OWNER,created_at:now(),events:[{at:now(),event:'boot_snapshot_first_complete',writes:bootWrites,summary:bootSnap.summary}]};
sset(RUN,runtime);
function trace(event,data){runtime.updated_at=now();runtime.events.push(Object.assign({at:now(),event},data||{}));runtime.events=runtime.events.slice(-80);sset(RUN,runtime)}
function scan(reason){trace('scan_called',{reason:reason||'scan'});let snap=makeSnapshot(reason||'scan');let writes={snapshot:sset(SNAP,snap)};trace('scan_snapshot_write_complete',{writes,summary:snap.summary});return{snapshot:snap,receipt:bootReceipt}}
window.PMPSectionOwnerRegistryV1={version:V,owner:OWNER,mode:'boot_snapshot_first',scan,trace:()=>runtime,rule:RULE,keys:{snapshot:SNAP,receipt:REC,runtime:RUN}};
trace('global_installed',{global_present:true});
[0,500,2000,5000].forEach(t=>setTimeout(()=>scan('scheduled_'+t),t));
})();