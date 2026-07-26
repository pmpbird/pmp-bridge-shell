#!/usr/bin/env node
'use strict';

const assert = require('assert');
const runner = require(
  './run_pass10_unit6_bank_reversible_migration_rehearsal_v1.js'
);

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
  'BANK_REVERSIBLE_MIGRATION_REHEARSAL_PROVEN',
  'result status'
);
equal(runner.verifyResultHash(result), true, 'result hash');

equal(
  result.authority.target,
  'DISPOSABLE_FIXTURE_STAGING_ONLY',
  'disposable target'
);
equal(result.authority.production_migration_allowed, false, 'production denied');
equal(result.authority.persisted_user_data_change_allowed, false, 'user data denied');
equal(result.authority.special_authority_required, false, 'no special authority');
equal(result.authority.special_authority_consumed, false, 'no authority consumed');

const preflight = result.preflight;
equal(preflight.contract_status, 'BANK_INVENTORY_CONTRACT_PROVEN', 'contract green');
equal(
  preflight.unit5_status,
  'BANK_FAULT_ROLLBACK_AND_CORRUPTION_CONTAINMENT_PROVEN',
  'U5 green'
);
equal(preflight.unit5_unresolved_failures, 0, 'U5 zero failures');
equal(preflight.plan_valid, true, 'plan valid');
check(/^[0-9a-f]{64}$/.test(preflight.plan_sha256), 'plan sha');
check(/^[0-9a-f]{64}$/.test(preflight.source_digest), 'source sha');
equal(preflight.source_namespaces, 5, 'five source namespaces');
equal(preflight.source_bytes_preserved, 4, 'four present exact-byte sources');
equal(preflight.plan_changed_source_workspace, false, 'planning read only');
check(/^[0-9a-f]{64}$/.test(preflight.baseline_digest), 'baseline sha');

const mapping = result.forward_mapping;
equal(mapping.items, 8, 'eight planned items');
equal(mapping.active, 2, 'two active items');
equal(mapping.reference_only, 1, 'one historic reference');
equal(mapping.quarantined, 4, 'four quarantine items');
equal(mapping.unavailable, 1, 'one unavailable item');
equal(mapping.stable_identities, true, 'stable identities');
equal(mapping.provenance_complete, true, 'provenance complete');
equal(mapping.delete_authority_denied, true, 'delete denied all');
equal(mapping.collision_rows, 2, 'two collision rows');
equal(mapping.collision_quarantined, true, 'collisions quarantine');
equal(mapping.collision_payloads_preserved, 2, 'collision payloads preserved');
equal(mapping.orphan_rows, 1, 'one orphan');
equal(mapping.orphan_quarantined, true, 'orphan quarantine');
equal(mapping.corrupt_rows, 1, 'one corrupt');
equal(mapping.corrupt_quarantined, true, 'corrupt quarantine');
equal(mapping.unavailable_rows, 1, 'one unavailable');
equal(mapping.unavailable_preserved, true, 'unavailable preserved');
equal(mapping.historic_rows, 1, 'one historic');
equal(mapping.historic_reference_only, true, 'historic reference only');

const apply = result.disposable_apply;
equal(apply.code, 'DISPOSABLE_STAGING_APPLIED', 'apply code');
equal(apply.changed_writes, 9, 'eight items plus manifest');
equal(apply.deletes, 0, 'apply no deletes');
equal(apply.receipt_valid, true, 'receipt valid');
equal(
  apply.receipt_target,
  'DISPOSABLE_FIXTURE_STAGING_ONLY',
  'receipt target'
);
equal(apply.staging_entries, 9, 'nine staged entries');
equal(apply.source_bytes_unchanged, true, 'apply source unchanged');
equal(apply.unrelated_bytes_unchanged, true, 'apply unrelated unchanged');

const idempotence = result.idempotence;
equal(idempotence.code, 'ALREADY_APPLIED', 'idempotent code');
equal(idempotence.changed_writes, 0, 'idempotent zero writes');
equal(idempotence.deletes, 0, 'idempotent zero deletes');
equal(idempotence.state_unchanged, true, 'idempotent state');
equal(idempotence.plan_sha256_unchanged, true, 'idempotent plan');

