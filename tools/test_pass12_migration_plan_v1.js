'use strict';
const fs=require('fs');
const path=require('path');
const crypto=require('crypto');
const root=path.resolve(__dirname,'..');
const gate=require(path.join(root,'pmp-migration-inactive-gate-v1.js'));
const plan=JSON.parse(fs.readFileSync(path.join(root,'pmp-migration-plan-v1.json'),'utf8'));
let total=0,failed=0;
function ok(value,label){total++;if(!value){failed++;process.stderr.write('FAIL '+label+'\n');}}
function eq(actual,expected,label){ok(JSON.stringify(actual)===JSON.stringify(expected),label+' actual='+JSON.stringify(actual)+' expected='+JSON.stringify(expected));}
function clone(value){return JSON.parse(JSON.stringify(value));}
function payloadHash(payload){return gate.sha256(gate.canonical(payload));}
function record(owner,id,payload,version=1){return{owner,record_id:id,schema_version:version,payload:clone(payload),payload_sha256:payloadHash(payload)};}
const owners=plan.inventory.map(row=>row.owner);
const fixtures=[
  record(owners[0],'bank:001',{title:'First',levels:[1,2,3],unknown:{preserve:true}}),
  record(owners[1],'packet:002',{indexeddb_key:'packet-002',bytes:4096,mime:'application/zip'}),
  record(owners[2],'mount:003',{mount:'continuous-run',active:true}),
  record(owners[3],'diagnostic:004',{status:'PASS',evidence:['a','b']}),
  record(owners[4],'route:005',{route:'bank',last_good:'control'}),
  record(owners[5],'level:006',{level:'6',state:'READY'}),
  record(owners[6],'source:007',{payload_ref:'sha256:source',payload_bytes:12345})
];

eq(gate.type,'PMP_MIGRATION_INACTIVE_GATE_V1','gate type');
eq(gate.version,'1.0.0-pass12','gate version');
eq(gate.plan_type,'PMP_MIGRATION_PLAN_V1','plan type export');
eq(gate.authority_type,'PMP_EXACT_PRODUCTION_MIGRATION_AUTHORITY_V1','authority type export');
eq(gate.sha256('abc'),crypto.createHash('sha256').update('abc').digest('hex'),'sha implementation');
eq(gate.canonical({z:1,a:{y:2,x:3}}),'{"a":{"x":3,"y":2},"z":1}','canonical ordering');
eq(gate.canonical([3,{b:2,a:1}]),'[3,{"a":1,"b":2}]','canonical array');
const snap=gate.snapshot();
eq(snap.status,'PRODUCTION_GATE_INACTIVE','snapshot inactive');
eq(snap.production_commit_available,false,'no production commit');
eq(snap.production_storage_api_present,false,'no storage api');
eq(snap.network_api_present,false,'no network api');
eq(snap.automatic_retry,false,'no retry');
eq(snap.effects_on_load.production_storage_reads,0,'no load reads');
eq(snap.effects_on_load.production_storage_writes,0,'no load writes');
eq(snap.effects_on_load.production_storage_deletes,0,'no load deletes');
eq(snap.effects_on_load.persisted_user_data_changed,false,'no load mutation');
eq(snap.effects_on_load.authority_consumed,false,'no authority consumed');

const valid=gate.validatePlan(plan);
ok(valid.ok,'plan valid');
eq(valid.decision,'ALLOW_STATIC_ONLY','static only');
eq(valid.code,'INACTIVE_PLAN_VALID','plan status');
eq(valid.inventory_count,7,'inventory count');
eq(valid.owner_count,7,'owner count');
ok(/^[0-9a-f]{64}$/.test(valid.plan_sha256),'plan hash');
for(const key of Object.keys(valid.effects)){eq(valid.effects[key],key==='persisted_user_data_changed'||key==='authority_consumed'?false:0,'plan effect '+key);}
for(const mutation of [
  p=>{p.type='BAD';},
  p=>{p.mode='ACTIVE';},
  p=>{p.default_decision='ALLOW';},
  p=>{p.target.activation='ACTIVE';},
  p=>{p.target.production_commit_available=true;},
  p=>{p.authority_gate.state='ACTIVE';},
  p=>{p.authority_gate.production_migration_authorized=true;},
  p=>{p.inventory=[];},
  p=>{p.inventory[0].id='';},
  p=>{p.inventory[0].owner='';},
  p=>{p.inventory[1].id=p.inventory[0].id;}
]){
  const altered=clone(plan);mutation(altered);ok(!gate.validatePlan(altered).ok,'invalid plan mutation denied');
}

