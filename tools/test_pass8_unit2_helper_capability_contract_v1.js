#!/usr/bin/env node
'use strict';
const assert=require('assert');
const runner=require('./run_pass8_unit2_helper_capability_contract_v1.js');
let assertions=0;
function check(value,message){assertions++;assert(value,message)}
function equal(actual,expected,message){assertions++;assert.deepStrictEqual(actual,expected,message)}

const policy=runner.contract();
equal(policy.contract_version,'PMP_HELPER_CAPABILITY_CONTRACT_V1','contract version');
equal(policy.model,'EXPLICIT_HELPER_CAPABILITY_FAIL_CLOSED','model');
equal(policy.root_grant_authority,'app_orchestrator_owner','root grantor');
equal(Object.keys(policy.owner_bindings).length,8,'eight owner labels resolved');
equal(policy.unknown_helper_sources.length,9,'nine unknown sources held');
equal(policy.legacy_policy,'HOLD_NO_ACTIVE_CAPABILITY','legacy held');
equal(policy.unknown_source_policy,'HOLD_NO_CAPABILITY','unknown held');
equal(policy.filename_authority_policy,'NEVER_INFER_AUTHORITY','filenames grant nothing');
equal(policy.growth_policy,'EXACT_DECLARED_SOURCE_OWNER_SLOT_AND_GROWTH_BINDING','growth exact');
equal(policy.revocation_policy,'MONOTONIC_FAIL_CLOSED','revocation monotonic');
equal(policy.failure_effect,'DENY_NO_RUNTIME_OR_EXTERNAL_SIDE_EFFECT_AND_EMIT_OPERATION_CODE','failure effect');
equal(policy.explicit_helper_holds.safe_writer_current_return_fix,'DECLARATION_AND_SOURCE_ROUTE_BEHAVIOR_REQUIRE_LATER_EXPLICIT_OWNER_RECONCILIATION','Safe Writer held');

const expectedBindings={
  app_orchestrator:['app_orchestrator_owner','app_orchestrator','OWNER_ALIAS'],
  mount_registry:['mount_registry_owner','mount_registry','OWNER_ALIAS'],
  continuous_run_owner:['continuous_run_level_owner','continuous_run','OWNER_ALIAS'],
  active_path_discovery_owner:['app_orchestrator_owner','app_orchestrator','BOUNDED_SUBDOMAIN'],
  runtime_health_monitor:['diagnostics_owner','diagnostics','BOUNDED_SUBDOMAIN'],
  runtime_version_manager:['diagnostics_owner','diagnostics','BOUNDED_SUBDOMAIN'],
  bug_bank_owner:['bank_screen_owner','bank','GUARDED_SUBDOMAIN'],
  safe_writer_owner:['reload_current_owner','current_reload','HELD_SUBDOMAIN']
};
for(const [label,expected] of Object.entries(expectedBindings)){
  const actual=policy.owner_bindings[label];
  equal(actual.canonical_owner_id,expected[0],`${label} owner`);
  equal(actual.section_id,expected[1],`${label} section`);
  equal(actual.binding_kind,expected[2],`${label} kind`);
  check(Array.isArray(actual.guard_requirements),`${label} guards array`);
}
equal(policy.owner_bindings.bug_bank_owner.guard_requirements,[
  'bounded_bug_authority_lease',
  'private_owner_token',
  'unexpired_lease',
  'formal_handoff'
],'bug domain exact guards');

