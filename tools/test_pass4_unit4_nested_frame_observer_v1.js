#!/usr/bin/env node
'use strict';
const assert=require('assert');
const vm=require('vm');
const {observerInitSource,classify}=require('./run_pass4_unit4_replacement_observation_v1.js');

function frame(url){
  const intervals=[];
  const ctx={location:{href:url},Date,setInterval:(fn)=>{intervals.push(fn);return 1},globalThis:null};
  ctx.globalThis=ctx;
  vm.runInNewContext(observerInitSource(),ctx);
  return {ctx,intervals};
}
const chain=[
 frame('http://x/pmp-app-current.html'),
 frame('http://x/pmp-route-guardian-current-loader-v22.html'),
 frame('http://x/pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html'),
 frame('http://x/pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html')
];
const inner=chain[3].ctx;
let state='BOOTING';
inner.PMPBootStatusStripOwnerV1={
 contract:'PMP_BOOT_STATUS_STRIP_PASSIVE_CONTRACT_V1',
 sideEffects:{routeAssignments:0,persistedUserDataWrites:0,appOrchestratorOwnershipTransfers:0,startupRepairs:0},
 statusFrom(){return {state}},
 derive(x){return {state:x.state}},
 tick(x){return {state:x.state}}
};
assert.strictEqual(inner.__PMP_UNIT4_FRAME_EVIDENCE__.assigned,true);
assert(inner.__PMP_UNIT4_FRAME_EVIDENCE__.states.includes('BOOTING'));
inner.PMPBootStatusStripOwnerV1.tick({state:'READY_ACKNOWLEDGED'});
assert(inner.__PMP_UNIT4_FRAME_EVIDENCE__.states.includes('READY_ACKNOWLEDGED'));
assert.deepStrictEqual(chain.map(x=>classify(x.ctx.location.href)),
 ['top','route_guardian_v22','reload_owner_v30','current_inner_v30']);
console.log('PASS: nested-frame observer captures frame-local assignment and states');