const run=gate.dryRun(plan,fixtures,{fixture_scope:'DISPOSABLE_FIXTURE'});
ok(run.ok,'dry run ok');
eq(run.decision,'ALLOW_DISPOSABLE_FIXTURE_ONLY','dry run scope');
eq(run.code,'DRY_RUN_COMPLETE','dry run code');
eq(run.source_snapshot.record_count,7,'source count');
eq(run.target_manifest.record_count,7,'target count');
eq(run.quarantine_count,0,'no quarantine');
eq(run.reconciliation.source_count,7,'reconcile source count');
eq(run.reconciliation.target_count,7,'reconcile target count');
eq(run.reconciliation.identity_match,true,'identity match');
eq(run.reconciliation.payload_hashes_match,true,'payload match');
eq(run.reconciliation.unrelated_storage_policy,'PRESERVE_EXACTLY','unrelated policy');
ok(/^[0-9a-f]{64}$/.test(run.migration_id),'migration id');
ok(/^[0-9a-f]{64}$/.test(run.result_sha256),'result hash');
ok(/^[0-9a-f]{64}$/.test(run.source_snapshot.records_sha256),'source hash');
ok(/^[0-9a-f]{64}$/.test(run.target_manifest.records_sha256),'target hash');
ok(run.source_snapshot.source_bytes>0,'source bytes');
for(const key of Object.keys(run.effects)){eq(run.effects[key],key==='persisted_user_data_changed'||key==='authority_consumed'?false:0,'run effect '+key);}
run.staged_records.forEach((row,index)=>{
  const source=fixtures.find(item=>item.owner===row.owner&&item.record_id===row.record_id);
  ok(Boolean(source),'staged source '+index);
  eq(row.migration_id,run.migration_id,'staged migration id '+index);
  eq(row.source_schema_version,source.schema_version,'source schema '+index);
  eq(row.target_schema_version,1,'target schema '+index);
  eq(row.payload,source.payload,'payload exact '+index);
  eq(row.payload_sha256,source.payload_sha256,'payload hash exact '+index);
  eq(row.source_record_sha256,gate.sha256(gate.canonical(source)),'record hash '+index);
  ok(/^[0-9a-f]{64}$/.test(row.migration_receipt),'receipt hash '+index);
});

for(let iteration=0;iteration<12;iteration++){
  const reordered=fixtures.slice().sort(()=>0.5-((iteration%3)/3)).reverse();
  const repeat=gate.dryRun(plan,reordered,{fixture_scope:'DISPOSABLE_FIXTURE'});
  eq(repeat.migration_id,run.migration_id,'idempotent id '+iteration);
  eq(repeat.source_snapshot.records_sha256,run.source_snapshot.records_sha256,'idempotent source '+iteration);
  eq(repeat.target_manifest.records_sha256,run.target_manifest.records_sha256,'idempotent target '+iteration);
  eq(repeat.result_sha256,run.result_sha256,'idempotent result '+iteration);
}

for(const badScope of [undefined,null,{},'',false,'PRODUCTION','LIVE','USER_DATA']){
  const denied=gate.dryRun(plan,fixtures,badScope&&typeof badScope==='object'?badScope:{fixture_scope:badScope});
  ok(!denied.ok,'bad scope denied '+String(badScope));
  eq(denied.code,'DENIED_NONDISPOSABLE_SCOPE','bad scope code '+String(badScope));
}
for(const mutation of [
  r=>null,
  r=>[],
  r=>({...r,owner:''}),
  r=>({...r,record_id:''}),
  r=>({...r,schema_version:0}),
  r=>({...r,schema_version:'1'}),
  r=>{const x={...r};delete x.payload;return x;},
  r=>({...r,payload_sha256:'0'.repeat(64)}),
]){
  const rows=clone(fixtures);rows[0]=mutation(rows[0]);
  const denied=gate.dryRun(plan,rows,{fixture_scope:'DISPOSABLE_FIXTURE'});
  ok(!denied.ok,'malformed denied');
  ok(/^DENIED_/.test(denied.code),'malformed code');
}
const duplicate=clone(fixtures);duplicate.push(clone(fixtures[0]));
eq(gate.dryRun(plan,duplicate,{fixture_scope:'DISPOSABLE_FIXTURE'}).code,'DENIED_DUPLICATE_IDENTITY','duplicate denied');
const stale=clone(fixtures);stale[0].payload.title='mutated without hash';
eq(gate.dryRun(plan,stale,{fixture_scope:'DISPOSABLE_FIXTURE'}).code,'DENIED_RECORD_PAYLOAD_HASH','stale hash denied');
eq(gate.dryRun(plan,{}, {fixture_scope:'DISPOSABLE_FIXTURE'}).code,'DENIED_RECORD_SET','record set denied');

