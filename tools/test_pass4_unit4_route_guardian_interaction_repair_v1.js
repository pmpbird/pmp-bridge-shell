#!/usr/bin/env node
'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const {
  activateInstalledRunButton,
  classifyFrameUrl,
  findSingleRouteGuardianFrame,
  installObserverOnEveryFrame,
  snapshotEveryFrame
} = require('./pass4_unit4_route_guardian_interaction_boundary_v1.js');

function makeFrame(url, evidence) {
  return {
    observerSources: [],
    url: () => url,
    evaluate: async (fn) => {
      const prior = globalThis.__PMP_UNIT4_FRAME_EVIDENCE__;
      globalThis.__PMP_UNIT4_FRAME_EVIDENCE__ = evidence;
      try {
        return fn();
      } finally {
        if (prior === undefined) delete globalThis.__PMP_UNIT4_FRAME_EVIDENCE__;
        else globalThis.__PMP_UNIT4_FRAME_EVIDENCE__ = prior;
      }
    }
  };
}

async function main() {
  const top = makeFrame('http://x/pmp-app-current.html', {frame: 'top'});
  const guardian = makeFrame(
    'http://x/pmp-route-guardian-current-loader-v22.html?route_authority=pmp-current-map-v12.json',
    {frame: 'route_guardian_v22'}
  );
  const reload = makeFrame(
    'http://x/pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html',
    {frame: 'reload_owner_v30'}
  );
  const inner = makeFrame(
    'http://x/pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html',
    {frame: 'current_inner_v30'}
  );
  const frames = [top, guardian, reload, inner];

  let installedHandlerInvocations = 0;
  let domClickInvocations = 0;
  let locatorEvaluateInvocations = 0;
  let playwrightActionClickInvocations = 0;
  let geometrySample = 0;
  const button = {
    id: 'openBtn',
    tagName: 'BUTTON',
    className: 'runFlash',
    getBoundingClientRect() {
      geometrySample += 1;
      return {width: 200 + geometrySample, height: 40 + geometrySample};
    },
    onclick(event) {
      installedHandlerInvocations += 1;
      if (event) event.preventDefault();
      return false;
    },
    click() {
      domClickInvocations += 1;
      return this.onclick({preventDefault() {}});
    }
  };
  const runLocator = {
    count: async () => 1,
    click: async () => {
      playwrightActionClickInvocations += 1;
      throw new Error('Normal Playwright action click is intentionally unstable.');
    },
    evaluate: async (fn) => {
      locatorEvaluateInvocations += 1;
      return fn(button);
    }
  };
  guardian.locator = (selector) => {
    assert.strictEqual(selector, '#openBtn');
    return runLocator;
  };

  let browserNavigationCount = 1;
  let observerSelectedDestination = null;
  const page = {
    frames: () => frames,
    goto: async () => {
      browserNavigationCount += 1;
      throw new Error('The interaction helper must not navigate.');
    }
  };

  const observerSource = 'globalThis.__PMP_UNIT4_FRAME_EVIDENCE__ = {attached:true};';
  const context = {
    addInitScriptCalls: 0,
    async addInitScript({content}) {
      this.addInitScriptCalls += 1;
      for (const frame of frames) frame.observerSources.push(content);
    }
  };
  const installation = await installObserverOnEveryFrame(context, observerSource);
  assert.strictEqual(installation.applies_to_existing_and_new_frames, true);
  assert.strictEqual(context.addInitScriptCalls, 1);
  assert(frames.every((frame) => frame.observerSources.length === 1));
  assert(frames.every((frame) => frame.observerSources[0] === observerSource));

  assert.strictEqual(findSingleRouteGuardianFrame(page), guardian);
  const activation = await activateInstalledRunButton(page);
  assert.strictEqual(activation.locator, '#openBtn');
  assert.strictEqual(activation.activation.method, 'DOM_ELEMENT_CLICK');
  assert.strictEqual(locatorEvaluateInvocations, 1);
  assert.strictEqual(domClickInvocations, 1);
  assert.strictEqual(installedHandlerInvocations, 1);
  assert.strictEqual(playwrightActionClickInvocations, 0);
  assert.strictEqual(browserNavigationCount, 1);
  assert.strictEqual(observerSelectedDestination, null);

  button.getBoundingClientRect();
  button.getBoundingClientRect();
  assert.notStrictEqual(button.getBoundingClientRect().width, button.getBoundingClientRect().width);
  assert.strictEqual(installedHandlerInvocations, 1);

  const snapshots = await snapshotEveryFrame(page);
  assert.deepStrictEqual(
    snapshots.map((snapshot) => snapshot.role),
    ['top', 'route_guardian_v22', 'reload_owner_v30', 'current_inner_v30']
  );
  assert.strictEqual(snapshots.length, frames.length);
  assert.deepStrictEqual(
    frames.map((frame) => classifyFrameUrl(frame.url())),
    ['top', 'route_guardian_v22', 'reload_owner_v30', 'current_inner_v30']
  );

  const duplicateGuardianPage = {frames: () => [guardian, guardian]};
  assert.throws(
    () => findSingleRouteGuardianFrame(duplicateGuardianPage),
    /Expected exactly one Route Guardian/
  );

  const source = fs.readFileSync(
    path.resolve(__dirname, 'pass4_unit4_route_guardian_interaction_boundary_v1.js'),
    'utf8'
  );
  const guardianSource = fs.readFileSync(
    path.resolve(__dirname, '../pmp-route-guardian-current-loader-v22.html'),
    'utf8'
  );
  assert(/\.runFlash\{[^}]*animation:pmpRunFlash 1s infinite/.test(guardianSource));
  assert(/@keyframes pmpRunFlash\{[^}]*transform:scale\(1\)/.test(guardianSource));
  assert(/btn\.onclick=function\(e\)\{[^}]*launch\('run'\)/.test(guardianSource));
  assert(source.includes('locator.evaluate'));
  assert(source.includes('button.click()'));
  assert(!/force\s*:\s*true/.test(source));
  assert(!/\.goto\s*\(/.test(source));
  assert(!/location\.(?:href|assign|replace)\s*=*\s*/.test(source));
  assert(!/\.src\s*=/.test(source));
  assert(!/\blaunch\s*\(/.test(source));

  console.log('PASS: deterministic Route Guardian DOM click invokes the installed handler once');
  console.log('PASS: continuously changing geometry cannot block the activation boundary');
  console.log('PASS: no Playwright action click, extra navigation, or observer-selected route is used');
  console.log('PASS: the observer installation and snapshot boundary covers every frame');
}

main().catch((error) => {
  console.error(error && error.stack || error);
  process.exitCode = 1;
});
