(()=>{
'use strict';
const V='1.0.2-receipt-only-no-visible-host-20260710A';
const OWNER='pmp-owner-diagnostics-host-v1';
const KEY='pmp_owner_diagnostics_host_v1_receipt';
const HOST_ID='pmpOwnerDiagnosticsHostV1';
const RULE='Receipt-only rollback. The legacy Pass 7 owner diagnostics host must not create a visible Diagnostics card in Control. Modern Diagnostics tab owns visible diagnostics.';
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function put(v){try{T().localStorage.setItem(KEY,JSON.stringify(v,null,2))}catch(e){}try{localStorage.setItem(KEY,JSON.stringify(v,null,2))}catch(e){}return v}
function docs(root,arr,depth){arr=arr||[];depth=depth||0;if(!root||depth>10)return arr;try{arr.push(root);Array.from(root.querySelectorAll('iframe,frame')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,arr,depth+1)}catch(e){}})}catch(e){}return arr}
function cleanupAll(){let n=0;docs(T().document).forEach(d=>{try{Array.from(d.querySelectorAll('#'+HOST_ID+', [data-owner-diagnostics-host]')).forEach(x=>{x.remove();n++})}catch(e){}});return n}
function scan(reason){let removed=cleanupAll();let receipt={type:'PMP_OWNER_DIAGNOSTICS_HOST_RECEIPT_V1',version:V,owner:OWNER,at:now(),reason:reason||'scan',mode:'receipt_only_no_visible_host',hosts_created:0,hosts_removed:removed,host_id:HOST_ID,rule:RULE,side_effects:{route_change_attempted:false,storage_migration_attempted:false,bank_rebuild_attempted:false,generic_body_diagnostics_mount:false,visible_host_created:false,ui_move_attempted:false}};put(receipt);return receipt}
window.PMPOwnerDiagnosticsHostV1={version:V,owner:OWNER,scan,rule:RULE};try{T().PMPOwnerDiagnosticsHostV1=window.PMPOwnerDiagnosticsHostV1}catch(e){};
[0,100,250,600,1200,2400,4200,7000].forEach(t=>setTimeout(()=>scan('scheduled_'+t),t));
scan('initial');
})();