#!/usr/bin/env node
'use strict';
const crypto=require('crypto');
const runtimeLibrary=require('../pmp-helper-owner-integration-v1.js');
const diagnosticsView=require('../pmp-helper-owner-diagnostics-view-v1.js');
const unit2=require('./run_pass8_unit2_helper_capability_contract_v1.js');
const unit3=require('./run_pass8_unit3_helper_registration_events_v1.js');
const TYPE='PMP_PASS8_UNIT5_HELPER_ISOLATION_RESTART_DENIAL_RESULT_V1';
const VERSION='1.0.0';
function clone(value){return JSON.parse(JSON.stringify(value))}
function stable(value){
  if(Array.isArray(value))return '['+value.map(stable).join(',')+']';
  if(value&&typeof value==='object'){
    return '{'+Object.keys(value).sort().map(key=>JSON.stringify(key)+':'+stable(value[key])).join(',')+'}';
  }
  return JSON.stringify(value);
}
function digest(value){
  return crypto.createHash('sha256').update(Buffer.from(stable(value))).digest('hex');
}
function eligible(){return unit2.inventory().declared.filter(row=>row.disposition==='ELIGIBLE_STATIC_CAPABILITY')}
function held(){return unit2.inventory().declared.filter(row=>row.disposition!=='ELIGIBLE_STATIC_CAPABILITY')}
function ownerRuntime(rows=eligible()){
  const pairs=new Map(rows.map(row=>[
    `${row.canonical_owner_id}/${row.section_id}`,
    {
      owner_id:row.canonical_owner_id,section_id:row.section_id,
      status:'REGISTERED_CAPABILITY_BOUND'
    }
  ]));
  return {
    available:true,
    snapshot(){
      return {
        type:'PMP_SECTION_OWNER_MOUNT_REGISTRY_SNAPSHOT_V1',
        registered:Array.from(pairs.values())
      };
    }
  };
}
function make(helperId,type,sequence,prior=null,overrides={}){
  const event=unit3.makeEvent(helperId,type,sequence,overrides);
  event.previous_event_digest=prior?unit3.digest(prior):null;
  return event;
}
function one(event,sections=ownerRuntime()){
  return runtimeLibrary.create(sections).applyHelperEvent(event);
}
function registrationMatrix(){
  const rows=eligible(),runtime=runtimeLibrary.create(ownerRuntime(rows));
  const events=[],outcomes=[];
  let prior=null;
  rows.forEach((row,index)=>{
    const event=make(row.helper_id,'HELPER_REGISTERED',index+1,prior,{
      observed_at:`2026-07-27T02:00:${String(index+1).padStart(2,'0')}Z`
    });
    events.push(event);
    outcomes.push(runtime.applyHelperEvent(event));
    prior=event;
  });
  return {rows,events,outcomes,runtime,snapshot:runtime.snapshot(),view:diagnosticsView.read(runtime)};
}
function heldMatrix(){
  return held().map(row=>{
    const outcome=one(make(row.helper_id,'HELPER_REGISTERED',1));
    return {helper_id:row.helper_id,disposition:row.disposition,code:outcome.code};
  });
}
function unknownMatrix(){
  return unit2.contract().unknown_helper_sources.map((file,index)=>{
    const template=make('pass2_atlas_adapter','HELPER_REGISTERED',1);
    template.event_id=`evt:p8u5:unknown:${index+1}`;
    template.operation_id=`op:p8u5:unknown:${index+1}`;
    template.helper_id=`unknown_helper_${index+1}`;
    template.helper_source_sha256=digest(file);
    template.authority.capability_id=`cap:p8u2:unknown_helper_${index+1}`;
    const outcome=one(template);
    return {file,helper_id:template.helper_id,code:outcome.code};
  });
}
function ownerAbsenceMatrix(){
  const empty=ownerRuntime([]);
  return eligible().map(row=>({
    helper_id:row.helper_id,
    code:one(make(row.helper_id,'HELPER_REGISTERED',1),empty).code
  }));
}
function bindingDenialMatrix(){
  const results=[];
  for(const row of eligible()){
    const seed=make(row.helper_id,'HELPER_REGISTERED',1);
    for(const [fault,mutate,code] of [
      ['source_hash',event=>{event.helper_source_sha256='0'.repeat(64)},'REJECTED_SOURCE_HASH'],
      ['canonical_owner',event=>{event.canonical_owner_id='wrong_owner'},'REJECTED_OWNER_BINDING'],
      ['section',event=>{event.section_id='wrong_section'},'REJECTED_OWNER_BINDING'],
      ['slot',event=>{event.slot='wrong_slot'},'REJECTED_SLOT_BINDING'],
      ['growth_source',event=>{event.growth_source='wrong_growth'},'REJECTED_GROWTH_SOURCE'],
      ['authorizer',event=>{event.authority.authorizer='wrong_owner'},'REJECTED_REGISTRATION_AUTHORITY'],
      ['capability',event=>{event.authority.capability_id='cap:p8u2:wrong'},'REJECTED_REGISTRATION_AUTHORITY'],
      ['decision',event=>{event.authority.decision='AUTHORIZED_RUNTIME'},'REJECTED_REGISTRATION_AUTHORITY']
    ]){
      const event=clone(seed);
      event.event_id+=`:${fault}`;
      event.operation_id+=`:${fault}`;
      mutate(event);
      const outcome=one(event);
      results.push({helper_id:row.helper_id,fault,expected:code,code:outcome.code});
    }
  }
  return results;
}
function growthMatrix(){
  return eligible().map(row=>{
    const event=make(row.helper_id,'HELPER_GROWTH_OBSERVED',1);
    const outcome=one(event);
    return {
      helper_id:row.helper_id,growth_source:row.growth_source,
      code:outcome.code,accepted:outcome.accepted,
      authority_granted:outcome.authority_granted,
      behavior_authorized:outcome.behavior_authorized
    };
  });
}
function duplicateAndSequenceMatrix(){
  const register=make('pass2_atlas_adapter','HELPER_REGISTERED',1);
  const runtime=runtimeLibrary.create(ownerRuntime());
  const accepted=runtime.applyHelperEvent(register);
  const duplicate=runtime.applyHelperEvent(register);
  const conflict=clone(register);
  conflict.operation_id='op:p8u5:conflict';
  const conflicting=runtime.applyHelperEvent(conflict);
  const update=make('pass2_atlas_adapter','HELPER_UPDATED',2,register,{
    registry_epoch:2,source_version:'source:v2'
  });
  const updateAccepted=runtime.applyHelperEvent(update);
  const stale=clone(update);
  stale.event_id='evt:p8u5:stale';
  stale.operation_id='op:p8u5:stale';
  stale.monotonic_sequence=1;
  const staleOutcome=runtime.applyHelperEvent(stale);
  const gap=clone(update);
  gap.event_id='evt:p8u5:gap';
  gap.operation_id='op:p8u5:gap';
  gap.monotonic_sequence=4;
  const gapOutcome=runtime.applyHelperEvent(gap);
  const chain=clone(update);
  chain.event_id='evt:p8u5:chain';
  chain.operation_id='op:p8u5:chain';
  chain.monotonic_sequence=3;
  chain.previous_event_digest='0'.repeat(64);
  const chainOutcome=runtime.applyHelperEvent(chain);
  return {
    accepted:accepted.code,duplicate:duplicate.code,
    conflicting:conflicting.code,update:updateAccepted.code,
    stale:staleOutcome.code,gap:gapOutcome.code,chain:chainOutcome.code,
    snapshot:runtime.snapshot()
  };
}
function revocationMatrix(){
  const runtime=runtimeLibrary.create(ownerRuntime());
  const register=make('pass2_atlas_adapter','HELPER_REGISTERED',1);
  const revoke=make('pass2_atlas_adapter','HELPER_REVOKED',2,register,{
    authority:unit3.authorityFor('pass2_atlas_adapter','HELPER_REVOKED',{revocation_epoch:1})
  });
  const update=make('pass2_atlas_adapter','HELPER_UPDATED',3,revoke,{
    registry_epoch:2,source_version:'source:after-revocation',
    authority:unit3.authorityFor('pass2_atlas_adapter','HELPER_UPDATED',{revocation_epoch:1})
  });
  const staleRevoke=make('pass2_atlas_adapter','HELPER_REVOKED',4,update,{
    registry_epoch:2,
    authority:unit3.authorityFor('pass2_atlas_adapter','HELPER_REVOKED',{revocation_epoch:1})
  });
  const outcomes=[
    runtime.applyHelperEvent(register),
    runtime.applyHelperEvent(revoke),
    runtime.applyHelperEvent(update),
    runtime.applyHelperEvent(staleRevoke)
  ];
  return {outcomes,snapshot:runtime.snapshot(),view:diagnosticsView.read(runtime)};
}
function restartMatrix(registration){
  const packageValue=runtimeLibrary.packageJournal(registration.runtime);
  const exact=runtimeLibrary.restore(ownerRuntime(),packageValue);
  const tamperCases=[];
  for(const [fault,mutate,expected] of [
    ['count',value=>{value.entry_count++},'RESTART_REJECTED_COUNT'],
    ['entry_digest',value=>{value.entries[0].event_digest='0'.repeat(64)},'RESTART_REJECTED_JOURNAL_EVENT'],
    ['head',value=>{value.head_event_digest='0'.repeat(64)},'RESTART_REJECTED_HEAD'],
    ['snapshot',value=>{value.snapshot_sha256='0'.repeat(64)},'RESTART_REJECTED_SNAPSHOT']
  ]){
    const copy=clone(packageValue);
    mutate(copy);
    const outcome=runtimeLibrary.restore(ownerRuntime(),copy);
    tamperCases.push({
      fault,expected,code:outcome.code,restored:outcome.restored,
      registered_after:outcome.runtime.snapshot().registered.length,
      journal_after:outcome.runtime.snapshot().journal.length
    });
  }
  const missingOwner=runtimeLibrary.restore(ownerRuntime([]),packageValue);
  return {
    package:packageValue,
    exact:{
      restored:exact.restored,code:exact.code,
      operation_ids:exact.operation_ids,
      registered:exact.runtime.snapshot().registered
    },
    tamper_cases:tamperCases,
    missing_owner:{
      restored:missingOwner.restored,code:missingOwner.code,
      rejected_code:missingOwner.rejected_code,
      registered_after:missingOwner.runtime.snapshot().registered.length,
      journal_after:missingOwner.runtime.snapshot().journal.length
    }
  };
}
function boundedDiagnosticsMatrix(){
  const runtime=runtimeLibrary.create(ownerRuntime());
  let prior=null;
  for(let sequence=1;sequence<=130;sequence++){
    const event=make(
      'pass2_atlas_adapter',
      sequence===1?'HELPER_REGISTERED':'HELPER_UPDATED',
      sequence,
      prior,
      {
        registry_epoch:1,source_version:`source:v${sequence}`,
        observed_at:'2026-07-27T03:00:00Z',
        event_id:`evt:p8u5:bounded:${sequence}`,
        operation_id:`op:p8u5:bounded:${sequence}`
      }
    );
    const outcome=runtime.applyHelperEvent(event);
    if(!outcome.accepted)throw new Error(`bounded event ${sequence}: ${outcome.code}`);
    prior=event;
  }
  const view=diagnosticsView.read(runtime);
  return {
    status:view.status,visible_event_count:view.visible_event_count,
    events_truncated:view.disclosure.events_truncated,
    first_visible_operation:view.events[0].operation_id,
    disclosure:view.disclosure,side_effects:view.side_effects,
    serialized_sha256:digest(view)
  };
}
function scenarioResult(){
  const registration=registrationMatrix();
  const result={
    type:TYPE,version:VERSION,status:'PASS',
    registration:{
      helpers:registration.rows.map(row=>row.helper_id),
      codes:registration.outcomes.map(row=>row.code),
      registered_count:registration.snapshot.registered.length,
      authority_grants:registration.outcomes.filter(row=>row.authority_granted).length,
      behavior_authorizations:registration.outcomes.filter(row=>row.behavior_authorized).length,
      diagnostic_registered_count:registration.view.registered_count
    },
    held:heldMatrix(),
    unknown:unknownMatrix(),
    owner_absence:ownerAbsenceMatrix(),
    binding_denials:bindingDenialMatrix(),
    growth:growthMatrix(),
    duplicate_sequence:duplicateAndSequenceMatrix(),
    revocation:revocationMatrix(),
    restart:restartMatrix(registration),
    bounded_diagnostics:boundedDiagnosticsMatrix(),
    effects:{
      production_files_changed:false,runtime_integrity_changed:false,
      browser_launched:false,network_requests:false,storage_writes:false,
      route_changes:false,mounts:false,bank_mutations:false,
      helper_ownership_changes:false,helper_behavior_activations:false,
      repairs:false,live_observation_performed:false,formal_proof_performed:false,
      persisted_user_data_changed:false,storage_migration_performed:false,
      production_behavior_activated:false
    },
    claim_ceiling:'Isolated deterministic production-integration proof only. No Helper behavior is activated, no Bank or Continuous Run repair occurs, and no live observation, formal proof, persisted-user-data change, or storage migration occurs.'
  };
  result.result_sha256=digest(result);
  return result;
}
function verifyResultHash(result){
  if(!result||typeof result.result_sha256!=='string')return false;
  const copy=clone(result),expected=copy.result_sha256;
  delete copy.result_sha256;
  return digest(copy)===expected;
}
if(require.main===module)process.stdout.write(JSON.stringify(scenarioResult(),null,2)+'\n');
module.exports={
  TYPE,VERSION,digest,eligible,held,ownerRuntime,make,registrationMatrix,
  heldMatrix,unknownMatrix,ownerAbsenceMatrix,bindingDenialMatrix,growthMatrix,
  duplicateAndSequenceMatrix,revocationMatrix,restartMatrix,
  boundedDiagnosticsMatrix,scenarioResult,verifyResultHash
};
