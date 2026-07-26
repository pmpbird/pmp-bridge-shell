#!/usr/bin/env node
'use strict';
const assert=require('assert');
const fs=require('fs');
const path=require('path');
const ROOT=path.resolve(__dirname,'..');
const runtimePath=path.join(ROOT,'pmp-section-owner-mount-integration-v1.js');
const runtimeSource=fs.readFileSync(runtimePath,'utf8');
const library=require(runtimePath);
const view=require(path.join(ROOT,'pmp-section-owner-diagnostics-view-v1.js'));
let assertions=0;
function check(value,message){assertions++;assert(value,message)}
function equal(actual,expected,message){assertions++;assert.deepStrictEqual(actual,expected,message)}

const owners=Object.entries(library.owners);
const zeroEffects={
  mount_lifecycle_events:0,
  legacy_atlas_calls:0,
  mounts:0,
  repairs:0,
  route_assignments:0,
  bank_mutations:0,
  storage_migrations:0,
  persisted_user_data_writes:0,
  production_activations:0
};
let mountCalls=0;
const mountRuntime={
  available:true,
  registryOwner:'mount_registry_owner',
  applyOwnerEvent(){mountCalls++;throw new Error('owner proof must not call Mount Lifecycle')},
  lifecycleSnapshot(){mountCalls++;throw new Error('owner proof must not read Mount Lifecycle')},
  apply(){mountCalls++;throw new Error('owner proof must not apply Mount Lifecycle')}
};
function authority(owner,action,capabilityOwner=owner){
  return {
    contract_version:library.capabilityContractVersion,
    authorizer:'app_orchestrator_owner',
    subject_id:owner,
    capability_id:'cap:p7u3:'+capabilityOwner,
    decision:'AUTHORIZED',
    action
  };
}
function growthAuthority(){
  return {
    contract_version:library.capabilityContractVersion,
    authorizer:'diagnostics_owner',
    subject_id:'diagnostics_owner',
    capability_id:'cap:p7u3:growth-observer',
    decision:'OBSERVED_ONLY_NO_AUTHORITY',
    action:'observe_owner_growth'
  };
}
function makeEvent({
  id,operation,sequence=1,epoch=1,type='OWNER_REGISTERED',
  owner='diagnostics_owner',section='diagnostics',action='register_owner',
  previous=null,time='2026-07-26T17:05:00Z',source='source:v1',
  eventAuthority=null
}){
  return {
    event_version:library.eventVersion,
    event_id:id,
    operation_id:operation,
    monotonic_sequence:sequence,
    registry_epoch:epoch,
    event_type:type,
    owner_id:owner,
    section_id:section,
    source_version:source,
    observed_at:time,
    previous_event_digest:previous,
    authority:eventAuthority||authority(owner,action)
  };
}
function clone(value){return JSON.parse(JSON.stringify(value))}
function isolatedCode(event){
  return library.create(mountRuntime).applyOwnerEvent(event).code;
}

equal(library.type,'PMP_SECTION_OWNER_MOUNT_INTEGRATION_V1','runtime type');
equal(library.version,'1.0.0','compatible runtime contract version');
equal(library.registryOwner,'mount_registry_owner','registry owner');
equal(typeof library.restore,'function','atomic restart API');
equal(owners.length,8,'eight declared owners');
equal(new Set(owners.map(row=>row[1])).size,8,'eight isolated sections');

