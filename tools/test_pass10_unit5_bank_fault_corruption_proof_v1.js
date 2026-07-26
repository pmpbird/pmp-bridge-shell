#!/usr/bin/env node
'use strict';

const assert = require('assert');
const runner = require('./run_pass10_unit5_bank_fault_corruption_proof_v1.js');

let assertions = 0;
function check(value, message) {
  assertions += 1;
  assert(value, message);
}
function equal(actual, expected, message) {
  assertions += 1;
  assert.deepStrictEqual(actual, expected, message);
}

const result = runner.scenarioResult();
equal(result.type, runner.TYPE, 'result type');
equal(result.version, runner.VERSION, 'result version');
equal(
  result.status,
  'BANK_FAULT_ROLLBACK_AND_CORRUPTION_CONTAINMENT_PROVEN',
  'result status'
);
equal(runner.verifyResultHash(result), true, 'result hash valid');

const chain = result.evidence_chain;
equal(chain.units.length, 4, 'four prior units');
equal(
  chain.units.map(row => row.unit),
  ['P10-U1', 'P10-U2', 'P10-U3', 'P10-U4'],
  'prior unit order'
);
equal(
  chain.units.map(row => row.status),
  [
    'BANK_INVENTORY_RECONCILIATION_PROVEN',
    'BANK_INVENTORY_CONTRACT_PROVEN',
    'BANK_READONLY_PROJECTION_PROVEN',
    'BANK_OWNER_PROJECTION_REFRESH_PROVEN'
  ],
  'prior statuses'
);
equal(
  chain.exact_progression,
  ['P10-U2', 'P10-U3', 'P10-U4', 'P10-U5'],
  'receipt progression'
);
equal(chain.assertions_by_unit, [110, 187, 125, 121], 'prior assertions');
equal(chain.cumulative_prior_assertions, 543, 'cumulative assertions');
equal(chain.all_permanent_gates_bound, true, 'all permanent gates bound');

const large = result.large_inventory;
equal(large.fixture_records, runner.LARGE_RECORDS, 'large fixture size');
equal(large.fixture_records, 2048, 'large inventory exact count');
equal(large.projected_items_first, 2048, 'first large projection count');
equal(large.projected_items_second, 2048, 'second large projection count');
equal(large.stable_ids, true, 'large stable IDs');
equal(large.unique_ids, 2048, 'large IDs unique');
equal(large.exact_bytes_after_first, true, 'first snapshot exact bytes');
equal(large.exact_bytes_after_second, true, 'second snapshot exact bytes');
equal(large.unrelated_bytes_preserved, true, 'large unrelated bytes');
equal(large.load_calls, {get: 0, set: 0, remove: 0, key: 0}, 'load zero calls');
check(large.first_effects.storage_reads > 0, 'first bounded reads');
equal(large.first_effects.storage_writes, 0, 'first zero writes');
equal(large.first_effects.storage_deletes, 0, 'first zero deletes');
equal(large.first_effects.indexeddb_reads, 0, 'first zero indexeddb');
check(large.second_effects.storage_reads > 0, 'second bounded reads');
equal(large.second_effects.storage_writes, 0, 'second zero writes');
equal(large.second_effects.storage_deletes, 0, 'second zero deletes');
equal(large.second_effects.indexeddb_reads, 0, 'second zero indexeddb');
equal(large.raw_payloads_exposed, 0, 'large no raw payload');

const duplicate = result.duplicate_and_collision;
equal(duplicate.projected_collision_items, 2, 'two collision items');
equal(duplicate.all_quarantined, true, 'collision quarantined');
equal(duplicate.all_collision_marked, true, 'collision reason');
equal(duplicate.payload_hashes_distinct, 2, 'collision payloads distinct');
equal(duplicate.duplicate_owner_event_denied, true, 'duplicate event denied');
equal(duplicate.duplicate_projection_refreshes, 1, 'duplicate no second refresh');
equal(duplicate.duplicate_bytes_unchanged, true, 'duplicate exact bytes');

const fault = result.orphan_and_corruption;
equal(fault.corrupt_items, 1, 'one corrupt item');
equal(fault.corrupt_quarantined, true, 'corrupt quarantined');
equal(fault.corrupt_raw_bytes_preserved, true, 'corrupt raw preserved');
equal(fault.orphan_items, 1, 'one orphan item');
equal(fault.orphan_quarantined, true, 'orphan quarantined');
equal(fault.orphan_owner_null, true, 'orphan owner null');
equal(fault.orphan_raw_bytes_preserved, true, 'orphan raw preserved');
equal(fault.snapshot_zero_writes, true, 'fault snapshot zero writes');
equal(fault.snapshot_zero_deletes, true, 'fault snapshot zero deletes');
equal(fault.all_fault_bytes_preserved, true, 'all fault bytes preserved');
equal(fault.unrelated_bytes_preserved, true, 'fault unrelated preserved');

