(()=>{
'use strict';
const V='1.0.1-passive-floating-path-stamp';
const RECEIPT_KEY='pmp_current_path_stamp_v1';
function now(){return new Date().toISOString()}
function topWin(){try{return top||window}catch(e){return window}}
function eachWin(fn){let seen=[];function walk(w,n){if(!w||n>14||seen.indexOf(w)>-1)return;seen.push(w);try{fn(w);Array.from(w.document.querySelectorAll('iframe,frame')).forEach(f=>{try{walk(f.contentWindow,n+1)}catch(e){}})}catch(e){}}walk(window,0);try{walk(topWin(),0)}catch(e){}}
function eachDoc(fn){eachWin(w=>{try{if(w.document)fn(w.document,w)}catch(e){}})}
function clean(x){return String(x||'').split('#')[0].split('?')[0].split('/').pop()}
function readLocal(k){let out=null;eachWin(w=>{if(out)return;try{let raw=w.localStorage&&w.localStorage.getItem(k);if(raw)out=JSON.parse(raw)}catch(e){}});return out}
function seenFiles(){let files=[];eachWin(w=>{try{files.push(clean(w.location&&w.location.pathname));Array.from(w.document.querySelectorAll('script[src],iframe[src],frame[src],a[href]')).forEach(el=>files.push(clean(el.getAttribute('src')||el.getAttribute('href'))))}catch(e){}});return Array.from(new Set(files.filter(Boolean)))}
function status(){let files=seenFiles(),href='';try{href=String((topWin().location&&topWin().location.href)||location.href)}catch(e){href=String(location.href||'')}
let receipt=readLocal('pmp_historic_v27_forward_receipt_v1');
let hasV20=files.indexOf('pmp-route-guardian-current-loader-v20.html')>=0||/route-guardian-current-loader-v20/i.test(href);
let hasV28=files.indexOf('pmp-current-reload-owner-v28.html')>=0||/pmp-current-reload-owner-v28/i.test(href);
let hasV29=files.indexOf('pmp-current-inner-cleanbug-rgcontrols-v29.html')>=0||/pmp-current-inner-cleanbug-rgcontrols-v29/i.test(href);
let old=[];['pmp-route-guardian-current-loader-v18.html','pmp-route-guardian-current-loader-v19.html','pmp-current-reload-owner-v27.html','pmp-current-inner-cleanbug-rgcontrols-v26.html','pmp-current-map-v9.json'].forEach(f=>{if(files.indexOf(f)>=0||href.indexOf(f)>=0)old.push(f)});
if(receipt&&receipt.type==='PMP_HISTORIC_V27_FORWARD_RECEIPT_V1'&&hasV28)old=old.filter(x=>x!=='pmp-current-reload-owner-v27.html');
let ok=hasV28&&hasV29&&old.length===0;
return{type:'PMP_CURRENT_PATH_STAMP_V1',version:V,at:now(),status:ok?'CURRENT PATH: PASS 7':'WRONG PATH: OLD ROUTE DETECTED',pass7_current:ok,expected:'v20 -> v28 -> v29 -> v23 -> v4 -> v3 -> home v6',seen:{v20:hasV20,v28:hasV28,v29:hasV29},old_route_files:old,href,files:files.slice(0,80),historic_forward_receipt_present:!!receipt}}
function removeOldCards(d){try{let old=d.getElementById('pmpCurrentPathStampV1');if(old)old.remove()}catch(e){}}
function install(){eachDoc(d=>{try{removeOldCards(d);let st=status();let bar=d.getElementById('pmpCurrentPathStampFloatingV1');if(!bar){bar=d.createElement('div');bar.id='pmpCurrentPathStampFloatingV1';bar.setAttribute('data-pmp-section-owner','current_path_stamp_passive_overlay');bar.setAttribute('data-pmp-not-control-card','1');d.body.appendChild(bar)}let ok=st.pass7_current;bar.textContent=(ok?'PASS 7 CURRENT':'OLD ROUTE DETECTED')+' · v28 '+st.seen.v28+' · v29 '+st.seen.v29+' · old '+st.old_route_files.length;bar.style.cssText='position:fixed;left:10px;right:10px;bottom:calc(74px + env(safe-area-inset-bottom));z-index:2147483000;pointer-events:none;text-align:center;border:2px solid #07101c;border-radius:999px;padding:7px 10px;background:'+(ok?'#dfffe4':'#ffe1df')+';color:#07101c;font:950 11px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;box-shadow:0 4px 16px rgba(0,0,0,.18);white-space:nowrap;overflow:hidden;text-overflow:ellipsis';try{localStorage.setItem(RECEIPT_KEY,JSON.stringify(st,null,2))}catch(e){}}catch(e){}})}
window.PMPCurrentPathStampV1={version:V,status,install};
[100,300,700,1200,2000,3500,5500,8000,12000,18000,26000,40000,60000].forEach(t=>setTimeout(install,t));
setInterval(install,2000);
})();