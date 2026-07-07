(()=>{
'use strict';
const V='1.0.1-pass7-active-control-only-diagnostics-host';
const OWNER='pmp-owner-diagnostics-host-v1';
const KEY='pmp_owner_diagnostics_host_v1_receipt';
const HOST_ID='pmpOwnerDiagnosticsHostV1';
const RULE='Creates one explicit diagnostics host only when the active route hash is #control. Removes hosted Diagnostics from all other tabs/routes. No route change, no storage migration, no Bank rebuild, no ownership takeover.';
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function put(v){try{T().localStorage.setItem(KEY,JSON.stringify(v,null,2))}catch(e){}try{localStorage.setItem(KEY,JSON.stringify(v,null,2))}catch(e){}return v}
function docs(root,arr,depth){arr=arr||[];depth=depth||0;if(!root||depth>10)return arr;try{arr.push(root);Array.from(root.querySelectorAll('iframe,frame')).forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,arr,depth+1)}catch(e){}})}catch(e){}return arr}
function visible(el){try{let w=el.ownerDocument.defaultView,cs=w.getComputedStyle(el),r=el.getBoundingClientRect();return cs.display!=='none'&&cs.visibility!=='hidden'&&r.width>0&&r.height>0&&!el.hidden}catch(e){return false}}
function activeHash(d){try{return String(d.defaultView&&d.defaultView.location&&d.defaultView.location.hash||'').toLowerCase()}catch(e){return''}}
function isControlDoc(d){return activeHash(d)==='#control'}
function cardForControl(d){try{let hs=Array.from(d.querySelectorAll('h1,h2,h3')).filter(x=>/Control Room/i.test(String(x.textContent||''))&&visible(x));for(let h of hs){let n=h;for(let i=0;i<5&&n&&n!==d.body;i++,n=n.parentElement){let t=String(n.textContent||'');if(/Control Room/i.test(t)&&/Open Safe Writer/i.test(t)&&visible(n))return n}return h.parentElement||d.body}}catch(e){}return d.body}
function cleanupAll(d,force){let n=0;try{Array.from(d.querySelectorAll('#'+HOST_ID+', [data-owner-diagnostics-host]')).forEach(x=>{if(force||!isControlDoc(d)){x.remove();n++}})}catch(e){}return n}
function style(d){if(d.getElementById(HOST_ID+'Style'))return;let s=d.createElement('style');s.id=HOST_ID+'Style';s.textContent='[data-owner-diagnostics-host]{margin:14px 0;padding:10px;border:3px solid rgba(0,0,0,.18);border-radius:18px;background:rgba(255,255,255,.68);box-sizing:border-box}[data-owner-diagnostics-host] h2{font-size:22px;margin:0 0 8px;font-weight:950}';(d.head||d.documentElement).appendChild(s)}
function ensure(d){if(!d||!d.body)return{made:false,removed:0,hash:''};let hash=activeHash(d);let removed=cleanupAll(d,false);if(hash!=='#control')return{made:false,removed,hash};let old=d.getElementById(HOST_ID);if(old)return{made:false,removed,exists:true,hash};style(d);let host=d.createElement('section');host.id=HOST_ID;host.setAttribute('data-owner-diagnostics-host','true');host.innerHTML='<h2>Diagnostics</h2>';let card=cardForControl(d);try{card.appendChild(host)}catch(e){d.body.appendChild(host)}return{made:true,removed,hash};}
function scan(reason){let made=0,removed=0,seen=0,controlDocs=0,hashes=[];docs(T().document).forEach(d=>{try{let r=ensure(d);seen++;if(r.hash)hashes.push(r.hash);if(r.hash==='#control')controlDocs++;if(r.made)made++;removed+=r.removed||0}catch(e){}});let receipt={type:'PMP_OWNER_DIAGNOSTICS_HOST_RECEIPT_V1',version:V,owner:OWNER,at:now(),reason:reason||'scan',mode:'active_control_hash_only',documents_seen:seen,control_documents_seen:controlDocs,hashes_seen:Array.from(new Set(hashes)),hosts_created:made,hosts_removed_from_non_control:removed,host_id:HOST_ID,rule:RULE,side_effects:{route_change_attempted:false,storage_migration_attempted:false,bank_rebuild_attempted:false,generic_body_diagnostics_mount:false}};put(receipt);return receipt}
window.PMPOwnerDiagnosticsHostV1={version:V,owner:OWNER,scan,rule:RULE};
[0,100,250,600,1200,2400,4200,7000].forEach(t=>setTimeout(()=>scan('scheduled_'+t),t));setInterval(()=>scan('slow_watch_3000'),3000);window.addEventListener('hashchange',()=>scan('hashchange'));scan('initial');
})();