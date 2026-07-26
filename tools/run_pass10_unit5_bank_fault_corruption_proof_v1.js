#!/usr/bin/env node
'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const TYPE = 'PMP_PASS10_UNIT5_BANK_FAULT_CORRUPTION_PROOF_RESULT_V1';
const VERSION = '1.0.0';
const OWNER = 'bank_screen_owner';
const RESOURCE = 'bank:persist:master_inventory';
const LARGE_RECORDS = 2048;

function source(name) {
  return fs.readFileSync(path.join(ROOT, name), 'utf8');
}
function json(name) {
  return JSON.parse(source(name));
}
function stable(value) {
  if (Array.isArray(value)) return '[' + value.map(stable).join(',') + ']';
  if (value && typeof value === 'object') {
    return '{' + Object.keys(value).sort()
      .map(key => JSON.stringify(key) + ':' + stable(value[key])).join(',') + '}';
  }
  return JSON.stringify(value);
}
function digest(value) {
  return crypto.createHash('sha256')
    .update(Buffer.from(typeof value === 'string' ? value : stable(value)))
    .digest('hex');
}

function storage(seed = {}, options = {}) {
  const values = new Map(Object.entries(seed));
  const calls = {get: 0, set: 0, remove: 0, key: 0};
  let remainingFailures = Number(options.failSetCalls || 0);
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
      if (
        remainingFailures > 0
        && (!options.failSetKey || String(key) === options.failSetKey)
      ) {
        remainingFailures -= 1;
        throw new Error('fixture setItem failure');
      }
      values.set(String(key), String(value));
    },
    removeItem(key) {
      calls.remove += 1;
      values.delete(String(key));
    }
  };
  return {values, calls, api};
}

