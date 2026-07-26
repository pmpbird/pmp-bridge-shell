#!/usr/bin/env node
'use strict';

const assert = require('assert');
const runner = require('./run_pass9_unit6_bounded_observation_decision_v1.js');
let assertions = 0;
function check(value, message) { assertions += 1; assert(value, message); }
function equal(actual, expected, message) { assertions += 1; assert.deepStrictEqual(actual, expected, message); }

const result = runner.scenarioResult();
equal(result.type, runner.TYPE, 'type');
equal(result.version, runner.VERSION, 'version');
equal(result.status, 'BOUNDED_OBSERVATION_NOT_REQUIRED', 'waiver status');
equal(runner.verifyResultHash(result), true, 'result hash');
equal(result.decision.observation_required, false, 'observation not required');
equal(result.decision.observation_performed, false, 'observation not performed');
equal(result.decision.observation_authority_requested, false, 'authority not requested');
equal(result.decision.observation_authority_consumed, false, 'authority not consumed');
equal(result.decision.retry_of_consumed_observation_authorized, false, 'retry not authorized');
equal(result.decision.next_step, 'P9-U7', 'next closure');
check(result.decision.basis.includes('duplicative'), 'basis duplicative');
check(result.decision.claim_boundary.includes('does not create a new user-observed visual claim'), 'claim boundary');

const criteria = result.criteria;
equal(criteria.complete_evidence_units, 5, 'five evidence units');
equal(criteria.all_prior_units_pass, true, 'prior units pass');
equal(criteria.cumulative_assertions, 979, 'cumulative assertions');
equal(criteria.production_repair_complete, true, 'repair complete');
equal(criteria.exhaustive_behavior_complete, true, 'behavior complete');
equal(criteria.authority_data_certified, true, 'authority data certified');
equal(criteria.exact_active_owner_order_certified, true, 'active order');
equal(criteria.owner_separation_certified, true, 'owner separation');
equal(criteria.governed_keys_certified, true, 'keys certified');
equal(criteria.user_data_touched, false, 'user data untouched');
equal(criteria.storage_migration_performed, false, 'no migration');
equal(criteria.scarce_observation_consumed_by_pass9, false, 'no Pass9 observation');
equal(criteria.formal_proof_consumed_by_pass9, false, 'no formal proof');
equal(criteria.unresolved_verification_failures, 0, 'no failures');
equal(criteria.prior_user_verified_working_point_present, true, 'historic user verification');
equal(criteria.deterministic_concurrency_covered, true, 'concurrency');
equal(criteria.deterministic_cancellation_covered, true, 'cancellation');
equal(criteria.deterministic_denials_covered, true, 'denials');
equal(criteria.deterministic_rollback_covered, true, 'rollback');
equal(criteria.deterministic_restart_handoff_covered, true, 'restart handoff');
equal(criteria.deterministic_receipt_bound_covered, true, 'receipt bound');
equal(criteria.unrelated_bytes_preserved, true, 'data preservation');
equal(criteria.new_visual_claim_required_for_pass9_exit, false, 'visual claim unnecessary');

equal(result.evidence_units.length, 5, 'evidence rows');
equal(result.evidence_units.map(row => row.unit), ['P9-U1', 'P9-U2', 'P9-U3', 'P9-U4', 'P9-U5'], 'evidence order');
equal(result.evidence_units.map(row => row.assertions), [135, 229, 234, 238, 143], 'evidence assertions');
equal(result.evidence_units.every(row => row.effects_zero), true, 'effects bounded');
for (const [key, value] of Object.entries(result.effects)) equal(value, false, `effect ${key}`);
check(result.claim_ceiling.includes('static evidence-sufficiency'), 'static ceiling');
check(result.claim_ceiling.includes('No app launch'), 'no app');
check(result.claim_ceiling.includes('new visual claim'), 'no visual claim');
check(result.claim_ceiling.includes('formal proof'), 'no formal proof');
check(result.claim_ceiling.includes('persisted-data change'), 'no data change');

console.log(`PASS: P9-U6 bounded observation evidence-sufficiency decision (${assertions}/${assertions})`);
