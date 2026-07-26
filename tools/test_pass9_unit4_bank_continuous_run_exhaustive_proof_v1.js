#!/usr/bin/env node
'use strict';

const assert = require('assert');
const runner = require('./run_pass9_unit4_bank_continuous_run_exhaustive_proof_v1.js');

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
equal(result.status, 'PASS', 'result status');
equal(runner.verifyResultHash(result), true, 'result SHA-256');

const boot = result.boot_repeated_load;
equal(boot.exact_bytes_before_sha256, boot.exact_bytes_after_first_sha256, 'first load exact bytes');
equal(boot.exact_bytes_before_sha256, boot.exact_bytes_after_second_sha256, 'repeated load exact bytes');
equal(boot.first_calls, {get: 0, set: 0, remove: 0}, 'first load zero storage calls');
equal(boot.second_calls, {get: 0, set: 0, remove: 0}, 'repeated load zero storage calls');
equal(boot.first_owner_pair, ['bank_screen_owner', 'continuous_run_level_owner'], 'first exact owners');
equal(boot.second_owner_pair, boot.first_owner_pair, 'repeated exact owners');
equal(boot.first_receipt_count, 0, 'first load no receipt');
equal(boot.second_receipt_count, 0, 'repeated load no receipt');
equal(boot.diagnostic_loaded, true, 'diagnostic loads');
equal(boot.diagnostic_keys_written_automatically, [], 'diagnostic not automatic');
equal(boot.boundary_ready_events, 2, 'one readiness event per explicit load');
equal(boot.persisted_user_data_changed, false, 'repeated load preserves data');

const concurrency = result.concurrency;
equal(concurrency.first_code, 'COMMITTED', 'first writer wins');
equal(concurrency.competing_code, 'DENIED_EXPECTED_VERSION', 'stale concurrent writer denied');
equal(concurrency.competing_zero_effects, true, 'stale concurrent zero effects');
equal(concurrency.retry_code, 'COMMITTED', 'fresh expected version accepted');
equal(concurrency.independent_resource_code, 'COMMITTED', 'independent resource accepted');
equal(concurrency.run_resource_version, 2, 'run resource version two');
equal(concurrency.project_resource_version, 1, 'project resource version one');
equal(concurrency.persisted_winner_after_retry, 'competing', 'retry payload wins only after new version');
equal(concurrency.unrelated_exactly_preserved, true, 'concurrency preserves unrelated');
equal(concurrency.receipt_count, 3, 'three accepted concurrency receipts');
equal(concurrency.receipt_chain_valid, true, 'concurrency receipt chain valid');
equal(concurrency.commit_events, 3, 'one event per accepted commit');

const cancellation = result.cancellation;
equal(cancellation.initial_code, 'COMMITTED', 'initial epoch accepted');
equal(cancellation.gap_code, 'DENIED_CANCELLATION_ADVANCE', 'epoch gap denied');
equal(cancellation.gap_zero_effects, true, 'epoch gap zero effects');
equal(cancellation.advance_code, 'COMMITTED', 'next epoch accepted');
equal(cancellation.stale_code, 'DENIED_STALE_CANCELLATION', 'stale epoch denied');
equal(cancellation.stale_zero_effects, true, 'stale epoch zero effects');
equal(cancellation.same_epoch_code, 'COMMITTED', 'same current epoch may advance version');
equal(cancellation.final_epoch, 1, 'final cancellation epoch one');
equal(cancellation.final_version, 3, 'three accepted cancellation writes');
equal(cancellation.final_value, 'same-epoch', 'last accepted value');
equal(cancellation.storage_deletes, 0, 'cancellation never deletes');

const duplicate = result.duplicate;
equal(duplicate.accepted_code, 'COMMITTED', 'duplicate seed accepted');
equal(duplicate.identical_replay_equal, true, 'identical duplicate result exact');
equal(duplicate.replay_new_writes, 0, 'identical replay no write');
equal(duplicate.replay_new_receipts, 0, 'identical replay no receipt');
equal(duplicate.conflict_code, 'DENIED_DUPLICATE_CONFLICT', 'duplicate conflict denied');
equal(duplicate.conflict_zero_effects, true, 'duplicate conflict no effect');
equal(duplicate.denied_code, 'DENIED_EXPECTED_VERSION', 'denied operation seeded');
equal(duplicate.denied_replay_equal, true, 'denied duplicate replay exact');
equal(duplicate.denied_replay_new_writes, 0, 'denied replay no write');
equal(duplicate.final_version, 1, 'duplicate matrix version one');

