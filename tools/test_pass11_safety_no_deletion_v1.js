#!/usr/bin/env node
'use strict';

const assert = require('assert');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
let assertions = 0;
function check(value, message) { assertions += 1; assert(value, message); }
function equal(actual, expected, message) { assertions += 1; assert.deepStrictEqual(actual, expected, message); }
function read(relative) { return fs.readFileSync(path.join(ROOT, relative), 'utf8'); }
function json(relative) { return JSON.parse(read(relative)); }
function clone(value) { return JSON.parse(JSON.stringify(value)); }

class FakeStorage {
  constructor(initial) {
    this.values = new Map(Object.entries(initial || {}));
    this.setCalls = [];
    this.removeCalls = [];
    this.failOnSet = 0;
  }
  getItem(key) { return this.values.has(String(key)) ? this.values.get(String(key)) : null; }
  setItem(key, value) {
    this.setCalls.push([String(key), String(value)]);
    if (this.failOnSet && this.setCalls.length === this.failOnSet) throw new Error('fixture write failure');
    this.values.set(String(key), String(value));
  }
  removeItem(key) { this.removeCalls.push(String(key)); this.values.delete(String(key)); }
  clear() { throw new Error('clear is forbidden in fixture'); }
  rawObject() { return Object.fromEntries(this.values.entries()); }
}

function fixture(initial) {
  const storage = new FakeStorage(initial);
  const listeners = Object.create(null);
  const document = {
    querySelectorAll() { return []; },
    getElementById() { return null; }
  };
  const context = {
    console,
    Date,
    JSON,
    Math,
    Map,
    Set,
    WeakMap,
    WeakSet,
    Object,
    Array,
    String,
    Number,
    Boolean,
    RegExp,
    Error,
    Promise,
    TextEncoder,
    localStorage: storage,
    document,
    confirm() { return true; },
    CustomEvent: class CustomEvent {
      constructor(type, options) { this.type = type; this.detail = options && options.detail; }
    },
    addEventListener(type, callback) {
      if (!listeners[type]) listeners[type] = [];
      listeners[type].push(callback);
    },
    dispatchEvent(event) {
      for (const callback of listeners[event.type] || []) callback(event);
      return true;
    },
    setTimeout() { return 1; },
    setInterval() { return 1; },
    clearTimeout() {},
    clearInterval() {}
  };
  context.window = context;
  context.top = context;
  context.globalThis = context;
  context.document.defaultView = context;
  vm.createContext(context);
  return {context, storage, listeners};
}

function load(context, relative) {
  vm.runInContext(read(relative), context, {filename: relative});
}

function authorityReceipt(guard, input, overrides) {
  const now = Date.now();
  const body = Object.assign({
    type: guard.delete_authority_type,
    version: '1.0.0',
    decision: 'ALLOW_DELETE_EXCEPTION',
    single_use: true,
    wildcards_allowed: false,
    operation_id: input.operation_id,
    requester_owner: input.requester_owner,
    target_owner: input.target_owner,
    record_id: input.record_id,
    expected_payload_sha256: input.expected_payload_sha256,
    issued_at: new Date(now - 1000).toISOString(),
    expires_at: new Date(now + 60000).toISOString(),
    user_confirmation_phrase: 'DELETE ' + input.record_id
  }, overrides || {});
  body.receipt_sha256 = guard.sha256(guard.canonical(body));
  return body;
}

