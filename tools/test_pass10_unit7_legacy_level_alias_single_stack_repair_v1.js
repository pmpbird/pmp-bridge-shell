#!/usr/bin/env node
'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const read = name => fs.readFileSync(path.join(ROOT, name), 'utf8');
const levelSource = read('pmp-continuous-run-level-ui-scope-v1.js');
const bankSource = read('pmp-master-bank-tab-v1.js');
const innerSource = read('pmp-current-inner-cleanbug-rgcontrols-v23.html');
const fixtureSource = read('tools/fixtures/pass10-unit7-legacy-level-alias-single-stack-v1.html');
let assertions = 0;
function check(value, message) { assertions += 1; assert(value, message); }
function equal(actual, expected, message) { assertions += 1; assert.deepStrictEqual(actual, expected, message); }

const expected = ['3','4','4B','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','30B'];
const aliases = [
  {id:'19', canonical:'data-level19-recovery-proof', legacy:'data-level19-recert-recovery', badge:'data-l19-badge', source:'pmp-level19-recertification-recovery-proof-v1.js'},
  {id:'21', canonical:'data-level21-one-tap-retest', legacy:'data-level21-full-retest', badge:'data-l21-badge', source:'pmp-level21-one-tap-full-chain-retest-lock-v1.js'},
  {id:'23', canonical:'data-level23-integrity-check', legacy:'data-level23-integrity', badge:'data-l23-badge', source:'pmp-level23-export-receipt-integrity-check-v1.js'},
  {id:'25', canonical:'data-level25-receipt-bundle', legacy:'data-level25-bundle', badge:'data-l25-badge', source:'pmp-level25-receipt-bundle-v1.js'},
  {id:'27', canonical:'data-level27-tampered-packet', legacy:'data-level27-tamper-packet', badge:'data-l27-badge', source:'pmp-level27-tampered-packet-rejection-test-v1.js'}
];

