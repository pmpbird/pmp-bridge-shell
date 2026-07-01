(()=>{
'use strict';
const V='1.2.0-pass1k-version-aligned-scan-fix';
const REGISTRY_VERSION='1.3.6-pass1k-census-merged';
const OWNER='pmp-mount-registry-doc-url-fix-v1';
const K={registry:'pmp_mount_registry_v1',receipt:'pmp_mount_registry_v1_receipt',snapshot:'pmp_mount_registry_live_snapshot_v1',missing:'pmp_mount_registry_missing_expected_v1'};
const OPTIONAL_ROUTE=['pmp-route-guardian-current-loader-v14.html','pmp-current-reload-owner-v27.html'];
function T(){try{return top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function nameFromUrl(u){return String(u||'').split('?')[0].split('#')[0].split('/').pop()||''}
function get(k,d){try{let v=T().localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){return d}}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function domDocs(){let out=[];function walk(w,n){if(!w||n>12)return;try{let d=w.document,u=String(w.location&&w.location.href||'');out.push({url:u,title:d&&d.title||'',path:nameFromUrl(u)});Array.from(d.querySelectorAll('iframe,frame')).forEach(f=>{try{walk(f.contentWindow,n+1)}catch(e){let src=String(f.getAttribute('src')||f.src||'');out.push({url:src,title:f.title||'',path:nameFromUrl(src),blocked:true})}})}catch(e){}}
walk(T(),0);try{if(window!==T())walk(window,0)}catch(e){}return out}
function mergeDocs(stored){let all=[];(Array.isArray(stored)?stored:[]).forEach(d=>all.push(d));domDocs().forEach(d=>all.push(d));let seen={},out=[];all.forEach(d=>{let p=nameFromUrl(d.url||d.path||'');if(!p||seen[p])return;seen[p]=1;out.push(Object.assign({},d,{path:p}))});return out}
function fixSnapshot(s){if(!s||typeof s!=='object')return s;let docs=mergeDocs(s.documents);let seen=new Set(docs.map(d=>d.path).filter(Boolean));s.documents=docs;s.expected_files=(Array.isArray(s.expected_files)?s.expected_files:[]).map(f=>{let g=Object.assign({},f);if(seen.has(g.path)){g.observed_as_document=true;g.observed_now=true}if(OPTIONAL_ROUTE.indexOf(g.path)>-1){g.active_route_owner=true;g.expected_at_boot=false}return g});s.missing_expected=s.expected_files.filter(f=>f.expected_at_boot&&!f.observed_now&&!/json/i.test(f.path));s.doc_url_scan_fix={version:V,owner:OWNER,at:now(),observed_document_paths:Array.from(seen)};return s}
function fixRecords(reason){let reg=get(K.registry,null),snap=fixSnapshot(get(K.snapshot,null)),missing=snap&&Array.isArray(snap.missing_expected)?snap.missing_expected:[];if(reg){reg.version=REGISTRY_VERSION;reg.doc_url_scan_fix={version:V,owner:OWNER,reason:reason||'fix',at:now()};put(K.registry,reg)}if(snap)put(K.snapshot,snap);put(K.missing,missing);let receipt=get(K.receipt,{});receipt.version=REGISTRY_VERSION;receipt.doc_url_scan_fix_version=V;receipt.missing_expected_count=missing.length;receipt.at=now();put(K.receipt,receipt);try{if(window.PMPMountRegistryV1){window.PMPMountRegistryV1.base_version=window.PMPMountRegistryV1.version;window.PMPMountRegistryV1.version=REGISTRY_VERSION;window.PMPMountRegistryV1.docUrlScanFixVersion=V}}catch(e){}return{missing,registry:reg,snapshot:snap}}
[0,90,270,630,990,1800,2700,3600,6300,9000,12000,18000].forEach(t=>setTimeout(()=>fixRecords('scheduled_'+t),t));
window.PMPMountRegistryDocUrlFixV1={version:V,registry_version:REGISTRY_VERSION,owner:OWNER,fixRecords};
})();
