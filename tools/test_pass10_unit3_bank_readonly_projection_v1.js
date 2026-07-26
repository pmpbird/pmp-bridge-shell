#!/usr/bin/env node
'use strict';

const crypto = require('crypto');
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
    get length() {
      return values.size;
    },
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
      for (const fn of listeners[event.type] || []) fn(event);
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

const seed = {
  pmp_master_bank_inventory_v1: JSON.stringify({
    type: 'PMP_MASTER_BANK_INVENTORY_V1',
    version: '2.0.0-pass9-unit3-owner-boundary',
    owner: 'bank_screen_owner',
    banks: {
      world: {
        name: 'World Bank',
        records: [
          {record_id: 'record:world:1', record_type: 'source', summary: 'world fact'}
        ],
        references: []
      },
      continuous_run: {
        name: 'Continuous Run Bank',
        records: [
          {record_id: 'record:run:1', record_type: 'state', summary: 'run fact'}
        ],
        references: []
      }
    }
  }),
  pmp_helper_bank_index_v1: JSON.stringify({
    type: 'PMP_HELPER_BANK_INDEX_V1',
    version: '2.0.0-pass9-unit3-owner-boundary',
    helpers: [
      {helper_id: 'helper-1', owning_bank: 'world', record_id: 'record:world:1'}
    ]
  }),
  pmp_bank_project_registry_v1: JSON.stringify({
    type: 'BANK_PROJECT_REGISTRY_V1',
    version: '2.0.0-pass9-unit3-owner-boundary',
    projects: [
      {id: 'bank-project-continuous-run-engine-000003', name: 'Continuous Run Engine'}
    ]
  }),
  pmp_connection_bank_inventory_v1: JSON.stringify({
    type: 'PMP_HISTORIC_CONNECTION_BANK_INVENTORY_V1',
    version: 'legacy',
    records: [{id: 'historic-1'}]
  }),
  pmp_source_bank_router_receipts_v1: '{not-json',
  pmp_custom_bank_unknown_v1: JSON.stringify({private: 'must not be exposed', value: 42}),
  unrelated_user_key: JSON.stringify({keep: 'exactly'})
};

const store = storage(seed);
const runtime = runtimeFor(store);
const exactBefore = Object.fromEntries(store.values);
load(runtime, 'pmp-bank-continuous-run-owner-boundary-v1.js');
equal(store.calls.get, 0, 'boundary load zero reads');
equal(store.calls.set, 0, 'boundary load zero writes');
equal(store.calls.remove, 0, 'boundary load zero deletes');
load(runtime, 'pmp-bank-inventory-readonly-projection-v1.js');
equal(store.calls.get, 0, 'projection load zero reads');
equal(store.calls.set, 0, 'projection load zero writes');
equal(store.calls.remove, 0, 'projection load zero deletes');
check(runtime.events.some(event => event.type === 'pmp:bank-inventory-readonly-projection-ready'), 'projection ready event');

const api = runtime.window.PMPBankInventoryReadonlyProjectionV1;
check(api, 'projection API installed');
equal(api.version, '1.0.0-pass10-unit3-readonly-projection-20260726A', 'projection version');
equal(api.contract_version, 'PMP_CANONICAL_BANK_INVENTORY_CONTRACT_V1', 'contract version');
equal(api.item_version, 'PMP_CANONICAL_BANK_INVENTORY_ITEM_V1', 'item version');
equal(api.owner, 'bank_screen_owner', 'Bank owner');
equal(api.namespaceRules.length, 14, 'LocalStorage namespace rules');
equal(api.indexedDBNamespaces.length, 2, 'IndexedDB namespaces');
equal(new Set(api.namespaceRules.map(row => row.namespace)).size, 14, 'namespace rules unique');
equal(Object.isFrozen(api), true, 'API frozen');
equal(typeof api.snapshot, 'function', 'snapshot API');
equal(typeof api.bank, 'function', 'bank API');
equal(typeof api.lastSnapshot, 'function', 'last snapshot API');
equal(api.write, undefined, 'no write API');
equal(api.delete, undefined, 'no delete API');
equal(api.migrate, undefined, 'no migration API');
check(api.rule.includes('Helper authority'), 'rule rejects Helper authority');
check(api.rule.includes('active-tab authority'), 'rule rejects active-tab authority');
check(api.rule.includes('raw payload'), 'rule rejects raw payload API');

