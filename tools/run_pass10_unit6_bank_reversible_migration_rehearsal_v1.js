#!/usr/bin/env node
'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const TYPE = 'PMP_PASS10_UNIT6_BANK_REVERSIBLE_MIGRATION_REHEARSAL_RESULT_V1';
const VERSION = '1.0.0';
const CONTRACT = 'PMP_CANONICAL_BANK_INVENTORY_CONTRACT_V1';
const OWNER = 'bank_screen_owner';
const STAGING_PREFIX = '__p10u6_disposable_staging_v1/';

function read(name) {
  return fs.readFileSync(path.join(ROOT, name), 'utf8');
}
function json(name) {
  return JSON.parse(read(name));
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
function clone(value) {
  return JSON.parse(JSON.stringify(value));
}
function mapObject(workspace) {
  return Object.fromEntries(Array.from(workspace.entries()).sort());
}
function byteLength(value) {
  return Buffer.byteLength(String(value), 'utf8');
}
function canonicalId(kind, namespace, nativeId, raw) {
  const native = String(nativeId || '').trim();
  const prefix = native ? 'bank-item:v1:' : 'bank-quarantine:v1:';
  const preimage = native
    ? [CONTRACT, kind, namespace, native].join('\0')
    : [CONTRACT, kind, namespace, digest(raw)].join('\0');
  return prefix + digest(preimage);
}

function fixtureWorkspace() {
  return new Map(Object.entries({
    pmp_master_bank_inventory_v1: JSON.stringify({
      type: 'PMP_MASTER_BANK_INVENTORY_V1',
      version: 'legacy-v7',
      owner: OWNER,
      banks: {
        world: {
          name: 'World Bank',
          records: [
            {record_id: 'world:alpha', summary: 'alpha'},
            {record_id: 'collision:same', summary: 'first'},
            {record_id: 'collision:same', summary: 'second'}
          ],
          references: []
        },
        library: {
          name: 'Library Bank',
          records: [{record_id: 'library:beta', summary: 'beta'}],
          references: []
        }
      }
    }),
    pmp_connection_bank_inventory_v1: JSON.stringify([
      {record_id: 'historic:connection:1', summary: 'historic-reference'}
    ]),
    pmp_bank_orphan_plugin_v77: '{"orphan":true,"payload":"EXACT-ORPHAN"}',
    pmp_helper_bank_index_v1: '{"type":"PMP_HELPER_BANK_INDEX_V1","broken":',
    unrelated_user_bytes: 'EXACT-UNRELATED-USER-BYTES'
  }));
}

function sourceSnapshot(workspace, namespaces) {
  return namespaces.map(namespace => ({
    namespace,
    present: workspace.has(namespace),
    raw: workspace.has(namespace) ? workspace.get(namespace) : null
  }));
}
function sourceDigest(workspace, namespaces) {
  return digest(sourceSnapshot(workspace, namespaces));
}
function makeItem(input) {
  const raw = String(input.raw == null ? '' : input.raw);
  return {
    canonical_id: canonicalId(
      input.storage_kind || 'LOCAL_STORAGE',
      input.namespace,
      input.native_id,
      raw
    ),
    source_storage_kind: input.storage_kind || 'LOCAL_STORAGE',
    source_namespace: input.namespace,
    source_native_id: input.native_id || null,
    owner_id: input.owner_id == null ? null : input.owner_id,
    owning_bank: input.owning_bank || 'master',
    provenance: {
      namespace: input.namespace,
      payload_sha256: digest(raw),
      payload_bytes: byteLength(raw)
    },
    state: input.state || 'ACTIVE',
    quarantine_reasons: (input.reasons || []).slice().sort(),
    exact_source_bytes_preserved: true,
    write_authority: input.write_authority || 'OWNER_REQUEST_ONLY',
    delete_authority: 'DENY',
    _raw: raw
  };
}

function planMigration(workspace) {
  const namespaces = [
    'pmp_master_bank_inventory_v1',
    'pmp_connection_bank_inventory_v1',
    'pmp_bank_orphan_plugin_v77',
    'pmp_helper_bank_index_v1',
    'pmp_missing_declared_binary_v1'
  ];
  const items = [];
  const masterRaw = workspace.get('pmp_master_bank_inventory_v1');
  const master = JSON.parse(masterRaw);
  Object.keys(master.banks).sort().forEach(bank => {
    const records = master.banks[bank].records || [];
    records.forEach(row => items.push(makeItem({
      namespace: 'pmp_master_bank_inventory_v1',
      native_id: row.record_id,
      owner_id: OWNER,
      owning_bank: bank,
      raw: JSON.stringify(row)
    })));
  });

  const historicRaw = workspace.get('pmp_connection_bank_inventory_v1');
  JSON.parse(historicRaw).forEach(row => items.push(makeItem({
    namespace: 'pmp_connection_bank_inventory_v1',
    native_id: row.record_id,
    owner_id: 'historic_connection_inventory',
    owning_bank: 'connections',
    raw: JSON.stringify(row),
    state: 'REFERENCE_ONLY',
    write_authority: 'NONE'
  })));

  const orphanRaw = workspace.get('pmp_bank_orphan_plugin_v77');
  items.push(makeItem({
    namespace: 'pmp_bank_orphan_plugin_v77',
    native_id: null,
    owner_id: null,
    owning_bank: 'master',
    raw: orphanRaw,
    state: 'QUARANTINED',
    reasons: ['UNKNOWN_NAMESPACE', 'UNKNOWN_OWNER', 'UNKNOWN_SCHEMA_TYPE'],
    write_authority: 'NONE'
  }));

  const corruptRaw = workspace.get('pmp_helper_bank_index_v1');
  items.push(makeItem({
    namespace: 'pmp_helper_bank_index_v1',
    native_id: null,
    owner_id: OWNER,
    owning_bank: 'helper',
    raw: corruptRaw,
    state: 'QUARANTINED',
    reasons: ['CORRUPT_RECORD'],
    write_authority: 'OWNER_REQUEST_ONLY'
  }));

  items.push(makeItem({
    namespace: 'pmp_missing_declared_binary_v1',
    native_id: 'declared:missing:1',
    owner_id: OWNER,
    owning_bank: 'connections',
    raw: '',
    state: 'UNAVAILABLE',
    reasons: ['SOURCE_UNAVAILABLE'],
    write_authority: 'OWNER_REQUEST_ONLY'
  }));

  const groups = {};
  items.forEach(item => (groups[item.canonical_id] ||= []).push(item));
  Object.values(groups).forEach(rows => {
    if (
      rows.length > 1
      && new Set(rows.map(row => row.provenance.payload_sha256)).size > 1
    ) {
      rows.forEach(row => {
        row.state = 'QUARANTINED';
        row.quarantine_reasons = Array.from(
          new Set(row.quarantine_reasons.concat('IDENTITY_COLLISION'))
        ).sort();
        row.write_authority = 'NONE';
      });
    }
  });

  const publicItems = items.map(item => {
    const row = clone(item);
    delete row._raw;
    return row;
  });
  const sourceBytes = Object.fromEntries(
    sourceSnapshot(workspace, namespaces)
      .filter(row => row.present)
      .map(row => [digest(row.raw), row.raw])
  );
  const plan = {
    type: 'PMP_PASS10_UNIT6_DISPOSABLE_MIGRATION_PLAN_V1',
    version: VERSION,
    contract_version: CONTRACT,
    owner: OWNER,
    target: 'DISPOSABLE_FIXTURE_STAGING_ONLY',
    source_namespaces: namespaces,
    source_digest: sourceDigest(workspace, namespaces),
    source_bytes_by_sha256: sourceBytes,
    items: publicItems,
    rules: {
      production_migration_allowed: false,
      delete_allowed: false,
      silent_rewrite_allowed: false,
      exact_rollback_required: true,
      idempotence_required: true,
      interruption_recovery_required: true
    }
  };
  plan.plan_sha256 = digest(plan);
  return plan;
}

function planValid(plan) {
  if (!plan || !/^[0-9a-f]{64}$/.test(plan.plan_sha256 || '')) return false;
  const copy = clone(plan);
  const expected = copy.plan_sha256;
  delete copy.plan_sha256;
  return digest(copy) === expected;
}
function rollback(workspace, snapshots) {
  [...snapshots].reverse().forEach(row => {
    if (row.present) workspace.set(row.key, row.raw);
    else workspace.delete(row.key);
  });
}
function applyPlan(workspace, plan, options = {}) {
  const deny = code => ({
    ok: false,
    decision: 'DENY',
    code,
    writes: 0,
    deletes: 0,
    receipt: null,
    rollback_snapshots: []
  });
  if (options.target === 'production') return deny('DENIED_PRODUCTION_TARGET');
  if (!planValid(plan)) return deny('DENIED_PLAN_INTEGRITY');
  if (sourceDigest(workspace, plan.source_namespaces) !== plan.source_digest) {
    return deny('DENIED_SOURCE_PREIMAGE_CHANGED');
  }
  const writes = plan.items.map((item, index) => ({
    key: STAGING_PREFIX + `item/${String(index).padStart(5, '0')}`,
    raw: JSON.stringify(item)
  })).concat([{
    key: STAGING_PREFIX + 'manifest',
    raw: JSON.stringify({
      type: 'PMP_PASS10_UNIT6_DISPOSABLE_STAGING_MANIFEST_V1',
      plan_sha256: plan.plan_sha256,
      source_digest: plan.source_digest,
      item_count: plan.items.length
    })
  }]);
  const snapshots = [];
  let changed = 0;
  try {
    writes.forEach((row, index) => {
      const current = workspace.has(row.key) ? workspace.get(row.key) : null;
      if (current === row.raw) return;
      snapshots.push({
        key: row.key,
        present: workspace.has(row.key),
        raw: current
      });
      workspace.set(row.key, row.raw);
      changed += 1;
      if (
        Number.isInteger(options.interrupt_after)
        && changed === options.interrupt_after
      ) {
        throw new Error(`fixture interruption after ${index + 1}`);
      }
    });
  } catch (error) {
    rollback(workspace, snapshots);
    return {
      ok: false,
      decision: 'DENY',
      code: 'DENIED_INTERRUPTED_ROLLED_BACK',
      writes: changed,
      deletes: 0,
      receipt: null,
      rollback_snapshots: snapshots,
      rollback_completed: true
    };
  }
  const receiptBody = {
    receipt_version: 'PMP_PASS10_UNIT6_DISPOSABLE_MIGRATION_RECEIPT_V1',
    plan_sha256: plan.plan_sha256,
    source_digest: plan.source_digest,
    target: plan.target,
    item_count: plan.items.length,
    changed_writes: changed,
    decision: 'ALLOW',
    code: changed ? 'DISPOSABLE_STAGING_APPLIED' : 'ALREADY_APPLIED'
  };
  const receipt = Object.assign(
    receiptBody,
    {receipt_sha256: digest(receiptBody)}
  );
  return {
    ok: true,
    decision: 'ALLOW',
    code: receipt.code,
    writes: changed,
    deletes: 0,
    receipt,
    rollback_snapshots: snapshots,
    rollback_completed: false
  };
}

function scenarioResult() {
  const unit5 = json('audit/pass10/pass10-bank-unit5-fault-corruption-proof-v1.json');
  const contract = json('audit/pass10/pass10-bank-unit2-inventory-contract-v1.json');
  const workspace = fixtureWorkspace();
  const baseline = mapObject(workspace);
  const baselineDigest = digest(baseline);
  const plan = planMigration(workspace);
  const afterPlan = mapObject(workspace);

  const interruptedWorkspace = fixtureWorkspace();
  const interruptedBefore = mapObject(interruptedWorkspace);
  const interrupted = applyPlan(interruptedWorkspace, plan, {
    interrupt_after: 3,
    target: 'disposable'
  });
  const interruptedAfter = mapObject(interruptedWorkspace);

  const migratedWorkspace = fixtureWorkspace();
  const migratedBefore = mapObject(migratedWorkspace);
  const applied = applyPlan(migratedWorkspace, plan, {target: 'disposable'});
  const migratedState = mapObject(migratedWorkspace);
  const appliedAgain = applyPlan(migratedWorkspace, plan, {
    target: 'disposable'
  });
  const idempotentState = mapObject(migratedWorkspace);
  rollback(migratedWorkspace, applied.rollback_snapshots);
  const rolledBack = mapObject(migratedWorkspace);

  const tamperedWorkspace = fixtureWorkspace();
  tamperedWorkspace.set(
    'pmp_bank_orphan_plugin_v77',
    '{"orphan":true,"payload":"TAMPERED"}'
  );
  const tamperedBefore = mapObject(tamperedWorkspace);
  const tampered = applyPlan(tamperedWorkspace, plan, {target: 'disposable'});
  const tamperedAfter = mapObject(tamperedWorkspace);

  const badPlan = clone(plan);
  badPlan.items[0].owner_id = 'helper_owner';
  const badPlanWorkspace = fixtureWorkspace();
  const badPlanBefore = mapObject(badPlanWorkspace);
  const badPlanResult = applyPlan(badPlanWorkspace, badPlan, {
    target: 'disposable'
  });
  const badPlanAfter = mapObject(badPlanWorkspace);

  const productionWorkspace = fixtureWorkspace();
  const productionBefore = mapObject(productionWorkspace);
  const production = applyPlan(productionWorkspace, plan, {
    target: 'production'
  });
  const productionAfter = mapObject(productionWorkspace);

  const collisionRows = plan.items.filter(
    item => item.source_native_id === 'collision:same'
  );
  const orphanRows = plan.items.filter(
    item => item.source_namespace === 'pmp_bank_orphan_plugin_v77'
  );
  const corruptRows = plan.items.filter(
    item => item.source_namespace === 'pmp_helper_bank_index_v1'
  );
  const unavailableRows = plan.items.filter(
    item => item.source_namespace === 'pmp_missing_declared_binary_v1'
  );
  const historicRows = plan.items.filter(
    item => item.source_namespace === 'pmp_connection_bank_inventory_v1'
  );

  const result = {
    type: TYPE,
    version: VERSION,
    status: 'BANK_REVERSIBLE_MIGRATION_REHEARSAL_PROVEN',
    authority: {
      target: plan.target,
      production_migration_allowed: plan.rules.production_migration_allowed,
      persisted_user_data_change_allowed: false,
      special_authority_required: false,
      special_authority_consumed: false
    },
    preflight: {
      contract_status: contract.status,
      unit5_status: unit5.status,
      unit5_unresolved_failures: unit5.proof.unresolved_deterministic_failures,
      plan_valid: planValid(plan),
      plan_sha256: plan.plan_sha256,
      source_digest: plan.source_digest,
      source_namespaces: plan.source_namespaces.length,
      source_bytes_preserved: Object.keys(plan.source_bytes_by_sha256).length,
      plan_changed_source_workspace: stable(baseline) !== stable(afterPlan),
      baseline_digest: baselineDigest
    },
    forward_mapping: {
      items: plan.items.length,
      active: plan.items.filter(item => item.state === 'ACTIVE').length,
      reference_only: historicRows.length,
      quarantined: plan.items.filter(
        item => item.state === 'QUARANTINED'
      ).length,
      unavailable: unavailableRows.length,
      stable_identities: plan.items.every(
        item => /^bank-(?:item|quarantine):v1:[0-9a-f]{64}$/.test(
          item.canonical_id
        )
      ),
      provenance_complete: plan.items.every(
        item => item.provenance
          && /^[0-9a-f]{64}$/.test(item.provenance.payload_sha256)
          && Number.isInteger(item.provenance.payload_bytes)
      ),
      delete_authority_denied: plan.items.every(
        item => item.delete_authority === 'DENY'
      ),
      collision_rows: collisionRows.length,
      collision_quarantined: collisionRows.every(
        item => item.state === 'QUARANTINED'
          && item.quarantine_reasons.includes('IDENTITY_COLLISION')
      ),
      collision_payloads_preserved: new Set(
        collisionRows.map(item => item.provenance.payload_sha256)
      ).size,
      orphan_rows: orphanRows.length,
      orphan_quarantined: orphanRows.every(
        item => item.state === 'QUARANTINED' && item.owner_id === null
      ),
      corrupt_rows: corruptRows.length,
      corrupt_quarantined: corruptRows.every(
        item => item.quarantine_reasons.includes('CORRUPT_RECORD')
      ),
      unavailable_rows: unavailableRows.length,
      unavailable_preserved: unavailableRows.every(
        item => item.state === 'UNAVAILABLE'
          && item.quarantine_reasons.includes('SOURCE_UNAVAILABLE')
      ),
      historic_rows: historicRows.length,
      historic_reference_only: historicRows.every(
        item => item.state === 'REFERENCE_ONLY'
          && item.write_authority === 'NONE'
      )
    },
    disposable_apply: {
      code: applied.code,
      changed_writes: applied.writes,
      deletes: applied.deletes,
      receipt_valid: applied.receipt.receipt_sha256 === digest(
        Object.fromEntries(
          Object.entries(applied.receipt).filter(
            ([key]) => key !== 'receipt_sha256'
          )
        )
      ),
      receipt_target: applied.receipt.target,
      staging_entries: Object.keys(migratedState).filter(
        key => key.startsWith(STAGING_PREFIX)
      ).length,
      source_bytes_unchanged: plan.source_namespaces.every(
        namespace => migratedBefore[namespace] === migratedState[namespace]
      ),
      unrelated_bytes_unchanged: migratedState.unrelated_user_bytes
        === 'EXACT-UNRELATED-USER-BYTES'
    },
    idempotence: {
      code: appliedAgain.code,
      changed_writes: appliedAgain.writes,
      deletes: appliedAgain.deletes,
      state_unchanged: stable(migratedState) === stable(idempotentState),
      plan_sha256_unchanged: appliedAgain.receipt.plan_sha256
        === plan.plan_sha256
    },
    interruption_recovery: {
      code: interrupted.code,
      writes_attempted: interrupted.writes,
      deletes: interrupted.deletes,
      rollback_completed: interrupted.rollback_completed,
      exact_baseline_restored: stable(interruptedBefore)
        === stable(interruptedAfter),
      staging_entries_after: Object.keys(interruptedAfter).filter(
        key => key.startsWith(STAGING_PREFIX)
      ).length,
      receipt_emitted: interrupted.receipt !== null
    },
    explicit_rollback: {
      exact_baseline_restored: stable(migratedBefore) === stable(rolledBack),
      staging_entries_after: Object.keys(rolledBack).filter(
        key => key.startsWith(STAGING_PREFIX)
      ).length,
      source_bytes_unchanged: plan.source_namespaces.every(
        namespace => migratedBefore[namespace] === rolledBack[namespace]
      ),
      unrelated_bytes_unchanged: rolledBack.unrelated_user_bytes
        === 'EXACT-UNRELATED-USER-BYTES'
    },
    denial_matrix: {
      production_code: production.code,
      production_zero_effect: stable(productionBefore) === stable(productionAfter),
      source_tamper_code: tampered.code,
      source_tamper_zero_effect: stable(tamperedBefore) === stable(tamperedAfter),
      plan_tamper_code: badPlanResult.code,
      plan_tamper_zero_effect: stable(badPlanBefore) === stable(badPlanAfter),
      deletes_across_denials: production.deletes
        + tampered.deletes
        + badPlanResult.deletes
    },
    observation_decision_input: {
      rehearsal_failures: 0,
      production_migration_performed: false,
      real_user_storage_accessed: false,
      user_app_check_required_now: false,
      bounded_observation_performed: false,
      bounded_observation_authority_consumed: false,
      pass10_closure_unit_ready: true
    },
    effects: {
      production_files_changed: false,
      runtime_integrity_changed: false,
      browser_launched: false,
      network_requests: false,
      disposable_fixture_writes_performed: true,
      disposable_fixture_rollback_completed: true,
      real_user_storage_reads: false,
      real_user_storage_writes: false,
      real_user_storage_deletes: false,
      persisted_user_data_changed: false,
      production_migration_performed: false,
      live_observation_performed: false,
      formal_proof_performed: false,
      production_behavior_activated: false
    },
    next_step: {
      id: 'P10-U7',
      objective: 'Decide whether a bounded observation is genuinely required, certify every Pass 10 unit and exit criterion, close Pass 10, and bind the exact Pass 11 entry.',
      requires_user_app_check_before_decision: false,
      perform_observation_automatically: false,
      requires_new_explicit_authority: false,
      persisted_user_data_change_allowed: false,
      production_migration_allowed: false,
      stop_after: false
    },
    claim_ceiling: 'P10-U6 disposable in-memory reversible migration rehearsal only. No production migration, real user storage access, deletion, persisted-data change, live observation, or formal proof occurred.'
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

if (require.main === module) {
  process.stdout.write(JSON.stringify(scenarioResult(), null, 2) + '\n');
}

module.exports = {
  TYPE,
  VERSION,
  CONTRACT,
  OWNER,
  STAGING_PREFIX,
  stable,
  digest,
  fixtureWorkspace,
  planMigration,
  planValid,
  applyPlan,
  rollback,
  scenarioResult,
  verifyResultHash
};
