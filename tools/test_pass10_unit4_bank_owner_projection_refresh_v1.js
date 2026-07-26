#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const source = name => fs.readFileSync(path.join(ROOT, name), 'utf8');
let assertions = 0;
function check(value, label) {
  assertions += 1;
  if (!value) throw new Error(`assertion failed: ${label}`);
}
function equal(actual, expected, label) {
  assertions += 1;
  if (JSON.stringify(actual) !== JSON.stringify(expected)) {
    throw new Error(`assertion failed: ${label}\nactual=${JSON.stringify(actual)}\nexpected=${JSON.stringify(expected)}`);
  }
}

function storage(seed = {}) {
  const values = new Map(Object.entries(seed));
  const calls = {get: 0, set: 0, remove: 0, key: 0};
  const api = {
    get length() { return values.size; },
    key(index) {
      calls.key += 1;
      return Array.from(values.keys())[index] ?? null;
    },
    getItem(key) {
      calls.get += 1;
      return values.has(String(key)) ? values.get(String(key)) : null;
    },
    setItem(key, value) {
      calls.set += 1;
      values.set(String(key), String(value));
    },
    removeItem(key) {
      calls.remove += 1;
      values.delete(String(key));
    }
  };
  return {values, calls, api};
}

function runtimeFor(store) {
  const events = [];
  const listeners = {};
  const window = {
    localStorage: store.api,
    addEventListener(type, fn) {
      (listeners[type] ||= []).push(fn);
    },
    dispatchEvent(event) {
      events.push(event);
      for (const fn of [...(listeners[event.type] || [])]) fn(event);
      return true;
    }
  };
  window.window = window;
  const context = vm.createContext({
    window,
    localStorage: store.api,
    CustomEvent: function CustomEvent(type, init) {
      this.type = type;
      this.detail = init && init.detail;
    },
    Date,
    JSON,
    Map,
    Set,
    WeakSet,
    Object,
    Array,
    String,
    Number,
    Boolean,
    Math,
    RegExp,
    encodeURIComponent,
    unescape
  });
  return {context, window, events, listeners};
}

function load(runtime, name) {
  vm.runInContext(source(name), runtime.context, {filename: name});
}

function initialInventory(label = 'before') {
  return {
    pmp_master_bank_inventory_v1: JSON.stringify({
      type: 'PMP_MASTER_BANK_INVENTORY_V1',
      version: 'fixture',
      owner: 'bank_screen_owner',
      banks: {
        world: {
          name: 'World Bank',
          records: [{record_id: `world:${label}`, summary: label}],
          references: []
        }
      }
    })
  };
}

function bankCommit(boundary, operation, value, expectedVersion) {
  const resource = 'bank:persist:master_inventory';
  return boundary.commitBundle({
    requester_owner: 'bank_screen_owner',
    resource,
    expected_version: expectedVersion,
    writes: [{
      key: 'pmp_master_bank_inventory_v1',
      value: {
        type: 'PMP_MASTER_BANK_INVENTORY_V1',
        version: 'fixture',
        owner: 'bank_screen_owner',
        banks: {
          world: {
            name: 'World Bank',
            records: [{record_id: `world:${value}`, summary: value}],
            references: []
          }
        }
      }
    }],
    operation_id: `op:p10u4:${operation}`,
    request_id: `req:p10u4:${operation}`,
    capability: `internal:bank_screen_owner:COMMIT_WRITE:${resource}`
  });
}

const store = storage(initialInventory());
const runtime = runtimeFor(store);
load(runtime, 'pmp-bank-continuous-run-owner-boundary-v1.js');
load(runtime, 'pmp-bank-inventory-readonly-projection-v1.js');
const projection = runtime.window.PMPBankInventoryReadonlyProjectionV1;
const before = projection.snapshot('p10u4_before_commit');
const readsBeforeCommit = store.calls.get;
const writesBeforeCommit = store.calls.set;
load(runtime, 'pmp-bank-owner-projection-refresh-v1.js');

