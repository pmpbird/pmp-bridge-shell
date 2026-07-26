#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const childProcess = require('child_process');
const harness = require('./pass6_deterministic_browser_frame_event_harness_v1.js');

const ROOT = path.resolve(__dirname, '..');
const MATRIX_TYPE = 'PMP_PASS6_DETERMINISTIC_FAULT_INJECTION_RESULT_V1';
const VERSION = '1.0.0';
const EMPTY_EFFECTS = Object.freeze(
  Object.fromEntries(harness.EFFECT_KEYS.map(key => [key, 0]))
);

function deep(value) {
  return JSON.parse(JSON.stringify(value));
}

function readTracked(relative) {
  const full = path.resolve(ROOT, relative);
  if (!full.startsWith(ROOT + path.sep)) throw new Error(`path escapes repository: ${relative}`);
  if (fs.existsSync(full)) return fs.readFileSync(full, 'utf8');
  return childProcess.execFileSync('git', ['show', `HEAD:${relative}`], {
    cwd: ROOT,
    encoding: 'utf8',
  });
}

function parseArgs(argv) {
  const options = {
    faults: 'audit/pass6/pass6-fault-injection-catalog-v1.json',
    catalog: 'audit/pass6/pass6-cross-system-invariant-catalog-v1.json',
    scenario: 'audit/pass6/fixtures/pass6-unit4-deterministic-proof-harness-positive-v1.json',
    output: null,
  };
  for (let index = 2; index < argv.length; index += 1) {
    const key = argv[index];
    if (!['--faults', '--catalog', '--scenario', '--output'].includes(key) || index + 1 >= argv.length) {
      throw new Error(`unknown or incomplete argument: ${key}`);
    }
    options[key.slice(2)] = argv[++index];
  }
  return options;
}

function throwingAdapter({ code, message, evidence, failStep = 0, teardownError = null }) {
  let teardownCalls = 0;
  return {
    contract_type: 'PMP_PASS6_DETERMINISTIC_BROWSER_ADAPTER_V1',
    perform(step, api) {
      if (api.step_index === failStep) {
        throw new harness.HarnessFailure(code, message, deep(evidence));
      }
      api.execute(step);
    },
    effects() {
      return deep(EMPTY_EFFECTS);
    },
    teardown(api) {
      teardownCalls += 1;
      if (teardownError) throw new Error(teardownError);
      return { status: 'PASS', calls: teardownCalls, final_tick: api.tick };
    },
  };
}

function duplicateRejectingAdapter() {
  const fingerprints = new Set();
  let teardownCalls = 0;
  return {
    contract_type: 'PMP_PASS6_DETERMINISTIC_BROWSER_ADAPTER_V1',
    perform(step, api) {
      if (step && step.op === 'emit_event') {
        const fingerprint = harness.digest({
          kind: step.kind,
          page_id: step.page_id || null,
          frame_id: step.frame_id || null,
          frame_generation: step.frame_generation === undefined ? null : step.frame_generation,
          invariant_ids: [...(step.invariant_ids || [])].sort(),
          payload: step.payload || {},
        });
        if (fingerprints.has(fingerprint)) {
          throw new harness.HarnessFailure(
            'DUPLICATE_EVENT_DETECTED',
            'identical lifecycle event replay was rejected',
            { fingerprint_sha256: fingerprint, step_index: api.step_index }
          );
        }
        fingerprints.add(fingerprint);
      }
      api.execute(step);
    },
    effects() {
      return deep(EMPTY_EFFECTS);
    },
    teardown(api) {
      teardownCalls += 1;
      return { status: 'PASS', calls: teardownCalls, final_tick: api.tick };
    },
  };
}

function injectTimeout(scenario) {
  const candidate = deep(scenario);
  candidate.id = 'P6-U6-TIMEOUT-001';
  candidate.steps.splice(5, 0, {
    op: 'advance_ticks',
    ticks: candidate.timeout_ticks + 1,
  });
  return {
    result: harness.runScenario({
      catalog: this.catalog,
      scenario: candidate,
      adapter: harness.createDeterministicAdapter(),
    }),
    restartResult: null,
  };
}

