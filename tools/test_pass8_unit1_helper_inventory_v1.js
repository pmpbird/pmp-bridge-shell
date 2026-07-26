#!/usr/bin/env node
'use strict';
const assert=require('assert');
const inventory=require('./run_pass8_unit1_helper_inventory_v1.js');
let assertions=0;
function check(value,message){assertions++;assert(value,message)}
function equal(actual,expected,message){assertions++;assert.deepStrictEqual(actual,expected,message)}

const result=inventory.build();
equal(result.type,'PMP_PASS8_UNIT1_HELPER_INVENTORY_RESULT_V1','result type');
equal(result.version,'1.0.0','result version');
equal(result.status,'PASS','result status');
equal(inventory.verifyResultHash(result),true,'result hash');
equal(result.counts.tracked_files,1883,'tracked pull-request-head files');
equal(result.counts.declared_helpers,14,'declared helper count');
equal(result.counts.declared_unique_ids,14,'unique helper IDs');
equal(result.counts.declared_unique_files,14,'unique helper files');
equal(result.counts.declared_files_present,14,'all declared files tracked');
equal(result.counts.declared_files_missing,0,'no missing declared files');
equal(result.counts.accepted_helpers,12,'accepted declarations');
equal(result.counts.diagnostic_only_helpers,1,'diagnostic declaration');
equal(result.counts.legacy_helpers_declared,1,'legacy declaration');
equal(result.counts.growth_helpers,1,'growth declaration');
equal(result.counts.declared_owner_labels,8,'owner label count');
equal(result.counts.exact_p7_owner_label_matches,0,'no exact P7 owner labels');
equal(result.counts.unresolved_owner_labels,8,'all owner labels unresolved');
equal(result.counts.legacy_registry_helpers,11,'legacy helper count');
equal(result.counts.helper_named_root_sources,12,'helper-named root sources');
equal(result.counts.helper_named_undeclared_sources,9,'undeclared helper-named sources');
equal(result.counts.storage_keys,24,'unique storage keys');
equal(result.counts.panel_ids,3,'unique panels');
equal(result.counts.duplicate_ids,0,'no duplicate IDs');
equal(result.counts.duplicate_files,0,'no duplicate declaration files');

const required=[
  'id','file','name','owner','slot','purpose','level','registration',
  'allowed','forbidden','storage','panels','growth_source'
];
for(const helper of result.declared_helpers){
  for(const key of required)check(Object.prototype.hasOwnProperty.call(helper,key),`${helper.id} ${key}`);
  check(typeof helper.id==='string'&&helper.id.length>0,`${helper.id} valid ID`);
  check(typeof helper.file==='string'&&helper.file.endsWith('.js'),`${helper.id} JS file`);
  check(typeof helper.owner==='string'&&helper.owner.length>0,`${helper.id} owner label`);
  check(typeof helper.slot==='string'&&helper.slot.length>0,`${helper.id} slot`);
  check(Array.isArray(helper.allowed)&&helper.allowed.length>0,`${helper.id} allowed`);
  check(Array.isArray(helper.forbidden)&&helper.forbidden.length>0,`${helper.id} forbidden`);
  check(Array.isArray(helper.storage),`${helper.id} storage`);
  check(Array.isArray(helper.panels)&&helper.panels.length>0,`${helper.id} panels`);
  equal(helper.forbidden.includes('another_owner'),true,`${helper.id} another owner forbidden`);
  equal(helper.forbidden.includes('mount_registry'),true,`${helper.id} Mount Registry forbidden`);
  equal(helper.forbidden.includes('route_guardian'),true,`${helper.id} Route Guardian forbidden`);
}

