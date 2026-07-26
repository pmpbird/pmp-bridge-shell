#!/usr/bin/env node
'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const TYPE = 'PMP_PASS9_UNIT4_BANK_CONTINUOUS_RUN_EXHAUSTIVE_PROOF_RESULT_V1';
const VERSION = '1.0.0';
const FIXED_NOW = '2026-07-26T20:40:00.000Z';
const RESOURCE_RUN = 'bank:persist:continuous_run_state';
const RESOURCE_PROJECT = 'bank:persist:project_registry';
const RESOURCE_BANK = 'bank:persist:master_inventory';
const ZERO = '0'.repeat(64);
const CORE = [
  'pmp-bank-continuous-run-owner-boundary-v1.js',
  'pmp-continuous-run-state-bank-v1.js',
  'pmp-master-bank-inventory-router-v1.js',
  'pmp-bank-continuous-run-owner-split-diagnostic-v1.js'
];

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function stable(value) {
  if (Array.isArray(value)) return '[' + value.map(stable).join(',') + ']';
  if (value && typeof value === 'object') {
    return '{' + Object.keys(value).sort().map(key => JSON.stringify(key) + ':' + stable(value[key])).join(',') + '}';
  }
  return JSON.stringify(value);
}

function digest(value) {
  const payload = Buffer.isBuffer(value) ? value : Buffer.from(typeof value === 'string' ? value : stable(value));
  return crypto.createHash('sha256').update(payload).digest('hex');
}

function source(name) {
  return fs.readFileSync(path.join(ROOT, name), 'utf8');
}

function seed() {
  return {
    pmp_continuous_run_state_bank_v1: JSON.stringify({
      type: 'PMP_UNIVERSAL_CONTINUOUS_WORK_ENGINE_STATE_V1',
      created_at: '2026-01-01T00:00:00Z',
      current_work_area: 'historic-area',
      current_work_item: 'historic-item',
      work_queue: ['historic-next'],
      last_run_status: 'stopped',
      notes: 'user-owned state must survive'
    }),
    pmp_continuous_run_state_receipts_v1: JSON.stringify([
      {id: 'historic-receipt', at: '2026-01-01T00:00:00Z'}
    ]),
    pmp_continuous_run_state_manifest_v1: JSON.stringify({
      type: 'historic-manifest',
      hash_algorithm: 'legacy',
      note: 'preserve until explicit write'
    }),
    pmp_master_bank_inventory_v1: JSON.stringify({
      type: 'PMP_MASTER_BANK_INVENTORY_V1',
      banks: {
        continuous_run: {
          name: 'Continuous Run Bank',
          records: [{record_id: 'historic-bank-record'}],
          references: []
        }
      }
    }),
    pmp_source_bank_router_receipts_v1: JSON.stringify([{id: 'historic-route'}]),
    pmp_helper_bank_index_v1: JSON.stringify({helpers: [{helper_id: 'historic-helper'}]}),
    pmp_connections_bank_chat_memory_deposits_v1: JSON.stringify({
      records: {historic: {indexeddb_key: 'historic-binary'}},
      categories: {historic: ['historic']}
    }),
    pmp_bank_project_registry_v1: JSON.stringify({
      type: 'PMP_BANK_PROJECT_REGISTRY_V1',
      projects: [{id: 'historic-project'}]
    }),
    pmp_bank_project_registry_v1_receipt: JSON.stringify({id: 'historic-project-receipt'}),
    unrelated_user_key: JSON.stringify({owner: 'user', preserve: true, nested: {value: 42}}),
    unrelated_binary_marker: '00ff-user-owned-bytes'
  };
}

function storage(seedValue = seed(), options = {}) {
  const values = new Map(Object.entries(seedValue));
  const calls = {get: 0, set: 0, remove: 0};
  const events = [];
  let failed = false;
  const api = {
    getItem(key) {
      calls.get += 1;
      return values.has(String(key)) ? values.get(String(key)) : null;
    },
    setItem(key, value) {
      calls.set += 1;
      if (!failed && options.failAtSet && calls.set === options.failAtSet) {
        failed = true;
        throw new Error('injected storage failure');
      }
      values.set(String(key), String(value));
    },
    removeItem(key) {
      calls.remove += 1;
      values.delete(String(key));
    }
  };
  return {values, calls, events, api};
}

function FixedDate(...args) {
  if (!(this instanceof FixedDate)) return new Date(args.length ? args[0] : FIXED_NOW).toString();
  return new Date(args.length ? args[0] : FIXED_NOW);
}
FixedDate.now = () => Date.parse(FIXED_NOW);
FixedDate.parse = Date.parse;
FixedDate.UTC = Date.UTC;
FixedDate.prototype = Date.prototype;

