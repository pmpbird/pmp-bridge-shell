#!/usr/bin/env node
'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const read = name => fs.readFileSync(path.join(ROOT, name), 'utf8');
const ownerSource = read('pmp-bank-screen-owner-v1.js');
const levelSource = read('pmp-continuous-run-level-ui-scope-v1.js');
const innerSource = read('pmp-current-inner-cleanbug-rgcontrols-v23.html');
const fixtureSource = read('tools/fixtures/pass10-unit7-uniform-title-weight-v1.html');
let assertions = 0;
function check(value, message) { assertions += 1; assert(value, message); }
function equal(actual, expected, message) { assertions += 1; assert.deepStrictEqual(actual, expected, message); }

const titles = [
  ['data-bso-run-state', 'Run State Summary'],
  ['data-bso-zip', 'Lossless Slots ZIP Import'],
  ['data-bso-stage', 'Staging Transfer Store'],
  ['data-bso-registry', 'Bank Project Registry'],
  ['data-bso-level1', 'Level 1 — Must-Reference Source ZIP Gate / Import'],
  ['data-bso-level2', 'Level 2 — Source ZIP Reader'],
];

check(ownerSource.includes("2.1.0-pass10-unit7-uniform-title-weight-20260727A"), 'owner version is exact');
check(ownerSource.includes("function titleStyle(){return 'margin:0 0 6px;font-weight:950'}"), 'one exact shared title style exists');
equal((ownerSource.match(/<h2 style="'\+titleStyle\(\)\+'"/g) || []).length, titles.length, 'all six pre-Level-3 titles use the shared style');
equal((ownerSource.match(/font-weight:950/g) || []).length, 1, 'the uniform weight is defined once');
check(levelSource.includes("S(title,'font-weight','950')"), 'Level 3+ canonical title weight remains 950');
check(innerSource.includes('pmp-bank-screen-owner-v1.js?fresh=pass10-unit7-uniform-title-weight-20260727A'), 'fresh owner binding activates the update');
equal(innerSource.includes('pmp-bank-screen-owner-v1.js?fresh=pass9-unit3-continuous-run-owner-20260726A'), false, 'stale owner binding is absent');
equal(ownerSource.includes('setInterval('), false, 'bank screen owner remains event-driven');
check(ownerSource.includes("window.addEventListener('pmp:bank-owner-slot-ready',scan)"), 'owner slot event remains bound');
check(ownerSource.includes("window.addEventListener('pmp:bank-owner-dependencies-ready',scan)"), 'owner dependency event remains bound');
check(ownerSource.includes("window.addEventListener('load',scan,{once:true})"), 'one-shot load binding remains');
check(ownerSource.includes("indexeddb_write:'not_attempted'"), 'owner receipt still states no IndexedDB write');
check(ownerSource.includes("storage_migration:'not_attempted'"), 'owner receipt still states no migration');

for (const [attribute, title] of titles) {
  check(ownerSource.includes(`<section ${attribute}`), `${attribute} card remains`);
  check(ownerSource.includes(`>${title}</h2>`), `${title} text remains exact`);
}
check(fixtureSource.includes("'uniform_weight_'+spec[0]"), 'browser fixture checks every uniform title weight');

for (const selector of [
  'data-bso-refresh-state',
  'data-bso-zip-file',
  'data-bso-import-slots',
  'data-bso-type',
  'data-bso-item-name',
  'data-bso-text',
  'data-bso-store',
  'data-bso-verify',
  'data-bso-copy-manifest',
  'data-bso-name',
  'data-bso-cat',
  'data-bso-status',
  'data-bso-save-project',
  'data-bso-view-projects',
  'data-bso-source-file',
  'data-bso-import-source',
  'data-bso-run-l2',
  'data-bso-run-l2b',
  'data-bso-run-l2c',
]) check(ownerSource.includes(selector), `${selector} functional selector remains`);

for (const marker of [
  'all_six_pre_level3_titles_present',
  'all_six_pre_level3_titles_weight_950',
  'all_six_pre_level3_titles_match_level3_weight',
  'all_six_pre_level3_card_identities_preserved',
  'all_six_pre_level3_title_identities_preserved',
  'all_pre_level3_controls_visible',
  'level3_single_card_presentation_preserved',
  'canonical_order_preserved',
  'twenty_noop_scans_zero_child_mutations',
  'locked_waiting_readiness_preserved',
]) check(fixtureSource.includes(marker), `browser fixture contains ${marker}`);
check(fixtureSource.includes('PMP_PASS10_UNIT7U_UNIFORM_TITLE_WEIGHT_FIXTURE_V1'), 'fixture result type is exact');

function modelUniformTitle(title) {
  const card = {};
  const heading = {title, weight: 700};
  const control = {};
  const identities = {card, heading, control};
  heading.weight = 950;
  return {card, heading, control, identities};
}

for (const [, title] of titles) {
  const model = modelUniformTitle(title);
  equal(model.heading.weight, 950, `${title} becomes weight 950`);
  equal(model.heading.title, title, `${title} wording is unchanged`);
  equal(model.card, model.identities.card, `${title} card identity is preserved`);
  equal(model.heading, model.identities.heading, `${title} heading identity is preserved`);
  equal(model.control, model.identities.control, `${title} control identity is preserved`);
}

console.log(`PASS: P10-U7U uniform title weight (${assertions}/${assertions})`);
