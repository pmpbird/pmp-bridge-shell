#!/usr/bin/env node
'use strict';
const fs=require('fs');
const path=require('path');

const RECEIPT=path.resolve(__dirname,'../audit/pass4/pass4-boot-status-strip-unit4-replacement-observation-v1.json');
const ENTRY='http://127.0.0.1:4175/pmp-app-current.html';

function observerInitSource(){
return `(() => {
  const root = globalThis;
  const evidence = root.__PMP_UNIT4_FRAME_EVIDENCE__ = {
    href: String(location.href), assigned:false, states:[], samples:[], errors:[]
  };
  let apiValue;
  function record(api, reason){
    try {
      if (!api) return;
      evidence.assigned = true;
      evidence.contract = api.contract || null;
      evidence.sideEffects = api.sideEffects || null;
      let status = null;
      if (typeof api.statusFrom === 'function') status = api.statusFrom(null);
      if (status && status.state && !evidence.states.includes(status.state)) evidence.states.push(status.state);
      evidence.samples.push({reason, state: status && status.state || null, at: Date.now()});
    } catch (e) { evidence.errors.push(String(e && e.message || e)); }
  }
  Object.defineProperty(root,'PMPBootStatusStripOwnerV1',{
    configurable:true,
    enumerable:true,
    get(){ return apiValue; },
    set(v){
      apiValue=v; record(v,'assignment');
      for (const name of ['derive','statusFrom','tick']) {
        if (v && typeof v[name] === 'function' && !v[name].__unit4Wrapped) {
          const original=v[name];
          const wrapped=function(...args){
            const out=original.apply(this,args);
            try {
              const state=out && out.state;
              if (state && !evidence.states.includes(state)) evidence.states.push(state);
              evidence.samples.push({reason:name,state:state||null,at:Date.now()});
            } catch (_) {}
            return out;
          };
          wrapped.__unit4Wrapped=true; v[name]=wrapped;
        }
      }
    }
  });
  setInterval(()=>record(apiValue,'poll'),100);
})();`;
}

function classify(url){
  if (/pmp-app-current\.html/.test(url)) return 'top';
  if (/pmp-route-guardian-current-loader-v22\.html/.test(url)) return 'route_guardian_v22';
  if (/pmp-current-reload-owner-v30-direct-boot-surface-20260708A\.html/.test(url)) return 'reload_owner_v30';
  if (/pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A\.html/.test(url)) return 'current_inner_v30';
  return 'other';
}

async function main(){
  const {chromium}=require('playwright');
  const started=new Date().toISOString();
  let browser, page;
  const receipt={
    type:'PMP_PASS4_BOOT_STATUS_STRIP_UNIT4_REPLACEMENT_OBSERVATION_V1',
    version:'1.0.0', status:'FAIL_PRESERVED', pass:4, unit:4,
    base_main_commit:'3c8c2e3813f48a7f4a0c64594aaca1a822ce0753',
    prior_failed_pr:149, replacement_authorized:true,
    observation_consumed:true, observation_count:1, browser_navigation_count:0,
    entry:ENTRY, started_at:started, frame_chain:[], observed_states:[],
    production_runtime_changed:false, runtime_integrity_changed:false,
    unit5_started:false, pass4_complete_claimed:false, pass5_started:false, pr122_touched:false
  };
  try {
    browser=await chromium.launch({headless:true});
    const context=await browser.newContext();
    await context.addInitScript({content:observerInitSource()});
    page=await context.newPage();
    await page.goto(ENTRY,{waitUntil:'domcontentloaded',timeout:30000});
    receipt.browser_navigation_count=1;
    await page.waitForTimeout(1200);
    const guardian=page.frames().find(f=>classify(f.url())==='route_guardian_v22');
    if (guardian) {
      const run=guardian.locator('#openBtn');
      if (await run.count()) await run.click();
    }
    const deadline=Date.now()+18000;
    while(Date.now()<deadline){
      const frames=page.frames();
      const snapshots=[];
      for(const frame of frames){
        let ev=null;
        try{ev=await frame.evaluate(()=>globalThis.__PMP_UNIT4_FRAME_EVIDENCE__||null)}catch(_){}
        snapshots.push({url:frame.url(),role:classify(frame.url()),evidence:ev});
      }
      receipt.frame_chain=snapshots;
      const states=[...new Set(snapshots.flatMap(x=>x.evidence&&x.evidence.states||[]))];
      receipt.observed_states=states;
      if(states.includes('BOOTING')&&states.includes('READY_ACKNOWLEDGED')) break;
      await page.waitForTimeout(250);
    }
    const inner=receipt.frame_chain.find(x=>x.role==='current_inner_v30');
    const guardianSeen=receipt.frame_chain.some(x=>x.role==='route_guardian_v22');
    const reloadSeen=receipt.frame_chain.some(x=>x.role==='reload_owner_v30');
    const side=inner&&inner.evidence&&inner.evidence.sideEffects;
    receipt.booting_observed=receipt.observed_states.includes('BOOTING');
    receipt.ready_acknowledged_observed=receipt.observed_states.includes('READY_ACKNOWLEDGED');
    receipt.boot_slow_naturally_observed=receipt.observed_states.includes('BOOT_SLOW');
    receipt.boot_failure_naturally_observed=receipt.observed_states.includes('BOOT_FAILURE');
    receipt.zero_effect_evidence={strip_declared_side_effects:side||null};
    const ok=guardianSeen&&reloadSeen&&!!inner&&inner.evidence&&inner.evidence.assigned&&
      receipt.booting_observed&&receipt.ready_acknowledged_observed&&side&&
      side.routeAssignments===0&&side.persistedUserDataWrites===0&&
      side.appOrchestratorOwnershipTransfers===0&&side.startupRepairs===0;
    receipt.status=ok?'PASS':'FAIL_PRESERVED';
    if(!ok) receipt.failure_reason='Required nested-frame live observations or zero-effect evidence were incomplete.';
  } catch(e){
    receipt.failure_reason=String(e&&e.stack||e);
  } finally {
    receipt.finished_at=new Date().toISOString();
    if(browser) await browser.close();
    fs.writeFileSync(RECEIPT,JSON.stringify(receipt,null,2)+'\n');
    console.log(JSON.stringify(receipt,null,2));
  }
}
if(require.main===module) main();
module.exports={observerInitSource,classify};
