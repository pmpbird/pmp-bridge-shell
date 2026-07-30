(()=>{
'use strict';
const V='1.0.0-pass-a-live-coverage-20260730A';
const OWNER='diagnostics_owner';
const KEY='pmp_diagnostic_coverage_pass_a_v1_receipt';
let LAST=null;
function T(){try{return window.top||window}catch(_){return window}}
function now(){return new Date().toISOString()}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(_){}return v}
function clean(x){return String(x||'').split('?')[0].split('#')[0].split('/').pop()}
function docs(){const out=[],seen=[];function walk(w,depth){if(!w||depth>10||seen.includes(w))return;seen.push(w);try{const d=w.document;out.push({window:w,document:d,path:clean(w.location&&w.location.pathname),title:String(d&&d.title||'')});d.querySelectorAll('iframe,frame').forEach(f=>{try{walk(f.contentWindow,depth+1)}catch(_){}})}catch(_){}}walk(T(),0);return out}
function read(k){try{return JSON.parse(T().localStorage.getItem(k)||'null')}catch(_){return null}}
async function ownership(){
  const api=T().PMPAppOrchestratorOwnershipRuntimeV1||window.PMPAppOrchestratorOwnershipRuntimeV1;
  if(!api||typeof api.load!=='function')return{status:'FAIL',reason:'OWNERSHIP_RUNTIME_API_UNAVAILABLE'};
  const receipt=await api.load();
  const registry=typeof api.registry==='function'?api.registry():null;
  const resources=registry&&Array.isArray(registry.resources)?registry.resources:[];
  const ids=new Map(),issues=[];
  resources.forEach(row=>{
    if(!row||!row.id||!row.owner||!row.writer)issues.push({code:'MALFORMED_RESOURCE',resource_id:row&&row.id||null});
    if(row&&row.id)ids.set(row.id,(ids.get(row.id)||0)+1);
  });
  ids.forEach((count,id)=>{if(count>1)issues.push({code:'DUPLICATE_RESOURCE_ID',resource_id:id,count})});
  const helperDeclarations=registry&&Array.isArray(registry.helper_declarations)?registry.helper_declarations:[];
  helperDeclarations.forEach(h=>{if(!h||!h.path||!h.owner||!h.role)issues.push({code:'MALFORMED_HELPER_DECLARATION',helper:h||null})});
  const current=typeof api.audit==='function'?api.audit('diagnostic_coverage_pass_a'):receipt;
  return{type:'PMP_PASS_A_OWNERSHIP_LIVE_DIAGNOSTIC_V1',at:now(),status:issues.length?'FAIL':'PASS',registry_loaded:!!registry,registry_version:registry&&registry.version||null,resources_checked:resources.length,helper_declarations_checked:helperDeclarations.length,issues,current_runtime_receipt:current,boundaries:{registry_write:false,owner_change:false,helper_change:false,canonical_writer_change:false}};
}
async function route(){
  let map=null,mapError=null;
  try{const r=await fetch('pmp-current-map-v12.json?fresh='+Date.now(),{cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);map=await r.json()}catch(e){mapError=String(e&&e.message||e)}
  const canonicalApi=T().PMPActivePathDiscoveryMachineV1||window.PMPActivePathDiscoveryMachineV1;
  const boundedApi=T().PMPActivePathDiscoveryMachineV2||window.PMPActivePathDiscoveryMachineV2;
  let canonical=read('pmp_active_path_discovery_report_v1');
  let bounded=read('pmp_active_path_discovery_bounded_report_v2');
  try{if(canonicalApi&&typeof canonicalApi.run==='function')canonical=canonicalApi.run('diagnostic_coverage_pass_a')}catch(e){canonical={status:'FAIL',error:String(e&&e.message||e)}}
  try{if(boundedApi&&typeof boundedApi.run==='function')bounded=boundedApi.run('diagnostic_coverage_pass_a')}catch(e){bounded={status:'FAIL',error:String(e&&e.message||e)}}
  const observed=docs().map(x=>x.path).filter(Boolean);
  const expected=['pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html','pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html','pmp-current-inner-cleanbug-rgcontrols-v23.html'];
  const missingExpected=expected.filter(x=>!observed.includes(x));
  const hardMissing=Number(canonical&&canonical.hard_missing_count||0)+Number(bounded&&bounded.hard_missing_count||0);
  const historic=Number(bounded&&bounded.historic_reference_current_boot_root_count||0);
  const issues=[];
  if(mapError)issues.push({code:'CURRENT_MAP_LOAD_FAILED',detail:mapError});
  if(missingExpected.length)issues.push({code:'LIVE_FRAME_CHAIN_MISMATCH',missing:missingExpected,observed});
  if(hardMissing>0)issues.push({code:'ACTIVE_PATH_HARD_MISSING',count:hardMissing});
  if(historic>0)issues.push({code:'HISTORIC_BOOT_ROOT_LIVE',count:historic});
  return{type:'PMP_PASS_A_ACTIVE_PATH_ROUTING_LIVE_DIAGNOSTIC_V1',at:now(),status:issues.length?'FAIL':'PASS',current_map_loaded:!!map,current_map:map&&{version:map.version||null,route_guardian:map.route_guardian||map.guardian||null,current_reload:map.current_reload||map.reload_owner||null,current_inner:map.current_inner||null,next_inner:map.next_inner||null},observed_frame_chain:observed,expected_frame_chain:expected,canonical,bounded,issues,boundaries:{route_change:false,frame_navigation:false,storage_migration:false}};
}
function mountLifecycle(){
  const contexts=docs();
  let registry=null;
  try{const api=T().PMPMountRegistryV1||window.PMPMountRegistryV1;if(api&&typeof api.registry==='function')registry=api.registry()}catch(_){}
  if(!registry)registry=read('pmp_mount_registry_v1');
  const files=[];
  contexts.forEach(ctx=>{files.push(ctx.path);try{ctx.document.querySelectorAll('script[src],iframe[src],frame[src]').forEach(el=>files.push(clean(el.getAttribute('src'))))}catch(_){}});
  const observed=Array.from(new Set(files.filter(Boolean))).sort();
  let expected=[];
  if(registry&&Array.isArray(registry.files))expected=registry.files.map(x=>clean(x&&x.path)).filter(Boolean);
  if(!expected.length&&registry&&registry.repo_file_classification)Object.values(registry.repo_file_classification).forEach(group=>{if(Array.isArray(group))expected=expected.concat(group.map(clean))});
  expected=Array.from(new Set(expected.filter(Boolean))).sort();
  const critical=['pmp-app-orchestrator-v1.js','pmp-diagnostics-owner-v1.js','pmp-diagnostics-consolidated-view-v1.js','pmp-app-orchestrator-ownership-runtime-v1.js','pmp-active-path-discovery-machine-v2.js'];
  const missingCritical=critical.filter(x=>!observed.includes(x));
  const requiredApis=['PMPAppOrchestratorV1','PMPDiagnosticsOwnerV1','PMPDiagnosticsConsolidatedViewV1','PMPAppOrchestratorOwnershipRuntimeV1','PMPActivePathDiscoveryMachineV2'];
  const apiState=requiredApis.map(name=>({name,available:!!(T()[name]||window[name]),version:(T()[name]||window[name]||{}).version||null}));
  const missingApis=apiState.filter(x=>!x.available).map(x=>x.name);
  const issues=[];
  if(!registry)issues.push({code:'MOUNT_REGISTRY_UNAVAILABLE'});
  if(missingCritical.length)issues.push({code:'CRITICAL_RUNTIME_FILES_NOT_OBSERVED',files:missingCritical});
  if(missingApis.length)issues.push({code:'CRITICAL_RUNTIME_APIS_UNAVAILABLE',apis:missingApis});
  return{type:'PMP_PASS_A_RUNTIME_MOUNT_LIFECYCLE_LIVE_DIAGNOSTIC_V1',at:now(),status:issues.length?'FAIL':'PASS',registry_available:!!registry,expected_registry_file_count:expected.length,observed_runtime_file_count:observed.length,accessible_documents:contexts.map(x=>({path:x.path,title:x.title})),critical_files_checked:critical,required_apis:apiState,issues,lifecycle_scope:'Current live mount availability and required runtime continuity. It does not invent past lifecycle events that were never observed.',boundaries:{mount:false,unmount:false,repair:false,route_assignment:false,registry_mutation:false,persisted_user_data_write:false}};
}
async function run(reason){
  const [ownershipResult,routeResult]=await Promise.all([ownership(),route()]);
  const mountResult=mountLifecycle();
  LAST={type:'PMP_DIAGNOSTIC_COVERAGE_PASS_A_V1',version:V,owner:OWNER,at:now(),reason:reason||'manual',status:[ownershipResult,routeResult,mountResult].every(x=>x.status==='PASS')?'PASS':'FAIL',app_orchestrator_system:ownershipResult,active_path_and_routing:routeResult,runtime_and_mount_lifecycle:mountResult,boundaries:{read_only:true,owner_changes:false,helper_changes:false,route_changes:false,mount_changes:false,storage_migration:false,persisted_user_data_write:false}};
  put(KEY,LAST);return LAST;
}
const api={version:V,owner:OWNER,run,last:()=>LAST||read(KEY),receiptKey:KEY,rule:'Read-only live diagnostics for Pass A. It observes and validates; it does not repair or take ownership.'};
window.PMPDiagnosticCoveragePassAV1=api;try{T().PMPDiagnosticCoveragePassAV1=api}catch(_){}
setTimeout(()=>run('boot'),700);
})();