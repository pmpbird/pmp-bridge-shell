(()=>{
'use strict';
const V='1.0.0-launcher-background-current-reload-v1';
const RECEIPT='pmp_launcher_background_current_reload_v1_receipt';
const RG='pmp-route-guardian-v1.js?fresh=launcher-bg-current-reload-v1';
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function text(x){return clean(x&&x.textContent)}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>8)return a;try{a.push(r);r.querySelectorAll('iframe').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function frameChain(){let out=[];function walk(w,n){if(!w||n>8)return;try{out.push(w);Array.from(w.document.querySelectorAll('iframe')).forEach(f=>{try{if(f.contentWindow)walk(f.contentWindow,n+1)}catch(e){}})}catch(e){}}walk(T(),0);return out}
function routeFrom(w){try{let h=w.location&&w.location.hash;if(h&&h!=='#')return h}catch(e){}try{let on=w.document&&w.document.querySelector&&w.document.querySelector('.screen.on[id]');if(on&&on.id)return '#'+on.id}catch(e){}try{let tab=w.document&&Array.from(w.document.querySelectorAll('.tab.on')).find(Boolean);let t=text(tab).toLowerCase();if(t){if(t.includes('world'))return '#world';if(t.includes('bridge'))return '#bridge';if(t.includes('library'))return '#library';if(t.includes('workshop'))return '#workshop';if(t.includes('control'))return '#control';if(t.includes('bank'))return '#bank'}}catch(e){}return ''}
function currentRoute(){let ws=frameChain().reverse();for(const w of ws){let r=routeFrom(w);if(r)return r}try{return T().location.hash||'#control'}catch(e){return '#control'}}
function loadRG(){return new Promise(res=>{try{if(T().PMPRouteGuardianV1)return res(true);let d=T().document;if(d.getElementById('pmpLauncherBgReloadRouteGuardianV1'))return setTimeout(()=>res(!!T().PMPRouteGuardianV1),250);let s=d.createElement('script');s.id='pmpLauncherBgReloadRouteGuardianV1';s.src=RG;s.onload=()=>res(true);s.onerror=()=>res(false);d.head.appendChild(s);setTimeout(()=>res(!!T().PMPRouteGuardianV1),900)}catch(e){res(false)}})}
async function guard(route){let ok=await loadRG(),report=null,err='';try{if(ok&&T().PMPRouteGuardianV1&&typeof T().PMPRouteGuardianV1.buildReport==='function')report=await T().PMPRouteGuardianV1.buildReport({store:false,source:'launcher_background_reload',route:route})}catch(e){err=String(e.message||e)}return put(RECEIPT,{type:'PMP_LAUNCHER_BACKGROUND_CURRENT_RELOAD_RECEIPT_V1',version:V,at:now(),route:route,used_route_guardian:!!report,verdict:report&&report.verdict||'',route_guardian_error:err})}
function topAppFrame(){try{return T().document.getElementById('app')||T().document.querySelector('iframe#app')||T().document.querySelector('iframe')}catch(e){return null}}
function forceRoute(route,tries){tries=tries||0;if(tries>20)return;frameChain().forEach(w=>{try{if(w.location&&w.location.hash!==route)w.history.replaceState(null,'',route)}catch(e){}try{if(typeof w.go==='function')w.go(route.replace(/^#/,''))}catch(e){}});setTimeout(()=>forceRoute(route,tries+1),150)}
async function reload(e){if(e){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation()}let route=currentRoute()||'#control';await guard(route);try{T().history.replaceState(null,'',route)}catch(e){}let f=topAppFrame();if(f){try{f.src='pmp-current-inner-cleanbug-rgcontrols-v3.html?from=launcher-background-current-reload-v1&fresh=launcher-bg-current-'+Date.now()+route}catch(e){try{f.contentWindow.location.replace('pmp-current-inner-cleanbug-rgcontrols-v3.html?from=launcher-background-current-reload-v1&fresh=launcher-bg-current-'+Date.now()+route)}catch(x){}}}else{try{T().location.replace('pmp-current-inner-cleanbug-rgcontrols-v4.html?from=launcher-background-current-reload-v1&fresh=launcher-bg-current-'+Date.now()+route)}catch(e){}}
setTimeout(()=>forceRoute(route,0),350);return false}
function install(d){try{Array.from(d.querySelectorAll('button,a')).forEach(b=>{if(text(b)!=='Reload')return;if(b.dataset.pmpLauncherBgCurrentReloadV1)return;b.dataset.pmpLauncherBgCurrentReloadV1='1';b.onclick=reload;b.addEventListener('click',reload,true)})}catch(e){}try{let w=d.defaultView||d.parentWindow;if(w&&!w.__pmpLauncherBgCurrentReloadV1){w.__pmpLauncherBgCurrentReloadV1=true;w.reloadApp=reload}}catch(e){}}
function scan(){docs(T().document).forEach(d=>install(d))}
T().PMPLauncherBackgroundCurrentReloadV1={version:V,reload:reload,route:currentRoute,receipt:()=>{try{return JSON.parse(T().localStorage.getItem(RECEIPT)||'null')}catch(e){return null}}};
window.addEventListener('load',()=>[250,800,1800,4000].forEach(t=>setTimeout(scan,t)));
setInterval(scan,700);scan();
})();