const inventory=runner.inventory(policy);
equal(inventory.counts,{
  declared_helpers:14,
  eligible_helpers:12,
  held_declared_helpers:2,
  owner_bindings:8,
  guarded_helpers:2,
  growth_helpers:1,
  legacy_helpers:1,
  unknown_helper_sources:9
},'inventory counts');
equal(inventory.declared.length,14,'fourteen described');
equal(inventory.unknown.length,9,'nine unknown rows');
equal(new Set(inventory.declared.map(row=>row.helper_id)).size,14,'unique IDs');
equal(new Set(inventory.declared.map(row=>row.helper_file)).size,14,'unique files');
equal(inventory.declared.filter(row=>row.disposition==='ELIGIBLE_STATIC_CAPABILITY').length,12,'eligible count');
equal(inventory.declared.find(row=>row.helper_id==='legacy_helper_registry').disposition,'HELD_LEGACY','legacy disposition');
equal(inventory.declared.find(row=>row.helper_id==='safe_writer_current_return_fix').disposition,'HELD_CONTRACT_CONFLICT','Safe Writer disposition');
check(inventory.unknown.every(row=>row.disposition==='HELD_UNDECLARED_SOURCE'),'all unknowns held');
check(inventory.declared.every(row=>/^[0-9a-f]{64}$/.test(row.helper_source_sha256)),'source hashes bound');
for(const helper of inventory.declared){
  check(helper.canonical_owner_id.endsWith('_owner'),`${helper.helper_id} canonical owner`);
  check(helper.section_id.length>0,`${helper.helper_id} section`);
  check(helper.slot.length>0,`${helper.helper_id} slot`);
  check(helper.actions.length>0,`${helper.helper_id} actions`);
  check(helper.resources.includes(`helper:${helper.helper_id}`),`${helper.helper_id} identity resource`);
  check(helper.resources.includes(`owner:${helper.canonical_owner_id}:slot:${helper.slot}`),`${helper.helper_id} slot resource`);
  equal(new Set(helper.actions).size,helper.actions.length,`${helper.helper_id} action uniqueness`);
  equal(new Set(helper.resources).size,helper.resources.length,`${helper.helper_id} resource uniqueness`);
}

function grantEvent(helperId,op='op:test:grant',overrides={}){
  return runner.event('GRANT',op,{capability:runner.capabilityFor(helperId,overrides,policy)});
}
function authorizeEvent(cap,op='op:test:authorize',overrides={}){
  return runner.event('AUTHORIZE',op,Object.assign({
    capability_id:cap.capability_id,
    helper_id:cap.helper_id,
    canonical_owner_id:cap.canonical_owner_id,
    section_id:cap.section_id,
    slot:cap.slot,
    action:cap.actions[0],
    resource:cap.resources[0],
    guard_evidence:cap.guard_requirements,
    growth_source:cap.growth_source,
    revocation_epoch:cap.revocation_epoch
  },overrides));
}
function lastCode(events){return runner.evaluate(events,policy).outcomes.slice(-1)[0].code}

const atlas=runner.capabilityFor('pass2_atlas_adapter',{},policy);
const positive=runner.evaluate([
  runner.event('GRANT','op:test:atlas-grant',{capability:atlas}),
  authorizeEvent(atlas,'op:test:atlas-authorize')
],policy);
equal(positive.status,'PASS','positive status');
equal(positive.summary.events,2,'positive events');
equal(positive.summary.accepted,2,'positive accepted');
equal(positive.summary.authorized,1,'positive authorized');
equal(positive.summary.rejected,0,'positive rejected');
equal(positive.outcomes.map(row=>row.code),['CAPABILITY_GRANTED','AUTHORIZED'],'positive codes');
check(runner.verifyResultHash(positive),'positive hash');
check(Object.values(positive.effects).every(value=>value===false),'zero effects');
check(positive.claim_ceiling.includes('Pure static'),'claim ceiling');
equal(runner.evaluate([
  runner.event('GRANT','op:test:atlas-grant',{capability:atlas}),
  authorizeEvent(atlas,'op:test:atlas-authorize')
],policy),positive,'deterministic');

for(const helper of inventory.declared.filter(row=>row.disposition==='ELIGIBLE_STATIC_CAPABILITY')){
  const cap=runner.capabilityFor(helper.helper_id,{},policy);
  const result=runner.evaluate([
    runner.event('GRANT',`op:all:${helper.helper_id}:grant`,{capability:cap}),
    authorizeEvent(cap,`op:all:${helper.helper_id}:authorize`)
  ],policy);
  equal(result.outcomes[0].code,'CAPABILITY_GRANTED',`${helper.helper_id} grant`);
  equal(result.outcomes[1].code,'AUTHORIZED',`${helper.helper_id} authorize`);
  equal(result.summary.authorized,1,`${helper.helper_id} authorized once`);
}

const bug=runner.capabilityFor('bug_watch_passive_capture',{},policy);
equal(
  lastCode([
    runner.event('GRANT','op:bug:grant',{capability:bug}),
    authorizeEvent(bug,'op:bug:missing-guard',{guard_evidence:[]})
  ]),
  'REJECTED_GUARD_REQUIREMENTS',
  'bug guard required'
);
equal(
  lastCode([
    runner.event('GRANT','op:bug:grant-ok',{capability:bug}),
    authorizeEvent(bug,'op:bug:authorize-ok')
  ]),
  'AUTHORIZED',
  'bug exact guard accepted'
);

