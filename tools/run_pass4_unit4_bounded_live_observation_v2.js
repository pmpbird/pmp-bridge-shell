#!/usr/bin/env node
'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const childProcess = require('child_process');
const {
  activateInstalledRunButton,
  classifyFrameUrl,
  installObserverOnEveryFrame,
  snapshotEveryFrame
} = require('./pass4_unit4_route_guardian_interaction_boundary_v1.js');

const ROOT = path.resolve(__dirname, '..');
const BASE = '0bb3a42907ca1a2f864c1a40d1ace3f203cd7e45';
const BRANCH = 'agent/pass4-unit4-bounded-live-observation-v2';
const ENTRY = 'http://127.0.0.1:4176/pmp-app-current.html';
const AUTH = path.join(ROOT, 'audit/pass4/pass4-boot-status-strip-unit4-live-observation-authorization-v2.json');
const DIRECTIVE = path.join(ROOT, 'audit/pass4/pass4-boot-status-strip-unit4-live-observation-directive-v2.json');
const RESULT = path.join(ROOT, 'audit/pass4/pass4-boot-status-strip-unit4-live-observation-result-v2.json');

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function git(...args) {
  return childProcess.execFileSync('git', args, {cwd: ROOT, encoding: 'utf8'}).trim();
}

function observerInitSource() {
  return `(() => {
    const root = globalThis;
    const evidence = root.__PMP_UNIT4_FRAME_EVIDENCE__ = {
      href: String(location.href),
      assigned: false,
      contract: null,
      sideEffects: null,
      states: [],
      samples: [],
      errors: [],
      poll_count: 0,
      app_orchestrator_present: false,
      app_orchestrator_acknowledged: false,
      route_ready: false,
      runtime_ready: false
    };
    let apiValue;
    const pushError = (error) => {
      if (evidence.errors.length < 20) evidence.errors.push(String(error && error.message || error));
    };
    const pushState = (state, reason, observed) => {
      if (!state) return;
      if (!evidence.states.includes(state)) evidence.states.push(state);
      const prior = evidence.samples[evidence.samples.length - 1];
      if (!prior || prior.state !== state || reason === 'assignment' || reason === 'dom') {
        if (evidence.samples.length < 200) {
          evidence.samples.push({reason, state, observed: observed || null, at: Date.now()});
        }
      }
    };
    function record(api, reason) {
      try {
        evidence.poll_count += 1;
        if (api) {
          evidence.assigned = true;
          evidence.contract = api.contract || null;
          evidence.sideEffects = api.sideEffects || null;
          let status = null;
          if (typeof api.getLastStatus === 'function') status = api.getLastStatus();
          if (!status && typeof api.statusFrom === 'function') status = api.statusFrom(null);
          if (status) pushState(status.state, reason, status.observed || null);
        }
        const strip = document.getElementById('pmpAppOrchestratorBootStatusStripV1');
        if (strip) pushState(strip.getAttribute('data-state'), 'dom', null);
        const ready = (id) => document.getElementById(id)?.getAttribute('data-ready') === 'true';
        const orchestrator = root.PMPAppOrchestratorV1;
        evidence.app_orchestrator_present = !!orchestrator;
        evidence.app_orchestrator_acknowledged =
          ready('bootOrchestrator') ||
          !!(orchestrator && typeof orchestrator.getLastLaunchGateReceipt === 'function');
        evidence.route_ready = ready('bootRoute');
        evidence.runtime_ready = ready('bootRuntime');
      } catch (error) {
        pushError(error);
      }
    }
    Object.defineProperty(root, 'PMPBootStatusStripOwnerV1', {
      configurable: true,
      enumerable: true,
      get() { return apiValue; },
      set(value) {
        apiValue = value;
        record(value, 'assignment');
      }
    });
    try {
      new MutationObserver(() => record(apiValue, 'mutation')).observe(
        document,
        {subtree: true, childList: true, attributes: true}
      );
    } catch (error) {
      pushError(error);
    }
    setInterval(() => record(apiValue, 'poll'), 25);
  })();`;
}

function verifyUnconsumedEntry() {
  const auth = readJson(AUTH);
  const directive = readJson(DIRECTIVE);
  const result = readJson(RESULT);
  const head = git('rev-parse', 'HEAD');
  assert.strictEqual(process.env.BASE_SHA, BASE);
  assert.strictEqual(process.env.PR_HEAD_SHA, head);
  assert.strictEqual(process.env.PR_HEAD_REF, BRANCH);
  assert.strictEqual(process.env.EVENT_ACTION, 'opened');
  assert(![122, 149, 150].includes(Number(process.env.PR_NUMBER)));
  assert.strictEqual(auth.status, 'AUTHORIZED_UNCONSUMED');
  assert.strictEqual(auth.authorization_consumed, false);
  assert.strictEqual(auth.observation_runs_authorized, 1);
  assert.strictEqual(auth.observation_runs_previously_executed_under_this_authorization, 0);
  assert.strictEqual(directive.status, 'SEALED_STATIC_ONLY_UNCONSUMED');
  assert.strictEqual(directive.authorization_consumed, false);
  assert.strictEqual(directive.authorized_observation_count, 1);
  assert.strictEqual(directive.previously_executed_count, 0);
  assert.strictEqual(result.status, 'AWAITING_AUTHORIZED_OBSERVATION');
  assert.strictEqual(result.authorization_consumed, false);
  assert.strictEqual(result.observation_consumed, false);
  assert.strictEqual(result.observation_count, 0);
  return head;
}

