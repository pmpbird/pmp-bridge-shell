#!/usr/bin/env node
'use strict';

const assert = require('assert');
const runner = require('./run_pass10_unit7_closure_certification_v1.js');

let assertions = 0;
function check(value, message) { assertions += 1; assert(value, message); }
function equal(actual, expected, message) { assertions += 1; assert.deepStrictEqual(actual, expected, message); }

const result = runner.scenarioResult();
equal(result.type, runner.TYPE, 'type');
equal(result.version, runner.VERSION, 'version');
equal(result.status, 'PASS10_BANK_INVENTORY_REBUILD_COMPLETE', 'closure status');
equal(result.pass10_result, 'PASS', 'Pass 10 result');
equal(runner.verifyResultHash(result), true, 'result hash');
equal(result.evidence_records, 11, 'eleven immutable evidence records');
equal(result.cumulative_predecessor_assertions, 1674, 'predecessor assertion total');

equal(result.evidence_rows.length, 11, 'eleven evidence rows');
equal(result.evidence_rows.map(row => row.status), runner.EXPECTED_STATUSES, 'statuses');
equal(result.evidence_rows.map(row => row.assertions), runner.EXPECTED_ASSERTIONS, 'assertions');
equal(result.evidence_rows.map(row => row.receipt_next_step), runner.EXPECTED_STEPS, 'receipt next-step chain');
equal(result.evidence_rows.every(row => row.assertions_failed === 0), true, 'zero predecessor failures');
equal(result.evidence_rows.every(row => row.receipt_status === row.status), true, 'receipt status match');
equal(result.evidence_rows.every(row => row.persisted_user_data_preserved), true, 'persisted data preserved');
equal(result.evidence_rows.every(row => row.storage_migration_not_performed), true, 'migration not performed');
equal(result.evidence_rows.every(row => row.formal_proof_not_performed), true, 'formal proof not performed');
equal(result.evidence_rows.every(row => row.special_authority_unconsumed), true, 'special authority unconsumed');
for (const row of result.evidence_rows) {
  equal(row.status, row.expected_status, `${row.evidence_id} status`);
  equal(row.assertions, row.expected_assertions, `${row.evidence_id} assertion count`);
  equal(row.receipt_next_step, row.expected_next_step, `${row.evidence_id} receipt chain`);
}

const handsOn = result.hands_on_confirmation;
equal(handsOn.source, 'USER_REPORT', 'hands-on source');
equal(handsOn.reported_after_merged_main, '09e78630cb9865a6817f460ef28a4dc455dcc036', 'confirmed main');
equal(handsOn.exact_statement, 'It worked.', 'exact user statement');
equal(handsOn.result, 'PASS', 'hands-on result');
equal(handsOn.current_app_state_confirmed, true, 'current state confirmed');
equal(handsOn.confirms_uniform_title_weight, true, 'title weight confirmed');
equal(handsOn.confirms_prior_card_order_and_no_flicker_repairs_remained_intact, true, 'prior repairs confirmed');
equal(handsOn.persisted_user_data_change_requested, false, 'no user data change requested');
equal(handsOn.special_authority_consumed, false, 'no special authority');

equal(Object.keys(result.exit_criteria).length, 21, 'exit criterion count');
for (const [key, value] of Object.entries(result.exit_criteria)) equal(value, true, `exit ${key}`);

const boundary = result.bank_boundary;
equal(boundary.inventory_contract, 'PMP_CANONICAL_BANK_INVENTORY_CONTRACT_V1', 'inventory contract');
equal(boundary.canonical_owner, 'bank_screen_owner', 'canonical owner');
equal(boundary.identity_algorithm, 'SHA-256', 'identity');
equal(boundary.quarantine_policy, 'PRESERVE_EXACT_BYTES_NEVER_SILENTLY_DELETE', 'quarantine');
equal(boundary.delete_default, 'DENY', 'delete default');
equal(boundary.projection_write_apis, 0, 'no write APIs');
equal(boundary.projection_delete_apis, 0, 'no delete APIs');
equal(boundary.projection_migration_apis, 0, 'no migration APIs');
equal(boundary.owner_refresh_mode, 'EXACT_OWNER_RECEIPT_ONE_PROJECTION_REFRESH_SANITIZED_UI_EVENT', 'refresh boundary');

equal(result.next_step.id, 'P11-U1', 'Pass 11 entry');
check(result.next_step.objective.includes('safety invariants'), 'next objective safety');
equal(result.next_step.requires_user_app_check, false, 'no app check');
equal(result.next_step.requires_new_explicit_authority, false, 'no new authority');
equal(result.next_step.persisted_user_data_change_allowed, false, 'no data mutation');
equal(result.next_step.production_migration_allowed, false, 'no migration');
equal(result.next_step.stop_after, false, 'continue');

for (const [key, value] of Object.entries(result.effects)) equal(value, false, `effect ${key}`);
check(result.claim_ceiling.includes('Static Pass 10 closure'), 'static claim');
check(result.claim_ceiling.includes('user-reported'), 'user report claim');
check(result.claim_ceiling.includes('runs no observation or formal proof'), 'no special action');
check(result.claim_ceiling.includes('changes no runtime or persisted user data'), 'no mutation');
check(result.claim_ceiling.includes('performs no migration'), 'no migration');

console.log(`PASS: P10-U7V Bank inventory rebuild closure certification (${assertions}/${assertions})`);
