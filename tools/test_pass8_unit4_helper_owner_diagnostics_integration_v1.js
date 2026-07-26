#!/usr/bin/env node
'use strict';
const assert=require('assert');
const fs=require('fs');
const path=require('path');
const ROOT=path.resolve(__dirname,'..');
const runtimeSource=fs.readFileSync(path.join(ROOT,'pmp-helper-owner-integration-v1.js'),'utf8');
const viewSource=fs.readFileSync(path.join(ROOT,'pmp-helper-owner-diagnostics-view-v1.js'),'utf8');
const diagnosticsSource=fs.readFileSync(path.join(ROOT,'pmp-diagnostics-owner-v1.js'),'utf8');
const innerSource=fs.readFileSync(path.join(ROOT,'pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html'),'utf8');
const library=require(path.join(ROOT,'pmp-helper-owner-integration-v1.js'));
const view=require(path.join(ROOT,'pmp-helper-owner-diagnostics-view-v1.js'));
const unit2=require(path.join(ROOT,'tools/run_pass8_unit2_helper_capability_contract_v1.js'));
const unit3=require(path.join(ROOT,'tools/run_pass8_unit3_helper_registration_events_v1.js'));
let assertions=0;
function check(value,message){assertions++;assert(value,message)}
function equal(actual,expected,message){assertions++;assert.deepStrictEqual(actual,expected,message)}
function clone(value){return JSON.parse(JSON.stringify(value))}

equal(library.type,'PMP_HELPER_OWNER_INTEGRATION_V1','runtime type');
equal(library.version,'1.0.0','runtime version');
equal(library.snapshotType,'PMP_HELPER_OWNER_SNAPSHOT_V1','snapshot type');
equal(library.eventVersion,unit3.EVENT_VERSION,'exact U3 event version');
equal(library.journalVersion,unit3.JOURNAL_VERSION,'exact U3 journal version');
equal(library.capabilityContractVersion,unit2.contract().contract_version,'exact U2 capability version');
equal(library.rootAuthority,'app_orchestrator_owner','root authority');
equal(library.growthObserver,'diagnostics_owner','growth observer');
equal(library.helpers.length,14,'fourteen exact helper declarations');
equal(library.helpers.filter(row=>row.disposition==='ELIGIBLE_STATIC_CAPABILITY').length,12,'twelve eligible');
equal(library.helpers.filter(row=>row.disposition!=='ELIGIBLE_STATIC_CAPABILITY').length,2,'two held declarations');
equal(library.unknownSources.length,9,'nine unknown sources held');
equal(view.type,'PMP_HELPER_OWNER_DIAGNOSTICS_VIEW_V1','view type');
equal(view.version,'1.0.0','view version');
equal(view.maximumVisibleEvents,128,'view event bound');

const unit2Rows=unit2.inventory().declared;
for(const expected of unit2Rows){
  const actual=library.helpers.find(row=>row.helper_id===expected.helper_id);
  check(!!actual,'embedded helper exists '+expected.helper_id);
  equal(actual.helper_source_sha256,expected.helper_source_sha256,'source hash '+expected.helper_id);
  equal(actual.canonical_owner_id,expected.canonical_owner_id,'owner '+expected.helper_id);
  equal(actual.section_id,expected.section_id,'section '+expected.helper_id);
  equal(actual.slot,expected.slot,'slot '+expected.helper_id);
  equal(actual.growth_source,expected.growth_source,'growth '+expected.helper_id);
  equal(actual.disposition,expected.disposition,'disposition '+expected.helper_id);
  equal(actual.guard_requirement_count,expected.guard_requirements.length,'guard count '+expected.helper_id);
}
equal(Array.from(library.unknownSources).sort(),unit2.contract().unknown_helper_sources.slice().sort(),'unknown source binding');