const interruption = result.interruption_recovery;
equal(
  interruption.code,
  'DENIED_INTERRUPTED_ROLLED_BACK',
  'interruption code'
);
equal(interruption.writes_attempted, 3, 'three fixture writes before interruption');
equal(interruption.deletes, 0, 'interruption no declared deletes');
equal(interruption.rollback_completed, true, 'interruption rollback');
equal(interruption.exact_baseline_restored, true, 'interruption exact baseline');
equal(interruption.staging_entries_after, 0, 'interruption no staging');
equal(interruption.receipt_emitted, false, 'interruption no receipt');

const rollback = result.explicit_rollback;
equal(rollback.exact_baseline_restored, true, 'explicit exact rollback');
equal(rollback.staging_entries_after, 0, 'explicit no staging');
equal(rollback.source_bytes_unchanged, true, 'explicit sources unchanged');
equal(rollback.unrelated_bytes_unchanged, true, 'explicit unrelated unchanged');

const denial = result.denial_matrix;
equal(denial.production_code, 'DENIED_PRODUCTION_TARGET', 'production denied');
equal(denial.production_zero_effect, true, 'production zero effect');
equal(
  denial.source_tamper_code,
  'DENIED_SOURCE_PREIMAGE_CHANGED',
  'source tamper denied'
);
equal(denial.source_tamper_zero_effect, true, 'source tamper zero effect');
equal(denial.plan_tamper_code, 'DENIED_PLAN_INTEGRITY', 'plan tamper denied');
equal(denial.plan_tamper_zero_effect, true, 'plan tamper zero effect');
equal(denial.deletes_across_denials, 0, 'denials no deletes');

const decision = result.observation_decision_input;
equal(decision.rehearsal_failures, 0, 'zero rehearsal failures');
equal(decision.production_migration_performed, false, 'no production migration');
equal(decision.real_user_storage_accessed, false, 'no user storage');
equal(decision.user_app_check_required_now, false, 'no app check now');
equal(decision.bounded_observation_performed, false, 'no observation');
equal(decision.bounded_observation_authority_consumed, false, 'no authority');
equal(decision.pass10_closure_unit_ready, true, 'closure ready');

equal(result.effects.production_files_changed, false, 'no production files');
equal(result.effects.runtime_integrity_changed, false, 'no integrity change');
equal(result.effects.browser_launched, false, 'no browser');
equal(result.effects.network_requests, false, 'no network');
equal(result.effects.disposable_fixture_writes_performed, true, 'fixture writes');
equal(result.effects.disposable_fixture_rollback_completed, true, 'fixture rollback');
equal(result.effects.real_user_storage_reads, false, 'no user reads');
equal(result.effects.real_user_storage_writes, false, 'no user writes');
equal(result.effects.real_user_storage_deletes, false, 'no user deletes');
equal(result.effects.persisted_user_data_changed, false, 'no persisted change');
equal(result.effects.production_migration_performed, false, 'no production migration');
equal(result.effects.live_observation_performed, false, 'no live observation');
equal(result.effects.formal_proof_performed, false, 'no formal proof');
equal(result.effects.production_behavior_activated, false, 'no production activation');

equal(result.next_step.id, 'P10-U7', 'next U7');
equal(
  result.next_step.requires_user_app_check_before_decision,
  false,
  'no check before U7 decision'
);
equal(result.next_step.perform_observation_automatically, false, 'no auto observation');
equal(result.next_step.requires_new_explicit_authority, false, 'no new authority');
equal(result.next_step.persisted_user_data_change_allowed, false, 'U7 no data');
equal(result.next_step.production_migration_allowed, false, 'U7 no migration');
equal(result.next_step.stop_after, false, 'continue after U6');
check(result.claim_ceiling.includes('disposable in-memory'), 'claim disposable');
check(result.claim_ceiling.includes('No production migration'), 'claim no production');
check(result.claim_ceiling.includes('real user storage'), 'claim no user storage');
check(result.claim_ceiling.includes('live observation'), 'claim no observation');
check(result.claim_ceiling.includes('formal proof'), 'claim no formal proof');

console.log(
  `PASS: P10-U6 Bank reversible migration rehearsal `
  + `(${assertions}/${assertions})`
);
