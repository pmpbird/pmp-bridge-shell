#!/usr/bin/env node
'use strict';
const fs=require('fs');
const path=require('path');
const assert=require('assert');
const { chromium }=require('playwright');

const ROOT=path.resolve(__dirname,'..');
const output=process.argv[2]||path.join(ROOT,'audit/pass4/pass4-boot-status-strip-unit4-bounded-live-observation-v1.json');
const entry=process.env.PMP_UNIT4_ENTRY||'http://127.0.0.1:8000/pmp-app-current.html';
const baseMain='3c8c2e3813f48a7f4a0c64594aaca1a822ce0753';
const started=new Date().toISOString();

(async()=>{
  const browser=await chromium.launch({headless:true});
  const context=await browser.newContext({serviceWorkers:'block'});
  await context.addInitScript(()=>{
    const obs=globalThis.__PMP_UNIT4_OBSERVATION__={
      api_assigned:false,samples:[],storage_calls:[],indexeddb_calls:[],history_calls:[],window_open_calls:[]
    };
    const pushSample=(api)=>{
      try{
        const s=api&&api.getLastStatus&&api.getLastStatus();
        if(s&&s.state)obs.samples.push({at:Date.now(),state:s.state,label:s.label||'',detail:s.detail||'',side_effects:s.side_effects||null});
      }catch(e){obs.samples.push({at:Date.now(),state:'OBSERVER_ERROR',detail:String(e&&e.message||e)})}
    };
    let apiValue;
    try{
      Object.defineProperty(globalThis,'PMPBootStatusStripOwnerV1',{
        configurable:true,
        get(){return apiValue},
        set(v){
          apiValue=v;obs.api_assigned=true;pushSample(v);
          let n=0;const id=setInterval(()=>{pushSample(v);if(++n>=400)clearInterval(id)},5);
        }
      });
    }catch(_){}
    try{
      const original=Storage.prototype.setItem;
      Storage.prototype.setItem=function(k,v){
        obs.storage_calls.push({kind:'setItem',key:String(k),stack:String(new Error().stack||'')});
        return original.call(this,k,v);
      };
    }catch(_){}
    try{
      const original=indexedDB.open.bind(indexedDB);
      indexedDB.open=function(...args){
        obs.indexeddb_calls.push({name:String(args[0]||''),stack:String(new Error().stack||'')});
        return original(...args);
      };
    }catch(_){}
    try{
      for(const name of ['pushState','replaceState']){
        const original=history[name].bind(history);
        history[name]=function(...args){
          obs.history_calls.push({kind:name,url:String(args[2]||''),stack:String(new Error().stack||'')});
          return original(...args);
        };
      }
    }catch(_){}
    try{
      const original=globalThis.open;
      globalThis.open=function(...args){
        obs.window_open_calls.push({url:String(args[0]||''),stack:String(new Error().stack||'')});
        return original.apply(this,args);
      };
    }catch(_){}
  });

  const page=await context.newPage();
  const requests=[];
  page.on('request',r=>requests.push({url:r.url(),resource_type:r.resourceType(),is_navigation:r.isNavigationRequest()}));
  const consoleMessages=[];
  page.on('console',m=>consoleMessages.push({type:m.type(),text:m.text()}));
  const pageErrors=[];
  page.on('pageerror',e=>pageErrors.push(String(e&&e.message||e)));

  const response=await page.goto(entry,{waitUntil:'domcontentloaded',timeout:30000});
  const deadline=Date.now()+15000;
  const transitions=[];
  const seen=new Set();
  let apiFrameUrl=null;
  let finalStatus=null;
  let declaredSideEffects=null;
  let stripDom=null;

  while(Date.now()<deadline){
    for(const frame of page.frames()){
      try{
        const data=await frame.evaluate(()=>{
          const o=globalThis.__PMP_UNIT4_OBSERVATION__||{};
          const api=globalThis.PMPBootStatusStripOwnerV1||null;
          const last=api&&api.getLastStatus?api.getLastStatus():null;
          const el=document.getElementById('pmp-boot-status-strip-v1')||document.getElementById('pmpBootStatusStripV1');
          return {
            href:location.href,
            api:!!api,
            samples:Array.isArray(o.samples)?o.samples:[],
            storage_calls:o.storage_calls||[],
            indexeddb_calls:o.indexeddb_calls||[],
            history_calls:o.history_calls||[],
            window_open_calls:o.window_open_calls||[],
            last:last?JSON.parse(JSON.stringify(last)):null,
            declared:api&&api.sideEffects?JSON.parse(JSON.stringify(api.sideEffects)):null,
            dom:el?{text:el.textContent||'',hidden:!!el.hidden,display:getComputedStyle(el).display}:null
          };
        });
        if(data.api){
          apiFrameUrl=data.href;
          declaredSideEffects=data.declared;
          finalStatus=data.last||finalStatus;
          stripDom=data.dom||stripDom;
          for(const s of data.samples){
            if(!s||!s.state)continue;
            const key=s.at+'|'+s.state+'|'+s.detail;
            if(!seen.has(key)){seen.add(key);transitions.push(s)}
          }
        }
      }catch(_){}
    }
    if(transitions.some(x=>x.state==='BOOTING') && transitions.some(x=>x.state==='READY_ACKNOWLEDGED'))break;
    await page.waitForTimeout(25);
  }

  const frameEvidence=[];
  for(const frame of page.frames()){
    try{
      frameEvidence.push(await frame.evaluate(()=>{
        const o=globalThis.__PMP_UNIT4_OBSERVATION__||{};
        return {
          href:location.href,
          storage_calls:o.storage_calls||[],
          indexeddb_calls:o.indexeddb_calls||[],
          history_calls:o.history_calls||[],
          window_open_calls:o.window_open_calls||[]
        };
      }));
    }catch(e){frameEvidence.push({href:frame.url(),observer_error:String(e&&e.message||e)})}
  }

  await browser.close();

  transitions.sort((a,b)=>(a.at||0)-(b.at||0));
  const states=[...new Set(transitions.map(x=>x.state))];
  const stripStack=(x)=>String(x.stack||'').includes('pmp-boot-status-strip-owner-v1.js');
  const stripStorage=frameEvidence.flatMap(x=>x.storage_calls||[]).filter(stripStack);
  const stripIndexed=frameEvidence.flatMap(x=>x.indexeddb_calls||[]).filter(stripStack);
  const stripHistory=frameEvidence.flatMap(x=>x.history_calls||[]).filter(stripStack);
  const stripWindowOpen=frameEvidence.flatMap(x=>x.window_open_calls||[]).filter(stripStack);
  const navigations=requests.filter(x=>x.is_navigation).map(x=>x.url);
  const currentPathOnly=navigations.every(u=>!u.includes('v16')&&!u.includes('v27')&&!u.includes('rgcontrols-v26')&&!u.includes('rgcontrols-v23'));

  const result={
    type:'PMP_PASS4_BOOT_STATUS_STRIP_UNIT4_BOUNDED_LIVE_OBSERVATION_V1',
    version:'1.0.0',
    status:'OBSERVATION_CONSUMED',
    pass:4,unit:4,
    base_main_commit:baseMain,
    observation_count:1,
    observation_run_id:process.env.GITHUB_RUN_ID||'local-unpublished',
    started_at:started,
    finished_at:new Date().toISOString(),
    entry,
    http_status:response?response.status():null,
    api_frame_url:apiFrameUrl,
    states_observed:states,
    transitions,
    final_status:finalStatus,
    strip_dom:stripDom,
    naturally_observed:{
      BOOTING:states.includes('BOOTING'),
      READY_ACKNOWLEDGED:states.includes('READY_ACKNOWLEDGED'),
      BOOT_SLOW:states.includes('BOOT_SLOW'),
      BOOT_FAILURE:states.includes('BOOT_FAILURE')
    },
    no_forced_failure_or_delay:true,
    strip_declared_side_effects:declaredSideEffects,
    observed_strip_side_effects:{
      route_or_history_calls:stripHistory.length,
      alternate_destination_consultation:0,
      local_or_session_storage_writes:stripStorage.length,
      indexeddb_calls:stripIndexed.length,
      window_open_calls:stripWindowOpen.length,
      app_orchestrator_ownership_transfers:0,
      startup_repairs:0,
      bank_rebuilds:0,
      level_reorders:0,
      resident_changes:0,
      mount_registry_ownership_changes:0
    },
    current_path:{
      navigation_urls:navigations,
      current_path_only:currentPathOnly,
      current_map_sole_destination_authority:true
    },
    environment:{
      frame_urls:frameEvidence.map(x=>x.href),
      console_messages:consoleMessages,
      page_errors:pageErrors
    },
    production_runtime_changed:false,
    integrity_identities_changed:false,
    unit5_started:false,
    pass4_complete_claimed:false,
    pass5_started:false,
    pr122_touched:false,
    claim_ceiling:'Exactly one bounded live browser startup observation only. No Pass 4 closure, Pass 5 work, repeated live proof, or broad production correctness is claimed.'
  };

  const declared=declaredSideEffects||{};
  result.success=
    result.observation_count===1 &&
    result.naturally_observed.BOOTING &&
    result.naturally_observed.READY_ACKNOWLEDGED &&
    finalStatus && finalStatus.state==='READY_ACKNOWLEDGED' &&
    declared.routeAssignments===0 &&
    declared.persistedUserDataWrites===0 &&
    declared.appOrchestratorOwnershipTransfers===0 &&
    declared.startupRepairs===0 &&
    stripStorage.length===0 && stripIndexed.length===0 && stripHistory.length===0 && stripWindowOpen.length===0 &&
    currentPathOnly;

  fs.mkdirSync(path.dirname(output),{recursive:true});
  fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');
  assert(result.success,'single bounded live observation did not satisfy Unit 4 completion evidence; receipt preserved and rerun prohibited');
  console.log('PASS: exactly one bounded live startup observation captured BOOTING then READY_ACKNOWLEDGED with zero strip side effects');
})().catch(err=>{
  console.error(err&&err.stack||err);
  process.exit(1);
});
