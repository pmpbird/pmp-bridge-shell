(()=>{
'use strict';
const VERSION='2.2.0-bounded-support-no-v1-alias-20260727A';
const OWNER='active_path_discovery_owner';
const REPORT_KEY='pmp_active_path_discovery_bounded_report_v2';
const RECEIPT_KEY='pmp_active_path_discovery_bounded_receipt_v2';
const CURRENT=['pmp-app-current.html','pmp-current-map-v12.json','pmp-route-guardian-current-loader-v22.html','pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html','pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html','pmp-current-inner-cleanbug-rgcontrols-v23.html','pmp-home-single-v6.html'];
const HISTORIC=['pmp-current-map-v11.json','pmp-current-map-v10.json','pmp-current-map-v9.json','pmp-current-map.json','pmp-route-guardian-current-loader-v15.html','pmp-route-guardian-current-loader-v17.html','pmp-route-guardian-current-loader-v18.html','pmp-route-guardian-current-loader-v19.html','pmp-route-guardian-current-loader-v20.html','pmp-route-guardian-current-loader-v21.html','pmp-current-reload-owner-v27.html','pmp-current-reload-owner-v28.html','pmp-current-reload-owner-v29.html'];
let LAST=null;
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function uniq(a){return Array.from(new Set((a||[]).filter(Boolean))).sort()}
function clean(x){return String(x||'').split('?')[0].split('#')[0].split('/').pop()}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function read(k){try{return JSON.parse(T().localStorage.getItem(k)||'null')}catch(e){return null}}
function liveFiles(){
  const out=[];
  try{
    out.push(clean(location.pathname));
    document.querySelectorAll('script[src],iframe[src],frame[src]').forEach(el=>out.push(clean(el.getAttribute('src'))));
  }catch(e){}
  return uniq(out);
}
function atlasPaths(){
  let registry=null;
  try{const api=window.PMPMountRegistryV1||T().PMPMountRegistryV1;if(api&&typeof api.registry==='function')registry=api.registry()}catch(e){}
  if(!registry)registry=read('pmp_mount_registry_v1');
  let paths=[];
  if(registry&&Array.isArray(registry.files))paths=paths.concat(registry.files.map(x=>x&&x.path));
  if(registry&&registry.repo_file_classification)Object.values(registry.repo_file_classification).forEach(x=>{if(Array.isArray(x))paths=paths.concat(x)});
  return uniq(paths.map(clean));
}
function run(reason){
  const started=now(),atlas=atlasPaths(),live=liveFiles(),hard=live.filter(path=>!atlas.includes(path)),historicLive=live.filter(path=>HISTORIC.includes(path));
  LAST={
    type:'PMP_ACTIVE_PATH_DISCOVERY_BOUNDED_REPORT_V2',
    version:VERSION,
    owner:OWNER,
    writer:'pmp-active-path-discovery-machine-v2.js',
    started_at:started,
    finished_at:now(),
    reason:reason||'bounded_current_frame_scan',
    mode:'bounded_support_input_current_frame_only',
    current_boot_roots:CURRENT,
    historic_references:HISTORIC,
    live_files:live,
    atlas_count:atlas.length,
    hard_missing_count:hard.length,
    hard_missing:hard,
    historic_reference_current_boot_root_count:historicLive.length,
    historic_reference_current_boot_root:historicLive,
    freeze_gate:{pass:hard.length===0&&historicLive.length===0},
    canonical_v1_report_written:false,
    canonical_v1_global_written:false,
    panel_mounted:false,
    side_effects:{route_change:'not_attempted',bank_rebuild:'not_attempted',indexeddb_write:'not_attempted',storage_migration:'not_attempted',ownership_takeover:'not_attempted'}
  };
  put(REPORT_KEY,LAST);
  put(RECEIPT_KEY,{type:'PMP_ACTIVE_PATH_DISCOVERY_BOUNDED_RECEIPT_V2',version:VERSION,owner:OWNER,at:now(),hard_missing_count:hard.length,historic_reference_current_boot_root_count:historicLive.length,freeze_gate_pass:LAST.freeze_gate.pass,report_key:REPORT_KEY});
  window.PMPActivePathDiscoveryBoundedReportV2=LAST;
  try{T().PMPActivePathDiscoveryBoundedReportV2=LAST}catch(e){}
  return LAST;
}
function copyNow(){const r=LAST||run('copy_requested');return JSON.stringify(r,null,2)}
const api={version:VERSION,owner:OWNER,run,copyNow,reportKey:REPORT_KEY,receiptKey:RECEIPT_KEY,rule:'Separate bounded support input. Never aliases or overwrites the canonical V1 report, receipt, machine, global, or visible card.'};
window.PMPActivePathDiscoveryMachineV2=api;
try{T().PMPActivePathDiscoveryMachineV2=api}catch(e){}
setTimeout(()=>run('bounded_support_boot_scan'),300);
})();