const unavailable = result.stale_and_unavailable;
equal(unavailable.stale_commit_denied, true, 'stale denied');
equal(unavailable.stale_code, 'DENIED_EXPECTED_VERSION', 'stale code');
equal(unavailable.stale_effects.storage_writes, 0, 'stale zero writes');
equal(unavailable.stale_effects.storage_deletes, 0, 'stale zero deletes');
equal(unavailable.stale_effects.persisted_user_data_changed, false, 'stale no data');
equal(unavailable.stale_bytes_unchanged, true, 'stale exact bytes');
equal(
  unavailable.unavailable_projection_status,
  'READ_ONLY_PROJECTION_READY',
  'unavailable projection status'
);
equal(unavailable.unavailable_projection_items, 0, 'unavailable zero items');
equal(unavailable.unavailable_commit_denied, true, 'unavailable commit denied');
equal(
  unavailable.unavailable_commit_code,
  'DENIED_STORAGE_UNAVAILABLE',
  'unavailable code'
);
equal(unavailable.unavailable_commit_effects.storage_writes, 0, 'unavailable zero writes');
equal(unavailable.unavailable_commit_effects.storage_deletes, 0, 'unavailable zero deletes');
equal(
  unavailable.unavailable_commit_effects.persisted_user_data_changed,
  false,
  'unavailable no data'
);
equal(
  unavailable.unavailable_storage_calls,
  {get: 0, set: 0, remove: 0, key: 0},
  'unavailable no storage calls'
);

const rollback = result.atomic_rollback;
equal(rollback.result_code, 'DENIED_ATOMIC_WRITE_FAILED', 'rollback code');
equal(rollback.result_effects.storage_writes, 0, 'rollback reports zero writes');
equal(rollback.result_effects.storage_deletes, 0, 'rollback reports zero deletes');
equal(
  rollback.result_effects.persisted_user_data_changed,
  false,
  'rollback reports no data'
);
equal(rollback.exact_bytes_restored, true, 'rollback exact bytes');
equal(rollback.existing_first_key_restored, true, 'first key restored');
equal(rollback.existing_second_key_preserved, true, 'second key preserved');
equal(rollback.unrelated_bytes_preserved, true, 'rollback unrelated preserved');
equal(rollback.resource_version, 0, 'rollback version unchanged');
equal(rollback.receipt_count, 0, 'rollback no receipt');

const restart = result.accepted_and_restart;
equal(restart.accepted_code, 'COMMITTED', 'accepted code');
equal(restart.accepted_refreshes, 1, 'accepted one refresh');
check(
  restart.accepted_snapshot_reason.startsWith('accepted_bank_owner_commit:'),
  'accepted receipt-bound reason'
);
equal(restart.accepted_item_visible, true, 'accepted item visible');
equal(
  restart.restart_load_delta,
  {get: 0, set: 0, remove: 0, key: 0},
  'restart load zero storage'
);
equal(restart.restart_snapshot_items, 1, 'restart item count');
equal(restart.restart_item_visible, true, 'restart item visible');
equal(restart.restart_item_id_matches, true, 'restart stable identity');
equal(restart.restart_snapshot_zero_writes, true, 'restart zero writes');
equal(restart.restart_snapshot_zero_deletes, true, 'restart zero deletes');
equal(restart.restart_bytes_unchanged, true, 'restart exact bytes');
equal(restart.restart_adapter_refreshes, 0, 'restart adapter no synthetic refresh');

const safety = result.active_safety;
equal(safety.boundary_only_writer_rule, true, 'boundary only writer');
equal(safety.projection_unknown_policy, true, 'unknown policy');
equal(safety.projection_historic_policy, true, 'historic policy');
equal(safety.adapter_receipt_hash_validation, true, 'receipt hash');
equal(safety.adapter_boundary_receipt_validation, true, 'boundary receipt');
equal(safety.adapter_duplicate_denial, true, 'adapter duplicate');
equal(safety.adapter_stale_denial, true, 'adapter stale');
equal(safety.tab_raw_owner_listener_absent, true, 'tab no raw listener');
equal(safety.tab_sanitized_listener_present, true, 'tab sanitized listener');
equal(safety.tab_cached_projection, true, 'tab cached projection');
equal(safety.one_boundary_load, 1, 'one boundary load');
equal(safety.one_projection_load, 1, 'one projection load');
equal(safety.one_adapter_load, 1, 'one adapter load');
equal(safety.one_tab_load, 1, 'one tab load');
equal(safety.recurring_timers, 0, 'no recurring timers');
equal(safety.adapter_write_api, false, 'adapter no write');
equal(safety.adapter_delete_api, false, 'adapter no delete');
equal(safety.adapter_migration_api, false, 'adapter no migration');

const decision = result.observation_decision_input;
equal(decision.deterministic_fault_cases.length, 12, 'twelve decision cases');
equal(decision.unresolved_deterministic_failures, 0, 'zero unresolved');
equal(decision.user_app_check_required_now, false, 'no app check now');
equal(decision.bounded_observation_performed, false, 'no observation');
equal(decision.bounded_observation_authority_consumed, false, 'no authority consumed');
equal(decision.next_unit_may_decide_rehearsal_without_observation, true, 'U6 ready');

for (const [key, value] of Object.entries(result.effects)) {
  equal(value, false, `effect false ${key}`);
}
equal(result.next_step.id, 'P10-U6', 'next U6');
equal(result.next_step.requires_user_app_check, false, 'U6 no app check');
equal(result.next_step.requires_new_explicit_authority, false, 'U6 no new authority');
equal(result.next_step.persisted_user_data_change_allowed, false, 'U6 no user data');
equal(result.next_step.production_migration_allowed, false, 'U6 no production migration');
equal(result.next_step.stop_after, false, 'continue after U5');
check(result.claim_ceiling.includes('disposable-fixture'), 'claim fixture only');
check(result.claim_ceiling.includes('No production source'), 'claim no production');
check(result.claim_ceiling.includes('real user storage'), 'claim no user storage');
check(result.claim_ceiling.includes('scarce observation'), 'claim no observation');
check(result.claim_ceiling.includes('formal proof'), 'claim no formal proof');

console.log(
  `PASS: P10-U5 Bank fault, rollback, restart, and corruption containment `
  + `(${assertions}/${assertions})`
);
