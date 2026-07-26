#!/usr/bin/env node
'use strict';

const crypto = require('crypto');

const CONTRACT_VERSION = 'PMP_CANONICAL_BANK_INVENTORY_CONTRACT_V1';
const ITEM_VERSION = 'PMP_CANONICAL_BANK_INVENTORY_ITEM_V1';
const RESULT_TYPE = 'PMP_PASS10_UNIT2_BANK_INVENTORY_CONTRACT_RESULT_V1';
const BANK_OWNER = 'bank_screen_owner';
const RUN_OWNER = 'continuous_run_level_owner';
const CANONICAL_BANKS = [
  'world',
  'continuous_run',
  'connections',
  'library',
  'workshop',
  'helper',
  'protection',
  'bug_memory',
  'migration',
  'ui_control_surface',
  'settings_preferences',
  'test_verification',
  'master'
];

function stable(value) {
  if (Array.isArray(value)) return `[${value.map(stable).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stable(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

function sha256(value) {
  const bytes = Buffer.isBuffer(value)
    ? value
    : Buffer.from(typeof value === 'string' ? value : stable(value));
  return crypto.createHash('sha256').update(bytes).digest('hex');
}

function policy() {
  return {
    contract_version: CONTRACT_VERSION,
    item_version: ITEM_VERSION,
    model: 'OWNER_FACTS_TO_READ_ONLY_CANONICAL_PROJECTION_FAIL_CLOSED',
    canonical_inventory: {
      storage_key: 'pmp_master_bank_inventory_v1',
      owner_id: BANK_OWNER,
      bank_ids: CANONICAL_BANKS.slice(),
      identity_algorithm: 'SHA-256',
      identity_preimage_fields: [
        'contract_version',
        'source_storage_kind',
        'source_namespace',
        'source_native_id'
      ],
      canonical_id_prefix: 'bank-item:v1:',
      missing_identity_prefix: 'bank-quarantine:v1:',
      native_identity_preserved: true,
      payload_exact_bytes_preserved: true
    },
    required_source_fields: [
      'source_storage_kind',
      'source_namespace',
      'source_native_id',
      'owning_bank',
      'owner_id',
      'schema_type',
      'schema_version',
      'raw_bytes',
      'compatibility_aliases'
    ],
    canonical_item_fields: [
      'item_version',
      'canonical_id',
      'source_storage_kind',
      'source_namespace',
      'source_native_id',
      'owning_bank',
      'owner_id',
      'schema_type',
      'schema_version',
      'payload_sha256',
      'payload_bytes',
      'raw_bytes_base64',
      'compatibility_aliases',
      'namespace_classification',
      'state',
      'quarantine_reasons',
      'write_authority',
      'delete_authority'
    ],
    namespace_rules: [
      {
        storage_kind: 'LOCAL_STORAGE',
        namespace: 'pmp_master_bank_inventory_v1',
        owner_id: BANK_OWNER,
        classification: 'CANONICAL_INDEX',
        write_authority: 'BANK_OWNER_RECEIPTED_REQUEST_ONLY'
      },
      {
        storage_kind: 'LOCAL_STORAGE',
        namespace: 'pmp_source_bank_router_receipts_v1',
        owner_id: BANK_OWNER,
        classification: 'OWNER_GOVERNED_RECEIPT_CHAIN',
        write_authority: 'BANK_OWNER_RECEIPTED_REQUEST_ONLY'
      },
      {
        storage_kind: 'LOCAL_STORAGE',
        namespace: 'pmp_helper_bank_index_v1',
        owner_id: BANK_OWNER,
        classification: 'OWNER_GOVERNED_INDEX',
        write_authority: 'BANK_OWNER_RECEIPTED_REQUEST_ONLY'
      },
      {
        storage_kind: 'LOCAL_STORAGE',
        namespace: 'pmp_connections_bank_chat_memory_deposits_v1',
        owner_id: BANK_OWNER,
        classification: 'OWNER_GOVERNED_INDEX',
        write_authority: 'BANK_OWNER_RECEIPTED_REQUEST_ONLY'
      },
      {
        storage_kind: 'LOCAL_STORAGE',
        namespace: 'pmp_continuous_run_state_bank_v1',
        owner_id: RUN_OWNER,
        classification: 'CONTINUOUS_RUN_OWNER_FACT',
        write_authority: 'CONTINUOUS_RUN_REQUEST_BANK_OWNER_COMMIT'
      },
      {
        storage_kind: 'LOCAL_STORAGE',
        namespace: 'pmp_continuous_run_state_receipts_v1',
        owner_id: RUN_OWNER,
        classification: 'CONTINUOUS_RUN_OWNER_RECEIPT_CHAIN',
        write_authority: 'CONTINUOUS_RUN_REQUEST_BANK_OWNER_COMMIT'
      },
      {
        storage_kind: 'LOCAL_STORAGE',
        namespace: 'pmp_continuous_run_state_manifest_v1',
        owner_id: RUN_OWNER,
        classification: 'CONTINUOUS_RUN_OWNER_MANIFEST',
        write_authority: 'CONTINUOUS_RUN_REQUEST_BANK_OWNER_COMMIT'
      },
      {
        storage_kind: 'LOCAL_STORAGE',
        namespace: 'pmp_bank_project_registry_v1',
        owner_id: RUN_OWNER,
        classification: 'CONTINUOUS_RUN_PROJECT_INDEX',
        write_authority: 'CONTINUOUS_RUN_REQUEST_BANK_OWNER_COMMIT'
      },
      {
        storage_kind: 'LOCAL_STORAGE',
        namespace: 'pmp_bank_project_registry_v1_receipt',
        owner_id: RUN_OWNER,
        classification: 'CONTINUOUS_RUN_PROJECT_RECEIPT',
        write_authority: 'CONTINUOUS_RUN_REQUEST_BANK_OWNER_COMMIT'
      },
      {
        storage_kind: 'INDEXED_DB',
        namespace: 'pmp_connections_bank_deposits_db_v1/deposits',
        owner_id: BANK_OWNER,
        classification: 'OWNER_GOVERNED_BINARY_PAYLOAD',
        write_authority: 'BANK_OWNER_RECEIPTED_REQUEST_ONLY'
      },
      {
        storage_kind: 'LOCAL_STORAGE',
        namespace: 'pmp_continuous_run_bank_transfer_store_manifest_v1',
        owner_id: RUN_OWNER,
        classification: 'AUXILIARY_READ_ONLY_UNTIL_OWNER_UPDATE',
        write_authority: 'NO_CANONICAL_WRITE_UNTIL_P10_U4'
      },
      {
        storage_kind: 'LOCAL_STORAGE',
        namespace: 'pmp_continuous_run_bank_transfer_store_receipts_v1',
        owner_id: RUN_OWNER,
        classification: 'AUXILIARY_READ_ONLY_UNTIL_OWNER_UPDATE',
        write_authority: 'NO_CANONICAL_WRITE_UNTIL_P10_U4'
      },
      {
        storage_kind: 'INDEXED_DB',
        namespace: 'pmp_continuous_run_bank_transfer_store_db_v1/items',
        owner_id: RUN_OWNER,
        classification: 'AUXILIARY_READ_ONLY_UNTIL_OWNER_UPDATE',
        write_authority: 'NO_CANONICAL_WRITE_UNTIL_P10_U4'
      },
      {
        storage_kind: 'LOCAL_STORAGE',
        namespace: 'pmp_connection_bank_inventory_v1',
        owner_id: 'historic_connection_inventory',
        classification: 'HISTORIC_REFERENCE_ONLY',
        write_authority: 'NONE'
      },
      {
        storage_kind: 'LOCAL_STORAGE',
        namespace: 'pmp_connection_protected_bank_registry_v1',
        owner_id: 'historic_connection_inventory',
        classification: 'HISTORIC_REFERENCE_ONLY',
        write_authority: 'NONE'
      },
      {
        storage_kind: 'LOCAL_STORAGE',
        namespace: 'pmp_connection_bank_inventory_receipt_v1',
        owner_id: 'historic_connection_inventory',
        classification: 'HISTORIC_REFERENCE_ONLY',
        write_authority: 'NONE'
      }
    ],
    accepted_schema_versions: {
      PMP_MASTER_BANK_INVENTORY_V1: ['1', '1.0.0'],
      PMP_HELPER_BANK_INDEX_V1: ['1', '1.0.0'],
      BANK_PROJECT_REGISTRY_V1: ['1', '1.0.0'],
      PMP_UNIVERSAL_CONTINUOUS_WORK_ENGINE_STATE_V1: ['1', '1.0.0'],
      PMP_PERSISTENT_CONTINUOUS_RUN_STATE_BANK_V1: ['1', '1.0.0'],
      PMP_CONTINUOUS_RUN_STATE_MANIFEST_V1: ['1', '1.0.0'],
      PMP_CONNECTIONS_BANK_DEPOSIT_INDEX_V1: ['1', '1.0.0'],
      PMP_BANK_BINARY_PAYLOAD_V1: ['1', '1.0.0'],
      PMP_HISTORIC_CONNECTION_BANK_INVENTORY_V1: ['1', '1.0.0'],
      PMP_UNKNOWN_SCHEMA: []
    },
    compatibility: {
      legacy_aliases_are_source_native_references: true,
      aliases_convey_authority: false,
      adapters_are_pure_and_read_only: true,
      active_tab_conveys_authority: false,
      helper_registration_conveys_bank_authority: false,
      historic_inventory_is_canonical: false,
      silent_alias_merge: 'FORBIDDEN',
      silent_schema_upgrade: 'FORBIDDEN',
      storage_migration: 'FORBIDDEN_IN_P10_U2_THROUGH_P10_U5'
    },
    quarantine: {
      policy: 'PRESERVE_EXACT_BYTES_NEVER_SILENTLY_DELETE',
      reasons: [
        'MISSING_REQUIRED_FIELD',
        'MISSING_NATIVE_ID',
        'UNKNOWN_NAMESPACE',
        'UNKNOWN_OWNING_BANK',
        'UNKNOWN_OWNER',
        'UNKNOWN_SCHEMA_TYPE',
        'UNKNOWN_SCHEMA_VERSION',
        'PAYLOAD_HASH_MISMATCH',
        'MALFORMED_COMPATIBILITY_ALIAS',
        'IDENTITY_COLLISION',
        'MISSING_BINARY_PAYLOAD',
        'SOURCE_UNAVAILABLE',
        'CORRUPT_RECORD',
        'ORPHANED_OWNER',
        'STALE_SOURCE'
      ],
      collision: 'QUARANTINE_ALL_COLLIDING_ITEMS_PRESERVE_EACH_PAYLOAD',
      unknown: 'QUARANTINE',
      orphan: 'QUARANTINE',
      corrupt: 'QUARANTINE',
      unavailable: 'PRESERVE_INDEX_FACT_AND_MARK_UNAVAILABLE',
      stale: 'PRESERVE_AND_MARK_STALE'
    },
    states: [
      'ACTIVE',
      'REFERENCE_ONLY',
      'UNKNOWN',
      'ORPHANED',
      'STALE',
      'UNAVAILABLE',
      'CORRUPT',
      'QUARANTINED'
    ],
    delete_contract: {
      default: 'DENY',
      bank_tab_delete_api: 'FORBIDDEN',
      quarantine_auto_delete: false,
      historic_auto_delete: false,
      unavailable_auto_delete: false,
      stale_auto_delete: false,
      exact_user_confirmation_required: true,
      exact_owner_capability_required: true,
      exact_expected_version_required: true,
      exact_payload_sha256_required: true,
      append_only_receipt_required: true,
      production_delete_enabled_in_p10_u2: false
    },
    representation_contract: {
      projection_mode: 'READ_ONLY_OWNER_FACTS',
      enumerate_only_declared_namespaces: false,
      unknown_namespaces_visible_as_quarantine: true,
      raw_payload_exposed_to_ui: false,
      write_api_exposed_to_ui: false,
      delete_api_exposed_to_ui: false,
      migration_api_exposed_to_ui: false,
      recurring_polling_required: false,
      owner_event_updates_only: true
    }
  };
}

function namespaceRule(input, contract) {
  return contract.namespace_rules.find(row =>
    row.storage_kind === input.source_storage_kind &&
    row.namespace === input.source_namespace
  );
}

function rawBuffer(value) {
  if (Buffer.isBuffer(value)) return Buffer.from(value);
  if (typeof value === 'string') return Buffer.from(value);
  if (value === undefined || value === null) return Buffer.alloc(0);
  return Buffer.from(stable(value));
}

function canonicalIdentity(input, contract = policy()) {
  const hasNativeId = typeof input.source_native_id === 'string' && input.source_native_id.length > 0;
  if (hasNativeId) {
    const preimage = [
      contract.contract_version,
      input.source_storage_kind,
      input.source_namespace,
      input.source_native_id
    ].join('\u0000');
    return `${contract.canonical_inventory.canonical_id_prefix}${sha256(preimage)}`;
  }
  const bytes = rawBuffer(input.raw_bytes);
  const preimage = [
    contract.contract_version,
    input.source_storage_kind || '',
    input.source_namespace || '',
    sha256(bytes)
  ].join('\u0000');
  return `${contract.canonical_inventory.missing_identity_prefix}${sha256(preimage)}`;
}

function normalizeItem(input, contract = policy()) {
  const reasons = [];
  for (const field of contract.required_source_fields) {
    if (!Object.prototype.hasOwnProperty.call(input || {}, field)) {
      reasons.push('MISSING_REQUIRED_FIELD');
    }
  }
  const bytes = rawBuffer(input?.raw_bytes);
  const payloadSha = sha256(bytes);
  const rule = namespaceRule(input || {}, contract);
  if (typeof input?.source_native_id !== 'string' || input.source_native_id.length === 0) {
    reasons.push('MISSING_NATIVE_ID');
  }
  if (!rule) reasons.push('UNKNOWN_NAMESPACE');
  if (!contract.canonical_inventory.bank_ids.includes(input?.owning_bank)) {
    reasons.push('UNKNOWN_OWNING_BANK');
  }
  if (!rule || input?.owner_id !== rule.owner_id) reasons.push('UNKNOWN_OWNER');
  if (!Object.prototype.hasOwnProperty.call(contract.accepted_schema_versions, input?.schema_type)) {
    reasons.push('UNKNOWN_SCHEMA_TYPE');
  } else if (!contract.accepted_schema_versions[input.schema_type].includes(String(input?.schema_version))) {
    reasons.push('UNKNOWN_SCHEMA_VERSION');
  }
  if (input?.declared_payload_sha256 && input.declared_payload_sha256 !== payloadSha) {
    reasons.push('PAYLOAD_HASH_MISMATCH');
  }
  if (!Array.isArray(input?.compatibility_aliases) ||
      (input.compatibility_aliases || []).some(alias => typeof alias !== 'string' || alias.length === 0)) {
    reasons.push('MALFORMED_COMPATIBILITY_ALIAS');
  }
  if (rule?.classification === 'OWNER_GOVERNED_BINARY_PAYLOAD' && bytes.length === 0) {
    reasons.push('MISSING_BINARY_PAYLOAD');
  }
  if (input?.source_available === false) reasons.push('SOURCE_UNAVAILABLE');
  if (input?.corrupt === true) reasons.push('CORRUPT_RECORD');
  if (input?.orphaned === true) reasons.push('ORPHANED_OWNER');
  if (input?.stale === true) reasons.push('STALE_SOURCE');

  const uniqueReasons = [...new Set(reasons)].sort();
  let state = 'ACTIVE';
  if (rule?.classification === 'HISTORIC_REFERENCE_ONLY') state = 'REFERENCE_ONLY';
  if (input?.stale === true) state = 'STALE';
  if (input?.source_available === false) state = 'UNAVAILABLE';
  if (input?.orphaned === true) state = 'ORPHANED';
  if (input?.corrupt === true) state = 'CORRUPT';
  if (uniqueReasons.some(reason => !['SOURCE_UNAVAILABLE', 'STALE_SOURCE'].includes(reason))) {
    state = 'QUARANTINED';
  }

  return {
    item_version: contract.item_version,
    canonical_id: canonicalIdentity(input || {}, contract),
    source_storage_kind: input?.source_storage_kind ?? null,
    source_namespace: input?.source_namespace ?? null,
    source_native_id: input?.source_native_id ?? null,
    owning_bank: input?.owning_bank ?? null,
    owner_id: input?.owner_id ?? null,
    schema_type: input?.schema_type ?? null,
    schema_version: input?.schema_version === undefined ? null : String(input.schema_version),
    payload_sha256: payloadSha,
    payload_bytes: bytes.length,
    raw_bytes_base64: bytes.toString('base64'),
    compatibility_aliases: Array.isArray(input?.compatibility_aliases)
      ? input.compatibility_aliases.slice()
      : [],
    namespace_classification: rule?.classification || 'UNKNOWN_NAMESPACE',
    state,
    quarantine_reasons: uniqueReasons,
    write_authority: rule?.write_authority || 'NONE',
    delete_authority: 'DENY_BY_DEFAULT_EXACT_OWNER_CAPABILITY_AND_CONFIRMATION_REQUIRED'
  };
}

function reconcileInventory(inputs, contract = policy()) {
  const items = inputs.map(input => normalizeItem(input, contract));
  const byIdentity = new Map();
  for (const item of items) {
    const rows = byIdentity.get(item.canonical_id) || [];
    rows.push(item);
    byIdentity.set(item.canonical_id, rows);
  }
  for (const rows of byIdentity.values()) {
    if (rows.length > 1 && new Set(rows.map(row => row.payload_sha256)).size > 1) {
      for (const item of rows) {
        item.state = 'QUARANTINED';
        item.quarantine_reasons = [...new Set(item.quarantine_reasons.concat('IDENTITY_COLLISION'))].sort();
      }
    }
  }
  const summary = {
    items: items.length,
    active: items.filter(row => row.state === 'ACTIVE').length,
    reference_only: items.filter(row => row.state === 'REFERENCE_ONLY').length,
    quarantined: items.filter(row => row.state === 'QUARANTINED').length,
    orphaned: items.filter(row => row.state === 'ORPHANED').length,
    stale: items.filter(row => row.state === 'STALE').length,
    unavailable: items.filter(row => row.state === 'UNAVAILABLE').length,
    corrupt: items.filter(row => row.state === 'CORRUPT').length,
    identities: new Set(items.map(row => row.canonical_id)).size,
    exact_payload_bytes_preserved: items.reduce((total, row) => total + row.payload_bytes, 0)
  };
  const body = {
    type: RESULT_TYPE,
    version: '1.0.0',
    status: 'PASS',
    contract,
    summary,
    items,
    effects: {
      production_files_changed: false,
      runtime_integrity_changed: false,
      browser_launched: false,
      network_requests: false,
      storage_reads: false,
      storage_writes: false,
      route_changes: false,
      mounts: false,
      bank_user_data_mutations: false,
      continuous_run_user_data_mutations: false,
      repairs: false,
      live_observation_performed: false,
      formal_proof_performed: false,
      persisted_user_data_changed: false,
      storage_migration_performed: false,
      production_behavior_activated: false
    },
    claim_ceiling: 'Pure static P10-U2 contract evaluation over supplied fixtures only. It reads no live storage, changes no Bank tab or production source, mutates no user data, performs no migration or observation, and consumes no formal proof.'
  };
  return Object.assign(body, {result_sha256: sha256(body)});
}

function verifyResultHash(result) {
  const copy = JSON.parse(JSON.stringify(result));
  const recorded = copy.result_sha256;
  delete copy.result_sha256;
  return recorded === sha256(copy);
}

function sampleInput(overrides = {}) {
  return Object.assign({
    source_storage_kind: 'LOCAL_STORAGE',
    source_namespace: 'pmp_master_bank_inventory_v1',
    source_native_id: 'record:sample:001',
    owning_bank: 'master',
    owner_id: BANK_OWNER,
    schema_type: 'PMP_MASTER_BANK_INVENTORY_V1',
    schema_version: '1.0.0',
    raw_bytes: '{"sample":true}',
    compatibility_aliases: []
  }, overrides);
}

if (require.main === module) {
  process.stdout.write(`${JSON.stringify(reconcileInventory([]), null, 2)}\n`);
}

module.exports = {
  CONTRACT_VERSION,
  ITEM_VERSION,
  RESULT_TYPE,
  BANK_OWNER,
  RUN_OWNER,
  CANONICAL_BANKS,
  stable,
  sha256,
  policy,
  canonicalIdentity,
  normalizeItem,
  reconcileInventory,
  verifyResultHash,
  sampleInput
};
