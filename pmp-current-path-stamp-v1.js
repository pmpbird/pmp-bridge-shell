(()=>{
'use strict';
const V='1.0.2-control-room-footer-path-stamp';
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
function removeOld(d){try{let a=d.getElementById('pmpCurrentPathStampV1');if(a)a.remove()}catch(e){}try{let b=d.getElementById('pmpCurrentPathStampFloatingV1');if(b)b.remove()}catch(e){}}
function install(){eachDoc(d=>{try{removeOld(d);let control=d.getElementById('control');if(!control)return;let st=status(),ok=st.pass7_current;let foot=d.getElementById('pmpCurrentPathStampFooterV1');if(!foot){foot=d.createElement('div');foot.id='pmpCurrentPathStampFooterV1';foot.setAttribute('data-pmp-section-owner','current_path_stamp_footer');foot.setAttribute('data-pmp-footer-stamp','1');control.appendChild(foot)}if(foot.parentNode!==control)control.appendChild(foot);foot.textContent=(ok?'PASS 7 CURRENT':'OLD ROUTE DETECTED')+' · v28 '+st.seen.v28+' · v29 '+st.seen.v29+' · old '+st.old_route_files.length;foot.style.cssText='position:relative;display:block;box-sizing:border-box;width:calc(100% - 24px);margin:18px 12px 24px;padding:10px 12px;text-align:center;border:3px solid #07101c;border-radius:999px;background:'+(ok?'#dfffe4':'#ffe1df')+';color:#07101c;font:950 13px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;box-shadow:0 8px 24px rgba(0,0,0,.20);white-space:nowrap;overflow:hidden;text-overflow:ellipsis';try{localStorage.setItem(RECEIPT_KEY,JSON.stringify(st,null,2))}catch(e){}}catch(e){}})}
window.PMPCurrentPathStampV1={version:V,status,install};
[100,300,700,1200,2000,3500,5500,8000,12000,18000,26000,40000,60000].forEach(t=>setTimeout(install,t));
setInterval(install,2000);
})();