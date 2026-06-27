(()=>{
'use strict';
const V='1.1.0-enabled-visible-reload-to-reload-current';
const KEY='pmp_launcher_reload_current_bridge_v1_receipt';
function T(){try{return top||window}catch(e){return window}}
function save(v){try{T().localStorage.setItem(KEY,JSON.stringify(v,null,2))}catch(e){}return v}
function text(x){return String((x&&x.textContent)||'').replace(/\s+/g,' ').trim()}
function clean(s){return String(s||'').replace(/[^a-z0-9]+/gi,' ').trim().toLowerCase()}
function docs(d,a,n){a=a||[];n=n||0;if(!d||n>12)return a;try{a.push(d);d.querySelectorAll('iframe,frame').forEach(f=>{try{let q=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(q)docs(q,a,n+1)}catch(e){}})}catch(e){}return a}
function engine(){let w=T();return w.PMPBankReloadCurrentButtonV1||w.PMPLiveReloadRestoreV12||null}
async function reloadCurrent(e,b){try{if(e){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation()}let eng=engine();save({type:'PMP_LAUNCHER_RELOAD_CURRENT_BRIDGE_V1_RECEIPT',version:V,at:new Date().toISOString(),status:eng?'ROUTING_VISIBLE_RELOAD_TO_RELOAD_CURRENT':'RELOAD_CURRENT_ENGINE_NOT_FOUND',button:text(b)});if(eng&&typeof eng.run==='function')return await eng.run({preventDefault(){},stopPropagation(){},stopImmediatePropagation(){},currentTarget:b||null});}catch(err){save({type:'PMP_LAUNCHER_RELOAD_CURRENT_BRIDGE_V1_RECEIPT',version:V,at:new Date().toISOString(),status:'ERROR',error:String(err)})}return false}
function patch(d){try{let w=d.defaultView;if(w&&!w.__pmpLauncherReloadCurrentBridgeV1){w.__pmpLauncherReloadCurrentBridgeV1=true;w.reloadApp=function(){return reloadCurrent(null,null)}}[...d.querySelectorAll('button,a,[role="button"]')].forEach(b=>{let label=clean(text(b)),oc=String(b.getAttribute('onclick')||'').toLowerCase();if(!(label==='reload'||label==='reload current'||oc.includes('reloadapp')))return;if(b.__pmpLauncherReloadCurrentBridgeV1)return;b.__pmpLauncherReloadCurrentBridgeV1=true;b.addEventListener('click',ev=>reloadCurrent(ev,b),true)})}catch(e){}}
function scan(){try{docs(T().document).forEach(patch)}catch(e){}}
T().PMPLauncherReloadCurrentBridgeV1={version:V,disabled:false,scan,reloadCurrent,key:KEY};
addEventListener('load',()=>[100,400,1000,2200,5000,9000].forEach(t=>setTimeout(scan,t)));
setInterval(scan,900);
scan();
})();