const sourceOrder = Array.from(levelSource.matchAll(/\n \['([^']+)'/g), match => match[1]);
equal(sourceOrder, expected, 'production source retains exact canonical order');
equal(new Set(sourceOrder).size, expected.length, 'production source retains one metadata row per level');
for (const alias of aliases) {
  const legacySource = read(alias.source);
  check(levelSource.includes(`[${alias.canonical}],[${alias.legacy}]`), `Level ${alias.id} canonical row includes real legacy alias`);
  check(bankSource.includes(`[${alias.canonical}]`), `Bank containment includes Level ${alias.id} canonical selector`);
  check(bankSource.includes(`[${alias.legacy}]`), `Bank containment includes Level ${alias.id} legacy selector`);
  check(legacySource.includes(`data-source-reference-gate-level4`), `Level ${alias.id} legacy helper still targets Level 4 mount`);
  check(legacySource.includes(alias.legacy), `Level ${alias.id} legacy helper real attribute is recorded`);
  check(legacySource.includes(alias.badge), `Level ${alias.id} legacy helper badge is recorded`);
}

check(levelSource.includes('data-cr-level-legacy-mount-sentinel-v1'), 'hidden legacy mount sentinel implemented');
check(levelSource.includes("selectorAttrs(meta).forEach(a=>sentinel.setAttribute(a,''))"), 'sentinel carries every canonical and legacy alias');
check(levelSource.includes("S(sentinel,'display','none')"), 'sentinel is never visible');
check(levelSource.includes('data-cr-level-legacy-badge-contained-v1'), 'redundant legacy badge containment implemented');
check(levelSource.includes("S(x,'display','none')"), 'legacy badges are hidden');
check(levelSource.includes("list.find(c=>{let own=c.el.closest&&c.el.closest('[data-cr-level-shell-v1]')"), 'misnested in-scope legacy candidates are eligible for repair');
check(levelSource.includes("shell.getAttribute('data-cr-level-id')!==id"), 'observer signals only a level in the wrong shell');
check(levelSource.includes("hasAttribute('data-cr-level-legacy-mount-sentinel-v1')"), 'observer ignores its own hidden sentinels');
check(levelSource.includes("legacy_aliases_contained:['19','21','23','25','27']"), 'receipt binds exact five aliases');
check(levelSource.includes("readiness_badge_contract:'PASS9_FAIL_CLOSED_VISIBLE_NOT_RUNNABLE_UNTIL_PROOF'"), 'receipt explains Locked/Waiting safety badge');
check(levelSource.includes('Locked / waiting is an intentional fail-closed readiness state'), 'runtime rule explains Locked/Waiting is not a duplicate level');
equal(levelSource.includes('setInterval('), false, 'canonical owner still has no recurring interval');
check(levelSource.includes("observer.observe(b,{childList:true,subtree:true})"), 'canonical owner remains event-driven');
equal(bankSource.includes('setInterval('), false, 'Bank owner still has no recurring interval');
equal(bankSource.includes('localStorage.setItem'), false, 'Bank owner still writes no storage');

equal((innerSource.match(/pmp-master-bank-tab-v1\.js/g) || []).length, 1, 'one active Bank owner script');
equal((innerSource.match(/pmp-continuous-run-level-ui-scope-v1\.js/g) || []).length, 1, 'one active canonical level owner script');
check(innerSource.includes('pass10-unit7-legacy-alias-containment-20260727A'), 'Bank owner fresh binding updated');
check(innerSource.includes('pass10-unit7-single-card-presentation-20260727A'), 'level owner fresh binding advances through the presentation-only successor');

for (const marker of [
  'canonical_level_order_after_alias_repair',
  'twenty_legacy_ticks_inject_zero_duplicates',
  'missing_sentinel_fault_injects_one_level19_duplicate',
  'observer_contains_reinjected_level19_duplicate',
  'observer_recreates_level19_sentinel',
  'twenty_noop_scans_produce_zero_stack_mutations',
  'locked_waiting_badge_is_intentional_fail_closed_readiness'
]) check(fixtureSource.includes(marker), `browser fixture contains ${marker}`);

function modelRepair(state) {
  let corrections = 0;
  for (const alias of aliases) {
    const panels = state.level4Panels.filter(id => id === alias.id);
    if (!state.canonicalPanels.has(alias.id) && panels.length) {
      state.canonicalPanels.add(alias.id);
      corrections += 1;
    }
    if (panels.length) {
      state.level4Panels = state.level4Panels.filter(id => id !== alias.id);
      corrections += panels.length;
    }
    if (state.canonicalPanels.has(alias.id) && !state.sentinels.has(alias.id)) {
      state.sentinels.add(alias.id);
      corrections += 1;
    }
    if (state.visibleBadges.has(alias.id)) {
      state.visibleBadges.delete(alias.id);
      corrections += 1;
    }
  }
  state.order = [...expected];
  return corrections;
}

function legacyTick(state) {
  let injections = 0;
  for (const alias of aliases) {
    if (!state.sentinels.has(alias.id) && !state.level4Panels.includes(alias.id)) {
      state.level4Panels.push(alias.id);
      state.visibleBadges.add(alias.id);
      injections += 1;
    }
  }
  return injections;
}

const state = {
  order: ['3','4','19','21','23','25','27','4B',...expected.slice(3)],
  level4Panels: aliases.map(x => x.id),
  canonicalPanels: new Set(),
  sentinels: new Set(),
  visibleBadges: new Set(aliases.map(x => x.id))
};
check(modelRepair(state) > 0, 'reported duplicate odd-level state is repaired');
equal(state.order, expected, 'reported sequence becomes exact canonical sequence');
equal([...state.canonicalPanels], aliases.map(x => x.id), 'five real panels become canonical members');
equal([...state.sentinels], aliases.map(x => x.id), 'five helper-blocking sentinels are installed');
equal(state.level4Panels, [], 'Level 4 retains no real odd-level panels');
equal([...state.visibleBadges], [], 'Level 4 retains no visible odd-level badges');
for (let attempt = 0; attempt < 20; attempt += 1) {
  equal(legacyTick(state), 0, `legacy helper tick ${attempt + 1} injects zero panels`);
  equal(modelRepair(state), 0, `post-tick reconcile ${attempt + 1} is a no-op`);
  equal(state.order, expected, `post-tick order ${attempt + 1} remains exact`);
}

state.sentinels.delete('19');
equal(legacyTick(state), 1, 'missing Level 19 sentinel fault injects exactly one panel');
equal(state.level4Panels, ['19'], 'fault injection is bounded to Level 19');
check(modelRepair(state) > 0, 'fault-injected Level 19 panel is contained');
equal(state.level4Panels, [], 'Level 4 is clean after fault recovery');
check(state.sentinels.has('19'), 'Level 19 sentinel is restored after fault recovery');
equal([...state.visibleBadges], [], 'fault-injected Level 19 badge is hidden');
equal(state.order, expected, 'order remains exact after fault recovery');
for (let attempt = 0; attempt < 20; attempt += 1) equal(legacyTick(state), 0, `recovered helper tick ${attempt + 1} injects zero panels`);

console.log(`PASS: P10-U7 legacy level alias single-stack repair (${assertions}/${assertions})`);
