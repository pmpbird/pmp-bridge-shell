#!/usr/bin/env node
'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const childProcess = require('child_process');
const harness = require('./pass6_deterministic_browser_frame_event_harness_v1.js');

const ROOT = path.resolve(__dirname, '..');
const CATALOG_PATH = 'audit/pass6/pass6-cross-system-invariant-catalog-v1.json';
const SCENARIO_PATH = 'audit/pass6/fixtures/pass6-unit4-deterministic-proof-harness-positive-v1.json';
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

const catalog = JSON.parse(readTracked(CATALOG_PATH));
const scenario = JSON.parse(readTracked(SCENARIO_PATH));

function run(nextScenario = scenario, adapterOptions = {}) {
  return harness.runScenario({
    catalog,
    scenario: nextScenario,
    adapter: harness.createDeterministicAdapter(adapterOptions),
  });
}

function expectFailure(code, mutate, adapterOptions = {}) {
  const candidate = deep(scenario);
  mutate(candidate);
  const result = run(candidate, adapterOptions);
  equal(result.status, 'FAIL', `${code}: status`);
  equal(result.failure.code, code, `${code}: code`);
  check(harness.verifyResultHash(result), `${code}: result hash`);
  equal(result.teardown.status, adapterOptions.teardown_error ? 'FAIL' : 'PASS', `${code}: teardown`);
  return result;
}

const first = run();
const second = run();
equal(first.status, 'PASS', 'baseline passes');
check(harness.verifyResultHash(first), 'baseline hash verifies');
equal(first, second, 'repeated evaluation is byte-for-byte deterministic');
equal(first.type, harness.RESULT_TYPE, 'result type');
equal(first.version, '1.0.0', 'result version');
equal(first.scenario_id, scenario.id, 'scenario identity');
equal(first.selected_invariants.length, 20, 'all catalog invariants selected');
equal(first.assertions.length, 20, 'all invariant assertions preserved');
equal(first.summary.invariants_required, 20, 'summary required invariants');
equal(first.summary.invariants_passed, 20, 'summary passed invariants');
equal(first.summary.events_captured, 8, 'eight lifecycle events captured');
equal(first.summary.frames_observed, 2, 'two frames observed');
equal(first.summary.final_tick, 8, 'monotonic final tick');
equal(first.summary.failures, 0, 'no baseline failure');
equal(first.failure, null, 'no baseline failure detail');
equal(first.secondary_failures, [], 'no baseline secondary failures');
equal(first.teardown, { status: 'PASS', calls: 1, final_tick: 8 }, 'teardown exactly once');
check(Object.values(first.effects).every(value => value === 0), 'all effect counters remain zero');
equal(first.events.map(event => event.event_id), [
  'E0001', 'E0002', 'E0003', 'E0004', 'E0005', 'E0006', 'E0007', 'E0008',
], 'stable event ids');
equal(first.events.map(event => event.monotonic_tick), [1, 2, 3, 4, 5, 6, 7, 8], 'monotonic ticks');
equal(first.events.map(event => event.kind), [
  'browser_started',
  'page_created',
  'frame_attached',
  'frame_navigated',
  'domcontentloaded',
  'frame_detached',
  'page_closed',
  'browser_closed',
], 'exact event ordering');
check(first.events.every(event => /^[a-f0-9]{64}$/.test(event.event_sha256)), 'every event is hashed');
equal(first.frames.map(frame => frame.frame_id), ['frame-child', 'frame-main'], 'stable frame ordering');
equal(first.frames[0].generation, 1, 'child frame generation advanced');
equal(first.frames[0].active, false, 'child frame detached');
equal(first.frames[1].active, false, 'main frame closed');
equal(first.assertions.map(row => row.invariant_id), [...scenario.invariant_ids].sort(), 'assertions sorted');
check(first.assertions.every(row => row.evidence_event_ids[0] === 'E0005'), 'assertions retain evidence binding');
equal(new Set(first.selected_invariants.map(row => row.subsystem)).size, 9, 'nine subsystems represented');
check(first.claim_ceiling.includes('no live-app'), 'claim ceiling blocks live outcome');
check(first.claim_ceiling.includes('formal-proof'), 'claim ceiling blocks formal proof outcome');

