#!/usr/bin/env node
'use strict';
const assert=require('assert');
const fs=require('fs');
const path=require('path');
const ROOT=path.resolve(__dirname,'..');
const runtimeSource=fs.readFileSync(path.join(ROOT,'pmp-section-owner-mount-integration-v1.js'),'utf8');
const viewSource=fs.readFileSync(path.join(ROOT,'pmp-section-owner-diagnostics-view-v1.js'),'utf8');
const diagnosticsSource=fs.readFileSync(path.join(ROOT,'pmp-diagnostics-owner-v1.js'),'utf8');
const innerSource=fs.readFileSync(path.join(ROOT,'pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html'),'utf8');
const library=require(path.join(ROOT,'pmp-section-owner-mount-integration-v1.js'));
const view=require(path.join(ROOT,'pmp-section-owner-diagnostics-view-v1.js'));
let assertions=0;
function check(value,message){assertions++;assert(value,message)}
function equal(actual,expected,message){assertions++;assert.deepStrictEqual(actual,expected,message)}

equal(library.type,'PMP_SECTION_OWNER_MOUNT_INTEGRATION_V1','runtime type');
equal(library.version,'1.0.0','runtime version');
equal(library.eventVersion,'PMP_SECTION_OWNER_REGISTRATION_EVENT_V1','event version');
equal(library.capabilityContractVersion,'PMP_SECTION_OWNER_CAPABILITY_CONTRACT_V1','capability version');
equal(library.registryOwner,'mount_registry_owner','registry owner');
equal(Object.keys(library.owners).length,8,'eight owners');
equal(new Set(Object.values(library.owners)).size,8,'eight isolated sections');
equal(view.type,'PMP_SECTION_OWNER_DIAGNOSTICS_VIEW_V1','view type');
equal(view.version,'1.0.0','view version');
equal(view.maximumVisibleEvents,128,'view bound');

const mountRuntime={
  available:true,
  registryOwner:'mount_registry_owner',
  applyOwnerEvent(){throw new Error('must never be called')},
  lifecycleSnapshot(){throw new Error('must never be called')}
};
const runtime=library.create(mountRuntime);
equal(runtime.available,true,'runtime available');
equal(runtime.mode,'PASSIVE_EXPLICIT_OWNER_EVENTS_ONLY','runtime mode');
equal(runtime.dependencies.mount_lifecycle_runtime_available,true,'mount dependency attested');
equal(runtime.dependencies.mount_registry_owner,'mount_registry_owner','mount dependency owner');
equal(runtime.sideEffects.mount_lifecycle_events,0,'no lifecycle events');
equal(runtime.sideEffects.legacy_atlas_calls,0,'no atlas calls');
equal(runtime.sideEffects.mounts,0,'no mounts');
equal(runtime.sideEffects.repairs,0,'no repairs');
equal(runtime.sideEffects.route_assignments,0,'no routes');
equal(runtime.sideEffects.bank_mutations,0,'no bank mutations');
equal(runtime.sideEffects.storage_migrations,0,'no migration');
equal(runtime.sideEffects.persisted_user_data_writes,0,'no user-data writes');
equal(runtime.sideEffects.production_activations,0,'no activation');

function authority(owner,action){
  return {
    contract_version:library.capabilityContractVersion,
    authorizer:'app_orchestrator_owner',
    subject_id:owner,
    capability_id:'cap:p7u3:'+owner,
    decision:'AUTHORIZED',
    action
  };
}
function event(id,operation,sequence,type,owner,section,action,previous=null,extra={}){
  return Object.assign({
    event_version:library.eventVersion,
    event_id:id,
    operation_id:operation,
    monotonic_sequence:sequence,
    registry_epoch:1,
    event_type:type,
    owner_id:owner,
    section_id:section,
    source_version:'source:v1',
    observed_at:'2026-07-27T00:00:00Z',
    previous_event_digest:previous,
    authority:authority(owner,action)
  },extra);
}

