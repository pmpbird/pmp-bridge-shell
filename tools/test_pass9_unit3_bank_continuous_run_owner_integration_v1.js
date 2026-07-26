#!/usr/bin/env node
'use strict';

const crypto = require('crypto');
const fs = require('fs');
const vm = require('vm');

const ROOT = require('path').resolve(__dirname, '..');
const source = name => fs.readFileSync(require('path').join(ROOT, name), 'utf8');
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

function storage(seed = {}, failAt = 0) {
  const values = new Map(Object.entries(seed));
  const calls = {get: 0, set: 0, remove: 0};
  return {
    values,
    calls,
    api: {
      getItem(key) {
        calls.get += 1;
        return values.has(String(key)) ? values.get(String(key)) : null;
      },
      setItem(key, value) {
        calls.set += 1;
        if (failAt && calls.set === failAt) throw new Error('injected storage failure');
        values.set(String(key), String(value));
      },
      removeItem(key) {
        calls.remove += 1;
        values.delete(String(key));
      }
    }
  };
}

function contextFor(store) {
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
  const context = {
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
  };
  return {context: vm.createContext(context), window, events, listeners};
}

function load(runtime, name) {
  vm.runInContext(source(name), runtime.context, {filename: name});
}

const persistedSeed = {
  pmp_continuous_run_state_bank_v1: JSON.stringify({
    type: 'PMP_UNIVERSAL_CONTINUOUS_WORK_ENGINE_STATE_V1',
    created_at: '2026-01-01T00:00:00Z',
    current_work_item: 'user-owned-item',
    notes: 'preserve exactly until an explicit action'
  }),
  pmp_continuous_run_state_receipts_v1: JSON.stringify([{id: 'historic-receipt',note: 'keep'}]),
  pmp_continuous_run_state_manifest_v1: JSON.stringify({type: 'historic-manifest',state_hash: 'legacy'}),
  pmp_master_bank_inventory_v1: JSON.stringify({
    type: 'PMP_MASTER_BANK_INVENTORY_V1',
    banks: {continuous_run: {name: 'Continuous Run Bank',records: [{record_id: 'historic'}],references: []}}
  }),
  unrelated_user_key: JSON.stringify({owned: 'by user',value: 42})
};
const seeded = storage(persistedSeed);
const runtime = contextFor(seeded);
const bytesBeforeLoad = Object.fromEntries(seeded.values);
load(runtime, 'pmp-bank-continuous-run-owner-boundary-v1.js');
equal(Object.fromEntries(seeded.values), bytesBeforeLoad, 'boundary load preserves all storage bytes');
equal(seeded.calls.get, 0, 'boundary load performs zero storage reads');
equal(seeded.calls.set, 0, 'boundary load performs zero storage writes');
equal(seeded.calls.remove, 0, 'boundary load performs zero storage deletes');

const boundary = runtime.window.PMPBankContinuousRunOwnerBoundaryV1;
check(boundary, 'boundary installed');
equal(boundary.version, '1.0.0-pass9-unit3-owner-boundary-20260726A', 'boundary version');
equal(boundary.contract_version, 'PMP_BANK_CONTINUOUS_RUN_OWNER_CONTRACT_V1', 'contract version');
equal(boundary.receipt_version, 'PMP_BANK_CONTINUOUS_RUN_OWNER_RECEIPT_V1', 'receipt version');
equal(boundary.owners.bank, 'bank_screen_owner', 'Bank owner exact');
equal(boundary.owners.continuous_run, 'continuous_run_level_owner', 'Run owner exact');
equal(boundary.request_fields.length, 13, 'request fields count');
equal(new Set(boundary.request_fields).size, 13, 'request fields unique');
const initialSnapshot = boundary.snapshot();
equal(initialSnapshot.status, 'READY', 'boundary ready');
equal(initialSnapshot.receipt_count, 0, 'no boot receipts');
equal(initialSnapshot.receipt_head, '0'.repeat(64), 'receipt chain root');
equal(initialSnapshot.load_effects, {
  storage_reads: 0,
  storage_writes: 0,
  storage_deletes: 0,
  persisted_user_data_changed: false
}, 'zero load effects');
equal(initialSnapshot.rules.active_tab_conveys_ownership, false, 'tab no authority');
equal(initialSnapshot.rules.filename_conveys_authority, false, 'filename no authority');
equal(initialSnapshot.rules.copied_cross_frame_api_conveys_authority, false, 'copied API no authority');
equal(initialSnapshot.rules.delete_or_clear_default, 'DENY', 'delete clear default deny');
equal(initialSnapshot.rules.storage_migration, 'FORBIDDEN', 'migration forbidden');
equal(initialSnapshot.rules.receipt_integrity, 'SHA-256_CHAINED', 'SHA receipt chain');
equal(initialSnapshot.rules.duplicate_policy, 'IDENTICAL_REPLAY_OR_CONFLICT_DENY', 'duplicate policy');