const allRuntime=library.create(mountRuntime);
const allEvents=[];
owners.forEach(([owner,section],index)=>{
  const item=makeEvent({
    id:`evt:p7u5:all:${index}`,
    operation:`op:p7u5:all:${index}`,
    owner,section
  });
  allEvents.push(item);
  const outcome=allRuntime.applyOwnerEvent(item);
  equal(outcome.code,'OWNER_REGISTERED',`${owner} registers`);
  equal(outcome.accepted,true,`${owner} accepted`);
  equal(outcome.mutated,true,`${owner} mutates isolated registry`);
  equal(outcome.authority_granted,false,`${owner} event grants no authority`);
  equal(outcome.operation_id,item.operation_id,`${owner} operation retained`);
});
const allSnapshot=allRuntime.snapshot();
equal(allSnapshot.registered.length,8,'all owners registered');
equal(allSnapshot.counts.registered,8,'registered count eight');
equal(allSnapshot.counts.accepted,8,'accepted count eight');
equal(allSnapshot.counts.rejected,0,'no positive rejection');
equal(allSnapshot.journal.length,8,'eight journal rows');
equal(allSnapshot.diagnostics.length,8,'eight diagnostic rows');
equal(
  allSnapshot.journal.map(row=>row.operation_id),
  allSnapshot.diagnostics.map(row=>row.operation_id),
  'journal and Diagnostics share operations'
);
equal(
  allSnapshot.registered.map(row=>[row.owner_id,row.section_id]),
  owners.slice().sort((a,b)=>a[0].localeCompare(b[0])),
  'exact owner-section isolation'
);
equal(allSnapshot.side_effects,zeroEffects,'all-owner side effects zero');
equal(mountCalls,0,'Mount Lifecycle untouched');

owners.forEach(([owner,section],index)=>{
  const wrongSection=owners[(index+1)%owners.length][1];
  const crossSection=makeEvent({
    id:`evt:p7u5:cross-section:${index}`,
    operation:`op:p7u5:cross-section:${index}`,
    owner,section:wrongSection
  });
  equal(
    isolatedCode(crossSection),
    'REJECTED_OWNER_SECTION_MISMATCH',
    `${owner} cannot cross section`
  );
  const crossCapability=makeEvent({
    id:`evt:p7u5:cross-capability:${index}`,
    operation:`op:p7u5:cross-capability:${index}`,
    owner,section,
    eventAuthority:authority(owner,'register_owner',owners[(index+1)%owners.length][0])
  });
  equal(
    isolatedCode(crossCapability),
    'REJECTED_REGISTRATION_AUTHORITY',
    `${owner} cannot borrow another owner capability`
  );
});
check(
  runtimeSource.includes("authority.capability_id!==ownerCapability(event.owner_id)"),
  'runtime enforces exact owner capability'
);
check(
  !runtimeSource.includes("authority.capability_id.indexOf('cap:p7u3:')!==0"),
  'prefix-only capability check removed'
);

const bankRegister=makeEvent({
  id:'evt:p7u5:bank:register',
  operation:'op:p7u5:bank:register',
  owner:'bank_screen_owner',
  section:'bank'
});
const duplicateRuntime=library.create(mountRuntime);
equal(duplicateRuntime.applyOwnerEvent(bankRegister).code,'OWNER_REGISTERED','duplicate seed');
equal(
  duplicateRuntime.applyOwnerEvent(bankRegister).code,
  'DUPLICATE_EVENT_IGNORED',
  'exact duplicate ignored'
);
let changed=clone(bankRegister);
changed.operation_id='op:p7u5:bank:event-conflict';
changed.source_version='source:conflict';
equal(
  duplicateRuntime.applyOwnerEvent(changed).code,
  'REJECTED_DUPLICATE_EVENT_CONFLICT',
  'conflicting duplicate rejected'
);
const duplicateOwner=makeEvent({
  id:'evt:p7u5:bank:duplicate-owner',
  operation:'op:p7u5:bank:duplicate-owner',
  sequence:2,
  owner:'bank_screen_owner',
  section:'bank',
  previous:library.eventDigest(bankRegister)
});
equal(
  duplicateRuntime.applyOwnerEvent(duplicateOwner).code,
  'REJECTED_DUPLICATE_OWNER',
  'duplicate owner rejected'
);
let duplicateSnapshot=duplicateRuntime.snapshot();
equal(duplicateSnapshot.counts.registered,1,'duplicate owner does not add row');
equal(duplicateSnapshot.counts.accepted,1,'duplicate paths do not append journal');
equal(duplicateSnapshot.counts.rejected,2,'conflict and duplicate owner counted');
equal(duplicateSnapshot.counts.duplicates,1,'exact duplicate counted separately');
equal(duplicateSnapshot.journal.length,1,'duplicate leaves one journal row');
equal(duplicateSnapshot.diagnostics.length,1,'duplicate leaves one diagnostic row');
equal(duplicateSnapshot.side_effects,zeroEffects,'duplicate side effects zero');

