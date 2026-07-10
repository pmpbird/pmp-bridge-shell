(()=>{
'use strict';
const V='1.0.0-bank-owner-cross-frame-dependencies-20260710A';
const OWNER='pmp-bank-owner-dependency-bridge-v1';
const KEY='pmp_bank_owner_dependency_bridge_v1_receipt';
const APIS=[
 'PMPMasterBankInventoryRouterV1',
 'PMPContinuousRunStateBankV1',
 'PMPContinuousRunBankTransferStoreV1',
 'PMPContinuousRunBankZipImporterV1',
 'PMPMustReferenceSourceZipV1',
 'PMPBankProjectRegistryV1',
 'PMPMasterBankTabV1'
];
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function put(k,v){try{T().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function docs(d,out,depth){out=out||[];depth=depth||0;if(!d||depth>10)return out;try{out.push(d);Array.from(d.querySelectorAll('iframe,frame')).forEach(f=>{try{let fd=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(fd)docs(fd,out,depth+1)}catch(e){}})}catch(e){}return out}
function winOf(d){try{return d.defaultView||T()}catch(e){return T()}}
function getFromAny(name,frames){for(const w of frames){try{if(w&&w[name])return w[name]}catch(e){}}return null}
function frameWindows(){let out=[];try{out.push(window);if(window.parent&&out.indexOf(window.parent)<0)out.push(window.parent);if(T()&&out.indexOf(T())<0)out.push(T())}catch(e){}docs(T().document).forEach(d=>{try{let w=winOf(d);if(w&&out.indexOf(w)<0)out.push(w)}catch(e){}});return out}
function expose(){let frames=frameWindows(),resolved={},copied=[];APIS.forEach(name=>{let api=getFromAny(name,frames);resolved[name]=api?String(api.version||'present'):'missing';if(!api)return;frames.forEach(w=>{try{if(!w[name]){w[name]=api;copied.push(name+' -> frame')}}catch(e){}})});return {frames:frames.length,resolved,copied}}
function callBankOwner(reason){let frames=frameWindows(),called=[];frames.forEach(w=>{try{let api=w.PMPMasterBankTabV1;if(api&&typeof api.scan==='function'){api.scan();called.push(String(api.version||'unknown'))}}catch(e){}});return called}
function run(reason){let x=expose();let called=callBankOwner(reason||'dependency_bridge');let ready=!!(x.resolved&&x.resolved.PMPMasterBankInventoryRouterV1&&x.resolved.PMPMasterBankInventoryRouterV1!=='missing');let r={type:'PMP_BANK_OWNER_DEPENDENCY_BRIDGE_V1_RECEIPT',version:V,owner:OWNER,at:now(),reason:reason||'run',status:ready?'BANK_OWNER_DEPENDENCIES_EXPOSED':'BANK_OWNER_DEPENDENCIES_WAITING',frames_seen:x.frames,resolved:x.resolved,copied:x.copied.length,bank_owner_scan_called:called.length,bank_owner_versions:called,rule:'Dependency bridge only. It exposes existing Bank APIs across same-origin parent/iframe windows so the real Bank Owner can see its dependencies. It does not repaint Bank, create Bank DOM, intercept buttons, rebuild Bank, or write IndexedDB/storage.',side_effects:{route_change:'not_attempted',bank_rebuild:'not_attempted',bank_dom_patch:'not_attempted',button_intercept:'not_attempted',panel_move:'not_attempted',panel_hide:'not_attempted',indexeddb_write:'not_attempted',storage_migration:'not_attempted',owner_takeover:'not_attempted'}};put(KEY,r);return r}
window.PMPBankOwnerDependencyBridgeV1={version:V,owner:OWNER,run,expose,rule:'Cross-frame dependency bridge for the real Bank Owner. No UI ownership.'};try{T().PMPBankOwnerDependencyBridgeV1=window.PMPBankOwnerDependencyBridgeV1}catch(e){};
[50,150,350,700,1200,2200,4200,7000,11000].forEach(t=>setTimeout(()=>run('startup_'+t),t));
})();