const policy = json('pmp-safety-no-deletion-policy-v1.json');
equal(policy.type, 'PMP_SAFETY_NO_DELETION_POLICY_V1', 'policy type');
equal(policy.version, '1.0.0-pass11', 'policy version');
equal(policy.default_decision, 'DENY', 'default deny');
equal(policy.protected_assets.length, 10, 'protected asset count');
for (const asset of [
  'persisted_user_data',
  'bank_records',
  'route_and_last_good_state',
  'diagnostic_and_proof_evidence',
  'checkpoint_packages',
  'unrelated_storage'
]) check(policy.protected_assets.includes(asset), `protected ${asset}`);
equal(policy.operation_classes.ARCHIVE.physical_delete_allowed, false, 'archive no delete');
equal(policy.operation_classes.ARCHIVE.active_index_removal_allowed, true, 'archive active index');
equal(policy.operation_classes.QUARANTINE.physical_delete_allowed, false, 'quarantine no delete');
equal(policy.operation_classes.DELETE_EXCEPTION.default, 'DENY', 'delete exception deny');
equal(policy.operation_classes.DELETE_EXCEPTION.wildcards_allowed, false, 'no wildcard');
equal(policy.operation_classes.DELETE_EXCEPTION.automatic_retry_allowed, false, 'no retry');
equal(policy.operation_classes.MIGRATION.default, 'INACTIVE_GATE', 'migration gate inactive');
equal(policy.operation_classes.MIGRATION.production_user_data_authority_required, true, 'migration authority');
equal(policy.transaction_phases.length, 7, 'transaction phases');
equal(policy.transaction_phases[0], 'PREFLIGHT', 'transaction preflight');
equal(policy.transaction_phases[6], 'ROLLBACK_ON_ANY_FAILURE', 'transaction rollback');
equal(policy.safe_writer_rules.partial_write, 'ROLLBACK_EXACT_BYTES', 'partial rollback');
equal(policy.safe_writer_rules.unrelated_bytes, 'PRESERVE_EXACTLY', 'unrelated bytes');
equal(policy.recovery_rules.user_data_never_used_as_test_fixture, true, 'no user fixtures');
equal(policy.active_connections_bank.visible_action, 'ARCHIVE_SELECTED_PACKET', 'connections archive');
equal(policy.active_connections_bank.physical_indexeddb_delete, false, 'no IDB delete');
equal(policy.formal_proof.performed, false, 'no formal proof');
equal(policy.formal_proof.pr_122_quarantined_untouched, true, 'PR122 preserved');

const direct = fixture();
load(direct.context, 'pmp-safety-no-deletion-guard-v1.js');
const guard = direct.context.PMPSafetyNoDeletionGuardV1;
check(guard, 'guard exported');
equal(guard.type, 'PMP_SAFETY_NO_DELETION_GUARD_V1', 'guard type');
equal(guard.policy_type, policy.type, 'guard policy binding');
equal(guard.snapshot().status, 'READY', 'guard ready');
equal(guard.snapshot().default_delete, 'DENY', 'guard delete deny');
equal(guard.snapshot().production_migration, 'INACTIVE_GATE', 'guard migration gate');
equal(guard.snapshot().load_effects.storage_writes, 0, 'load writes');
equal(guard.snapshot().load_effects.storage_deletes, 0, 'load deletes');

const archiveInput = {
  action: 'ARCHIVE',
  operation_id: 'op:p11:archive:direct:1',
  requester_owner: 'bank_screen_owner',
  target_owner: 'bank_screen_owner',
  resource: 'bank:connections',
  owning_bank: 'connections',
  record_id: 'chat_memory_deposit:direct',
  expected_payload_sha256: guard.sha256('direct payload'),
  payload_bytes: 14,
  preservation: 'PRESERVE_EXACT_PAYLOAD_RECOVERABLE',
  user_confirmed: true,
  capability: 'manual:bank_screen_owner:archive_record:connections'
};
const archiveDenials = [
  ['action', 'DELETE', 'DENIED_ACTION'],
  ['operation_id', 'bad', 'DENIED_OPERATION_ID'],
  ['requester_owner', 'helper', 'DENIED_OWNER'],
  ['target_owner', 'continuous_run_level_owner', 'DENIED_OWNER'],
  ['resource', 'unknown', 'DENIED_RESOURCE'],
  ['record_id', '', 'DENIED_RECORD_ID'],
  ['expected_payload_sha256', 'bad', 'DENIED_PAYLOAD_HASH'],
  ['payload_bytes', -1, 'DENIED_PAYLOAD_BYTES'],
  ['preservation', 'DROP_PAYLOAD', 'DENIED_PRESERVATION'],
  ['user_confirmed', false, 'DENIED_USER_CONFIRMATION'],
  ['capability', 'wildcard', 'DENIED_CAPABILITY']
];
for (const [key, value, code] of archiveDenials) {
  const candidate = Object.assign({}, archiveInput, {[key]: value, operation_id: archiveInput.operation_id + ':' + key});
  if (key === 'operation_id') candidate.operation_id = value;
  const result = guard.authorizeArchive(candidate);
  equal(result.ok, false, `archive denial ${key}`);
  equal(result.code, code, `archive denial code ${key}`);
  equal(result.effects.storage_deletes, 0, `archive denial effect ${key}`);
}
const archiveAllowed = guard.authorizeArchive(archiveInput);
equal(archiveAllowed.ok, true, 'archive allowed');
equal(archiveAllowed.code, 'ARCHIVE_AUTHORIZED_EXACT_PAYLOAD_PRESERVED', 'archive allow code');
equal(archiveAllowed.effects.storage_deletes, 0, 'archive allow no delete');
check(/^[0-9a-f]{64}$/.test(archiveAllowed.receipt.receipt_sha256), 'archive receipt hash');
const archiveReplay = guard.authorizeArchive(archiveInput);
equal(archiveReplay.ok, false, 'archive replay denied');
equal(archiveReplay.code, 'DENIED_ARCHIVE_OPERATION_REPLAY', 'archive replay code');