const bankUpdate=makeEvent({
  id:'evt:p7u5:bank:update',
  operation:'op:p7u5:bank:update',
  sequence:2,
  type:'OWNER_UPDATED',
  owner:'bank_screen_owner',
  section:'bank',
  action:'update_owner',
  previous:library.eventDigest(bankRegister),
  source:'source:v2'
});
equal(
  duplicateRuntime.applyOwnerEvent(bankUpdate).code,
  'OWNER_UPDATED',
  'rejected duplicate does not poison valid sequence'
);
const bankRemove=makeEvent({
  id:'evt:p7u5:bank:remove',
  operation:'op:p7u5:bank:remove',
  sequence:3,
  type:'OWNER_REMOVED',
  owner:'bank_screen_owner',
  section:'bank',
  action:'remove_owner',
  previous:library.eventDigest(bankUpdate),
  source:'source:v2'
});
equal(duplicateRuntime.applyOwnerEvent(bankRemove).code,'OWNER_REMOVED','owner removed');
const updateRemoved=makeEvent({
  id:'evt:p7u5:bank:update-removed',
  operation:'op:p7u5:bank:update-removed',
  sequence:4,
  type:'OWNER_UPDATED',
  owner:'bank_screen_owner',
  section:'bank',
  action:'update_owner',
  previous:library.eventDigest(bankRemove),
  source:'source:v3'
});
equal(
  duplicateRuntime.applyOwnerEvent(updateRemoved).code,
  'REJECTED_OWNER_NOT_REGISTERED',
  'removed owner cannot update'
);
const bankReregister=makeEvent({
  id:'evt:p7u5:bank:reregister',
  operation:'op:p7u5:bank:reregister',
  sequence:4,
  type:'OWNER_REGISTERED',
  owner:'bank_screen_owner',
  section:'bank',
  action:'register_owner',
  previous:library.eventDigest(bankRemove),
  source:'source:v3'
});
equal(
  duplicateRuntime.applyOwnerEvent(bankReregister).code,
  'OWNER_REGISTERED',
  'denied removed-owner update does not poison re-registration'
);
duplicateSnapshot=duplicateRuntime.snapshot();
equal(duplicateSnapshot.registered.length,1,'bank re-registered once');
equal(duplicateSnapshot.registered[0].source_version,'source:v3','bank source current');
equal(duplicateSnapshot.journal.length,4,'only valid lifecycle journaled');
equal(duplicateSnapshot.diagnostics.length,4,'only valid lifecycle diagnosed');
equal(duplicateSnapshot.side_effects.bank_mutations,0,'owner events never mutate Bank');

const staleRuntime=library.create(mountRuntime);
const initial=makeEvent({
  id:'evt:p7u5:stale:register',
  operation:'op:p7u5:stale:register',
  epoch:2,
  owner:'continuous_run_level_owner',
  section:'continuous_run'
});
equal(staleRuntime.applyOwnerEvent(initial).code,'OWNER_REGISTERED','stale seed');
function updateEvent(id,sequence,epoch,previous,time='2026-07-26T17:06:00Z'){
  return makeEvent({
    id:`evt:p7u5:stale:${id}`,
    operation:`op:p7u5:stale:${id}`,
    sequence,epoch,type:'OWNER_UPDATED',
    owner:'continuous_run_level_owner',
    section:'continuous_run',
    action:'update_owner',
    previous,time,
    source:`source:${id}`
  });
}
equal(
  staleRuntime.applyOwnerEvent(updateEvent('epoch',2,1,library.eventDigest(initial))).code,
  'REJECTED_STALE_EPOCH',
  'stale epoch rejected'
);
equal(
  staleRuntime.applyOwnerEvent(updateEvent('sequence',1,2,library.eventDigest(initial))).code,
  'REJECTED_STALE_SEQUENCE',
  'stale sequence rejected'
);
equal(
  staleRuntime.applyOwnerEvent(updateEvent('gap',3,2,library.eventDigest(initial))).code,
  'REJECTED_SEQUENCE_GAP',
  'sequence gap rejected'
);
equal(
  staleRuntime.applyOwnerEvent(updateEvent('epoch-gap',2,4,library.eventDigest(initial))).code,
  'REJECTED_EPOCH_GAP',
  'epoch gap rejected'
);
equal(
  staleRuntime.applyOwnerEvent(updateEvent('chain',2,2,'0'.repeat(64))).code,
  'REJECTED_EVENT_CHAIN',
  'wrong chain rejected'
);
equal(
  staleRuntime.applyOwnerEvent(
    updateEvent('time',2,2,library.eventDigest(initial),'2026-07-26T17:04:59Z')
  ).code,
  'REJECTED_TIME_REGRESSION',
  'time regression rejected'
);
const current=updateEvent('current',2,3,library.eventDigest(initial));
equal(staleRuntime.applyOwnerEvent(current).code,'OWNER_UPDATED','valid epoch advance accepted');
const afterDenials=staleRuntime.snapshot();
equal(afterDenials.counts.accepted,2,'only valid stale scenario events accepted');
equal(afterDenials.counts.rejected,6,'six stale/conflict paths rejected');
equal(afterDenials.journal.length,2,'denials do not append journal');
equal(afterDenials.registered[0].registry_epoch,3,'current epoch retained');
equal(afterDenials.registered[0].source_version,'source:current','current source retained');
equal(afterDenials.side_effects,zeroEffects,'stale denial effects zero');

