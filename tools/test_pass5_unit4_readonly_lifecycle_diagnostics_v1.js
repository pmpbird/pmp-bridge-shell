#!/usr/bin/env node
'use strict';
const assert=require('assert');
const fs=require('fs');
const path=require('path');
const ROOT=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(ROOT,'pmp-mount-lifecycle-diagnostics-view-v1.js'),'utf8');
const diagnosticsSource=fs.readFileSync(path.join(ROOT,'pmp-diagnostics-owner-v1.js'),'utf8');
const view=require(path.join(ROOT,'pmp-mount-lifecycle-diagnostics-view-v1.js'));

assert.strictEqual(view.version,'1.0.0');
assert.strictEqual(view.type,'PMP_MOUNT_LIFECYCLE_DIAGNOSTICS_VIEW_V1');
assert.strictEqual(view.maximumVisibleOperations,64);

const missing=view.read(null);
assert.strictEqual(missing.status,'LIFECYCLE_RUNTIME_UNAVAILABLE');
assert.strictEqual(missing.available,false);
assert.strictEqual(missing.operation_count,0);
assert.strictEqual(missing.side_effects.lifecycle_events_applied,0);
assert.strictEqual(missing.side_effects.persisted_user_data_writes,0);

const unavailable=view.read({
  available:false,
  dependencyStatus:{contract_available:true,legacy_atlas_available:false}
});
assert.deepStrictEqual(unavailable.dependencies,{
  contract_available:true,
  legacy_atlas_available:false
});

const failed=view.read({
  available:true,
  dependencyStatus:{contract_available:true,legacy_atlas_available:true},
  lifecycleSnapshot(){throw new Error('bounded-test')}
});
assert.strictEqual(failed.status,'LIFECYCLE_SNAPSHOT_ERROR');

const malformed=view.read({
  available:true,
  dependencyStatus:{contract_available:true,legacy_atlas_available:true},
  lifecycleSnapshot(){return {type:'wrong',operations:[]}}
});
assert.strictEqual(malformed.status,'LIFECYCLE_SNAPSHOT_MALFORMED');

let reads=0;
const snapshot={
  type:'PMP_MOUNT_LIFECYCLE_REGISTRY_SNAPSHOT_V1',
  contract_version:'PMP_MOUNT_LIFECYCLE_CONTRACT_V1',
  registry_owner:'mount_registry_owner',
  policy:{
    routeAuthority:'current_map_owner',
    maxOperations:256,
    maxEventsPerOperation:64,
    retention:'REJECT_AT_CAPACITY_NO_EVIDENCE_DELETION',
    restart:'REPLAY_VALIDATED_SNAPSHOT_ONLY'
  },
  operations:[
    {
      operation_id:'pmp-mount:second:unit4-002',
      state:'FAILED',
      last_sequence:4,
      last_observed_at:'2026-07-26T08:09:04Z',
      resolved_owner:'bank_screen_owner',
      events:[{details:{secret:'DO_NOT_EXPOSE_SECOND_PAYLOAD'}}]
    },
    {
      operation_id:'pmp-mount:first:unit4-001',
      state:'READY',
      last_sequence:5,
      last_observed_at:'2026-07-26T08:09:05Z',
      resolved_owner:'app_orchestrator_owner',
      events:[{details:{secret:'DO_NOT_EXPOSE_FIRST_PAYLOAD'}}]
    }
  ],
  diagnostics:{
    accepted:9,
    duplicates:1,
    rejected:2,
    rejection_counts:{
      REJECTED_NON_AUTHORITATIVE_TRUST:1,
      REJECTED_SEQUENCE_GAP:1,
      'bad key':900
    },
    last_rejection:{
      code:'REJECTED_SEQUENCE_GAP',
      operation_id:'pmp-mount:sensitive:do-not-disclose',
      monotonic_sequence:7,
      injected_payload:'DO_NOT_EXPOSE_REJECTION_PAYLOAD'
    }
  }
};
const runtime={
  available:true,
  dependencyStatus:{contract_available:true,legacy_atlas_available:true},
  lifecycleSnapshot(){reads++;return snapshot}
};
const result=view.read(runtime);
assert.strictEqual(reads,1);
assert.strictEqual(result.status,'READY_WITH_OPERATIONS');
assert.strictEqual(result.registry_owner,'mount_registry_owner');
assert.strictEqual(result.operation_count,2);
assert.deepStrictEqual(result.operations.map(x=>x.operation_id),[
  'pmp-mount:first:unit4-001',
  'pmp-mount:second:unit4-002'
]);
assert.strictEqual(result.operations[0].event_count,1);
assert.strictEqual(result.operations[1].terminal,true);
assert.deepStrictEqual(result.rejections.counts,{
  REJECTED_NON_AUTHORITATIVE_TRUST:1,
  REJECTED_SEQUENCE_GAP:1
});
assert.deepStrictEqual(result.rejections.last,{
  code:'REJECTED_SEQUENCE_GAP',
  operation_present:true,
  monotonic_sequence:7
});
const encoded=JSON.stringify(result);
for(const secret of [
  'DO_NOT_EXPOSE_SECOND_PAYLOAD',
  'DO_NOT_EXPOSE_FIRST_PAYLOAD',
  'pmp-mount:sensitive:do-not-disclose',
  'DO_NOT_EXPOSE_REJECTION_PAYLOAD'
])assert(!encoded.includes(secret),secret);
assert.strictEqual(result.disclosure.event_details_exposed,false);
assert.strictEqual(result.disclosure.raw_event_payloads_exposed,false);
assert.deepStrictEqual(view.read(runtime),result);
assert.strictEqual(reads,2);

const many=Object.assign({},snapshot,{
  operations:Array.from({length:65},(_,index)=>({
    operation_id:`pmp-mount:bounded:unit4-${String(index).padStart(3,'0')}`,
    state:'READY',
    last_sequence:5,
    last_observed_at:'2026-07-26T08:09:05Z',
    resolved_owner:'app_orchestrator_owner',
    events:[{}]
  }))
});
const bounded=view.read({
  available:true,
  dependencyStatus:runtime.dependencyStatus,
  lifecycleSnapshot(){return many}
});
assert.strictEqual(bounded.operation_count,65);
assert.strictEqual(bounded.visible_operation_count,64);
assert.strictEqual(bounded.disclosure.operations_truncated,true);

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
  '.src=',
  'applyOwnerEvent',
  'registry.apply'
])assert(!source.includes(forbidden),`forbidden read-only-view token: ${forbidden}`);
assert.strictEqual((source.match(/runtime\.lifecycleSnapshot\(\)/g)||[]).length,1);
assert(diagnosticsSource.includes("mount_lifecycle:lifecycle"));
assert(diagnosticsSource.includes("readMountLifecycle:lifecycleView"));
assert(diagnosticsSource.includes("lifecycle_event_application:'not_attempted'"));
assert(!diagnosticsSource.includes('applyOwnerEvent'));

console.log('PASS: P5-U4 redacted read-only lifecycle Diagnostics view and zero-effect boundary');