const knownOwners=new Set(unit2Rows.map(row=>`${row.canonical_owner_id}/${row.section_id}`));
const sectionRuntime={
  available:true,
  snapshot(){
    return {
      type:'PMP_SECTION_OWNER_MOUNT_REGISTRY_SNAPSHOT_V1',
      registered:Array.from(knownOwners).map(value=>{
        const [owner_id,section_id]=value.split('/');
        return {owner_id,section_id,status:'REGISTERED_CAPABILITY_BOUND'};
      })
    };
  },
  applyOwnerEvent(){throw new Error('must never be called')}
};
const runtime=library.create(sectionRuntime);
equal(runtime.available,true,'runtime available');
equal(runtime.mode,'PASSIVE_EXPLICIT_HELPER_EVENTS_ONLY','passive explicit mode');
equal(runtime.dependencies.section_owner_runtime_available,true,'section owner dependency');
for(const value of Object.values(runtime.sideEffects))equal(value,0,'runtime external effect zero');

function make(helperId,type,sequence,prior=null,overrides={}){
  let event=unit3.makeEvent(helperId,type,sequence,overrides);
  event.previous_event_digest=prior?unit3.digest(prior):null;
  return event;
}
const register=make('pass2_atlas_adapter','HELPER_REGISTERED',1);
equal(library.digest(register),unit3.digest(register),'production digest equals U3 SHA-256');
let outcome=runtime.applyHelperEvent(register);
equal(outcome.code,'HELPER_REGISTERED','register accepted');
equal(outcome.accepted,true,'register accepted flag');
equal(outcome.mutated,true,'register mutates isolated state');
equal(outcome.authority_granted,false,'register grants no authority');
equal(outcome.behavior_authorized,false,'register authorizes no behavior');

const update=make('pass2_atlas_adapter','HELPER_UPDATED',2,register,{
  registry_epoch:2,source_version:'source:v2'
});
equal(library.digest(update),unit3.digest(update),'update digest exact');
outcome=runtime.applyHelperEvent(update);
equal(outcome.code,'HELPER_UPDATED','update accepted');
const growth=make('continuous_run_bank_order_frame_loader','HELPER_GROWTH_OBSERVED',3,update,{
  registry_epoch:2
});
equal(library.digest(growth),unit3.digest(growth),'growth digest exact');
outcome=runtime.applyHelperEvent(growth);
equal(outcome.code,'HELPER_GROWTH_RECORDED_NO_AUTHORITY','growth recorded');
equal(outcome.authority_granted,false,'growth no authority');
equal(outcome.behavior_authorized,false,'growth no behavior');

const snapshot=runtime.snapshot();
equal(snapshot.type,'PMP_HELPER_OWNER_SNAPSHOT_V1','snapshot type');
equal(snapshot.registered.length,1,'one registered helper');
equal(snapshot.registered[0].helper_id,'pass2_atlas_adapter','atlas registered');
equal(snapshot.registered[0].status,'REGISTERED_STATIC_EVENT_ONLY','static event status');
equal(snapshot.registered[0].behavior_authorized,false,'snapshot no behavior');
equal(snapshot.pending_growth.length,1,'one pending growth');
equal(snapshot.pending_growth[0].helper_id,'continuous_run_bank_order_frame_loader','growth helper');
equal(snapshot.pending_growth[0].status,'OBSERVED_PENDING_NO_AUTHORITY','growth pending');
equal(snapshot.held_declared.length,2,'two held in snapshot');
equal(snapshot.unknown_sources.length,9,'nine unknown in snapshot');
equal(snapshot.journal.length,3,'three journal entries');
equal(snapshot.diagnostics.length,3,'three diagnostic entries');
equal(snapshot.journal.map(row=>row.operation_id),snapshot.diagnostics.map(row=>row.operation_id),'shared operation identity');
equal(snapshot.counts.eligible_static,12,'snapshot eligible count');
equal(snapshot.counts.held_declared,2,'snapshot held count');
equal(snapshot.counts.unknown_sources,9,'snapshot unknown count');
equal(snapshot.counts.accepted,3,'snapshot accepted count');
for(const value of Object.values(snapshot.side_effects))equal(value,0,'snapshot external effect zero');