for (const event of first.events) {
  check(event.step_index >= 0, `${event.event_id}: step index preserved`);
  check(event.monotonic_tick > 0, `${event.event_id}: positive tick`);
  check(harness.digest({
    ...event,
    event_sha256: undefined,
  }) === event.event_sha256, `${event.event_id}: hash recomputes`);
}
for (const invariant of first.selected_invariants) {
  check(catalog.invariants.some(item => item.id === invariant.id), `${invariant.id}: catalog linked`);
  check(typeof invariant.owner === 'string' && invariant.owner.length > 0, `${invariant.id}: owner preserved`);
  check(typeof invariant.enforcement === 'string', `${invariant.id}: enforcement preserved`);
  check(typeof invariant.failure_behavior === 'string', `${invariant.id}: failure behavior preserved`);
}

{
  const badCatalog = deep(catalog);
  badCatalog.type = 'BAD';
  const result = harness.runScenario({
    catalog: badCatalog,
    scenario,
    adapter: harness.createDeterministicAdapter(),
  });
  equal(result.status, 'FAIL', 'bad catalog fails');
  equal(result.failure.code, 'CATALOG_IDENTITY_INVALID', 'bad catalog code');
  check(harness.verifyResultHash(result), 'bad catalog result hash');
}
{
  const badCatalog = deep(catalog);
  badCatalog.invariants.push(deep(badCatalog.invariants[0]));
  const result = harness.runScenario({
    catalog: badCatalog,
    scenario,
    adapter: harness.createDeterministicAdapter(),
  });
  equal(result.failure.code, 'CATALOG_INVARIANT_DUPLICATE', 'duplicate catalog invariant fails');
  check(harness.verifyResultHash(result), 'duplicate catalog invariant hash');
}
{
  const badCatalog = deep(catalog);
  badCatalog.invariants[0].evidence_paths = [];
  const result = harness.runScenario({
    catalog: badCatalog,
    scenario,
    adapter: harness.createDeterministicAdapter(),
  });
  equal(result.failure.code, 'CATALOG_INVARIANT_EVIDENCE_MISSING', 'missing catalog evidence fails');
}
{
  const badCatalog = deep(catalog);
  badCatalog.invariants[0].deterministic_test_paths = [];
  const result = harness.runScenario({
    catalog: badCatalog,
    scenario,
    adapter: harness.createDeterministicAdapter(),
  });
  equal(result.failure.code, 'CATALOG_INVARIANT_TEST_MISSING', 'missing deterministic test fails');
}

