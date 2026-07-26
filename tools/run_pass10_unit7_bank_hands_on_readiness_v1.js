#!/usr/bin/env node
'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const TYPE = 'PMP_PASS10_UNIT7_BANK_HANDS_ON_READINESS_RESULT_V1';
const VERSION = '1.0.0';
const UNIT_PATHS = [
  'audit/pass10/pass10-bank-unit1-inventory-reconciliation-v1.json',
  'audit/pass10/pass10-bank-unit2-inventory-contract-v1.json',
  'audit/pass10/pass10-bank-unit3-readonly-projection-v1.json',
  'audit/pass10/pass10-bank-unit4-owner-projection-refresh-v1.json',
  'audit/pass10/pass10-bank-unit5-fault-corruption-proof-v1.json',
  'audit/pass10/pass10-bank-unit6-reversible-migration-rehearsal-v1.json'
];
const EXPECTED_STATUSES = [
  'BANK_INVENTORY_RECONCILIATION_PROVEN',
  'BANK_INVENTORY_CONTRACT_PROVEN',
  'BANK_READONLY_PROJECTION_PROVEN',
  'BANK_OWNER_PROJECTION_REFRESH_PROVEN',
  'BANK_FAULT_ROLLBACK_AND_CORRUPTION_CONTAINMENT_PROVEN',
  'BANK_REVERSIBLE_MIGRATION_REHEARSAL_PROVEN'
];
const EXPECTED_ASSERTIONS = [110, 187, 125, 121, 133, 102];

