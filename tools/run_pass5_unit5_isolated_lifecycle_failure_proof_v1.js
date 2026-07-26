#!/usr/bin/env node
'use strict';
const assert=require('assert');
const crypto=require('crypto');
const fs=require('fs');
const path=require('path');

const ROOT=path.resolve(__dirname,'..');
const OUTPUT=process.argv[2];
if(!OUTPUT)throw new Error('usage: run_pass5_unit5_isolated_lifecycle_failure_proof_v1.js OUTPUT_JSON');

const contract=require(path.join(ROOT,'pmp-mount-lifecycle-contract-v1.js'));
const runtimeLibrary=require(path.join(ROOT,'pmp-mount-lifecycle-runtime-v1.js'));
const diagnosticsView=require(path.join(ROOT,'pmp-mount-lifecycle-diagnostics-view-v1.js'));
const sourceFiles=[
  'pmp-mount-lifecycle-contract-v1.js',
  'pmp-mount-lifecycle-runtime-v1.js',
  'pmp-mount-lifecycle-diagnostics-view-v1.js',
  'pmp-diagnostics-owner-v1.js'
];
const sources=Object.fromEntries(sourceFiles.map(file=>[
  file,
  fs.readFileSync(path.join(ROOT,file),'utf8')
]));
const sourceHashes=Object.fromEntries(sourceFiles.map(file=>[
  file,
  crypto.createHash('sha256').update(sources[file]).digest('hex')
]));

const POLICY={
  routeAuthority:'current_map_owner',
  allowedMountOwners:['app_orchestrator_owner','bank_screen_owner'],
  allowedSources:['current_map_owner','app_orchestrator_owner','bank_screen_owner'],
  maxOperations:8,
  maxEventsPerOperation:12
};
const assertions=[];
function check(category,name,condition,evidence){
  assertions.push({category,name,pass:!!condition,evidence:evidence===undefined?null:evidence});
  assert(condition,`${category}: ${name}`);
}
function equal(category,name,actual,expected){
  let pass=true;
  try{assert.deepStrictEqual(actual,expected)}catch(_){pass=false}
  check(category,name,pass,{actual,expected});
}
function operation(scope,id){
  return `pmp-mount:${scope}:${id}`;
}
function event(op,sequence,state,owner,details,overrides){
  return Object.assign({
    contract_version:contract.contractVersion,
    operation_id:op,
    monotonic_sequence:sequence,
    owner,
    source:owner,
    state,
    reason_code:state+'_P5_U5',
    observed_at:`2026-07-26T08:30:${String(sequence).padStart(2,'0')}Z`,
    trust:'OWNER_ATTESTED'
  },details===undefined?{}:{details},overrides||{});
}
function route(op,sequence,state,details,overrides){
  return event(op,sequence,state,'current_map_owner',details,overrides);
}
function mount(op,sequence,state,owner,details,overrides){
  return event(op,sequence,state,owner,details,overrides);
}
function accepted(registry,category,name,item,code='ACCEPTED'){
  const result=registry.apply(item);
  equal(category,name,result.code,code);
  return result;
}
function happyEvents(op,owner='app_orchestrator_owner'){
  return [
    route(op,1,'ROUTE_REQUESTED',{route:'current_app'}),
    route(op,2,'OWNER_RESOLVED',{resolved_owner:owner}),
    mount(op,3,'MOUNT_STARTED',owner,{mount_point:'current_app'}),
    mount(op,4,'MOUNTED',owner,{mount_point:'current_app'}),
    mount(op,5,'READY',owner,{acknowledged:true})
  ];
}

check('identity','contract version',contract.contractVersion==='PMP_MOUNT_LIFECYCLE_CONTRACT_V1');
check('identity','registry owner',contract.registryOwner==='mount_registry_owner');
check('identity','runtime type',runtimeLibrary.runtimeType==='PMP_MOUNT_LIFECYCLE_RUNTIME_V1');
check('identity','Diagnostics view type',diagnosticsView.type==='PMP_MOUNT_LIFECYCLE_DIAGNOSTICS_VIEW_V1');
check('identity','four source hashes sealed in report',Object.keys(sourceHashes).length===4,sourceHashes);

