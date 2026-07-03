(()=>{
'use strict';
const V='1.0.0-pass4-boot-status-strip-owner';
const OWNER='pmp-boot-status-strip-owner-v1';
const STRIP_ID='pmpAppOrchestratorBootStatusStripV1';
const STYLE_ID='pmpBootStatusStripOwnerV1Style';
const RECEIPT_KEY='pmp_boot_status_strip_owner_v1_receipt';
const STATUS_KEY='pmp_boot_status_strip_owner_v1_status';
const SLOW_MS=9000;
const READY_HIDE_MS=420;
let bootAt=Date.now(),hidden=false,readySeen=false,lastState=null,lastReceipt=null;
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function esc(s){return String(s==null?'':s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function safeText(s,n){s=String(s==null?'':s).replace(/\s+/g,' ').trim();return n&&s.length>n?s.slice(0,n):s}
function docs(root,arr,path,depth){arr=arr||[];path=path||'top';depth=depth||0;if(!root||depth>12)return arr;try{arr.push({doc:root,path,url:String(root.location&&root.location.href||''),title:root.title||''});Array.from(root.querySelectorAll('iframe,frame')).forEach((f,i)=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,arr,path+' > frame['+i+'] '+safeText(f.title||'',40),depth+1)}catch(e){arr.push({doc:null,path:path+' > frame['+i+']',url:'blocked',title:'blocked',error:String(e&&e.message||e)})}})}catch(e){}return arr}
function allDocs(){try{return docs(T().document)}catch(e){return []}}
function hasFile(list,name){return (list||[]).some(x=>String(x.url||'').indexOf(name)>-1)}
function hasVisibleApp(list){try{return (list||[]).some(x=>x.doc&&x.doc.querySelector&&x.doc.querySelector('[data-tab="bank"],#bank,#control,[data-screen="control"]'))}catch(e){return false}}
function appOrchestratorLoaded(){try{return !!(window.PMPAppOrchestratorV1||(window.parent&&window.parent.PMPAppOrchestratorV1)||(T().PMPAppOrchestratorV1))}catch(e){return false}}
function mountRegistryLoaded(){try{return !!(window.PMPMountRegistryV1||(window.parent&&window.parent.PMPMountRegistryV1)||(T().PMPMountRegistryV1))}catch(e){return false}}
function compute(){let list=allDocs();let checks={route_guardian_v16:hasFile(list,'pmp-route-guardian-current-loader-v16.html'),current_reload_v27:hasFile(list,'pmp-current-reload-owner-v27.html'),current_inner_v26:hasFile(list,'pmp-current-inner-cleanbug-rgcontrols-v26.html'),inner_v23:hasFile(list,'pmp-current-inner-cleanbug-rgcontrols-v23.html'),app_orchestrator_loaded:appOrchestratorLoaded(),mount_registry_loaded:mountRegistryLoaded(),visible_app_anchor:hasVisibleApp(list)};let state='BOOTING',label='Booting…';if(checks.route_guardian_v16) {state='ROUTE_GUARDIAN_OK';label='Route Guardian OK';}
if(checks.app_orchestrator_loaded) {state='APP_ORCHESTRATOR_OK';label='App Orchestrator OK';}
if(checks.mount_registry_loaded) {state='MOUNT_REGISTRY_OK';label='Mount Registry OK';}
if(checks.current_inner_v26) {state='APP_LOADING';label='App Loading…';}
if(checks.inner_v23||checks.visible_app_anchor){state='APP_READY';label='App Ready';}
if(Date.now()-bootAt>SLOW_MS&&state!=='APP_READY'){state='BOOT_SLOW';label='Boot Slow — still watching';}
return{type:'PMP_BOOT_STATUS_STRIP_OWNER_V1_STATUS',version:V,owner:OWNER,at:now(),elapsed_ms:Date.now()-bootAt,state,label,checks,documents:list.map(x=>({path:x.path,url:x.url,title:x.title,blocked:!x.doc,error:x.error||null})),rule:'Passive visual/status layer only. No route change, no Bank rebuild, no level reorder, no Resident change, no storage migration.'}}
function ensureStyle(d){let st=d.getElementById(STYLE_ID);if(st)return st;st=d.createElement('style');st.id=STYLE_ID;st.textContent='#'+STRIP_ID+'{position:fixed;left:10px;right:10px;top:calc(6px + env(safe-area-inset-top));z-index:2147483647;pointer-events:none;display:flex;justify-content:center;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}#'+STRIP_ID+' span{max-width:min(520px,calc(100vw - 20px));overflow:hidden;text-overflow:ellipsis;white-space:nowrap;background:rgba(255,255,255,.96);color:#07101c;border:2px solid #07101c;border-radius:999px;padding:7px 12px;font-size:12px;font-weight:950;box-shadow:0 6px 18px rgba(0,0,0,.14)}#'+STRIP_ID+'[data-state="BOOT_SLOW"] span{background:#fff3de}';(d.head||d.documentElement).appendChild(st);return st}
function ensureStrip(){if(hidden)return null;let d=document;if(!d||!d.body)return null;ensureStyle(d);let x=d.getElementById(STRIP_ID);if(!x){x=d.createElement('div');x.id=STRIP_ID;x.innerHTML='<span>Booting…</span>';d.body.appendChild(x)}x.setAttribute('data-pmp-boot-status-strip-owner','true');return x}
function paint(status){if(hidden)return;let x=ensureStrip();if(!x)return;x.setAttribute('data-state',status.state);let span=x.querySelector('span')||x;span.innerHTML=esc(status.label);}
function hide(reason){if(hidden)return;hidden=true;let receipt=lastReceipt||makeReceipt(lastState||compute(),reason||'hidden');receipt.hidden_at=now();receipt.hide_reason=reason||'hidden';put(RECEIPT_KEY,receipt);try{let x=document.getElementById(STRIP_ID);if(x)x.remove()}catch(e){}try{let st=document.getElementById(STYLE_ID);if(st)st.remove()}catch(e){} }
function makeReceipt(status,reason){return{type:'PMP_BOOT_STATUS_STRIP_OWNER_V1_RECEIPT',version:V,owner:OWNER,at:now(),mode:'passive_boot_status_strip_only',reason:reason||'status',state:status.state,label:status.label,elapsed_ms:status.elapsed_ms,checks:status.checks,passive_only:true,route_change:false,bank_rebuild:false,level_reorder:false,resident_change:false,storage_migration:false,rule:status.rule}}
function tick(reason){let status=compute();lastState=status;put(STATUS_KEY,status);paint(status);let receipt=makeReceipt(status,reason||'tick');lastReceipt=receipt;put(RECEIPT_KEY,receipt);if(status.state==='APP_READY'&&!readySeen){readySeen=true;setTimeout(()=>hide('app_ready_auto_hide_'+READY_HIDE_MS+'ms'),READY_HIDE_MS)}return receipt}
function bindFrameLoad(){try{let f=document.getElementById('app');if(f&&!f.__pmpBootStatusStripOwnerBound){f.__pmpBootStatusStripOwnerBound=true;f.addEventListener('load',()=>tick('inner_frame_load'),false)}}catch(e){}}
function start(){bindFrameLoad();tick('start');[90,270,630,990,1530,2100,2700,3600,5400,7200,9000].forEach(ms=>setTimeout(()=>tick('scheduled_'+ms),ms));let fast=setInterval(()=>{let r=tick('watch');if(hidden||Date.now()-bootAt>12000)clearInterval(fast)},180)}
window.PMPBootStatusStripOwnerV1={version:V,owner:OWNER,mode:'passive_boot_status_strip_only',scan:compute,tick,hide,getLastReceipt:()=>lastReceipt,rule:'Passive visual/status layer only. No route change, no Bank rebuild, no level reorder, no Resident change, no storage migration.'};
try{start()}catch(e){put(RECEIPT_KEY,{type:'PMP_BOOT_STATUS_STRIP_OWNER_V1_RECEIPT',version:V,owner:OWNER,at:now(),status:'ERROR',error:String(e&&e.message||e),passive_only:true})}
})();