const growthRuntime=library.create(mountRuntime);
const growth1=makeEvent({
  id:'evt:p7u5:growth:1',
  operation:'op:p7u5:growth:1',
  type:'OWNER_GROWTH_OBSERVED',
  owner:'future_owner',
  section:'future_section',
  action:'observe_owner_growth',
  source:'future:private:v1',
  eventAuthority:growthAuthority()
});
equal(
  growthRuntime.applyOwnerEvent(growth1).code,
  'OWNER_GROWTH_RECORDED_NO_AUTHORITY',
  'growth recorded pending'
);
const growth2=makeEvent({
  id:'evt:p7u5:growth:2',
  operation:'op:p7u5:growth:2',
  sequence:2,
  type:'OWNER_GROWTH_OBSERVED',
  owner:'future_owner',
  section:'future_section',
  action:'observe_owner_growth',
  previous:library.eventDigest(growth1),
  source:'future:private:v2',
  eventAuthority:growthAuthority()
});
equal(
  growthRuntime.applyOwnerEvent(growth2).code,
  'OWNER_GROWTH_RECORDED_NO_AUTHORITY',
  'growth update remains pending'
);
equal(
  growthRuntime.applyOwnerEvent(growth2).code,
  'DUPLICATE_EVENT_IGNORED',
  'growth duplicate ignored'
);
const growthSnapshot=growthRuntime.snapshot();
equal(growthSnapshot.pending_growth.length,1,'one pending owner');
equal(growthSnapshot.pending_growth[0].status,'OBSERVED_PENDING_NO_AUTHORITY','pending status');
equal(growthSnapshot.pending_growth[0].authority_granted,false,'pending grants nothing');
equal(growthSnapshot.registered.length,0,'growth never registers owner');
equal(growthSnapshot.counts.accepted,2,'two growth observations accepted');
equal(growthSnapshot.counts.duplicates,1,'growth duplicate counted');
equal(growthSnapshot.side_effects,zeroEffects,'growth effects zero');
const growthDiagnostic=view.read(growthRuntime);
equal(growthDiagnostic.status,'READY_WITH_PENDING_GROWTH','growth visible to Diagnostics');
equal(growthDiagnostic.pending_growth_count,1,'Diagnostics pending count');
equal(growthDiagnostic.registered_count,0,'Diagnostics no registration');
equal(growthDiagnostic.events.length,2,'Diagnostics sees accepted growth only');
equal(
  growthDiagnostic.events.map(row=>row.operation_id),
  growthSnapshot.journal.map(row=>row.operation_id),
  'growth operations shared'
);
equal(
  growthDiagnostic.events.every(row=>row.authority_granted===false),
  true,
  'Diagnostics growth grants no authority'
);
const growthText=JSON.stringify(growthDiagnostic);
check(!growthText.includes('cap:p7u3:growth-observer'),'growth capability redacted');
check(!growthText.includes('future:private:'),'growth source redacted');
check(!growthText.includes('"authority"'),'growth raw authority redacted');