const refresh = runtime.window.PMPBankOwnerProjectionRefreshV1;
const boundary = runtime.window.PMPBankContinuousRunOwnerBoundaryV1;
check(refresh, 'refresh adapter installed');
equal(refresh.version, '1.0.0-pass10-unit4-owner-refresh-20260726A', 'adapter version');
equal(refresh.owner, 'bank_screen_owner', 'adapter owner');
equal(Object.isFrozen(refresh), true, 'adapter API frozen');
equal(typeof refresh.diagnostic, 'function', 'diagnostic API exposed');
equal(refresh.write, undefined, 'no write API');
equal(refresh.delete, undefined, 'no delete API');
equal(refresh.migrate, undefined, 'no migration API');
equal(refresh.refresh, undefined, 'no direct refresh API');
check(refresh.rule.includes('exact accepted Bank-owner receipt'), 'exact owner receipt rule');
check(refresh.rule.includes('duplicate'), 'duplicate denial rule');
check(refresh.rule.includes('stale'), 'stale denial rule');
check(refresh.rule.includes('Helper'), 'Helper no-authority rule');
check(refresh.rule.includes('active-tab'), 'active tab no-authority rule');
check(refresh.rule.includes('direct UI'), 'direct UI no-authority rule');
equal(store.calls.set, writesBeforeCommit, 'adapter load zero writes');
equal(store.calls.remove, 0, 'adapter load zero deletes');
equal(store.calls.get, readsBeforeCommit, 'adapter load zero reads');

const initialDiagnostic = refresh.diagnostic();
equal(initialDiagnostic.accepted_owner_events, 0, 'initial accepted zero');
equal(initialDiagnostic.denied_owner_events, 0, 'initial denied zero');
equal(initialDiagnostic.projection_refreshes, 0, 'initial refresh zero');
equal(initialDiagnostic.attempt_limit, 1, 'one refresh attempt per event');
equal(initialDiagnostic.helper_registration_conveys_authority, false, 'Helper diagnostic no authority');
equal(initialDiagnostic.active_tab_conveys_authority, false, 'tab diagnostic no authority');
equal(initialDiagnostic.direct_ui_event_conveys_authority, false, 'UI diagnostic no authority');
equal(initialDiagnostic.write_api_exposed, false, 'diagnostic no write API');
equal(initialDiagnostic.delete_api_exposed, false, 'diagnostic no delete API');
equal(initialDiagnostic.migration_api_exposed, false, 'diagnostic no migration API');

const accepted = bankCommit(boundary, 'accepted-1', 'after', 0);
equal(accepted.ok, true, 'owner commit accepted');
equal(accepted.decision, 'ALLOW', 'owner commit allowed');
equal(accepted.code, 'COMMITTED', 'owner commit committed');
equal(accepted.receipt.requester_owner, 'bank_screen_owner', 'receipt Bank owner');
equal(accepted.receipt.target_owner, 'bank_screen_owner', 'receipt target owner');
equal(accepted.receipt.resource_version_before, 0, 'receipt version before');
equal(accepted.receipt.resource_version_after, 1, 'receipt version after');
equal(store.calls.set - writesBeforeCommit, 1, 'only boundary performed one fixture write');
equal(store.calls.remove, 0, 'accepted refresh zero deletes');

const acceptedDiagnostic = refresh.diagnostic();
equal(acceptedDiagnostic.accepted_owner_events, 1, 'one owner event accepted');
equal(acceptedDiagnostic.denied_owner_events, 0, 'no owner event denied');
equal(acceptedDiagnostic.projection_refreshes, 1, 'projection refreshed exactly once');
equal(acceptedDiagnostic.last_decision, 'ALLOW', 'last decision allow');
equal(acceptedDiagnostic.last_code, 'REFRESHED_EXACTLY_ONCE', 'exactly once code');
equal(acceptedDiagnostic.last_receipt_sha256, accepted.receipt.receipt_sha256, 'diagnostic receipt binding');
equal(acceptedDiagnostic.last_resource, 'bank:persist:master_inventory', 'diagnostic resource');
equal(acceptedDiagnostic.last_version, 1, 'diagnostic version');