const diagnostic=view.read(runtime);
equal(diagnostic.status,'READY_WITH_PENDING_GROWTH','diagnostic status');
equal(diagnostic.available,true,'diagnostic available');
equal(diagnostic.registered_count,1,'diagnostic registered');
equal(diagnostic.pending_growth_count,1,'diagnostic pending');
equal(diagnostic.held_declared_count,2,'diagnostic held');
equal(diagnostic.unknown_source_count,9,'diagnostic unknown');
equal(diagnostic.visible_event_count,3,'diagnostic events');
equal(diagnostic.events.map(row=>row.operation_id),snapshot.diagnostics.map(row=>row.operation_id),'diagnostic operation identity');
equal(diagnostic.events.every(row=>row.authority_granted===false),true,'diagnostic no grants');
equal(diagnostic.events.every(row=>row.behavior_authorized===false),true,'diagnostic no behavior');
equal(diagnostic.disclosure.capability_ids_exposed,false,'capability IDs hidden');
equal(diagnostic.disclosure.helper_source_hashes_exposed,false,'source hashes hidden');
equal(diagnostic.disclosure.raw_authority_payloads_exposed,false,'authority hidden');
equal(diagnostic.disclosure.source_versions_exposed,false,'source versions hidden');
const diagnosticText=JSON.stringify(diagnostic);
check(!diagnosticText.includes('cap:p8u2:'),'no capability ID disclosed');
check(!diagnosticText.includes(unit2Rows[0].helper_source_sha256),'no source hash disclosed');
check(!diagnosticText.includes('"authority"'),'no raw authority disclosed');
check(!diagnosticText.includes('source:v2'),'no source version disclosed');
for(const value of Object.values(diagnostic.side_effects))equal(value,0,'view external effect zero');

equal(view.read(null).status,'HELPER_OWNER_RUNTIME_UNAVAILABLE','missing runtime');
equal(view.read({available:true,snapshot(){return {type:'wrong'}}}).status,'HELPER_OWNER_SNAPSHOT_MALFORMED','malformed snapshot');
equal(view.read({available:true,snapshot(){throw new Error('bounded')}}).status,'HELPER_OWNER_SNAPSHOT_ERROR','throwing snapshot');

function lastCode(events,ownerRuntime=sectionRuntime){
  const isolated=library.create(ownerRuntime);
  let result;
  for(const event of events)result=isolated.applyHelperEvent(event);
  return result.code;
}
let changed=clone(register);
changed.event_version='V2';
equal(lastCode([changed]),'REJECTED_EVENT_VERSION','wrong event version');
changed=clone(register);
changed.helper_source_sha256='0'.repeat(64);
equal(lastCode([changed]),'REJECTED_SOURCE_HASH','source mismatch');
changed=clone(register);
changed.canonical_owner_id='app_orchestrator_owner';
equal(lastCode([changed]),'REJECTED_OWNER_BINDING','owner mismatch');
changed=clone(register);
changed.section_id='bank';
equal(lastCode([changed]),'REJECTED_OWNER_BINDING','section mismatch');
changed=clone(register);
changed.slot='wrong_slot';
equal(lastCode([changed]),'REJECTED_SLOT_BINDING','slot mismatch');
changed=clone(register);
changed.growth_source='invented_growth';
equal(lastCode([changed]),'REJECTED_GROWTH_SOURCE','growth mismatch');
changed=clone(register);
changed.authority.authorizer='mount_registry_owner';
equal(lastCode([changed]),'REJECTED_REGISTRATION_AUTHORITY','forged root authority');
changed=clone(register);
changed.authority.capability_id='cap:p8u2:wrong';
equal(lastCode([changed]),'REJECTED_REGISTRATION_AUTHORITY','wrong capability');
changed=clone(growth);
changed.authority.decision='AUTHORIZED_STATIC_EVENT';
equal(lastCode([changed]),'REJECTED_GROWTH_OBSERVER_AUTHORITY','forged growth observer');

const legacy=make('legacy_helper_registry','HELPER_REGISTERED',1);
equal(lastCode([legacy]),'REJECTED_LEGACY_HELPER_HELD','legacy held');
const held=make('safe_writer_current_return_fix','HELPER_REGISTERED',1);
equal(lastCode([held]),'REJECTED_HELPER_CONFLICT_HELD','Safe Writer conflict held');
changed=clone(register);
changed.helper_id='invented_helper';
changed.authority.capability_id='cap:p8u2:invented_helper';
equal(lastCode([changed]),'REJECTED_UNKNOWN_HELPER','unknown helper held');
equal(lastCode([register],null),'REJECTED_SECTION_OWNER_RUNTIME_UNAVAILABLE','missing owner runtime');
const noOwner={available:true,snapshot(){return{type:'PMP_SECTION_OWNER_MOUNT_REGISTRY_SNAPSHOT_V1',registered:[]}}};
equal(lastCode([register],noOwner),'REJECTED_SECTION_OWNER_NOT_REGISTERED','owner must be registered');
equal(sectionRuntime.apply_calls,undefined,'no section owner mutator touched');