for (const text of ['', 'abc', 'P9-U3 owner boundary', 'Unicode ✓ café']) {
  equal(
    boundary.sha256(text),
    crypto.createHash('sha256').update(text).digest('hex'),
    `SHA-256 ${JSON.stringify(text)}`
  );
}
equal(boundary.canonical({b: 2,a: [3,{z: 1,y: 0}]}), '{"a":[3,{"y":0,"z":1}],"b":2}', 'canonical JSON');

function commit(overrides = {}) {
  const resource = overrides.resource || 'bank:persist:continuous_run_state';
  const writes = overrides.writes || [{key: 'pmp_continuous_run_state_bank_v1',value: {type: 'state',n: 1}}];
  return boundary.commitBundle(Object.assign({
    requester_owner: 'continuous_run_level_owner',
    resource,
    expected_version: boundary.resourceVersion(resource),
    writes,
    operation_id: `op:test:${Math.random().toString(16).slice(2)}`,
    request_id: `req:test:${Math.random().toString(16).slice(2)}`,
    capability: `request:bank_screen_owner:COMMIT_WRITE:${resource}`
  }, overrides));
}

const deniedBefore = Object.fromEntries(seeded.values);
const wrongCapability = commit({capability: 'wrong'});
equal(wrongCapability.ok, false, 'wrong capability denied');
equal(wrongCapability.code, 'DENIED_CAPABILITY', 'wrong capability code');
equal(Object.fromEntries(seeded.values), deniedBefore, 'denial writes nothing');
const wrongScope = commit({writes: [{key: 'unrelated_user_key',value: {hacked: true}}]});
equal(wrongScope.ok, false, 'wrong key scope denied');
equal(wrongScope.code, 'DENIED_STORAGE_SCOPE', 'wrong key scope code');
equal(JSON.parse(seeded.values.get('unrelated_user_key')).value, 42, 'unrelated key preserved');
const wrongVersion = commit({expected_version: 99});
equal(wrongVersion.code, 'DENIED_EXPECTED_VERSION', 'wrong expected version denied');
const wrongAction = commit({action: 'DELETE_BANK', capability: 'request:bank_screen_owner:DELETE_BANK:bank:persist:continuous_run_state'});
equal(wrongAction.code, 'DENIED_ACTION', 'delete action denied');
const wrongOwner = commit({requester_owner: 'unknown_owner'});
equal(wrongOwner.code, 'DENIED_OWNER', 'unknown owner denied');
const expiredIssued = new Date(Date.now() - 600000).toISOString();
const expired = commit({
  issued_at: expiredIssued,
  expires_at: new Date(Date.parse(expiredIssued) + 1000).toISOString()
});
equal(expired.code, 'DENIED_EXPIRED', 'expired request denied');
equal(boundary.manualDeleteAuthority({}, 'connections'), false, 'delete absent authority denied');
equal(boundary.manualDeleteAuthority({user_confirmed: true,capability: 'wrong'}, 'connections'), false, 'delete wrong capability denied');
equal(boundary.manualDeleteAuthority({user_confirmed: true,capability: 'manual:bank_screen_owner:delete_record:connections'}, 'connections'), true, 'exact user delete authority accepted');