const after = projection.lastSnapshot();
equal(after.reason, `accepted_bank_owner_commit:${accepted.receipt.receipt_sha256}`, 'projection owner reason');
equal(after.summary.items >= 1, true, 'refreshed projection has items');
equal(after.banks.world.items.some(row => row.source_native_id === 'world:after'), true, 'refreshed projection sees committed owner fact');
equal(after.banks.world.items.some(row => row.source_native_id === 'world:before'), false, 'old owner fact no longer projected');
equal(after.effects.storage_writes, 0, 'projection refresh reports zero writes');
equal(after.effects.storage_deletes, 0, 'projection refresh reports zero deletes');
equal(after.rules.read_only, true, 'projection remains read only');
equal(after.rules.helper_registration_conveys_authority, false, 'projection preserves Helper no authority');
equal(after.rules.active_tab_conveys_authority, false, 'projection preserves tab no authority');

const refreshedEvents = runtime.events.filter(event => event.type === 'pmp:bank-inventory-projection-refreshed');
equal(refreshedEvents.length, 1, 'one sanitized projection refreshed event');
equal(refreshedEvents[0].detail.owner, 'bank_screen_owner', 'refreshed event owner');
equal(refreshedEvents[0].detail.receipt_sha256, accepted.receipt.receipt_sha256, 'refreshed event receipt');
equal(refreshedEvents[0].detail.version, 1, 'refreshed event version');
equal(refreshedEvents[0].detail.raw_payload_exposed, false, 'refreshed event no raw payload');
equal(JSON.stringify(refreshedEvents[0].detail).includes('world:after'), false, 'refreshed event excludes payload');

runtime.window.dispatchEvent(new runtime.context.CustomEvent('pmp:bank-owner-write-committed', {
  detail: {
    resource: 'bank:persist:master_inventory',
    version: 1,
    receipt: accepted.receipt
  }
}));
const duplicateDiagnostic = refresh.diagnostic();
equal(duplicateDiagnostic.accepted_owner_events, 1, 'duplicate not accepted');
equal(duplicateDiagnostic.projection_refreshes, 1, 'duplicate does not refresh');
equal(duplicateDiagnostic.denied_owner_events, 1, 'duplicate denied');
equal(duplicateDiagnostic.duplicate_owner_events, 1, 'duplicate counted');
equal(duplicateDiagnostic.last_code, 'DENIED_DUPLICATE_OWNER_RECEIPT', 'duplicate code');
equal(runtime.events.filter(event => event.type === 'pmp:bank-inventory-projection-refreshed').length, 1, 'duplicate emits no refresh event');

const replay = bankCommit(boundary, 'accepted-1', 'after', 1);
equal(replay.ok, false, 'conflicting operation replay denied');
equal(replay.code, 'DENIED_DUPLICATE_CONFLICT', 'conflicting replay code');
equal(refresh.diagnostic().projection_refreshes, 1, 'boundary conflict emits no refresh');

const staleBoundary = bankCommit(boundary, 'stale-version', 'stale', 0);
equal(staleBoundary.ok, false, 'stale boundary version denied');
equal(staleBoundary.code, 'DENIED_EXPECTED_VERSION', 'stale boundary code');
equal(refresh.diagnostic().projection_refreshes, 1, 'stale boundary denial no refresh');

const wrongOwnerReceipt = {...accepted.receipt, requester_owner: 'helper_owner'};
runtime.window.dispatchEvent(new runtime.context.CustomEvent('pmp:bank-owner-write-committed', {
  detail: {resource: accepted.receipt.resource, version: 1, receipt: wrongOwnerReceipt, helper_registered: true, active_tab: 'bank'}
}));
equal(refresh.diagnostic().accepted_owner_events, 1, 'wrong owner not accepted');
equal(refresh.diagnostic().projection_refreshes, 1, 'wrong owner no refresh');
equal(refresh.diagnostic().last_code, 'DENIED_WRONG_OWNER_OR_DECISION', 'wrong owner code');

