#!/usr/bin/env node
'use strict';

const ROUTE_GUARDIAN_V22 = /pmp-route-guardian-current-loader-v22\.html(?:[?#]|$)/;

function classifyFrameUrl(url) {
  const value = String(url || '');
  if (/pmp-app-current\.html(?:[?#]|$)/.test(value)) return 'top';
  if (ROUTE_GUARDIAN_V22.test(value)) return 'route_guardian_v22';
  if (/pmp-current-reload-owner-v30-direct-boot-surface-20260708A\.html(?:[?#]|$)/.test(value)) {
    return 'reload_owner_v30';
  }
  if (/pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A\.html(?:[?#]|$)/.test(value)) {
    return 'current_inner_v30';
  }
  return 'other';
}

async function installObserverOnEveryFrame(context, observerSource) {
  if (!context || typeof context.addInitScript !== 'function') {
    throw new Error('A browser context with addInitScript is required.');
  }
  if (typeof observerSource !== 'string' || observerSource.length === 0) {
    throw new Error('A non-empty observer source is required.');
  }
  await context.addInitScript({content: observerSource});
  return Object.freeze({
    installation: 'BROWSER_CONTEXT_ADD_INIT_SCRIPT',
    applies_to_existing_and_new_frames: true
  });
}

function findSingleRouteGuardianFrame(page) {
  if (!page || typeof page.frames !== 'function') {
    throw new Error('A page with frame enumeration is required.');
  }
  const matches = page.frames().filter((frame) => classifyFrameUrl(frame.url()) === 'route_guardian_v22');
  if (matches.length !== 1) {
    throw new Error(`Expected exactly one Route Guardian v22 frame; found ${matches.length}.`);
  }
  return matches[0];
}

async function activateInstalledRunButton(page) {
  const guardian = findSingleRouteGuardianFrame(page);
  const locator = guardian.locator('#openBtn');
  const count = await locator.count();
  if (count !== 1) {
    throw new Error(`Expected exactly one Route Guardian #openBtn; found ${count}.`);
  }
  const activation = await locator.evaluate((button) => {
    if (!button || typeof button.click !== 'function') {
      throw new Error('Route Guardian #openBtn does not expose the DOM click boundary.');
    }
    button.click();
    return {
      id: String(button.id || ''),
      tag_name: String(button.tagName || '').toUpperCase(),
      method: 'DOM_ELEMENT_CLICK'
    };
  });
  return Object.freeze({
    frame_url: guardian.url(),
    locator: '#openBtn',
    activation
  });
}

async function snapshotEveryFrame(page) {
  if (!page || typeof page.frames !== 'function') {
    throw new Error('A page with frame enumeration is required.');
  }
  const snapshots = [];
  for (const frame of page.frames()) {
    let evidence = null;
    try {
      evidence = await frame.evaluate(() => globalThis.__PMP_UNIT4_FRAME_EVIDENCE__ || null);
    } catch (error) {
      evidence = {observer_error: String(error && error.message || error)};
    }
    snapshots.push({
      url: frame.url(),
      role: classifyFrameUrl(frame.url()),
      evidence
    });
  }
  return snapshots;
}

module.exports = {
  ROUTE_GUARDIAN_V22,
  activateInstalledRunButton,
  classifyFrameUrl,
  findSingleRouteGuardianFrame,
  installObserverOnEveryFrame,
  snapshotEveryFrame
};