const writes = [
  {key: 'pmp_continuous_run_state_bank_v1',value: {type: 'state',n: 1}},
  {key: 'pmp_continuous_run_state_receipts_v1',value: [{id: 'new'}]},
  {key: 'pmp_continuous_run_state_manifest_v1',value: {type: 'manifest'}}
];
const operation = 'op:test:atomic-commit';
const requestId = 'req:test:atomic-commit';
const issuedAt = new Date().toISOString();
const expiresAt = new Date(Date.parse(issuedAt) + 300000).toISOString();
const accepted = commit({writes,operation_id: operation,request_id: requestId,issued_at: issuedAt,expires_at: expiresAt});
equal(accepted.ok, true, 'exact commit accepted');
equal(accepted.code, 'COMMITTED', 'commit code');
equal(accepted.effects.storage_writes, 3, 'three exact writes');
equal(accepted.effects.storage_deletes, 0, 'no deletes');
equal(boundary.resourceVersion('bank:persist:continuous_run_state'), 1, 'resource version advanced');
equal(JSON.parse(seeded.values.get('pmp_continuous_run_state_bank_v1')).n, 1, 'state committed');
equal(JSON.parse(seeded.values.get('pmp_continuous_run_state_receipts_v1'))[0].id, 'new', 'receipts committed');
equal(JSON.parse(seeded.values.get('pmp_continuous_run_state_manifest_v1')).type, 'manifest', 'manifest committed');
equal(JSON.parse(seeded.values.get('unrelated_user_key')).value, 42, 'unrelated key survives commit');
check(/^[0-9a-f]{64}$/.test(accepted.receipt.request_sha256), 'request SHA-256');
check(/^[0-9a-f]{64}$/.test(accepted.receipt.receipt_sha256), 'receipt SHA-256');
equal(accepted.receipt.previous_receipt_sha256, '0'.repeat(64), 'first receipt chain root');
equal(accepted.receipt.resource_version_before, 0, 'first receipt version before');
equal(accepted.receipt.resource_version_after, 1, 'first receipt version after');
equal(accepted.receipt.requester_owner, 'continuous_run_level_owner', 'receipt requester');
equal(accepted.receipt.target_owner, 'bank_screen_owner', 'receipt target');

const replaySetCount = seeded.calls.set;
const replay = commit({writes,operation_id: operation,request_id: requestId,expected_version: 0,issued_at: issuedAt,expires_at: expiresAt});
equal(replay, accepted, 'identical operation returns identical result');
equal(seeded.calls.set, replaySetCount, 'replay performs no new write');
const conflict = commit({writes: [{key: 'pmp_continuous_run_state_bank_v1',value: {n: 2}}],operation_id: operation,request_id: requestId,expected_version: 1,issued_at: issuedAt,expires_at: expiresAt});
equal(conflict.ok, false, 'duplicate conflict denied');
equal(conflict.code, 'DENIED_DUPLICATE_CONFLICT', 'duplicate conflict code');

const failing = storage(persistedSeed, 2);
const failingRuntime = contextFor(failing);
load(failingRuntime, 'pmp-bank-continuous-run-owner-boundary-v1.js');
const failingBoundary = failingRuntime.window.PMPBankContinuousRunOwnerBoundaryV1;
const failureResult = failingBoundary.commitBundle({
  requester_owner: 'continuous_run_level_owner',
  resource: 'bank:persist:continuous_run_state',
  expected_version: 0,
  writes,
  operation_id: 'op:test:rollback',
  request_id: 'req:test:rollback',
  capability: 'request:bank_screen_owner:COMMIT_WRITE:bank:persist:continuous_run_state'
});
equal(failureResult.ok, false, 'injected failure denied');
equal(failureResult.code, 'DENIED_ATOMIC_WRITE_FAILED', 'atomic failure code');
equal(Object.fromEntries(failing.values), persistedSeed, 'atomic failure restores exact prior bytes');

