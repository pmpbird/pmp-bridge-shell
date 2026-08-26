(()=>{
'use strict';
const VERSION='1.5.0-served-a003-reference-truth-20260826A';
const SOURCE_IDENTITY='pmp-active-path-discovery-machine-v1.js';
const CLASSIFICATION_REVISION='1.1.0-served-a003-reference-truth-20260826A';
const OWNER='active_path_discovery_owner';
const MAP_PATH='pmp-current-map-v12.json';
const MANIFEST_PATH='pmp-runtime-integrity-manifest-v1.json';
const REPORT_KEY='pmp_active_path_discovery_report_v1';
const RECEIPT_KEY='pmp_active_path_discovery_receipt_v1';
const COPY_RECEIPT_KEY='pmp_active_path_discovery_copy_receipt_v1';
const IGNORE=['discovery-report.json','freeze-proof.txt','blocker-detail.txt','PDF.js'];
const MAX=320;
const STATIC_POLICY={
  current:['pmp-app-current.html','pmp-current-map-v12.json','pmp-route-guardian-current-loader-v22.html','pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html','pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html','pmp-current-inner-cleanbug-rgcontrols-v23.html','pmp-current-inner-cleanbug-rgcontrols-v4.html','pmp-current-inner-cleanbug-rgcontrols-v3.html','pmp-home-single-v6.html','pmp-reload-current-live-update-marker-v1.json'],
  support:['bug-memory-current-clean-v1.html','pmp-route-guardian-action-v2.html','resident.html','safe-writer-v14.html','code-safety-v13.html','pmp-current-inner-cleanbug-rgcontrols-v2.html'],
  recovery:['pmp-route-guardian-last-good-clean-v1.js','pmp-current-inner-cleanbug-rgcontrols-v16.html','pmp-route-guardian-last-good-v3-button-v1.js','pmp-route-guardian-last-good-v1.html','pmp-route-guardian-last-good-v18.html','pmp-route-guardian-recovery-tools-v8.html','pmp-move-ledger-candidate-follow-v1.html','pmp-route-guardian-current-loader-v14.html','pmp-current-inner-cleanbug-rgcontrols-v9.html','pmp-current-inner-cleanbug-rgcontrols-v13.html'],
  historic:['pmp-current-map-v11.json','pmp-current-map-v10.json','pmp-current-map-v9.json','pmp-current-map.json','pmp-route-guardian-current-loader-v15.html','pmp-route-guardian-current-loader-v17.html','pmp-route-guardian-current-loader-v18.html','pmp-route-guardian-current-loader-v19.html','pmp-route-guardian-current-loader-v20.html','pmp-route-guardian-current-loader-v21.html','pmp-current-reload-owner-v27.html','pmp-current-reload-owner-v28.html','pmp-current-reload-owner-v29.html','pmp-current-reload-owner-v29-cachelift-20260706b.html','pmp-current-reload-owner-v29-permanent-update-gate-20260706f.html','pmp-current-inner-cleanbug-rgcontrols-v24.html','pmp-current-inner-cleanbug-rgcontrols-v26.html','pmp-current-inner-cleanbug-rgcontrols-v29.html'],
  known_absent:['pmp-clean-v13.html','pmp-current-reload-current-live-update-marker-v1.json']
};
let LAST=null;
let MOUNT_TIMER=null;
let SCAN_COUNTER=0;
const WIRED_DOCS=new WeakSet();
const WIRED_FRAMES=new WeakSet();
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function uniq(a){return Array.from(new Set((a||[]).filter(Boolean))).sort()}
function scanId(prefix){SCAN_COUNTER+=1;return String(prefix||'pmp-active-path-scan')+'-'+Date.now().toString(36)+'-'+SCAN_COUNTER.toString(36)}
function clean(x){
  x=String(x||'').replace(/&amp;/g,'&').trim().split('#')[0].split('?')[0].replace(/^\.\//,'').replace(/^\//,'');
  if(!x||IGNORE.some(p=>p.toLowerCase()===x.toLowerCase())||/^https?:/i.test(x)||x.includes('://')||x.includes('..'))return'';
  return/^[a-zA-Z0-9._/-]+\.(?:html|htm|js|mjs|json|css|wasm)$/i.test(x)?x:'';
}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function read(k){try{return JSON.parse(T().localStorage.getItem(k)||'null')}catch(e){return null}}
function eachDoc(fn){
  const seen=[];
  function walk(w,n){if(!w||n>12||seen.includes(w))return;seen.push(w);try{fn(w.document,w);w.document.querySelectorAll('iframe,frame').forEach(f=>{try{walk(f.contentWindow,n+1)}catch(e){}})}catch(e){}}
  walk(window,0);try{walk(T(),0)}catch(e){}
}
function liveFiles(){const out=[];eachDoc((d,w)=>{out.push(clean(String(w.location&&w.location.pathname||'').split('/').pop()));d.querySelectorAll('script[src],iframe[src],frame[src],a[href]').forEach(el=>out.push(clean(el.getAttribute('src')||el.getAttribute('href'))))});return uniq(out)}
function registry(){
  try{const api=window.PMPMountRegistryV1||T().PMPMountRegistryV1;if(api&&typeof api.registry==='function')return api.registry()}catch(e){}
  return read('pmp_mount_registry_v1')||{};
}
function atlasPaths(){
  const r=registry();let paths=[];
  if(Array.isArray(r.files))paths=paths.concat(r.files.map(x=>x&&x.path));
  if(r.repo_file_classification)Object.values(r.repo_file_classification).forEach(x=>{if(Array.isArray(x))paths=paths.concat(x)});
  return uniq(paths.map(clean));
}
function mapPaths(obj){const out=[];Object.values(obj||{}).forEach(v=>{if(v&&typeof v==='object'&&typeof v.path==='string')out.push(clean(v.path))});return uniq(out)}
function staticPolicy(extra){return Object.assign({source:'STATIC_FAIL_CLOSED_FALLBACK',map_fetch_ok:false,map_status:0,map_error:null},Object.fromEntries(Object.entries(STATIC_POLICY).map(([k,v])=>[k,uniq(v.map(clean))])),extra||{})}
async function loadPolicy(){
  try{
    const response=await fetch(MAP_PATH,{cache:'no-store'});
    if(!response.ok)return staticPolicy({map_status:response.status,map_error:'CURRENT_MAP_HTTP_'+response.status});
    const map=await response.json();
    const current=uniq([MAP_PATH,clean(map.entry&&map.entry.path),clean(map.route_guardian&&map.route_guardian.path),clean(map.route_guardian_loader&&map.route_guardian_loader.path),clean(map.current_app&&map.current_app.path)].concat(mapPaths(map.runtime_chain)));
    const support=mapPaths(map.tool_routes),recovery=mapPaths(map.recovery_routes),historic=mapPaths(map.historic_routes),knownAbsent=uniq(Object.keys(map.known_broken_absent_claims||{}).map(clean));
    return{source:'CURRENT_MAP_FETCH',map_fetch_ok:true,map_status:response.status,map_error:null,current,support,recovery,historic,known_absent:knownAbsent,map_version:map.app_version||null,route_epoch:map.route_epoch||null};
  }catch(error){return staticPolicy({map_error:String(error&&error.message||error)})}
}
function stripStaticComments(text,path){
  const src=String(text||''),kind=String(path||'');
  if(!/\.(?:js|mjs|css|html?|htm)$/i.test(kind))return src;
  let out='',i=0,quote='',escape=false,line=false,block=false,html=false;
  while(i<src.length){
    const c=src[i],n=src[i+1]||'';
    if(line){if(c==='\n'){line=false;out+=c}else out+=' ';i+=1;continue}
    if(block){if(c==='*'&&n==='/'){block=false;out+='  ';i+=2}else{out+=c==='\n'?'\n':' ';i+=1}continue}
    if(html){if(src.slice(i,i+3)==='-->'){html=false;out+='   ';i+=3}else{out+=c==='\n'?'\n':' ';i+=1}continue}
    if(quote){out+=c;if(escape)escape=false;else if(c==='\\')escape=true;else if(c===quote)quote='';i+=1;continue}
    if(c==="'"||c==='"'||c==='`'){quote=c;out+=c;i+=1;continue}
    if(c==='/'&&n==='/'&&/\.(?:js|mjs)$/i.test(kind)){line=true;out+='  ';i+=2;continue}
    if(c==='/'&&n==='*'){block=true;out+='  ';i+=2;continue}
    if(c==='<'&&src.slice(i,i+4)==='<!--'){html=true;out+='    ';i+=4;continue}
    out+=c;i+=1;
  }
  return out;
}
function extract(text,path){
  const out=[],strong=new Set(),source=stripStaticComments(text,path);
  function add(value,isStrong){const p=clean(value);if(!p)return;if(isStrong)strong.add(p);out.push(p)}
  String(source).replace(/(?:src|href)\s*=\s*['"]([^'"]+)['"]/gi,(m,p)=>{add(p,true);return m});
  String(source).replace(/\b(?:fetch|importScripts|import)\s*\(\s*['"]([^'"]+)['"]/gi,(m,p)=>{add(p,true);return m});
  String(source).replace(/\bnew\s+(?:Worker|SharedWorker)\s*\(\s*['"]([^'"]+)['"]/gi,(m,p)=>{add(p,true);return m});
  String(source).replace(/['"`(=\s]([a-zA-Z0-9._/-]+\.(?:html|htm|js|mjs|json|css|wasm))(?=$|[?#'"`\s)>,;])/gi,(m,p)=>{
    const c=clean(p);
    if(c&&!strong.has(c)&&!/^(?:metadata|packet|report)\.json$/i.test(c))out.push(c);
    return m;
  });
  return uniq(out);
}
function isPackage(path){const p=String(path||'');return /^(?:audit|exact_scope|gates|receipts|control-pack)\//i.test(p)||/^(?:NEW_CHAT_SAFE_HANDOFF|PACKAGE_MANIFEST)\.json$/i.test(p)}
function lane(path,from,policy,live){
  if(policy.current.includes(path))return'current_boot_root';
  if(live.includes(path))return'live_runtime';
  if(policy.support.includes(path)||policy.support.includes(from))return'support_reachable';
  if(policy.recovery.includes(path)||policy.recovery.includes(from))return'fallback_or_recovery';
  if(policy.historic.includes(path)||policy.known_absent.includes(path)||policy.historic.includes(from)||isPackage(path)||/test|archive|history|legacy|diagnostic/i.test(path))return'historic_or_legacy';
  return'direct_current';
}
function canFollow(item){return item.depth<2&&item.lane!=='historic_or_legacy'&&!(['support_reachable','fallback_or_recovery'].includes(item.lane)&&item.depth>0)}
function transportClass(row){
  if(row.ok)return'REACHABLE';
  if(row.status===404||row.status===410)return'MISSING';
  if(row.status===412)return'PRECONDITION_REJECTED';
  if(row.status>0)return'HTTP_REJECTED';
  return'NETWORK_ERROR';
}
function isRequiredLane(l){return l==='current_boot_root'||l==='live_runtime'||l==='direct_current'}
async function servedIntegrityEvidence(scanId){
  const out={source:'SERVED_A003_MANIFEST',path:MANIFEST_PATH,scan_id:String(scanId||''),fetch_ok:false,status:0,manifest_sha256:null,manifest_version:null,runtime_source_set_sha256:null,record_count:null,error:null};
  try{
    const response=await fetch(MANIFEST_PATH+'?active_path_integrity='+encodeURIComponent(out.scan_id),{cache:'no-store'});
    out.status=response.status;
    const bytes=new Uint8Array(await response.arrayBuffer());
    if(!response.ok){out.error='A003_MANIFEST_HTTP_'+response.status;return out}
    if(!(globalThis.crypto&&globalThis.crypto.subtle)){out.error='WEB_CRYPTO_UNAVAILABLE';return out}
    const digest=await globalThis.crypto.subtle.digest('SHA-256',bytes);
    out.manifest_sha256=Array.from(new Uint8Array(digest)).map(v=>v.toString(16).padStart(2,'0')).join('');
    try{
      const manifest=JSON.parse(new TextDecoder().decode(bytes));
      out.manifest_version=manifest.version||null;
      out.runtime_source_set_sha256=manifest.runtime_source_set_sha256||null;
      out.record_count=Array.isArray(manifest.records)?manifest.records.length:null;
    }catch(error){out.error='A003_MANIFEST_JSON_'+String(error&&error.message||error);return out}
    out.fetch_ok=true;
    return out;
  }catch(error){out.error=String(error&&error.message||error);return out}
}
async function run(reason,options){
  options=options||{};
  const requestedScanId=String(options.scan_id||scanId('pmp-active-path-scan'));
  const started=now(),policy=await loadPolicy(),integrity=await servedIntegrityEvidence(requestedScanId),atlas=atlasPaths(),live=liveFiles(),queue=[],seen={},rows=[],edges=[];
  function push(path,from,depth){path=clean(path);if(!path||seen[path]||queue.some(x=>x.path===path))return;queue.push({path,from:from||'',depth:depth||0,lane:lane(path,from||'',policy,live)})}
  uniq(policy.current.concat(live,policy.support,policy.recovery,policy.historic,policy.known_absent)).forEach(p=>push(p,'',0));
  while(queue.length&&rows.length<MAX){
    const item=queue.shift();if(seen[item.path])continue;seen[item.path]=true;
    const row={...item,ok:false,status:0,found:[],in_atlas:atlas.includes(item.path),live_now:live.includes(item.path),map_declared:policy.current.includes(item.path)||policy.support.includes(item.path)||policy.recovery.includes(item.path)||policy.historic.includes(item.path)||policy.known_absent.includes(item.path)};
    try{
      const response=await fetch(item.path+'?active_path_discovery='+encodeURIComponent(requestedScanId),{cache:'no-store'});row.ok=response.ok;row.status=response.status;
      const text=await response.text().catch(()=>'');
      if(response.ok){row.found=extract(text,item.path);if(canFollow(item))row.found.forEach(path=>{const nextLane=lane(path,item.path,policy,live);edges.push({from:item.path,to:path,lane:nextLane});push(path,item.path,item.depth+1)})}
    }catch(error){row.error=String(error&&error.message||error)}
    row.transport_class=transportClass(row);rows.push(row);
  }
  const reachable=uniq(rows.filter(x=>x.transport_class==='REACHABLE').map(x=>x.path));
  const missingRows=rows.filter(x=>x.transport_class==='MISSING');
  const policyRejected=rows.filter(x=>x.transport_class==='PRECONDITION_REJECTED');
  const httpRejected=rows.filter(x=>x.transport_class==='HTTP_REJECTED');
  const networkErrors=rows.filter(x=>x.transport_class==='NETWORK_ERROR');
  const gaps=rows.filter(x=>x.transport_class==='REACHABLE'&&!x.in_atlas&&x.lane!=='historic_or_legacy');
  const hard=uniq(missingRows.filter(x=>isRequiredLane(x.lane)).map(x=>x.path));
  const currentPolicyRejected=policyRejected.filter(x=>isRequiredLane(x.lane));
  const currentHttpRejected=httpRejected.filter(x=>isRequiredLane(x.lane));
  const currentNetworkErrors=networkErrors.filter(x=>isRequiredLane(x.lane));
  const oldAsRoot=uniq(rows.filter(x=>policy.historic.includes(x.path)&&x.lane==='current_boot_root').map(x=>x.path));
  const byLane=(items,name)=>uniq(items.filter(x=>x.lane===name).map(x=>x.path));
  
  LAST={
    type:'PMP_ACTIVE_PATH_DISCOVERY_REPORT_V1',version:VERSION,revision:CLASSIFICATION_REVISION,source_identity:SOURCE_IDENTITY,owner:OWNER,writer:SOURCE_IDENTITY,
    scan_id:requestedScanId,requested_scan_id:requestedScanId,started_at:started,finished_at:now(),reason:reason||'canonical_detailed_scan',mode:'passive_canonical_detailed_discovery_fresh_bound',
    runtime_integrity_manifest_sha256:integrity.manifest_sha256,
    runtime_integrity_binding:integrity,
    map_policy:{source:policy.source,fetch_ok:policy.map_fetch_ok,status:policy.map_status,error:policy.map_error||null,map_version:policy.map_version||integrity.map_version||null,route_epoch:policy.route_epoch||integrity.route_epoch||null,current_count:policy.current.length,support_count:policy.support.length,recovery_count:policy.recovery.length,historic_count:policy.historic.length,known_absent_count:policy.known_absent.length},
    pass_alignment:{current_boot_root:policy.current,historic_current_references_not_boot_root:policy.historic,historic_reference_current_boot_root_count:oldAsRoot.length,historic_reference_current_boot_root:oldAsRoot},
    scanned_count:rows.length,reachable_count:reachable.length,atlas_count:atlas.length,
    hard_missing_count:hard.length,hard_missing:hard,
    atlas_registry_gap_count:gaps.length,atlas_registry_gap:uniq(gaps.map(x=>x.path)),live_runtime_registry_gap:byLane(gaps,'live_runtime'),direct_current_registry_gap:byLane(gaps,'direct_current'),support_registry_gap:byLane(gaps,'support_reachable'),fallback_registry_gap:byLane(gaps,'fallback_or_recovery'),
    live_runtime_missing_count:byLane(missingRows,'live_runtime').length,live_runtime_missing:byLane(missingRows,'live_runtime'),direct_current_missing_count:byLane(missingRows,'direct_current').length,direct_current_missing:byLane(missingRows,'direct_current'),support_reachable_missing_count:byLane(missingRows,'support_reachable').length,support_reachable_missing:byLane(missingRows,'support_reachable'),fallback_or_recovery_missing_count:byLane(missingRows,'fallback_or_recovery').length,fallback_or_recovery_missing:byLane(missingRows,'fallback_or_recovery'),legacy_or_test_missing_count:byLane(missingRows,'historic_or_legacy').length,legacy_or_test_missing:byLane(missingRows,'historic_or_legacy'),
    dead_reference_count:missingRows.length,dead_references:missingRows.map(x=>({path:x.path,status:x.status,lane:x.lane,from:x.from,classification:'MISSING'})),
    precondition_rejected_count:policyRejected.length,precondition_rejected:policyRejected.map(x=>({path:x.path,status:x.status,lane:x.lane,from:x.from,classification:'PRECONDITION_REJECTED'})),
    current_precondition_rejected_count:currentPolicyRejected.length,
    http_rejected_count:httpRejected.length,http_rejected:httpRejected.map(x=>({path:x.path,status:x.status,lane:x.lane,from:x.from,classification:'HTTP_REJECTED'})),
    network_error_count:networkErrors.length,network_errors:networkErrors.map(x=>({path:x.path,error:x.error||null,lane:x.lane,from:x.from,classification:'NETWORK_ERROR'})),
    reachable_files:reachable,live_files:live,edges,scanned:rows,
    freeze_gate:{pass:policy.map_fetch_ok&&integrity.fetch_ok&&!!integrity.manifest_sha256&&integrity.scan_id===requestedScanId&&hard.length===0&&currentPolicyRejected.length===0&&currentHttpRejected.length===0&&currentNetworkErrors.length===0&&oldAsRoot.length===0,rule:'PASS requires current-map policy evidence, a served A-003 manifest digest bound to this exact scan ID, zero true missing required current files, zero current precondition/HTTP/network rejects, and zero historic files acting as current boot roots. Static comments and weak generic output basenames are not runtime dependency claims; reachable files absent from the Atlas registry are ATLAS_REGISTRY_GAP, not HARD_MISSING.'},
    side_effects:{fix:'not_attempted',move:'not_attempted',delete:'not_attempted',reroute:'not_attempted',bank_rebuild:'not_attempted',continuous_run_mutation:'not_attempted',storage_migration:'not_attempted',persisted_user_data_write:'not_attempted'}
  };
  put(REPORT_KEY,LAST);put(RECEIPT_KEY,{type:'PMP_ACTIVE_PATH_DISCOVERY_RECEIPT_V1',version:VERSION,revision:CLASSIFICATION_REVISION,source_identity:SOURCE_IDENTITY,owner:OWNER,writer:SOURCE_IDENTITY,at:now(),scan_id:requestedScanId,hard_missing_count:LAST.hard_missing_count,atlas_registry_gap_count:LAST.atlas_registry_gap_count,precondition_rejected_count:LAST.precondition_rejected_count,dead_reference_count:LAST.dead_reference_count,historic_reference_current_boot_root_count:oldAsRoot.length,freeze_gate_pass:LAST.freeze_gate.pass});
  window.PMPActivePathDiscoveryReportV1=LAST;mount();return LAST;
}
function summary(r){if(!r)return'Waiting for discovery scan...';return'hard missing: '+r.hard_missing_count+' · atlas gaps: '+(r.atlas_registry_gap_count||0)+' · 412/precondition: '+(r.precondition_rejected_count||0)+' · dead: '+r.dead_reference_count+' · scan: '+(r.scan_id||'')}
function proof(r){const a=r&&r.pass_alignment||{};return['PMP_DISCOVERY_FREEZE_PROOF_V1','report_version: '+(r&&r.version||''),'revision: '+(r&&r.revision||''),'source_identity: '+(r&&r.source_identity||''),'scan_id: '+(r&&r.scan_id||''),'finished_at: '+(r&&r.finished_at||''),'hard_missing_count: '+(r&&r.hard_missing_count),'atlas_registry_gap_count: '+(r&&r.atlas_registry_gap_count),'precondition_rejected_count: '+(r&&r.precondition_rejected_count),'dead_reference_count: '+(r&&r.dead_reference_count),'historic_reference_current_boot_root_count: '+a.historic_reference_current_boot_root_count,'freeze_gate_pass: '+(r&&r.freeze_gate&&r.freeze_gate.pass),'canonical_writer: '+SOURCE_IDENTITY].join('\n')}
async function copyText(d,text){try{await navigator.clipboard.writeText(text)}catch(e){const ta=d.createElement('textarea');ta.value=text;ta.style.position='fixed';ta.style.left='-9999px';d.body.appendChild(ta);ta.select();d.execCommand('copy');ta.remove()}}
async function copyNow(d,r,out){r=r||await run('copy_requested',{scan_id:scanId('pmp-active-path-copy')});const text=proof(r);await copyText(d,text);put(COPY_RECEIPT_KEY,{type:'PMP_ACTIVE_PATH_DISCOVERY_COPY_RECEIPT_V1',version:VERSION,revision:CLASSIFICATION_REVISION,owner:OWNER,at:now(),scan_id:r.scan_id,text_length:text.length,freeze_gate_pass:r.freeze_gate&&r.freeze_gate.pass});if(out)out.textContent='Discovery Freeze Proof copied. '+summary(r)}
function button(d,text,fn){const b=d.createElement('button');b.type='button';b.textContent=text;b.style.cssText='width:100%;border:2px solid var(--line,#07101c);border-radius:16px;padding:12px;margin:8px 0;background:var(--a,#acd1fb);color:var(--buttonText,#101827);font:inherit;font-weight:950;text-align:left';b.onclick=fn;return b}
function mount(){
  eachDoc(d=>{try{
    const target=d.querySelector('#control .card')||d.querySelector('[data-screen="control"] .card')||d.querySelector('#control');if(!target)return;
    let card=d.getElementById('pmpActivePathDiscoveryCardV1');
    if(!card){card=d.createElement('div');card.id='pmpActivePathDiscoveryCardV1';card.setAttribute('data-pmp-section-owner',OWNER);card.setAttribute('data-pmp-owner-lock',VERSION);card.style.cssText='background:var(--card,#fff);color:var(--text,#101827);border:2px solid var(--line,#07101c);border-radius:20px;padding:12px;margin:10px 0;white-space:pre-wrap';const title=d.createElement('b'),out=d.createElement('div');title.textContent='Active Path Discovery';out.id='pmpActivePathDiscoveryOutV1';card.append(title,out,button(d,'Copy Discovery Freeze Proof',()=>copyNow(d,null,out)),button(d,'Run Discovery Again',async()=>{out.textContent='Running fresh discovery...';out.textContent=summary(await run('manual_run',{scan_id:scanId('pmp-active-path-manual')}))}));target.appendChild(card)}
    const out=card.querySelector('#pmpActivePathDiscoveryOutV1');if(out&&(!out.textContent||/Waiting for discovery scan/i.test(out.textContent)))out.textContent=summary(LAST);
  }catch(e){}})
}
function containsMountTarget(node){if(!node||node.nodeType!==1)return false;if(node.matches&&node.matches('iframe,frame,#control,[data-screen="control"]'))return true;return!!(node.querySelector&&node.querySelector('iframe,frame,#control,[data-screen="control"]'))}
function scheduleMount(){if(MOUNT_TIMER!==null)return;MOUNT_TIMER=setTimeout(()=>{MOUNT_TIMER=null;mount();bindLifecycle()},0)}
function wireDocument(d){
  if(!d||WIRED_DOCS.has(d))return;WIRED_DOCS.add(d);
  try{const root=d.documentElement;if(root){const observer=new MutationObserver(records=>{if(records.some(record=>Array.from(record.addedNodes||[]).some(containsMountTarget)))scheduleMount()});observer.observe(root,{childList:true,subtree:true})}}catch(e){}
  try{d.querySelectorAll('iframe,frame').forEach(frame=>{if(WIRED_FRAMES.has(frame))return;WIRED_FRAMES.add(frame);frame.addEventListener('load',scheduleMount)})}catch(e){}
}
function bindLifecycle(){eachDoc(d=>wireDocument(d))}
const api={version:VERSION,revision:CLASSIFICATION_REVISION,sourceIdentity:SOURCE_IDENTITY,owner:OWNER,writer:SOURCE_IDENTITY,run,mount,copyNow,reportKey:REPORT_KEY,newScanId:scanId};
window.PMPActivePathDiscoveryMachineV1=api;
setTimeout(()=>run('canonical_boot_scan',{scan_id:scanId('pmp-active-path-boot')}),3500);
bindLifecycle();scheduleMount();window.addEventListener('load',scheduleMount,{once:true});window.addEventListener('pageshow',scheduleMount);
})();
