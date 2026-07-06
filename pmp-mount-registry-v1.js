(()=>{
'use strict';
const V='1.5.6-pass7-v21-v29-atlas-minimal';
const OWNER='pmp-mount-registry-v1';
const K={registry:'pmp_mount_registry_v1',receipt:'pmp_mount_registry_v1_receipt',snapshot:'pmp_mount_registry_live_snapshot_v1',missing:'pmp_mount_registry_missing_expected_v1'};
function list(s){return Array.from(new Set(String(s||'').trim().split(/\s+/).filter(Boolean)))}
function now(){return new Date().toISOString()}
function T(){try{return top||window}catch(e){return window}}
const ACTIVE_CURRENT_APP=list(`
pmp-app-current.html
pmp-current-map-v11.json
pmp-current-map-v10.json
pmp-route-guardian-current-loader-v21.html
pmp-current-reload-owner-v29.html
pmp-current-inner-cleanbug-rgcontrols-v29.html
pmp-current-inner-cleanbug-rgcontrols-v23.html
pmp-current-inner-cleanbug-rgcontrols-v4.html
pmp-current-inner-cleanbug-rgcontrols-v3.html
pmp-home-single-v6.html
pmp-launcher-reload-current-v2-guard.js
pmp-active-path-discovery-zip-export-v2.js
pmp-reload-world-from-map-v1.js
pmp-app-orchestrator-v1.js
pmp-mount-registry-v1.js
pmp-pass1r-version-aligner-v1.js
pmp-pass1w-live-proof-reader-v1.js
pmp-pass2-atlas-adapter-v2.js
pmp-active-path-discovery-machine-v1.js
pmp-active-bug-found-contract-v1.js
pmp-authority-rules-v1.js
pmp-bug-watch-passive-capture-v1.js
pmp-safe-writer-current-return-fix-v1.js
pmp-phase8-atlas-marker-v1.js
pmp-continuous-run-bank-order-frame-loader-v1.js
pmp-master-bank-inventory-router-v1.js
pmp-continuous-run-state-bank-v1.js
pmp-continuous-run-dashboard-stable-v1.js
pmp-current-screen-pointer-v1.js
pmp-launcher-reload-current-bridge-v1.js
pmp-launcher-panel-reload-button-v1.js
pmp-reload-current-final-wire-v1.js
pmp-active-page-tracker-v1.js
`);
const DYNAMIC_CURRENT_APP=list(`
pmp-route-guardian-current-loader-v20.html
pmp-route-guardian-current-loader-v19.html
pmp-route-guardian-current-loader-v18.html
pmp-route-guardian-current-loader-v17.html
pmp-route-guardian-current-loader-v15.html
pmp-current-reload-owner-v28.html
pmp-current-reload-owner-v27.html
pmp-current-map-v9.json
pmp-current-map.json
pmp-current-inner-cleanbug-rgcontrols-v26.html
pmp-current-inner-cleanbug-rgcontrols-v24.html
pmp-current-inner-cleanbug-rgcontrols-v13.html
resident.html
pmp-resident-continuous-run-status-reader-v1.js
pmp-resident-cr-status-router-v1.js
pmp-source-zip-reader-level2-v1.js
pmp-source-zip-extractor-level2b-v1.js
pmp-source-pdf-text-level2c-v1.js
pmp-private-field-extractor-v1.js
bug-memory-current-clean-v1.html
safe-writer-v14.html
code-safety-v13.html
pmp-clean-v21.html
pmp.html
safety.html
restore.html
safe-writer.html
code-safety.html
pmp-inventory-eyes-manifest-v1.0.0.json
pmp-lossless-inventory-vault/current.json
pmp-lossless-inventory-vault/rejected-ledger.json
`);
const CLASSIFICATION={ACTIVE_CURRENT_APP,DYNAMIC_CURRENT_APP,EXTERNAL_TOOL_SURFACE:[],LEGACY_INSPECT_ONLY:[],UNKNOWN_DO_NOT_MOUNT:[]};
const ATLAS_BUCKETS=[{id:'ACTIVE_CURRENT_APP',rule:'Current v21/v29 boot path and active app support.'},{id:'DYNAMIC_CURRENT_APP',rule:'Reachable support and prior wrappers, not boot authority.'},{id:'PROTECTED_STORAGE_OWNER',rule:'Observed storage owners only.'}];
const ACTIVE_EXPECTED=list(`pmp-app-current.html pmp-route-guardian-current-loader-v21.html pmp-current-reload-owner-v29.html pmp-current-inner-cleanbug-rgcontrols-v29.html pmp-current-inner-cleanbug-rgcontrols-v23.html pmp-current-inner-cleanbug-rgcontrols-v4.html pmp-current-inner-cleanbug-rgcontrols-v3.html pmp-home-single-v6.html pmp-app-orchestrator-v1.js pmp-mount-registry-v1.js pmp-pass1r-version-aligner-v1.js pmp-pass1w-live-proof-reader-v1.js pmp-active-path-discovery-machine-v1.js pmp-active-path-discovery-zip-export-v2.js pmp-launcher-reload-current-v2-guard.js`);
const INDEXED_DB=[];
function strip(s){return String(s||'').split('?')[0].split('#')[0]}
function nameFromUrl(u){return strip(u).split('/').pop()||''}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function vis(el){if(!el)return false;try{let c=el.ownerDocument.defaultView.getComputedStyle(el),r=el.getBoundingClientRect();return c.display!=='none'&&c.visibility!=='hidden'&&c.opacity!=='0'&&r.width>0&&r.height>0&&!el.hidden}catch(e){return false}}
function docs(root,a,p,n){a=a||[];p=p||'top';n=n||0;if(!root||n>12)return a;try{a.push({doc:root,path:p,url:String(root.location&&root.location.href||''),title:root.title||''});Array.from(root.querySelectorAll('iframe,frame')).forEach((f,i)=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,p+' > frame['+i+']',n+1)}catch(e){a.push({doc:null,path:p+' > frame['+i+']',url:String(f.src||''),blocked:true})}})}catch(e){}return a}
function scripts(d){try{return Array.from(d.querySelectorAll('script[src]')).map(s=>({src:nameFromUrl(s.getAttribute('src')||''),full_src:String(s.getAttribute('src')||''),id:s.id||''}))}catch(e){return[]}}
function frames(d){try{return Array.from(d.querySelectorAll('iframe,frame')).map(f=>({id:f.id||'',title:f.title||'',src:nameFromUrl(f.getAttribute('src')||f.src||''),full_src:String(f.getAttribute('src')||f.src||''),visible:vis(f)}))}catch(e){return[]}}
function store(){let out=[];try{let ls=T().localStorage;for(let i=0;i<ls.length;i++){let k=ls.key(i),v=ls.getItem(k)||'';if(/^pmp_/i.test(k))out.push({key:k,chars:v.length,has_value:!!v})}}catch(e){out.push({key:'LOCALSTORAGE_SCAN_ERROR',error:String(e&&e.message||e)})}return out}
function uniqFiles(a){return a.filter((x,i,arr)=>x&&x.path&&arr.findIndex(y=>y.path===x.path&&y.bucket===x.bucket)===i)}
function allFiles(){let out=[];ACTIVE_CURRENT_APP.forEach(path=>out.push({path,bucket:'ACTIVE_CURRENT_APP',group:'active_current_app'}));DYNAMIC_CURRENT_APP.forEach(path=>out.push({path,bucket:'DYNAMIC_CURRENT_APP',group:'dynamic_current_app'}));return uniqFiles(out)}
function fileToSlot(bucket,path){let id=(bucket+'_'+path).toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_|_$/g,'');return{id,bucket,owner:bucket+' File Owner',parent:'active_path_atlas',selectors:[],files:[path],policy:'Active Path Atlas only'}}
function allSlots(){let slots=[];ACTIVE_CURRENT_APP.forEach(path=>slots.push(fileToSlot('ACTIVE_CURRENT_APP',path)));DYNAMIC_CURRENT_APP.forEach(path=>slots.push(fileToSlot('DYNAMIC_CURRENT_APP',path)));slots.push({id:'route_guardian_gate_v21',bucket:'ACTIVE_CURRENT_APP',owner:'Route Guardian',parent:'outer shell',selectors:['#openBtn'],files:['pmp-route-guardian-current-loader-v21.html'],policy:'current route gate'});slots.push({id:'reload_owner_v29',bucket:'ACTIVE_CURRENT_APP',owner:'Reload Owner',parent:'route guardian',selectors:['iframe#a'],files:['pmp-current-reload-owner-v29.html'],policy:'fresh current app owner'});slots.push({id:'launcher_reload_current_v2_guard',bucket:'ACTIVE_CURRENT_APP',owner:'Launcher Reload Current Guard',parent:'launcher',selectors:['[data-launcher-reload-current]'],files:['pmp-launcher-reload-current-v2-guard.js'],policy:'v21-first reload guard'});return slots}
function registry(){return{type:'PMP_ACTIVE_PATH_ATLAS_V1',version:V,owner:OWNER,updated_at:now(),mode:'active_path_registry_only',scope:'Active Path Atlas only. Current path is v21 Route Guardian to v29 Reload Owner to current inner v29.',rule:'Only current active path files may drive implementation. Dynamic files are support only.',default_for_unlisted_files:'NON_BOOT_OUTSIDE_ACTIVE_ATLAS',atlas_buckets:ATLAS_BUCKETS,repo_file_classification:CLASSIFICATION,files:allFiles(),slots:allSlots(),storage_owners:store().map(x=>({key:x.key,owner:'Observed Storage Owner',bucket:'PROTECTED_STORAGE_OWNER',policy:'observe only'})),indexeddb_owners:INDEXED_DB,keys:K,active_discovery_merge:{version:'1.0.3-pass7-v21-v29-discovery-blocker-repair',pass7_current_path:'v21/v29',registered_current_files:['pmp-current-map-v11.json','pmp-route-guardian-current-loader-v21.html','pmp-current-reload-owner-v29.html','pmp-current-inner-cleanbug-rgcontrols-v29.html','pmp-launcher-reload-current-v2-guard.js','pmp-active-path-discovery-zip-export-v2.js'],registered_transition_support:['pmp-route-guardian-current-loader-v20.html','pmp-route-guardian-current-loader-v19.html','pmp-current-reload-owner-v28.html'],rule:'Atlas-only current path refresh.'},known_dead_reference_count:15,do_not_claim:['not repo deletion','not complete repo tree certified','not erasing history','not permission to mount unlisted files']}}
function expected(liveScripts,liveFrames,docPaths){let ss=new Set(liveScripts.map(x=>x.src)),fs=new Set(liveFrames.map(x=>x.src)),ds=new Set(docPaths||[]);let all=allFiles().map(f=>{let on=ss.has(f.path)||fs.has(f.path)||ds.has(f.path);return Object.assign({},f,{observed_as_script:ss.has(f.path),observed_as_frame:fs.has(f.path),observed_as_document:ds.has(f.path),observed_now:on,expected_at_boot:ACTIVE_EXPECTED.indexOf(f.path)>-1})});return{all,missing:all.filter(x=>x.expected_at_boot&&!x.observed_now&&!/json/i.test(x.path))}}
function snapshot(){let liveScripts=[],liveFrames=[],docPaths=[];let documents=docs(T().document).map(x=>{let p=nameFromUrl(x.url||x.path||'');if(p)docPaths.push(p);if(!x.doc)return{path:x.path,url:x.url,title:x.title||'',blocked:true};let sc=scripts(x.doc),fr=frames(x.doc);liveScripts=liveScripts.concat(sc);liveFrames=liveFrames.concat(fr);return{path:x.path,url:x.url,title:x.title||'',scripts:sc,iframes:fr}});let ex=expected(liveScripts,liveFrames,docPaths);return{type:'PMP_ACTIVE_PATH_ATLAS_LIVE_SNAPSHOT_V1',version:V,owner:OWNER,at:now(),mode:'active_path_scan_only',atlas_buckets:ATLAS_BUCKETS,repo_file_classification:CLASSIFICATION,documents,slot_status:allSlots(),storage_keys:store(),expected_files:ex.all,missing_expected:ex.missing,indexeddb_owners:INDEXED_DB,rule:registry().rule}}
function scan(reason){let r=registry(),s=snapshot();put(K.registry,r);put(K.snapshot,s);put(K.missing,s.missing_expected);put(K.receipt,{type:'PMP_ACTIVE_PATH_ATLAS_RECEIPT_V1',version:V,owner:OWNER,at:now(),reason:reason||'scan',mode:'passive_only',slot_count:r.slots.length,active_file_count:r.files.filter(x=>x.bucket==='ACTIVE_CURRENT_APP').length,dynamic_file_count:r.files.filter(x=>x.bucket==='DYNAMIC_CURRENT_APP').length,atlas_bucket_count:r.atlas_buckets.length,observed_document_count:s.documents.length,observed_storage_key_count:s.storage_keys.length,missing_expected_count:s.missing_expected.length,expanded_detail:'pass7_current_path_atlas_v21_v29',rule:r.rule});return{registry:r,snapshot:s}}
window.PMPMountRegistryV1={version:V,owner:OWNER,mode:'active_path_registry_only',keys:K,registry,scan,snapshot,atlasBuckets:ATLAS_BUCKETS,repoFileClassification:CLASSIFICATION,rule:'active path atlas only with pass7 current path v21/v29 registered'};
[0,90,270,630,990,1800,2100,2700,3600,6300,9000,18000].forEach(t=>setTimeout(()=>scan('scheduled_'+t),t));
setInterval(()=>scan('slow_watch_9000'),9000);
scan('initial');
})();
