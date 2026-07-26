#!/usr/bin/env node
'use strict';
const assert=require('assert');
const runner=require('./run_pass8_unit3_helper_registration_events_v1.js');
let assertions=0;
function check(value,message){assertions++;assert(value,message)}
function equal(actual,expected,message){assertions++;assert.deepStrictEqual(actual,expected,message)}
function code(events){return runner.evaluate(events).outcomes.slice(-1)[0].code}

equal(runner.EVENT_VERSION,'PMP_HELPER_REGISTRATION_EVENT_V1','event version');
equal(runner.JOURNAL_VERSION,'PMP_HELPER_REGISTRATION_JOURNAL_V1','journal version');
equal(runner.REQUIRED_FIELDS.length,16,'event fields');
equal(runner.AUTHORITY_FIELDS.length,6,'authority fields');
equal(runner.EVENT_TYPES.size,5,'event types');
const contract=runner.eventContract();
equal(contract.model,'APPEND_ONLY_DIGEST_CHAIN_FAIL_CLOSED','model');
equal(contract.restore_policy,'ATOMIC_EXACT_PACKAGE_OR_EMPTY','restore');
equal(contract.growth_policy,'OBSERVED_PENDING_NO_AUTHORITY','growth');
equal(contract.denial_policy,'REJECT_BEFORE_JOURNAL_OR_STATE_MUTATION','denial');

const register=runner.makeEvent('pass2_atlas_adapter','HELPER_REGISTERED',1);
const update=runner.withPrevious(runner.makeEvent('pass2_atlas_adapter','HELPER_UPDATED',2,{
  registry_epoch:2,source_version:'source:v2'
}),register);
const remove=runner.withPrevious(runner.makeEvent('pass2_atlas_adapter','HELPER_REMOVED',3,{
  registry_epoch:2
}),update);
const lifecycle=runner.evaluate([register,update,remove]);
equal(lifecycle.status,'PASS','status');
equal(lifecycle.outcomes.map(row=>row.code),['HELPER_REGISTERED','HELPER_UPDATED','HELPER_REMOVED'],'lifecycle');
equal(lifecycle.summary.accepted,3,'accepted');
equal(lifecycle.summary.rejected,0,'rejected');
equal(lifecycle.summary.registered_helpers,0,'removed');
equal(lifecycle.summary.authority_grants,0,'no grants');
equal(lifecycle.summary.shared_operation_identities,true,'operation identity');
check(runner.verifyResultHash(lifecycle),'result hash');
check(Object.values(lifecycle.effects).every(value=>value===false),'zero effects');
check(lifecycle.claim_ceiling.includes('Pure static'),'claim ceiling');
equal(lifecycle.snapshot.journal.map(row=>row.operation_id),lifecycle.snapshot.diagnostics.map(row=>row.operation_id),'diagnostic journal identity');

const growth=runner.makeEvent('continuous_run_bank_order_frame_loader','HELPER_GROWTH_OBSERVED',1);
const growthResult=runner.evaluate([growth]);
equal(growthResult.outcomes[0].code,'HELPER_GROWTH_RECORDED_NO_AUTHORITY','growth recorded');
equal(growthResult.summary.pending_growth,1,'growth pending');
equal(growthResult.summary.registered_helpers,0,'growth not registered');
equal(growthResult.snapshot.pending_growth[0].status,'OBSERVED_PENDING_NO_AUTHORITY','growth status');
equal(growthResult.snapshot.pending_growth[0].authority_granted,false,'growth no grant');

for(const row of runner.helperRows().filter(item=>item.disposition==='ELIGIBLE_STATIC_CAPABILITY')){
  const event=runner.makeEvent(row.helper_id,'HELPER_REGISTERED',1);
  const result=runner.evaluate([event]);
  equal(result.outcomes[0].code,'HELPER_REGISTERED',`${row.helper_id} register`);
  equal(result.snapshot.registered[0].canonical_owner_id,row.canonical_owner_id,`${row.helper_id} owner`);
  equal(result.snapshot.registered[0].slot,row.slot,`${row.helper_id} slot`);
  equal(result.snapshot.registered[0].helper_source_sha256,row.helper_source_sha256,`${row.helper_id} source`);
}
equal(code([runner.makeEvent('legacy_helper_registry','HELPER_REGISTERED',1)]),'REJECTED_LEGACY_HELPER_HELD','legacy held');
equal(code([runner.makeEvent('safe_writer_current_return_fix','HELPER_REGISTERED',1)]),'REJECTED_HELPER_CONFLICT_HELD','Safe Writer held');

