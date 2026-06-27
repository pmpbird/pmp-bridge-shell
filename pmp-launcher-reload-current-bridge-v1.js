(()=>{
'use strict';
const V='1.2.0-visible-reload-direct-fallback';
const KEY='pmp_launcher_reload_current_bridge_v1_receipt';
function T(){try{return top||window}catch(e){return window}}
function save(v){try{T().localStorage.setItem(KEY,JSON.stringify(v,null,2))}catch(e){}return v}
function text(x){return String((x&&x.textContent)||'').replace(/\s+/g,' ').trim()}
function clean(s){return String(s||'').replace(/[^a-z0-9]+/gi,' ').trim().toLowerCase()}
function ok(p){return /^#(world|bridge|library|workshop|control|bank)$/i.test(String(p||''))}
function docs(d,a,n){a=a||[];n=n||0;if(!d||n>12)return a;try{a.push(d);d.querySelectorAll('iframe,frame').forEach(f=>{try{let q=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(q)docs(q,a,n+1)}catch(e){}})}catch(e){}return a}
function page(d){try{let h=d.defaultView.location.hash;if(ok(h))return h.toLowerCase()}catch(e){}try{let x=d.querySelector('.screen.on');if(x&&x.id&&ok('#'+x.id))return '#'+x.id.toLowerCase()}catch(e){}try{let b=text(d.body).slice(0,1600);if(/Control Room|Code Safety|Safe Writer/i.test(b))return'#control';if(/Bank Project|Master Bank|Continuous Run Bank|Connections Bank/i.test(b))return'#bank';if(/Workshop/i.test(b))return'#workshop';if(/Library/i.test(b))return'#library';if(/Bridge|Connections/i.test(b))return'#bridge';if(/World|PMP World/i.test(b))return'#world'}catch(e){}return'#world'}
function engine(){let w=T();return w.PMPBankReloadCurrentButtonV1||w.PMPLiveReloadRestoreV12||null}
async function latest(){try{let r=await fetch('pmp-current-map-v9.json?reloadBridge='+Date.now(),{cache:'no-store'});let j=await r.json(),a=j.current_app||{};let p=String(a.path||'pmp-current-inner-cleanbug-rgcontrols-v24.html');let k=String(a.cache_key||j.updated_at||Date.now());if(!/^[a-zA-Z0-9._/-]+\.html$/.test(p))p='pmp-current-inner-cleanbug-rgcontrols-v24.html';return{p,k}}catch(e){return{p:'pmp-current-inner-cleanbug-rgcontrols-v24.html',k:'fallback'}}}
async function directFallback(b){let d=(b&&b.ownerDocument)||document,pg=page(d),t=await latest();let snap={type:'PMP_RELOAD_CURRENT_LIVE_SNAPSHOT_V12',version:V,at:new Date().toISOString(),made_at:Date.now(),page:pg,pressed_text:text(b)};try{T().localStorage.setItem('pmp_reload_current_live_snapshot_v12',JSON.stringify(snap,null,2))}catch(e){}save({type:'PMP_LAUNCHER_RELOAD_CURRENT_BRIDGE_V1_RECEIPT',version:V,at:new Date().toISOString(),status:'DIRECT_FALLBACK_RELOAD_CURRENT_PAGE',snapshot:snap,target:t});window.location.replace(t.p+'?from=bridge-direct-fallback&fresh='+encodeURIComponent(t.k)+'-'+Date.now()+pg);return false}
async function reloadCurrent(e,b){try{if(e){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation()}let eng=engine();if(eng&&typeof eng.run==='function'){save({type:'PMP_LAUNCHER_RELOAD_CURRENT_BRIDGE_V1_RECEIPT',version:V,at:new Date().toISOString(),status:'ROUTING_VISIBLE_RELOAD_TO_RELOAD_CURRENT',button:text(b)});return await eng.run({preventDefault(){},stopPropagation(){},stopImmediatePropagation(){},currentTarget:b||null})}return await directFallback(b)}catch(err){save({type:'PMP_LAUNCHER_RELOAD_CURRENT_BRIDGE_V1_RECEIPT',version:V,at:new Date().toISOString(),status:'ERROR',error:String(err)});return false}}
function patch(d){try{let w=d.defaultView;if(w){w.__pmpLauncherReloadCurrentBridgeV1=true;w.reloadApp=function(){return reloadCurrent(null,null)}}[...d.querySelectorAll('button,a,[role="button"]')].forEach(b=>{let label=clean(text(b)),oc=String(b.getAttribute('onclick')||'').toLowerCase();if(!(label==='reload'||label==='reload current'||oc.includes('reloadapp')))return;if(b.__pmpLauncherReloadCurrentBridgeV1)return;b.__pmpLauncherReloadCurrentBridgeV1=true;b.addEventListener('click',ev=>reloadCurrent(ev,b),true)})}catch(e){}}
function scan(){try{docs(T().document).forEach(patch)}catch(e){}}
T().PMPLauncherReloadCurrentBridgeV1={version:V,disabled:false,scan,reloadCurrent,key:KEY};
addEventListener('load',()=>[100,400,1000,2200,5000,9000].forEach(t=>setTimeout(scan,t)));
setInterval(scan,900);
scan();
})();