const transactionInput = {
  action: 'TRANSACTIONAL_WRITE',
  operation_id: 'op:p11:transaction:1',
  requester_owner: 'bank_screen_owner',
  target_owner: 'bank_screen_owner',
  resource: 'bank:connections',
  expected_version: 0,
  payload_sha256: guard.sha256('after'),
  rollback_sha256: guard.sha256('before'),
  backup_ref: 'backup:p11:fixture:1',
  append_only_receipt: true
};
const transaction = guard.planTransaction(transactionInput);
equal(transaction.ok, true, 'transaction allowed');
equal(transaction.phases.length, 7, 'transaction phase count');
equal(transaction.storage_deletes_allowed, 0, 'transaction no delete');
equal(transaction.automatic_retry, false, 'transaction no retry');
equal(transaction.unrelated_bytes_policy, 'PRESERVE_EXACTLY', 'transaction unrelated bytes');
for (const [key, value, code] of [
  ['action', 'DELETE', 'DENIED_TRANSACTION_ACTION'],
  ['operation_id', 'bad', 'DENIED_OPERATION_ID'],
  ['target_owner', 'other', 'DENIED_OWNER_SCOPE'],
  ['resource', '', 'DENIED_RESOURCE'],
  ['expected_version', -1, 'DENIED_EXPECTED_VERSION'],
  ['payload_sha256', 'bad', 'DENIED_TRANSACTION_HASH'],
  ['rollback_sha256', 'bad', 'DENIED_TRANSACTION_HASH'],
  ['backup_ref', '', 'DENIED_BACKUP_REF'],
  ['append_only_receipt', false, 'DENIED_APPEND_ONLY_RECEIPT']
]) {
  const candidate = Object.assign({}, transactionInput, {[key]: value, operation_id: transactionInput.operation_id + ':' + key});
  if (key === 'operation_id') candidate.operation_id = value;
  const result = guard.planTransaction(candidate);
  equal(result.ok, false, `transaction denial ${key}`);
  equal(result.code, code, `transaction denial code ${key}`);
  equal(result.effects.storage_deletes, 0, `transaction denial effect ${key}`);
}

