#!/usr/bin/env node
'use strict';
const assert=require('assert');
const fs=require('fs');
const path=require('path');
const ROOT=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(ROOT,'pmp-mount-lifecycle-contract-v1.js'),'utf8');
const api=require(path.join(ROOT,'pmp-mount-lifecycle-contract-v1.js'));

const POLICY={
  routeAuthority:'current_map_owner',
  allowedMountOwners:['app_orchestrator_owner','bank_screen_owner'],
  allowedSources:['current_map_owner','app_orchestrator_owner','bank_screen_owner'],
  maxOperations:4,
  maxEventsPerOperation:9
};
const OP='pmp-mount:current-app:op-001';
function event(sequence,state,owner,details,overrides){
  return Object.assign({
    contract_version:api.contractVersion,
    operation_id:OP,
    monotonic_sequence:sequence,
    owner,
    source:owner,
    state,
    reason_code:state+'_TEST',
    observed_at:`2026-07-26T07:02:${String(sequence).padStart(2,'0')}Z`,
    trust:'OWNER_ATTESTED'
  },details===undefined?{}:{details},overrides||{});
}
function route(sequence,state,details,overrides){
  return event(sequence,state,'current_map_owner',details,overrides);
}
function mount(sequence,state,details,overrides){
  return event(sequence,state,'app_orchestrator_owner',details,overrides);
}

assert.strictEqual(api.version,'1.0.0');
assert.strictEqual(api.contractVersion,'PMP_MOUNT_LIFECYCLE_CONTRACT_V1');
assert.strictEqual(api.registryOwner,'mount_registry_owner');
assert.deepStrictEqual(api.activeStates,['ROUTE_REQUESTED','OWNER_RESOLVED','MOUNT_STARTED','MOUNTED','READY']);
assert.deepStrictEqual(api.failureStates,['SLOW','DEGRADED','BLOCKED','FAILED']);
assert.deepStrictEqual(api.trustLevels,['OWNER_ATTESTED','OBSERVER_REPORTED','INFERRED']);

const registry=api.createRegistry(POLICY);
const happy=[
  route(1,'ROUTE_REQUESTED',{route:'current_app'}),
  route(2,'OWNER_RESOLVED',{resolved_owner:'app_orchestrator_owner'}),
  mount(3,'MOUNT_STARTED',{mount_point:'current_app'}),
  mount(4,'MOUNTED',{mount_point:'current_app'}),
  mount(5,'READY',{acknowledged:true})
];
for(const e of happy){
  const out=registry.apply(e);
  assert.strictEqual(out.accepted,true);
  assert.strictEqual(out.code,'ACCEPTED');
}
assert.strictEqual(registry.operation(OP).state,'READY');

const duplicate=registry.apply(happy[4]);
assert.deepStrictEqual(
  {accepted:duplicate.accepted,mutated:duplicate.mutated,code:duplicate.code},
  {accepted:true,mutated:false,code:'DUPLICATE_IGNORED'}
);
const conflict=registry.apply(Object.assign({},happy[4],{reason_code:'CONFLICT'}));
assert.strictEqual(conflict.code,'REJECTED_DUPLICATE_CONFLICT');
assert.strictEqual(registry.operation(OP).events.length,5);

const stale=registry.apply(mount(4,'MOUNTED',{mount_point:'current_app'}));
assert.strictEqual(stale.code,'REJECTED_STALE_SEQUENCE');
const gap=registry.apply(mount(7,'DEGRADED',{detail:'gap'}));
assert.strictEqual(gap.code,'REJECTED_SEQUENCE_GAP');
const timeBack=registry.apply(mount(6,'DEGRADED',{detail:'clock'},{
  observed_at:'2026-07-26T07:02:03Z'
}));
assert.strictEqual(timeBack.code,'REJECTED_TIME_REGRESSION');

const wrongOwner=registry.apply(event(6,'DEGRADED','bank_screen_owner',{detail:'wrong'}));
assert.strictEqual(wrongOwner.code,'REJECTED_MOUNT_OWNER');
const inferred=registry.apply(mount(6,'DEGRADED',{detail:'observer'},{trust:'INFERRED'}));
assert.strictEqual(inferred.code,'REJECTED_NON_AUTHORITATIVE_TRUST');
const degraded=registry.apply(mount(6,'DEGRADED',{detail:'real'}));
assert.strictEqual(degraded.code,'ACCEPTED');
const recovered=registry.apply(mount(7,'READY',{acknowledged:true}));
assert.strictEqual(recovered.code,'ACCEPTED');