const growth=runner.capabilityFor('continuous_run_bank_order_frame_loader',{},policy);
equal(
  lastCode([
    runner.event('GRANT','op:growth:grant',{capability:growth}),
    authorizeEvent(growth,'op:growth:mismatch',{growth_source:'other_growth'})
  ]),
  'REJECTED_GROWTH_SOURCE',
  'growth mismatch denied'
);
equal(
  lastCode([
    runner.event('GRANT','op:growth:grant-ok',{capability:growth}),
    authorizeEvent(growth,'op:growth:ok')
  ]),
  'AUTHORIZED',
  'growth exact binding accepted'
);

equal(lastCode([grantEvent('legacy_helper_registry')]),'REJECTED_LEGACY_HELPER_HELD','legacy grant denied');
equal(lastCode([grantEvent('safe_writer_current_return_fix')]),'REJECTED_HELPER_CONFLICT_HELD','Safe Writer grant denied');

const fake=runner.capabilityFor('pass2_atlas_adapter',{
  capability_id:'cap:p8u2:undeclared',
  helper_id:'undeclared_helper',
  helper_file:policy.unknown_helper_sources[0]
},policy);
equal(lastCode([runner.event('GRANT','op:unknown-source',{capability:fake})]),'REJECTED_UNDECLARED_SOURCE','undeclared source denied');
fake.helper_file='not-tracked-helper.js';
equal(lastCode([runner.event('GRANT','op:unknown-helper',{capability:fake})]),'REJECTED_UNKNOWN_HELPER','unknown helper denied');

const mutations=[
  ['helper_file','other.js','REJECTED_HELPER_FILE_BINDING'],
  ['helper_source_sha256','0'.repeat(64),'REJECTED_SOURCE_HASH'],
  ['declared_owner_label','other_owner','REJECTED_OWNER_ALIAS'],
  ['canonical_owner_id','app_orchestrator_owner','REJECTED_OWNER_BINDING'],
  ['section_id','app_orchestrator','REJECTED_OWNER_BINDING'],
  ['slot','other_slot','REJECTED_SLOT_BINDING'],
  ['registration','legacy','REJECTED_REGISTRATION_BINDING'],
  ['actions',['read_atlas'],'REJECTED_ACTION_BINDING'],
  ['resources',['helper:pass2_atlas_adapter'],'REJECTED_RESOURCE_BINDING'],
  ['guard_requirements',['unexpected_guard'],'REJECTED_GUARD_BINDING'],
  ['growth_source','unexpected_growth','REJECTED_GROWTH_SOURCE'],
  ['granted_by','mount_registry_owner','REJECTED_ROOT_GRANT_AUTHORITY'],
  ['expires_at','2026-07-25T00:00:00Z','REJECTED_EXPIRY'],
  ['revocation_epoch',-1,'REJECTED_REVOCATION_EPOCH']
];
for(const [field,value,code] of mutations){
  equal(lastCode([grantEvent('pass2_atlas_adapter',`op:mutate:${field}`,{[field]:value})]),code,`${field} denied`);
}
equal(
  lastCode([runner.event('GRANT','op:shape',{capability:{}})]),
  'REJECTED_CAPABILITY_SHAPE',
  'shape denied'
);
equal(
  lastCode([grantEvent('pass2_atlas_adapter','op:version',{contract_version:'wrong'})]),
  'REJECTED_CONTRACT_VERSION',
  'version denied'
);
equal(
  lastCode([grantEvent('pass2_atlas_adapter','op:bad-id',{capability_id:'BAD ID'})]),
  'REJECTED_CAPABILITY_ID',
  'capability ID denied'
);

equal(
  lastCode([
    grantEvent('pass2_atlas_adapter','op:duplicate-a'),
    grantEvent('pass2_atlas_adapter','op:duplicate-b')
  ]),
  'REJECTED_DUPLICATE_CAPABILITY',
  'duplicate capability denied'
);
equal(
  lastCode([
    grantEvent('pass2_atlas_adapter','op:duplicate-operation'),
    authorizeEvent(atlas,'op:duplicate-operation')
  ]),
  'REJECTED_DUPLICATE_OPERATION',
  'duplicate operation denied'
);
equal(lastCode([runner.event('AUTHORIZE','op:missing',{capability_id:'cap:missing'})]),'REJECTED_CAPABILITY_MISSING','missing denied');