const denial = result.denial;
equal(denial.authorize_cases.length, 16, 'sixteen authorization denials');
for (const row of denial.authorize_cases) {
  equal(row.code, row.expected, `authorization denial ${row.fault}`);
  equal(row.writes, 0, `authorization denial writes ${row.fault}`);
  equal(row.deletes, 0, `authorization denial deletes ${row.fault}`);
}
equal(denial.commit_cases.length, 4, 'four commit denials in primary storage');
for (const row of denial.commit_cases) {
  equal(row.code, row.expected, `commit denial ${row.fault}`);
  equal(row.writes, 0, `commit denial writes ${row.fault}`);
  equal(row.deletes, 0, `commit denial deletes ${row.fault}`);
}
equal(denial.storage_unavailable_code, 'DENIED_STORAGE_UNAVAILABLE', 'storage unavailable denied');
equal(denial.all_codes_exact, true, 'all denial codes exact');
equal(denial.all_denials_zero_effect, true, 'all denials zero reported effect');
equal(denial.persisted_bytes_unchanged, true, 'denials preserve all persisted bytes');
equal(denial.unrelated_exactly_preserved, true, 'denials preserve unrelated');
equal(denial.manual_delete_absent, false, 'delete absent authority');
equal(denial.manual_delete_wrong_confirmation, false, 'delete wrong confirmation');
equal(denial.manual_delete_wrong_capability, false, 'delete wrong capability');
equal(denial.manual_delete_exact, true, 'delete exact authority');

const rollback = result.atomic_rollback;
equal(rollback.existing_keys_code, 'DENIED_ATOMIC_WRITE_FAILED', 'rollback existing code');
equal(rollback.existing_keys_exact_restore, true, 'rollback existing exact restore');
equal(rollback.existing_keys_version, 0, 'rollback existing version unchanged');
equal(rollback.new_key_code, 'DENIED_ATOMIC_WRITE_FAILED', 'rollback new key code');
equal(rollback.absent_key_remains_absent, true, 'rollback restores absent key');
equal(rollback.new_key_exact_restore, true, 'rollback new key exact restore');
equal(rollback.new_key_version, 0, 'rollback new key version unchanged');
equal(rollback.unrelated_exactly_preserved, true, 'rollback unrelated exact');

const restart = result.restart_handoff;
equal(restart.first_codes, ['COMMITTED', 'COMMITTED', 'COMMITTED', 'COMMITTED'], 'handoff writes accepted');
equal(restart.handoff_pack_type, 'PMP_CONTINUOUS_WORK_ENGINE_RESUME_PACK_V1', 'handoff pack type');
equal(restart.handoff_owner, 'continuous_run_level_owner', 'handoff owner');
check(/^[0-9a-f]{64}$/.test(restart.handoff_state_sha256), 'handoff state digest');
check(restart.handoff_receipts >= 5, 'handoff receipt history');
equal(restart.restart_load_reads, 0, 'restart load no reads');
equal(restart.restart_load_writes, 0, 'restart load no writes');
equal(restart.restart_load_deletes, 0, 'restart load no deletes');
equal(restart.persisted_bytes_unchanged_by_restart_load, true, 'restart load exact bytes');
equal(restart.restored_area, 'pass9-bank-repair', 'restart area');
equal(restart.restored_item, 'p9-u4-proof', 'restart item');
equal(restart.restored_queue, ['proof', 'closure'], 'restart queue');
equal(restart.restored_status, 'stopped', 'restart status');
equal(restart.restored_stop_reason, 'bounded-handoff', 'restart stop reason');
equal(restart.restored_receipts, restart.handoff_receipts, 'restart exact receipt count');
equal(restart.export_after_restart_writes, 0, 'restart export read-only');
equal(restart.export_after_restart_type, restart.handoff_pack_type, 'restart pack type stable');
equal(restart.resume_code, 'COMMITTED', 'resume accepted');
equal(restart.resume_changed_bytes, true, 'resume explicit change');
equal(restart.final_status, 'resumed', 'resume state');
equal(restart.final_stop_reason, '', 'resume clears stop reason');
equal(restart.final_context_status, 'resume_recorded', 'resume context');
equal(restart.second_boundary_version_after_resume, 1, 'fresh boundary version after one resume');
equal(restart.corrupted_read_fails_closed_in_memory, true, 'corrupt restart fallback in memory');
equal(restart.corrupted_raw_bytes_preserved, true, 'corrupt raw bytes preserved');
equal(restart.corrupted_read_storage_writes, 0, 'corrupt read no writes');
equal(restart.unrelated_exactly_preserved, true, 'restart unrelated exact');