const malformed={...register};delete malformed.slot;
equal(code([malformed]),'REJECTED_MALFORMED_EVENT','malformed denied');
equal(code([{...register,event_version:'V2'}]),'REJECTED_EVENT_VERSION','version denied');
equal(code([{...register,helper_source_sha256:'0'.repeat(64)}]),'REJECTED_SOURCE_HASH','source denied');
equal(code([{...register,canonical_owner_id:'app_orchestrator_owner'}]),'REJECTED_OWNER_BINDING','owner denied');
equal(code([{...register,section_id:'app_orchestrator'}]),'REJECTED_OWNER_BINDING','section denied');
equal(code([{...register,slot:'other_slot'}]),'REJECTED_SLOT_BINDING','slot denied');
equal(code([{...register,growth_source:'other_growth'}]),'REJECTED_GROWTH_SOURCE','growth binding denied');
equal(code([{...register,helper_id:'unknown_helper'}]),'REJECTED_UNKNOWN_HELPER','unknown denied');

const wrongAuthority=JSON.parse(JSON.stringify(register));
wrongAuthority.authority.authorizer='mount_registry_owner';
equal(code([wrongAuthority]),'REJECTED_REGISTRATION_AUTHORITY','authority denied');
const wrongContract=JSON.parse(JSON.stringify(register));
wrongContract.authority.contract_version='V0';
equal(code([wrongContract]),'REJECTED_REGISTRATION_AUTHORITY','contract denied');
const growthOnNormal=runner.makeEvent('pass2_atlas_adapter','HELPER_GROWTH_OBSERVED',1);
equal(code([growthOnNormal]),'REJECTED_GROWTH_OBSERVER_AUTHORITY','non-growth denied');
const forgedGrowth=JSON.parse(JSON.stringify(growth));
forgedGrowth.authority.decision='AUTHORIZED_STATIC_EVENT';
equal(code([forgedGrowth]),'REJECTED_GROWTH_OBSERVER_AUTHORITY','growth authority denied');

const stale={...update,monotonic_sequence:1};
equal(code([register,stale]),'REJECTED_STALE_SEQUENCE','stale denied');
const gap={...update,monotonic_sequence:3};
equal(code([register,gap]),'REJECTED_SEQUENCE_GAP','gap denied');
const epochGap={...update,registry_epoch:3};
equal(code([register,epochGap]),'REJECTED_EPOCH_GAP','epoch gap denied');
const badChain={...update,previous_event_digest:'0'.repeat(64)};
equal(code([register,badChain]),'REJECTED_EVENT_CHAIN','chain denied');
const timeRegression={...update,observed_at:'2026-07-26T00:00:00Z'};
equal(code([register,timeRegression]),'REJECTED_TIME_REGRESSION','time denied');

const exactDuplicate=runner.evaluate([register,register]);
equal(exactDuplicate.outcomes[1].code,'DUPLICATE_EVENT_IGNORED','exact duplicate ignored');
equal(exactDuplicate.outcomes[1].mutated,false,'duplicate no mutation');
const conflictingDuplicate=JSON.parse(JSON.stringify(register));
conflictingDuplicate.source_version='source:v2';
equal(code([register,conflictingDuplicate]),'REJECTED_DUPLICATE_EVENT_CONFLICT','duplicate conflict');
const sameOperation=runner.makeEvent('authority_rules','HELPER_REGISTERED',2,{
  operation_id:register.operation_id,
  previous_event_digest:runner.digest(register)
});
equal(code([register,sameOperation]),'REJECTED_DUPLICATE_OPERATION','duplicate operation');