const deleteInput = {
  action: 'DELETE_EXCEPTION',
  operation_id: 'op:p11:delete:fixture:1',
  requester_owner: 'bank_screen_owner',
  target_owner: 'bank_screen_owner',
  resource: 'bank:connections',
  record_id: 'chat_memory_deposit:delete-fixture',
  expected_payload_sha256: guard.sha256('delete fixture'),
  user_confirmation_phrase: 'DELETE chat_memory_deposit:delete-fixture'
};
deleteInput.authority_receipt = authorityReceipt(guard, deleteInput);
const deleteAllowed = guard.authorizeDeleteException(deleteInput);
equal(deleteAllowed.ok, true, 'exact delete authority accepted');
equal(deleteAllowed.code, 'DELETE_EXCEPTION_AUTHORIZED_ONCE', 'delete authority code');
equal(deleteAllowed.effects.authority_consumed, true, 'delete authority consumed');
equal(deleteAllowed.effects.storage_deletes, 0, 'authorization itself deletes nothing');
const deleteReplay = guard.authorizeDeleteException(deleteInput);
equal(deleteReplay.ok, false, 'delete authority replay denied');
equal(deleteReplay.code, 'DENIED_EXACT_AUTHORITY_REPLAY', 'delete replay code');
for (const mutation of [
  {key: 'type', value: 'WRONG', code: 'DENIED_EXACT_AUTHORITY_TYPE'},
  {key: 'decision', value: 'DENY', code: 'DENIED_EXACT_AUTHORITY_DECISION'},
  {key: 'record_id', value: 'other', code: 'DENIED_EXACT_AUTHORITY_RESOURCE'},
  {key: 'user_confirmation_phrase', value: 'DELETE *', code: 'DENIED_EXACT_USER_CONFIRMATION'},
  {key: 'receipt_sha256', value: '0'.repeat(64), code: 'DENIED_EXACT_AUTHORITY_INTEGRITY'}
]) {
  const candidate = clone(deleteInput);
  candidate.operation_id = 'op:p11:delete:mutation:' + mutation.key;
  candidate.record_id = candidate.authority_receipt.record_id;
  candidate.user_confirmation_phrase = candidate.authority_receipt.user_confirmation_phrase;
  candidate.authority_receipt.operation_id = candidate.operation_id;
  candidate.authority_receipt[mutation.key] = mutation.value;
  if (mutation.key !== 'receipt_sha256') {
    candidate.authority_receipt.receipt_sha256 = guard.sha256(guard.canonical(Object.assign({}, candidate.authority_receipt, {receipt_sha256: undefined})));
    const body = clone(candidate.authority_receipt);
    delete body.receipt_sha256;
    candidate.authority_receipt.receipt_sha256 = guard.sha256(guard.canonical(body));
  }
  const result = guard.authorizeDeleteException(candidate);
  equal(result.ok, false, `delete mutation ${mutation.key}`);
  equal(result.code, mutation.code, `delete mutation code ${mutation.key}`);
}

const record = {
  record_id: 'chat_memory_deposit:packet-1',
  record_type: 'chat_memory_deposit',
  owning_bank: 'connections',
  payload_key: 'binary:packet-1',
  summary: 'fixture packet'
};
const inventory = {
  type: 'PMP_MASTER_BANK_INVENTORY_V1',
  banks: {
    connections: {name: 'Connections Bank', records: [clone(record)], references: []}
  }
};
const deposits = {
  records: {
    'packet-1': {id: 'packet-1', indexeddb_key: 'binary:packet-1', title: 'fixture', bytes: 123}
  },
  categories: {fixture: ['packet-1']},
  archived_records: {}
};
const initial = {
  pmp_master_bank_inventory_v1: JSON.stringify(inventory),
  pmp_source_bank_router_receipts_v1: JSON.stringify([]),
  pmp_connections_bank_chat_memory_deposits_v1: JSON.stringify(deposits),
  unrelated_fixture_key: 'UNRELATED-EXACT-BYTES'
};
const active = fixture(initial);
load(active.context, 'pmp-bank-continuous-run-owner-boundary-v1.js');
load(active.context, 'pmp-safety-no-deletion-guard-v1.js');
load(active.context, 'pmp-master-bank-inventory-router-v1.js');
const router = active.context.PMPMasterBankInventoryRouterV1;
check(router, 'router exported');
equal(router.version, '2.0.0-pass9-unit3-owner-boundary', 'router compatibility version');
equal(router.safety_version, '3.0.0-pass11-safety-no-deletion', 'router Pass11 safety version');
check(typeof router.recordArchive === 'function', 'archive API');
const defaultDelete = router.recordDelete({
  owning_bank: 'connections',
  record_id: record.record_id,
  operation_id: 'op:p11:delete:legacy:1',
  expected_payload_sha256: active.context.PMPSafetyNoDeletionGuardV1.sha256(
    active.context.PMPSafetyNoDeletionGuardV1.canonical(record)
  ),
  user_confirmation_phrase: 'DELETE ' + record.record_id,
  user_confirmed: true,
  capability: 'manual:bank_screen_owner:delete_record:connections'
});
equal(defaultDelete.ok, false, 'legacy manual delete denied');
equal(defaultDelete.code, 'DENIED_EXACT_AUTHORITY_TYPE', 'legacy delete exact authority required');
equal(active.storage.rawObject().unrelated_fixture_key, 'UNRELATED-EXACT-BYTES', 'delete denial unrelated bytes');
equal(active.storage.removeCalls.length, 0, 'delete denial no remove');

