#!/usr/bin/env node
'use strict';

const assert = require('assert');
const runner = require('./run_pass9_unit5_authority_persisted_data_certification_v1.js');

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
equal(result.status, 'AUTHORITY_SEPARATION_AND_PERSISTED_DATA_CERTIFIED', 'result status');
equal(runner.verifyResultHash(result), true, 'result hash');

const chain = result.evidence_chain;
equal(chain.units.length, 4, 'four completed evidence units');
equal(chain.units.map(row => row.unit), ['P9-U1', 'P9-U2', 'P9-U3', 'P9-U4'], 'unit order');
equal(chain.units.map(row => row.status), [
  'BANK_CONTINUOUS_RUN_INVENTORY_PROVEN',
  'BANK_CONTINUOUS_RUN_OWNER_CONTRACT_PROVEN',
  'BANK_CONTINUOUS_RUN_OWNER_INTEGRATION_PROVEN',
  'BANK_CONTINUOUS_RUN_EXHAUSTIVE_BEHAVIOR_PROVEN'
], 'unit statuses');
equal(chain.exact_progression, ['P9-U2', 'P9-U3', 'P9-U4', 'P9-U5'], 'receipt next-move chain');
equal(chain.inventory_conflicts_identified, 9, 'nine original conflicts');
equal(chain.unit1_assertions, 135, 'unit1 assertions');
equal(chain.unit2_assertions, 229, 'unit2 assertions');
equal(chain.unit3_assertions, 234, 'unit3 assertions');
equal(chain.unit4_assertions, 238, 'unit4 assertions');
equal(chain.cumulative_assertions, 836, 'cumulative assertions');
equal(chain.all_permanent_gates_bound, true, 'all units permanent-gate bound');

const authority = result.authority_separation;
equal(authority.contract_model, 'SEPARATE_OWNERS_FAIL_CLOSED_REQUEST_RECEIPT', 'contract model');
equal(authority.bank_owner, runner.BANK_OWNER, 'contract Bank owner');
equal(authority.continuous_run_owner, runner.RUN_OWNER, 'contract Run owner');
equal(authority.owners_distinct, true, 'owners distinct');
equal(authority.durable_writer, runner.BANK_OWNER, 'Bank durable writer');
equal(authority.run_state_requester, runner.RUN_OWNER, 'Run requester');
equal(authority.bank_resource_prefix, 'bank:', 'Bank resource prefix');
equal(authority.continuous_run_resource_prefix, 'continuous_run:', 'Run resource prefix');
equal(authority.request_fields, 13, 'request fields');
equal(authority.receipt_fields, 15, 'receipt fields');
equal(authority.receipt_algorithm, 'SHA-256', 'receipt algorithm');
equal(authority.append_only_receipt_chain, true, 'append-only receipt chain');
equal(authority.active_tab_conveys_ownership, false, 'tab no ownership');
equal(authority.filename_conveys_authority, false, 'filename no authority');
equal(authority.copied_cross_frame_apis_convey_authority, false, 'copied API no authority');
equal(authority.delete_or_clear_default, 'DENY', 'default delete deny');
equal(authority.storage_migration_contract, 'FORBIDDEN_IN_P9_U2_AND_P9_U3', 'migration contract');
equal(authority.integration_model, 'SEPARATE_OWNERS_ATOMIC_BANK_COMMIT_EVENT_DRIVEN_RENDER', 'integration model');
equal(authority.integration_bank_owner, runner.BANK_OWNER, 'integration Bank owner');
equal(authority.integration_continuous_run_owner, runner.RUN_OWNER, 'integration Run owner');
equal(authority.integration_receipt_algorithm, 'SHA-256_CHAINED', 'integration receipt chain');
equal(authority.owner_boundary_exact_ids_in_source, true, 'source exact owner IDs');
equal(authority.boundary_only_durable_writer_rule, true, 'boundary only writer rule');
equal(authority.state_requests_bank_commits, true, 'state requests Bank');
equal(authority.router_uses_internal_bank_capability, true, 'router internal Bank capability');
equal(authority.dependency_bridge_copies_mutable_apis, false, 'bridge no copied APIs');
equal(authority.runtime_owner_api_alias_is_identity_only, true, 'legacy alias points to same Run owner API');
equal(authority.bank_shell_open_calls_record_write, false, 'Bank opening read-only');