const happyOp=operation('current-app','proof-happy-001');
const happy=contract.createRegistry(POLICY);
happyEvents(happyOp).forEach((item,index)=>accepted(happy,'happy_path',`accept step ${index+1}`,item));
equal('happy_path','final state',happy.operation(happyOp).state,'READY');
equal('happy_path','event count',happy.operation(happyOp).events.length,5);
accepted(happy,'happy_path','exact duplicate ignored',happyEvents(happyOp)[4],'DUPLICATE_IGNORED');
equal('happy_path','duplicate does not append',happy.operation(happyOp).events.length,5);

const slowOp=operation('current-app','proof-slow-002');
const slow=contract.createRegistry(POLICY);
[
  route(slowOp,1,'ROUTE_REQUESTED',{route:'current_app'}),
  route(slowOp,2,'OWNER_RESOLVED',{resolved_owner:'app_orchestrator_owner'}),
  mount(slowOp,3,'MOUNT_STARTED','app_orchestrator_owner'),
  mount(slowOp,4,'SLOW','app_orchestrator_owner',{elapsed_ms:9001}),
  mount(slowOp,5,'DEGRADED','app_orchestrator_owner',{reason:'bounded'}),
  mount(slowOp,6,'MOUNTED','app_orchestrator_owner'),
  mount(slowOp,7,'READY','app_orchestrator_owner')
].forEach((item,index)=>accepted(slow,'slow_degraded_recovery',`accept step ${index+1}`,item));
equal('slow_degraded_recovery','recovered final state',slow.operation(slowOp).state,'READY');

const blockedOp=operation('current-app','proof-blocked-003');
const blocked=contract.createRegistry(POLICY);
accepted(blocked,'terminal_paths','blocked route start',route(blockedOp,1,'ROUTE_REQUESTED'));
accepted(blocked,'terminal_paths','route authority blocks',route(blockedOp,2,'BLOCKED',{reason:'owner_unavailable'}));
equal('terminal_paths','blocked terminal state',blocked.operation(blockedOp).state,'BLOCKED');
equal(
  'terminal_paths',
  'blocked rejects later transition',
  blocked.apply(route(blockedOp,3,'FAILED')).code,
  'REJECTED_INVALID_TRANSITION'
);

const failedOp=operation('bank','proof-failed-004');
const failed=contract.createRegistry(POLICY);
accepted(failed,'terminal_paths','failed route start',route(failedOp,1,'ROUTE_REQUESTED'));
accepted(failed,'terminal_paths','failed owner resolve',route(failedOp,2,'OWNER_RESOLVED',{resolved_owner:'bank_screen_owner'}));
accepted(failed,'terminal_paths','failed mount start',mount(failedOp,3,'MOUNT_STARTED','bank_screen_owner'));
accepted(failed,'terminal_paths','owner reports failed',mount(failedOp,4,'FAILED','bank_screen_owner',{reason:'fixture_failure'}));
equal('terminal_paths','failed terminal state',failed.operation(failedOp).state,'FAILED');