const duplicateRuntime=library.create(sectionRuntime);
equal(duplicateRuntime.applyHelperEvent(register).code,'HELPER_REGISTERED','duplicate seed');
equal(duplicateRuntime.applyHelperEvent(register).code,'DUPLICATE_EVENT_IGNORED','identical duplicate ignored');
equal(duplicateRuntime.snapshot().counts.duplicates,1,'duplicate counted');
changed=clone(register);
changed.operation_id='op:p8u4:conflict';
equal(duplicateRuntime.applyHelperEvent(changed).code,'REJECTED_DUPLICATE_EVENT_CONFLICT','conflicting duplicate denied');
changed=clone(growth);
changed.event_id='evt:p8u4:duplicate-operation';
changed.operation_id=register.operation_id;
equal(duplicateRuntime.applyHelperEvent(changed).code,'REJECTED_DUPLICATE_OPERATION','duplicate operation denied');

changed=clone(update);
changed.event_id='evt:p8u4:stale';
changed.operation_id='op:p8u4:stale';
changed.monotonic_sequence=1;
equal(lastCode([register,changed]),'REJECTED_STALE_SEQUENCE','stale sequence denied');
changed=clone(update);
changed.event_id='evt:p8u4:gap';
changed.operation_id='op:p8u4:gap';
changed.monotonic_sequence=3;
equal(lastCode([register,changed]),'REJECTED_SEQUENCE_GAP','sequence gap denied');
changed=clone(update);
changed.event_id='evt:p8u4:chain';
changed.operation_id='op:p8u4:chain';
changed.previous_event_digest='0'.repeat(64);
equal(lastCode([register,changed]),'REJECTED_EVENT_CHAIN','chain mismatch denied');
changed=clone(update);
changed.monotonic_sequence=1;
changed.registry_epoch=1;
changed.previous_event_digest=null;
equal(lastCode([changed]),'REJECTED_HELPER_NOT_REGISTERED','update before register denied');

const revoke=make('pass2_atlas_adapter','HELPER_REVOKED',2,register,{
  authority:unit3.authorityFor('pass2_atlas_adapter','HELPER_REVOKED',{revocation_epoch:1})
});
const revokeRuntime=library.create(sectionRuntime);
equal(revokeRuntime.applyHelperEvent(register).code,'HELPER_REGISTERED','revoke seed');
equal(revokeRuntime.applyHelperEvent(revoke).code,'HELPER_REVOKED','revoke accepted');
equal(revokeRuntime.snapshot().revoked.pass2_atlas_adapter,1,'revocation recorded');
const staleRevoke=make('pass2_atlas_adapter','HELPER_REVOKED',3,revoke,{
  registry_epoch:2,
  authority:unit3.authorityFor('pass2_atlas_adapter','HELPER_REVOKED',{revocation_epoch:1})
});
equal(revokeRuntime.applyHelperEvent(staleRevoke).code,'REJECTED_STALE_REVOCATION','stale revocation denied');

const journalPackage=library.packageJournal(runtime);
equal(journalPackage.type,unit3.JOURNAL_VERSION,'journal package type');
equal(journalPackage.entry_count,3,'journal package count');
equal(journalPackage.head_event_digest,unit3.digest(growth),'journal exact head');
let restored=library.restore(sectionRuntime,journalPackage);
equal(restored.restored,true,'journal restored');
equal(restored.code,'RESTART_REPLAY_ACCEPTED','restore code');
equal(restored.operation_ids,snapshot.journal.map(row=>row.operation_id),'restore operations');
equal(restored.runtime.snapshot().registered,snapshot.registered,'restore registered exact');
equal(restored.runtime.snapshot().pending_growth,snapshot.pending_growth,'restore growth exact');
for(const value of Object.values(restored.side_effects))equal(value,0,'restore external effect zero');
for(const mutation of [
  value=>{value.entry_count++},
  value=>{value.entries[0].event_digest='0'.repeat(64)},
  value=>{value.head_event_digest='0'.repeat(64)},
  value=>{value.snapshot_sha256='0'.repeat(64)}
]){
  const bad=clone(journalPackage);
  mutation(bad);
  restored=library.restore(sectionRuntime,bad);
  equal(restored.restored,false,'tampered restore denied');
  equal(restored.runtime.snapshot().registered.length,0,'tampered restore empty');
  equal(restored.runtime.snapshot().journal.length,0,'tampered restore no partial journal');
}

