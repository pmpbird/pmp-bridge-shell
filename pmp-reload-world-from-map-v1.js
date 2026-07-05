(()=>{
'use strict';
const V='1.0.2-route-guardian-v20-first-visible';
const OWNER='pmp-reload-world-from-map-v1';
const ROUTE_GUARDIAN='pmp-route-guardian-current-loader-v20.html';
const MAPS=['pmp-current-map-v11.json','pmp-current-map-v10.json'];
let busy=false,last=0;
async function readMap(){let lastErr=null;for(let p of MAPS){try{let r=await fetch(p+'?reload-current-v1='+encodeURIComponent(V)+'-'+Date.now(),{cache:'no-store',headers:{'Cache-Control':'no-cache'}});if(!r.ok)throw Error(p+' '+r.status);let m=await r.json();m._path=p;return m}catch(e){lastErr=e}}throw lastErr||Error('no current map')}
async function target(){let m=await readMap(),g=m.route_guardian_loader||{};let key=String(g.cache_key||m.updated_at||V);return{map:m,path:ROUTE_GUARDIAN,key}}
function page(){try{return /^#(world|bridge|library|workshop|control|bank)$/i.test(location.hash)?location.hash:'#control'}catch(e){return'#control'}}
async function go(e){
  if(e){e.preventDefault();e.stopPropagation();if(e.stopImmediatePropagation)e.stopImmediatePropagation()}
  let n=Date.now();if(busy||n-last<1200)return false;busy=true;last=n;
  let got;
  try{got=await target()}catch(x){got={path:ROUTE_GUARDIAN,key:V,map:{error:String(x&&x.message||x)}}}
  let url=ROUTE_GUARDIAN+'?from=reload-current-v1&autoRun=1&fresh=reload-current-'+encodeURIComponent(V)+'-'+encodeURIComponent(got.key)+'-'+Date.now()+page();
  let receipt={type:'PMP_RELOAD_CURRENT_V1_RECEIPT',version:V,owner:OWNER,at:new Date().toISOString(),target:ROUTE_GUARDIAN,cache_key:got.key,map_path:got.map&&got.map._path,map_route_guardian:got.map&&got.map.route_guardian_loader||null,map_current_app:got.map&&got.map.current_app||null,map_updated_at:got.map&&got.map.updated_at||null,launch_url:url,rule:'Reload Current must return to Route Guardian v20 first. Route Guardian then opens current v28/v29 App Orchestrator. No direct v28, v27, v9, v18, or pass4 route.'};
  try{localStorage.setItem('pmp_reload_current_v1_receipt',JSON.stringify(receipt,null,2))}catch(e){}
  try{(window.top||window).location.replace(url)}catch(e2){location.href=url}
  return false;
}
function t(x){return String((x&&x.textContent)||x&&x.value||'').toLowerCase().trim()}
function is(b){let s=t(b),o=String(b&&b.getAttribute&&b.getAttribute('onclick')||'').toLowerCase();return s==='reload'||s==='reload current'||s.includes('reload current')||o.includes('reloadapp')||b&&b.getAttribute&&b.getAttribute('data-launcher-reload-current')}
function docs(d,a,n){a=a||[];n=n||0;if(!d||n>8)return a;try{a.push(d);d.querySelectorAll('iframe').forEach(f=>{try{if(f.contentDocument)docs(f.contentDocument,a,n+1)}catch(e){}})}catch(e){}return a}
function patch(d){try{let w=d.defaultView;if(w)w.reloadApp=function(){return go(null)};d.querySelectorAll('button,a,input,[role="button"],[data-launcher-reload-current]').forEach(b=>{if(is(b)){b.setAttribute('data-launcher-reload-current','1');b.onclick=function(e){return go(e)}}});if(!d.__reloadWorldMap){d.__reloadWorldMap=1;d.addEventListener('click',e=>{let b=e.target&&e.target.closest&&e.target.closest('button,a,input,[role="button"]');if(is(b))return go(e)},true)}}catch(e){}}
function scan(){try{top.PMPLauncherReloadCurrentBridgeV1=top.PMPLauncherReloadCurrentBridgeV1||{};top.PMPLauncherReloadCurrentBridgeV1.version=V;top.PMPLauncherReloadCurrentBridgeV1.reloadCurrent=go;docs(top.document).forEach(patch)}catch(e){patch(document)}}
addEventListener('load',scan);setInterval(scan,500);scan();
})();