expectFailure('SCENARIO_IDENTITY_INVALID', candidate => { candidate.type = 'BAD'; });
expectFailure('SCENARIO_ID_INVALID', candidate => { candidate.id = '../escape'; });
expectFailure('SCENARIO_INVARIANTS_INVALID', candidate => { candidate.invariant_ids = []; });
expectFailure('SCENARIO_INVARIANTS_INVALID', candidate => {
  candidate.invariant_ids.push(candidate.invariant_ids[0]);
});
expectFailure('SCENARIO_INVARIANT_UNKNOWN', candidate => {
  candidate.invariant_ids[0] = 'P6-INV-UNKNOWN-999';
});
expectFailure('SCENARIO_REQUIRED_EVENTS_INVALID', candidate => { candidate.required_events = []; });
expectFailure('SCENARIO_REQUIRED_EVENT_UNKNOWN', candidate => {
  candidate.required_events[0] = 'mystery_event';
});
expectFailure('SCENARIO_TIMEOUT_INVALID', candidate => { candidate.timeout_ticks = 0; });
expectFailure('SCENARIO_TIMEOUT_INVALID', candidate => { candidate.timeout_ticks = 1.5; });
expectFailure('SCENARIO_STEPS_INVALID', candidate => { candidate.steps = []; });
expectFailure('STEP_MALFORMED', candidate => { candidate.steps[0] = null; });
expectFailure('STEP_OPERATION_MISSING', candidate => { delete candidate.steps[0].op; });
expectFailure('STEP_OPERATION_UNKNOWN', candidate => { candidate.steps[0].op = 'invent'; });
expectFailure('BROWSER_NOT_OPEN', candidate => { candidate.steps.splice(0, 1); });
expectFailure('BROWSER_ALREADY_OPEN', candidate => {
  candidate.steps.splice(1, 0, { op: 'launch_browser' });
});
expectFailure('DUPLICATE_PAGE_ID', candidate => {
  candidate.steps.splice(2, 0, deep(candidate.steps[1]));
});
expectFailure('FRAME_ID_INVALID', candidate => { candidate.steps[1].main_frame_id = '../bad'; });
expectFailure('FRAME_URL_INVALID', candidate => { candidate.steps[1].url = ''; });
expectFailure('DUPLICATE_FRAME_ID', candidate => {
  candidate.steps.splice(3, 0, deep(candidate.steps[2]));
});
expectFailure('FRAME_NOT_ACTIVE', candidate => { candidate.steps[2].parent_frame_id = 'frame-missing'; });
expectFailure('FRAME_PARENT_SELF', candidate => { candidate.steps[2].frame_id = 'frame-main'; });
expectFailure('FRAME_URL_INVALID', candidate => { candidate.steps[2].url = ''; });
expectFailure('FRAME_NOT_ACTIVE', candidate => { candidate.steps[3].frame_id = 'frame-missing'; });
expectFailure('FRAME_GENERATION_STALE', candidate => { candidate.steps[3].expected_generation = 9; });
expectFailure('FRAME_URL_INVALID', candidate => { candidate.steps[3].url = ''; });
expectFailure('EVENT_KIND_UNKNOWN', candidate => { candidate.steps[4].kind = 'unknown'; });
expectFailure('EVENT_FRAME_NOT_ACTIVE', candidate => { candidate.steps[4].frame_id = 'frame-missing'; });
expectFailure('EVENT_INVARIANTS_INVALID', candidate => {
  candidate.steps[4].invariant_ids.push(candidate.steps[4].invariant_ids[0]);
});
expectFailure('EVENT_INVARIANT_OUT_OF_SCOPE', candidate => {
  candidate.invariant_ids = candidate.invariant_ids.slice(1);
});
expectFailure('EXPECTED_EVENT_KIND_UNKNOWN', candidate => { candidate.steps[5].kind = 'unknown'; });
expectFailure('REQUIRED_EVENT_MISSING', candidate => { candidate.steps[5].kind = 'load'; });
expectFailure('ASSERTION_INVARIANT_OUT_OF_SCOPE', candidate => {
  candidate.invariant_ids = candidate.invariant_ids.slice(1);
  candidate.steps[4].invariant_ids = candidate.steps[4].invariant_ids.slice(1);
});
expectFailure('INVARIANT_ASSERTION_FAILED', candidate => { candidate.steps[6].outcome = 'FAIL'; });
expectFailure('ASSERTION_EVIDENCE_INVALID', candidate => { candidate.steps[6].evidence_event_ids = []; });
expectFailure('ASSERTION_EVIDENCE_MISSING', candidate => {
  candidate.steps[6].evidence_event_ids = ['E9999'];
});
expectFailure('ASSERTION_EVIDENCE_UNBOUND', candidate => {
  candidate.steps[4].invariant_ids = candidate.steps[4].invariant_ids.slice(1);
});
expectFailure('ASSERTION_DUPLICATE', candidate => {
  candidate.steps.splice(7, 0, deep(candidate.steps[6]));
});
expectFailure('ADVANCE_TICKS_INVALID', candidate => {
  candidate.steps.splice(5, 0, { op: 'advance_ticks', ticks: 0 });
});
expectFailure('SCENARIO_TIMEOUT', candidate => {
  candidate.steps.splice(5, 0, { op: 'advance_ticks', ticks: 200 });
});
expectFailure('MAIN_FRAME_DETACH_FORBIDDEN', candidate => {
  candidate.steps[candidate.steps.length - 3].frame_id = 'frame-main';
});
expectFailure('ACTIVE_CHILD_FRAME_REMAINS', candidate => {
  candidate.steps.splice(candidate.steps.length - 3, 1);
});
expectFailure('ACTIVE_PAGE_REMAINS', candidate => {
  candidate.steps.splice(candidate.steps.length - 2, 1);
});
expectFailure('BROWSER_LEFT_OPEN', candidate => {
  candidate.steps.splice(candidate.steps.length - 1, 1);
});
expectFailure('INVARIANT_ASSERTION_MISSING', candidate => {
  candidate.steps.splice(6, 1);
  candidate.steps[4].invariant_ids = candidate.steps[4].invariant_ids.slice(1);
  candidate.invariant_ids = candidate.invariant_ids.slice(1);
  candidate.invariant_ids.push('P6-INV-ROUTE-001');
});
expectFailure('REQUIRED_EVENT_MISSING', candidate => {
  candidate.required_events.push('console');
});
expectFailure('ADAPTER_OPERATION_FAILED', candidate => {}, { fail_step_index: 3 });
for (const key of harness.EFFECT_KEYS) {
  expectFailure('FORBIDDEN_EFFECT_OBSERVED', candidate => {}, { effects: { [key]: 1 } });
}
{
  const result = run(scenario, { teardown_error: 'bounded teardown failure' });
  equal(result.status, 'FAIL', 'teardown error fails result');
  equal(result.failure.code, 'TEARDOWN_FAILED', 'teardown failure code');
  equal(result.teardown.status, 'FAIL', 'teardown status fails');
  check(harness.verifyResultHash(result), 'teardown failure result hash');
}
{
  const result = run(scenario, {
    fail_step_index: 2,
    teardown_error: 'secondary teardown failure',
  });
  equal(result.failure.code, 'ADAPTER_OPERATION_FAILED', 'primary adapter failure preserved');
  equal(result.secondary_failures.length, 1, 'secondary teardown failure preserved');
  equal(result.secondary_failures[0].code, 'TEARDOWN_FAILED', 'secondary failure code');
  check(harness.verifyResultHash(result), 'primary plus secondary result hash');
}
{
  const adapter = harness.createDeterministicAdapter({ effects: { storage_writes: -1 } });
  const result = harness.runScenario({ catalog, scenario, adapter });
  equal(result.failure.code, 'EFFECT_COUNT_INVALID', 'negative effect count fails');
}
{
  const adapter = harness.createDeterministicAdapter({ effects: { unexpected_effect: 1 } });
  const result = harness.runScenario({ catalog, scenario, adapter });
  equal(result.failure.code, 'EFFECT_KEY_UNKNOWN', 'unknown effect key fails');
}
{
  const result = harness.runScenario({ catalog, scenario, adapter: {} });
  equal(result.failure.code, 'ADAPTER_CONTRACT_INVALID', 'missing adapter contract fails');
  check(harness.verifyResultHash(result), 'bad adapter result hash');
}
{
  const tampered = deep(first);
  tampered.summary.events_captured += 1;
  equal(harness.verifyResultHash(tampered), false, 'tampered result hash rejected');
}
{
  const tampered = deep(first.events[0]);
  tampered.payload.engine = 'changed';
  check(
    harness.digest({ ...tampered, event_sha256: undefined }) !== tampered.event_sha256,
    'tampered event hash rejected'
  );
}

console.log(`PASS: P6-U4 deterministic browser/frame/event proof harness (${assertions}/${assertions})`);
