#!/usr/bin/env node
'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const childProcess = require('child_process');
const harness = require('./pass6_deterministic_browser_frame_event_harness_v1.js');
const faultRunner = require('./run_pass6_unit6_fault_injection_v1.js');

const ROOT = path.resolve(__dirname, '..');
const FAULTS = 'audit/pass6/pass6-fault-injection-catalog-v1.json';
const CATALOG = 'audit/pass6/pass6-cross-system-invariant-catalog-v1.json';
const SCENARIO = 'audit/pass6/fixtures/pass6-unit4-deterministic-proof-harness-positive-v1.json';
const REQUIRED_CATEGORIES = [
  'timeout',
  'animation',
  'nested_frames',
  'malformed_state',
  'missing_dependencies',
  'duplicate_events',
  'restart',
  'partial_failure',
];
let assertions = 0;

function check(condition, message) {
  assertions += 1;
  assert(condition, message);
}

function equal(actual, expected, message) {
  assertions += 1;
  assert.deepStrictEqual(actual, expected, message);
}

function readTracked(relative) {
  const full = path.resolve(ROOT, relative);
  if (fs.existsSync(full)) return fs.readFileSync(full, 'utf8');
  return childProcess.execFileSync('git', ['show', `HEAD:${relative}`], {
    cwd: ROOT,
    encoding: 'utf8',
  });
}

function deep(value) {
  return JSON.parse(JSON.stringify(value));
}

const faultCatalog = JSON.parse(readTracked(FAULTS));
const catalog = JSON.parse(readTracked(CATALOG));
const scenario = JSON.parse(readTracked(SCENARIO));
const first = faultRunner.runMatrix({ faultCatalog, catalog, scenario });
const second = faultRunner.runMatrix({ faultCatalog, catalog, scenario });

equal(first, second, 'repeated matrix execution is byte-for-byte deterministic');
equal(first.type, faultRunner.MATRIX_TYPE, 'matrix type');
equal(first.version, '1.0.0', 'matrix version');
equal(first.status, 'PASS', 'matrix passes');
check(faultRunner.verifyMatrixHash(first), 'matrix hash verifies');
equal(first.lane, 'deterministic_browser_harness', 'synthetic deterministic lane');
equal(first.attempts, 1, 'one lane attempt');
equal(first.automatic_retry_performed, false, 'no automatic retry');
equal(first.special_authority_required, false, 'no special authority required');
equal(first.special_authority_consumed, false, 'no special authority consumed');
equal(first.cases.length, 8, 'eight fault cases');
equal(first.summary.faults_required, 8, 'eight fault categories required');
equal(first.summary.faults_executed, 8, 'eight fault cases executed');
equal(first.summary.faults_preserved, 8, 'eight fault cases preserved');
equal(first.summary.primary_failures_preserved, 8, 'all primary failures preserved');
equal(first.summary.secondary_failures_preserved, 8, 'all secondary failure sets preserved');
equal(first.summary.restart_sequences, 1, 'one bounded restart sequence');
equal(first.summary.retries, 0, 'zero retries');
equal(first.summary.forbidden_effects, 0, 'zero forbidden effects');
check(first.claim_ceiling.includes('no live-app'), 'claim ceiling excludes live app');
check(first.claim_ceiling.includes('formal-proof'), 'claim ceiling excludes formal proof');