function injectAnimation(scenario) {
  const candidate = deep(scenario);
  candidate.id = 'P6-U6-ANIMATION-001';
  return {
    result: harness.runScenario({
      catalog: this.catalog,
      scenario: candidate,
      adapter: throwingAdapter({
        code: 'ANIMATION_SETTLE_TIMEOUT',
        message: 'animation did not settle before the deterministic deadline',
        evidence: {
          animation_id: 'continuous-run-bank-pulse',
          deadline_ticks: 16,
          observed_stable_frames: 0,
        },
        failStep: 4,
      }),
    }),
    restartResult: null,
  };
}

function injectNestedFrames(scenario) {
  const candidate = deep(scenario);
  candidate.id = 'P6-U6-NESTED-FRAME-001';
  const detachIndex = candidate.steps.findIndex(step => step.op === 'detach_frame');
  candidate.steps.splice(detachIndex, 0, {
    op: 'attach_frame',
    page_id: 'page-primary',
    frame_id: 'frame-grandchild',
    parent_frame_id: 'frame-child',
    url: 'https://proof.invalid/nested-frame',
  });
  return {
    result: harness.runScenario({
      catalog: this.catalog,
      scenario: candidate,
      adapter: harness.createDeterministicAdapter(),
    }),
    restartResult: null,
  };
}

function injectMalformedState(scenario) {
  const candidate = deep(scenario);
  candidate.id = 'P6-U6-MALFORMED-STATE-001';
  candidate.steps[0] = null;
  return {
    result: harness.runScenario({
      catalog: this.catalog,
      scenario: candidate,
      adapter: harness.createDeterministicAdapter(),
    }),
    restartResult: null,
  };
}

function injectMissingDependency(scenario) {
  const candidate = deep(scenario);
  candidate.id = 'P6-U6-MISSING-DEPENDENCY-001';
  return {
    result: harness.runScenario({
      catalog: this.catalog,
      scenario: candidate,
      adapter: throwingAdapter({
        code: 'DEPENDENCY_MISSING',
        message: 'required deterministic adapter dependency is unavailable',
        evidence: {
          dependency: 'PMP_DETERMINISTIC_FRAME_CLOCK_V1',
          resolution: 'FAIL_CLOSED',
        },
      }),
    }),
    restartResult: null,
  };
}

function injectDuplicateEvents(scenario) {
  const candidate = deep(scenario);
  candidate.id = 'P6-U6-DUPLICATE-EVENT-001';
  const emitIndex = candidate.steps.findIndex(step => step.op === 'emit_event');
  candidate.steps.splice(emitIndex + 1, 0, deep(candidate.steps[emitIndex]));
  return {
    result: harness.runScenario({
      catalog: this.catalog,
      scenario: candidate,
      adapter: duplicateRejectingAdapter(),
    }),
    restartResult: null,
  };
}

function injectRestart(scenario) {
  const initial = deep(scenario);
  initial.id = 'P6-U6-RESTART-001-PRE-RESTART';
  const restarted = deep(scenario);
  restarted.id = 'P6-U6-RESTART-001-POST-RESTART';
  const result = harness.runScenario({
    catalog: this.catalog,
    scenario: initial,
    adapter: harness.createDeterministicAdapter({ fail_step_index: 3 }),
  });
  const restartResult = harness.runScenario({
    catalog: this.catalog,
    scenario: restarted,
    adapter: harness.createDeterministicAdapter(),
  });
  return { result, restartResult };
}

function injectPartialFailure(scenario) {
  const candidate = deep(scenario);
  candidate.id = 'P6-U6-PARTIAL-FAILURE-001';
  return {
    result: harness.runScenario({
      catalog: this.catalog,
      scenario: candidate,
      adapter: harness.createDeterministicAdapter({
        fail_step_index: 3,
        teardown_error: 'secondary teardown failure retained',
      }),
    }),
    restartResult: null,
  };
}

const INJECTORS = Object.freeze({
  timeout: injectTimeout,
  animation: injectAnimation,
  nested_frames: injectNestedFrames,
  malformed_state: injectMalformedState,
  missing_dependencies: injectMissingDependency,
  duplicate_events: injectDuplicateEvents,
  restart: injectRestart,
  partial_failure: injectPartialFailure,
});

function failureCodes(result) {
  return (result.secondary_failures || []).map(item => item.code);
}