const register=event(
  'evt:p7u4:register-bank','op:p7u4:register-bank',1,'OWNER_REGISTERED',
  'bank_screen_owner','bank','register_owner'
);
let outcome=runtime.applyOwnerEvent(register);
equal(outcome.code,'OWNER_REGISTERED','register accepted');
equal(outcome.accepted,true,'register accepted flag');
equal(outcome.mutated,true,'register mutates isolated registry');
equal(outcome.authority_granted,false,'register grants no authority');
equal(outcome.registry_owner,'mount_registry_owner','register registry owner');

const update=event(
  'evt:p7u4:update-bank','op:p7u4:update-bank',2,'OWNER_UPDATED',
  'bank_screen_owner','bank','update_owner',library.eventDigest(register),
  {source_version:'source:v2'}
);
outcome=runtime.applyOwnerEvent(update);
equal(outcome.code,'OWNER_UPDATED','update accepted');
equal(outcome.authority_granted,false,'update grants no authority');

const growthAuthority={
  contract_version:library.capabilityContractVersion,
  authorizer:'diagnostics_owner',
  subject_id:'diagnostics_owner',
  capability_id:'cap:p7u3:growth-observer',
  decision:'OBSERVED_ONLY_NO_AUTHORITY',
  action:'observe_owner_growth'
};
const growth=event(
  'evt:p7u4:growth','op:p7u4:growth',1,'OWNER_GROWTH_OBSERVED',
  'future_owner','future_section','observe_owner_growth',null,
  {authority:growthAuthority,source_version:'future:secret-source-v7'}
);
outcome=runtime.applyOwnerEvent(growth);
equal(outcome.code,'OWNER_GROWTH_RECORDED_NO_AUTHORITY','growth accepted passive');
equal(outcome.authority_granted,false,'growth no authority');

const snapshot=runtime.snapshot();
equal(snapshot.type,'PMP_SECTION_OWNER_MOUNT_REGISTRY_SNAPSHOT_V1','snapshot type');
equal(snapshot.registry_owner,'mount_registry_owner','snapshot owner');
equal(snapshot.registered.length,1,'one registered');
equal(snapshot.registered[0].owner_id,'bank_screen_owner','bank registered');
equal(snapshot.registered[0].section_id,'bank','bank section');
equal(snapshot.registered[0].status,'REGISTERED_CAPABILITY_BOUND','bank bound');
equal(snapshot.pending_growth.length,1,'one pending');
equal(snapshot.pending_growth[0].owner_id,'future_owner','future visible');
equal(snapshot.pending_growth[0].status,'OBSERVED_PENDING_NO_AUTHORITY','future pending');
equal(snapshot.pending_growth[0].authority_granted,false,'future no grant');
equal(snapshot.journal.length,3,'three journal events');
equal(snapshot.diagnostics.length,3,'three diagnostics events');
equal(
  snapshot.journal.map(row=>row.operation_id),
  snapshot.diagnostics.map(row=>row.operation_id),
  'shared operation identities'
);
equal(snapshot.counts.registered,1,'registered count');
equal(snapshot.counts.pending_growth,1,'pending count');
equal(snapshot.counts.accepted,3,'accepted count');
equal(snapshot.counts.rejected,0,'rejected count');
equal(snapshot.disclosure.capability_ids_exposed_to_diagnostics,false,'cap IDs hidden');
equal(snapshot.disclosure.raw_authority_payloads_exposed,false,'authority hidden');
for(const value of Object.values(snapshot.side_effects))equal(value,0,'snapshot effect zero');