const readsBeforeStateLoad = seeded.calls.get;
const writesBeforeStateLoad = seeded.calls.set;
load(runtime, 'pmp-continuous-run-state-bank-v1.js');
equal(seeded.calls.get, readsBeforeStateLoad, 'state module load performs no storage read');
equal(seeded.calls.set, writesBeforeStateLoad, 'state module load performs no storage write');
const stateApi = runtime.window.PMPContinuousRunStateBankV1;
equal(stateApi.owner, 'continuous_run_level_owner', 'state API canonical owner');
equal(stateApi.version, '2.0.0-pass9-unit3-owner-boundary', 'state API version');
const readsBefore = seeded.calls.get;
const writesBefore = seeded.calls.set;
const current = stateApi.readRunState();
check(seeded.calls.get > readsBefore, 'state read reads storage');
equal(seeded.calls.set, writesBefore, 'state read never persists');
equal(current.type, 'PMP_UNIVERSAL_CONTINUOUS_WORK_ENGINE_STATE_V1', 'current state normalized in memory');
equal(current.n, 1, 'current explicit committed payload preserved');
const manifest = stateApi.buildManifest(current, stateApi.readReceipts());
equal(manifest.hash_algorithm, 'SHA-256', 'manifest algorithm');
check(/^[0-9a-f]{64}$/.test(manifest.state_hash), 'manifest state SHA');
check(/^[0-9a-f]{64}$/.test(manifest.receipts_hash), 'manifest receipts SHA');
const writeManifestBefore = seeded.calls.set;
const writeManifestDenied = stateApi.writeManifest();
equal(writeManifestDenied.code, 'READ_PATH_CANNOT_WRITE_MANIFEST', 'read manifest write denied');
equal(seeded.calls.set, writeManifestBefore, 'writeManifest compatibility path no write');
const clearBefore = Object.fromEntries(seeded.values);
const clearDenied = stateApi.clearCurrentState();
equal(clearDenied.code, 'CLEAR_DENIED_BY_DEFAULT', 'clear default denial');
equal(Object.fromEntries(seeded.values), clearBefore, 'denied clear preserves bytes');
const manualWrong = stateApi.manualClear('MANUAL CLEAR WORK STATE', {capability: 'wrong'});
equal(manualWrong.code, 'CLEAR_DENIED_BY_DEFAULT', 'manual clear wrong capability denied');
const updateBefore = seeded.calls.set;
const update = stateApi.setCurrentWorkItem('bounded-item');
check(update.owner_receipt && update.owner_receipt.code === 'COMMITTED', 'state update receives Bank receipt');
equal(update.state.current_work_item, 'bounded-item', 'state lifecycle update');
equal(update.state.current_item, 'bounded-item', 'legacy state alias update');
equal(seeded.calls.set - updateBefore, 3, 'state update atomic three-key bundle');
equal(JSON.parse(seeded.values.get('pmp_continuous_run_state_bank_v1')).current_work_item, 'bounded-item', 'state update persisted');
equal(JSON.parse(seeded.values.get('unrelated_user_key')).value, 42, 'state update preserves unrelated');
const exportBefore = seeded.calls.set;
const pack = stateApi.exportResumePack();
equal(pack.type, 'PMP_CONTINUOUS_WORK_ENGINE_RESUME_PACK_V1', 'resume pack type');
equal(seeded.calls.set, exportBefore, 'resume export read-only');
const resetBeforeRemove = seeded.calls.remove;
const reset = stateApi.manualClear('MANUAL CLEAR WORK STATE', {capability: 'manual:continuous_run_level_owner:reset_state_preserve_keys'});
equal(reset.ok, true, 'exact manual reset accepted');
equal(reset.changed, true, 'manual reset changed');
equal(seeded.calls.remove, resetBeforeRemove, 'manual reset preserves keys rather than deleting');
check(seeded.values.has('pmp_continuous_run_state_bank_v1'), 'state key preserved after reset');
check(seeded.values.has('pmp_continuous_run_state_receipts_v1'), 'receipt key preserved after reset');
check(seeded.values.has('pmp_continuous_run_state_manifest_v1'), 'manifest key preserved after reset');
equal(JSON.parse(seeded.values.get('unrelated_user_key')).value, 42, 'manual reset preserves unrelated');

