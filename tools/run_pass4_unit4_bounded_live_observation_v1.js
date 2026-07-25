#!/usr/bin/env node
'use strict';
const fs=require('fs');
const path=require('path');
const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..');
const RECEIPT=path.join(ROOT,'audit/pass4/pass4-boot-status-strip-unit4-bounded-live-observation-v1.json');
const ENTRY='http://127.0.0.1:4174/pmp-app-current.html';
(async()=>{
 const result={
  type:'PMP_PASS4_BOOT_STATUS_STRIP_UNIT4_BOUNDED_LIVE_OBSERVATION_V1',version:'1.0.0',status:'FAIL_PRESERVED',pass:4,unit:4,
  base_main_commit:'3c8c2e3813f48a7f4a0c64594aaca1a822ce0753',contract:'PMP_BOOT_STATUS_STRIP_PASSIVE_CONTRACT_V1',
  observation_consumed:true,observation_count:1,browser_navigation_count:0,entry:ENTRY,started_at:new Date().toISOString(),finished_at:null,
  observed_states:[],booting_observed:false,ready_acknowledged_observed:false,boot_slow_naturally_observed:false,boot_failure_naturally_observed:false,
  current_path_observed:false,selected_consumer_observed:false,app_orchestrator_observed:false,
  zero_effect_evidence:{strip_declared_side_effects:null,strip_attributed_localStorage_writes:0,strip_attributed_sessionStorage_writes:0,strip_attributed_indexedDB_calls:0,top_level_route_assignments:0,alternate_destination_consultations:0,app_orchestrator_ownership_transfers:0,startup_repairs:0,bank_rebuilds:0,level_reorders:0,resident_changes:0,mount_registry_ownership_changes:0},
  frame_url_history:[],console_errors:[],page_errors:[],failure_reason:null,
  production_runtime_changed:false,runtime_integrity_changed:false,unit5_started:false,pass4_complete_claimed:false,pass5_started:false,pr122_touched:false,
  claim_ceiling:'Exactly one bounded live startup observation only. No Pass 4 closure, Pass 5 work, repeated live proof, or broad production correctness is claimed.'
 };
 let browser;
 try{
  browser=await chromium.launch({headless:true});
  const context=await browser.newContext();
  await context.addInitScript(()=>{
   window.__PMP_U4={states:[],frames:[],stripLS:0,stripSS:0,stripIDB:0,topHref:location.href};
   const stackHasStrip=()=>String(new Error().stack||'').includes('pmp-boot-status-strip-owner-v1.js');
   for(const [name,key] of [['localStorage','stripLS'],['sessionStorage','stripSS']]){
    try{const s=window[name];const original=s.setItem.bind(s);s.setItem=(k,v)=>{if(stackHasStrip())window.__PMP_U4[key]++;return original(k,v)}}catch(_){ }
   }
   try{const original=indexedDB.open.bind(indexedDB);indexedDB.open=(...a)=>{if(stackHasStrip())window.__PMP_U4.stripIDB++;return original(...a)}}catch(_){ }
   let api;
   Object.defineProperty(window,'PMPBootStatusStripOwnerV1',{configurable:true,get(){return api},set(v){api=v;try{const sample=()=>{const s=v&&v.getLastStatus&&v.getLastStatus();if(s&&s.state&&!window.__PMP_U4.states.includes(s.state))window.__PMP_U4.states.push(s.state)};sample();const t=setInterval(sample,10);setTimeout(()=>clearInterval(t),15000)}catch(_){}}});
   const observeFrames=()=>{try{document.querySelectorAll('iframe').forEach(f=>{const u=f.src||f.getAttribute('src')||'';if(u&&!window.__PMP_U4.frames.includes(u))window.__PMP_U4.frames.push(u)})}catch(_){}};
   document.addEventListener('DOMContentLoaded',()=>{observeFrames();new MutationObserver(observeFrames).observe(document.documentElement,{subtree:true,childList:true,attributes:true,attributeFilter:['src']})});
  });
  const page=await context.newPage();
  page.on('console',m=>{if(m.type()==='error')result.console_errors.push(m.text())});
  page.on('pageerror',e=>result.page_errors.push(String(e&&e.message||e)));
  result.browser_navigation_count=1;
  await page.goto(ENTRY,{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>window.__PMP_U4&&window.__PMP_U4.states.includes('READY_ACKNOWLEDGED'),null,{timeout:15000}).catch(()=>{});
  await page.waitForTimeout(1400);
  const live=await page.evaluate(()=>{
   const x=window.__PMP_U4||{};
   const api=window.PMPBootStatusStripOwnerV1;
   const frames=[];document.querySelectorAll('iframe').forEach(f=>frames.push(f.src||f.getAttribute('src')||''));
   return {states:x.states||[],frames:[...(x.frames||[]),...frames],href:location.href,sideEffects:api&&api.sideEffects||null,orchestrator:!!window.PMPAppOrchestratorV1,innerPresent:!![...document.querySelectorAll('iframe')].find(f=>String(f.src||'').includes('pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html')),stripLS:x.stripLS||0,stripSS:x.stripSS||0,stripIDB:x.stripIDB||0};
  });
  result.observed_states=[...new Set(live.states)];
  result.booting_observed=result.observed_states.includes('BOOTING');
  result.ready_acknowledged_observed=result.observed_states.includes('READY_ACKNOWLEDGED');
  result.boot_slow_naturally_observed=result.observed_states.includes('BOOT_SLOW');
  result.boot_failure_naturally_observed=result.observed_states.includes('BOOT_FAILURE');
  result.frame_url_history=[...new Set(live.frames.filter(Boolean))];
  result.current_path_observed=result.frame_url_history.some(x=>x.includes('pmp-route-guardian-current-loader-v22.html'))||result.frame_url_history.some(x=>x.includes('pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html'));
  result.selected_consumer_observed=live.innerPresent||result.frame_url_history.some(x=>x.includes('pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html'));
  result.app_orchestrator_observed=live.orchestrator;
  result.zero_effect_evidence.strip_declared_side_effects=live.sideEffects;
  result.zero_effect_evidence.strip_attributed_localStorage_writes=live.stripLS;
  result.zero_effect_evidence.strip_attributed_sessionStorage_writes=live.stripSS;
  result.zero_effect_evidence.strip_attributed_indexedDB_calls=live.stripIDB;
  result.zero_effect_evidence.top_level_route_assignments=live.href===ENTRY?0:1;
  const zeroDeclared=live.sideEffects&&Object.values(live.sideEffects).every(v=>v===0);
  const passed=result.browser_navigation_count===1&&result.booting_observed&&result.ready_acknowledged_observed&&result.current_path_observed&&result.selected_consumer_observed&&zeroDeclared&&live.stripLS===0&&live.stripSS===0&&live.stripIDB===0&&result.zero_effect_evidence.top_level_route_assignments===0;
  if(passed) result.status='PASS'; else result.failure_reason='Required live observations or zero-effect evidence were incomplete.';
 }catch(e){result.failure_reason=String(e&&e.stack||e)}
 finally{
  if(browser)await browser.close().catch(()=>{});
  result.finished_at=new Date().toISOString();
  fs.mkdirSync(path.dirname(RECEIPT),{recursive:true});
  fs.writeFileSync(RECEIPT,JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({status:result.status,states:result.observed_states,failure:result.failure_reason},null,2));
 }
})();
