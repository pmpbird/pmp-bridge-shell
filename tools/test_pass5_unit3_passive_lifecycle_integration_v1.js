#!/usr/bin/env node
'use strict';
const assert=require('assert');
const fs=require('fs');
const path=require('path');
const ROOT=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(ROOT,'pmp-mount-lifecycle-runtime-v1.js'),'utf8');
const contract=require(path.join(ROOT,'pmp-mount-lifecycle-contract-v1.js'));
const library=require(path.join(ROOT,'pmp-mount-lifecycle-runtime-v1.js'));

let calls={registry:0,snapshot:0,scan:0};
const legacy={
  version:'1.6.3',
  atlasBuckets:['ACTIVE_CURRENT_APP'],
  keys:{registry:'pmp_mount_registry_v1'},
  registry(){calls.registry++;return {legacy:true}},
  snapshot(){calls.snapshot++;return {legacySnapshot:true}},
  scan(reason){calls.scan++;return {reason}}
};
const runtime=library.createRuntime(contract,legacy);
assert.strictEqual(runtime.available,true);
assert.strictEqual(runtime.mode,'PASSIVE_EXPLICIT_OWNER_EVENTS_ONLY');
assert.deepStrictEqual(calls,{registry:0,snapshot:0,scan:0});
assert.strictEqual(runtime.lifecycleSnapshot().operations.length,0);
assert.strictEqual(runtime.sideEffects.automaticLifecycleEvents,0);
assert.strictEqual(runtime.sideEffects.storageMigrations,0);

const operation='pmp-mount:current-app:unit3-001';
function event(sequence,state,owner,details,overrides){
  return Object.assign({
    contract_version:contract.contractVersion,
    operation_id:operation,
    monotonic_sequence:sequence,
    owner,
    source:owner,
    state,
    reason_code:state+'_UNIT3',
    observed_at:`2026-07-26T07:45:${String(sequence).padStart(2,'0')}Z`,
    trust:'OWNER_ATTESTED'
  },details===undefined?{}:{details},overrides||{});
}
const events=[
  event(1,'ROUTE_REQUESTED','current_map_owner',{route:'current_app'}),
  event(2,'OWNER_RESOLVED','current_map_owner',{resolved_owner:'app_orchestrator_owner'}),
  event(3,'MOUNT_STARTED','app_orchestrator_owner',{mount_point:'current_app'}),
  event(4,'MOUNTED','app_orchestrator_owner',{mount_point:'current_app'}),
  event(5,'READY','app_orchestrator_owner',{acknowledged:true})
];
for(const item of events)assert.strictEqual(runtime.applyOwnerEvent(item).code,'ACCEPTED');
assert.strictEqual(runtime.lifecycleOperation(operation).state,'READY');
assert.strictEqual(runtime.applyOwnerEvent(events[4]).code,'DUPLICATE_IGNORED');
assert.strictEqual(runtime.lifecycleOperation(operation).events.length,5);

const operation2='pmp-mount:bank:unit3-002';
const observer=Object.assign({},events[0],{
  operation_id:operation2,
  trust:'OBSERVER_REPORTED'
});
assert.strictEqual(runtime.applyOwnerEvent(observer).code,'REJECTED_NON_AUTHORITATIVE_TRUST');
assert.strictEqual(runtime.lifecycleOperation(operation2),null);

assert.deepStrictEqual(runtime.legacyCompatibility.registry(),{legacy:true});
assert.deepStrictEqual(runtime.legacyCompatibility.snapshot(),{legacySnapshot:true});
assert.deepStrictEqual(runtime.legacyCompatibility.scan('explicit-unit3'),{reason:'explicit-unit3'});
assert.deepStrictEqual(calls,{registry:1,snapshot:1,scan:1});

const host={
  PMPMountLifecycleContractV1:contract,
  PMPMountRegistryV1:legacy
};
const installed=library.install(host);
assert.strictEqual(installed.available,true);
assert.strictEqual(library.install(host),installed);
assert.strictEqual(host.PMPMountLifecycleRuntimeV1,installed);
assert.strictEqual(host.PMPMountRegistryLifecycleCompatibilityV1,installed.legacyCompatibility);
assert.deepStrictEqual(calls,{registry:1,snapshot:1,scan:1});
assert.strictEqual(installed.lifecycleSnapshot().operations.length,0);

for(const hostWithoutDependencies of [{}, {PMPMountLifecycleContractV1:contract}, {PMPMountRegistryV1:legacy}]){
  const failed=library.install(hostWithoutDependencies);
  assert.strictEqual(failed.available,false);
  assert.strictEqual(failed.mode,'FAIL_CLOSED_NO_PARTIAL_REGISTRY');
  assert.strictEqual(failed.lifecycleSnapshot(),null);
  assert.strictEqual(failed.applyOwnerEvent(events[0]).code,'REJECTED_LIFECYCLE_RUNTIME_UNAVAILABLE');
}

for(const forbidden of [
  'localStorage',
  'sessionStorage',
  'indexedDB',
  'document.',
  'fetch(',
  'XMLHttpRequest',
  'setTimeout(',
  'setInterval(',
  'location.',
  '.src='
])assert(!source.includes(forbidden),`forbidden passive-runtime token: ${forbidden}`);
assert.strictEqual((source.match(/registry\.apply\(event\)/g)||[]).length,1);
assert.strictEqual((source.match(/function applyOwnerEvent\(/g)||[]).length,1);

console.log('PASS: P5-U3 passive lifecycle runtime integration and zero-automatic-effect boundary');
