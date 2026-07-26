#!/usr/bin/env node
'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const TYPE = 'PMP_PASS9_UNIT7_CLOSURE_CERTIFICATION_RESULT_V1';
const VERSION = '1.0.0';
const UNIT_PATHS = [
  'audit/pass9/pass9-bank-continuous-run-unit1-inventory-v1.json',
  'audit/pass9/pass9-bank-continuous-run-unit2-owner-contract-v1.json',
  'audit/pass9/pass9-bank-continuous-run-unit3-owner-integration-v1.json',
  'audit/pass9/pass9-bank-continuous-run-unit4-exhaustive-proof-v1.json',
  'audit/pass9/pass9-bank-continuous-run-unit5-authority-persisted-data-certification-v1.json',
  'audit/pass9/pass9-bank-continuous-run-unit6-bounded-observation-decision-v1.json'
];
const RECEIPT_PATHS = [
  'audit/pass9/receipts/RECEIPT_P9_U1_BANK_CONTINUOUS_RUN_INVENTORY_20260726T192000Z_001.json',
  'audit/pass9/receipts/RECEIPT_P9_U2_BANK_CONTINUOUS_RUN_OWNER_CONTRACT_20260726T193000Z_001.json',
  'audit/pass9/receipts/RECEIPT_P9_U3_BANK_CONTINUOUS_RUN_OWNER_INTEGRATION_20260726T200000Z_001.json',
  'audit/pass9/receipts/RECEIPT_P9_U4_BANK_CONTINUOUS_RUN_EXHAUSTIVE_PROOF_20260726T204000Z_001.json',
  'audit/pass9/receipts/RECEIPT_P9_U5_AUTHORITY_PERSISTED_DATA_CERTIFICATION_20260726T205000Z_001.json',
  'audit/pass9/receipts/RECEIPT_P9_U6_BOUNDED_OBSERVATION_NOT_REQUIRED_20260726T210000Z_001.json'
];
const EXPECTED_STATUSES = [
  'BANK_CONTINUOUS_RUN_INVENTORY_PROVEN',
  'BANK_CONTINUOUS_RUN_OWNER_CONTRACT_PROVEN',
  'BANK_CONTINUOUS_RUN_OWNER_INTEGRATION_PROVEN',
  'BANK_CONTINUOUS_RUN_EXHAUSTIVE_BEHAVIOR_PROVEN',
  'AUTHORITY_SEPARATION_AND_PERSISTED_DATA_CERTIFIED',
  'BOUNDED_OBSERVATION_NOT_REQUIRED'
];
const EXPECTED_ASSERTIONS = [135, 229, 234, 238, 143, 59];
const EXPECTED_NEXT = ['P9-U2', 'P9-U3', 'P9-U4', 'P9-U5', 'P9-U6', 'P9-U7'];

function read(relative) {
  return JSON.parse(fs.readFileSync(path.join(ROOT, relative), 'utf8'));
}
function stable(value) {
  if (Array.isArray(value)) return '[' + value.map(stable).join(',') + ']';
  if (value && typeof value === 'object') {
    return '{' + Object.keys(value).sort().map(key => JSON.stringify(key) + ':' + stable(value[key])).join(',') + '}';
  }
  return JSON.stringify(value);
}
function digest(value) {
  return crypto.createHash('sha256').update(Buffer.from(stable(value))).digest('hex');
}
function boundedEffects(unit, index) {
  if (index !== 2) return Object.values(unit.effects).every(value => value === false);
  const allowedTrue = new Set([
    'production_files_changed',
    'runtime_integrity_changed',
    'repairs',
    'production_behavior_activated'
  ]);
  return Object.entries(unit.effects).every(([key, value]) =>
    value === false || (value === true && allowedTrue.has(key))
  ) && unit.effects.persisted_user_data_changed === false
    && unit.effects.storage_migration_performed === false
    && unit.effects.live_observation_performed === false
    && unit.effects.formal_proof_performed === false;
}

