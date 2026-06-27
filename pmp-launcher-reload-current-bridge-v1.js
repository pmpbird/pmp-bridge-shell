(()=>{
'use strict';
const V='1.3.0-direct-app-reload';
const KEY='pmp_launcher_reload_current_bridge_v1_receipt';
function T(){try{return top||window}catch(e){return window}}
function save(v){try{T().localStorage.setItem(KEY,JSON.stringify(v,null,2))}catch(e){}return v}
function txt(x){return String((x&&x.textContent)||x&&x.value||'').replace(/\s+/g,' ').trim()}
function clean(s){return String(s||'').replace(/[^a-z0-9]+/gi,' ').trim().toLowerCase()}
function ok(p){return /^#(world|bridge|library|workshop|control|bank)$/i.test(String(p||''))}
function docs(d,a,n){a=a||[];n=n||0;if(!d||n>12)return a;try{a.push(d);d.querySelectorAll('iframe,frame').forEach(f=>{try{let q=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(q)docs(q,a,n+1)}catch(e){}})}catch(e){}return a}
function currentPage(d){try{let h=d.defaultView.location.hash;if(ok(h))return h.toLowerCase()}catch(e){}try{let x=d.querySelector('.screen.on');if(x&&x.id&&ok('#'+x.id))return '#'+x.id.toLowerCase()}catch(e){}try{let b=txt(d.body).slice(0,1800);if(/Control Room|Code Safety|Safe Writer/i.test(b))return'#control';if(/Bank Project|Master Bank|Continuous Run Bank|Connections Bank|Staging Transfer Store/i.test(b))return'#bank';if(/Workshop/i.test(b))return'#workshop';if(/Library/i.test(b))return'#library';if(/Bridge|Connections/i.test(b))return'#bridge';if(/World|PMP World/i.test(b))return'#world'}catch(e){}return'#world'}
async function latest(){try{let r=await fetch('pmp-current-map-v9.json?reloadBridge='+Date.now(),{cache:'no-store'});let j=await r.json(),a=j.current_app||{};return{path:String(a.path||'pmp-current-reload-owner-v25.html'),key:String(a.cache_key||j.updated_at||Date.now())}}catch(e){return{path:'pmp-current-reload-owner-v25.html',key:'fallback'}}}
async function reloadCurrent(e,b){try{if(e){e.preventDefault();e.stopPropagation()}b=b||(e&&e.currentTarget)||null;let d=(b&&b.ownerDocument)||document;let pg=currentPage(d);let t=await latest();if(!/^[a-zA-Z0-9._/-]+\.html$/.test(t.path))t.path='pmp-current-reload-owner-v25.html';let snap={type:'PMP_RELOAD_CURRENT_LIVE_SNAPSHOT_V12',version:V,at:new Date().toISOString(),made_at:Date.now(),page:pg,pressed_text:txt(b)};try{T().localStorage.setItem('pmp_reload_current_live_snapshot_v12',JSON.stringify(snap,null,2));T().localStorage.setItem('pmp_reload_current_live_snapshot_v12_last_kept',JSON.stringify(snap,null,2))}catch(x){}save({type:'PMP_LAUNCHER_RELOAD_CURRENT_BRIDGE_V1_RECEIPT',version:V,status:'DIRECT_APP_RELOAD',snapshot:snap,target:t,at:new Date().toISOString()});window.location.replace(t.path+'?from=bridge-direct-fallback&fresh='+encodeURIComponent(t.key)+'-'+Date.now()+pg)}catch(err){save({type:'PMP_LAUNCHER_RELOAD_CURRENT_BRIDGE_V1_RECEIPT',version:V,status:'ERROR',error:String(err),at:new Date().toISOString()})}return false}
function isReload(b){let s=clean(txt(b)),o=String(b.getAttribute('onclick')||'').toLowerCase();return s==='reload'||s==='reload current'||s==='reload app'||s.includes('reload')||o.includes('reloadapp')}
function patch(d){try{let w=d.defaultView;if(w){w.reloadApp=function(){return reloadCurrent(null,null)}}[...d.querySelectorAll('button,a,[role="button"],input')].forEach(b=>{if(!isReload(b)||b.__pmpReloadBridgeV13)return;b.__pmpReloadBridgeV13=1;try{b.onclick=null;b.removeAttribute('onclick');if(clean(txt(b))==='reload')b.textContent='Reload Current'}catch(e){}b.addEventListener('click',ev=>reloadCurrent(ev,b),true)})}catch(e){}}
function scan(){try{docs(T().document).forEach(patch)}catch(e){}}
T().PMPLauncherReloadCurrentBridgeV1={version:V,scan,reloadCurrent,key:KEY};
addEventListener('load',()=>[80,300,900,2000,5000,9000].forEach(t=>setTimeout(scan,t)));
setInterval(scan,800);scan();
})();