(()=>{
'use strict';
const VERSION='1.3.0-canonical-event-driven-mount-20260727B';
const OWNER='active_path_discovery_owner';
const REPORT_KEY='pmp_active_path_discovery_report_v1';
const RECEIPT_KEY='pmp_active_path_discovery_receipt_v1';
const COPY_RECEIPT_KEY='pmp_active_path_discovery_copy_receipt_v1';
const CURRENT=['pmp-app-current.html','pmp-current-map-v12.json','pmp-route-guardian-current-loader-v22.html','pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html','pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html','pmp-current-inner-cleanbug-rgcontrols-v23.html','pmp-home-single-v6.html'];
const HISTORIC=['pmp-current-map-v11.json','pmp-current-map-v10.json','pmp-current-map-v9.json','pmp-current-map.json','pmp-route-guardian-current-loader-v15.html','pmp-route-guardian-current-loader-v17.html','pmp-route-guardian-current-loader-v18.html','pmp-route-guardian-current-loader-v19.html','pmp-route-guardian-current-loader-v20.html','pmp-route-guardian-current-loader-v21.html','pmp-current-reload-owner-v27.html','pmp-current-reload-owner-v28.html','pmp-current-reload-owner-v29.html','pmp-current-reload-owner-v29-permanent-update-gate-20260706f.html','pmp-current-inner-cleanbug-rgcontrols-v24.html','pmp-current-inner-cleanbug-rgcontrols-v26.html','pmp-current-inner-cleanbug-rgcontrols-v29.html'];
const IGNORE=['discovery-report.json','freeze-proof.txt','blocker-detail.txt','PDF.js'];
const MAX=260;
let LAST=null;
let MOUNT_TIMER=null;
const WIRED_DOCS=new WeakSet();
const WIRED_FRAMES=new WeakSet();
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function uniq(a){return Array.from(new Set((a||[]).filter(Boolean))).sort()}
function clean(x){
  x=String(x||'').replace(/&amp;/g,'&').trim().split('#')[0].split('?')[0].replace(/^\.\//,'').replace(/^\//,'');
  if(!x||IGNORE.some(p=>p.toLowerCase()===x.toLowerCase())||/^https?:/i.test(x)||x.includes('://')||x.includes('..'))return'';
  return/^[a-zA-Z0-9._/-]+\.(?:html|js|json)$/i.test(x)?x:'';
}
function put(k,v){try{localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function read(k){try{return JSON.parse(T().localStorage.getItem(k)||'null')}catch(e){return null}}
function eachDoc(fn){
  const seen=[];
  function walk(w,n){if(!w||n>10||seen.includes(w))return;seen.push(w);try{fn(w.document,w);w.document.querySelectorAll('iframe,frame').forEach(f=>{try{walk(f.contentWindow,n+1)}catch(e){}})}catch(e){}}
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
function supportPaths(){const r=registry(),x=r.repo_file_classification&&r.repo_file_classification.SUPPORT_REACHABLE;return uniq((Array.isArray(x)?x:[]).map(clean))}
function extract(text){
  const out=[];
  String(text||'').replace(/(?:src|href)\s*=\s*['"]([^'"]+)['"]/gi,(m,p)=>{out.push(clean(p));return m});
  String(text||'').replace(/['"`(=\s]([a-zA-Z0-9._/-]+\.(?:html|js|json))(?=$|[?#'"`\s)>,;])/gi,(m,p)=>{out.push(clean(p));return m});
  return uniq(out);
}
function lane(path,from,support){
  const p=String(path).toLowerCase(),f=String(from).toLowerCase();
  if(support.includes(path)||support.includes(from))return'support_reachable_candidate';
  if(HISTORIC.includes(path)||/test|candidate|archive|history|legacy|diagnostic/.test(p))return'legacy_or_test_candidate';
  if(/last-good|recovery|restore|safe-writer|code-safety|resident/.test(p)||/last-good|recovery/.test(f))return'fallback_or_recovery_candidate';
  if(CURRENT.includes(path))return'current_boot_root';
  return'direct_current_candidate';
}
function canFollow(item){return item.depth<2&&!/legacy_or_test/.test(item.lane)&&!(/support_reachable|fallback_or_recovery/.test(item.lane)&&item.depth>0)}
async function run(reason){
  const started=now(),atlas=atlasPaths(),support=supportPaths(),live=liveFiles(),queue=[],seen={},rows=[],edges=[],dead=[];
  function push(path,from,depth){path=clean(path);if(!path||seen[path]||queue.some(x=>x.path===path))return;queue.push({path,from:from||'',depth:depth||0,lane:from?lane(path,from,support):(CURRENT.includes(path)?'current_boot_root':lane(path,'',support))})}
  CURRENT.concat(live).forEach(p=>push(p,'',0));
  while(queue.length&&rows.length<MAX){
    const item=queue.shift();if(seen[item.path])continue;seen[item.path]=true;
    const row={...item,ok:false,status:0,found:[],in_atlas:atlas.includes(item.path),live_now:live.includes(item.path),support_reachable:support.includes(item.path)};
    try{
      const response=await fetch(item.path+'?active_path_discovery='+Date.now(),{cache:'no-store'});row.ok=response.ok;row.status=response.status;
      const text=await response.text().catch(()=>'');
      if(response.ok){row.found=extract(text);if(canFollow(item))row.found.forEach(path=>{const nextLane=lane(path,item.path,support);edges.push({from:item.path,to:path,lane:nextLane});push(path,item.path,item.depth+1)})}
      else dead.push({path:item.path,status:response.status,lane:item.lane,from:item.from});
    }catch(error){row.error=String(error&&error.message||error);dead.push({path:item.path,error:row.error,lane:item.lane,from:item.from})}
    rows.push(row);
  }
  const reachable=uniq(rows.filter(x=>x.ok).map(x=>x.path));
  const liveMissing=live.filter(x=>!atlas.includes(x));
  const byLane=name=>uniq(rows.filter(x=>x.ok&&x.lane===name&&!atlas.includes(x.path)).map(x=>x.path));
  const direct=byLane('direct_current_candidate'),supportMissing=byLane('support_reachable_candidate'),fallback=byLane('fallback_or_recovery_candidate'),legacy=byLane('legacy_or_test_candidate');
  const hard=uniq(liveMissing.concat(direct)),oldAsRoot=uniq(rows.filter(x=>HISTORIC.includes(x.path)&&x.lane==='current_boot_root').map(x=>x.path));
  LAST={
    type:'PMP_ACTIVE_PATH_DISCOVERY_REPORT_V1',version:VERSION,owner:OWNER,writer:'pmp-active-path-discovery-machine-v1.js',
    started_at:started,finished_at:now(),reason:reason||'canonical_detailed_scan',mode:'passive_canonical_detailed_discovery',
    pass_alignment:{current_boot_root:CURRENT,historic_current_references_not_boot_root:HISTORIC,historic_reference_current_boot_root_count:oldAsRoot.length,historic_reference_current_boot_root:oldAsRoot},
    scanned_count:rows.length,reachable_count:reachable.length,atlas_count:atlas.length,support_atlas_count:support.length,
    hard_missing_count:hard.length,live_runtime_missing_count:liveMissing.length,direct_current_missing_count:direct.length,support_reachable_missing_count:supportMissing.length,fallback_or_recovery_missing_count:fallback.length,legacy_or_test_missing_count:legacy.length,dead_reference_count:dead.length,
    hard_missing:hard,live_runtime_missing:liveMissing,direct_current_missing:direct,support_reachable_missing:supportMissing,fallback_or_recovery_missing:fallback,legacy_or_test_missing:legacy,dead_references:dead,reachable_files:reachable,live_files:live,edges,scanned:rows,
    freeze_gate:{pass:hard.length===0&&oldAsRoot.length===0,rule:'Hard missing must be zero and historic references may not act as current boot roots.'},
    side_effects:{fix:'not_attempted',move:'not_attempted',delete:'not_attempted',reroute:'not_attempted',bank_rebuild:'not_attempted',storage_migration:'not_attempted'}
  };
  put(REPORT_KEY,LAST);put(RECEIPT_KEY,{type:'PMP_ACTIVE_PATH_DISCOVERY_RECEIPT_V1',version:VERSION,owner:OWNER,writer:'pmp-active-path-discovery-machine-v1.js',at:now(),hard_missing_count:hard.length,support_reachable_missing_count:supportMissing.length,dead_reference_count:dead.length,historic_reference_current_boot_root_count:oldAsRoot.length,freeze_gate_pass:LAST.freeze_gate.pass});
  window.PMPActivePathDiscoveryReportV1=LAST;mount();return LAST;
}
function summary(r){if(!r)return'Waiting for discovery scan...';return'hard missing: '+r.hard_missing_count+' · live: '+r.live_runtime_missing_count+' · direct: '+r.direct_current_missing_count+' · support: '+r.support_reachable_missing_count+' · fallback: '+r.fallback_or_recovery_missing_count+' · legacy/test: '+r.legacy_or_test_missing_count+' · dead: '+r.dead_reference_count}
function proof(r){const a=r&&r.pass_alignment||{};return['PMP_DISCOVERY_FREEZE_PROOF_V1','report_version: '+(r&&r.version||''),'finished_at: '+(r&&r.finished_at||''),'hard_missing_count: '+(r&&r.hard_missing_count),'support_reachable_missing_count: '+(r&&r.support_reachable_missing_count),'dead_reference_count: '+(r&&r.dead_reference_count),'historic_reference_current_boot_root_count: '+a.historic_reference_current_boot_root_count,'freeze_gate_pass: '+(r&&r.freeze_gate&&r.freeze_gate.pass),'canonical_writer: pmp-active-path-discovery-machine-v1.js'].join('\n')}
async function copyText(d,text){try{await navigator.clipboard.writeText(text)}catch(e){const ta=d.createElement('textarea');ta.value=text;ta.style.position='fixed';ta.style.left='-9999px';d.body.appendChild(ta);ta.select();d.execCommand('copy');ta.remove()}}
async function copyNow(d,r,out){r=r||LAST||await run('copy_requested');const text=proof(r);await copyText(d,text);put(COPY_RECEIPT_KEY,{type:'PMP_ACTIVE_PATH_DISCOVERY_COPY_RECEIPT_V1',version:VERSION,owner:OWNER,at:now(),text_length:text.length,freeze_gate_pass:r.freeze_gate&&r.freeze_gate.pass});if(out)out.textContent='Discovery Freeze Proof copied. '+summary(r)}
function button(d,text,fn){const b=d.createElement('button');b.type='button';b.textContent=text;b.style.cssText='width:100%;border:2px solid var(--line,#07101c);border-radius:16px;padding:12px;margin:8px 0;background:var(--a,#acd1fb);color:var(--buttonText,#101827);font:inherit;font-weight:950;text-align:left';b.onclick=fn;return b}
function mount(){
  eachDoc(d=>{try{
    const target=d.querySelector('#control .card')||d.querySelector('[data-screen="control"] .card')||d.querySelector('#control');if(!target)return;
    let card=d.getElementById('pmpActivePathDiscoveryCardV1');
    if(!card){card=d.createElement('div');card.id='pmpActivePathDiscoveryCardV1';card.setAttribute('data-pmp-section-owner',OWNER);card.setAttribute('data-pmp-owner-lock',VERSION);card.style.cssText='background:var(--card,#fff);color:var(--text,#101827);border:2px solid var(--line,#07101c);border-radius:20px;padding:12px;margin:10px 0;white-space:pre-wrap';const title=d.createElement('b'),out=d.createElement('div');title.textContent='Active Path Discovery';out.id='pmpActivePathDiscoveryOutV1';card.append(title,out,button(d,'Copy Discovery Freeze Proof',()=>copyNow(d,LAST,out)),button(d,'Run Discovery Again',async()=>{out.textContent='Running discovery...';out.textContent=summary(await run('manual_run'))}));target.appendChild(card)}
    const out=card.querySelector('#pmpActivePathDiscoveryOutV1');if(out)out.textContent=summary(LAST);
  }catch(e){}})
}
function containsMountTarget(node){
  if(!node||node.nodeType!==1)return false;
  if(node.matches&&node.matches('iframe,frame,#control,[data-screen="control"]'))return true;
  return!!(node.querySelector&&node.querySelector('iframe,frame,#control,[data-screen="control"]'));
}
function scheduleMount(){
  if(MOUNT_TIMER!==null)return;
  MOUNT_TIMER=setTimeout(()=>{MOUNT_TIMER=null;mount();bindLifecycle()},0);
}
function wireDocument(d){
  if(!d||WIRED_DOCS.has(d))return;
  WIRED_DOCS.add(d);
  try{
    const root=d.documentElement;
    if(root){
      const observer=new MutationObserver(records=>{
        if(records.some(record=>Array.from(record.addedNodes||[]).some(containsMountTarget)))scheduleMount();
      });
      observer.observe(root,{childList:true,subtree:true});
    }
  }catch(e){}
  try{
    d.querySelectorAll('iframe,frame').forEach(frame=>{
      if(WIRED_FRAMES.has(frame))return;
      WIRED_FRAMES.add(frame);
      frame.addEventListener('load',scheduleMount);
    });
  }catch(e){}
}
function bindLifecycle(){eachDoc(d=>wireDocument(d))}
const api={version:VERSION,owner:OWNER,writer:'pmp-active-path-discovery-machine-v1.js',run,mount,copyNow,reportKey:REPORT_KEY,currentBootRoot:CURRENT,historicCurrentReferences:HISTORIC};
window.PMPActivePathDiscoveryMachineV1=api;
setTimeout(()=>run('canonical_boot_scan'),3500);
bindLifecycle();
scheduleMount();
window.addEventListener('load',scheduleMount,{once:true});
window.addEventListener('pageshow',scheduleMount);
})();
