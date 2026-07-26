#!/usr/bin/env node
'use strict';

const assert = require('assert');
const runner = require('./run_pass9_unit7_closure_certification_v1.js');

let assertions = 0;
function check(value, message) { assertions += 1; assert(value, message); }
function equal(actual, expected, message) { assertions += 1; assert.deepStrictEqual(actual, expected, message); }

const result = runner.scenarioResult();
equal(result.type, runner.TYPE, 'type');
equal(result.version, runner.VERSION, 'version');
equal(result.status, 'PASS9_BANK_CONTINUOUS_RUN_COMPLETE', 'closure status');
equal(result.pass9_result, 'PASS', 'Pass 9 result');
equal(runner.verifyResultHash(result), true, 'result hash');
equal(result.completed_units, 6, 'six predecessor units');
equal(result.cumulative_prior_assertions, 1038, 'prior assertion total');

equal(result.unit_rows.length, 6, 'six unit rows');
equal(result.unit_rows.map(row => row.unit_id), ['P9-U1', 'P9-U2', 'P9-U3', 'P9-U4', 'P9-U5', 'P9-U6'], 'unit order');
equal(result.unit_rows.map(row => row.status), runner.EXPECTED_STATUSES, 'unit statuses');
equal(result.unit_rows.map(row => row.assertions), runner.EXPECTED_ASSERTIONS, 'unit assertions');
equal(result.unit_rows.map(row => row.next_step), runner.EXPECTED_NEXT, 'receipt next-step chain');
equal(result.unit_rows.every(row => row.assertions_failed === 0), true, 'zero predecessor failures');
equal(result.unit_rows.every(row => row.receipt_status === row.status), true, 'receipt status match');
equal(result.unit_rows.every(row => row.effects_bounded), true, 'effect boundary');
equal(result.unit_rows.every(row => row.special_authority_consumed === false), true, 'special authority unconsumed');
for (const row of result.unit_rows) {
  equal(row.status, row.expected_status, `${row.unit_id} expected status`);
  equal(row.assertions, row.expected_assertions, `${row.unit_id} expected assertions`);
  equal(row.next_step, row.expected_next_step, `${row.unit_id} expected next step`);
}

const criteria = result.exit_criteria;
equal(Object.keys(criteria).length, 28, 'exit criterion count');
for (const [key, value] of Object.entries(criteria)) equal(value, true, `exit ${key}`);

const owner = result.owner_boundary;
equal(owner.bank_owner, 'bank_screen_owner', 'Bank owner');
equal(owner.continuous_run_owner, 'continuous_run_level_owner', 'Continuous Run owner');
equal(owner.durable_writer, 'bank_screen_owner', 'sole durable writer');
equal(owner.run_state_requester, 'continuous_run_level_owner', 'run state requester');
equal(owner.governed_persisted_keys, 9, 'governed persisted keys');
equal(owner.receipt_algorithm, 'SHA-256_CHAINED', 'receipt algorithm');
equal(owner.active_runtime_order, 'BOUNDARY_THEN_STATE_AND_ROUTER_THEN_BANK_SHELL_THEN_CONTINUOUS_RUN_OWNER', 'active runtime order');

const observation = result.observation_boundary;
equal(observation.decision, 'BOUNDED_OBSERVATION_NOT_REQUIRED', 'observation decision');
equal(observation.observation_required, false, 'observation not required');
equal(observation.observation_performed, false, 'observation not performed');
equal(observation.authority_consumed, false, 'observation authority unconsumed');
equal(observation.retry_authorized, false, 'observation retry forbidden');

equal(result.next_step.id, 'P10-U1', 'Pass 10 entry');
check(result.next_step.objective.includes('read-only'), 'next objective read-only');
equal(result.next_step.requires_user_app_check, false, 'no app check');
equal(result.next_step.requires_new_explicit_authority, false, 'no new authority');
equal(result.next_step.persisted_user_data_change_allowed, false, 'no data mutation');
equal(result.next_step.storage_migration_allowed, false, 'no migration');
equal(result.next_step.stop_after, false, 'continue');

for (const [key, value] of Object.entries(result.effects)) equal(value, false, `effect ${key}`);
check(result.claim_ceiling.includes('Bank and Continuous Run repair is complete and green'), 'repair closure claim');
check(result.claim_ceiling.includes('P10-U1 remains read-only'), 'P10 boundary');
check(result.claim_ceiling.includes('No app launch'), 'no app');
check(result.claim_ceiling.includes('formal proof'), 'no formal proof');
check(result.claim_ceiling.includes('user-data change'), 'no user-data change');

console.log(`PASS: P9-U7 Bank and Continuous Run closure certification (${assertions}/${assertions})`);