equal(faultCatalog.type, 'PMP_PASS6_DETERMINISTIC_FAULT_INJECTION_CATALOG_V1', 'catalog type');
equal(faultCatalog.version, '1.0.0', 'catalog version');
equal(faultCatalog.pass, 6, 'catalog pass');
equal(faultCatalog.unit, 'P6-U6', 'catalog unit');
equal(faultCatalog.execution.attempts, 1, 'catalog one attempt');
equal(faultCatalog.execution.automatic_retry, false, 'catalog automatic retry forbidden');
equal(faultCatalog.execution.special_authority_required, false, 'catalog special authority absent');
equal(faultCatalog.execution.failed_attempt_erasure, false, 'failed attempt erasure forbidden');
equal(faultCatalog.execution.preserve_primary_and_secondary_failures, true, 'both failure levels required');
equal(faultCatalog.execution.upload_before_enforcement, true, 'upload-before-enforcement required');
equal(faultCatalog.faults.length, 8, 'catalog contains eight faults');
equal(faultCatalog.required_categories, REQUIRED_CATEGORIES, 'exact required category order');
equal(new Set(faultCatalog.required_categories).size, 8, 'categories unique');
equal(new Set(faultCatalog.faults.map(item => item.id)).size, 8, 'fault IDs unique');
equal(
  faultCatalog.faults.map(item => item.category),
  REQUIRED_CATEGORIES,
  'faults cover exact required categories'
);

for (const item of first.cases) {
  const contract = faultCatalog.faults.find(fault => fault.id === item.fault_id);
  check(Boolean(contract), `${item.fault_id}: contract exists`);
  equal(item.category, contract.category, `${item.fault_id}: category preserved`);
  equal(item.injection, contract.injection, `${item.fault_id}: injection preserved`);
  equal(item.status, 'FAULT_PRESERVED', `${item.fault_id}: fault preserved`);
  equal(
    item.expected_primary_failure,
    contract.expected_primary_failure,
    `${item.fault_id}: expected primary`
  );
  equal(
    item.actual_primary_failure,
    contract.expected_primary_failure,
    `${item.fault_id}: actual primary`
  );
  equal(
    item.expected_secondary_failures,
    contract.expected_secondary_failures,
    `${item.fault_id}: expected secondary`
  );
  equal(
    item.actual_secondary_failures,
    contract.expected_secondary_failures,
    `${item.fault_id}: actual secondary`
  );
  equal(item.original_failure_preserved, true, `${item.fault_id}: original failure preserved`);
  equal(item.harness_result.status, 'FAIL', `${item.fault_id}: harness fails closed`);
  check(Boolean(item.harness_result.failure), `${item.fault_id}: failure record exists`);
  check(Boolean(item.harness_result.failure.state), `${item.fault_id}: failure state exists`);
  equal(item.harness_result_hash_valid, true, `${item.fault_id}: result hash reported valid`);
  check(harness.verifyResultHash(item.harness_result), `${item.fault_id}: result hash recomputes`);
  equal(item.restart_result_hash_valid, true, `${item.fault_id}: restart hash valid`);
  equal(item.forbidden_effects_observed, false, `${item.fault_id}: no forbidden effects`);
  check(
    Object.values(item.harness_result.effects).every(value => value === 0),
    `${item.fault_id}: effect counters zero`
  );
  equal(
    item.harness_result.summary.failures,
    1 + contract.expected_secondary_failures.length,
    `${item.fault_id}: failure count preserved`
  );
  check(
    /^[a-f0-9]{64}$/.test(item.harness_result.result_sha256),
    `${item.fault_id}: stable result digest`
  );
  check(
    typeof item.harness_result.failure.message === 'string'
      && item.harness_result.failure.message.length > 0,
    `${item.fault_id}: failure message preserved`
  );
}

const byCategory = Object.fromEntries(first.cases.map(item => [item.category, item]));