function read(name) {
  return JSON.parse(fs.readFileSync(path.join(ROOT, name), 'utf8'));
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
function assertionsFor(unit, index) {
  if (index === 3) return unit.deterministic_matrix.assertions_passed;
  return unit.verification.assertions_passed;
}
function failuresFor(unit, index) {
  if (index === 3) return unit.deterministic_matrix.assertions_failed;
  return unit.verification.assertions_failed;
}
function effectsBounded(unit, index) {
  const effects = unit.effects || {};
  const forbidden = [
    'browser_launched',
    'network_requests',
    'storage_deletes',
    'bank_user_data_mutations',
    'continuous_run_user_data_mutations',
    'user_storage_reads',
    'user_storage_writes',
    'user_storage_deletes',
    'real_user_storage_reads',
    'real_user_storage_writes',
    'real_user_storage_deletes',
    'persisted_user_data_changed',
    'storage_migration_performed',
    'production_migration_performed',
    'live_observation_performed',
    'formal_proof_performed'
  ];
  if (forbidden.some(key => effects[key] === true)) return false;
  if (index === 2) {
    return effects.production_files_changed === true
      && effects.runtime_integrity_changed === true
      && effects.repairs === true
      && effects.production_behavior_activated === true;
  }
  if (index === 3) {
    return effects.production_files_changed === true
      && effects.runtime_integrity_changed === true
      && effects.production_behavior_activated === true
      && effects.adapter_storage_writes === 0
      && effects.adapter_storage_deletes === 0;
  }
  if (index === 5) {
    return effects.disposable_fixture_writes_performed === true
      && effects.disposable_fixture_rollback_completed === true
      && effects.production_migration_performed === false;
  }
  return effects.production_files_changed === false
    && effects.persisted_user_data_changed === false;
}

function scenarioResult() {
  const units = UNIT_PATHS.map(read);
  const rows = units.map((unit, index) => ({
    unit_id: `P10-U${index + 1}`,
    status: unit.status,
    expected_status: EXPECTED_STATUSES[index],
    assertions: assertionsFor(unit, index),
    expected_assertions: EXPECTED_ASSERTIONS[index],
    assertions_failed: failuresFor(unit, index),
    effects_bounded: effectsBounded(unit, index)
  }));
  const cumulative = rows.reduce((sum, row) => sum + row.assertions, 0);
  const deterministicReady = rows.every(row =>
    row.status === row.expected_status
    && row.assertions === row.expected_assertions
    && row.assertions_failed === 0
    && row.effects_bounded
  );
  const liveOnlyClaims = [
    {
      id: 'BANK_HOME_SINGLE_STABLE_PROJECTION',
      statement: 'The real PMP Bank home displays one stable canonical inventory without blanking, flicker, or duplicate Bank buttons.'
    },
    {
      id: 'OWNER_REFRESH_VISUALLY_EXACTLY_ONCE',
      statement: 'Repeated read-only refresh and Bank navigation do not cause helpers, active tabs, or duplicate listeners to repaint conflicting content.'
    },
    {
      id: 'CONTINUOUS_RUN_SINGLE_OWNER_STACK',
      statement: 'Continuous Run Bank displays one stable Continuous Run owner stack and remains usable after leaving and reopening it.'
    }
  ];
  const check = {
    mode: 'USER_HANDS_ON_READ_ONLY_APP_CHECK',
    target: 'current PMP app from verified GitHub main',
    steps: [
      'Open the PMP app normally and open the Bank tab.',
      'Wait 10 seconds. Confirm the Bank list stays visible and does not flicker, blank, reorder repeatedly, or duplicate buttons.',
      'Press Refresh Read-Only View three times. Confirm the same Bank buttons remain present once each.',
      'Open Continuous Run Bank. Wait 10 seconds. Confirm one Run State Summary and one Continuous Run owner stack appear, with no duplicate sections or controls.',
      'Return to Banks, reopen Continuous Run Bank, and confirm the same single stable view returns.',
      'Do not import, save, delete, clear, or migrate anything during this check.'
    ],
    requested_response: 'Reply either “all six checks passed” or identify the first numbered check that failed and describe what stayed visible.',
    changes_user_data: false,
    automated_observation: false,
    consumes_scarce_observation_authority: false
  };
  const result = {
    type: TYPE,
    version: VERSION,
    status: deterministicReady ? 'HANDS_ON_APP_CHECK_REQUIRED' : 'DETERMINISTIC_READINESS_FAILED',
    pass: 10,
    unit: 'P10-U7',
    substep: 'P10-U7A',
    deterministic_readiness: {
      ready: deterministicReady,
      completed_units: rows.length,
      cumulative_prior_assertions: cumulative,
      unresolved_assertion_failures: rows.reduce((sum, row) => sum + row.assertions_failed, 0),
      all_effect_boundaries_preserved: rows.every(row => row.effects_bounded),
      unit_rows: rows
    },
    decision: {
      bounded_hands_on_check_required: deterministicReady,
      reason: deterministicReady
        ? 'Pass 10 changed the visible Bank projection and owner-driven refresh path. Deterministic tests prove safety and ownership, but only a brief real PMP check can establish that the user-visible Bank and Continuous Run Bank remain stable with no helper/listener fighting.'
        : 'One or more deterministic predecessor requirements are not green.',
      unresolved_live_only_claims: deterministicReady ? liveOnlyClaims : [],
      pass10_complete: false,
      observation_performed: false,
      automated_observation_performed: false,
      observation_authority_consumed: false,
      formal_proof_performed: false,
      next_step: deterministicReady ? 'USER_HANDS_ON_CHECK_THEN_P10_U7B_RECONCILIATION_AND_CLOSURE' : 'STOP_FOR_DETERMINISTIC_REPAIR'
    },
    hands_on_check: check,
    effects: {
      production_files_changed: false,
      runtime_integrity_changed: false,
      browser_launched: false,
      network_requests: false,
      storage_writes: false,
      storage_deletes: false,
      route_changes: false,
      bank_user_data_mutations: false,
      continuous_run_user_data_mutations: false,
      repairs: false,
      live_observation_performed: false,
      formal_proof_performed: false,
      persisted_user_data_changed: false,
      storage_migration_performed: false,
      production_behavior_activated: false
    },
    claim_ceiling: 'P10-U7A certifies deterministic readiness for one user hands-on read-only Bank stability check. Pass 10 is not complete, no app check has yet occurred, and no production code, persisted data, migration, automated observation, or formal proof is changed or consumed.'
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
module.exports = {
  TYPE,
  VERSION,
  UNIT_PATHS,
  EXPECTED_STATUSES,
  EXPECTED_ASSERTIONS,
  stable,
  digest,
  scenarioResult,
  verifyResultHash
};