const persisted = result.persisted_data;
equal(persisted.bank_keys, runner.BANK_KEYS, 'exact Bank keys');
equal(persisted.continuous_run_keys, runner.RUN_KEYS, 'exact Run keys');
equal(persisted.total_governed_keys, 9, 'nine governed keys');
equal(persisted.keys_unique, true, 'governed keys unique');
equal(persisted.contract_preserved_existing_keys, runner.RUN_KEYS.slice(0, 3), 'contract existing keys');
equal(persisted.integration_preserved_existing_keys, runner.RUN_KEYS.slice(0, 3), 'integration existing keys');
equal(persisted.boundary_bank_keys_bound, true, 'Bank keys bound');
equal(persisted.boundary_run_keys_bound, true, 'Run keys bound');
equal(persisted.state_direct_local_storage_writes, 0, 'state no direct writes');
equal(persisted.state_direct_local_storage_deletes, 0, 'state no direct deletes');
equal(persisted.router_direct_local_storage_writes, 0, 'router no direct writes');
equal(persisted.connection_delete_direct_local_storage_writes, 0, 'Connections delete no direct writes');
equal(persisted.boundary_load_reads, 0, 'integration load reads');
equal(persisted.boundary_load_writes, 0, 'integration load writes');
equal(persisted.boundary_load_deletes, 0, 'integration load deletes');
equal(persisted.first_core_load_calls, {get: 0, set: 0, remove: 0}, 'first core load zero');
equal(persisted.repeated_core_load_calls, {get: 0, set: 0, remove: 0}, 'repeat core load zero');
equal(persisted.repeated_load_changed_data, false, 'repeat load preserves');
equal(persisted.stale_concurrency_zero_effects, true, 'stale concurrency preserves');
equal(persisted.cancellation_gap_zero_effects, true, 'cancellation gap preserves');
equal(persisted.cancellation_stale_zero_effects, true, 'stale cancellation preserves');
equal(persisted.duplicate_conflict_zero_effects, true, 'duplicate conflict preserves');
equal(persisted.all_denials_zero_effect, true, 'denials preserve');
equal(persisted.denial_bytes_unchanged, true, 'denial exact bytes');
equal(persisted.existing_key_rollback_exact, true, 'existing rollback exact');
equal(persisted.absent_key_rollback_exact, true, 'absent rollback exact');
equal(persisted.restart_load_changed_data, false, 'restart load preserves');
equal(persisted.corrupt_restart_raw_bytes_preserved, true, 'corrupt restart raw preserved');
equal(persisted.router_default_delete_zero_effect, true, 'default delete preserves');
equal(persisted.router_wrong_delete_zero_effect, true, 'wrong delete preserves');
equal(persisted.bounded_receipt_chain_valid, true, 'bounded chain valid');
equal(persisted.bounded_receipts_retained, 256, 'receipt bound');
equal(persisted.unrelated_bytes_preserved_across_all_matrices, true, 'unrelated exact bytes all matrices');
equal(persisted.user_persisted_data_touched, false, 'user data untouched');
equal(persisted.storage_migration_performed, false, 'no migration');