const bounded=library.create(sectionRuntime);
let prior=null;
for(let sequence=1;sequence<=130;sequence++){
  const type=sequence===1?'HELPER_REGISTERED':'HELPER_UPDATED';
  const event=make('pass2_atlas_adapter',type,sequence,prior,{
    registry_epoch:1,source_version:'source:v'+sequence,
    observed_at:'2026-07-27T01:00:00Z',
    event_id:'evt:p8u4:bounded:'+sequence,
    operation_id:'op:p8u4:bounded:'+sequence
  });
  equal(bounded.applyHelperEvent(event).accepted,true,'bounded event '+sequence);
  prior=event;
}
const boundedView=view.read(bounded);
equal(boundedView.visible_event_count,128,'bounded view count');
equal(boundedView.disclosure.events_truncated,true,'bounded view truncation');
equal(boundedView.events[0].operation_id,'op:p8u4:bounded:3','bounded view retains newest');

const installHost={PMPSectionOwnerMountRuntimeV1:sectionRuntime};
const installed=library.install(installHost);
equal(installHost.PMPHelperOwnerRuntimeV1,installed,'install exposes runtime');
equal(installed.snapshot().registered.length,0,'install registers no helper');
equal(installed.snapshot().journal.length,0,'install emits no event');
equal(installed.snapshot().side_effects.production_activations,0,'install no activation');

for(const forbidden of [
  'localStorage','sessionStorage','indexedDB','document.','fetch(',
  'XMLHttpRequest','WebSocket','location.','.src=','setTimeout(','setInterval('
]){
  check(!runtimeSource.includes(forbidden),'runtime forbidden token '+forbidden);
  check(!viewSource.includes(forbidden),'view forbidden token '+forbidden);
}
for(const forbidden of ['applyHelperEvent','applyOwnerEvent','registry.apply']){
  check(!viewSource.includes(forbidden),'view mutation token '+forbidden);
}
check(diagnosticsSource.includes('function helperOwnerView()'),'diagnostics reads Helper view');
check(diagnosticsSource.includes('readHelpers:helperOwnerView'),'diagnostics exposes read only');
check(diagnosticsSource.includes('Diagnostics cannot register or activate a Helper'),'diagnostics explains hold');
check(diagnosticsSource.includes('helper_source_hashes_exposed:false'),'diagnostics fallback redacted');
check(!diagnosticsSource.includes('PMPHelperOwnerRuntimeV1.applyHelperEvent'),'diagnostics cannot apply');
const sectionViewPos=innerSource.indexOf('pmp-section-owner-diagnostics-view-v1.js?fresh=');
const helperPos=innerSource.indexOf('pmp-helper-owner-integration-v1.js?fresh=');
const helperViewPos=innerSource.indexOf('pmp-helper-owner-diagnostics-view-v1.js?fresh=');
const authorityPos=innerSource.indexOf('pmp-authority-rules-v1.js?fresh=');
check(sectionViewPos>-1&&sectionViewPos<helperPos&&helperPos<helperViewPos&&helperViewPos<authorityPos,'load order');
equal((innerSource.match(/pmp-helper-owner-integration-v1\.js\?fresh=/g)||[]).length,1,'one runtime tag');
equal((innerSource.match(/pmp-helper-owner-diagnostics-view-v1\.js\?fresh=/g)||[]).length,1,'one view tag');

console.log(`PASS: P8-U4 bounded Helper Owner and Diagnostics integration (${assertions}/${assertions})`);