const snapshot = api.snapshot('deterministic_test');
equal(snapshot.type, 'PMP_BANK_INVENTORY_READONLY_PROJECTION_V1', 'snapshot type');
equal(snapshot.version, api.version, 'snapshot version');
equal(snapshot.contract_version, api.contract_version, 'snapshot contract');
equal(snapshot.owner, 'bank_screen_owner', 'snapshot owner');
equal(snapshot.status, 'READ_ONLY_PROJECTION_READY', 'snapshot ready');
equal(snapshot.reason, 'deterministic_test', 'snapshot reason');
equal(Object.keys(snapshot.banks).length, 13, '13 Bank families');
equal(snapshot.indexeddb_namespaces.length, 2, 'two IndexedDB declarations');
equal(snapshot.indexeddb_namespaces.every(row => row.state === 'DECLARED_NOT_OPENED_BY_P10_U3'), true, 'P10-U3 does not open IndexedDB');
equal(snapshot.effects.storage_writes, 0, 'snapshot zero writes');
equal(snapshot.effects.storage_deletes, 0, 'snapshot zero deletes');
equal(snapshot.effects.indexeddb_reads, 0, 'snapshot zero IndexedDB reads');
check(snapshot.effects.storage_reads > 0, 'snapshot performs bounded reads');
check(snapshot.effects.key_enumerations > 0, 'snapshot enumerates for unknown Bank namespaces');
equal(store.calls.set, 0, 'real storage zero writes after snapshot');
equal(store.calls.remove, 0, 'real storage zero deletes after snapshot');
equal(Object.fromEntries(store.values), exactBefore, 'all source bytes preserved exactly');

equal(snapshot.rules.read_only, true, 'read-only rule');
equal(snapshot.rules.owner_facts_only, true, 'owner facts rule');
equal(snapshot.rules.helper_registration_conveys_authority, false, 'Helper registration no authority');
equal(snapshot.rules.active_tab_conveys_authority, false, 'active tab no authority');
equal(snapshot.rules.filename_conveys_authority, false, 'filename no authority');
equal(snapshot.rules.write_api_exposed, false, 'write API hidden');
equal(snapshot.rules.delete_api_exposed, false, 'delete API hidden');
equal(snapshot.rules.migration_api_exposed, false, 'migration API hidden');
equal(snapshot.rules.raw_payload_exposed, false, 'raw payload hidden');
equal(snapshot.rules.refresh_mode, 'EXPLICIT_USER_OR_OWNER_EVENT_ONLY', 'no recurring refresh');
equal(snapshot.rules.unknown_or_orphan_policy, 'QUARANTINE_PRESERVE_EXACT_BYTES_NEVER_SILENTLY_DELETE', 'quarantine policy');
equal(snapshot.rules.historic_namespace_policy, 'REFERENCE_ONLY_NEVER_SILENTLY_MERGE', 'historic policy');
equal(snapshot.summary.exact_source_bytes_preserved, true, 'source bytes preserved');
equal(snapshot.summary.raw_payloads_exposed, 0, 'zero raw payloads');

check(snapshot.items.length >= 7, 'expected inventory facts represented');
equal(snapshot.summary.items, snapshot.items.length, 'summary item count');
equal(snapshot.summary.active, snapshot.items.filter(row => row.state === 'ACTIVE').length, 'active count');
equal(snapshot.summary.reference_only, snapshot.items.filter(row => row.state === 'REFERENCE_ONLY').length, 'reference count');
equal(snapshot.summary.quarantined, snapshot.items.filter(row => row.state === 'QUARANTINED').length, 'quarantine count');
equal(snapshot.items.every(row => /^bank-(?:item|quarantine):v1:[0-9a-f]{64}$/.test(row.canonical_id)), true, 'canonical IDs');
equal(snapshot.items.every(row => /^[0-9a-f]{64}$/.test(row.payload_sha256)), true, 'payload SHA-256');
equal(snapshot.items.every(row => Number.isInteger(row.payload_bytes) && row.payload_bytes >= 0), true, 'payload byte counts');
equal(snapshot.items.every(row => row.exact_bytes_preserved_in_source === true), true, 'exact bytes preservation fact');
equal(snapshot.items.every(row => row.raw_payload_exposed_to_ui === false), true, 'raw bytes hidden per item');
equal(snapshot.items.some(row => Object.prototype.hasOwnProperty.call(row, 'raw_bytes_base64')), false, 'no raw bytes field');
equal(JSON.stringify(snapshot).includes('must not be exposed'), false, 'unknown raw payload text not exposed');
equal(JSON.stringify(snapshot).includes('"value":42'), false, 'unknown raw payload structure not exposed');

