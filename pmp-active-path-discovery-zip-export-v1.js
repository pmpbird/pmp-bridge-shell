(()=>{
'use strict';
const V='1.0.2-stale-shim-self-removing';
const V1='pmp-active-path-discovery-zip-export-v1.js';
const V2='pmp-active-path-discovery-zip-export-v2.js';
function topWin(){try{return top||window}catch(e){return window}}
function eachDoc(fn){let seen=[];function walk(w,n){if(!w||n>14||seen.indexOf(w)>-1)return;seen.push(w);try{if(w.document)fn(w.document,w);Array.from(w.document.querySelectorAll('iframe,frame')).forEach(f=>{try{walk(f.contentWindow,n+1)}catch(e){}})}catch(e){}}walk(window,0);try{walk(topWin(),0)}catch(e){}}
function hasScript(d,path){try{return !!Array.from(d.querySelectorAll('script[src]')).find(s=>String(s.getAttribute('src')||'').indexOf(path)>-1)}catch(e){return false}}
function removeV1(){eachDoc(d=>{try{Array.from(d.querySelectorAll('script[src]')).forEach(s=>{if(String(s.getAttribute('src')||'').indexOf(V1)>-1)s.remove()})}catch(e){}})}
function loadV2(){eachDoc(d=>{try{if(hasScript(d,V2))return;let s=d.createElement('script');s.src=V2+'?fresh=stale-v1-handoff-20260704K-'+Date.now();s.setAttribute('data-pmp-stale-v1-handoff','1');(d.head||d.documentElement||d.body).appendChild(s)}catch(e){}})}
function installReceipt(){try{topWin().localStorage.setItem('pmp_stale_zip_export_v1_shim_receipt',JSON.stringify({type:'PMP_STALE_ZIP_EXPORT_V1_SHIM_RECEIPT',version:V,at:new Date().toISOString(),action:'removed v1 script tags and loaded v2 if missing'}))}catch(e){}}
function run(){removeV1();loadV2();installReceipt()}
window.PMPActivePathDiscoveryZipExportV1={version:V,stale:true,run};
run();
[100,300,700,1500,3000,6000].forEach(t=>setTimeout(run,t));
})();