const depositsAfterArchive = clone(deposits);
depositsAfterArchive.archived_records['packet-1'] = {
  record: clone(deposits.records['packet-1']),
  archived_at: new Date().toISOString(),
  recoverable: true,
  indexeddb_key: 'binary:packet-1',
  exact_payload_sha256: active.context.PMPSafetyNoDeletionGuardV1.sha256(
    active.context.PMPSafetyNoDeletionGuardV1.canonical(deposits.records['packet-1'])
  ),
  physical_payload_deleted: false
};
delete depositsAfterArchive.records['packet-1'];
depositsAfterArchive.categories.fixture = [];
const archiveResult = router.recordArchive({
  owning_bank: 'connections',
  source_tab: 'bank',
  active_system: 'connections_bank',
  record_type: 'chat_memory_deposit',
  record_id: record.record_id,
  operation_id: 'op:p11:archive:fixture:packet-1',
  user_confirmed: true,
  capability: 'manual:bank_screen_owner:archive_record:connections',
  connections_deposits_after_archive: depositsAfterArchive
});
equal(archiveResult.ok, true, 'router archive succeeds');
equal(archiveResult.receipt.action, 'archive_record_exact_payload_preserved', 'archive receipt action');
equal(archiveResult.receipt.deleted_count, 0, 'archive deleted count');
equal(archiveResult.archived.recoverable, true, 'archive recoverable');
equal(archiveResult.archived.record, record, 'archive exact record');
equal(active.storage.removeCalls.length, 0, 'archive no storage remove');
equal(active.storage.getItem('unrelated_fixture_key'), 'UNRELATED-EXACT-BYTES', 'archive unrelated bytes');
const storedInventory = JSON.parse(active.storage.getItem('pmp_master_bank_inventory_v1'));
equal(storedInventory.banks.connections.records.length, 0, 'active index removed');
equal(storedInventory.banks.connections.archives.length, 1, 'archive retained');
equal(storedInventory.banks.connections.archives[0].record, record, 'stored archive exact');
const storedDeposits = JSON.parse(active.storage.getItem('pmp_connections_bank_chat_memory_deposits_v1'));
equal(Object.keys(storedDeposits.records).length, 0, 'active deposit index removed');
equal(storedDeposits.archived_records['packet-1'].record, deposits.records['packet-1'], 'deposit exact archive');
equal(storedDeposits.archived_records['packet-1'].physical_payload_deleted, false, 'binary retained');
const duplicateArchive = router.recordArchive({
  owning_bank: 'connections',
  record_id: record.record_id,
  operation_id: 'op:p11:archive:fixture:packet-1',
  user_confirmed: true,
  capability: 'manual:bank_screen_owner:archive_record:connections'
});
equal(duplicateArchive.ok, false, 'duplicate archive denied');
equal(duplicateArchive.code, 'ARCHIVE_RECORD_NOT_FOUND', 'duplicate no active record');
equal(active.storage.removeCalls.length, 0, 'duplicate no delete');

const failing = fixture(initial);
load(failing.context, 'pmp-bank-continuous-run-owner-boundary-v1.js');
load(failing.context, 'pmp-safety-no-deletion-guard-v1.js');
load(failing.context, 'pmp-master-bank-inventory-router-v1.js');
const beforeFailure = clone(failing.storage.rawObject());
failing.storage.failOnSet = failing.storage.setCalls.length + 2;
const failedArchive = failing.context.PMPMasterBankInventoryRouterV1.recordArchive({
  owning_bank: 'connections',
  record_id: record.record_id,
  operation_id: 'op:p11:archive:fixture:failure',
  user_confirmed: true,
  capability: 'manual:bank_screen_owner:archive_record:connections',
  connections_deposits_after_archive: depositsAfterArchive
});
equal(failedArchive.ok, false, 'partial archive fails');
equal(failedArchive.denial.code, 'DENIED_ATOMIC_WRITE_FAILED', 'partial archive failure code');
equal(failing.storage.rawObject(), beforeFailure, 'partial archive exact rollback');
equal(failing.storage.getItem('unrelated_fixture_key'), 'UNRELATED-EXACT-BYTES', 'partial archive unrelated bytes');

