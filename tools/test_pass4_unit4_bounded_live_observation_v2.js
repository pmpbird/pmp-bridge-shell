#!/usr/bin/env node
'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const {observerInitSource} = require('./run_pass4_unit4_bounded_live_observation_v2.js');

function makeDocument() {
  const nodes = new Map();
  return {
    nodes,
    getElementById(id) {
      return nodes.get(id) || null;
    }
  };
}

function runObserver(url) {
  const intervals = [];
  const document = makeDocument();
  class MutationObserver {
    constructor(callback) {
      this.callback = callback;
    }
    observe() {}
  }
  const context = {
    Date,
    JSON,
    MutationObserver,
    document,
    location: {href: url},
    setInterval(callback) {
      intervals.push(callback);
      return intervals.length;
    },
    globalThis: null
  };
  context.globalThis = context;
  vm.runInNewContext(observerInitSource(), context);
  return {context, document, intervals};
}

const frame = runObserver(
  'http://x/pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html'
);
let state = 'BOOTING';
const sideEffects = {
  routeAssignments: 0,
  persistedUserDataWrites: 0,
  appOrchestratorOwnershipTransfers: 0,
  startupRepairs: 0
};
frame.context.PMPAppOrchestratorV1 = {getLastLaunchGateReceipt() { return null; }};
frame.context.PMPBootStatusStripOwnerV1 = Object.freeze({
  contract: 'PMP_BOOT_STATUS_STRIP_PASSIVE_CONTRACT_V1',
  sideEffects,
  getLastStatus() {
    return {state, observed: {elapsed_ms: 1}};
  },
  statusFrom() {
    return {state, observed: {elapsed_ms: 1}};
  }
});
assert.strictEqual(frame.context.__PMP_UNIT4_FRAME_EVIDENCE__.assigned, true);
assert(frame.context.__PMP_UNIT4_FRAME_EVIDENCE__.states.includes('BOOTING'));
state = 'READY_ACKNOWLEDGED';
frame.intervals.forEach((callback) => callback());
assert(frame.context.__PMP_UNIT4_FRAME_EVIDENCE__.states.includes('READY_ACKNOWLEDGED'));
assert.strictEqual(frame.context.__PMP_UNIT4_FRAME_EVIDENCE__.app_orchestrator_present, true);
assert.strictEqual(frame.context.__PMP_UNIT4_FRAME_EVIDENCE__.app_orchestrator_acknowledged, true);
assert.deepStrictEqual(
  JSON.parse(JSON.stringify(frame.context.__PMP_UNIT4_FRAME_EVIDENCE__.sideEffects)),
  sideEffects
);

const source = fs.readFileSync(
  path.resolve(__dirname, 'run_pass4_unit4_bounded_live_observation_v2.js'),
  'utf8'
);
assert.strictEqual((source.match(/chromium\.launch\(/g) || []).length, 1);
assert.strictEqual((source.match(/page\.goto\(/g) || []).length, 1);
assert.strictEqual((source.match(/activateInstalledRunButton\(page\)/g) || []).length, 1);
assert(!/locator\.click\(/.test(source));
assert(!/force\s*:\s*true/.test(source));
assert(!/location\.(?:assign|replace)\(/.test(source));
assert(!/\.src\s*=/.test(source));
assert(!/workflow_dispatch/.test(source));

console.log('PASS: every-frame init observer captures BOOTING and READY_ACKNOWLEDGED');
console.log('PASS: runner binds one browser launch, one page navigation, and the merged DOM-click helper');
console.log('PASS: runner contains no Playwright action click, forced click, or observer-selected navigation');
