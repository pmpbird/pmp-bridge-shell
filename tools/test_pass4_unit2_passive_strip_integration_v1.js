#!/usr/bin/env node
'use strict';
const fs=require('fs');
const vm=require('vm');
const assert=require('assert');
const path=require('path');
const ROOT=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(ROOT,'pmp-boot-status-strip-owner-v1.js'),'utf8');
const inner=fs.readFileSync(path.join(ROOT,'pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html'),'utf8');

function element(tag){return {tagName:tag.toUpperCase(),id:'',className:'',textContent:'',innerHTML:'',attrs:{},children:[],setAttribute(k,v){this.attrs[k]=String(v)},getAttribute(k){return this.attrs[k]||null},appendChild(x){this.children.push(x);if(x.id)elements.set(x.id,x);return x},remove(){if(this.id)elements.delete(this.id)}}}
const elements=new Map();
const head=element('head'),body=element('body');
const document={head,body,createElement:element,getElementById:id=>elements.get(id)||null};
for(const id of ['bootRoute','bootRuntime','bootOrchestrator','bootEntry','bootNote','bootLog']){const x=element('div');x.id=id;elements.set(id,x)}
const context={window:null,document,location:{pathname:'/pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html'},Date,Object,String,Number,RegExp,console,setInterval:()=>1,clearInterval:()=>{},setTimeout:()=>1};
context.window=context;
vm.runInNewContext(source,context,{filename:'pmp-boot-status-strip-owner-v1.js'});
const api=context.PMPBootStatusStripOwnerV1;
assert(api,'Boot Status Strip API missing');
assert.strictEqual(api.contract,'PMP_BOOT_STATUS_STRIP_PASSIVE_CONTRACT_V1');
assert.strictEqual(api.derive({elapsed_ms:0,app_orchestrator_present:false,app_orchestrator_valid:false}).state,'BOOTING');
assert.strictEqual(api.derive({elapsed_ms:9000,app_orchestrator_present:false,app_orchestrator_valid:false}).state,'BOOT_SLOW');
assert.strictEqual(api.derive({elapsed_ms:10,failure_signal:true,failure_detail:'blocked'}).state,'BOOT_FAILURE');
assert.strictEqual(api.derive({elapsed_ms:10,app_orchestrator_present:true,app_orchestrator_valid:false}).state,'BOOT_FAILURE');
assert.strictEqual(api.derive({elapsed_ms:10,app_orchestrator_present:true,app_orchestrator_valid:true,app_orchestrator_acknowledged:true,route_ready:true,runtime_ready:true}).state,'READY_ACKNOWLEDGED');
assert.deepStrictEqual(JSON.parse(JSON.stringify(api.sideEffects)),{routeAssignments:0,persistedUserDataWrites:0,appOrchestratorOwnershipTransfers:0,startupRepairs:0});
for(const forbidden of ['localStorage','sessionStorage','indexedDB','location.assign','location.replace','location.href=','frame.src=','document.write'])assert(!source.includes(forbidden),`forbidden side effect token: ${forbidden}`);
const orch='pmp-app-orchestrator-v1.js?fresh=app-orchestrator-final-clean-startup-certification-20260709A';
const strip='pmp-boot-status-strip-owner-v1.js?fresh=pass4-unit2-current-path-20260725A';
assert(inner.includes(orch)&&inner.includes(strip),'current-path scripts missing');
assert(inner.indexOf(orch)<inner.indexOf(strip),'strip must load immediately after App Orchestrator opportunity');
console.log('PASS: Unit 2 passive strip states, malformed-input behavior, load order, and zero-side-effect contract verified');