runtime.window.dispatchEvent(new runtime.context.CustomEvent('pmp:bank-owner-write-committed', {
  detail: {resource: 'bank:persist:master_inventory', version: 'one', receipt: {}}
}));
equal(refresh.diagnostic().last_code, 'DENIED_MALFORMED_OWNER_EVENT', 'malformed event code');
equal(refresh.diagnostic().projection_refreshes, 1, 'malformed no refresh');

runtime.window.dispatchEvent(new runtime.context.CustomEvent('pmp:bank-inventory-projection-refreshed', {
  detail: {type: 'PMP_BANK_INVENTORY_PROJECTION_REFRESHED_V1', owner: 'helper_owner', receipt_sha256: 'f'.repeat(64)}
}));
equal(refresh.diagnostic().projection_refreshes, 1, 'direct UI refresh event cannot refresh projection');
equal(projection.lastSnapshot(), after, 'direct UI event leaves projection unchanged');

const staleStore = storage(initialInventory('zero'));
const staleRuntime = runtimeFor(staleStore);
load(staleRuntime, 'pmp-bank-continuous-run-owner-boundary-v1.js');
load(staleRuntime, 'pmp-bank-inventory-readonly-projection-v1.js');
const staleOwnerBoundary = staleRuntime.window.PMPBankContinuousRunOwnerBoundaryV1;
const firstBeforeAdapter = bankCommit(staleOwnerBoundary, 'pre-adapter', 'one', 0);
equal(firstBeforeAdapter.ok, true, 'pre-adapter owner commit accepted');
load(staleRuntime, 'pmp-bank-owner-projection-refresh-v1.js');
const secondAfterAdapter = bankCommit(staleOwnerBoundary, 'post-adapter', 'two', 1);
equal(secondAfterAdapter.ok, true, 'post-adapter owner commit accepted');
equal(staleRuntime.window.PMPBankOwnerProjectionRefreshV1.diagnostic().projection_refreshes, 1, 'post-adapter refresh once');
staleRuntime.window.dispatchEvent(new staleRuntime.context.CustomEvent('pmp:bank-owner-write-committed', {
  detail: {resource: firstBeforeAdapter.receipt.resource, version: 1, receipt: firstBeforeAdapter.receipt}
}));
const staleDiagnostic = staleRuntime.window.PMPBankOwnerProjectionRefreshV1.diagnostic();
equal(staleDiagnostic.projection_refreshes, 1, 'stale receipt no refresh');
equal(staleDiagnostic.stale_owner_events, 1, 'stale receipt counted');
equal(staleDiagnostic.last_code, 'DENIED_STALE_BOUNDARY_VERSION', 'stale receipt code');

const missingStore = storage(initialInventory());
const missingRuntime = runtimeFor(missingStore);
load(missingRuntime, 'pmp-bank-owner-projection-refresh-v1.js');
missingRuntime.window.dispatchEvent(new missingRuntime.context.CustomEvent('pmp:bank-owner-write-committed', {detail: {}}));
equal(missingRuntime.window.PMPBankOwnerProjectionRefreshV1.diagnostic().last_code, 'DENIED_DEPENDENCY_OR_DETAIL', 'missing dependency fail closed');
equal(missingStore.calls.get, 0, 'missing dependency zero reads');
equal(missingStore.calls.set, 0, 'missing dependency zero writes');
equal(missingStore.calls.remove, 0, 'missing dependency zero deletes');