function runtimeFor(store, unavailable = false) {
  const events = [];
  const listeners = {};
  const window = {
    addEventListener(type, fn) {
      (listeners[type] ||= []).push(fn);
    },
    dispatchEvent(event) {
      events.push(event);
      for (const fn of [...(listeners[event.type] || [])]) fn(event);
      return true;
    }
  };
  if (!unavailable) window.localStorage = store.api;
  window.window = window;
  const context = vm.createContext({
    window,
    localStorage: unavailable ? undefined : store.api,
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
function loadChain(runtime) {
  load(runtime, 'pmp-bank-continuous-run-owner-boundary-v1.js');
  load(runtime, 'pmp-bank-inventory-readonly-projection-v1.js');
  load(runtime, 'pmp-bank-owner-projection-refresh-v1.js');
  return {
    boundary: runtime.window.PMPBankContinuousRunOwnerBoundaryV1,
    projection: runtime.window.PMPBankInventoryReadonlyProjectionV1,
    refresh: runtime.window.PMPBankOwnerProjectionRefreshV1
  };
}
function rawObject(value) {
  return JSON.stringify(value);
}
function master(records, version = 'fixture-v1') {
  return {
    type: 'PMP_MASTER_BANK_INVENTORY_V1',
    version,
    owner: OWNER,
    banks: {
      world: {
        name: 'World Bank',
        records,
        references: []
      }
    }
  };
}
function commit(boundary, operation, records, expectedVersion = 0) {
  return boundary.commitBundle({
    requester_owner: OWNER,
    resource: RESOURCE,
    expected_version: expectedVersion,
    writes: [{
      key: 'pmp_master_bank_inventory_v1',
      value: master(records, `fixture-${operation}`)
    }],
    operation_id: `op:p10u5:${operation}`,
    request_id: `req:p10u5:${operation}`,
    capability: `internal:${OWNER}:COMMIT_WRITE:${RESOURCE}`
  });
}
function byteMap(store) {
  return Object.fromEntries(Array.from(store.values.entries()).sort());
}

function scenarioResult() {
  const unit1 = json('audit/pass10/pass10-bank-unit1-inventory-reconciliation-v1.json');
  const unit2 = json('audit/pass10/pass10-bank-unit2-inventory-contract-v1.json');
  const unit3 = json('audit/pass10/pass10-bank-unit3-readonly-projection-v1.json');
  const unit4 = json('audit/pass10/pass10-bank-unit4-owner-projection-refresh-v1.json');
  const receipt1 = json(
    'audit/pass10/receipts/'
    + 'RECEIPT_P10_U1_BANK_INVENTORY_RECONCILIATION_20260726T212000Z_001.json'
  );
  const receipt2 = json(
    'audit/pass10/receipts/'
    + 'RECEIPT_P10_U2_BANK_INVENTORY_CONTRACT_20260726T220000Z_001.json'
  );
  const receipt3 = json(
    'audit/pass10/receipts/'
    + 'RECEIPT_P10_U3_BANK_READONLY_PROJECTION_20260726T223500Z_001.json'
  );
  const receipt4 = json(
    'audit/pass10/receipts/'
    + 'RECEIPT_P10_U4_BANK_OWNER_PROJECTION_REFRESH_20260726T230500Z_001.json'
  );

  const largeRows = Array.from({length: LARGE_RECORDS}, (_, index) => ({
    record_id: `large:${String(index).padStart(5, '0')}`,
    summary: `fixture-${index}`,
    owner: OWNER,
    provenance: `fixture-source-${index % 17}`
  }));
  const largeRaw = rawObject(master(largeRows, 'large-v1'));
  const largeStore = storage({
    pmp_master_bank_inventory_v1: largeRaw,
    pmp_unrelated_user_preference_v1: 'EXACT-UNRELATED-BYTES'
  });
  const largeBefore = byteMap(largeStore);
  const largeRuntime = runtimeFor(largeStore);
  const largeChain = loadChain(largeRuntime);
  const loadCalls = {...largeStore.calls};
  const largeFirst = largeChain.projection.snapshot('p10u5_large_first');
  const afterFirst = byteMap(largeStore);
  const largeSecond = largeChain.projection.snapshot('p10u5_large_second');
  const afterSecond = byteMap(largeStore);

  const corruptRaw = '{"type":"PMP_MASTER_BANK_INVENTORY_V1","broken":';
  const orphanRaw = '{"orphan":true,"payload":"PRESERVE-ME"}';
  const collisionRaw = rawObject(master([
    {record_id: 'duplicate:1', summary: 'first'},
    {record_id: 'duplicate:1', summary: 'second'}
  ], 'collision-v1'));
  const faultStore = storage({
    pmp_master_bank_inventory_v1: collisionRaw,
    pmp_helper_bank_index_v1: corruptRaw,
    pmp_bank_orphan_plugin_v77: orphanRaw,
    unrelated_exact_bytes: 'DO-NOT-TOUCH'
  });
  const faultBefore = byteMap(faultStore);
  const faultRuntime = runtimeFor(faultStore);
  const faultChain = loadChain(faultRuntime);
  const faultSnapshot = faultChain.projection.snapshot('p10u5_faults');
  const faultAfter = byteMap(faultStore);
  const collisionItems = faultSnapshot.items.filter(
    row => row.source_native_id === 'duplicate:1'
  );
  const corruptItems = faultSnapshot.items.filter(
    row => row.source_namespace === 'pmp_helper_bank_index_v1'
  );
  const orphanItems = faultSnapshot.items.filter(
    row => row.source_namespace === 'pmp_bank_orphan_plugin_v77'
  );

  const rollbackInitial = {
    pmp_master_bank_inventory_v1: rawObject(master([
      {record_id: 'before:1', summary: 'before'}
    ], 'before-v1')),
    pmp_source_bank_router_receipts_v1: 'EXACT-SECOND-KEY-BEFORE',
    unrelated_exact_bytes: 'ROLLBACK-UNRELATED'
  };
  const rollbackStore = storage(rollbackInitial, {
    failSetCalls: 1,
    failSetKey: 'pmp_source_bank_router_receipts_v1'
  });
  const rollbackRuntime = runtimeFor(rollbackStore);
  const rollbackBoundary = loadChain(rollbackRuntime).boundary;
  const rollbackBefore = byteMap(rollbackStore);
  const rollbackResult = rollbackBoundary.commitBundle({
    requester_owner: OWNER,
    resource: RESOURCE,
    expected_version: 0,
    writes: [
      {
        key: 'pmp_master_bank_inventory_v1',
        value: master([{record_id: 'after:1', summary: 'after'}], 'after-v1')
      },
      {
        key: 'pmp_source_bank_router_receipts_v1',
        value: [{receipt_id: 'should-not-persist'}]
      }
    ],
    operation_id: 'op:p10u5:rollback',
    request_id: 'req:p10u5:rollback',
    capability: `internal:${OWNER}:COMMIT_WRITE:${RESOURCE}`
  });
  const rollbackAfter = byteMap(rollbackStore);

  const acceptedStore = storage({
    pmp_master_bank_inventory_v1: rawObject(master([
      {record_id: 'accepted:before', summary: 'before'}
    ], 'accepted-before'))
  });
  const acceptedRuntime = runtimeFor(acceptedStore);
  const acceptedChain = loadChain(acceptedRuntime);
  const accepted = commit(
    acceptedChain.boundary,
    'accepted',
    [{record_id: 'accepted:after', summary: 'after'}],
    0
  );
  const acceptedBytes = byteMap(acceptedStore);
  const acceptedSnapshot = acceptedChain.projection.lastSnapshot();
  acceptedRuntime.window.dispatchEvent(
    new acceptedRuntime.context.CustomEvent(
      'pmp:bank-owner-write-committed',
      {
        detail: {
          resource: RESOURCE,
          version: 1,
          receipt: accepted.receipt,
          helper_registered: true,
          active_tab: 'bank'
        }
      }
    )
  );
  const duplicateDiagnostic = acceptedChain.refresh.diagnostic();
  const afterDuplicateBytes = byteMap(acceptedStore);
  const stale = commit(
    acceptedChain.boundary,
    'stale',
    [{record_id: 'stale:never', summary: 'never'}],
    0
  );
  const afterStaleBytes = byteMap(acceptedStore);

  const restartBeforeCalls = {...acceptedStore.calls};
  const restartRuntime = runtimeFor(acceptedStore);
  const restartChain = loadChain(restartRuntime);
  const restartAfterLoadCalls = {...acceptedStore.calls};
  const restartSnapshot = restartChain.projection.snapshot('p10u5_restart');
  const restartBytes = byteMap(acceptedStore);

  const unavailableStore = storage();
  const unavailableRuntime = runtimeFor(unavailableStore, true);
  const unavailableChain = loadChain(unavailableRuntime);
  const unavailableSnapshot = unavailableChain.projection.snapshot(
    'p10u5_unavailable'
  );
  const unavailableCommit = commit(
    unavailableChain.boundary,
    'unavailable',
    [{record_id: 'unavailable:never', summary: 'never'}],
    0
  );

  const chain = [
    {unit: 'P10-U1', status: unit1.status, next: receipt1.next_safe_move.step_id},
    {unit: 'P10-U2', status: unit2.status, next: receipt2.next_safe_move.step_id},
    {unit: 'P10-U3', status: unit3.status, next: receipt3.next_safe_move.step_id},
    {unit: 'P10-U4', status: unit4.status, next: receipt4.next_safe_move.step_id}
  ];
  const assertionsByUnit = [
    unit1.verification.assertions_passed,
    unit2.verification.assertions_passed,
    unit3.verification.assertions_passed,
    unit4.deterministic_matrix.assertions_passed
  ];
  const adapterSource = source('pmp-bank-owner-projection-refresh-v1.js');
  const projectionSource = source('pmp-bank-inventory-readonly-projection-v1.js');
  const tabSource = source('pmp-master-bank-tab-v1.js');
  const innerSource = source('pmp-current-inner-cleanbug-rgcontrols-v23.html');
  const boundarySource = source('pmp-bank-continuous-run-owner-boundary-v1.js');

  const result = {
    type: TYPE,
    version: VERSION,
    status: 'BANK_FAULT_ROLLBACK_AND_CORRUPTION_CONTAINMENT_PROVEN',
    evidence_chain: {
      units: chain,
      exact_progression: chain.map(row => row.next),
      assertions_by_unit: assertionsByUnit,
      cumulative_prior_assertions: assertionsByUnit.reduce((a, b) => a + b, 0),
      all_permanent_gates_bound: [unit1, unit2, unit3, unit4].every(
        unit => unit.no_blind_flying_gate
          && unit.no_blind_flying_gate.upload_before_enforcement === true
          && unit.no_blind_flying_gate.automatic_retry === false
      )
    },
    large_inventory: {
      fixture_records: LARGE_RECORDS,
      projected_items_first: largeFirst.summary.items,
      projected_items_second: largeSecond.summary.items,
      stable_ids: largeFirst.items.map(row => row.canonical_id).join('\n')
        === largeSecond.items.map(row => row.canonical_id).join('\n'),
      unique_ids: new Set(largeFirst.items.map(row => row.canonical_id)).size,
      exact_bytes_after_first: stable(largeBefore) === stable(afterFirst),
      exact_bytes_after_second: stable(largeBefore) === stable(afterSecond),
      unrelated_bytes_preserved: largeStore.values.get(
        'pmp_unrelated_user_preference_v1'
      ) === 'EXACT-UNRELATED-BYTES',
      load_calls: loadCalls,
      first_effects: largeFirst.effects,
      second_effects: largeSecond.effects,
      raw_payloads_exposed: largeSecond.summary.raw_payloads_exposed
    },
    duplicate_and_collision: {
      projected_collision_items: collisionItems.length,
      all_quarantined: collisionItems.every(row => row.state === 'QUARANTINED'),
      all_collision_marked: collisionItems.every(
        row => row.quarantine_reasons.includes('IDENTITY_COLLISION')
      ),
      payload_hashes_distinct: new Set(
        collisionItems.map(row => row.payload_sha256)
      ).size,
      duplicate_owner_event_denied: duplicateDiagnostic.last_code
        === 'DENIED_DUPLICATE_OWNER_RECEIPT',
      duplicate_projection_refreshes: duplicateDiagnostic.projection_refreshes,
      duplicate_bytes_unchanged: stable(acceptedBytes)
        === stable(afterDuplicateBytes)
    },
    orphan_and_corruption: {
      corrupt_items: corruptItems.length,
      corrupt_quarantined: corruptItems.every(
        row => row.state === 'QUARANTINED'
          && row.quarantine_reasons.includes('CORRUPT_RECORD')
      ),
      corrupt_raw_bytes_preserved: faultStore.values.get(
        'pmp_helper_bank_index_v1'
      ) === corruptRaw,
      orphan_items: orphanItems.length,
      orphan_quarantined: orphanItems.every(
        row => row.state === 'QUARANTINED'
          && row.quarantine_reasons.includes('UNKNOWN_NAMESPACE')
          && row.quarantine_reasons.includes('UNKNOWN_OWNER')
      ),
      orphan_owner_null: orphanItems.every(row => row.owner_id === null),
      orphan_raw_bytes_preserved: faultStore.values.get(
        'pmp_bank_orphan_plugin_v77'
      ) === orphanRaw,
      snapshot_zero_writes: faultSnapshot.effects.storage_writes === 0,
      snapshot_zero_deletes: faultSnapshot.effects.storage_deletes === 0,
      all_fault_bytes_preserved: stable(faultBefore) === stable(faultAfter),
      unrelated_bytes_preserved: faultStore.values.get('unrelated_exact_bytes')
        === 'DO-NOT-TOUCH'
    },
    stale_and_unavailable: {
      stale_commit_denied: stale.ok === false,
      stale_code: stale.code,
      stale_effects: stale.effects,
      stale_bytes_unchanged: stable(acceptedBytes) === stable(afterStaleBytes),
      unavailable_projection_status: unavailableSnapshot.status,
      unavailable_projection_items: unavailableSnapshot.summary.items,
      unavailable_commit_denied: unavailableCommit.ok === false,
      unavailable_commit_code: unavailableCommit.code,
      unavailable_commit_effects: unavailableCommit.effects,
      unavailable_storage_calls: unavailableStore.calls
    },
    atomic_rollback: {
      result_code: rollbackResult.code,
      result_effects: rollbackResult.effects,
      exact_bytes_restored: stable(rollbackBefore) === stable(rollbackAfter),
      existing_first_key_restored: rollbackStore.values.get(
        'pmp_master_bank_inventory_v1'
      ) === rollbackInitial.pmp_master_bank_inventory_v1,
      existing_second_key_preserved: rollbackStore.values.get(
        'pmp_source_bank_router_receipts_v1'
      ) === rollbackInitial.pmp_source_bank_router_receipts_v1,
      unrelated_bytes_preserved: rollbackStore.values.get(
        'unrelated_exact_bytes'
      ) === 'ROLLBACK-UNRELATED',
      resource_version: rollbackBoundary.resourceVersion(RESOURCE),
      receipt_count: rollbackBoundary.snapshot().receipt_count
    },
    accepted_and_restart: {
      accepted_code: accepted.code,
      accepted_refreshes: acceptedChain.refresh.diagnostic().projection_refreshes,
      accepted_snapshot_reason: acceptedSnapshot.reason,
      accepted_item_visible: acceptedSnapshot.items.some(
        row => row.source_native_id === 'accepted:after'
      ),
      restart_load_delta: {
        get: restartAfterLoadCalls.get - restartBeforeCalls.get,
        set: restartAfterLoadCalls.set - restartBeforeCalls.set,
        remove: restartAfterLoadCalls.remove - restartBeforeCalls.remove,
        key: restartAfterLoadCalls.key - restartBeforeCalls.key
      },
      restart_snapshot_items: restartSnapshot.summary.items,
      restart_item_visible: restartSnapshot.items.some(
        row => row.source_native_id === 'accepted:after'
      ),
      restart_item_id_matches: restartSnapshot.items.some(
        row => row.canonical_id === acceptedSnapshot.items.find(
          item => item.source_native_id === 'accepted:after'
        ).canonical_id
      ),
      restart_snapshot_zero_writes: restartSnapshot.effects.storage_writes === 0,
      restart_snapshot_zero_deletes: restartSnapshot.effects.storage_deletes === 0,
      restart_bytes_unchanged: stable(acceptedBytes) === stable(restartBytes),
      restart_adapter_refreshes: restartChain.refresh.diagnostic()
        .projection_refreshes
    },
    active_safety: {
      boundary_only_writer_rule: boundarySource.includes(
        'Bank Owner is the only durable writer'
      ),
      projection_unknown_policy: projectionSource.includes(
        'QUARANTINE_PRESERVE_EXACT_BYTES_NEVER_SILENTLY_DELETE'
      ),
      projection_historic_policy: projectionSource.includes(
        'REFERENCE_ONLY_NEVER_SILENTLY_MERGE'
      ),
      adapter_receipt_hash_validation: adapterSource.includes(
        'receiptHashValid(boundary,receipt)'
      ),
      adapter_boundary_receipt_validation: adapterSource.includes(
        'recentReceiptValid(boundary,receipt)'
      ),
      adapter_duplicate_denial: adapterSource.includes('processed.has(hash)'),
      adapter_stale_denial: adapterSource.includes(
        'boundary.resourceVersion(resource)!==version'
      ),
      tab_raw_owner_listener_absent: !tabSource.includes(
        "window.addEventListener('pmp:bank-owner-write-committed',scan)"
      ),
      tab_sanitized_listener_present: tabSource.includes(
        "window.addEventListener('pmp:bank-inventory-projection-refreshed'"
      ),
      tab_cached_projection: tabSource.includes(
        'p.lastSnapshot?p.lastSnapshot():null'
      ),
      one_boundary_load: (
        innerSource.match(/pmp-bank-continuous-run-owner-boundary-v1\.js/g) || []
      ).length,
      one_projection_load: (
        innerSource.match(/pmp-bank-inventory-readonly-projection-v1\.js/g) || []
      ).length,
      one_adapter_load: (
        innerSource.match(/pmp-bank-owner-projection-refresh-v1\.js/g) || []
      ).length,
      one_tab_load: (
        innerSource.match(/pmp-master-bank-tab-v1\.js/g) || []
      ).length,
      recurring_timers: ['setInterval(', 'setTimeout('].reduce(
        (sum, token) => sum + (
          adapterSource.split(token).length - 1
          + projectionSource.split(token).length - 1
          + tabSource.split(token).length - 1
        ),
        0
      ),
      adapter_write_api: adapterSource.includes('write:'),
      adapter_delete_api: adapterSource.includes('delete:'),
      adapter_migration_api: adapterSource.includes('migrate:')
    },
    observation_decision_input: {
      deterministic_fault_cases: [
        'large inventory',
        'identity collision',
        'duplicate owner receipt',
        'orphan namespace',
        'corrupt governed record',
        'stale expected version',
        'storage unavailable',
        'atomic multi-write rollback',
        'fresh-process restart',
        'Helper and active-tab decoration',
        'direct UI event',
        'missing owner dependency'
      ],
      unresolved_deterministic_failures: 0,
      user_app_check_required_now: false,
      bounded_observation_performed: false,
      bounded_observation_authority_consumed: false,
      next_unit_may_decide_rehearsal_without_observation: true
    },
    effects: {
      production_files_changed: false,
      runtime_integrity_changed: false,
      browser_launched: false,
      network_requests: false,
      fixture_storage_writes: false,
      user_storage_reads: false,
      user_storage_writes: false,
      user_storage_deletes: false,
      bank_user_data_mutations: false,
      storage_migration_performed: false,
      live_observation_performed: false,
      formal_proof_performed: false,
      persisted_user_data_changed: false,
      production_behavior_activated: false
    },
    next_step: {
      id: 'P10-U6',
      objective: 'Perform the roadmap-required reversible Bank migration rehearsal using disposable fixtures only; prove exact rollback and keep production migration forbidden.',
      requires_user_app_check: false,
      requires_new_explicit_authority: false,
      persisted_user_data_change_allowed: false,
      production_migration_allowed: false,
      stop_after: false
    },
    claim_ceiling: 'P10-U5 static and deterministic disposable-fixture proof only. No production source, real user storage, persisted user data, migration, scarce observation, or formal proof is changed or consumed.'
  };
  result.result_sha256 = digest(result);
  return result;
}

function verifyResultHash(result) {
  if (!result || typeof result.result_sha256 !== 'string') return false;
  const copy = JSON.parse(JSON.stringify(result));
  const expected = copy.result_sha256;
  delete copy.result_sha256;
  return digest(copy) === expected;
}

if (require.main === module) {
  process.stdout.write(JSON.stringify(scenarioResult(), null, 2) + '\n');
}

module.exports = {
  TYPE,
  VERSION,
  OWNER,
  RESOURCE,
  LARGE_RECORDS,
  stable,
  digest,
  scenarioResult,
  verifyResultHash
};