const active = result.active_runtime;
check(active.boundary_position > 0, 'boundary active');
check(active.boundary_position < active.state_position, 'boundary before state');
check(active.boundary_position < active.router_position, 'boundary before router');
check(active.state_position < active.bank_shell_position, 'state before shell');
check(active.router_position < active.bank_shell_position, 'router before shell');
check(active.bank_shell_position < active.continuous_owner_position, 'shell before Run owner');
equal(active.exact_order, true, 'exact active order');
equal(active.boundary_occurrences, 1, 'one boundary');
equal(active.state_occurrences, 1, 'one state');
equal(active.router_occurrences, 1, 'one router');
equal(active.bank_shell_occurrences, 1, 'one Bank shell');
equal(active.continuous_owner_occurrences, 1, 'one Run owner');
equal(active.legacy_mode_occurrences, 0, 'legacy mode excluded');
equal(active.legacy_cleaner_occurrences, 0, 'legacy cleaner excluded');
equal(active.master_recurring_painter, false, 'no master interval');
equal(active.continuous_owner_recurring_painter, false, 'no owner interval');
equal(active.loader_recurring_scan, false, 'no loader interval');
equal(active.loader_event_driven_mode, true, 'loader event driven');
equal(active.diagnostic_automatic_run, false, 'diagnostic manual');
equal(active.diagnostic_reads_boundary, true, 'diagnostic boundary');
equal(active.diagnostic_reports_sha_chain, true, 'diagnostic SHA report');

const deletion = result.deletion_authority;
equal(deletion.default, 'DENY', 'delete default');
equal(deletion.router_requires_user_confirmation, true, 'router confirmation');
equal(deletion.connections_exact_capability, true, 'Connections exact capability');
equal(deletion.connections_routes_final_index_through_owner, true, 'Connections owner routing');
equal(deletion.connections_opens_indexeddb_only_after_owner_commit, true, 'IDB only after owner');
equal(deletion.no_recurring_delete_timer, true, 'no recurring delete');
equal(deletion.default_delete_result, 'DELETE_DENIED_BY_DEFAULT', 'default delete result');
equal(deletion.wrong_capability_result, 'DELETE_DENIED_BY_DEFAULT', 'wrong capability result');
equal(deletion.exact_confirmed_result, 'COMMITTED', 'exact delete result');

const receipts = result.receipt_diagnostics;
equal(receipts.exact_request_field_count, 13, 'diagnostic request count');
equal(receipts.exact_receipt_field_count, 15, 'diagnostic receipt count');
equal(new Set(receipts.request_fields).size, 13, 'request fields unique');
equal(new Set(receipts.receipt_fields).size, 15, 'receipt fields unique');
equal(receipts.production_chain_valid_in_unit4, true, 'production chain');
equal(receipts.bounded_chain_valid_in_unit4, true, 'bounded chain');
equal(receipts.retained_receipts, 256, 'retained receipts');
equal(receipts.visible_receipts, 32, 'visible receipts');
equal(receipts.diagnostic_snapshot_status, 'READY', 'diagnostic ready');
equal(receipts.diagnostic_snapshot_writes, 0, 'diagnostic zero writes');
equal(receipts.diagnostic_snapshot_deletes, 0, 'diagnostic zero deletes');

for (const [key, value] of Object.entries(result.effects)) {
  equal(value, false, `effect false ${key}`);
}
equal(result.next_decision.id, 'P9-U6', 'next P9-U6');
equal(result.next_decision.requires_user_app_check_before_decision, false, 'no check before decision');
equal(result.next_decision.requires_new_explicit_authority_before_decision, false, 'no authority before decision');
equal(result.next_decision.perform_observation_automatically, false, 'no automatic observation');
check(result.claim_ceiling.includes('static and deterministic'), 'claim static');
check(result.claim_ceiling.includes('No production source'), 'claim no production');
check(result.claim_ceiling.includes('user persisted data'), 'claim user data');
check(result.claim_ceiling.includes('scarce live observation'), 'claim observation');
check(result.claim_ceiling.includes('formal proof'), 'claim formal proof');

console.log(`PASS: P9-U5 Bank/Continuous Run authority separation and persisted-data certification (${assertions}/${assertions})`);
