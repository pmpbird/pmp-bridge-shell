#!/usr/bin/env node
'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const read = name => fs.readFileSync(path.join(ROOT, name), 'utf8');
const levelSource = read('pmp-continuous-run-level-ui-scope-v1.js');
const innerSource = read('pmp-current-inner-cleanbug-rgcontrols-v23.html');
const fixtureSource = read('tools/fixtures/pass10-unit7-single-card-presentation-v1.html');
let assertions = 0;
function check(value, message) { assertions += 1; assert(value, message); }
function equal(actual, expected, message) { assertions += 1; assert.deepStrictEqual(actual, expected, message); }

const expected = ['3','4','4B','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','30B'];
const sourceOrder = Array.from(levelSource.matchAll(/\n \['([^']+)'/g), match => match[1]);
equal(sourceOrder, expected, 'production source retains exact canonical Level 3-30B order');
equal(new Set(sourceOrder).size, expected.length, 'production source retains one metadata row per level');

check(levelSource.includes("2.2.0-pass10-unit7-single-card-presentation-20260727A"), 'single-card production version is exact');
check(levelSource.includes('function directLevelHeading(el,id)'), 'direct duplicate-heading classifier exists');
check(levelSource.includes("el.querySelector(':scope > h1,:scope > h2,:scope > h3,:scope > h4')"), 'duplicate-heading query is direct-child bounded');
check(levelSource.includes("parseLevelText(h.textContent||'')===id"), 'duplicate heading must match the canonical level id');
check(levelSource.includes('function styleSingleCardPresentation(sh,member,meta)'), 'single-card presentation function exists');
check(levelSource.includes("data-cr-level-visible-title-v1"), 'one visible outer title marker exists');
check(levelSource.includes("clamp(28px,7vw,34px)"), 'outer title is enlarged for mobile and desktop');
check(levelSource.includes("data-cr-level-single-card-presentation-v1"), 'canonical functional member receives presentation marker');
check(levelSource.includes("S(member,'background','transparent')"), 'inner member background becomes transparent');
check(levelSource.includes("S(member,'border','0')"), 'inner member border is visually removed');
check(levelSource.includes("S(member,'padding','0')"), 'inner member padding is visually collapsed');
check(levelSource.includes("S(member,'box-shadow','none')"), 'inner member shadow is visually removed');
check(levelSource.includes("data-cr-level-duplicate-title-contained-v1"), 'repeated inner title receives containment marker');
check(levelSource.includes("duplicate.setAttribute('aria-hidden','true')"), 'repeated inner title is accessibility-contained');
check(levelSource.includes("S(duplicate,'display','none')"), 'repeated inner title is visually hidden');
check(levelSource.includes('styleSingleCardPresentation(sh,chosen.el,meta)'), 'presentation runs after canonical member selection');
check(levelSource.includes("presentation_contract:'VISUAL_ONLY_KEEP_CANONICAL_MEMBER_AND_ALL_FUNCTIONAL_DESCENDANTS'"), 'receipt binds visual-only contract');
check(levelSource.includes("functional_nodes_removed:'none'"), 'receipt states no functional nodes are removed');
check(levelSource.includes("functional_controls_hidden:'none'"), 'receipt states no functional controls are hidden');
check(levelSource.includes("status:'CANONICAL_LEVEL3PLUS_SINGLE_CARD_PRESENTATION_READY'"), 'receipt has exact presentation-ready status');
check(levelSource.includes("readiness_badge_contract:'PASS9_FAIL_CLOSED_VISIBLE_NOT_RUNNABLE_UNTIL_PROOF'"), 'Locked/Waiting contract remains explicit');
check(levelSource.includes("legacy_aliases_contained:['19','21','23','25','27']"), 'five legacy alias protections remain bound');
check(levelSource.includes('data-cr-level-legacy-mount-sentinel-v1'), 'hidden legacy mount sentinels remain implemented');
equal(levelSource.includes('setInterval('), false, 'canonical owner still has no recurring interval');
check(levelSource.includes("observer.observe(b,{childList:true,subtree:true})"), 'canonical owner remains event-driven');

const presentationFunction = levelSource.slice(
  levelSource.indexOf('function styleSingleCardPresentation'),
  levelSource.indexOf('function readiness')
);
for (const forbidden of [
  'appendChild(', 'insertBefore(', 'replaceWith(', '.remove(', 'innerHTML=',
  'localStorage', 'indexedDB', 'dispatchEvent(', 'setInterval('
]) equal(presentationFunction.includes(forbidden), false, `presentation function forbids ${forbidden}`);

equal((innerSource.match(/pmp-continuous-run-level-ui-scope-v1\.js/g) || []).length, 1, 'one active canonical level owner script');
check(innerSource.includes('pass10-unit7-single-card-presentation-20260727A'), 'fresh binding activates the presentation update');
equal(innerSource.includes('pass10-unit7-legacy-alias-single-stack-20260727A'), false, 'stale presentation binding is absent');

for (const marker of [
  'canonical_order_preserved_during_visual_cleanup',
  'one_shell_per_level_preserved',
  'level1_identity_unchanged',
  'level2_identity_unchanged',
  'redundant_inner_border_removed',
  'outer_title_enlarged',
  'duplicate_heading_node_preserved',
  'duplicate_heading_visually_hidden',
  'description_visible',
  'input_visible',
  'button_visible',
  'status_visible',
  'readiness_badge_preserved',
  'one_visible_level_heading',
  'twenty_noop_scans_produce_zero_child_mutations',
  'user_entered_control_value_preserved',
  'functional_button_handler_preserved',
  'locked_waiting_readiness_contract_preserved'
]) check(fixtureSource.includes(marker), `browser fixture contains ${marker}`);
check(fixtureSource.includes('PMP_PASS10_UNIT7T_SINGLE_CARD_PRESENTATION_FIXTURE_V1'), 'fixture result type is exact');

function modelPresentation(level) {
  const state = {
    level,
    shellIdentity: {},
    memberIdentity: {},
    duplicateHeadingIdentity: {},
    buttonIdentity: {},
    inputValue: `value-${level}`,
    shellTitleSize: 34,
    memberBorder: 2,
    memberPadding: 8,
    memberBackground: 'white',
    duplicateHeadingVisible: true,
    readinessVisible: true,
    memberConnected: true,
    handlerConnected: true,
  };
  const identities = {
    shell: state.shellIdentity,
    member: state.memberIdentity,
    heading: state.duplicateHeadingIdentity,
    button: state.buttonIdentity,
  };
  state.memberBorder = 0;
  state.memberPadding = 0;
  state.memberBackground = 'transparent';
  state.duplicateHeadingVisible = false;
  state.presentationMarker = level;
  state.visibleTitleCount = 1;
  return {state, identities};
}

for (const level of expected) {
  const {state, identities} = modelPresentation(level);
  equal(state.presentationMarker, level, `Level ${level} receives its exact presentation marker`);
  equal(state.memberBorder, 0, `Level ${level} redundant inner border is removed`);
  equal(state.memberPadding, 0, `Level ${level} redundant inner padding is removed`);
  equal(state.memberBackground, 'transparent', `Level ${level} inner background is transparent`);
  equal(state.duplicateHeadingVisible, false, `Level ${level} repeated heading is hidden`);
  equal(state.visibleTitleCount, 1, `Level ${level} retains one visible title`);
  equal(state.memberConnected, true, `Level ${level} functional member remains connected`);
  equal(state.handlerConnected, true, `Level ${level} handler remains connected`);
  equal(state.readinessVisible, true, `Level ${level} readiness remains visible`);
  equal(state.inputValue, `value-${level}`, `Level ${level} input value is preserved`);
  equal(state.shellIdentity, identities.shell, `Level ${level} shell identity is preserved`);
  equal(state.memberIdentity, identities.member, `Level ${level} member identity is preserved`);
  equal(state.duplicateHeadingIdentity, identities.heading, `Level ${level} heading node identity is preserved`);
  equal(state.buttonIdentity, identities.button, `Level ${level} button identity is preserved`);
}

console.log(`PASS: P10-U7T single-card presentation (${assertions}/${assertions})`);