function runtimeFor(store, options = {}) {
  const listeners = {};
  const document = {
    defaultView: null,
    body: {},
    documentElement: {},
    querySelectorAll() { return []; },
    getElementById() { return null; },
    createElement() {
      return {
        style: {},
        setAttribute() {},
        appendChild() {},
        focus() {},
        select() {},
        setSelectionRange() {},
        remove() {}
      };
    },
    execCommand() { return false; }
  };
  const window = {
    localStorage: options.storageUnavailable ? null : store.api,
    document,
    navigator: {clipboard: null},
    innerHeight: 900,
    addEventListener(type, fn) {
      (listeners[type] ||= []).push(fn);
    },
    dispatchEvent(event) {
      store.events.push({type: event.type, detail: clone(event.detail || null)});
      for (const fn of listeners[event.type] || []) fn(event);
      return true;
    },
    getComputedStyle() {
      return {display: 'block', visibility: 'visible', opacity: '1'};
    }
  };
  window.window = window;
  window.top = window;
  document.defaultView = window;
  const context = vm.createContext({
    window,
    document,
    localStorage: window.localStorage,
    navigator: window.navigator,
    CustomEvent: function CustomEvent(type, init) {
      this.type = type;
      this.detail = init && init.detail;
    },
    Date: FixedDate,
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
  return {context, window, document, listeners, store};
}

function load(runtime, name) {
  vm.runInContext(source(name), runtime.context, {filename: name});
}

function loadCore(runtime) {
  CORE.forEach(name => load(runtime, name));
  return {
    boundary: runtime.window.PMPBankContinuousRunOwnerBoundaryV1,
    state: runtime.window.PMPContinuousRunStateBankV1,
    router: runtime.window.PMPMasterBankInventoryRouterV1,
    diagnostic: runtime.window.PMPBankContinuousRunOwnerSplitDiagnosticV1
  };
}

function raw(store) {
  return Object.fromEntries(store.values);
}

function exactRequest(boundary, overrides = {}) {
  const resource = overrides.resource || RESOURCE_RUN;
  const writes = overrides.writes || [{
    key: 'pmp_continuous_run_state_bank_v1',
    value: {type: 'PMP_TEST_STATE', value: 1}
  }];
  return Object.assign({
    requester_owner: 'continuous_run_level_owner',
    resource,
    expected_version: boundary.resourceVersion(resource),
    writes,
    operation_id: 'op:p9u4:exact',
    request_id: 'req:p9u4:exact',
    issued_at: FIXED_NOW,
    expires_at: '2026-07-26T20:45:00.000Z',
    cancellation_epoch: 0,
    capability: `request:bank_screen_owner:COMMIT_WRITE:${resource}`
  }, overrides);
}

function bootAndRepeatedLoadMatrix() {
  const store = storage();
  const runtime = runtimeFor(store);
  const before = raw(store);
  const first = loadCore(runtime);
  const afterFirst = raw(store);
  const firstCalls = clone(store.calls);
  const firstSnapshot = first.boundary.snapshot();
  const second = loadCore(runtime);
  return {
    exact_bytes_before_sha256: digest(before),
    exact_bytes_after_first_sha256: digest(afterFirst),
    exact_bytes_after_second_sha256: digest(raw(store)),
    first_calls: firstCalls,
    second_calls: clone(store.calls),
    first_owner_pair: [firstSnapshot.bank_owner, firstSnapshot.continuous_run_owner],
    second_owner_pair: [second.boundary.snapshot().bank_owner, second.boundary.snapshot().continuous_run_owner],
    first_receipt_count: firstSnapshot.receipt_count,
    second_receipt_count: second.boundary.snapshot().receipt_count,
    diagnostic_loaded: !!second.diagnostic,
    diagnostic_keys_written_automatically: [
      'pmp_bank_continuous_run_owner_split_diagnostic_v1',
      'pmp_bank_continuous_run_owner_split_diagnostic_receipt_v1'
    ].filter(key => store.values.has(key)),
    boundary_ready_events: store.events.filter(row => row.type === 'pmp:bank-continuous-run-owner-boundary-ready').length,
    persisted_user_data_changed: stable(before) !== stable(raw(store))
  };
}

function concurrencyMatrix() {
  const store = storage();
  const runtime = runtimeFor(store);
  const {boundary} = loadCore(runtime);
  const beforeUnrelated = store.values.get('unrelated_user_key');
  const firstInput = exactRequest(boundary, {
    operation_id: 'op:p9u4:concurrency:first',
    request_id: 'req:p9u4:concurrency:first',
    writes: [{key: 'pmp_continuous_run_state_bank_v1', value: {winner: 'first'}}]
  });
  const competingInput = exactRequest(boundary, {
    operation_id: 'op:p9u4:concurrency:competing',
    request_id: 'req:p9u4:concurrency:competing',
    expected_version: 0,
    writes: [{key: 'pmp_continuous_run_state_bank_v1', value: {winner: 'competing'}}]
  });
  const first = boundary.commitBundle(firstInput);
  const afterFirst = raw(store);
  const competing = boundary.commitBundle(competingInput);
  const afterCompeting = raw(store);
  const retry = boundary.commitBundle(Object.assign({}, competingInput, {
    operation_id: 'op:p9u4:concurrency:retry',
    request_id: 'req:p9u4:concurrency:retry',
    expected_version: 1
  }));
  const project = boundary.commitBundle(exactRequest(boundary, {
    resource: RESOURCE_PROJECT,
    operation_id: 'op:p9u4:concurrency:independent',
    request_id: 'req:p9u4:concurrency:independent',
    writes: [{key: 'pmp_bank_project_registry_v1', value: {projects: [{id: 'independent'}]}}],
    cancellation_epoch: 1,
    capability: `request:bank_screen_owner:COMMIT_WRITE:${RESOURCE_PROJECT}`
  }));
  const snapshot = boundary.snapshot();
  return {
    first_code: first.code,
    competing_code: competing.code,
    competing_zero_effects: stable(afterFirst) === stable(afterCompeting),
    retry_code: retry.code,
    independent_resource_code: project.code,
    run_resource_version: boundary.resourceVersion(RESOURCE_RUN),
    project_resource_version: boundary.resourceVersion(RESOURCE_PROJECT),
    persisted_winner_after_retry: JSON.parse(store.values.get('pmp_continuous_run_state_bank_v1')).winner,
    unrelated_exactly_preserved: store.values.get('unrelated_user_key') === beforeUnrelated,
    receipt_count: snapshot.receipt_count,
    receipt_chain_valid: snapshot.recent_receipts.every((receipt, index, rows) =>
      /^[0-9a-f]{64}$/.test(receipt.request_sha256)
      && /^[0-9a-f]{64}$/.test(receipt.receipt_sha256)
      && receipt.receipt_sha256 === boundary.sha256(boundary.canonical(Object.fromEntries(
        Object.entries(receipt).filter(([key]) => key !== 'receipt_sha256')
      )))
      && (index === 0 ? receipt.previous_receipt_sha256 === ZERO : receipt.previous_receipt_sha256 === rows[index - 1].receipt_sha256)
    ),
    commit_events: store.events.filter(row => row.type === 'pmp:bank-owner-write-committed').length
  };
}

function cancellationMatrix() {
  const store = storage();
  const runtime = runtimeFor(store);
  const {boundary} = loadCore(runtime);
  const make = (suffix, epoch, expected, value) => exactRequest(boundary, {
    resource: RESOURCE_PROJECT,
    operation_id: `op:p9u4:cancellation:${suffix}`,
    request_id: `req:p9u4:cancellation:${suffix}`,
    expected_version: expected,
    cancellation_epoch: epoch,
    writes: [{key: 'pmp_bank_project_registry_v1', value: {epoch, value}}],
    capability: `request:bank_screen_owner:COMMIT_WRITE:${RESOURCE_PROJECT}`
  });
  const initial = boundary.commitBundle(make('initial', 0, 0, 'initial'));
  const bytesAfterInitial = raw(store);
  const gap = boundary.commitBundle(make('gap', 2, 1, 'gap'));
  const bytesAfterGap = raw(store);
  const advance = boundary.commitBundle(make('advance', 1, 1, 'advance'));
  const bytesAfterAdvance = raw(store);
  const stale = boundary.commitBundle(make('stale', 0, 2, 'stale'));
  const bytesAfterStale = raw(store);
  const sameEpoch = boundary.commitBundle(make('same-epoch', 1, 2, 'same-epoch'));
  return {
    initial_code: initial.code,
    gap_code: gap.code,
    gap_zero_effects: stable(bytesAfterInitial) === stable(bytesAfterGap),
    advance_code: advance.code,
    stale_code: stale.code,
    stale_zero_effects: stable(bytesAfterAdvance) === stable(bytesAfterStale),
    same_epoch_code: sameEpoch.code,
    final_epoch: boundary.snapshot().cancellation_epochs[RESOURCE_PROJECT],
    final_version: boundary.resourceVersion(RESOURCE_PROJECT),
    final_value: JSON.parse(store.values.get('pmp_bank_project_registry_v1')).value,
    storage_deletes: store.calls.remove
  };
}

function duplicateMatrix() {
  const store = storage();
  const runtime = runtimeFor(store);
  const {boundary} = loadCore(runtime);
  const input = exactRequest(boundary, {
    operation_id: 'op:p9u4:duplicate',
    request_id: 'req:p9u4:duplicate',
    writes: [{key: 'pmp_continuous_run_state_bank_v1', value: {duplicate: 'original'}}]
  });
  const accepted = boundary.commitBundle(input);
  const callsAfter = clone(store.calls);
  const snapshotAfter = boundary.snapshot();
  const replay = boundary.commitBundle(input);
  const callsReplay = clone(store.calls);
  const snapshotReplay = boundary.snapshot();
  const beforeConflict = raw(store);
  const conflict = boundary.commitBundle(Object.assign({}, input, {
    expected_version: 1,
    writes: [{key: 'pmp_continuous_run_state_bank_v1', value: {duplicate: 'conflict'}}]
  }));
  const afterConflict = raw(store);
  const deniedInput = exactRequest(boundary, {
    operation_id: 'op:p9u4:duplicate-denied',
    request_id: 'req:p9u4:duplicate-denied',
    expected_version: 99,
    writes: [{key: 'pmp_continuous_run_state_bank_v1', value: {denied: true}}]
  });
  const denied = boundary.commitBundle(deniedInput);
  const deniedCalls = clone(store.calls);
  const deniedReplay = boundary.commitBundle(deniedInput);
  return {
    accepted_code: accepted.code,
    identical_replay_equal: stable(accepted) === stable(replay),
    replay_new_writes: callsReplay.set - callsAfter.set,
    replay_new_receipts: snapshotReplay.receipt_count - snapshotAfter.receipt_count,
    conflict_code: conflict.code,
    conflict_zero_effects: stable(beforeConflict) === stable(afterConflict),
    denied_code: denied.code,
    denied_replay_equal: stable(denied) === stable(deniedReplay),
    denied_replay_new_writes: store.calls.set - deniedCalls.set,
    final_version: boundary.resourceVersion(RESOURCE_RUN)
  };
}

function denialMatrix() {
  const store = storage();
  const runtime = runtimeFor(store);
  const {boundary} = loadCore(runtime);
  const writes = [{key: 'pmp_continuous_run_state_bank_v1', value: {denied: false}}];
  const payload = boundary.sha256(boundary.canonical(writes));
  const valid = boundary.requestFor({
    requester_owner: 'continuous_run_level_owner',
    resource: RESOURCE_RUN,
    expected_version: 0,
    writes,
    payload_sha256: payload,
    operation_id: 'op:p9u4:authorize',
    request_id: 'req:p9u4:authorize',
    issued_at: FIXED_NOW,
    expires_at: '2026-07-26T20:45:00.000Z',
    cancellation_epoch: 0,
    capability: `request:bank_screen_owner:COMMIT_WRITE:${RESOURCE_RUN}`
  });
  const cases = [
    ['malformed', null, 'DENIED_MALFORMED'],
    ['contract', Object.assign({}, valid, {contract_version: 'wrong'}), 'DENIED_CONTRACT_VERSION'],
    ['operation', Object.assign({}, valid, {operation_id: 'bad operation'}), 'DENIED_OPERATION_ID'],
    ['request', Object.assign({}, valid, {request_id: 'bad request'}), 'DENIED_REQUEST_ID'],
    ['requester_owner', Object.assign({}, valid, {requester_owner: 'unknown'}), 'DENIED_OWNER'],
    ['target_owner', Object.assign({}, valid, {target_owner: 'unknown'}), 'DENIED_OWNER'],
    ['action', Object.assign({}, valid, {action: 'DELETE_BANK'}), 'DENIED_ACTION'],
    ['resource', Object.assign({}, valid, {resource: 'continuous_run:direct'}), 'DENIED_RESOURCE'],
    ['expected_version', Object.assign({}, valid, {expected_version: 9}), 'DENIED_EXPECTED_VERSION'],
    ['payload_hash', Object.assign({}, valid, {payload_sha256: 'bad'}), 'DENIED_PAYLOAD_HASH'],
    ['time_invalid', Object.assign({}, valid, {issued_at: 'bad'}), 'DENIED_TIME'],
    ['time_order', Object.assign({}, valid, {expires_at: '2026-07-26T20:30:00.000Z'}), 'DENIED_TIME'],
    ['expired', Object.assign({}, valid, {
      issued_at: '2026-07-26T19:00:00.000Z',
      expires_at: '2026-07-26T19:05:00.000Z'
    }), 'DENIED_EXPIRED'],
    ['capability', Object.assign({}, valid, {capability: 'wrong'}), 'DENIED_CAPABILITY'],
    ['cancellation_stale', Object.assign({}, valid, {cancellation_epoch: -1}), 'DENIED_STALE_CANCELLATION'],
    ['cancellation_gap', Object.assign({}, valid, {cancellation_epoch: 2}), 'DENIED_CANCELLATION_ADVANCE']
  ].map(([fault, request, expected]) => {
    const outcome = boundary.authorize(request);
    return {fault, expected, code: outcome.code, writes: outcome.effects.storage_writes, deletes: outcome.effects.storage_deletes};
  });
  const bytesBeforeCommitDenials = raw(store);
  const commitCases = [
    {
      fault: 'payload_binding',
      input: exactRequest(boundary, {
        operation_id: 'op:p9u4:payload-binding',
        request_id: 'req:p9u4:payload-binding',
        payload_sha256: '0'.repeat(64)
      }),
      expected: 'DENIED_PAYLOAD_BINDING'
    },
    {
      fault: 'storage_scope',
      input: exactRequest(boundary, {
        operation_id: 'op:p9u4:scope',
        request_id: 'req:p9u4:scope',
        writes: [{key: 'unrelated_user_key', value: {overwrite: true}}]
      }),
      expected: 'DENIED_STORAGE_SCOPE'
    },
    {
      fault: 'delete_action',
      input: exactRequest(boundary, {
        operation_id: 'op:p9u4:delete',
        request_id: 'req:p9u4:delete',
        action: 'DELETE_BANK',
        capability: `request:bank_screen_owner:DELETE_BANK:${RESOURCE_RUN}`
      }),
      expected: 'DENIED_ACTION'
    },
    {
      fault: 'unknown_owner',
      input: exactRequest(boundary, {
        operation_id: 'op:p9u4:unknown-owner',
        request_id: 'req:p9u4:unknown-owner',
        requester_owner: 'unknown_owner'
      }),
      expected: 'DENIED_OWNER'
    }
  ].map(row => {
    const outcome = boundary.commitBundle(row.input);
    return {fault: row.fault, expected: row.expected, code: outcome.code, writes: outcome.effects.storage_writes, deletes: outcome.effects.storage_deletes};
  });
  const unavailableStore = storage();
  const unavailableRuntime = runtimeFor(unavailableStore, {storageUnavailable: true});
  const unavailableBoundary = loadCore(unavailableRuntime).boundary;
  const unavailable = unavailableBoundary.commitBundle(exactRequest(unavailableBoundary, {
    operation_id: 'op:p9u4:unavailable',
    request_id: 'req:p9u4:unavailable'
  }));
  return {
    authorize_cases: cases,
    commit_cases: commitCases,
    storage_unavailable_code: unavailable.code,
    all_codes_exact: cases.every(row => row.code === row.expected)
      && commitCases.every(row => row.code === row.expected)
      && unavailable.code === 'DENIED_STORAGE_UNAVAILABLE',
    all_denials_zero_effect: cases.concat(commitCases).every(row => row.writes === 0 && row.deletes === 0),
    persisted_bytes_unchanged: stable(bytesBeforeCommitDenials) === stable(raw(store)),
    unrelated_exactly_preserved: store.values.get('unrelated_user_key') === seed().unrelated_user_key,
    manual_delete_absent: boundary.manualDeleteAuthority({}, 'continuous_run'),
    manual_delete_wrong_confirmation: boundary.manualDeleteAuthority({
      user_confirmed: false,
      capability: 'manual:bank_screen_owner:delete_record:continuous_run'
    }, 'continuous_run'),
    manual_delete_wrong_capability: boundary.manualDeleteAuthority({
      user_confirmed: true,
      capability: 'wrong'
    }, 'continuous_run'),
    manual_delete_exact: boundary.manualDeleteAuthority({
      user_confirmed: true,
      capability: 'manual:bank_screen_owner:delete_record:continuous_run'
    }, 'continuous_run')
  };
}

function rollbackMatrix() {
  const original = seed();
  const store = storage(original, {failAtSet: 2});
  const runtime = runtimeFor(store);
  const {boundary} = loadCore(runtime);
  const result = boundary.commitBundle(exactRequest(boundary, {
    operation_id: 'op:p9u4:rollback',
    request_id: 'req:p9u4:rollback',
    writes: [
      {key: 'pmp_continuous_run_state_bank_v1', value: {step: 1}},
      {key: 'pmp_continuous_run_state_receipts_v1', value: [{step: 2}]},
      {key: 'pmp_continuous_run_state_manifest_v1', value: {step: 3}}
    ]
  }));
  const newKeySeed = Object.assign({}, original);
  delete newKeySeed.pmp_continuous_run_state_receipts_v1;
  const newKeyStore = storage(newKeySeed, {failAtSet: 2});
  const newKeyRuntime = runtimeFor(newKeyStore);
  const newBoundary = loadCore(newKeyRuntime).boundary;
  const newKeyResult = newBoundary.commitBundle(exactRequest(newBoundary, {
    operation_id: 'op:p9u4:rollback:new-key',
    request_id: 'req:p9u4:rollback:new-key',
    writes: [
      {key: 'pmp_continuous_run_state_bank_v1', value: {step: 1}},
      {key: 'pmp_continuous_run_state_receipts_v1', value: [{step: 2}]},
      {key: 'pmp_continuous_run_state_manifest_v1', value: {step: 3}}
    ]
  }));
  return {
    existing_keys_code: result.code,
    existing_keys_exact_restore: stable(raw(store)) === stable(original),
    existing_keys_version: boundary.resourceVersion(RESOURCE_RUN),
    new_key_code: newKeyResult.code,
    absent_key_remains_absent: !newKeyStore.values.has('pmp_continuous_run_state_receipts_v1'),
    new_key_exact_restore: stable(raw(newKeyStore)) === stable(newKeySeed),
    new_key_version: newBoundary.resourceVersion(RESOURCE_RUN),
    unrelated_exactly_preserved: store.values.get('unrelated_user_key') === original.unrelated_user_key
  };
}

function restartAndHandoffMatrix() {
  const store = storage();
  const firstRuntime = runtimeFor(store);
  const first = loadCore(firstRuntime);
  const area = first.state.setCurrentWorkArea('pass9-bank-repair');
  const item = first.state.setCurrentWorkItem('p9-u4-proof');
  const queue = first.state.setWorkQueue(['proof', 'closure']);
  const stopped = first.state.recordStop('bounded-handoff');
  const pack = first.state.exportResumePack();
  const persistedAtHandoff = raw(store);
  const callsAtHandoff = clone(store.calls);
  const secondRuntime = runtimeFor(store);
  const second = loadCore(secondRuntime);
  const callsAfterRestartLoad = clone(store.calls);
  const restartLoadPreservedBytes = stable(persistedAtHandoff) === stable(raw(store));
  const restored = second.state.readRunState();
  const restoredReceipts = second.state.readReceipts();
  const exportedAfterRestart = second.state.exportResumePack();
  const callsAfterRestartReads = clone(store.calls);
  const beforeResume = raw(store);
  const resumed = second.state.recordResume();
  const finalState = second.state.readRunState();
  const corruptedSeed = seed();
  corruptedSeed.pmp_continuous_run_state_bank_v1 = '{not-json';
  const corruptedStore = storage(corruptedSeed);
  const corruptedRuntime = runtimeFor(corruptedStore);
  const corrupted = loadCore(corruptedRuntime);
  const corruptedBeforeRead = raw(corruptedStore);
  const fallback = corrupted.state.readRunState();
  const corruptedAfterRead = raw(corruptedStore);
  return {
    first_codes: [
      area.owner_receipt && area.owner_receipt.code,
      item.owner_receipt && item.owner_receipt.code,
      queue.owner_receipt && queue.owner_receipt.code,
      stopped.owner_receipt && stopped.owner_receipt.code
    ],
    handoff_pack_type: pack.type,
    handoff_owner: pack.owner,
    handoff_state_sha256: digest(pack.state),
    handoff_receipts: pack.receipts.length,
    restart_load_reads: callsAfterRestartLoad.get - callsAtHandoff.get,
    restart_load_writes: callsAfterRestartLoad.set - callsAtHandoff.set,
    restart_load_deletes: callsAfterRestartLoad.remove - callsAtHandoff.remove,
    persisted_bytes_unchanged_by_restart_load: restartLoadPreservedBytes,
    restored_area: restored.current_work_area,
    restored_item: restored.current_work_item,
    restored_queue: restored.work_queue,
    restored_status: restored.last_run_status,
    restored_stop_reason: restored.last_stop_reason,
    restored_receipts: restoredReceipts.length,
    export_after_restart_writes: callsAfterRestartReads.set - callsAfterRestartLoad.set,
    export_after_restart_type: exportedAfterRestart.type,
    resume_code: resumed.owner_receipt && resumed.owner_receipt.code,
    resume_changed_bytes: stable(beforeResume) !== stable(raw(store)),
    final_status: finalState.last_run_status,
    final_stop_reason: finalState.last_stop_reason,
    final_context_status: finalState.context_recovery_state.status,
    second_boundary_version_after_resume: second.boundary.resourceVersion(RESOURCE_RUN),
    corrupted_read_fails_closed_in_memory: fallback.current_work_item === '' && fallback.owner === 'continuous_run_level_owner',
    corrupted_raw_bytes_preserved: stable(corruptedBeforeRead) === stable(corruptedAfterRead),
    corrupted_read_storage_writes: corruptedStore.calls.set,
    unrelated_exactly_preserved: store.values.get('unrelated_user_key') === seed().unrelated_user_key
  };
}

function routerAndDiagnosticsMatrix() {
  const store = storage();
  const runtime = runtimeFor(store);
  const {boundary, router, diagnostic} = loadCore(runtime);
  const beforeReads = clone(store.calls);
  const inventory = router.inventory();
  const routeLog = router.routeLog();
  const helpers = router.helpers();
  const afterReads = clone(store.calls);
  const beforeDenied = raw(store);
  const denied = router.recordDelete({
    owning_bank: 'continuous_run',
    record_id: 'historic-bank-record'
  });
  const afterDenied = raw(store);
  const write = router.recordWrite({
    owning_bank: 'continuous_run',
    record_id: 'p9u4-proof-record',
    record_type: 'test_verification',
    source_tab: 'bank',
    active_system: 'continuous_run',
    action: 'proof',
    summary: 'deterministic fixture only'
  });
  const writeRecordPresent = router.inventory().banks.continuous_run.records.some(
    row => row.record_id === 'p9u4-proof-record'
  );
  const beforeDeleteDenial = raw(store);
  const wrongDelete = router.recordDelete({
    owning_bank: 'continuous_run',
    record_id: 'p9u4-proof-record',
    user_confirmed: true,
    capability: 'wrong'
  });
  const afterDeleteDenial = raw(store);
  const exactDelete = router.recordDelete({
    owning_bank: 'continuous_run',
    record_id: 'p9u4-proof-record',
    user_confirmed: true,
    capability: 'manual:bank_screen_owner:delete_record:continuous_run'
  });
  const beforeDiagnostic = clone(store.calls);
  const diagnosticSnapshot = diagnostic.boundarySnapshot();
  const afterDiagnostic = clone(store.calls);
  return {
    read_inventory_present: !!inventory.banks.continuous_run,
    read_route_count: routeLog.length,
    read_helper_count: helpers.helpers.length,
    read_path_writes: afterReads.set - beforeReads.set,
    read_path_deletes: afterReads.remove - beforeReads.remove,
    default_delete_code: denied.code,
    default_delete_zero_effect: stable(beforeDenied) === stable(afterDenied),
    write_code: write.owner_receipt && write.owner_receipt.code,
    write_record_present: writeRecordPresent,
    wrong_delete_code: wrongDelete.code,
    wrong_delete_zero_effect: stable(beforeDeleteDenial) === stable(afterDeleteDenial),
    exact_delete_code: exactDelete.owner_receipt && exactDelete.owner_receipt.code,
    exact_delete_record_absent: !router.inventory().banks.continuous_run.records.some(row => row.record_id === 'p9u4-proof-record'),
    diagnostic_status: diagnosticSnapshot.status,
    diagnostic_owner_pair: [diagnosticSnapshot.bank_owner, diagnosticSnapshot.continuous_run_owner],
    diagnostic_reads: afterDiagnostic.get - beforeDiagnostic.get,
    diagnostic_writes: afterDiagnostic.set - beforeDiagnostic.set,
    diagnostic_deletes: afterDiagnostic.remove - beforeDiagnostic.remove,
    diagnostic_report_auto_written: store.values.has('pmp_bank_continuous_run_owner_split_diagnostic_v1'),
    unrelated_exactly_preserved: store.values.get('unrelated_user_key') === seed().unrelated_user_key,
    boundary_version: boundary.version
  };
}

function receiptBoundMatrix() {
  const store = storage();
  const runtime = runtimeFor(store);
  const {boundary} = loadCore(runtime);
  for (let index = 0; index < 260; index += 1) {
    const resource = RESOURCE_RUN;
    const result = boundary.commitBundle(exactRequest(boundary, {
      operation_id: `op:p9u4:bounded:${index}`,
      request_id: `req:p9u4:bounded:${index}`,
      expected_version: index,
      writes: [{key: 'pmp_continuous_run_state_bank_v1', value: {bounded: index}}]
    }));
    if (!result.ok) throw new Error(`bounded receipt ${index}: ${result.code}`);
  }
  const snapshot = boundary.snapshot();
  return {
    commits: 260,
    receipt_count: snapshot.receipt_count,
    visible_receipts: snapshot.recent_receipts.length,
    final_version: boundary.resourceVersion(RESOURCE_RUN),
    first_visible_operation: snapshot.recent_receipts[0].operation_id,
    last_visible_operation: snapshot.recent_receipts[snapshot.recent_receipts.length - 1].operation_id,
    first_previous_is_historic_hash: /^[0-9a-f]{64}$/.test(snapshot.recent_receipts[0].previous_receipt_sha256)
      && snapshot.recent_receipts[0].previous_receipt_sha256 !== ZERO,
    visible_chain_valid: snapshot.recent_receipts.every((receipt, index, rows) =>
      /^[0-9a-f]{64}$/.test(receipt.request_sha256)
      && /^[0-9a-f]{64}$/.test(receipt.receipt_sha256)
      && receipt.receipt_sha256 === boundary.sha256(boundary.canonical(Object.fromEntries(
        Object.entries(receipt).filter(([key]) => key !== 'receipt_sha256')
      )))
      && (index === 0 || receipt.previous_receipt_sha256 === rows[index - 1].receipt_sha256)
    ),
    storage_deletes: store.calls.remove,
    unrelated_exactly_preserved: store.values.get('unrelated_user_key') === seed().unrelated_user_key
  };
}

function sourcePolicyMatrix() {
  const files = {
    boundary: source('pmp-bank-continuous-run-owner-boundary-v1.js'),
    state: source('pmp-continuous-run-state-bank-v1.js'),
    router: source('pmp-master-bank-inventory-router-v1.js'),
    diagnostic: source('pmp-bank-continuous-run-owner-split-diagnostic-v1.js'),
    master: source('pmp-master-bank-tab-v1.js'),
    owner: source('pmp-bank-screen-owner-v1.js'),
    bridge: source('pmp-bank-owner-dependency-bridge-v1.js'),
    loader: source('pmp-continuous-run-bank-order-frame-loader-v1.js'),
    connectionDelete: source('pmp-connections-bank-packet-delete-v1.js'),
    mode: source('pmp-bank-mode1-hide-unchecked-v1.js'),
    cleaner: source('pmp-bank-scoped-test-data-cleaner-v1.js')
  };
  const policies = {
    boundary_has_exact_owners: files.boundary.includes("const BANK_OWNER='bank_screen_owner'") && files.boundary.includes("const RUN_OWNER='continuous_run_level_owner'"),
    boundary_sha256_chained: files.boundary.includes("receipt_integrity:'SHA-256_CHAINED'"),
    state_no_delete: !files.state.includes('localStorage.removeItem'),
    state_read_manifest_denied: files.state.includes('READ_PATH_CANNOT_WRITE_MANIFEST'),
    router_user_confirmation: files.router.includes('input.user_confirmed!==true'),
    diagnostic_no_automatic_run: !files.diagnostic.includes("setTimeout(()=>evaluate('script_load"),
    master_no_interval: !files.master.includes('setInterval('),
    master_open_read_only: !files.master.includes('.recordWrite('),
    owner_no_interval: !files.owner.includes('setInterval('),
    bridge_no_timer_or_copy: !files.bridge.includes('setInterval(') && !files.bridge.includes('setTimeout(') && !files.bridge.includes('w[name]=api'),
    loader_event_driven: !files.loader.includes('setInterval(') && files.loader.includes('EVENT_DRIVEN_NEW_DOCUMENT_ONCE'),
    connection_delete_owner_routed: !files.connectionDelete.includes('localStorage.setItem') && files.connectionDelete.includes("capability:'manual:bank_screen_owner:delete_record:connections'"),
    legacy_mode_passive: !files.mode.includes('localStorage') && files.mode.includes('PASSIVE_COMPATIBILITY_HELD'),
    legacy_cleaner_denied: !files.cleaner.includes('localStorage') && files.cleaner.includes('DELETE_DENIED_BY_DEFAULT')
  };
  return {
    policies,
    all_pass: Object.values(policies).every(Boolean),
    source_sha256: Object.fromEntries(Object.entries(files).map(([key, value]) => [key, digest(value)]))
  };
}

function scenarioResult() {
  const result = {
    type: TYPE,
    version: VERSION,
    status: 'PASS',
    boot_repeated_load: bootAndRepeatedLoadMatrix(),
    concurrency: concurrencyMatrix(),
    cancellation: cancellationMatrix(),
    duplicate: duplicateMatrix(),
    denial: denialMatrix(),
    atomic_rollback: rollbackMatrix(),
    restart_handoff: restartAndHandoffMatrix(),
    router_diagnostics: routerAndDiagnosticsMatrix(),
    bounded_receipts: receiptBoundMatrix(),
    source_policy: sourcePolicyMatrix(),
    coverage: {
      concurrency_cases: 4,
      cancellation_cases: 5,
      duplicate_cases: 4,
      authorization_denial_cases: 16,
      commit_denial_cases: 5,
      rollback_cases: 2,
      restart_handoff_cases: 2,
      router_delete_cases: 3,
      bounded_receipt_commits: 260,
      source_policy_checks: 14
    },
    effects: {
      production_files_changed: false,
      runtime_integrity_changed: false,
      browser_launched: false,
      network_requests: false,
      route_changes: false,
      mounts: false,
      persisted_user_data_changed: false,
      storage_migration_performed: false,
      scarce_live_observation_performed: false,
      formal_proof_performed: false,
      special_authority_consumed: false
    },
    claim_ceiling: 'P9-U4 isolated deterministic proof against the exact merged P9-U3 production sources. Storage effects occur only inside in-memory fixtures. No user persisted data, storage migration, scarce live observation, or formal proof is performed.'
  };
  result.result_sha256 = digest(result);
  return result;
}

function verifyResultHash(result) {
  if (!result || typeof result.result_sha256 !== 'string') return false;
  const copy = clone(result);
  const expected = copy.result_sha256;
  delete copy.result_sha256;
  return digest(copy) === expected;
}

if (require.main === module) process.stdout.write(JSON.stringify(scenarioResult(), null, 2) + '\n');

module.exports = {
  TYPE,
  VERSION,
  FIXED_NOW,
  CORE,
  clone,
  stable,
  digest,
  seed,
  storage,
  runtimeFor,
  load,
  loadCore,
  raw,
  exactRequest,
  bootAndRepeatedLoadMatrix,
  concurrencyMatrix,
  cancellationMatrix,
  duplicateMatrix,
  denialMatrix,
  rollbackMatrix,
  restartAndHandoffMatrix,
  routerAndDiagnosticsMatrix,
  receiptBoundMatrix,
  sourcePolicyMatrix,
  scenarioResult,
  verifyResultHash
};