const diagnostic=view.read(runtime);
equal(diagnostic.status,'READY_WITH_PENDING_GROWTH','diagnostic status');
equal(diagnostic.available,true,'diagnostic available');
equal(diagnostic.registry_owner,'mount_registry_owner','diagnostic owner');
equal(diagnostic.registered_count,1,'diagnostic registered');
equal(diagnostic.pending_growth_count,1,'diagnostic pending');
equal(diagnostic.visible_event_count,3,'diagnostic events');
equal(diagnostic.events.map(row=>row.operation_id),snapshot.diagnostics.map(row=>row.operation_id),'diagnostic operations');
equal(diagnostic.events.every(row=>row.authority_granted===false),true,'diagnostic no grants');
equal(diagnostic.events.every(row=>row.capability_present===true),true,'capability presence only');
equal(diagnostic.disclosure.capability_ids_exposed,false,'view cap IDs hidden');
equal(diagnostic.disclosure.raw_authority_payloads_exposed,false,'view authority hidden');
equal(diagnostic.disclosure.source_versions_exposed,false,'source versions hidden');
equal(diagnostic.disclosure.maximum_visible_events,128,'view event bound');
for(const value of Object.values(diagnostic.side_effects))equal(value,0,'view effect zero');
const diagnosticText=JSON.stringify(diagnostic);
check(!diagnosticText.includes('cap:p7u3:'),'no capability IDs disclosed');
check(!diagnosticText.includes('future:secret-source-v7'),'no source version disclosed');
check(!diagnosticText.includes('"authority"'),'no raw authority disclosed');

const missing=view.read(null);
equal(missing.status,'SECTION_OWNER_RUNTIME_UNAVAILABLE','missing runtime');
equal(missing.available,false,'missing unavailable');
const malformed=view.read({available:true,snapshot(){return {type:'wrong'}}});
equal(malformed.status,'SECTION_OWNER_SNAPSHOT_MALFORMED','malformed snapshot');
const throwing=view.read({available:true,snapshot(){throw new Error('bounded')}});
equal(throwing.status,'SECTION_OWNER_SNAPSHOT_ERROR','throwing snapshot');

function lastCode(events){
  const isolated=library.create(mountRuntime);
  let result;
  for(const item of events)result=isolated.applyOwnerEvent(item);
  return result.code;
}
let changed=JSON.parse(JSON.stringify(register));
changed.event_id='evt:p7u4:wrong-section';
changed.operation_id='op:p7u4:wrong-section';
changed.section_id='continuous_run';
equal(lastCode([changed]),'REJECTED_OWNER_SECTION_MISMATCH','cross section denied');

changed=JSON.parse(JSON.stringify(register));
changed.event_id='evt:p7u4:unknown';
changed.operation_id='op:p7u4:unknown';
changed.owner_id='invented_owner';
changed.section_id='invented';
changed.authority.subject_id='invented_owner';
equal(lastCode([changed]),'REJECTED_UNDECLARED_OWNER','unknown register denied');

changed=JSON.parse(JSON.stringify(register));
changed.event_id='evt:p7u4:forged';
changed.operation_id='op:p7u4:forged';
changed.authority.authorizer='bank_screen_owner';
equal(lastCode([changed]),'REJECTED_REGISTRATION_AUTHORITY','forged authority denied');

changed=JSON.parse(JSON.stringify(growth));
changed.event_id='evt:p7u4:growth-forged';
changed.operation_id='op:p7u4:growth-forged';
changed.authority.decision='AUTHORIZED';
equal(lastCode([changed]),'REJECTED_GROWTH_OBSERVER_AUTHORITY','forged growth denied');

changed=JSON.parse(JSON.stringify(register));
changed.event_version='V2';
equal(lastCode([changed]),'REJECTED_EVENT_VERSION','event version denied');

changed=JSON.parse(JSON.stringify(register));
changed.authority.contract_version='V0';
equal(lastCode([changed]),'REJECTED_CAPABILITY_CONTRACT_VERSION','contract denied');

changed=JSON.parse(JSON.stringify(register));
delete changed.registry_epoch;
equal(lastCode([changed]),'REJECTED_MALFORMED_EVENT','malformed denied');