const orphan=record('unknown_owner','orphan:1',{exact:'bytes',nested:[1,2,3]});
const withOrphan=gate.dryRun(plan,fixtures.concat([orphan]),{fixture_scope:'DISPOSABLE_FIXTURE'});
ok(withOrphan.ok,'orphan quarantined');
eq(withOrphan.source_snapshot.record_count,7,'orphan excluded source count');
eq(withOrphan.target_manifest.record_count,7,'orphan excluded target count');
eq(withOrphan.quarantine_count,1,'orphan quarantine count');
eq(withOrphan.quarantine[0].identity,'unknown_owner\u0000orphan:1','orphan identity');
eq(withOrphan.quarantine[0].exact_record,orphan,'orphan exact');
eq(withOrphan.quarantine[0].record_sha256,gate.sha256(gate.canonical(orphan)),'orphan hash');

const shadow=gate.shadowCompare(fixtures,run.staged_records);
ok(shadow.ok,'shadow match');
eq(shadow.decision,'PURE_COMPARE_ONLY','shadow pure');
eq(shadow.code,'SHADOW_MATCH','shadow code');
eq(shadow.source_count,7,'shadow source count');
eq(shadow.target_count,7,'shadow target count');
eq(shadow.source_sha256,shadow.target_sha256,'shadow aggregate match');
for(const key of Object.keys(shadow.effects)){eq(shadow.effects[key],key==='persisted_user_data_changed'||key==='authority_consumed'?false:0,'shadow effect '+key);}
const alteredTarget=clone(run.staged_records);alteredTarget[0].payload_sha256='f'.repeat(64);
const mismatch=gate.shadowCompare(fixtures,alteredTarget);
ok(!mismatch.ok,'shadow mismatch');
eq(mismatch.code,'SHADOW_MISMATCH','shadow mismatch code');
ok(mismatch.source_sha256!==mismatch.target_sha256,'shadow mismatch hashes');
eq(gate.shadowCompare({},[]).code,'DENIED_SHADOW_INPUT','bad shadow source');
eq(gate.shadowCompare([],{}).code,'DENIED_SHADOW_INPUT','bad shadow target');

const unrelated={third_party:{token:'opaque',bytes:[0,1,2,255]},other_db:{version:99,records:['leave','alone']}};
const rollback=gate.buildRollbackPlan(run,fixtures,unrelated);
ok(rollback.ok,'rollback plan');
eq(rollback.code,'ROLLBACK_PLAN_READY','rollback code');
eq(rollback.decision,'ALLOW_PLAN_ONLY','rollback scope');
eq(rollback.plan.action,'DISCARD_STAGED_TARGET_AND_RETAIN_SOURCE','rollback action');
eq(rollback.plan.source_record_count,7,'rollback count');
eq(rollback.plan.exact_source_records,fixtures,'rollback exact source');
eq(rollback.plan.unrelated_storage,unrelated,'rollback unrelated');
eq(rollback.plan.unrelated_storage_sha256,gate.sha256(gate.canonical(unrelated)),'rollback unrelated hash');
eq(rollback.plan.source_delete_allowed,false,'rollback source delete false');
eq(rollback.plan.target_partial_discard_required,true,'rollback partial discard');
eq(rollback.plan.automatic_retry,false,'rollback retry false');
ok(/^[0-9a-f]{64}$/.test(rollback.plan.rollback_plan_sha256),'rollback hash');
for(const key of Object.keys(rollback.effects)){eq(rollback.effects[key],key==='persisted_user_data_changed'||key==='authority_consumed'?false:0,'rollback effect '+key);}
eq(gate.buildRollbackPlan({},fixtures,unrelated).code,'DENIED_ROLLBACK_INPUT','bad rollback result');
eq(gate.buildRollbackPlan(run,{},unrelated).code,'DENIED_ROLLBACK_INPUT','bad rollback source');

for(let failAfter=0;failAfter<fixtures.length;failAfter++){
  const partial=gate.simulateBoundedStage(run,failAfter);
  ok(!partial.ok,'partial fails '+failAfter);
  eq(partial.decision,'ROLLBACK','partial rollback '+failAfter);
  eq(partial.code,'INJECTED_PARTIAL_STAGE_FAILURE','partial code '+failAfter);
  eq(partial.staged_before_failure,failAfter,'partial count '+failAfter);
  eq(partial.staged_after_rollback,0,'partial cleared '+failAfter);
  eq(partial.rollback_complete,true,'partial rollback complete '+failAfter);
  eq(partial.source_changed,false,'partial source unchanged '+failAfter);
  eq(partial.automatic_retry,false,'partial no retry '+failAfter);
  eq(partial.effects.persisted_user_data_changed,false,'partial no user data '+failAfter);
}
const staged=gate.simulateBoundedStage(run,fixtures.length);
ok(staged.ok,'complete disposable stage');
eq(staged.code,'DISPOSABLE_STAGE_COMPLETE','stage code');
eq(staged.staged_count,7,'stage count');
eq(staged.source_changed,false,'stage source unchanged');
ok(/^[0-9a-f]{64}$/.test(staged.target_manifest_sha256),'stage hash');
eq(gate.simulateBoundedStage({},0).code,'DENIED_STAGE_INPUT','bad stage denied');

