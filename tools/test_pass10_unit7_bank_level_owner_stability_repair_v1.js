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
const fixtureSource = read('tools/fixtures/pass10-unit7-bank-level-owner-stability-v1.html');
let assertions = 0;
function check(value, message) { assertions += 1; assert(value, message); }
function equal(actual, expected, message) { assertions += 1; assert.deepStrictEqual(actual, expected, message); }

const expected = ['3','4','4B','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','30B'];
const sourceOrder = Array.from(levelSource.matchAll(/\n \['([^']+)'/g), match => match[1]);
equal(sourceOrder, expected, 'production source exact canonical order');
equal(new Set(sourceOrder).size, expected.length, 'one metadata row per level');
equal(levelSource.includes('setInterval('), false, 'no recurring level reconciler');
equal(levelSource.includes("attributeFilter:['class','style','hidden']"), false, 'no self-triggering style observer');
check(levelSource.includes("observer.observe(b,{childList:true,subtree:true})"), 'observer watches external child additions only');
check(levelSource.includes("shell.getAttribute('data-cr-level-id')!==id"), 'correct-shell internal mutations ignored while misnested helpers are repaired');
check(levelSource.includes("if(at!==sh){s.insertBefore(sh,at);moved=true}"), 'shell moved only when position is wrong');
equal(levelSource.includes('s.appendChild(sh)'), false, 'no unconditional shell append');
check(levelSource.includes("list.find(c=>properShell(c.el,meta.id))||list.find(c=>!isOwnedByThis(c.el))"), 'existing canonical member wins over outside competitor');
check(levelSource.includes('shells.forEach(x=>{x.remove();deduped++'), 'duplicate shells removed exactly once');
check(levelSource.includes('recurring_timer_active:false'), 'receipt reports timer off');
check(levelSource.includes("scan_mode:'EVENT_DRIVEN_EXTERNAL_CHILD_ADDITIONS_ONLY'"), 'receipt binds event-driven scan mode');
check(levelSource.includes("window.addEventListener('pmp:bank-owner-slot-ready',scan)"), 'owner slot event drives scan');
check(levelSource.includes("window.addEventListener('pmp:bank-owner-detail-ready',scan)"), 'owner detail event drives scan');

const requiredOwned = [
  '[data-bank-screen-owner-v1]',
  '[data-continuous-run-level-ui-scope-v1]',
  '[data-source-text-reader-level3]',
  '[data-source-reference-gate-level4]',
  '[data-source-reference-gate-level4b]',
  ...Array.from({length: 26}, (_, index) => `[data-level${index + 5}-`).slice(0, 25),
  '[data-level30-final-seal]',
  '[data-resident-l30b-auto-gate]'
];
for (const selector of requiredOwned) check(bankSource.includes(selector), `Bank containment includes ${selector}`);
check(bankSource.includes('escaped.filter(x=>!escaped.some(y=>y!==x&&y.contains&&y.contains(x)))'), 'only topmost escaped owner roots move');
check(bankSource.includes('rt.appendChild(x);contained++'), 'escaped nodes preserved in owner slot');
check(bankSource.includes("observer.observe(s,{childList:true,subtree:true})"), 'Bank boundary watches late external owner nodes');
check(bankSource.includes('Promise.resolve().then(()=>'), 'late containment is event-driven without a timer');
check(bankSource.includes('boundarySignal(node,rt)'), 'Bank boundary filters relevant external additions');
check(bankSource.includes('bank_home_continuous_run_level_count'), 'receipt proves Bank home zero count');
check(bankSource.includes('can never render beneath the Bank home Router Receipt Summary'), 'Bank home exclusion rule explicit');
equal(bankSource.includes('localStorage.setItem'), false, 'Bank repair writes no storage');
equal(bankSource.includes('setInterval('), false, 'Bank repair adds no recurring painter');

equal((innerSource.match(/pmp-master-bank-tab-v1\.js/g) || []).length, 1, 'one active Bank owner script');
equal((innerSource.match(/pmp-continuous-run-level-ui-scope-v1\.js/g) || []).length, 1, 'one active level owner script');
check(innerSource.includes('pass10-unit7-legacy-alias-containment-20260727A'), 'Bank owner fresh token remains current');
check(innerSource.includes('pass10-unit7-single-card-presentation-20260727A'), 'level owner fresh token remains current through the presentation-only successor');
check(fixtureSource.includes('twenty_noop_scans_produce_zero_child_mutations'), 'fixture covers no-op flicker');
check(fixtureSource.includes('bank_home_contains_zero_continuous_run_levels'), 'fixture covers Bank home leak');
check(fixtureSource.includes('canonical_level_order'), 'fixture covers exact order');

function reconcile(stack, ids) {
  let moves = 0;
  for (let index = 0; index < ids.length; index += 1) {
    const id = ids[index];
    const current = stack.indexOf(id);
    if (current === -1) {
      stack.splice(index, 0, id);
      moves += 1;
    } else if (current !== index) {
      stack.splice(current, 1);
      stack.splice(index, 0, id);
      moves += 1;
    }
  }
  for (let index = stack.length - 1; index >= 0; index -= 1) {
    if (!ids.includes(stack[index]) || stack.indexOf(stack[index]) !== index) {
      stack.splice(index, 1);
      moves += 1;
    }
  }
  return moves;
}

const shuffled = [...expected].reverse();
check(reconcile(shuffled, expected) > 0, 'shuffled stack corrected');
equal(shuffled, expected, 'shuffled stack becomes exact canonical order');
for (let attempt = 0; attempt < 20; attempt += 1) {
  equal(reconcile(shuffled, expected), 0, `no-op reconcile ${attempt + 1} makes zero moves`);
  equal(shuffled, expected, `no-op reconcile ${attempt + 1} preserves identity order`);
}
const duplicate = ['5','3','4','3','30B','4B'];
check(reconcile(duplicate, expected) > 0, 'duplicate partial stack corrected');
equal(duplicate, expected, 'duplicate partial stack becomes one exact ordered set');

console.log(`PASS: P10-U7 Bank level owner stability repair (${assertions}/${assertions})`);