equal(
  result.declared_helpers.map(row=>row.id).length,
  new Set(result.declared_helpers.map(row=>row.id)).size,
  'IDs isolated'
);
equal(
  result.declared_helpers.map(row=>row.file).length,
  new Set(result.declared_helpers.map(row=>row.file)).size,
  'files isolated'
);
equal(result.conflicts.missing_declared_files,[],'missing list empty');
equal(result.conflicts.duplicate_ids,[],'duplicate ID list empty');
equal(result.conflicts.duplicate_files,[],'duplicate file list empty');
equal(
  result.conflicts.owner_labels_not_exact_p7_ids,
  [
    'active_path_discovery_owner',
    'app_orchestrator',
    'bug_bank_owner',
    'continuous_run_owner',
    'mount_registry',
    'runtime_health_monitor',
    'runtime_version_manager',
    'safe_writer_owner'
  ],
  'owner vocabulary conflicts exact'
);
equal(
  result.conflicts.helper_named_sources_without_pass8_declaration,
  [
    'pmp-continuous-run-helper-conflict-blocker-v1.js',
    'pmp-helper-bank-live-inspector-v1.js',
    'pmp-helper-bank-live-inspector-v2.js',
    'pmp-helper-problem-display-sync-v1.js',
    'pmp-helper-problem-memory-v1.js',
    'pmp-helper-problem-type-only-v1.js',
    'pmp-helper-problem-type-seeds-v1.js',
    'pmp-helper-symptom-watcher-v1.js',
    'pmp-p15-helper-tidy-v1.js'
  ],
  'undeclared helper-named sources exact'
);
equal(
  result.conflicts.disposition,
  'HOLD_AS_OBSERVED_CONFLICT_NO_AUTHORITY_UNTIL_P8_U2_CONTRACT',
  'conflicts held'
);
equal(
  result.conflicts.legacy_registry_parent_owner_vocabulary,
  'P7_OWNER_IDS',
  'legacy vocabulary'
);
equal(
  result.conflicts.pass8_rules_owner_vocabulary,
  'NON_P7_ALIASES_AND_ADDITIONAL_DOMAINS',
  'rules vocabulary'
);

equal(result.owner_rows.length,8,'eight owner rows');
for(const row of result.owner_rows){
  check(row.helper_count>0,`${row.owner_label} has helpers`);
  equal(row.exact_p7_owner_match,false,`${row.owner_label} not silently normalized`);
}
equal(
  result.owner_rows.reduce((total,row)=>total+row.helper_count,0),
  14,
  'owner row helper total'
);
equal(result.growth_helpers.length,1,'one growth row');
equal(result.growth_helpers[0].id,'continuous_run_bank_order_frame_loader','growth helper identity');
equal(result.growth_helpers[0].owner,'continuous_run_owner','growth owner unresolved');
equal(result.growth_helpers[0].growth_source,'continuous_run_frame_loader','growth source');
equal(result.growth_helpers[0].panels.includes('continuous_run'),true,'growth panel declared');

equal(result.legacy_helpers.length,11,'legacy rows');
equal(new Set(result.legacy_helpers.map(row=>row.id)).size,11,'legacy IDs unique');
equal(
  result.legacy_helpers.every(row=>row.parent_owner.endsWith('_owner')),
  true,
  'legacy owners use P7-style IDs'
);
equal(result.legacy_snapshot_summary.helpers_total,11,'legacy snapshot total');
equal(result.legacy_snapshot_summary.helpers_present,0,'sandbox observes none');
equal(result.legacy_snapshot_summary.helpers_healthy,0,'sandbox certifies none');
equal(result.legacy_snapshot_summary.missing_active_helpers.length,2,'legacy active missing');
equal(result.legacy_snapshot_summary.orphan_helpers.length,11,'legacy sandbox orphans');

equal(result.storage_keys.includes('pmp_helper_registry_snapshot_v1'),true,'legacy storage mapped');
equal(result.storage_keys.includes('pmp_bug_watch_receipt_lineage_v2'),true,'Bug Watch storage mapped');
equal(result.panel_ids,['active_path_discovery_card','continuous_run','diagnostic_output'],'panels exact');

for(const value of Object.values(result.effects))equal(value,false,'inventory effect false');
check(result.claim_ceiling.includes('Read-only static Helper inventory'),'claim ceiling');
check(result.claim_ceiling.includes('in-memory storage only'),'sandbox ceiling');
check(result.claim_ceiling.includes('grants no Helper'),'no authority ceiling');

const tampered=JSON.parse(JSON.stringify(result));
tampered.counts.declared_helpers=15;
equal(inventory.verifyResultHash(tampered),false,'tampered result rejected');

console.log(`PASS: P8-U1 read-only Helper inventory (${assertions}/${assertions})`);