const OP2='pmp-mount:bank:op-002';
function bank(sequence,state,owner,details,overrides){
  return event(sequence,state,owner,details,Object.assign({operation_id:OP2},overrides||{}));
}
const invalid=api.createRegistry(POLICY);
assert.strictEqual(invalid.apply(bank(1,'MOUNT_STARTED','bank_screen_owner')).code,'REJECTED_MISSING_OPERATION');
assert.strictEqual(invalid.apply(bank(1,'ROUTE_REQUESTED','current_map_owner')).code,'ACCEPTED');
assert.strictEqual(invalid.apply(bank(2,'MOUNT_STARTED','bank_screen_owner')).code,'REJECTED_INVALID_TRANSITION');
assert.strictEqual(invalid.apply(bank(2,'OWNER_RESOLVED','current_map_owner',{resolved_owner:'unknown_owner'})).code,'REJECTED_RESOLVED_OWNER');
assert.strictEqual(invalid.apply(bank(2,'OWNER_RESOLVED','current_map_owner',{resolved_owner:'bank_screen_owner'})).code,'ACCEPTED');
assert.strictEqual(invalid.apply(bank(3,'MOUNT_STARTED','bank_screen_owner')).code,'ACCEPTED');
assert.strictEqual(invalid.apply(bank(4,'SLOW','bank_screen_owner')).code,'ACCEPTED');
assert.strictEqual(invalid.apply(bank(5,'MOUNTED','bank_screen_owner')).code,'ACCEPTED');
assert.strictEqual(invalid.apply(bank(6,'READY','bank_screen_owner')).code,'ACCEPTED');

for(const bad of [
  null,
  {},
  Object.assign({},route(1,'ROUTE_REQUESTED'),{contract_version:'wrong'}),
  Object.assign({},route(1,'ROUTE_REQUESTED'),{operation_id:'bad'}),
  Object.assign({},route(1,'ROUTE_REQUESTED'),{monotonic_sequence:0}),
  Object.assign({},route(1,'ROUTE_REQUESTED'),{reason_code:'bad reason'}),
  Object.assign({},route(1,'ROUTE_REQUESTED'),{observed_at:'not-a-time'}),
  Object.assign({},route(1,'ROUTE_REQUESTED'),{extra:'forbidden'})
]){
  const r=api.createRegistry(POLICY).apply(bad);
  assert.strictEqual(r.accepted,false);
  assert.strictEqual(r.mutated,false);
}

const limited=api.createRegistry(Object.assign({},POLICY,{maxOperations:1,maxEventsPerOperation:2}));
assert.strictEqual(limited.apply(route(1,'ROUTE_REQUESTED')).code,'ACCEPTED');
assert.strictEqual(limited.apply(route(2,'OWNER_RESOLVED',{resolved_owner:'app_orchestrator_owner'})).code,'ACCEPTED');
assert.strictEqual(limited.apply(mount(3,'MOUNT_STARTED')).code,'REJECTED_EVENT_RETENTION_CAPACITY');
assert.strictEqual(limited.apply(Object.assign({},route(1,'ROUTE_REQUESTED'),{
  operation_id:'pmp-mount:other:op-003'
})).code,'REJECTED_RETENTION_CAPACITY');
assert.strictEqual(limited.snapshot().operations.length,1);
assert.strictEqual(limited.snapshot().operations[0].events.length,2);

const snapshot=registry.snapshot();
const restored=api.restoreSnapshot(snapshot,POLICY);
assert.strictEqual(restored.ok,true);
assert.deepStrictEqual(restored.registry.snapshot().operations,snapshot.operations);
const badRestore=api.restoreSnapshot(Object.assign({},snapshot,{
  operations:[{events:[Object.assign({},snapshot.operations[0].events[0],{state:'MOUNTED'})]}]
}),POLICY);
assert.strictEqual(badRestore.ok,false);
assert.strictEqual(badRestore.registry,null);

let calls={registry:0,snapshot:0,scan:0};
const legacy={
  version:'1.6.3',
  atlasBuckets:['ACTIVE_CURRENT_APP'],
  keys:{registry:'pmp_mount_registry_v1'},
  registry(){calls.registry++;return {legacy:true}},
  snapshot(){calls.snapshot++;return {legacySnapshot:true}},
  scan(reason){calls.scan++;return {reason}}
};
const facade=api.createLegacyAtlasFacade(legacy,registry);
assert.deepStrictEqual(calls,{registry:0,snapshot:0,scan:0});
assert.strictEqual(facade.compatibilityMode,'ADDITIVE_NO_AUTOMATIC_SCAN_NO_STORAGE_MIGRATION');
assert.deepStrictEqual(facade.registry(),{legacy:true});
assert.deepStrictEqual(facade.snapshot(),{legacySnapshot:true});
assert.deepStrictEqual(facade.scan('manual'),{reason:'manual'});
assert.strictEqual(facade.lifecycleSnapshot().contract_version,api.contractVersion);
assert.deepStrictEqual(calls,{registry:1,snapshot:1,scan:1});

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
])assert(!source.includes(forbidden),`forbidden pure-contract token: ${forbidden}`);

console.log('PASS: P5-U2 lifecycle schema, authority, transitions, retention, restart, and compatibility facade');