const router = result.router_diagnostics;
equal(router.read_inventory_present, true, 'router inventory read');
equal(router.read_route_count, 1, 'router historic route read');
equal(router.read_helper_count, 1, 'router historic helper read');
equal(router.read_path_writes, 0, 'router reads no writes');
equal(router.read_path_deletes, 0, 'router reads no deletes');
equal(router.default_delete_code, 'DELETE_DENIED_BY_DEFAULT', 'router default delete denied');
equal(router.default_delete_zero_effect, true, 'router default delete zero effect');
equal(router.write_code, 'COMMITTED', 'router exact write');
equal(router.write_record_present, true, 'router write present');
equal(router.wrong_delete_code, 'DELETE_DENIED_BY_DEFAULT', 'router wrong delete denied');
equal(router.wrong_delete_zero_effect, true, 'router wrong delete zero effect');
equal(router.exact_delete_code, 'COMMITTED', 'router exact delete accepted');
equal(router.exact_delete_record_absent, true, 'router exact delete removes fixture record');
equal(router.diagnostic_status, 'READY', 'diagnostic boundary ready');
equal(router.diagnostic_owner_pair, ['bank_screen_owner', 'continuous_run_level_owner'], 'diagnostic exact owners');
equal(router.diagnostic_reads, 0, 'diagnostic snapshot no storage read');
equal(router.diagnostic_writes, 0, 'diagnostic snapshot no storage write');
equal(router.diagnostic_deletes, 0, 'diagnostic snapshot no storage delete');
equal(router.diagnostic_report_auto_written, false, 'diagnostic no automatic report');
equal(router.unrelated_exactly_preserved, true, 'router unrelated exact');
equal(router.boundary_version, '1.0.0-pass9-unit3-owner-boundary-20260726A', 'boundary exact version');

const bounded = result.bounded_receipts;
equal(bounded.commits, 260, 'bounded commit count');
equal(bounded.receipt_count, 256, 'bounded internal receipt count');
equal(bounded.visible_receipts, 32, 'bounded diagnostic receipt window');
equal(bounded.final_version, 260, 'bounded final resource version');
equal(bounded.first_visible_operation, 'op:p9u4:bounded:228', 'bounded first visible');
equal(bounded.last_visible_operation, 'op:p9u4:bounded:259', 'bounded last visible');
equal(bounded.first_previous_is_historic_hash, true, 'bounded window chains to hidden history');
equal(bounded.visible_chain_valid, true, 'bounded visible chain valid');
equal(bounded.storage_deletes, 0, 'bounded commits never delete');
equal(bounded.unrelated_exactly_preserved, true, 'bounded unrelated exact');

equal(Object.keys(result.source_policy.policies).length, 14, 'fourteen source policies');
for (const [name, value] of Object.entries(result.source_policy.policies)) {
  equal(value, true, `source policy ${name}`);
}
equal(result.source_policy.all_pass, true, 'all source policies pass');
for (const [name, value] of Object.entries(result.source_policy.source_sha256)) {
  check(/^[0-9a-f]{64}$/.test(value), `source digest ${name}`);
}

equal(result.coverage.concurrency_cases, 4, 'coverage concurrency');
equal(result.coverage.cancellation_cases, 5, 'coverage cancellation');
equal(result.coverage.duplicate_cases, 4, 'coverage duplicate');
equal(result.coverage.authorization_denial_cases, 16, 'coverage authorization denial');
equal(result.coverage.commit_denial_cases, 5, 'coverage commit denial');
equal(result.coverage.rollback_cases, 2, 'coverage rollback');
equal(result.coverage.restart_handoff_cases, 2, 'coverage restart handoff');
equal(result.coverage.router_delete_cases, 3, 'coverage router delete');
equal(result.coverage.bounded_receipt_commits, 260, 'coverage bounded receipts');
equal(result.coverage.source_policy_checks, 14, 'coverage source policies');

for (const [key, value] of Object.entries(result.effects)) {
  equal(value, false, `external effect false ${key}`);
}
check(result.claim_ceiling.includes('in-memory fixtures'), 'fixture claim ceiling');
check(result.claim_ceiling.includes('No user persisted data'), 'user-data claim ceiling');
check(result.claim_ceiling.includes('scarce live observation'), 'observation claim ceiling');
check(result.claim_ceiling.includes('formal proof'), 'formal-proof claim ceiling');

console.log(`PASS: P9-U4 Bank/Continuous Run exhaustive concurrency, cancellation, restart, handoff, duplicate, denial, diagnostics, and preserved-data proof (${assertions}/${assertions})`);