const routerLoadGets = seeded.calls.get;
const routerLoadSets = seeded.calls.set;
load(runtime, 'pmp-master-bank-inventory-router-v1.js');
equal(seeded.calls.get, routerLoadGets, 'router load performs no storage read');
equal(seeded.calls.set, routerLoadSets, 'router load performs no storage write');
const router = runtime.window.PMPMasterBankInventoryRouterV1;
equal(router.owner, 'bank_screen_owner', 'router canonical owner');
equal(router.version, '2.0.0-pass9-unit3-owner-boundary', 'router version');
const inventorySetBefore = seeded.calls.set;
const inventory = router.inventory();
equal(seeded.calls.set, inventorySetBefore, 'inventory read never persists');
check(inventory.banks.continuous_run, 'continuous run bank preserved');
check(inventory.banks.connections, 'missing bank normalized in memory');
check(inventory.rule.includes('Active tab'), 'no active-tab ownership rule');
check(inventory.rule.includes('never create ownership'), 'explicit ownership rule');
const routerWriteBefore = seeded.calls.set;
const bankWrite = router.recordWrite({
  owning_bank: 'continuous_run',
  record_id: 'p9u3-test-record',
  record_type: 'test',
  source_tab: 'bank',
  active_system: 'continuous_run',
  action: 'test_write',
  summary: 'bounded deterministic write'
});
equal(bankWrite.ok, true, 'Bank record write accepted');
equal(seeded.calls.set - routerWriteBefore, 2, 'Bank record write exact inventory and route bundle');
check(router.inventory().banks.continuous_run.records.some(row => row.record_id === 'p9u3-test-record'), 'Bank record persisted');
const deleteBytes = Object.fromEntries(seeded.values);
const deleteDenied = router.recordDelete({owning_bank: 'continuous_run',record_id: 'p9u3-test-record'});
equal(deleteDenied.code, 'DELETE_DENIED_BY_DEFAULT', 'record delete default deny');
equal(Object.fromEntries(seeded.values), deleteBytes, 'denied record delete preserves bytes');
const deleteAccepted = router.recordDelete({
  owning_bank: 'continuous_run',
  record_id: 'p9u3-test-record',
  user_confirmed: true,
  capability: 'manual:bank_screen_owner:delete_record:continuous_run'
});
equal(deleteAccepted.ok, true, 'exact user-confirmed record delete accepted');
check(!router.inventory().banks.continuous_run.records.some(row => row.record_id === 'p9u3-test-record'), 'exact record deleted');
equal(JSON.parse(seeded.values.get('unrelated_user_key')).value, 42, 'Bank delete preserves unrelated');
const connectionsWrite = router.recordWrite({
  owning_bank: 'connections',
  record_id: 'chat_memory_deposit:packet-1',
  record_type: 'chat_memory_deposit',
  source_tab: 'bank',
  active_system: 'connections_bank',
  action: 'test_write'
});
equal(connectionsWrite.ok, true, 'Connections inventory record accepted');
seeded.values.set('pmp_connections_bank_chat_memory_deposits_v1', JSON.stringify({
  records: {'packet-1': {indexeddb_key: 'packet-1-binary'}},
  categories: {test: ['packet-1']}
}, null, 2));
const connectionsBefore = Object.fromEntries(seeded.values);
const connectionsDenied = router.recordDelete({
  owning_bank: 'connections',
  record_id: 'chat_memory_deposit:packet-1',
  connections_deposits_after_delete: {records: {},categories: {}}
});
equal(connectionsDenied.code, 'DELETE_DENIED_BY_DEFAULT', 'Connections delete default deny');
equal(Object.fromEntries(seeded.values), connectionsBefore, 'denied Connections delete preserves exact bytes');
const connectionsDeleteWrites = seeded.calls.set;
const connectionsAccepted = router.recordDelete({
  owning_bank: 'connections',
  record_id: 'chat_memory_deposit:packet-1',
  user_confirmed: true,
  capability: 'manual:bank_screen_owner:delete_record:connections',
  connections_deposits_after_delete: {records: {},categories: {}}
});
equal(connectionsAccepted.ok, true, 'exact user-confirmed Connections delete accepted');
equal(seeded.calls.set - connectionsDeleteWrites, 3, 'Connections delete atomically commits inventory, route, and deposit index');
equal(JSON.parse(seeded.values.get('pmp_connections_bank_chat_memory_deposits_v1')), {records: {},categories: {}}, 'Connections deposit index committed by Bank Owner');
check(!router.inventory().banks.connections.records.some(row => row.record_id === 'chat_memory_deposit:packet-1'), 'Connections inventory record deleted in same commit');
equal(JSON.parse(seeded.values.get('unrelated_user_key')).value, 42, 'Connections delete preserves unrelated');
const cancellationResource = 'bank:persist:project_registry';
const cancellationGap = commit({
  resource: cancellationResource,
  writes: [{key: 'pmp_bank_project_registry_v1',value: {projects: []}}],
  cancellation_epoch: 2
});
equal(cancellationGap.code, 'DENIED_CANCELLATION_ADVANCE', 'cancellation epoch gap denied');
const cancellationAdvance = commit({
  resource: cancellationResource,
  writes: [{key: 'pmp_bank_project_registry_v1',value: {projects: []}}],
  cancellation_epoch: 1
});
equal(cancellationAdvance.ok, true, 'next cancellation epoch accepted');
const cancellationStale = commit({
  resource: cancellationResource,
  writes: [{key: 'pmp_bank_project_registry_v1',value: {projects: [{id: 'stale'}]}}],
  cancellation_epoch: 0
});
equal(cancellationStale.code, 'DENIED_STALE_CANCELLATION', 'stale cancellation epoch denied');