const invalidOp=operation('current-app','proof-invalid-005');
function fresh(){return contract.createRegistry(POLICY)}
equal('schema_failures','null input',fresh().apply(null).code,'REJECTED_UNAVAILABLE');
equal('schema_failures','empty input',fresh().apply({}).code,'REJECTED_MALFORMED');
equal('schema_failures','contract mismatch',fresh().apply(Object.assign({},route(invalidOp,1,'ROUTE_REQUESTED'),{contract_version:'wrong'})).code,'REJECTED_CONTRACT_VERSION');
equal('schema_failures','operation id malformed',fresh().apply(Object.assign({},route(invalidOp,1,'ROUTE_REQUESTED'),{operation_id:'bad'})).code,'REJECTED_OPERATION_ID');
equal('schema_failures','sequence malformed',fresh().apply(Object.assign({},route(invalidOp,1,'ROUTE_REQUESTED'),{monotonic_sequence:0})).code,'REJECTED_SEQUENCE');
equal('schema_failures','state malformed',fresh().apply(Object.assign({},route(invalidOp,1,'ROUTE_REQUESTED'),{state:'UNKNOWN'})).code,'REJECTED_STATE');
equal('schema_failures','reason malformed',fresh().apply(Object.assign({},route(invalidOp,1,'ROUTE_REQUESTED'),{reason_code:'bad reason'})).code,'REJECTED_REASON_CODE');
equal('schema_failures','time malformed',fresh().apply(Object.assign({},route(invalidOp,1,'ROUTE_REQUESTED'),{observed_at:'not-time'})).code,'REJECTED_TIME');
equal('schema_failures','trust malformed',fresh().apply(Object.assign({},route(invalidOp,1,'ROUTE_REQUESTED'),{trust:'UNKNOWN'})).code,'REJECTED_TRUST');
equal('schema_failures','extra field rejected',fresh().apply(Object.assign({},route(invalidOp,1,'ROUTE_REQUESTED'),{extra:'forbidden'})).code,'REJECTED_MALFORMED');
equal('schema_failures','dangerous details rejected',fresh().apply(route(invalidOp,1,'ROUTE_REQUESTED',{constructor:'forbidden'})).code,'REJECTED_DETAILS');

const authority=contract.createRegistry(POLICY);
equal(
  'authority_failures',
  'wrong route owner',
  authority.apply(event(invalidOp,1,'ROUTE_REQUESTED','bank_screen_owner')).code,
  'REJECTED_ROUTE_AUTHORITY'
);
equal(
  'authority_failures',
  'source outside allowlist',
  authority.apply(route(invalidOp,1,'ROUTE_REQUESTED',undefined,{source:'intruder_owner'})).code,
  'REJECTED_SOURCE_AUTHORITY'
);
accepted(authority,'authority_failures','valid route start',route(invalidOp,1,'ROUTE_REQUESTED'));
equal(
  'authority_failures',
  'unknown resolved owner',
  authority.apply(route(invalidOp,2,'OWNER_RESOLVED',{resolved_owner:'unknown_owner'})).code,
  'REJECTED_RESOLVED_OWNER'
);
accepted(authority,'authority_failures','valid owner resolve',route(invalidOp,2,'OWNER_RESOLVED',{resolved_owner:'app_orchestrator_owner'}));
equal(
  'authority_failures',
  'wrong mount owner',
  authority.apply(mount(invalidOp,3,'MOUNT_STARTED','bank_screen_owner')).code,
  'REJECTED_MOUNT_OWNER'
);
equal(
  'authority_failures',
  'observer trust rejected',
  authority.apply(mount(invalidOp,3,'MOUNT_STARTED','app_orchestrator_owner',undefined,{trust:'OBSERVER_REPORTED'})).code,
  'REJECTED_NON_AUTHORITATIVE_TRUST'
);
equal(
  'authority_failures',
  'inferred trust rejected',
  authority.apply(mount(invalidOp,3,'MOUNT_STARTED','app_orchestrator_owner',undefined,{trust:'INFERRED'})).code,
  'REJECTED_NON_AUTHORITATIVE_TRUST'
);