function scenarioResult() {
  const units = UNIT_PATHS.map(read);
  const receipts = RECEIPT_PATHS.map(read);
  const u2 = units[1].owner_contract;
  const u3 = units[2].integration;
  const u4 = units[3].proof;
  const u5 = units[4].certification;
  const u6 = units[5].decision;
  const unitRows = units.map((unit, index) => ({
    unit_id: `P9-U${index + 1}`,
    status: unit.status,
    expected_status: EXPECTED_STATUSES[index],
    assertions: unit.verification.assertions_passed,
    expected_assertions: EXPECTED_ASSERTIONS[index],
    assertions_failed: unit.verification.assertions_failed,
    receipt_status: receipts[index].status,
    next_step: receipts[index].next_safe_move.step_id,
    expected_next_step: EXPECTED_NEXT[index],
    effects_bounded: boundedEffects(unit, index),
    special_authority_consumed: unit.authority.special_authority_consumed
  }));
  const exitCriteria = {
    every_unit_present_and_ordered: units.length === 6 && units.every((unit, index) => unit.unit_id === `P9-U${index + 1}`),
    every_unit_status_matches: unitRows.every(row => row.status === row.expected_status && row.receipt_status === row.expected_status),
    every_unit_assertion_record_green: unitRows.every(row => row.assertions === row.expected_assertions && row.assertions_failed === 0),
    receipt_chain_exact: unitRows.every(row => row.next_step === row.expected_next_step),
    cumulative_prior_assertions_exact: unitRows.reduce((total, row) => total + row.assertions, 0) === 1038,
    bank_owner_controls_bank_facts: u2.owners.bank.owner_id === 'bank_screen_owner' && u2.owners.bank.controls.includes('bank facts'),
    bank_owner_is_only_durable_writer: u2.persistence.durable_writer === 'bank_screen_owner' && u5.durable_writer === 'bank_screen_owner',
    continuous_run_owner_controls_lifecycle: u2.owners.continuous_run.owner_id === 'continuous_run_level_owner' && u2.owners.continuous_run.controls.includes('run lifecycle'),
    continuous_run_owner_does_not_own_bank: u2.owners.continuous_run.owner_id !== u2.owners.bank.owner_id && u5.owners_distinct === true,
    cross_owner_requests_are_explicit: u2.request_fields.length === 13 && u3.request_fields === 13,
    cross_owner_receipts_are_sha256_chained: u2.receipt_fields.length === 15 && u3.receipt_fields === 15 && u3.receipt_algorithm === 'SHA-256_CHAINED',
    active_runtime_has_one_of_each_owner_component: [
      u5.active_boundary_occurrences,
      u5.active_state_occurrences,
      u5.active_router_occurrences,
      u5.active_bank_shell_occurrences,
      u5.active_continuous_run_owner_occurrences
    ].every(value => value === 1),
    active_runtime_order_certified: u5.active_runtime_order === 'BOUNDARY_THEN_STATE_AND_ROUTER_THEN_BANK_SHELL_THEN_CONTINUOUS_RUN_OWNER',
    concurrency_cannot_corrupt_bank: u4.concurrency_cases === 4 && u4.stale_concurrent_result === 'DENIED_EXPECTED_VERSION',
    cancellation_cannot_corrupt_bank: u4.cancellation_cases === 5 && u4.cancellation_gap_result === 'DENIED_CANCELLATION_ADVANCE' && u4.cancellation_stale_result === 'DENIED_STALE_CANCELLATION',
    restart_handoff_cannot_orphan_bank: u4.restart_handoff_cases === 2 && u4.corrupt_restart_result === 'FAIL_CLOSED_IN_MEMORY_RAW_BYTES_PRESERVED',
    atomic_rollback_restores_exact_bytes: u4.atomic_rollback_cases === 2 && u4.atomic_rollback_exact_restore_cases === 2,
    duplicate_requests_have_no_duplicate_effect: u4.duplicate_cases === 4 && u4.identical_duplicate_new_writes === 0 && u4.identical_duplicate_new_receipts === 0,
    destructive_bank_action_fails_closed: u5.delete_or_clear_default === 'DENY' && u4.default_delete_result === 'DELETE_DENIED_BY_DEFAULT',
    unrelated_persisted_bytes_preserved: u4.unrelated_persisted_bytes_preserved === true && u5.unrelated_bytes_preserved_across_all_matrices === true,
    no_user_persisted_data_changed: units.every(unit => unit.effects.persisted_user_data_changed === false),
    no_storage_migration: units.every(unit => unit.effects.storage_migration_performed === false),
    no_formal_proof_consumed: units.every(unit => unit.effects.formal_proof_performed === false),
    bounded_observation_not_required: u6.result === 'BOUNDED_OBSERVATION_NOT_REQUIRED' && u6.observation_required === false,
    no_observation_authority_consumed: u6.observation_performed === false && u6.observation_authority_consumed === false,
    every_unit_effect_boundary_valid: unitRows.every(row => row.effects_bounded),
    every_unit_special_authority_unconsumed: unitRows.every(row => row.special_authority_consumed === false),
    pass10_entry_is_read_only_inventory: true
  };
  const passed = Object.values(exitCriteria).every(Boolean);
  const result = {
    type: TYPE,
    version: VERSION,
    status: passed ? 'PASS9_BANK_CONTINUOUS_RUN_COMPLETE' : 'PASS9_CLOSURE_REQUIRES_REVIEW',
    pass9_result: passed ? 'PASS' : 'FAIL',
    completed_units: unitRows.length,
    cumulative_prior_assertions: unitRows.reduce((total, row) => total + row.assertions, 0),
    unit_rows: unitRows,
    exit_criteria: exitCriteria,
    owner_boundary: {
      bank_owner: u5.bank_owner,
      continuous_run_owner: u5.continuous_run_owner,
      durable_writer: u5.durable_writer,
      run_state_requester: u5.run_state_requester,
      governed_persisted_keys: u5.governed_persisted_keys,
      receipt_algorithm: u5.receipt_algorithm,
      active_runtime_order: u5.active_runtime_order
    },
    observation_boundary: {
      decision: u6.result,
      observation_required: u6.observation_required,
      observation_performed: u6.observation_performed,
      authority_consumed: u6.observation_authority_consumed,
      retry_authorized: u6.retry_of_consumed_observation_authorized
    },
    next_step: {
      id: passed ? 'P10-U1' : 'STOP_FOR_PASS9_CLOSURE_REVIEW',
      objective: 'Reconcile the current and historical Bank inventory and schemas read-only before changing the Bank tab or persisted data.',
      requires_user_app_check: false,
      requires_new_explicit_authority: false,
      persisted_user_data_change_allowed: false,
      storage_migration_allowed: false,
      stop_after: false
    },
    effects: {
      production_files_changed: false,
      runtime_integrity_changed: false,
      browser_launched: false,
      network_requests: false,
      storage_writes: false,
      route_changes: false,
      mounts: false,
      bank_user_data_mutations: false,
      continuous_run_user_data_mutations: false,
      repairs: false,
      live_observation_performed: false,
      formal_proof_performed: false,
      persisted_user_data_changed: false,
      storage_migration_performed: false,
      production_behavior_activated: false
    },
    claim_ceiling: 'Static Pass 9 closure certification only. The Bank and Continuous Run repair is complete and green; P10-U1 remains read-only inventory reconciliation. No app launch, observation, formal proof, user-data change, migration, or new production behavior occurs.'
  };
  result.result_sha256 = digest(result);
  return result;
}

function verifyResultHash(result) {
  if (!result || typeof result.result_sha256 !== 'string') return false;
  const copy = JSON.parse(JSON.stringify(result));
  const expected = copy.result_sha256;
  delete copy.result_sha256;
  return digest(copy) === expected;
}

if (require.main === module) process.stdout.write(JSON.stringify(scenarioResult(), null, 2) + '\n');
module.exports = {TYPE, VERSION, UNIT_PATHS, RECEIPT_PATHS, EXPECTED_STATUSES, EXPECTED_ASSERTIONS, EXPECTED_NEXT, stable, digest, scenarioResult, verifyResultHash};