equal(
  lastCode([
    runner.event('GRANT','op:owner:grant',{capability:atlas}),
    authorizeEvent(atlas,'op:owner:deny',{canonical_owner_id:'app_orchestrator_owner'})
  ]),
  'REJECTED_OWNER_BINDING',
  'authorize owner denied'
);
equal(
  lastCode([
    runner.event('GRANT','op:slot:grant',{capability:atlas}),
    authorizeEvent(atlas,'op:slot:deny',{slot:'other_slot'})
  ]),
  'REJECTED_SLOT_BINDING',
  'authorize slot denied'
);
equal(
  lastCode([
    runner.event('GRANT','op:action:grant',{capability:atlas}),
    authorizeEvent(atlas,'op:action:deny',{action:'other_action'})
  ]),
  'REJECTED_ACTION_NOT_GRANTED',
  'authorize action denied'
);
equal(
  lastCode([
    runner.event('GRANT','op:resource:grant',{capability:atlas}),
    authorizeEvent(atlas,'op:resource:deny',{resource:'other:resource'})
  ]),
  'REJECTED_RESOURCE_NOT_GRANTED',
  'authorize resource denied'
);
equal(
  lastCode([
    runner.event('GRANT','op:identity:grant',{capability:atlas}),
    authorizeEvent(atlas,'op:identity:deny',{helper_id:'other_helper'})
  ]),
  'REJECTED_HELPER_IDENTITY',
  'authorize helper denied'
);
equal(
  lastCode([
    runner.event('GRANT','op:epoch:grant',{capability:atlas}),
    authorizeEvent(atlas,'op:epoch:deny',{revocation_epoch:1})
  ]),
  'REJECTED_REVOCATION_EPOCH',
  'authorize epoch denied'
);
equal(
  lastCode([
    runner.event('GRANT','op:future:grant',{capability:atlas}),
    authorizeEvent(atlas,'op:future:deny',{observed_at:'2026-07-25T00:00:00Z'})
  ]),
  'REJECTED_NOT_YET_VALID',
  'not-yet-valid denied'
);
equal(
  lastCode([
    runner.event('GRANT','op:expired:grant',{capability:atlas}),
    authorizeEvent(atlas,'op:expired:deny',{observed_at:'2026-08-03T00:00:00Z'})
  ]),
  'REJECTED_EXPIRED',
  'expired denied'
);

equal(
  lastCode([
    runner.event('GRANT','op:revoke:grant',{capability:atlas}),
    runner.event('REVOKE','op:revoke:wrong',{
      capability_id:atlas.capability_id,
      actor_id:'mount_registry_owner',
      revocation_epoch:1
    })
  ]),
  'REJECTED_REVOCATION_AUTHORITY',
  'wrong revoker denied'
);
equal(
  lastCode([
    runner.event('GRANT','op:revoke:stale-grant',{capability:atlas}),
    runner.event('REVOKE','op:revoke:stale',{
      capability_id:atlas.capability_id,
      actor_id:'app_orchestrator_owner',
      revocation_epoch:0
    })
  ]),
  'REJECTED_STALE_REVOCATION',
  'stale revocation denied'
);
const revoked=runner.evaluate([
  runner.event('GRANT','op:revoke:ok-grant',{capability:atlas}),
  runner.event('REVOKE','op:revoke:ok',{
    capability_id:atlas.capability_id,
    actor_id:'app_orchestrator_owner',
    revocation_epoch:1
  }),
  authorizeEvent(atlas,'op:revoke:after')
],policy);
equal(revoked.outcomes[1].code,'CAPABILITY_REVOKED','revocation accepted');
equal(revoked.outcomes[2].code,'REJECTED_CAPABILITY_REVOKED','revoked use denied');
equal(revoked.summary.capabilities_revoked,1,'revoked count');

const tampered=JSON.parse(JSON.stringify(positive));
tampered.summary.authorized=2;
equal(runner.verifyResultHash(tampered),false,'tampered result rejected');
console.log(`PASS: P8-U2 Helper capability contract (${assertions}/${assertions})`);