const restored=library.restore(mountRuntime,allSnapshot.journal);
equal(restored.restored,true,'restart replay accepted');
equal(restored.code,'RESTART_REPLAY_ACCEPTED','restart code');
equal(restored.mutated,true,'restart rebuilt isolated state');
equal(restored.authority_granted,false,'restart grants no authority');
equal(restored.rejected_index,null,'restart no rejected index');
equal(restored.rejected_code,null,'restart no rejected code');
equal(
  restored.operation_ids,
  allSnapshot.journal.map(row=>row.operation_id),
  'restart preserves operation identities'
);
const restoredSnapshot=restored.runtime.snapshot();
equal(restoredSnapshot.registered,allSnapshot.registered,'restart registered state identical');
equal(restoredSnapshot.journal,allSnapshot.journal,'restart journal identical');
equal(restoredSnapshot.diagnostics,allSnapshot.diagnostics,'restart Diagnostics identical');
equal(restoredSnapshot.side_effects,zeroEffects,'restart runtime effects zero');
equal(restored.side_effects,zeroEffects,'restart result effects zero');
equal(mountCalls,0,'restart never calls Mount Lifecycle');

const malformedRestart=library.restore(mountRuntime,{journal:allSnapshot.journal});
equal(malformedRestart.restored,false,'malformed restart rejected');
equal(malformedRestart.code,'RESTART_REJECTED_MALFORMED_JOURNAL','malformed restart code');
equal(malformedRestart.runtime.snapshot().journal.length,0,'malformed restart exposes empty state');
equal(malformedRestart.operation_ids,[],'malformed restart exposes no operations');
equal(malformedRestart.side_effects,zeroEffects,'malformed restart effects zero');

const corruptJournal=clone(allSnapshot.journal);
corruptJournal[3].previous_event_digest='0'.repeat(64);
const corruptDigestInput=clone(corruptJournal[3]);
delete corruptDigestInput.event_digest;
corruptJournal[3].event_digest=library.eventDigest(corruptDigestInput);
const corruptRestart=library.restore(mountRuntime,corruptJournal);
equal(corruptRestart.restored,false,'corrupt restart rejected');
equal(corruptRestart.code,'RESTART_REJECTED_JOURNAL_EVENT','corrupt restart code');
equal(corruptRestart.rejected_index,3,'corrupt restart exact index');
equal(corruptRestart.rejected_code,'REJECTED_SEQUENCE_START','corrupt restart reason');
equal(corruptRestart.runtime.snapshot().registered.length,0,'corrupt restart no partial owners');
equal(corruptRestart.runtime.snapshot().journal.length,0,'corrupt restart no partial journal');
equal(corruptRestart.operation_ids,[],'corrupt restart no partial operations');
equal(corruptRestart.side_effects,zeroEffects,'corrupt restart effects zero');

const duplicateJournal=allSnapshot.journal.concat(clone(allSnapshot.journal[0]));
const duplicateRestart=library.restore(mountRuntime,duplicateJournal);
equal(duplicateRestart.restored,false,'duplicate restart rejected');
equal(duplicateRestart.rejected_index,8,'duplicate restart exact index');
equal(duplicateRestart.rejected_code,'DUPLICATE_EVENT_IGNORED','duplicate restart reason');
equal(duplicateRestart.runtime.snapshot().counts.accepted,0,'duplicate restart atomic empty');

const emptyRestart=library.restore(mountRuntime,[]);
equal(emptyRestart.restored,true,'empty restart valid');
equal(emptyRestart.mutated,false,'empty restart no mutation');
equal(emptyRestart.operation_ids,[],'empty restart no operations');
equal(emptyRestart.runtime.snapshot().counts.accepted,0,'empty restart empty runtime');

