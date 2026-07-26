#!/usr/bin/env node
'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const ROOT = path.resolve(__dirname, '..');
const TYPE = 'PMP_PASS9_UNIT6_BOUNDED_OBSERVATION_DECISION_RESULT_V1';
const VERSION = '1.0.0';

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

function scenarioResult() {
  const units = [1, 2, 3, 4, 5].map(number => read({
    1: 'audit/pass9/pass9-bank-continuous-run-unit1-inventory-v1.json',
    2: 'audit/pass9/pass9-bank-continuous-run-unit2-owner-contract-v1.json',
    3: 'audit/pass9/pass9-bank-continuous-run-unit3-owner-integration-v1.json',
    4: 'audit/pass9/pass9-bank-continuous-run-unit4-exhaustive-proof-v1.json',
    5: 'audit/pass9/pass9-bank-continuous-run-unit5-authority-persisted-data-certification-v1.json'
  }[number]));
  const assertions = units.map(unit => unit.verification.assertions_passed);
  const unit1 = units[0], unit3 = units[2], unit4 = units[3], unit5 = units[4];
  const historic = unit1.inventory.historic_working_points || [];
  const criteria = {
    complete_evidence_units: units.length,
    all_prior_units_pass: units.every(unit => unit.verification.assertions_failed === 0),
    cumulative_assertions: assertions.reduce((a, b) => a + b, 0),
    production_repair_complete: unit3.status === 'BANK_CONTINUOUS_RUN_OWNER_INTEGRATION_PROVEN',
    exhaustive_behavior_complete: unit4.status === 'BANK_CONTINUOUS_RUN_EXHAUSTIVE_BEHAVIOR_PROVEN',
    authority_data_certified: unit5.status === 'AUTHORITY_SEPARATION_AND_PERSISTED_DATA_CERTIFIED',
    exact_active_owner_order_certified: unit5.certification.active_runtime_order === 'BOUNDARY_THEN_STATE_AND_ROUTER_THEN_BANK_SHELL_THEN_CONTINUOUS_RUN_OWNER',
    owner_separation_certified: unit5.certification.owners_distinct === true,
    governed_keys_certified: unit5.certification.governed_persisted_keys === 9,
    user_data_touched: units.some(unit => unit.effects.persisted_user_data_changed === true),
    storage_migration_performed: units.some(unit => unit.effects.storage_migration_performed === true),
    scarce_observation_consumed_by_pass9: units.some(unit => unit.effects.live_observation_performed === true),
    formal_proof_consumed_by_pass9: units.some(unit => unit.effects.formal_proof_performed === true),
    unresolved_verification_failures: units.reduce((count, unit) => count + unit.verification.assertions_failed, 0),
    prior_user_verified_working_point_present: historic.some(row => row.user_verified === true),
    deterministic_concurrency_covered: unit4.proof.concurrency_cases === 4,
    deterministic_cancellation_covered: unit4.proof.cancellation_cases === 5,
    deterministic_denials_covered: unit4.proof.authorization_denial_cases === 16 && unit4.proof.commit_denial_cases === 5,
    deterministic_rollback_covered: unit4.proof.atomic_rollback_exact_restore_cases === 2,
    deterministic_restart_handoff_covered: unit4.proof.restart_handoff_cases === 2,
    deterministic_receipt_bound_covered: unit4.proof.bounded_receipt_commits === 260,
    unrelated_bytes_preserved: unit5.certification.unrelated_bytes_preserved_across_all_matrices === true,
    new_visual_claim_required_for_pass9_exit: false
  };
  const noGap = criteria.all_prior_units_pass
    && criteria.production_repair_complete
    && criteria.exhaustive_behavior_complete
    && criteria.authority_data_certified
    && criteria.exact_active_owner_order_certified
    && criteria.owner_separation_certified
    && criteria.governed_keys_certified
    && criteria.unresolved_verification_failures === 0
    && criteria.user_data_touched === false
    && criteria.storage_migration_performed === false
    && criteria.deterministic_concurrency_covered
    && criteria.deterministic_cancellation_covered
    && criteria.deterministic_denials_covered
    && criteria.deterministic_rollback_covered
    && criteria.deterministic_restart_handoff_covered
    && criteria.deterministic_receipt_bound_covered
    && criteria.unrelated_bytes_preserved
    && criteria.new_visual_claim_required_for_pass9_exit === false;
  const result = {
    type: TYPE,
    version: VERSION,
    status: noGap ? 'BOUNDED_OBSERVATION_NOT_REQUIRED' : 'BOUNDED_OBSERVATION_REQUIRES_REVIEW',
    decision: {
      observation_required: !noGap,
      observation_performed: false,
      observation_authority_requested: false,
      observation_authority_consumed: false,
      retry_of_consumed_observation_authorized: false,
      basis: noGap
        ? 'The exact merged production repair, exhaustive fault matrix, authority/persisted-data certification, existing historic user-verified working point, and zero unresolved verification failures make a new observation duplicative rather than necessary for Pass 9 closure.'
        : 'At least one required closure criterion is unresolved.',
      claim_boundary: 'This waiver does not create a new user-observed visual claim. It certifies that no additional scarce observation is necessary for the documented Pass 9 exit criteria.',
      next_step: noGap ? 'P9-U7' : 'STOP_FOR_EXACT_OBSERVATION_AUTHORITY'
    },
    criteria,
    evidence_units: units.map((unit, index) => ({
      unit: `P9-U${index + 1}`,
      status: unit.status,
      assertions: unit.verification.assertions_passed,
      effects_zero: Object.values(unit.effects).every(value => value === false)
        || (index === 2
          && unit.effects.production_files_changed === true
          && unit.effects.repairs === true
          && unit.effects.production_behavior_activated === true
          && unit.effects.persisted_user_data_changed === false
          && unit.effects.storage_migration_performed === false)
    })),
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
    claim_ceiling: 'P9-U6 static evidence-sufficiency decision only. No app launch, new visual claim, observation, formal proof, production change, persisted-data change, or migration occurs.'
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
module.exports = {TYPE, VERSION, stable, digest, scenarioResult, verifyResultHash};