function runMatrix({ faultCatalog, catalog, scenario }) {
  const cases = [];
  for (const fault of faultCatalog.faults) {
    const injector = INJECTORS[fault.category];
    if (!injector) throw new Error(`unsupported fault category: ${fault.category}`);
    const { result, restartResult } = injector.call({ catalog }, scenario);
    const primary = result.failure ? result.failure.code : null;
    const secondary = failureCodes(result);
    const expectedPrimary = fault.expected_primary_failure;
    const expectedSecondary = fault.expected_secondary_failures;
    const resultHashValid = harness.verifyResultHash(result);
    const restartHashValid = restartResult ? harness.verifyResultHash(restartResult) : true;
    const restartValid = fault.category !== 'restart'
      || (
        restartResult
        && restartResult.status === 'PASS'
        && result.status === 'FAIL'
        && result.failure
        && result.failure.code === expectedPrimary
      );
    const effectsClean = Object.values(result.effects).every(value => value === 0)
      && (!restartResult || Object.values(restartResult.effects).every(value => value === 0));
    const preserved = (
      result.status === 'FAIL'
      && primary === expectedPrimary
      && harness.stableJson(secondary) === harness.stableJson(expectedSecondary)
      && resultHashValid
      && restartHashValid
      && restartValid
      && effectsClean
    );
    cases.push({
      fault_id: fault.id,
      category: fault.category,
      injection: fault.injection,
      status: preserved ? 'FAULT_PRESERVED' : 'EVIDENCE_INVALID',
      expected_primary_failure: expectedPrimary,
      actual_primary_failure: primary,
      expected_secondary_failures: deep(expectedSecondary),
      actual_secondary_failures: secondary,
      original_failure_preserved: preserved,
      harness_result_hash_valid: resultHashValid,
      restart_result_hash_valid: restartHashValid,
      forbidden_effects_observed: !effectsClean,
      harness_result: result,
      restart: restartResult
        ? {
          generation: 1,
          status: restartResult.status,
          original_failure_code: primary,
          original_failure_result_sha256: result.result_sha256,
          result: restartResult,
        }
        : null,
    });
  }
  const output = {
    type: MATRIX_TYPE,
    version: VERSION,
    fault_catalog_sha256: harness.digest(faultCatalog),
    invariant_catalog_sha256: harness.digest(catalog),
    baseline_scenario_sha256: harness.digest(scenario),
    lane: 'deterministic_browser_harness',
    attempts: 1,
    automatic_retry_performed: false,
    special_authority_required: false,
    special_authority_consumed: false,
    status: cases.every(item => item.status === 'FAULT_PRESERVED')
      ? 'PASS'
      : 'FAIL_CLOSED',
    cases,
    summary: {
      faults_required: faultCatalog.required_categories.length,
      faults_executed: cases.length,
      faults_preserved: cases.filter(item => item.status === 'FAULT_PRESERVED').length,
      primary_failures_preserved: cases.filter(item => item.original_failure_preserved).length,
      secondary_failures_preserved: cases.filter(
        item => harness.stableJson(item.actual_secondary_failures)
          === harness.stableJson(item.expected_secondary_failures)
      ).length,
      restart_sequences: cases.filter(item => item.restart !== null).length,
      retries: 0,
      forbidden_effects: cases.filter(item => item.forbidden_effects_observed).length,
    },
    claim_ceiling: 'Deterministic synthetic fault-preservation evidence only; no live-app, production, repair, migration, persisted-user-data, later-pass, or formal-proof outcome is implied.',
  };
  output.result_sha256 = harness.digest(output);
  return output;
}

function verifyMatrixHash(result) {
  if (!result || typeof result.result_sha256 !== 'string') return false;
  const copy = deep(result);
  const expected = copy.result_sha256;
  delete copy.result_sha256;
  return harness.digest(copy) === expected;
}

function main() {
  const options = parseArgs(process.argv);
  const faultCatalog = JSON.parse(readTracked(options.faults));
  const catalog = JSON.parse(readTracked(options.catalog));
  const scenario = JSON.parse(readTracked(options.scenario));
  const result = runMatrix({ faultCatalog, catalog, scenario });
  const payload = JSON.stringify(result, null, 2) + '\n';
  if (options.output) fs.writeFileSync(path.resolve(options.output), payload);
  process.stdout.write(payload);
  if (result.status !== 'PASS') process.exitCode = 1;
}

if (require.main === module) main();

module.exports = Object.freeze({
  MATRIX_TYPE,
  VERSION,
  INJECTORS,
  runMatrix,
  verifyMatrixHash,
});