const ordering=contract.createRegistry(POLICY);
const orderingEvents=happyEvents(operation('current-app','proof-order-006'));
accepted(ordering,'ordering_failures','ordering start',orderingEvents[0]);
equal('ordering_failures','sequence gap',ordering.apply(orderingEvents[2]).code,'REJECTED_SEQUENCE_GAP');
accepted(ordering,'ordering_failures','ordering resolve',orderingEvents[1]);
equal(
  'ordering_failures',
  'conflicting duplicate',
  ordering.apply(Object.assign({},orderingEvents[1],{reason_code:'CONFLICT'})).code,
  'REJECTED_DUPLICATE_CONFLICT'
);
accepted(ordering,'ordering_failures','ordering mount start',orderingEvents[2]);
equal('ordering_failures','stale sequence',ordering.apply(orderingEvents[1]).code,'REJECTED_STALE_SEQUENCE');
equal(
  'ordering_failures',
  'time regression',
  ordering.apply(Object.assign({},orderingEvents[3],{observed_at:'2026-07-26T08:30:02Z'})).code,
  'REJECTED_TIME_REGRESSION'
);
equal(
  'ordering_failures',
  'invalid transition',
  ordering.apply(Object.assign({},orderingEvents[3],{state:'READY'})).code,
  'REJECTED_INVALID_TRANSITION'
);
equal(
  'ordering_failures',
  'unknown operation cannot start later state',
  fresh().apply(mount(operation('bank','proof-missing-007'),1,'MOUNT_STARTED','bank_screen_owner')).code,
  'REJECTED_MISSING_OPERATION'
);

const capacity=contract.createRegistry(Object.assign({},POLICY,{maxOperations:1,maxEventsPerOperation:2}));
const capOp=operation('current-app','proof-capacity-008');
accepted(capacity,'retention','capacity first event',route(capOp,1,'ROUTE_REQUESTED'));
accepted(capacity,'retention','capacity second event',route(capOp,2,'OWNER_RESOLVED',{resolved_owner:'app_orchestrator_owner'}));
equal(
  'retention',
  'event capacity rejects without deletion',
  capacity.apply(mount(capOp,3,'MOUNT_STARTED','app_orchestrator_owner')).code,
  'REJECTED_EVENT_RETENTION_CAPACITY'
);
equal(
  'retention',
  'operation capacity rejects without deletion',
  capacity.apply(route(operation('other','proof-capacity-009'),1,'ROUTE_REQUESTED')).code,
  'REJECTED_RETENTION_CAPACITY'
);
equal('retention','retained operation count',capacity.snapshot().operations.length,1);
equal('retention','retained event count',capacity.snapshot().operations[0].events.length,2);

const restartSnapshot=happy.snapshot();
const restored=contract.restoreSnapshot(restartSnapshot,POLICY);
check('restart','valid snapshot restored',restored.ok===true);
equal('restart','restored state',restored.registry.operation(happyOp).state,'READY');
const badRestore=contract.restoreSnapshot(Object.assign({},restartSnapshot,{
  operations:[{events:[Object.assign({},restartSnapshot.operations[0].events[0],{state:'MOUNTED'})]}]
}),POLICY);
equal('restart','invalid event fails closed',badRestore.code,'RESTORE_REJECTED_EVENT');
equal('restart','invalid restore exposes no registry',badRestore.registry,null);
equal('restart','malformed snapshot fails closed',contract.restoreSnapshot({},POLICY).code,'RESTORE_REJECTED_MALFORMED');

let legacyCalls={registry:0,snapshot:0,scan:0};
const legacy={
  version:'1.6.3',
  atlasBuckets:['ACTIVE_CURRENT_APP'],
  keys:{registry:'pmp_mount_registry_v1'},
  registry(){legacyCalls.registry++;return {legacy:true}},
  snapshot(){legacyCalls.snapshot++;return {legacySnapshot:true}},
  scan(reason){legacyCalls.scan++;return {reason}}
};
const facade=contract.createLegacyAtlasFacade(legacy,happy);
equal('compatibility','facade construction has zero calls',legacyCalls,{registry:0,snapshot:0,scan:0});
equal('compatibility','explicit registry call',facade.registry(),{legacy:true});
equal('compatibility','explicit snapshot call',facade.snapshot(),{legacySnapshot:true});
equal('compatibility','explicit scan call',facade.scan('proof'),{reason:'proof'});
equal('compatibility','only explicit calls counted',legacyCalls,{registry:1,snapshot:1,scan:1});