const duplicateRuntime=library.create(mountRuntime);
equal(duplicateRuntime.applyOwnerEvent(register).code,'OWNER_REGISTERED','duplicate seed');
equal(duplicateRuntime.applyOwnerEvent(register).code,'DUPLICATE_EVENT_IGNORED','duplicate ignored');
equal(duplicateRuntime.snapshot().counts.duplicates,1,'duplicate counted');
changed=JSON.parse(JSON.stringify(register));
changed.operation_id='op:p7u4:register-conflict';
changed.source_version='source:changed';
equal(duplicateRuntime.applyOwnerEvent(changed).code,'REJECTED_DUPLICATE_EVENT_CONFLICT','duplicate conflict');

changed=JSON.parse(JSON.stringify(growth));
changed.event_id='evt:p7u4:duplicate-operation';
changed.operation_id=register.operation_id;
equal(duplicateRuntime.applyOwnerEvent(changed).code,'REJECTED_DUPLICATE_OPERATION','operation duplicate');

const stale=JSON.parse(JSON.stringify(update));
stale.event_id='evt:p7u4:stale';
stale.operation_id='op:p7u4:stale';
stale.monotonic_sequence=1;
equal(lastCode([register,stale]),'REJECTED_STALE_SEQUENCE','stale denied');

const gap=JSON.parse(JSON.stringify(update));
gap.event_id='evt:p7u4:gap';
gap.operation_id='op:p7u4:gap';
gap.monotonic_sequence=3;
equal(lastCode([register,gap]),'REJECTED_SEQUENCE_GAP','gap denied');

const badChain=JSON.parse(JSON.stringify(update));
badChain.event_id='evt:p7u4:chain';
badChain.operation_id='op:p7u4:chain';
badChain.previous_event_digest='0'.repeat(64);
equal(lastCode([register,badChain]),'REJECTED_EVENT_CHAIN','chain denied');

const earlyUpdate=JSON.parse(JSON.stringify(update));
earlyUpdate.monotonic_sequence=1;
earlyUpdate.previous_event_digest=null;
equal(lastCode([earlyUpdate]),'REJECTED_OWNER_NOT_REGISTERED','update missing denied');

for(const forbidden of [
  'localStorage','sessionStorage','indexedDB','document.','fetch(',
  'XMLHttpRequest','WebSocket','location.','.src=','setTimeout(','setInterval('
]){
  check(!runtimeSource.includes(forbidden),'runtime forbidden token '+forbidden);
  check(!viewSource.includes(forbidden),'view forbidden token '+forbidden);
}
for(const forbidden of ['applyOwnerEvent','registry.apply','mountRuntime.applyOwnerEvent']){
  check(!viewSource.includes(forbidden),'view mutation token '+forbidden);
}
check(diagnosticsSource.includes('function ownerView()'),'diagnostics reads view');
check(diagnosticsSource.includes('readSectionOwners=ownerView'),'diagnostics API read only');
check(diagnosticsSource.includes('renderSectionOwners'),'diagnostics owner card');
check(diagnosticsSource.includes('capability_ids_exposed:false'),'diagnostics fallback redacted');
check(!diagnosticsSource.includes('PMPSectionOwnerMountRuntimeV1.applyOwnerEvent'),'diagnostics cannot apply');
const mountPos=innerSource.indexOf('pmp-mount-lifecycle-runtime-v1.js?fresh=');
const ownerPos=innerSource.indexOf('pmp-section-owner-mount-integration-v1.js?fresh=');
const viewPos=innerSource.indexOf('pmp-section-owner-diagnostics-view-v1.js?fresh=');
const authorityPos=innerSource.indexOf('pmp-authority-rules-v1.js?fresh=');
check(mountPos>-1&&mountPos<ownerPos&&ownerPos<viewPos&&viewPos<authorityPos,'load order');
equal((innerSource.match(/pmp-section-owner-mount-integration-v1\.js\?fresh=/g)||[]).length,1,'one runtime tag');
equal((innerSource.match(/pmp-section-owner-diagnostics-view-v1\.js\?fresh=/g)||[]).length,1,'one view tag');

console.log(`PASS: P7-U4 bounded owner Mount Registry and Diagnostics integration (${assertions}/${assertions})`);
