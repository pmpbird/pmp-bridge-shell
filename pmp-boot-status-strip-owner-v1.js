(()=>{
'use strict';
const V='2.0.0-pass4-unit2-current-path-passive';
const OWNER='pmp-boot-status-strip-owner-v1';
const CONTRACT='PMP_BOOT_STATUS_STRIP_PASSIVE_CONTRACT_V1';
const STRIP_ID='pmpAppOrchestratorBootStatusStripV1';
const STYLE_ID='pmpBootStatusStripOwnerV1Style';
const SLOW_MS=9000;
const READY_HIDE_MS=1200;
const startedAt=Date.now();
let hidden=false,lastStatus=null,timer=null;
function now(){return new Date().toISOString()}
function text(id){try{const x=document.getElementById(id);return String(x&&x.textContent||'').replace(/\s+/g,' ').trim()}catch(e){return''}}
function ready(id){try{return document.getElementById(id)?.getAttribute('data-ready')==='true'}catch(e){return false}}
function orchestrator(){try{return window.PMPAppOrchestratorV1}catch(e){return null}}
function snapshot(){
  const api=orchestrator();
  const note=text('bootNote');
  const log=text('bootLog');
  const combined=(note+' '+log).toLowerCase();
  return {
    elapsed_ms:Date.now()-startedAt,
    current_document:String(location&&location.pathname||''),
    app_orchestrator_present:!!api,
    app_orchestrator_valid:!!api&&typeof api==='object',
    app_orchestrator_acknowledged:ready('bootOrchestrator')||!!(api&&typeof api.getLastLaunchGateReceipt==='function'),
    route_ready:ready('bootRoute'),
    runtime_ready:ready('bootRuntime'),
    entry_ready:ready('bootEntry'),
    failure_signal:/fail|error|blocked|unavailable/.test(combined),
    failure_detail:/fail|error|blocked|unavailable/.test(combined)?(note||log||'Startup failure observed'):'',
  };
}
function derive(input){
  const x=input&&typeof input==='object'?input:{};
  if(x.failure_signal||x.app_orchestrator_present&&!x.app_orchestrator_valid){
    return {state:'BOOT_FAILURE',label:'Startup needs attention',detail:x.failure_detail||'A required startup acknowledgement is malformed or unavailable.'};
  }
  if(x.app_orchestrator_acknowledged&&x.route_ready&&x.runtime_ready){
    return {state:'READY_ACKNOWLEDGED',label:'App Orchestrator ready',detail:'Startup acknowledged. PMP entry remains owned by the existing startup chain.'};
  }
  if(Number(x.elapsed_ms)>=SLOW_MS){
    return {state:'BOOT_SLOW',label:'Startup is taking longer',detail:'Still observing. No repair, reroute, or ownership change is being attempted.'};
  }
  return {state:'BOOTING',label:'App Orchestrator working…',detail:'Observing the current startup chain.'};
}
function statusFrom(input){
  const observed=input&&typeof input==='object'?input:snapshot();
  const state=derive(observed);
  return Object.freeze({type:'PMP_BOOT_STATUS_STRIP_PASSIVE_STATUS_V1',version:V,contract:CONTRACT,owner:OWNER,at:now(),...state,observed:Object.freeze({...observed}),side_effects:Object.freeze({route_assignments:0,persisted_user_data_writes:0,app_orchestrator_ownership_transfers:0,startup_repairs:0})});
}
function ensureStyle(){
  if(!document.head||document.getElementById(STYLE_ID))return;
  const s=document.createElement('style');s.id=STYLE_ID;
  s.textContent='#'+STRIP_ID+'{position:fixed;left:10px;right:10px;top:calc(7px + env(safe-area-inset-top));z-index:2147483647;pointer-events:none;display:grid;justify-items:center;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}#'+STRIP_ID+' .pmpPassiveBootStrip{max-width:min(620px,calc(100vw - 20px));box-sizing:border-box;border:2px solid #07101c;border-radius:999px;background:rgba(255,255,255,.97);color:#07101c;padding:8px 13px;box-shadow:0 6px 18px rgba(0,0,0,.14);font-size:12px;font-weight:900;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}#'+STRIP_ID+'[data-state="BOOT_SLOW"] .pmpPassiveBootStrip{background:#fff3de}#'+STRIP_ID+'[data-state="BOOT_FAILURE"] .pmpPassiveBootStrip{background:#ffd9d5}#'+STRIP_ID+'[data-state="READY_ACKNOWLEDGED"] .pmpPassiveBootStrip{background:#dfffe4}';
  document.head.appendChild(s);
}
function render(status){
  if(hidden||!document.body)return status;
  ensureStyle();
  let root=document.getElementById(STRIP_ID);
  if(!root){root=document.createElement('div');root.id=STRIP_ID;root.setAttribute('role','status');root.setAttribute('aria-live','polite');document.body.appendChild(root)}
  root.setAttribute('data-state',status.state);
  root.setAttribute('data-pmp-passive-contract',CONTRACT);
  root.innerHTML='';
  const line=document.createElement('div');line.className='pmpPassiveBootStrip';line.textContent=status.label+' — '+status.detail;root.appendChild(line);
  return status;
}
function hide(){hidden=true;try{document.getElementById(STRIP_ID)?.remove();document.getElementById(STYLE_ID)?.remove()}catch(e){}if(timer)clearInterval(timer)}
function tick(input){lastStatus=statusFrom(input);render(lastStatus);if(lastStatus.state==='READY_ACKNOWLEDGED')setTimeout(hide,READY_HIDE_MS);return lastStatus}
function start(){tick();timer=setInterval(()=>tick(),250);setTimeout(()=>{if(timer)clearInterval(timer)},15000)}
window.PMPBootStatusStripOwnerV1=Object.freeze({version:V,owner:OWNER,contract:CONTRACT,mode:'passive_current_path_observer_only',derive,statusFrom,tick,hide,getLastStatus:()=>lastStatus,sideEffects:Object.freeze({routeAssignments:0,persistedUserDataWrites:0,appOrchestratorOwnershipTransfers:0,startupRepairs:0})});
try{start()}catch(e){try{render(statusFrom({failure_signal:true,failure_detail:String(e&&e.message||e),app_orchestrator_present:false,app_orchestrator_valid:false,elapsed_ms:Date.now()-startedAt}))}catch(_){}}
})();