legacyCalls={registry:0,snapshot:0,scan:0};
const runtime=runtimeLibrary.createRuntime(contract,legacy);
check('runtime','runtime available',runtime.available===true);
equal('runtime','runtime creation has zero legacy calls',legacyCalls,{registry:0,snapshot:0,scan:0});
equal('runtime','runtime starts empty',runtime.lifecycleSnapshot().operations.length,0);
const runtimeOp=operation('current-app','proof-runtime-010');
happyEvents(runtimeOp).forEach((item,index)=>equal(
  'runtime',
  `explicit runtime event ${index+1}`,
  runtime.applyOwnerEvent(item).code,
  'ACCEPTED'
));
equal('runtime','runtime final state',runtime.lifecycleOperation(runtimeOp).state,'READY');
equal('runtime','runtime exact duplicate',runtime.applyOwnerEvent(happyEvents(runtimeOp)[4]).code,'DUPLICATE_IGNORED');
const host={PMPMountLifecycleContractV1:contract,PMPMountRegistryV1:legacy};
const installed=runtimeLibrary.install(host);
check('runtime','install available',installed.available===true);
check('runtime','duplicate install returns same object',runtimeLibrary.install(host)===installed);
check('runtime','compatibility global installed',host.PMPMountRegistryLifecycleCompatibilityV1===installed.legacyCompatibility);
const missingRuntime=runtimeLibrary.install({});
check('runtime','missing dependencies fail closed',missingRuntime.available===false);
equal('runtime','missing runtime rejects event',missingRuntime.applyOwnerEvent(happyEvents(runtimeOp)[0]).code,'REJECTED_LIFECYCLE_RUNTIME_UNAVAILABLE');

const emptyView=diagnosticsView.read(installed);
equal('diagnostics','empty registry view status',emptyView.status,'READY_EMPTY');
equal('diagnostics','empty registry view operations',emptyView.operation_count,0);
const runtimeView=diagnosticsView.read(runtime);
equal('diagnostics','populated view status',runtimeView.status,'READY_WITH_OPERATIONS');
equal('diagnostics','populated view operations',runtimeView.operation_count,1);
equal('diagnostics','view final state',runtimeView.operations[0].state,'READY');
check('diagnostics','raw events absent',!Object.prototype.hasOwnProperty.call(runtimeView.operations[0],'events'));
check('diagnostics','details absent',!JSON.stringify(runtimeView).includes('mount_point'));
equal('diagnostics','repeated view deterministic',JSON.stringify(diagnosticsView.read(runtime)),JSON.stringify(runtimeView));
equal('diagnostics','unavailable view passive',diagnosticsView.read(null).status,'LIFECYCLE_RUNTIME_UNAVAILABLE');
equal(
  'diagnostics',
  'snapshot error passive',
  diagnosticsView.read({
    available:true,
    dependencyStatus:runtime.dependencyStatus,
    lifecycleSnapshot(){throw new Error('proof')}
  }).status,
  'LIFECYCLE_SNAPSHOT_ERROR'
);
equal(
  'diagnostics',
  'malformed snapshot passive',
  diagnosticsView.read({
    available:true,
    dependencyStatus:runtime.dependencyStatus,
    lifecycleSnapshot(){return {type:'wrong',operations:[]}}
  }).status,
  'LIFECYCLE_SNAPSHOT_MALFORMED'
);

const syntheticOperations=Array.from({length:65},(_,index)=>({
  operation_id:`pmp-mount:bounded:proof-${String(index).padStart(3,'0')}`,
  state:'READY',
  last_sequence:5,
  last_observed_at:'2026-07-26T08:30:05Z',
  resolved_owner:'app_orchestrator_owner',
  events:[{details:{secret:`hidden-${index}`}}]
}));
const boundedView=diagnosticsView.read({
  available:true,
  dependencyStatus:runtime.dependencyStatus,
  lifecycleSnapshot(){return {
    type:'PMP_MOUNT_LIFECYCLE_REGISTRY_SNAPSHOT_V1',
    contract_version:contract.contractVersion,
    registry_owner:contract.registryOwner,
    policy:runtime.policy,
    operations:syntheticOperations,
    diagnostics:{rejected:0,rejection_counts:{},last_rejection:null}
  }}
});
equal('diagnostics','bounded total operation truth',boundedView.operation_count,65);
equal('diagnostics','bounded visible operation count',boundedView.visible_operation_count,64);
check('diagnostics','bounded truncation declared',boundedView.disclosure.operations_truncated===true);
check('diagnostics','bounded details redacted',!JSON.stringify(boundedView).includes('hidden-'));