const missingUpdate=runner.makeEvent('pass2_atlas_adapter','HELPER_UPDATED',1);
equal(code([missingUpdate]),'REJECTED_HELPER_NOT_REGISTERED','update missing');
const duplicateHelper=runner.withPrevious(runner.makeEvent('pass2_atlas_adapter','HELPER_REGISTERED',2),register);
equal(code([register,duplicateHelper]),'REJECTED_DUPLICATE_HELPER','duplicate helper');

const revoke=runner.withPrevious(runner.makeEvent('pass2_atlas_adapter','HELPER_REVOKED',2,{
  authority:runner.authorityFor('pass2_atlas_adapter','HELPER_REVOKED',{revocation_epoch:1})
}),register);
const revoked=runner.evaluate([register,revoke]);
equal(revoked.outcomes[1].code,'HELPER_REVOKED','revoked');
equal(revoked.summary.revoked_helpers,1,'revoked count');
equal(revoked.snapshot.registered[0].status,'REVOKED_STATIC_EVENT_ONLY','revoked status');
const staleRevoke=runner.withPrevious(runner.makeEvent('pass2_atlas_adapter','HELPER_REVOKED',2),register);
equal(code([register,staleRevoke]),'REJECTED_STALE_REVOCATION','stale revoke');

for(const key of runner.REQUIRED_FIELDS)check(Object.prototype.hasOwnProperty.call(register,key),`event ${key}`);
for(const key of runner.AUTHORITY_FIELDS)check(Object.prototype.hasOwnProperty.call(register.authority,key),`authority ${key}`);
for(const outcome of lifecycle.outcomes.concat(growthResult.outcomes))equal(outcome.authority_granted,false,`${outcome.code} no grant`);

const packageValue=runner.packageJournal(lifecycle);
equal(packageValue.entry_count,3,'package count');
equal(packageValue.head_event_digest,lifecycle.snapshot.journal[2].event_digest,'package head');
check(/^[0-9a-f]{64}$/.test(packageValue.snapshot_sha256),'snapshot seal');
const restored=runner.restoreJournal(packageValue);
equal(restored.status,'RESTORED','restore status');
equal(restored.code,'JOURNAL_RESTORED','restore code');
equal(restored.restored,true,'restored true');
equal(restored.result.snapshot,lifecycle.snapshot,'restored snapshot exact');
equal(restored.result.result_sha256,lifecycle.result_sha256,'restored result exact');

for(const [name,mutate,expected] of [
  ['count',p=>{p.entry_count+=1},'REJECTED_JOURNAL_COUNT'],
  ['digest',p=>{p.entries[0].event_digest='0'.repeat(64)},'REJECTED_JOURNAL_DIGEST'],
  ['head',p=>{p.head_event_digest='0'.repeat(64)},'REJECTED_JOURNAL_HEAD'],
  ['snapshot',p=>{p.snapshot_sha256='0'.repeat(64)},'REJECTED_JOURNAL_SNAPSHOT']
]){
  const candidate=JSON.parse(JSON.stringify(packageValue));mutate(candidate);
  const result=runner.restoreJournal(candidate);
  equal(result.status,'FAIL_CLOSED_EMPTY',`${name} empty`);
  equal(result.code,expected,`${name} code`);
  equal(result.result.snapshot.registered,[],`${name} no partial state`);
}
const scenario=runner.scenarioResult();
equal(scenario.status,'PASS','scenario status');
equal(scenario.result.summary.accepted,3,'scenario accepted');
equal(scenario.result.summary.registered_helpers,1,'scenario registered');
equal(scenario.result.summary.pending_growth,1,'scenario growth');
equal(scenario.restore.status,'RESTORED','scenario restored');
check(Object.values(scenario.result.effects).every(value=>value===false),'scenario effects');

const tampered=JSON.parse(JSON.stringify(lifecycle));
tampered.summary.authority_grants=1;
equal(runner.verifyResultHash(tampered),false,'tamper denied');
console.log(`PASS: P8-U3 Helper registration events (${assertions}/${assertions})`);
