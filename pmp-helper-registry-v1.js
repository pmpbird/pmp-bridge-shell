(()=>{
'use strict';
const V='1.0.4-pass7-helper-immediate-snapshot-write';
const OWNER='pmp-helper-registry-v1';
const KEYS={registry:'pmp_helper_registry_v1',snapshot:'pmp_helper_registry_snapshot_v1',receipt:'pmp_helper_registry_v1_receipt',violations:'pmp_helper_registry_violations_v1',runtime:'pmp_helper_registry_runtime_audit_v1'};
const RULE='Immediate helper snapshot writer. Required snapshots are written before owner dependency checks. Helpers assist exactly one parent owner and never become owners.';
const HELPERS=[
{id:'mount_registry_helper',name:'Mount Registry Helper',parent_owner:'app_orchestrator_owner',status:'active',detect:['PMPMountRegistryV1']},
{id:'active_path_discovery_helper',name:'Active Path Discovery Helper',parent_owner:'app_orchestrator_owner',status:'active_or_visible_when_loaded',detect:['PMPActivePathDiscoveryZipExportV2','PMPActivePathDiscoveryMachineV1']},
{id:'section_owner_registry_helper',name:'Section Owner Registry Helper',parent_owner:'diagnostics_owner',status:'active',detect:['PMPSectionOwnerRegistryV1']},
{id:'bank_transfer_store_helper',name:'Bank Transfer Store Helper',parent_owner:'bank_screen_owner',status:'active_or_visible_when_bank_loaded',detect:['PMPContinuousRunBankTransferStoreV1']},
{id:'bank_zip_importer_helper',name:'Bank ZIP Importer Helper',parent_owner:'bank_screen_owner',status:'active_or_visible_when_bank_loaded',detect:['PMPContinuousRunBankZipImporterV1']},
{id:'containment_guard_helper',name:'Containment Guard Helper',parent_owner:'continuous_run_level_owner',status:'active_or_visible_when_levels_loaded',detect:['PMPContinuousRunLevelUIScopeV1']},
{id:'level_card_helper',name:'Level Card Helper',parent_owner:'continuous_run_level_owner',status:'active_or_visible_when_levels_loaded',detect:['PMPLevel30FinalSealDoneLockV1','PMPSourceTextReaderLevel3V1','PMPSourceReferenceGateLevel4V1']},
{id:'resident_status_reader_helper',name:'Resident Status Reader Helper',parent_owner:'resident_30b_owner',status:'active_or_visible_when_resident_loaded',detect:['PMPResidentContinuousRunStatusReaderV1','PMPResidentStartupLevel30AutoGateV1']},
{id:'zip_reader_helper',name:'Source ZIP Reader Helper',parent_owner:'source_gate_owner',status:'active_or_visible_when_source_gate_loaded',detect:['PMPSourceZipReaderLevel2V1','PMPSourceZipExtractorLevel2bV1']},
{id:'text_reader_helper',name:'Source Text Reader Helper',parent_owner:'source_gate_owner',status:'active_or_visible_when_source_gate_loaded',detect:['PMPSourceTextReaderLevel3V1']},
{id:'reference_gate_helper',name:'Source Reference Gate Helper',parent_owner:'source_gate_owner',status:'active_or_visible_when_source_gate_loaded',detect:['PMPSourceReferenceGateLevel4V1']}
];
function now(){return new Date().toISOString()}
function targets(){let a=[];try{a.push(localStorage)}catch(e){}try{if(window.top&&window.top.localStorage&&a.indexOf(window.top.localStorage)<0)a.push(window.top.localStorage)}catch(e){}return a}
function put(k,v){let txt='';try{txt=JSON.stringify(v,null,2)}catch(e){txt=JSON.stringify({type:'SERIALIZE_FAILED',error:String(e&&e.message||e),at:now()})}let writes=0,errors=[];targets().forEach((s,i)=>{try{s.setItem(k,txt);writes++}catch(e){errors.push({target:i,error:String(e&&e.message||e)})}});return{writes,errors,bytes:txt.length}}
let runtime={type:'PMP_HELPER_REGISTRY_RUNTIME_AUDIT_V1',version:V,owner:OWNER,created_at:now(),events:[]};
function trace(event,data){runtime.updated_at=now();runtime.events.push(Object.assign({at:now(),event},data||{}));runtime.events=runtime.events.slice(-80);try{put(KEYS.runtime,runtime)}catch(e){}return runtime}
function baseRows(){return HELPERS.map(h=>({id:h.id,name:h.name,parent_owner:h.parent_owner,status:h.status,detect:h.detect||[],observed:{present:false,detected_globals:[],parent_owner_known:false,immediate_seed:true},health:{present:false,missing:h.status==='active',orphan:true,illegal_owner_claim:false,healthy:false},evidence:{last_update:now(),phase:'immediate_snapshot_seed'}}))}
function writeImmediate(reason){let rows=baseRows();let violations=[];rows.forEach(h=>{if(h.health.orphan)violations.push({helper_id:h.id,parent_owner:h.parent_owner,type:'missing_parent_owner_seed'});if(h.health.missing)violations.push({helper_id:h.id,type:'active_helper_missing_seed',expected:h.detect})});let summary={helpers_total:rows.length,helpers_present:0,helpers_healthy:0,violations:violations.length,missing_active_helpers:rows.filter(h=>h.health.missing).map(h=>h.id),orphan_helpers:rows.filter(h=>h.health.orphan).map(h=>h.id)};let registry={type:'PMP_HELPER_REGISTRY_V1',version:V,owner:OWNER,updated_at:now(),mode:'immediate_helper_truth_table',helper_count:HELPERS.length,helpers:HELPERS,keys:KEYS,rule:RULE};let snapshot={type:'PMP_HELPER_REGISTRY_SNAPSHOT_V1',version:V,owner:OWNER,at:now(),reason:reason||'immediate',mode:'immediate_snapshot_first',parent_owner_ids_seen:[],helpers:rows,violations,summary,rule:RULE};let writes={registry:put(KEYS.registry,registry),snapshot:put(KEYS.snapshot,snapshot),violations:put(KEYS.violations,violations)};let receipt={type:'PMP_HELPER_REGISTRY_RECEIPT_V1',version:V,owner:OWNER,at:now(),reason:reason||'immediate',mode:'immediate_snapshot_first',pass:false,summary,storage_writes:writes,side_effects:{repair_attempted:false,route_change_attempted:false,indexeddb_write_attempted:false,bank_rebuild_attempted:false,storage_migration_attempted:false,section_takeover_attempted:false,helper_takeover_attempted:false},rule:RULE};writes.receipt=put(KEYS.receipt,receipt);trace('immediate_snapshot_write_complete',{summary,writes});return{registry,snapshot,receipt}}
function scan(reason){trace('scan_enter',{reason:reason||'scan'});try{return writeImmediate(reason||'scan')}catch(e){trace('scan_exception',{error:String(e&&e.message||e),stack:String(e&&e.stack||'')});return null}}
trace('script_start',{href:String(location.href||'')});
window.PMPHelperRegistryV1={version:V,owner:OWNER,mode:'immediate_snapshot_first',keys:KEYS,scan,trace:()=>runtime,rule:RULE};
trace('global_installed',{global_present:!!window.PMPHelperRegistryV1});
writeImmediate('script_start_immediate');
[0,250,1000,3000,7000].forEach(t=>setTimeout(()=>scan('scheduled_'+t),t));setInterval(()=>scan('slow_watch_5000'),5000);
})();