const effectTokens=[
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
];
for(const file of sourceFiles.slice(0,3)){
  for(const token of effectTokens){
    check('zero_effect_source',`${file} excludes ${token}`,!sources[file].includes(token));
  }
}
check('zero_effect_source','Diagnostics view has no event application entrypoint',!sources['pmp-mount-lifecycle-diagnostics-view-v1.js'].includes('applyOwnerEvent'));
check('zero_effect_source','Diagnostics owner has no event application entrypoint',!sources['pmp-diagnostics-owner-v1.js'].includes('applyOwnerEvent'));
check('zero_effect_source','Diagnostics owner declares no lifecycle mutation',sources['pmp-diagnostics-owner-v1.js'].includes("lifecycle_registry_mutation:'not_attempted'"));

const categoryCounts={};
assertions.forEach(row=>{categoryCounts[row.category]=(categoryCounts[row.category]||0)+1});
const report={
  type:'PMP_PASS5_UNIT5_ISOLATED_LIFECYCLE_TRANSITION_FAILURE_PROOF_V1',
  version:'1.0.0',
  created_at:'2026-07-26T08:24:00Z',
  repository:'pmpbird/pmp-bridge-shell',
  base_main_commit:'6f19ca6594b6a8950caed60d027075d2ba30eb46',
  mode:'ISOLATED_DETERMINISTIC_FIXTURES_ONLY',
  status:'PASS_ISOLATED_PROOF',
  components:{
    contract_version:contract.contractVersion,
    registry_owner:contract.registryOwner,
    runtime_type:runtimeLibrary.runtimeType,
    diagnostics_view_type:diagnosticsView.type,
    source_sha256:sourceHashes
  },
  coverage:{
    assertions_total:assertions.length,
    assertions_passed:assertions.filter(row=>row.pass).length,
    assertions_failed:assertions.filter(row=>!row.pass).length,
    category_counts:categoryCounts,
    categories:Object.keys(categoryCounts)
  },
  assertions,
  effects:{
    production_files_changed:false,
    current_path_started:false,
    live_observation_performed:false,
    formal_proof_performed:false,
    lifecycle_events_applied_outside_fixture:0,
    registry_mutations_outside_fixture:0,
    legacy_atlas_automatic_calls:0,
    mounts:0,
    repairs:0,
    route_assignments:0,
    storage_migrations:0,
    persisted_user_data_writes:0,
    historical_evidence_changes:0,
    pr122_touched:false
  },
  authority:{
    special_authority_type:'NONE',
    special_authority_consumed:false,
    consumed_observations_retried:false,
    formal_proof_retried:false
  },
  next_step:{
    id:'P5-U6',
    objective:'Decide from isolated evidence whether a bounded current-path observation is required; do not run one without the applicable exact authority.',
    requires_user_app_check:false,
    requires_new_explicit_authority:'ONLY_IF_P5_U6_DETERMINES_A_NEW_LIVE_OBSERVATION_IS_REQUIRED'
  },
  claim_ceiling:'Isolated deterministic lifecycle and read-only Diagnostics proof only. No production file change, current-path observation, app check, lifecycle event outside fixtures, persisted state change, or Pass 5 completion.'
};
fs.writeFileSync(OUTPUT,JSON.stringify(report,null,2)+'\n');
console.log(`PASS: P5-U5 isolated lifecycle proof (${assertions.length} assertions)`);