const finalSnapshot = boundary.snapshot();
check(finalSnapshot.receipt_count >= 4, 'owner receipts accumulated');
check(finalSnapshot.receipt_count <= 256, 'receipt view bounded');
equal(finalSnapshot.recent_receipts.length, finalSnapshot.receipt_count, 'all current bounded receipts visible');
for (let index = 0; index < finalSnapshot.recent_receipts.length; index += 1) {
  const receipt = finalSnapshot.recent_receipts[index];
  check(/^[0-9a-f]{64}$/.test(receipt.request_sha256), `receipt ${index} request hash`);
  check(/^[0-9a-f]{64}$/.test(receipt.receipt_sha256), `receipt ${index} receipt hash`);
  equal(receipt.receipt_version, 'PMP_BANK_CONTINUOUS_RUN_OWNER_RECEIPT_V1', `receipt ${index} version`);
  equal(receipt.target_owner, 'bank_screen_owner', `receipt ${index} target`);
  if (index > 0) equal(receipt.previous_receipt_sha256, finalSnapshot.recent_receipts[index - 1].receipt_sha256, `receipt ${index} chain`);
}

const boundarySource = source('pmp-bank-continuous-run-owner-boundary-v1.js');
const stateSource = source('pmp-continuous-run-state-bank-v1.js');
const routerSource = source('pmp-master-bank-inventory-router-v1.js');
const masterSource = source('pmp-master-bank-tab-v1.js');
const ownerSource = source('pmp-bank-screen-owner-v1.js');
const bridgeSource = source('pmp-bank-owner-dependency-bridge-v1.js');
const loaderSource = source('pmp-continuous-run-bank-order-frame-loader-v1.js');
const helperOwnerSource = source('pmp-helper-owner-integration-v1.js');
const modeSource = source('pmp-bank-mode1-hide-unchecked-v1.js');
const cleanerSource = source('pmp-bank-scoped-test-data-cleaner-v1.js');
const diagnosticSource = source('pmp-bank-continuous-run-owner-split-diagnostic-v1.js');
const connectionDeleteSource = source('pmp-connections-bank-packet-delete-v1.js');
const inner23 = source('pmp-current-inner-cleanbug-rgcontrols-v23.html');
const inner4 = source('pmp-current-inner-cleanbug-rgcontrols-v4.html');