const largePayload='x'.repeat(256*1024);
const largeRecord=record(owners[0],'bank:large',{blob:largePayload});
const largeRun=gate.dryRun(plan,[largeRecord],{fixture_scope:'DISPOSABLE_FIXTURE'});
ok(largeRun.ok,'large fixture');
eq(largeRun.source_snapshot.record_count,1,'large count');
ok(largeRun.source_snapshot.source_bytes>256*1024,'large bytes counted');
eq(largeRun.staged_records[0].payload.blob.length,largePayload.length,'large exact length');
eq(largeRun.staged_records[0].payload_sha256,largeRecord.payload_sha256,'large exact hash');

for(const authority of [
  undefined,
  null,
  {},
  {type:'WRONG'},
  {type:'PMP_EXACT_PRODUCTION_MIGRATION_AUTHORITY_V1'},
  {type:'PMP_EXACT_PRODUCTION_MIGRATION_AUTHORITY_V1',single_use:true,commit:plan.base_main_commit,receipt_sha256:'a'.repeat(64)}
]){
  const denied=gate.requestProductionMigration({authority_receipt:authority});
  ok(!denied.ok,'production denied');
  eq(denied.decision,'DENY','production decision');
  eq(denied.code,'PRODUCTION_GATE_INACTIVE','production inactive');
  eq(denied.effects.production_storage_reads,0,'production no reads');
  eq(denied.effects.production_storage_writes,0,'production no writes');
  eq(denied.effects.production_storage_deletes,0,'production no deletes');
  eq(denied.effects.persisted_user_data_changed,false,'production no user mutation');
  eq(denied.effects.authority_consumed,false,'production no authority consume');
}

eq(plan.target.activation,'INACTIVE','plan target inactive');
eq(plan.target.production_commit_available,false,'plan no commit');
eq(plan.authority_gate.state,'INACTIVE','authority inactive');
eq(plan.authority_gate.production_migration_authorized,false,'migration unauthorized');
eq(plan.authority_gate.persisted_user_data_change_authorized,false,'user data unauthorized');
eq(plan.authority_gate.single_use,true,'future exact authority single use');
eq(plan.authority_gate.wildcards_allowed,false,'future no wildcard');
eq(plan.authority_gate.automatic_retry,false,'future no retry');
eq(plan.rollback.source_is_never_deleted,true,'source never deleted');
eq(plan.rollback.old_application_remains_recoverable,true,'old app recoverable');
eq(plan.rollback.partial_target_is_discarded,true,'partial target discarded');
eq(plan.rollback.unrelated_storage_preserved,true,'unrelated preserved');
eq(plan.checkpoints.append_only,true,'checkpoints append only');
eq(plan.checkpoints.overwrite_allowed,false,'checkpoint overwrite false');
eq(plan.idempotency.repeat_dry_run,'EXACT_SAME_RESULT','idempotency contract');
eq(plan.idempotency.automatic_retry,false,'no automatic retry');
eq(plan.inventory.length,7,'seven inventory classes');
eq(new Set(plan.inventory.map(row=>row.id)).size,7,'unique inventory ids');
eq(new Set(plan.inventory.map(row=>row.owner)).size,7,'unique owners');
ok(plan.forbidden_pass12_operations.includes('PRODUCTION_STORAGE_READ'),'read forbidden');
ok(plan.forbidden_pass12_operations.includes('PRODUCTION_STORAGE_WRITE'),'write forbidden');
ok(plan.forbidden_pass12_operations.includes('PRODUCTION_STORAGE_DELETE'),'delete forbidden');
ok(plan.forbidden_pass12_operations.includes('PERSISTED_USER_DATA_CHANGE'),'mutation forbidden');
ok(plan.forbidden_pass12_operations.includes('FORMAL_PROOF'),'formal proof forbidden');
ok(plan.allowed_pass12_operations.includes('DISPOSABLE_FIXTURE_DRY_RUN'),'fixture allowed');
ok(plan.allowed_pass12_operations.includes('SAFE_BLOCKED_PACKET'),'blocked packet allowed');

if(failed){process.stderr.write(`Pass 12 migration plan failed (${total-failed}/${total})\n`);process.exit(1);}
process.stdout.write(`PASS: Pass 12 inactive migration plan, disposable dry run, shadow compare, rollback, fault injection, and authority denial verified (${total}/${total})\n`);