check(
  byCategory.timeout.harness_result.failure.evidence.tick
    > byCategory.timeout.harness_result.failure.evidence.timeout_ticks,
  'timeout preserves observed and allowed ticks'
);
equal(
  byCategory.animation.harness_result.failure.evidence.animation_id,
  'continuous-run-bank-pulse',
  'animation identity preserved'
);
equal(
  byCategory.animation.harness_result.failure.evidence.observed_stable_frames,
  0,
  'animation stability evidence preserved'
);
equal(
  byCategory.nested_frames.harness_result.failure.evidence.frame_id,
  'frame-child',
  'nested-frame parent preserved'
);
equal(
  byCategory.nested_frames.harness_result.failure.evidence.child_frame_id,
  'frame-grandchild',
  'nested-frame child preserved'
);
equal(byCategory.malformed_state.harness_result.failure.step_index, 0, 'malformed step index');
equal(byCategory.malformed_state.harness_result.failure.state.tick, 0, 'malformed state tick');
equal(
  byCategory.missing_dependencies.harness_result.failure.evidence.dependency,
  'PMP_DETERMINISTIC_FRAME_CLOCK_V1',
  'missing dependency identity'
);
equal(
  byCategory.missing_dependencies.harness_result.failure.evidence.resolution,
  'FAIL_CLOSED',
  'missing dependency fails closed'
);
check(
  /^[a-f0-9]{64}$/.test(
    byCategory.duplicate_events.harness_result.failure.evidence.fingerprint_sha256
  ),
  'duplicate event fingerprint preserved'
);
equal(
  byCategory.duplicate_events.harness_result.failure.step_index,
  5,
  'duplicate event fails at replay step'
);

const restart = byCategory.restart;
check(Boolean(restart.restart), 'restart evidence exists');
equal(restart.restart.generation, 1, 'restart generation is explicit');
equal(restart.restart.status, 'PASS', 'restart phase passes');
equal(
  restart.restart.original_failure_code,
  restart.actual_primary_failure,
  'restart retains original failure code'
);
equal(
  restart.restart.original_failure_result_sha256,
  restart.harness_result.result_sha256,
  'restart retains original failure hash'
);
equal(restart.restart.result.status, 'PASS', 'restart result passes');
check(harness.verifyResultHash(restart.restart.result), 'restart result hash recomputes');
equal(restart.restart.result.summary.invariants_passed, 20, 'restart covers all invariants');
equal(restart.restart.result.summary.events_captured, 8, 'restart preserves lifecycle coverage');
equal(restart.harness_result.status, 'FAIL', 'initial restart phase remains failed');

const partial = byCategory.partial_failure;
equal(partial.harness_result.failure.code, 'ADAPTER_OPERATION_FAILED', 'partial primary');
equal(partial.harness_result.secondary_failures.length, 1, 'partial secondary count');
equal(partial.harness_result.secondary_failures[0].code, 'TEARDOWN_FAILED', 'partial secondary');
equal(partial.harness_result.teardown.status, 'FAIL', 'partial teardown failure retained');

const baseline = harness.runScenario({
  catalog,
  scenario: deep(scenario),
  adapter: harness.createDeterministicAdapter(),
});
equal(baseline.status, 'PASS', 'baseline still passes after all fault injections');
equal(baseline.summary.invariants_passed, 20, 'baseline keeps all invariants');
equal(baseline.summary.events_captured, 8, 'baseline keeps event coverage');
equal(baseline.summary.failures, 0, 'baseline has no failure');
check(harness.verifyResultHash(baseline), 'baseline hash verifies');
check(Object.values(baseline.effects).every(value => value === 0), 'baseline has no effects');
equal(scenario.id, 'P6-U4-POSITIVE-ALL-INVARIANTS-001', 'baseline fixture not mutated');
equal(scenario.steps.length, 29, 'baseline step count not mutated');

{
  const tampered = deep(first);
  tampered.cases[0].actual_primary_failure = 'FALSE_GREEN';
  equal(faultRunner.verifyMatrixHash(tampered), false, 'tampered matrix rejected');
}
{
  const tampered = deep(first.cases[0].harness_result);
  tampered.failure.evidence.tick = 0;
  equal(harness.verifyResultHash(tampered), false, 'tampered fault evidence rejected');
}
{
  const missing = deep(first);
  missing.cases.pop();
  equal(faultRunner.verifyMatrixHash(missing), false, 'missing fault case rejected');
}
{
  const falseGreen = deep(first);
  falseGreen.cases[0].harness_result.status = 'PASS';
  equal(faultRunner.verifyMatrixHash(falseGreen), false, 'false-green mutation rejected');
}

console.log(`PASS: P6-U6 deterministic fault injection (${assertions}/${assertions})`);