for (const [name, text] of [
  ['boundary', boundarySource],
  ['state', stateSource],
  ['router', routerSource],
  ['master', masterSource],
  ['continuous owner', ownerSource],
  ['bridge', bridgeSource],
  ['loader', loaderSource],
  ['mode shim', modeSource],
  ['cleaner shim', cleanerSource],
  ['diagnostic', diagnosticSource],
  ['connections delete', connectionDeleteSource]
]) {
  check(!text.includes('indexedDB.open'), `${name} does not open IndexedDB`);
  check(!text.includes('MIGRATE_STORAGE'), `${name} does not invoke migration`);
}
check(!stateSource.includes('Math.imul'), 'state no FNV hash');
check(!routerSource.includes("rule:'The active tab or active system creates ownership"), 'old ownership rule removed');
check(stateSource.includes("hash_algorithm:'SHA-256'"), 'state manifest SHA binding');
check(stateSource.includes('READ_PATH_CANNOT_WRITE_MANIFEST'), 'read manifest fail closed');
check(stateSource.includes('CLEAR_DENIED_BY_DEFAULT'), 'clear default denial present');
check(!stateSource.includes('localStorage.removeItem'), 'state never deletes storage keys');
check(routerSource.includes('DELETE_DENIED_BY_DEFAULT'), 'router delete default denial present');
check(routerSource.includes('input.user_confirmed!==true'), 'router exact user confirmation');
check(connectionDeleteSource.includes("capability:'manual:bank_screen_owner:delete_record:connections'"), 'Connections delete exact capability');
check(connectionDeleteSource.includes("connections_deposits_after_delete:deposits"), 'Connections deletion routes final deposit state through Bank Owner');
check(!connectionDeleteSource.includes('localStorage.setItem'), 'Connections delete has no direct localStorage writer');
check(!connectionDeleteSource.includes('setInterval('), 'Connections delete has no recurring timer');
check(ownerSource.includes("capability:'manual:bank_screen_owner:delete_record:project_registry'"), 'project deletion exact capability');
check(ownerSource.includes("window.confirm('Delete this Bank project?"), 'project deletion exact user confirmation');
check(!masterSource.includes('setInterval('), 'Bank master no recurring painter');
check(!masterSource.includes('.recordWrite('), 'opening Bank detail never writes inventory');
check(!ownerSource.includes('setInterval('), 'Continuous Run owner no recurring painter');
check(!bridgeSource.includes('setInterval('), 'dependency bridge no recurring timer');
check(!bridgeSource.includes('setTimeout('), 'dependency bridge no startup timer cascade');
check(!bridgeSource.includes('w[name]=api'), 'dependency bridge never copies APIs');
check(bridgeSource.includes('mutable_apis_copied:0'), 'dependency bridge reports no copy');
check(!loaderSource.includes('setInterval('), 'frame loader no recurring scan');
check(loaderSource.includes('EVENT_DRIVEN_NEW_DOCUMENT_ONCE'), 'frame loader event-driven mode');
check(loaderSource.includes('bank_owner_duplicate_injection_attempted:false'), 'frame loader duplicate denial');
check(
  helperOwnerSource.includes(crypto.createHash('sha256').update(loaderSource).digest('hex')),
  'Helper Owner binds the exact repaired frame-loader source hash'
);
check(!modeSource.includes('document.'), 'legacy mode shim no DOM');
check(!modeSource.includes('localStorage'), 'legacy mode shim no storage');
check(!modeSource.includes('setInterval('), 'legacy mode shim no interval');
check(modeSource.includes('PASSIVE_COMPATIBILITY_HELD'), 'legacy mode held');
check(!cleanerSource.includes('document.'), 'legacy cleaner shim no DOM');
check(!cleanerSource.includes('localStorage'), 'legacy cleaner shim no storage');
check(!cleanerSource.includes('setInterval('), 'legacy cleaner shim no interval');
check(cleanerSource.includes('DELETE_DENIED_BY_DEFAULT'), 'legacy cleaner deny');
check(diagnosticSource.includes('boundarySnapshot'), 'Diagnostics reads owner boundary');
check(diagnosticSource.includes('sha256_receipt_chain'), 'Diagnostics reports SHA chain');
check(!diagnosticSource.includes("setTimeout(()=>evaluate('script_load"), 'Diagnostics no automatic run');

const boundaryPos = inner23.indexOf('pmp-bank-continuous-run-owner-boundary-v1.js?fresh=');
const statePos = inner23.indexOf('pmp-continuous-run-state-bank-v1.js?fresh=');
const routerPos = inner23.indexOf('pmp-master-bank-inventory-router-v1.js?fresh=');
const masterPos = inner23.indexOf('pmp-master-bank-tab-v1.js?fresh=');
const ownerPos = inner23.indexOf('pmp-bank-screen-owner-v1.js?fresh=');
check(boundaryPos > 0, 'boundary loaded');
check(boundaryPos < statePos, 'boundary before state');
check(boundaryPos < routerPos, 'boundary before router');
check(statePos < masterPos, 'state before Bank tab');
check(routerPos < masterPos, 'router before Bank tab');
check(masterPos < ownerPos, 'Bank shell before Continuous Run owner');
equal((inner23.match(/pmp-bank-mode1-hide-unchecked-v1\.js/g) || []).length, 0, 'legacy mode removed from v23');
equal((inner23.match(/pmp-bank-scoped-test-data-cleaner-v1\.js/g) || []).length, 0, 'legacy cleaner removed from v23');
equal((inner4.match(/pmp-bank-mode1-hide-unchecked-v1\.js/g) || []).length, 1, 'one compatibility mode load remains');
equal((inner4.match(/pmp-bank-scoped-test-data-cleaner-v1\.js/g) || []).length, 1, 'one compatibility cleaner load remains');
equal((inner23.match(/pmp-bank-continuous-run-owner-boundary-v1\.js/g) || []).length, 1, 'one boundary load');

console.log(`PASS: P9-U3 Bank/Continuous Run owner integration (${assertions}/${assertions})`);