const world = snapshot.banks.world;
const continuous = snapshot.banks.continuous_run;
const helper = snapshot.banks.helper;
const connections = snapshot.banks.connections;
const master = snapshot.banks.master;
equal(world.items.some(row => row.source_native_id === 'record:world:1'), true, 'world record represented');
equal(continuous.items.some(row => row.source_native_id === 'record:run:1'), true, 'run record represented');
equal(continuous.items.some(row => row.source_native_id === 'bank-project-continuous-run-engine-000003'), true, 'project represented');
equal(helper.items.some(row => row.source_native_id.includes('helper-1')), true, 'Helper fact represented');
equal(helper.items.every(row => row.owner_id === 'bank_screen_owner'), true, 'Helper index remains Bank-owned fact');
equal(connections.items.some(row => row.state === 'REFERENCE_ONLY'), true, 'historic inventory reference-only');
equal(connections.items.find(row => row.state === 'REFERENCE_ONLY').write_authority, 'NONE', 'historic no write');
equal(master.items.some(row => row.source_namespace === 'pmp_custom_bank_unknown_v1'), true, 'unknown Bank namespace visible');
const unknown = master.items.find(row => row.source_namespace === 'pmp_custom_bank_unknown_v1');
equal(unknown.state, 'QUARANTINED', 'unknown namespace quarantined');
check(unknown.quarantine_reasons.includes('UNKNOWN_NAMESPACE'), 'unknown namespace reason');
check(unknown.quarantine_reasons.includes('UNKNOWN_OWNER'), 'unknown owner reason');
check(unknown.quarantine_reasons.includes('UNKNOWN_SCHEMA_TYPE'), 'unknown schema reason');
equal(unknown.write_authority, 'NONE', 'unknown no write');
const corrupt = master.items.find(row => row.source_namespace === 'pmp_source_bank_router_receipts_v1');
equal(corrupt.state, 'QUARANTINED', 'corrupt record quarantined');
check(corrupt.quarantine_reasons.includes('CORRUPT_RECORD'), 'corrupt reason');

const firstIdentities = snapshot.items.map(row => row.canonical_id);
const second = api.snapshot('deterministic_repeat');
equal(second.items.map(row => row.canonical_id), firstIdentities, 'identity deterministic across refresh');
equal(Object.fromEntries(store.values), exactBefore, 'repeat snapshot preserves exact bytes');
equal(api.lastSnapshot(), second, 'last snapshot');
const bankOnly = api.bank('world', 'bank_only_test');
equal(bankOnly.name, 'World Bank', 'bank accessor');
equal(bankOnly.items.some(row => row.source_native_id === 'record:world:1'), true, 'bank accessor item');
equal(Object.fromEntries(store.values), exactBefore, 'bank accessor preserves exact bytes');

const collisionSeed = {
  pmp_master_bank_inventory_v1: JSON.stringify({
    type: 'PMP_MASTER_BANK_INVENTORY_V1',
    version: 'legacy',
    banks: {
      world: {records: [{record_id: 'same-id', value: 'one'}], references: []},
      master: {records: [{record_id: 'same-id', value: 'two'}], references: []}
    }
  })
};
const collisionStore = storage(collisionSeed);
const collisionRuntime = runtimeFor(collisionStore);
load(collisionRuntime, 'pmp-bank-continuous-run-owner-boundary-v1.js');
load(collisionRuntime, 'pmp-bank-inventory-readonly-projection-v1.js');
const collision = collisionRuntime.window.PMPBankInventoryReadonlyProjectionV1.snapshot('collision_test');
const collisionRows = collision.items.filter(row => row.source_native_id === 'same-id');
equal(collisionRows.length, 2, 'collision keeps both source facts');
equal(new Set(collisionRows.map(row => row.canonical_id)).size, 1, 'collision shares deterministic identity');
equal(collisionRows.every(row => row.state === 'QUARANTINED'), true, 'collision quarantines all');
equal(collisionRows.every(row => row.quarantine_reasons.includes('IDENTITY_COLLISION')), true, 'collision reason');
equal(collisionStore.calls.set, 0, 'collision zero writes');
equal(collisionStore.calls.remove, 0, 'collision zero deletes');
equal(Object.fromEntries(collisionStore.values), collisionSeed, 'collision preserves both exact source bytes');

