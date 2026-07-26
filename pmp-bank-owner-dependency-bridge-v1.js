(()=>{
'use strict';
const V='1.0.0-pass9-unit3-readonly-discovery-20260726A';
const OWNER='pmp-bank-owner-dependency-bridge-v1';
const APIS=['PMPBankContinuousRunOwnerBoundaryV1','PMPMasterBankInventoryRouterV1','PMPContinuousRunStateBankV1','PMPContinuousRunBankTransferStoreV1','PMPContinuousRunBankZipImporterV1','PMPMustReferenceSourceZipV1','PMPBankProjectRegistryV1','PMPMasterBankTabV1','PMPContinuousRunLevelOwnerV1'];
let last=null,lastSignature='',dispatches=0;
function T(){try{return window.top||window}catch(e){return window}}
function now(){return new Date().toISOString()}
function docs(d,out,depth){out=out||[];depth=depth||0;if(!d||depth>10)return out;try{out.push(d);Array.from(d.querySelectorAll('iframe,frame')).forEach(f=>{try{let fd=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(fd)docs(fd,out,depth+1)}catch(e){}})}catch(e){}return out}
function winOf(d){try{return d.defaultView||T()}catch(e){return T()}}
function frameWindows(){let out=[];try{out.push(window);if(window.parent&&out.indexOf(window.parent)<0)out.push(window.parent);if(T()&&out.indexOf(T())<0)out.push(T())}catch(e){}docs(T().document).forEach(d=>{try{let w=winOf(d);if(w&&out.indexOf(w)<0)out.push(w)}catch(e){}});return out}
function discover(){let frames=frameWindows(),resolved={};APIS.forEach(name=>{let hits=[];frames.forEach((w,index)=>{try{let api=w&&w[name];if(api)hits.push({frame:index,version:String(api.version||'present'),owner:String(api.owner||'not_declared')})}catch(e){}});resolved[name]=hits});return{frames:frames.length,resolved,copied:[],mutable_apis_copied:0}}
function signatureOf(x){return JSON.stringify(Object.keys(x.resolved).map(k=>[k,x.resolved[k].map(v=>v.frame+':'+v.version)]))}
function notify(frames,detail){frames.forEach(w=>{try{w.dispatchEvent(new CustomEvent('pmp:bank-owner-dependencies-ready',{detail}))}catch(e){}});dispatches++}
function run(reason){let x=discover(),signature=signatureOf(x),changed=signature!==lastSignature;if(changed){lastSignature=signature;notify(frameWindows(),{version:V,reason:String(reason||'run'),signature})}let boundaryHits=x.resolved.PMPBankContinuousRunOwnerBoundaryV1||[],routerHits=x.resolved.PMPMasterBankInventoryRouterV1||[],stateHits=x.resolved.PMPContinuousRunStateBankV1||[];last={type:'PMP_BANK_OWNER_DEPENDENCY_BRIDGE_V2_RECEIPT',version:V,owner:OWNER,at:now(),reason:String(reason||'run'),status:boundaryHits.length&&routerHits.length&&stateHits.length?'OWNER_BOUNDARY_DEPENDENCIES_DISCOVERED':'OWNER_BOUNDARY_DEPENDENCIES_WAITING',frames_seen:x.frames,resolved:x.resolved,copied:0,mutable_apis_copied:0,bank_owner_scan_called:0,event_dispatched:changed,dispatch_count:dispatches,rule:'Read-only same-origin discovery. Mutable APIs and authority are never copied between frames. A readiness event is emitted only when the dependency signature changes.',side_effects:{storage_write:'not_attempted',route_change:'not_attempted',bank_rebuild:'not_attempted',bank_dom_patch:'not_attempted',owner_takeover:'not_attempted'}};return last}
window.PMPBankOwnerDependencyBridgeV1={version:V,owner:OWNER,run,discover,last:()=>last,rule:'Read-only discovery and change event only. No copied APIs, scan calls, timer loop, storage write, or authority transfer.'};
window.addEventListener('load',()=>run('window_load'),{once:true});
run('script_load');
})();
