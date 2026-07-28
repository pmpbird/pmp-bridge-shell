(()=>{
'use strict';
const V='1.1.0-diagnostics-restoration-context-20260727B';
const OWNER='app_orchestrator_owner';
const RECEIPT_KEY='pmp_new_chat_safe_handoff_v1_receipt';
const MAX_COPY_BYTES=480000;
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function read(k){try{return JSON.parse(T().localStorage.getItem(k)||'null')}catch(e){return null}}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
async function fetchJSON(path){try{const r=await fetch(path+'?handoff='+Date.now(),{cache:'no-store'});return r.ok?await r.json():{status:'unavailable',path,http_status:r.status}}catch(e){return{status:'unavailable',path,error:String(e&&e.message||e)}}}
async function fetchText(path){try{const r=await fetch(path+'?handoff='+Date.now(),{cache:'no-store'});return r.ok?await r.text():JSON.stringify({status:'unavailable',path,http_status:r.status})}catch(e){return JSON.stringify({status:'unavailable',path,error:String(e&&e.message||e)})}}
function safeSummary(value,limit){
  const text=JSON.stringify(value||null);
  if(text.length<=limit)return value;
  return{type:value&&value.type||'TRUNCATED_RECORD',status:value&&value.status||'present',truncated:true,original_characters:text.length,summary:text.slice(0,limit)};
}
async function packet(){
  const [ownership,currentMap,authorityMatrix,maintenanceRules,maintenancePointer,maintenanceState,exactNextMove,maintenanceEvidence,diagnosticsRestoration]=await Promise.all([
    fetchJSON('pmp-app-orchestrator-ownership-registry-v1.json'),
    fetchJSON('pmp-current-map-v12.json'),
    fetchJSON('audit/pass13/PMP_APP_ORCHESTRATOR_AUTHORITY_MATRIX_V1.json'),
    fetchText('audit/pass13/PMP_APP_ORCHESTRATOR_MAINTENANCE_AND_FUTURE_CHANGE_RULES_V1.md'),
    fetchJSON('audit/pass13/PMP_APP_ORCHESTRATOR_LATEST_MAINTENANCE_POINTER_V1.json'),
    fetchText('audit/pass13/PMP_APP_ORCHESTRATOR_MAINTENANCE_CURRENT_STATE_V1.md'),
    fetchText('audit/pass13/PMP_APP_ORCHESTRATOR_MAINTENANCE_EXACT_NEXT_MOVE_V1.md'),
    fetchJSON('audit/pass13/app-orchestrator-ownership-maintenance-v1.json'),
    fetchJSON('audit/pass13/app-orchestrator-diagnostics-handoff-active-path-restoration-v1.json')
  ]);
  const report={
    type:'PMP_NEW_CHAT_SAFE_HANDOFF_V1',
    version:V,
    owner:OWNER,
    generated_at:now(),
    repository:{name:'pmpbird/pmp-bridge-shell',default_branch:'main',expected_runtime_map:'pmp-current-map-v12.json'},
    start_here:[
      'Use this packet as architecture and safety context before changing PMP.',
      'Inspect current GitHub main and the newest canonical handoff before editing.',
      'One canonical writer owns each protected resource. Helpers may read or request only.',
      'Preserve persisted user data, Safe Writer behavior, Current Map authority, Bank/Continuous Run separation, and recoverability.',
      'Run the ownership maintenance gate, runtime integrity gate, permanent no-blind-flying gate, and affected owner tests before merging.'
    ],
    ownership_registry:ownership,
    authority_matrix:authorityMatrix,
    maintenance:{
      rules:maintenanceRules,
      pointer:maintenancePointer,
      current_state:maintenanceState,
      exact_next_move:exactNextMove,
      evidence:maintenanceEvidence,
      diagnostics_handoff_active_path_restoration:diagnosticsRestoration
    },
    current_map:currentMap,
    current_runtime:{
      app_orchestrator:safeSummary(read('pmp_app_orchestrator_v1_receipt'),80000),
      ownership_runtime:safeSummary(read('pmp_app_orchestrator_ownership_runtime_v1_receipt'),40000),
      active_path_canonical:safeSummary(read('pmp_active_path_discovery_report_v1'),120000),
      active_path_bounded:safeSummary(read('pmp_active_path_discovery_bounded_report_v2'),50000),
      mount_registry:safeSummary(read('pmp_mount_registry_v1_receipt'),40000),
      section_owners:safeSummary(read('pmp_section_owner_registry_snapshot_v1'),60000),
      helpers_legacy_snapshot:{
        warning:'Historical Pass 7/8 evidence only. It is not current write authority and may report old missing/orphan states.',
        snapshot:safeSummary(read('pmp_helper_registry_snapshot_v1'),60000)
      },
      current_helper_declarations:ownership&&ownership.helper_declarations||[],
      diagnostics:safeSummary(read('pmp_diagnostics_owner_v1_receipt'),50000),
      reload:safeSummary(read('pmp_reload_current_canonical_v1_receipt')||read('pmp_reload_current_v1_receipt'),30000)
    },
    protected_boundaries:{
      route_authority:'pmp-current-map-v12.json only',
      bank_owner:'bank_screen_owner',
      continuous_run_owner:'continuous_run_level_owner',
      diagnostics_owner:'diagnostics_owner',
      app_orchestrator_owner:'app_orchestrator_owner',
      helper_policy:'unknown or held helpers have no active capability',
      production_user_data:'no delete, migration, repair, or mutation without exact authority'
    },
    required_gates:[
      'python3 tools/test_app_orchestrator_ownership_maintenance_v1.py',
      'python3 tools/verify_app_orchestrator_ownership_maintenance_v1.py',
      'python3 tools/test_a003_integrity.py',
      'python3 tools/test_pass6_unit7_no_blind_flying_gate_v1.py'
    ]
  };
  return report;
}
function crc32(bytes){
  let c=-1;
  for(let i=0;i<bytes.length;i++){c^=bytes[i];for(let j=0;j<8;j++)c=(c>>>1)^((c&1)?0xedb88320:0)}
  return(c^-1)>>>0;
}
function u16(n){return[n&255,(n>>>8)&255]}
function u32(n){return[n&255,(n>>>8)&255,(n>>>16)&255,(n>>>24)&255]}
function concat(parts){let n=parts.reduce((s,p)=>s+p.length,0),out=new Uint8Array(n),at=0;parts.forEach(p=>{out.set(p,at);at+=p.length});return out}
function storedZip(files){
  const enc=new TextEncoder(),locals=[],centers=[];let offset=0;
  Object.keys(files).sort().forEach(name=>{
    const nb=enc.encode(name),data=enc.encode(files[name]),crc=crc32(data);
    const local=concat([new Uint8Array(u32(0x04034b50)),new Uint8Array(u16(20)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u32(crc)),new Uint8Array(u32(data.length)),new Uint8Array(u32(data.length)),new Uint8Array(u16(nb.length)),new Uint8Array(u16(0)),nb,data]);
    const center=concat([new Uint8Array(u32(0x02014b50)),new Uint8Array(u16(20)),new Uint8Array(u16(20)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u32(crc)),new Uint8Array(u32(data.length)),new Uint8Array(u32(data.length)),new Uint8Array(u16(nb.length)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u32(0)),new Uint8Array(u32(offset)),nb]);
    locals.push(local);centers.push(center);offset+=local.length;
  });
  const central=concat(centers),end=concat([new Uint8Array(u32(0x06054b50)),new Uint8Array(u16(0)),new Uint8Array(u16(0)),new Uint8Array(u16(centers.length)),new Uint8Array(u16(centers.length)),new Uint8Array(u32(central.length)),new Uint8Array(u32(offset)),new Uint8Array(u16(0))]);
  return concat(locals.concat([central,end]));
}
async function sha256(text){const b=new TextEncoder().encode(text),d=await crypto.subtle.digest('SHA-256',b);return Array.from(new Uint8Array(d)).map(x=>x.toString(16).padStart(2,'0')).join('')}
async function copy(text){if(navigator.clipboard&&navigator.clipboard.writeText){await navigator.clipboard.writeText(text);return true}const ta=document.createElement('textarea');ta.value=text;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();const ok=document.execCommand('copy');ta.remove();return ok}
function download(bytes,name){const url=URL.createObjectURL(new Blob([bytes],{type:'application/zip'})),a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500)}
async function run(){
  const data=await packet(),json=JSON.stringify(data,null,2),digest=await sha256(json),bytes=new TextEncoder().encode(json).length;
  let mode='clipboard',ok=false,file_name=null;
  if(bytes<=MAX_COPY_BYTES){ok=await copy(json)}
  else{
    mode='zip';
    file_name='PMP_NEW_CHAT_SAFE_HANDOFF_'+new Date().toISOString().replace(/[-:.]/g,'').replace('Z','Z')+'.zip';
    const start='Attach this ZIP to the new chat and say: Read NEW_CHAT_SAFE_HANDOFF.json first. Follow its ownership and safety boundaries before changing PMP.\\n';
    const manifest=JSON.stringify({type:'PMP_NEW_CHAT_SAFE_HANDOFF_PACKAGE_MANIFEST_V1',version:V,generated_at:now(),payload:'NEW_CHAT_SAFE_HANDOFF.json',payload_bytes:bytes,payload_sha256:digest},null,2);
    download(storedZip({'00_READ_THIS_FIRST.txt':start,'NEW_CHAT_SAFE_HANDOFF.json':json,'PACKAGE_MANIFEST.json':manifest,'NEW_CHAT_SAFE_HANDOFF.json.sha256':digest+'  NEW_CHAT_SAFE_HANDOFF.json\\n'}),file_name);
    ok=true;
  }
  const receipt={type:'PMP_NEW_CHAT_SAFE_HANDOFF_RECEIPT_V1',version:V,owner:OWNER,at:now(),status:ok?'PASS':'FAILED',mode,payload_bytes:bytes,payload_sha256:digest,file_name,rule:'One button copies the complete safe handoff when bounded; otherwise it downloads one small self-verifying ZIP. No persisted user data is included or changed.'};
  put(RECEIPT_KEY,receipt);
  return receipt;
}
const api={version:V,owner:OWNER,packet,run,receipt:()=>read(RECEIPT_KEY),maxCopyBytes:MAX_COPY_BYTES};
window.PMPNewChatSafeHandoffV1=api;
try{T().PMPNewChatSafeHandoffV1=api}catch(e){}
})();