const connectionsSource = read('pmp-connections-bank-packet-delete-v1.js');
check(connectionsSource.includes('Archive Selected Packet'), 'archive button');
check(connectionsSource.includes('recordArchive'), 'archive owner API');
check(connectionsSource.includes('physical_payload_deleted:false'), 'payload retained marker');
check(connectionsSource.includes('Nothing will be deleted'), 'user message no delete');
equal(/indexedDB|objectStore|\.delete\(/.test(connectionsSource), false, 'no physical IndexedDB delete code');
equal(/localStorage\.removeItem/.test(connectionsSource), false, 'no localStorage removal');
check(connectionsSource.includes('there is no physical-delete call'), 'runtime rule');

const routerSource = read('pmp-master-bank-inventory-router-v1.js');
check(routerSource.includes('recordArchive'), 'router archive source');
check(routerSource.includes('authorizeDeleteException'), 'router exact delete gate');
check(routerSource.includes('ARCHIVE_RECORD_NOT_FOUND'), 'router missing record fail closed');
check(routerSource.includes('deleted_count:0'), 'router archive no delete');
check(routerSource.includes('exact_payload_sha256'), 'router archive payload hash');
check(routerSource.includes('recoverable:true'), 'router archive recoverable');

const inner = read('pmp-current-inner-cleanbug-rgcontrols-v23.html');
equal((inner.match(/pmp-safety-no-deletion-guard-v1\.js/g) || []).length, 1, 'one active safety guard');
check(inner.indexOf('pmp-safety-no-deletion-guard-v1.js') < inner.indexOf('pmp-master-bank-inventory-router-v1.js'), 'guard before router');
check(inner.indexOf('pmp-master-bank-inventory-router-v1.js') < inner.indexOf('pmp-connections-bank-packet-delete-v1.js'), 'router before connections archive');

const manifest = json('pmp-runtime-integrity-manifest-v1.json');
const manifestIndex = new Map(manifest.records.map(row => [row.path, row]));
for (const runtimePath of [
  'pmp-safety-no-deletion-guard-v1.js',
  'pmp-master-bank-inventory-router-v1.js',
  'pmp-connections-bank-packet-delete-v1.js',
  'pmp-current-inner-cleanbug-rgcontrols-v23.html'
]) {
  const payload = fs.readFileSync(path.join(ROOT, runtimePath));
  const digest = crypto.createHash('sha256').update(payload).digest('hex');
  check(manifestIndex.has(runtimePath), `manifest ${runtimePath}`);
  equal(manifestIndex.get(runtimePath).sha256_hex, digest, `manifest hash ${runtimePath}`);
  equal(manifestIndex.get(runtimePath).bytes, payload.length, `manifest bytes ${runtimePath}`);
}

const finalSnapshot = active.context.PMPSafetyNoDeletionGuardV1.snapshot();
equal(finalSnapshot.default_delete, 'DENY', 'final delete deny');
equal(finalSnapshot.archive_policy, 'PRESERVE_EXACT_PAYLOAD_RECOVERABLE', 'final archive policy');
equal(finalSnapshot.quarantine_policy, 'PRESERVE_EXACT_BYTES', 'final quarantine policy');
equal(finalSnapshot.production_migration, 'INACTIVE_GATE', 'final migration inactive');
equal(finalSnapshot.delete_exception.single_use, true, 'final delete single use');
equal(finalSnapshot.delete_exception.wildcards_allowed, false, 'final delete no wildcards');
equal(finalSnapshot.delete_exception.automatic_retry, false, 'final delete no retry');

console.log(`PASS: Pass 11 safety and no-deletion deterministic proof (${assertions}/${assertions})`);