const adapterSource = source('pmp-bank-owner-projection-refresh-v1.js');
const tabSource = source('pmp-master-bank-tab-v1.js');
const projectionSource = source('pmp-bank-inventory-readonly-projection-v1.js');
const inner = source('pmp-current-inner-cleanbug-rgcontrols-v23.html');
const mounts = source('pmp-mount-registry-v1.js');
for (const forbidden of ['setInterval(', 'setTimeout(', '.setItem(', '.removeItem(', 'indexedDB.open']) {
  equal(adapterSource.includes(forbidden), false, `adapter forbids ${forbidden}`);
}
check(adapterSource.includes("window.addEventListener('pmp:bank-owner-write-committed',onOwnerCommit)"), 'adapter is sole owner event consumer');
check(adapterSource.includes("receipt.requester_owner!==OWNER"), 'adapter rejects wrong owner');
check(adapterSource.includes("processed.has(hash)"), 'adapter rejects duplicate receipt');
check(adapterSource.includes("boundary.resourceVersion(resource)!==version"), 'adapter rejects stale boundary');
check(adapterSource.includes("projection.snapshot('accepted_bank_owner_commit:'"), 'adapter exact owner projection refresh');
check(adapterSource.includes("recentReceiptValid(boundary,receipt)"), 'adapter verifies boundary receipt');
check(adapterSource.includes("receiptHashValid(boundary,receipt)"), 'adapter verifies receipt hash');
check(adapterSource.includes("direct_ui_event_conveys_authority:false"), 'adapter direct UI no authority');
equal(tabSource.includes("window.addEventListener('pmp:bank-owner-write-committed',scan)"), false, 'Bank tab no raw owner event listener');
check(tabSource.includes("window.addEventListener('pmp:bank-inventory-projection-refreshed',ownerProjectionRefreshed)"), 'Bank tab listens only sanitized refresh');
check(tabSource.includes("state.last_code!=='REFRESHED_EXACTLY_ONCE'"), 'Bank tab checks adapter decision');
check(tabSource.includes("hash===lastOwnerRefreshReceipt"), 'Bank tab deduplicates paint');
check(tabSource.includes("p.lastSnapshot?p.lastSnapshot():null"), 'Bank tab renders cached projection');
check(tabSource.includes("p.snapshot('bank_tab_initial_projection')"), 'Bank tab initial snapshot once');
check(tabSource.includes("paint(d,true,'bank_tab_user_refresh')"), 'explicit user refresh remains bounded');
equal(tabSource.includes('.recordWrite('), false, 'Bank tab no direct write');
equal(tabSource.includes('.recordDelete('), false, 'Bank tab no direct delete');
equal(tabSource.includes('localStorage.setItem'), false, 'Bank tab no storage write');
equal(tabSource.includes('setInterval('), false, 'Bank tab no recurring painter');
equal(projectionSource.includes('.setItem('), false, 'projection still no write');
equal(projectionSource.includes('.removeItem('), false, 'projection still no delete');
const boundaryIndex = inner.indexOf('pmp-bank-continuous-run-owner-boundary-v1.js');
const routerIndex = inner.indexOf('pmp-master-bank-inventory-router-v1.js');
const projectionIndex = inner.indexOf('pmp-bank-inventory-readonly-projection-v1.js');
const refreshIndex = inner.indexOf('pmp-bank-owner-projection-refresh-v1.js');
const tabIndex = inner.indexOf('pmp-master-bank-tab-v1.js');
check(0 <= boundaryIndex && boundaryIndex < routerIndex, 'boundary before router');
check(routerIndex < projectionIndex, 'router before projection');
check(projectionIndex < refreshIndex, 'projection before refresh adapter');
check(refreshIndex < tabIndex, 'refresh adapter before Bank tab');
equal((inner.match(/pmp-bank-owner-projection-refresh-v1\.js/g) || []).length, 1, 'one active refresh adapter');
equal((mounts.match(/pmp-bank-owner-projection-refresh-v1\.js/g) || []).length, 1, 'one refresh adapter mount');

console.log(`PASS: P10-U4 Bank owner projection refresh (${assertions}/${assertions})`);