const unavailableStore = storage({});
const unavailableRuntime = runtimeFor(unavailableStore);
load(unavailableRuntime, 'pmp-bank-inventory-readonly-projection-v1.js');
const unavailable = unavailableRuntime.window.PMPBankInventoryReadonlyProjectionV1.snapshot('no_boundary');
equal(unavailable.status, 'OWNER_BOUNDARY_UNAVAILABLE', 'missing boundary fails closed');
equal(unavailable.items, [], 'missing boundary exposes no items');
equal(unavailable.effects.storage_reads, 0, 'missing boundary zero reads');
equal(unavailable.effects.storage_writes, 0, 'missing boundary zero writes');
equal(unavailableStore.calls.get, 0, 'missing boundary does not touch storage');

const projectionSource = source('pmp-bank-inventory-readonly-projection-v1.js');
const masterSource = source('pmp-master-bank-tab-v1.js');
const inner = source('pmp-current-inner-cleanbug-rgcontrols-v23.html');
const mounts = source('pmp-mount-registry-v1.js');
check(projectionSource.includes("helper_registration_conveys_authority:false"), 'source rejects Helper authority');
check(projectionSource.includes("active_tab_conveys_authority:false"), 'source rejects tab authority');
check(projectionSource.includes("refresh_mode:'EXPLICIT_USER_OR_OWNER_EVENT_ONLY'"), 'source event/user refresh only');
equal(projectionSource.includes('setInterval('), false, 'projection no recurring painter');
equal(projectionSource.includes('setTimeout('), false, 'projection no delayed painter');
equal(projectionSource.includes('.setItem('), false, 'projection no storage write');
equal(projectionSource.includes('.removeItem('), false, 'projection no storage delete');
equal(projectionSource.includes('indexedDB.open'), false, 'projection no IndexedDB open');
check(masterSource.includes("PMPBankInventoryReadonlyProjectionV1"), 'Bank tab consumes projection');
check(masterSource.includes("PMP_BANK_TAB_READONLY_EXPORT_V1"), 'read-only export');
check(masterSource.includes("raw_payload_exposed:false"), 'Bank tab raw payload hidden');
check(masterSource.includes("Helper registration and active tab convey no authority"), 'Bank receipt rejects Helper authority');
equal(masterSource.includes('.recordWrite('), false, 'Bank tab has no direct write');
equal(masterSource.includes('.recordDelete('), false, 'Bank tab has no direct delete');
equal(masterSource.includes('setInterval('), false, 'Bank tab no recurring painter');
equal(masterSource.includes('localStorage.setItem'), false, 'Bank tab no storage write');
const boundaryIndex = inner.indexOf('pmp-bank-continuous-run-owner-boundary-v1.js');
const routerIndex = inner.indexOf('pmp-master-bank-inventory-router-v1.js');
const projectionIndex = inner.indexOf('pmp-bank-inventory-readonly-projection-v1.js');
const tabIndex = inner.indexOf('pmp-master-bank-tab-v1.js');
check(boundaryIndex >= 0 && boundaryIndex < routerIndex, 'boundary before router');
check(routerIndex < projectionIndex, 'router before projection');
check(projectionIndex < tabIndex, 'projection before Bank tab');
equal((inner.match(/pmp-bank-inventory-readonly-projection-v1\.js/g) || []).length, 1, 'one projection load');
equal((inner.match(/pmp-master-bank-tab-v1\.js/g) || []).length, 1, 'one Bank tab load');
equal((mounts.match(/pmp-bank-inventory-readonly-projection-v1\.js/g) || []).length, 1, 'projection registered once');

equal(crypto.createHash('sha256').update(source('pmp-bank-inventory-readonly-projection-v1.js')).digest('hex').length, 64, 'projection source hash');
console.log(`PASS: P10-U3 Bank read-only projection (${assertions}/${assertions})`);
