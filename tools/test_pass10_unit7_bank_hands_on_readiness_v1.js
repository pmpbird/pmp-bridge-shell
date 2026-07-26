#!/usr/bin/env node
'use strict';

const assert = require('assert');
const runner = require('./run_pass10_unit7_bank_hands_on_readiness_v1.js');

let assertions = 0;
function check(value, message) { assertions += 1; assert(value, message); }
function equal(actual, expected, message) { assertions += 1; assert.deepStrictEqual(actual, expected, message); }

const result = runner.scenarioResult();
equal(result.type, runner.TYPE, 'type');
equal(result.version, runner.VERSION, 'version');
equal(result.status, 'HANDS_ON_APP_CHECK_REQUIRED', 'readiness status');
equal(result.pass, 10, 'pass');
equal(result.unit, 'P10-U7', 'unit');
equal(result.substep, 'P10-U7A', 'substep');
equal(runner.verifyResultHash(result), true, 'result hash');

const readiness = result.deterministic_readiness;
equal(readiness.ready, true, 'deterministic readiness');
equal(readiness.completed_units, 6, 'six complete units');
equal(readiness.cumulative_prior_assertions, 778, 'prior assertion total');
equal(readiness.unresolved_assertion_failures, 0, 'zero prior failures');
equal(readiness.all_effect_boundaries_preserved, true, 'effect boundaries');
equal(readiness.unit_rows.length, 6, 'unit rows');
equal(readiness.unit_rows.map(row => row.unit_id), ['P10-U1', 'P10-U2', 'P10-U3', 'P10-U4', 'P10-U5', 'P10-U6'], 'unit order');
equal(readiness.unit_rows.map(row => row.status), runner.EXPECTED_STATUSES, 'unit statuses');
equal(readiness.unit_rows.map(row => row.assertions), runner.EXPECTED_ASSERTIONS, 'unit assertions');
equal(readiness.unit_rows.every(row => row.assertions_failed === 0), true, 'unit failures');
equal(readiness.unit_rows.every(row => row.effects_bounded), true, 'bounded unit effects');
for (const row of readiness.unit_rows) {
  equal(row.status, row.expected_status, `${row.unit_id} expected status`);
  equal(row.assertions, row.expected_assertions, `${row.unit_id} expected assertions`);
}

const decision = result.decision;
equal(decision.bounded_hands_on_check_required, true, 'hands-on check required');
check(decision.reason.includes('visible Bank projection'), 'visible projection reason');
check(decision.reason.includes('helper/listener fighting'), 'helper fighting reason');
equal(decision.unresolved_live_only_claims.length, 3, 'three live-only claims');
equal(decision.unresolved_live_only_claims.map(row => row.id), [
  'BANK_HOME_SINGLE_STABLE_PROJECTION',
  'OWNER_REFRESH_VISUALLY_EXACTLY_ONCE',
  'CONTINUOUS_RUN_SINGLE_OWNER_STACK'
], 'live-only claim IDs');
equal(decision.pass10_complete, false, 'Pass 10 remains open');
equal(decision.observation_performed, false, 'check not performed');
equal(decision.automated_observation_performed, false, 'automated observation not performed');
equal(decision.observation_authority_consumed, false, 'observation authority not consumed');
equal(decision.formal_proof_performed, false, 'formal proof not performed');
equal(decision.next_step, 'USER_HANDS_ON_CHECK_THEN_P10_U7B_RECONCILIATION_AND_CLOSURE', 'next step');

const handsOn = result.hands_on_check;
equal(handsOn.mode, 'USER_HANDS_ON_READ_ONLY_APP_CHECK', 'check mode');
check(handsOn.target.includes('verified GitHub main'), 'current target');
equal(handsOn.steps.length, 6, 'six steps');
check(handsOn.steps[0].includes('Bank tab'), 'open Bank');
check(handsOn.steps[1].includes('Wait 10 seconds'), 'Bank stability wait');
check(handsOn.steps[1].includes('duplicate'), 'Bank duplicate check');
check(handsOn.steps[2].includes('three times'), 'three refreshes');
check(handsOn.steps[3].includes('Continuous Run Bank'), 'open Continuous Run');
check(handsOn.steps[3].includes('one Run State Summary'), 'single owner stack');
check(handsOn.steps[4].includes('reopen Continuous Run Bank'), 'navigation reopening');
check(handsOn.steps[5].includes('Do not import'), 'read-only prohibition');
check(handsOn.requested_response.includes('all six checks passed'), 'simple response');
equal(handsOn.changes_user_data, false, 'no user-data change');
equal(handsOn.automated_observation, false, 'manual check only');
equal(handsOn.consumes_scarce_observation_authority, false, 'scarce authority not consumed');

for (const [key, value] of Object.entries(result.effects)) equal(value, false, `effect ${key}`);
check(result.claim_ceiling.includes('Pass 10 is not complete'), 'Pass 10 claim ceiling');
check(result.claim_ceiling.includes('no app check has yet occurred'), 'observation claim ceiling');
check(result.claim_ceiling.includes('formal proof'), 'formal proof claim ceiling');
check(result.claim_ceiling.includes('persisted data'), 'persisted data claim ceiling');

console.log(`PASS: P10-U7A Bank hands-on readiness (${assertions}/${assertions})`);
