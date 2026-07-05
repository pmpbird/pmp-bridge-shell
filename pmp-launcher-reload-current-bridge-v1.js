(()=>{
'use strict';
const V='1.8.0-route-guardian-first-only';
const KEY='pmp_launcher_reload_current_bridge_v1_receipt';
const RG='pmp-route-guardian-current-loader-v20.html';
function T(){try{return top||window}catch(e){return window}}
function save(v){try{T().localStorage.setItem(KEY,JSON.stringify(v,null,2))}catch(e){}return v}
function text(x){return String((x&&x.textContent)||x&&x.value||'').replace(/\s+/g,' ').trim()}
function page(){try{return /^#(world|bridge|library|workshop|control|bank)$/i.test(T().location.hash)?T().location.hash:'#control'}catch(e){return'#control'}}
function reloadCurrent(e,b){try{if(e){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation()}let url=RG+'?from=legacy-launcher-reload&autoRun=1&fresh='+encodeURIComponent(V)+'-'+Date.now()+page();save({type:'PMP_LAUNCHER_RELOAD_CURRENT_BRIDGE_V1_RECEIPT',version:V,status:'ROUTE_GUARDIAN_FIRST_ONLY',pressed_text:text(b),launch_url:url,at:new Date().toISOString(),rule:'Legacy reload bridge only returns to Route Guardian v20. No direct current-owner route.'});T().location.replace(url)}catch(err){save({type:'PMP_LAUNCHER_RELOAD_CURRENT_BRIDGE_V1_RECEIPT',version:V,status:'ERROR',error:String(err),at:new Date().toISOString()})}return false}
function norm(x){return text(x).toLowerCase().replace(/[^a-z0-9]+/g,' ').trim()}
function isReload(b){let s=norm(b),o=String(b&&b.getAttribute&&b.getAttribute('onclick')||'').toLowerCase();return s==='reload'||s==='reload current'||s.includes('reload current')||o.includes('reloadapp')||b&&b.getAttribute&&b.getAttribute('data-launcher-reload-current')}
function docs(d,a,n){a=a||[];n=n||0;if(!d||n>12)return a;try{a.push(d);d.querySelectorAll('iframe,frame').forEach(f=>{try{let q=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(q)docs(q,a,n+1)}catch(e){}})}catch(e){}return a}
function patch(d){try{let w=d.defaultView;if(w)w.reloadApp=function(){return reloadCurrent(null,null)};d.querySelectorAll('button,a,[role="button"],input,[data-launcher-reload-current]').forEach(b=>{if(!isReload(b)||b.__pmpLegacyReloadRG)return;b.__pmpLegacyReloadRG=1;try{b.onclick=null;b.removeAttribute('onclick');b.setAttribute('data-launcher-reload-current','1');if(norm(b)==='reload')b.textContent='Reload Current'}catch(e){}b.addEventListener('click',ev=>reloadCurrent(ev,b),true)})}catch(e){}}
function scan(){try{docs(T().document).forEach(patch)}catch(e){try{patch(document)}catch(x){}}}
T().PMPLauncherReloadCurrentBridgeV1={version:V,scan,reloadCurrent,key:KEY};
addEventListener('load',scan);setInterval(scan,500);scan();
})();