async function main() {
  const authorizedHead = verifyUnconsumedEntry();
  const {chromium} = require('playwright');
  const startedAt = new Date().toISOString();
  const receipt = {
    type: 'PMP_PASS4_BOOT_STATUS_STRIP_UNIT4_LIVE_OBSERVATION_RESULT_V2',
    version: '2.0.0',
    status: 'FAIL_PRESERVED',
    pass: 4,
    unit: 4,
    substep: 'P4-U4O',
    authorized_base_main_commit: BASE,
    authorized_head_commit: authorizedHead,
    authorized_branch: BRANCH,
    pull_request: Number(process.env.PR_NUMBER),
    workflow_run_id: Number(process.env.GITHUB_RUN_ID || 0),
    authorization_consumed: true,
    observation_consumed: true,
    observation_count: 1,
    browser_launch_count: 0,
    browser_navigation_count: 0,
    entry: ENTRY,
    started_at: startedAt,
    activation: null,
    frame_roles_observed: [],
    frame_url_history: [],
    observed_states: [],
    booting_observed: false,
    ready_acknowledged_observed: false,
    boot_slow_naturally_observed: false,
    boot_failure_naturally_observed: false,
    boot_status_strip_api_assigned: false,
    app_orchestrator_acknowledged: false,
    zero_effect_evidence: {strip_declared_side_effects: null},
    console_errors: [],
    page_errors: [],
    production_runtime_changed: false,
    runtime_integrity_changed: false,
    persisted_user_data_changed: false,
    historical_failure_evidence_changed: false,
    unit5_started: false,
    pass4_complete_claimed: false,
    pass5_started: false,
    formal_proof_run: false,
    pr122_touched: false,
    retry_authorized: false,
    claim_ceiling: 'Exactly one newly sealed bounded live startup observation. No retry, formal proof, production activation, persisted-user-data mutation, Unit 5, Pass 5, or broad production correctness is claimed.'
  };
  let browser = null;
  try {
    receipt.browser_launch_count = 1;
    browser = await chromium.launch({headless: true});
    const context = await browser.newContext();
    receipt.observer_installation = await installObserverOnEveryFrame(context, observerInitSource());
    const page = await context.newPage();
    page.on('console', (message) => {
      if (message.type() === 'error' && receipt.console_errors.length < 50) {
        receipt.console_errors.push(message.text());
      }
    });
    page.on('pageerror', (error) => {
      if (receipt.page_errors.length < 50) receipt.page_errors.push(String(error && error.message || error));
    });
    await page.goto(ENTRY, {waitUntil: 'domcontentloaded', timeout: 30000});
    receipt.browser_navigation_count = 1;
    await page.waitForTimeout(500);
    receipt.activation = await activateInstalledRunButton(page);

    const roles = new Set();
    const urls = new Set();
    const states = new Set();
    let assigned = false;
    let acknowledged = false;
    let sideEffects = null;
    const deadline = Date.now() + 30000;
    while (Date.now() < deadline) {
      const snapshots = await snapshotEveryFrame(page);
      for (const snapshot of snapshots) {
        roles.add(snapshot.role);
        if (snapshot.url) urls.add(snapshot.url);
        const evidence = snapshot.evidence;
        if (!evidence) continue;
        for (const state of evidence.states || []) states.add(state);
        if (snapshot.role === 'current_inner_v30') {
          assigned = assigned || evidence.assigned === true;
          acknowledged = acknowledged || evidence.app_orchestrator_acknowledged === true;
          if (evidence.sideEffects) sideEffects = evidence.sideEffects;
        }
      }
      receipt.frame_roles_observed = [...roles];
      receipt.frame_url_history = [...urls];
      receipt.observed_states = [...states];
      if (
        roles.has('route_guardian_v22') &&
        roles.has('reload_owner_v30') &&
        roles.has('current_inner_v30') &&
        assigned &&
        acknowledged &&
        states.has('BOOTING') &&
        states.has('READY_ACKNOWLEDGED')
      ) {
        break;
      }
      await page.waitForTimeout(50);
    }

    receipt.booting_observed = states.has('BOOTING');
    receipt.ready_acknowledged_observed = states.has('READY_ACKNOWLEDGED');
    receipt.boot_slow_naturally_observed = states.has('BOOT_SLOW');
    receipt.boot_failure_naturally_observed = states.has('BOOT_FAILURE');
    receipt.boot_status_strip_api_assigned = assigned;
    receipt.app_orchestrator_acknowledged = acknowledged;
    receipt.zero_effect_evidence.strip_declared_side_effects = sideEffects;
    const expectedSideEffects = {
      routeAssignments: 0,
      persistedUserDataWrites: 0,
      appOrchestratorOwnershipTransfers: 0,
      startupRepairs: 0
    };
    const requiredRoles = ['top', 'route_guardian_v22', 'reload_owner_v30', 'current_inner_v30'];
    const passed =
      requiredRoles.every((role) => roles.has(role)) &&
      assigned &&
      acknowledged &&
      receipt.booting_observed &&
      receipt.ready_acknowledged_observed &&
      JSON.stringify(sideEffects) === JSON.stringify(expectedSideEffects) &&
      receipt.browser_launch_count === 1 &&
      receipt.browser_navigation_count === 1;
    receipt.status = passed ? 'PASS' : 'FAIL_PRESERVED';
    if (!passed) {
      receipt.failure_reason = 'Required nested-frame states, acknowledgement, exact counts, or zero-effect evidence were incomplete.';
    }
  } catch (error) {
    receipt.failure_reason = String(error && error.stack || error);
  } finally {
    receipt.finished_at = new Date().toISOString();
    if (browser) await browser.close();
    fs.writeFileSync(RESULT, JSON.stringify(receipt, null, 2) + '\n');
    console.log(JSON.stringify(receipt, null, 2));
  }
}

if (require.main === module) {
  main().catch((error) => {
    console.error(error && error.stack || error);
    process.exitCode = 1;
  });
}

module.exports = {observerInitSource, verifyUnconsumedEntry};
