#!/usr/bin/env node
'use strict';
const fs=require('fs');
const vm=require('vm');
const assert=require('assert');
const path=require('path');
const ROOT=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(ROOT,'pmp-boot-status-strip-owner-v1.js'),'utf8');
const map=JSON.parse(fs.readFileSync(path.join(ROOT,'pmp-current-map-v12.json'),'utf8'));

const effects={
 routeAssignments:0, alternateDestinations:0, localStorageWrites:0, sessionStorageWrites:0,
 indexedDBWrites:0, ownershipTransfers:0, startupRepairs:0, startupDelays:0,
 bankRebuilds:0, levelReorders:0, residentChanges:0, mountRegistryChanges:0
};
const elements=new Map();
function element(tag){return {tagName:String(tag).toUpperCase(),id:'',className:'',textContent:'',innerHTML:'',attrs:{},children:[],
 setAttribute(k,v){this.attrs[k]=String(v)},getAttribute(k){return this.attrs[k]||null},
 appendChild(x){this.children.push(x);if(x.id)elements.set(x.id,x);return x},
 remove(){if(this.id)elements.delete(this.id)}}}
const document={head:element('head'),body:element('body'),createElement:element,getElementById:id=>elements.get(id)||null};
for(const id of ['bootRoute','bootRuntime','bootOrchestrator','bootEntry','bootNote','bootLog']){
 const x=element('div');x.id=id;x.textContent='';elements.set(id,x);
}
const storage=()=>({getItem:()=>null,setItem:()=>{throw new Error('persisted storage write')},removeItem:()=>{throw new Error('persisted storage write')}});
const location={pathname:'/pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html',
 assign(){effects.routeAssignments++;throw new Error('route assignment')},
 replace(){effects.routeAssignments++;throw new Error('route replacement')}};
Object.defineProperty(location,'href',{get(){return location.pathname},set(){effects.routeAssignments++;throw new Error('route href write')}});
const context={window:null,document,location,Date,Object,String,Number,RegExp,console,
 localStorage:storage(),sessionStorage:storage(),
 indexedDB:{open(){effects.indexedDBWrites++;throw new Error('indexedDB write')}},
 setInterval:()=>1,clearInterval:()=>{},setTimeout:()=>1};
context.window=context;
vm.runInNewContext(source,context,{filename:'pmp-boot-status-strip-owner-v1.js'});
const api=context.PMPBootStatusStripOwnerV1;
assert(api,'installed Boot Status Strip API missing');
assert.strictEqual(api.contract,'PMP_BOOT_STATUS_STRIP_PASSIVE_CONTRACT_V1');

function plain(x){return JSON.parse(JSON.stringify(x))}
function requiredUnavailable(detail){return {elapsed_ms:1,failure_signal:true,failure_detail:detail,app_orchestrator_present:false,app_orchestrator_valid:false}}
assert.strictEqual(api.derive({elapsed_ms:0,app_orchestrator_present:false,app_orchestrator_valid:false}).state,'BOOTING');
assert.strictEqual(api.derive({elapsed_ms:8999,app_orchestrator_present:false,app_orchestrator_valid:false}).state,'BOOTING');
assert.strictEqual(api.derive({elapsed_ms:9000,app_orchestrator_present:false,app_orchestrator_valid:false}).state,'BOOT_SLOW');
assert.strictEqual(api.derive({failure_signal:true,failure_detail:'explicit failure'}).state,'BOOT_FAILURE');
assert.strictEqual(api.derive({app_orchestrator_present:true,app_orchestrator_valid:false}).state,'BOOT_FAILURE');
assert.strictEqual(api.derive(requiredUnavailable('required observation unavailable')).state,'BOOT_FAILURE');
assert.strictEqual(api.derive(requiredUnavailable('required observation blocked')).state,'BOOT_FAILURE');
assert.strictEqual(api.derive({elapsed_ms:1,app_orchestrator_present:true,app_orchestrator_valid:true,app_orchestrator_acknowledged:true,route_ready:true,runtime_ready:true}).state,'READY_ACKNOWLEDGED');
assert.notStrictEqual(api.derive({elapsed_ms:1,app_orchestrator_present:true,app_orchestrator_valid:true,app_orchestrator_acknowledged:true,route_ready:false,runtime_ready:true}).state,'READY_ACKNOWLEDGED');

const missing=api.statusFrom(null);
assert(['BOOTING','BOOT_SLOW','BOOT_FAILURE','READY_ACKNOWLEDGED'].includes(missing.state));
assert.deepStrictEqual(plain(api.sideEffects),{routeAssignments:0,persistedUserDataWrites:0,appOrchestratorOwnershipTransfers:0,startupRepairs:0});
const before=JSON.stringify(effects);
api.tick(requiredUnavailable('blocked'));
assert.strictEqual(JSON.stringify(effects),before);

assert.strictEqual(map.route_contract.sole_authority,'pmp-current-map-v12.json');
assert.strictEqual(map.route_contract.implicit_fallbacks,false);
for(const token of ['pmp-route-guardian-current-loader-v16','pmp-current-reload-owner-v27','rgcontrols-v26','rgcontrols-v23'])
 assert(!source.includes(token),`obsolete historical dependency: ${token}`);
for(const token of ['localStorage','sessionStorage','indexedDB','location.assign','location.replace','document.write','frame.src='])
 assert(!source.includes(token),`prohibited side-effect token: ${token}`);
assert(!/current-map|alternate destination|fallback/i.test(source),'strip must not consult destination authority');
console.log('PASS: Unit 3 isolated four-state, fail-passive, zero-side-effect, and sole-authority proof');
