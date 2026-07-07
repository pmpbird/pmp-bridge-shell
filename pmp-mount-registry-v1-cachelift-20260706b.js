(()=>{
'use strict';
const V='1.6.1-pass7-cachelift-force-loader-121';
const OWNER='pmp-mount-registry-v1-cachelift-20260706b';
const KEY='pmp_mount_registry_cachelift_loader_force_receipt_v1';
const LOADER_ID='pmpContinuousRunBankOrderFrameLoaderV1DirectFrame';
const FRESH='pass7-loader-forces-registry-probe-scans-20260706N';
const LATEST_SRC='pmp-continuous-run-bank-order-frame-loader-v1.js?fresh='+FRESH;
const RULE='Cachelift bridge only. Forces Pass 7 frame loader 1.2.1+ into the current iframe when an older forced loader is present. No route change, no storage migration, no Bank rebuild, no ownership takeover.';
function now(){return new Date().toISOString()}
function T(){try{return window.top||window}catch(e){return window}}
function put(v){try{localStorage.setItem(KEY,JSON.stringify(v,null,2))}catch(e){}try{T().localStorage.setItem(KEY,JSON.stringify(v,null,2))}catch(e){}return v}
function docs(root,out,depth){out=out||[];depth=depth||0;if(!root||depth>8)return out;try{out.push(root);Array.from(root.querySelectorAll('iframe,frame')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,out,depth+1)}catch(e){}})}catch(e){}return out}
function injectDoc(d){let events=[];if(!d||!d.body)return{made:0,events:['no_body']};try{let old=d.getElementById(LOADER_ID);if(old){let src=old.getAttribute('src')||'';if(src.indexOf(FRESH)>=0)return{made:0,events:['latest_loader_121_already_present']};events.push('removed_old_loader:'+src);try{old.remove()}catch(e){events.push('remove_old_loader_error:'+String(e&&e.message||e))}}
let s=d.createElement('script');s.id=LOADER_ID;s.src=LATEST_SRC+'-'+Date.now();s.onload=()=>{try{put({type:'PMP_MOUNT_REGISTRY_CACHELIFT_LOADER_FORCE_RECEIPT_V1',version:V,owner:OWNER,at:now(),event:'latest_loader_121_loaded',src:s.src,rule:RULE})}catch(e){}};s.onerror=()=>{try{put({type:'PMP_MOUNT_REGISTRY_CACHELIFT_LOADER_FORCE_RECEIPT_V1',version:V,owner:OWNER,at:now(),event:'latest_loader_121_error',src:s.src,rule:RULE})}catch(e){}};d.body.appendChild(s);events.push('latest_loader_121_injected:'+s.src);return{made:1,events}}catch(e){events.push('inject_exception:'+String(e&&e.message||e));return{made:0,events}}}
function scan(reason){let made=0,events=[],seen=0;try{docs(document).forEach(d=>{seen++;let r=injectDoc(d);made+=r.made||0;events=events.concat(r.events||[])})}catch(e){events.push('scan_exception:'+String(e&&e.message||e))}let receipt={type:'PMP_MOUNT_REGISTRY_CACHELIFT_LOADER_FORCE_RECEIPT_V1',version:V,owner:OWNER,at:now(),reason:reason||'scan',documents_seen:seen,latest_loader_src:LATEST_SRC,loaders_injected:made,events:events.slice(-30),rule:RULE,side_effects:{route_change_attempted:false,indexeddb_write_attempted:false,bank_rebuild_attempted:false,storage_migration_attempted:false,section_takeover_attempted:false}};put(receipt);return receipt}
window.PMPMountRegistryCacheliftLoaderForceV1={version:V,owner:OWNER,scan,rule:RULE};
[0,50,150,350,700,1200,2200,4200,7000].forEach(t=>setTimeout(()=>scan('scheduled_'+t),t));setInterval(()=>scan('slow_watch_4000'),4000);scan('initial');
})();