const inputClone=makeEvent({
  id:'evt:p7u5:clone',
  operation:'op:p7u5:clone',
  owner:'diagnostics_owner',
  section:'diagnostics'
});
const cloneRuntime=library.create(mountRuntime);
equal(cloneRuntime.applyOwnerEvent(inputClone).code,'OWNER_REGISTERED','clone seed accepted');
inputClone.owner_id='tampered_after_accept';
inputClone.authority.capability_id='tampered_after_accept';
let clonedSnapshot=cloneRuntime.snapshot();
equal(clonedSnapshot.registered[0].owner_id,'diagnostics_owner','input cloned before storage');
clonedSnapshot.registered[0].owner_id='tampered_snapshot';
clonedSnapshot.journal.length=0;
clonedSnapshot=cloneRuntime.snapshot();
equal(clonedSnapshot.registered[0].owner_id,'diagnostics_owner','snapshot mutation isolated');
equal(clonedSnapshot.journal.length,1,'snapshot journal mutation isolated');

const denialRuntime=library.create(mountRuntime);
const denialSeed=makeEvent({
  id:'evt:p7u5:deny:seed',
  operation:'op:p7u5:deny:seed',
  owner:'resident_30b_owner',
  section:'resident_30b'
});
equal(denialRuntime.applyOwnerEvent(denialSeed).code,'OWNER_REGISTERED','denial seed');
const denialCases=[];
changed=makeEvent({
  id:'evt:p7u5:deny:cross-cap',
  operation:'op:p7u5:deny:cross-cap',
  sequence:2,
  type:'OWNER_UPDATED',
  owner:'resident_30b_owner',
  section:'resident_30b',
  action:'update_owner',
  previous:library.eventDigest(denialSeed),
  eventAuthority:authority('resident_30b_owner','update_owner','bank_screen_owner')
});
denialCases.push([changed,'REJECTED_REGISTRATION_AUTHORITY']);
changed=clone(denialSeed);
changed.event_id='evt:p7u5:deny:operation';
denialCases.push([changed,'REJECTED_DUPLICATE_OPERATION']);
changed=clone(denialSeed);
changed.event_id='evt:p7u5:deny:unknown';
changed.operation_id='op:p7u5:deny:unknown';
changed.owner_id='unknown_owner';
changed.section_id='unknown_section';
changed.authority.subject_id='unknown_owner';
changed.authority.capability_id='cap:p7u3:unknown_owner';
denialCases.push([changed,'REJECTED_UNDECLARED_OWNER']);
changed=clone(denialSeed);
changed.event_id='evt:p7u5:deny:action';
changed.operation_id='op:p7u5:deny:action';
changed.authority.action='bank_mutation';
denialCases.push([changed,'REJECTED_REGISTRATION_AUTHORITY']);
for(const [item,code] of denialCases){
  const before=denialRuntime.snapshot();
  const outcome=denialRuntime.applyOwnerEvent(item);
  const after=denialRuntime.snapshot();
  equal(outcome.code,code,`denial ${code}`);
  equal(outcome.accepted,false,`${code} not accepted`);
  equal(outcome.mutated,false,`${code} no registry mutation`);
  equal(outcome.authority_granted,false,`${code} no authority`);
  equal(after.registered,before.registered,`${code} registered unchanged`);
  equal(after.pending_growth,before.pending_growth,`${code} growth unchanged`);
  equal(after.journal,before.journal,`${code} journal unchanged`);
  equal(after.diagnostics,before.diagnostics,`${code} Diagnostics unchanged`);
  equal(after.side_effects,zeroEffects,`${code} external effects zero`);
}

for(const forbidden of [
  'localStorage','sessionStorage','indexedDB','document.','fetch(',
  'XMLHttpRequest','WebSocket','location.','.src=','setTimeout(','setInterval('
]){
  check(!runtimeSource.includes(forbidden),`runtime forbidden token ${forbidden}`);
}
equal(mountCalls,0,'all proof paths leave Mount Lifecycle untouched');
equal(allRuntime.sideEffects,zeroEffects,'public side-effects declaration zero');
equal(Object.isFrozen(restored),true,'restart result frozen');
equal(Object.isFrozen(restored.operation_ids),true,'restart operations frozen');
equal(Object.isFrozen(restored.runtime),true,'restored runtime frozen');

console.log(`PASS: P7-U5 owner isolation, restart, growth, and denial proof (${assertions}/${assertions})`);
