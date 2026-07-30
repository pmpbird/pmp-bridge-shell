(()=>{
'use strict';
const V='2.0.0-full-diagnostics-continuation-20260730A';
const OWNER='app_orchestrator_owner';
const RECEIPT_KEY='pmp_new_chat_safe_handoff_v1_receipt';
const MAX_COPY_BYTES=480000;
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function read(k){try{return JSON.parse(T().localStorage.getItem(k)||'null')}catch(e){return null}}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
async function fetchJSON(path){try{const r=await fetch(path+'?handoff='+Date.now(),{cache:'no-store'});return r.ok?await r.json():{status:'unavailable',path,http_status:r.status}}catch(e){return{status:'unavailable',path,error:String(e&&e.message||e)}}}
async function fetchText(path){try{const r=await fetch(path+'?handoff='+Date.now(),{cache:'no-store'});return r.ok?await r.text():JSON.stringify({status:'unavailable',path,http_status:r.status})}catch(e){return JSON.stringify({status:'unavailable',path,error:String(e&&e.message||e)})}}
function safeSummary(value,limit){const text=JSON.stringify(value||null);if(text.length<=limit)return value;return{type:value&&value.type||'TRUNCATED_RECORD',status:value&&value.status||'present',truncated:true,original_characters:text.length,summary:text.slice(0,limit)}}
function diagnosticsPackage(){try{const d=T().PMPDiagnosticsConsolidatedViewV1||window.PMPDiagnosticsConsolidatedViewV1;if(d&&typeof d.fullDiagnosticReport==='function')return d.fullDiagnosticReport();return{status:'FULL_DIAGNOSTICS_API_NOT_READY',fallback:safeSummary(read('pmp_diagnostics_owner_v1_receipt'),50000)}}catch(e){return{status:'FULL_DIAGNOSTICS_READ_ERROR',error:String(e&&e.message||e)}}}
async function packet(){
  const [ownership,currentMap,authorityMatrix,maintenanceRules,maintenancePointer,maintenanceState,exactNextMove,maintenanceEvidence,diagnosticsRestoration,libraryGate,orchestratorClosure]=await Promise.all([
    fetchJSON('pmp-app-orchestrator-ownership-registry-v1.json'),
    fetchJSON('pmp-current-map-v12.json'),
    fetchJSON('audit/pass13/PMP_APP_ORCHESTRATOR_AUTHORITY_MATRIX_V1.json'),
    fetchText('audit/pass13/PMP_APP_ORCHESTRATOR_MAINTENANCE_AND_FUTURE_CHANGE_RULES_V1.md'),
    fetchJSON('audit/pass13/PMP_APP_ORCHESTRATOR_LATEST_MAINTENANCE_POINTER_V1.json'),
    fetchText('audit/pass13/PMP_APP_ORCHESTRATOR_MAINTENANCE_CURRENT_STATE_V1.md'),
    fetchText('audit/pass13/PMP_APP_ORCHESTRATOR_MAINTENANCE_EXACT_NEXT_MOVE_V1.md'),
    fetchJSON('audit/pass13/app-orchestrator-ownership-maintenance-v1.json'),
    fetchJSON('audit/pass13/app-orchestrator-diagnostics-handoff-active-path-restoration-v1.json'),
    fetchJSON('audit/pass13/udl-private-library-integration-gate-v1.json'),
    fetchJSON('audit/pass13/PMP_APP_ORCHESTRATOR_PASS_CLOSURE_LEDGER_V1.json')
  ]);
  const fullDiagnostics=diagnosticsPackage();
  return{
    type:'PMP_NEW_CHAT_SAFE_HANDOFF_V2',version:V,owner:OWNER,generated_at:now(),
    repository:{name:'pmpbird/pmp-bridge-shell',default_branch:'main',expected_runtime_map:'pmp-current-map-v12.json'},
    start_here:{
      purpose:'Give a receiving chat enough architecture, authority, health, proof, and continuation context to inspect the live repository before making a safe change.',
      first_actions:[
        'Read this packet completely before changing PMP.',
        'Inspect current GitHub main; never assume this packet overrides newer repository truth.',
        'Compare the packet source-of-truth pointers and diagnostics against current main.',
        'Report mismatches, stale evidence, missing coverage, or failed gates before editing.',
        'Preserve owner/helper authority, protected resources, persisted user data, Current Map authority, Bank/Continuous Run separation, and recoverability.'
      ]
    },
    project_and_architecture_summary:{
      authority_chain:['App Orchestrator','Owners','Helpers'],
      supporting_layers:['Ownership Registry','Protected Resources','Canonical Writers','Readers and Requesters','Runtime Enforcement','Diagnostics and Proof','Maintenance','Safe Handoff'],
      major_systems:['Active Path and Routing','Runtime and Mount Lifecycle','Bridge','Library','Bank','Continuous Run','Errors, Bug Watch and Visual Stability','Diagnostics'],
      rule:'App Orchestrator records and enforces authority. Each subsystem retains its own functional diagnostics.'
    },
    governing_rules_and_boundaries:{
      one_canonical_writer:'One canonical writer owns each protected resource.',
      helpers:'Helpers may read, inspect, request, or present only within declared capability. They do not independently commit owner state.',
      route_authority:'pmp-current-map-v12.json only',
      persisted_user_data:'No deletion, migration, repair, replacement, or mutation without exact authority and proof.',
      bank_continuous_run:'Bank and Continuous Run remain separate systems even where Continuous Run is presented through Bank.',
      fail_closed:'Unknown resources, undeclared actors, missing proof, and failed gates must not be treated as authorization.',
      diagnostics:'Missing evidence must be labelled NOT_PROVEN or WARNING, never silently PASS.'
    },
    full_diagnostics_package:fullDiagnostics,
    whole_app_health:fullDiagnostics&&fullDiagnostics.whole_app_health||{status:'NOT_AVAILABLE'},
    ownership_registry:ownership,
    authority_matrix:authorityMatrix,
    source_of_truth_pointers:[
      {path:'pmp-current-map-v12.json',purpose:'canonical route authority'},
      {path:'pmp-app-orchestrator-v1.js',purpose:'App Orchestrator runtime'},
      {path:'pmp-app-orchestrator-ownership-registry-v1.json',purpose:'owner/helper/protected-resource authority'},
      {path:'pmp-diagnostics-owner-v1.js',purpose:'raw Diagnostics Owner evidence'},
      {path:'pmp-diagnostics-consolidated-view-v1.js',purpose:'Whole App Health and Full Diagnostics package'},
      {path:'pmp-new-chat-safe-handoff-v1.js',purpose:'safe continuation package builder'},
      {path:'pmp-universal-discovery-library-v1.js',purpose:'new Library implementation'},
      {path:'audit/pass13/udl-private-library-integration-gate-v1.json',purpose:'Library integration evidence'},
      {path:'audit/pass13/PMP_APP_ORCHESTRATOR_MAINTENANCE_CURRENT_STATE_V1.md',purpose:'maintenance state'},
      {path:'audit/pass13/PMP_APP_ORCHESTRATOR_MAINTENANCE_EXACT_NEXT_MOVE_V1.md',purpose:'repository-maintained next move'}
    ],
    maintenance:{rules:maintenanceRules,pointer:maintenancePointer,current_state:maintenanceState,repository_exact_next_move:exactNextMove,evidence:maintenanceEvidence,diagnostics_handoff_active_path_restoration:diagnosticsRestoration,app_orchestrator_closure:orchestratorClosure,library_integration_gate:libraryGate},
    current_runtime:{
      app_orchestrator:safeSummary(read('pmp_app_orchestrator_v1_receipt'),80000),
      ownership_runtime:safeSummary(read('pmp_app_orchestrator_ownership_runtime_v1_receipt'),40000),
      active_path_canonical:safeSummary(read('pmp_active_path_discovery_report_v1'),120000),
      active_path_bounded:safeSummary(read('pmp_active_path_discovery_bounded_report_v2'),50000),
      mount_registry:safeSummary(read('pmp_mount_registry_v1_receipt'),40000),
      section_owners:safeSummary(read('pmp_section_owner_registry_snapshot_v1'),60000),
      current_helper_declarations:ownership&&ownership.helper_declarations||[],
      historical_helper_snapshot:{warning:'Historical evidence only; not current write authority.',snapshot:safeSummary(read('pmp_helper_registry_snapshot_v1'),60000)},
      diagnostics:safeSummary(read('pmp_diagnostics_owner_v1_receipt'),50000),
      reload:safeSummary(read('pmp_reload_current_canonical_v1_receipt')||read('pmp_reload_current_v1_receipt'),30000),
      bridge:safeSummary(read('pmp_bridge_runtime_v1_receipt')||read('pmp_bridge_shell_v1_receipt'),50000),
      library:safeSummary(read('pmp_udl_private_library_integration_gate_v1_receipt')||read('pmp_universal_discovery_library_v1_receipt'),50000),
      bank:safeSummary(read('pmp_bank_diagnostics_v1_receipt')||read('pmp_bank_screen_owner_v1_receipt'),50000),
      continuous_run:safeSummary(read('pmp_continuous_run_diagnostics_v1_receipt')||read('pmp_continuous_run_level_owner_v1_receipt'),50000),
      bug_watch:safeSummary(read('pmp_bug_watch_v1_receipt')||read('pmp_diagnostic_journal_v1_receipt'),50000)
    },
    repository_audit_instructions:[
      'Fetch and inspect current main before editing.',
      'Confirm every source-of-truth pointer still exists and identify newer replacements without silently substituting them.',
      'Compare ownership registry declarations against runtime owner/helper behavior and protected-resource writers.',
      'Audit diagnostic coverage for App Orchestrator itself and every owner-governed subsystem.',
      'Audit Bridge and Library implementation, integration, persistence, runtime availability, and ownership boundaries.',
      'Audit Active Path, routing, mounts, lifecycle, Bank, Continuous Run, errors, Bug Watch, flicker, duplicates, and visual stability.',
      'Classify each result as PASS, WARNING, FAIL, or NOT_PROVEN with evidence and confidence.',
      'Stop and report before changing code when repository truth conflicts with the packet or a required gate fails.'
    ],
    required_tests_and_gates:[
      'python3 tools/test_app_orchestrator_ownership_maintenance_v1.py',
      'python3 tools/verify_app_orchestrator_ownership_maintenance_v1.py',
      'python3 tools/test_a003_integrity.py',
      'python3 tools/test_pass6_unit7_no_blind_flying_gate_v1.py',
      'python3 tools/test_udl_private_library_no_blind_gate_v1.py',
      'python3 tools/test_udl_library_integration_v1.py',
      'Run the affected Diagnostics, Bridge, Bank, Continuous Run, route, mount, and owner tests discovered on current main.'
    ],
    exact_next_move:{
      packet_instruction:'Audit current main against this handoff and Full Diagnostics before any edit. Repair only proven missing diagnostic or handoff coverage. Do not alter owner/helper authority, routes, storage, or persisted user data unless separately authorized.',
      repository_maintained_instruction:exactNextMove
    },
    authorization_boundaries:{
      allowed_without_new_authority:['read-only diagnostics presentation','copy/export integration','accurate missing-evidence labels','safe-handoff packaging'],
      not_authorized:['owner reassignment','helper reassignment','ownership registry rewrite','canonical writer transfer','route change','storage migration','persisted user-data mutation','Bank/Continuous Run merger']
    },
    recent_change_history:[
      {pr:217,change:'Diagnostics presentation consolidated without changing owner/helper authority',merge_commit:'629b36d5179d704469fd11954e266ea2ab0feb09'},
      {pr:218,change:'Diagnostics tab opening regression repaired by preserving original screen creation/activation',merge_commit:'71e42aa3030c0a3dece0ac581dd9b061d6264911'}
    ],
    evidence_manifest:{classification_rule:'Every item must be treated as current, historical, runtime, stored, unavailable, or not proven. Recent timestamps alone do not establish authority.',items:[
      {name:'ownership_registry',authority:'governing',status:ownership&&ownership.status||'loaded'},
      {name:'current_map',authority:'route',status:currentMap&&currentMap.status||'loaded'},
      {name:'authority_matrix',authority:'governing evidence',status:authorityMatrix&&authorityMatrix.status||'loaded'},
      {name:'full_diagnostics_package',authority:'read-only diagnostic evidence',status:fullDiagnostics&&fullDiagnostics.status||'loaded'},
      {name:'maintenance_state',authority:'continuation evidence',status:'loaded_or_unavailable_text'},
      {name:'library_integration_gate',authority:'integration evidence',status:libraryGate&&libraryGate.status||'loaded'}
    ]},
    package_truth:{self_verifying_when_zipped:true,payload_hash_in_manifest:true,no_persisted_user_data_included:true,repository_must_be_rechecked:true}
  };
}
function crc32(bytes){let c=-1;for(let i=0;i<bytes.length;i++){c^=bytes[i];for(let j=0;j<8;j++)c=(c>>>1)^((c&1)?0xedb88320:0)}return(c^-1)>>>0}
function u16(n){return[n&255,(n>>>8)&255]}
function u32(n){return[n&255,(n>>>8)&255,(n>>>16)&255,(n>>>24)&255]}
function concat(parts){let n=parts.reduce((s,p)=>s+p.length,0),out=new Uint8Array(n),at=0;parts.forEach(p=>{out.set(p,at);at+=p.length});return out}
function storedZip(files){const enc=new TextEncoder(),locals=[],centers=[];let offset=0;Object.keys(files).sort().forEach(name=>{const nb=enc.encode(name),data=enc.encode(files[name]),crc=crc32(data);const local=concat([new Uint8Array(u32(0x04034b50)),new Uint8Array(u16(20)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u32(crc)),new Uint8Array(u32(data.length)),new Uint8Array(u32(data.length)),new Uint8Array(u16(nb.length)),new Uint8Array(u16(0)),nb,data]);const center=concat([new Uint8Array(u32(0x02014b50)),new Uint8Array(u16(20)),new Uint8Array(u16(20)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u32(crc)),new Uint8Array(u32(data.length)),new Uint8Array(u32(data.length)),new Uint8Array(u16(nb.length)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u32(0)),new Uint8Array(u32(offset)),nb]);locals.push(local);centers.push(center);offset+=local.length});const central=concat(centers),end=concat([new Uint8Array(u32(0x06054b50)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u16(centers.length)),new Uint8Array(u16(centers.length)),new Uint8Array(u32(central.length)),new Uint8Array(u32(offset)),new Uint8Array(u16(0))]);return concat(locals.concat([central,end]))}
async function sha256(text){const b=new TextEncoder().encode(text),d=await crypto.subtle.digest('SHA-256',b);return Array.from(new Uint8Array(d)).map(x=>x.toString(16).padStart(2,'0')).join('')}
async function copy(text){if(navigator.clipboard&&navigator.clipboard.writeText){await navigator.clipboard.writeText(text);return true}const ta=document.createElement('textarea');ta.value=text;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();const ok=document.execCommand('copy');ta.remove();return ok}
function download(bytes,name){const url=URL.createObjectURL(new Blob([bytes],{type:'application/zip'})),a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500)}
async function run(){const data=await packet(),json=JSON.stringify(data,null,2),digest=await sha256(json),bytes=new TextEncoder().encode(json).length;let mode='clipboard',ok=false,file_name=null;if(bytes<=MAX_COPY_BYTES){ok=await copy(json)}else{mode='zip';file_name='PMP_NEW_CHAT_SAFE_HANDOFF_'+new Date().toISOString().replace(/[-:.]/g,'').replace('Z','Z')+'.zip';const start='Attach this ZIP to the new chat. Read 00_READ_THIS_FIRST.txt and NEW_CHAT_SAFE_HANDOFF.json before changing PMP. Audit current GitHub main against the packet; do not assume the packet overrides newer repository truth.\n';const manifest=JSON.stringify({type:'PMP_NEW_CHAT_SAFE_HANDOFF_PACKAGE_MANIFEST_V2',version:V,generated_at:now(),payload:'NEW_CHAT_SAFE_HANDOFF.json',payload_bytes:bytes,payload_sha256:digest},null,2);download(storedZip({'00_READ_THIS_FIRST.txt':start,'NEW_CHAT_SAFE_HANDOFF.json':json,'PACKAGE_MANIFEST.json':manifest,'NEW_CHAT_SAFE_HANDOFF.json.sha256':digest+'  NEW_CHAT_SAFE_HANDOFF.json\n'}),file_name);ok=true}const receipt={type:'PMP_NEW_CHAT_SAFE_HANDOFF_RECEIPT_V2',version:V,owner:OWNER,at:now(),status:ok?'PASS':'FAILED',mode,payload_bytes:bytes,payload_sha256:digest,file_name,includes_full_diagnostics:true,includes_repository_audit_instructions:true,rule:'Copies the complete safe handoff when bounded; otherwise downloads one self-verifying ZIP. No persisted user data is included or changed.'};put(RECEIPT_KEY,receipt);return receipt}
const api={version:V,owner:OWNER,packet,run,receipt:()=>read(RECEIPT_KEY),maxCopyBytes:MAX_COPY_BYTES};
window.PMPNewChatSafeHandoffV1=api;try{T().PMPNewChatSafeHandoffV1=api}catch(e){}
})();