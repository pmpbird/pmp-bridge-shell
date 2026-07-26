#!/usr/bin/env node
'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const TYPE = 'PMP_PASS10_UNIT1_BANK_INVENTORY_RECONCILIATION_RESULT_V1';
const VERSION = '1.0.0';
const CANONICAL_SOURCES = [
  'pmp-bank-continuous-run-owner-boundary-v1.js',
  'pmp-continuous-run-state-bank-v1.js',
  'pmp-master-bank-inventory-router-v1.js',
  'pmp-master-bank-tab-v1.js',
  'pmp-bank-screen-owner-v1.js'
];
const BANK_KEYS = [
  'pmp_master_bank_inventory_v1',
  'pmp_source_bank_router_receipts_v1',
  'pmp_helper_bank_index_v1',
  'pmp_connections_bank_chat_memory_deposits_v1'
];
const CONTINUOUS_RUN_KEYS = [
  'pmp_continuous_run_state_bank_v1',
  'pmp_continuous_run_state_receipts_v1',
  'pmp_continuous_run_state_manifest_v1',
  'pmp_bank_project_registry_v1',
  'pmp_bank_project_registry_v1_receipt'
];
const BANKS = {
  world: 'World Bank',
  continuous_run: 'Continuous Run Bank',
  connections: 'Connections Bank',
  library: 'Library Bank',
  workshop: 'Workshop Bank',
  helper: 'Helper Bank',
  protection: 'Protection Bank',
  bug_memory: 'Bug Bank',
  migration: 'Migration Bank',
  ui_control_surface: 'UI / Control Surface Bank',
  settings_preferences: 'Settings / Preferences Bank',
  test_verification: 'Test / Verification Bank',
  master: 'Master Bank Inventory'
};

function file(relative) {
  return fs.readFileSync(path.join(ROOT, relative), 'utf8');
}
function shaBytes(payload) {
  return crypto.createHash('sha256').update(payload).digest('hex');
}
function stable(value) {
  if (Array.isArray(value)) return '[' + value.map(stable).join(',') + ']';
  if (value && typeof value === 'object') {
    return '{' + Object.keys(value).sort().map(key => JSON.stringify(key) + ':' + stable(value[key])).join(',') + '}';
  }
  return JSON.stringify(value);
}
function digest(value) {
  return shaBytes(Buffer.from(stable(value)));
}
function classifySource(name) {
  if (CANONICAL_SOURCES.includes(name)) return 'CANONICAL_OWNER_CHAIN';
  if (/diagnostic|probe|recorder|test|readiness|timeline|inspector|cause-map/i.test(name)) return 'DIAGNOSTIC_OR_REHEARSAL';
  return 'HISTORICAL_COMPATIBILITY_OR_AUXILIARY';
}
function hasAll(text, values) {
  return values.every(value => text.includes(value));
}

function scenarioResult() {
  const bankNamedSources = fs.readdirSync(ROOT)
    .filter(name => /^pmp-.*bank.*\.(?:js|json|html)$/i.test(name))
    .sort()
    .map(name => {
      const payload = fs.readFileSync(path.join(ROOT, name));
      return {
        path: name,
        extension: path.extname(name).slice(1),
        role: classifySource(name),
        bytes: payload.length,
        sha256: shaBytes(payload)
      };
    });
  const sourceCounts = {
    total: bankNamedSources.length,
    js: bankNamedSources.filter(row => row.extension === 'js').length,
    html: bankNamedSources.filter(row => row.extension === 'html').length,
    json: bankNamedSources.filter(row => row.extension === 'json').length,
    canonical_owner_chain: bankNamedSources.filter(row => row.role === 'CANONICAL_OWNER_CHAIN').length,
    diagnostic_or_rehearsal: bankNamedSources.filter(row => row.role === 'DIAGNOSTIC_OR_REHEARSAL').length,
    historical_compatibility_or_auxiliary: bankNamedSources.filter(row => row.role === 'HISTORICAL_COMPATIBILITY_OR_AUXILIARY').length
  };
  const sourceCatalogSha256 = digest(bankNamedSources);
  const source = Object.fromEntries(CANONICAL_SOURCES.map(name => [name, file(name)]));
  const boundary = source['pmp-bank-continuous-run-owner-boundary-v1.js'];
  const router = source['pmp-master-bank-inventory-router-v1.js'];
  const tab = source['pmp-master-bank-tab-v1.js'];
  const state = source['pmp-continuous-run-state-bank-v1.js'];
  const owner = source['pmp-bank-screen-owner-v1.js'];
  const project = file('pmp-bank-project-registry-v1.js');
  const transfer = file('pmp-continuous-run-bank-transfer-store-v1.js');
  const connections = file('pmp-connections-bank-packet-delete-v1.js');
  const historicInventory = file('pmp-connection-bank-inventory-v1.js');

  const declaredSchemas = {
    master_inventory: {
      storage_key: BANK_KEYS[0],
      type: 'PMP_MASTER_BANK_INVENTORY_V1',
      owner: 'bank_screen_owner',
      top_level_fields: ['type', 'version', 'owner', 'updated_at', 'rule', 'banks'],
      bank_entry_fields: ['name', 'records', 'references'],
      canonical_banks: Object.entries(BANKS).map(([bank_id, name]) => ({bank_id, name})),
      record_required_fields: ['record_id', 'record_type', 'owning_bank', 'source_tab', 'active_system', 'action', 'summary', 'helper_id', 'allowed_references', 'write_permissions', 'created_at', 'updated_at'],
      record_optional_fields: ['payload', 'payload_key', 'project_state_id'],
      reference_fields: ['to_bank', 'record_id', 'reason', 'at', 'note']
    },
    helper_index: {
      storage_key: BANK_KEYS[2],
      type: 'PMP_HELPER_BANK_INDEX_V1',
      item_fields: ['helper_id', 'owning_bank', 'record_id', 'source_tab', 'active_system', 'last_touched_at', 'allowed_references', 'write_permissions']
    },
    project_registry: {
      storage_key: CONTINUOUS_RUN_KEYS[3],
      type: 'BANK_PROJECT_REGISTRY_V1',
      project_fields: ['id', 'name', 'category', 'status', 'item_count', 'created_at', 'updated_at'],
      protected_seed_ids: ['bank-project-bank-system-000001', 'bank-project-resident-system-000002', 'bank-project-continuous-run-engine-000003']
    },
    continuous_run_state: {
      storage_keys: CONTINUOUS_RUN_KEYS.slice(0, 3),
      type: 'PMP_UNIVERSAL_CONTINUOUS_WORK_ENGINE_STATE_V1',
      legacy_type: 'PMP_PERSISTENT_CONTINUOUS_RUN_STATE_BANK_V1',
      owner: 'continuous_run_level_owner',
      compatibility_aliases_retained: true
    },
    connections_deposit_index: {
      storage_key: BANK_KEYS[3],
      top_level_fields_observed: ['records', 'categories', 'updated_at'],
      binary_store: {database: 'pmp_connections_bank_deposits_db_v1', object_store: 'deposits'}
    },
    staging_transfer_store: {
      manifest_key: 'pmp_continuous_run_bank_transfer_store_manifest_v1',
      receipt_key: 'pmp_continuous_run_bank_transfer_store_receipts_v1',
      binary_store: {database: 'pmp_continuous_run_bank_transfer_store_db_v1', object_store: 'items'},
      status: 'OUTSIDE_P9_NINE_KEY_OWNER_SET_REQUIRES_P10_CONTRACT_CLASSIFICATION'
    },
    historic_inventory_output: {
      keys: ['pmp_connection_bank_inventory_v1', 'pmp_connection_protected_bank_registry_v1', 'pmp_connection_bank_inventory_receipt_v1'],
      status: 'HISTORIC_READ_SCAN_OUTPUT_NOT_CANONICAL_INVENTORY'
    }
  };
  const reconciliation = {
    canonical_owner_sources_present: CANONICAL_SOURCES.every(name => fs.existsSync(path.join(ROOT, name))),
    canonical_owner_source_hashes: Object.fromEntries(CANONICAL_SOURCES.map(name => [name, shaBytes(fs.readFileSync(path.join(ROOT, name)))])),
    boundary_declares_all_nine_governed_keys: hasAll(boundary, BANK_KEYS.concat(CONTINUOUS_RUN_KEYS)),
    router_declares_all_thirteen_banks: Object.entries(BANKS).every(([key, name]) => router.includes(`${key}:'${name}'`)),
    router_declares_record_identity: hasAll(router, ['record_id', 'record_type', 'owning_bank']),
    router_reads_do_not_persist: router.includes('Read paths never persist.'),
    tab_exports_all_current_families: hasAll(tab, ['master_inventory', 'router_receipts', 'helper_bank', 'continuous_run_bank', 'connections_bank_chat_memory_deposit_index']),
    continuous_run_retains_legacy_aliases: hasAll(state, ['legacy_type', 'PMP_PERSISTENT_CONTINUOUS_RUN_STATE_BANK_V1', 'PMP_CONTINUOUS_RUN_STATE_MANIFEST_V1']),
    continuous_run_owner_requests_bank_commits: hasAll(owner, ['request:bank_screen_owner:COMMIT_WRITE:', 'bank:persist:project_registry']),
    project_registry_schema_present: hasAll(project, declaredSchemas.project_registry.project_fields),
    transfer_store_namespaces_present: hasAll(transfer, [declaredSchemas.staging_transfer_store.manifest_key, declaredSchemas.staging_transfer_store.receipt_key, declaredSchemas.staging_transfer_store.binary_store.database]),
    connections_binary_namespace_present: hasAll(connections, [declaredSchemas.connections_deposit_index.binary_store.database, declaredSchemas.connections_deposit_index.binary_store.object_store]),
    historic_inventory_namespace_present: hasAll(historicInventory, declaredSchemas.historic_inventory_output.keys),
    live_user_inventory_read: false,
    browser_launched: false,
    persisted_user_data_changed: false,
    storage_migration_performed: false
  };
  const conflicts = [
    {
      id: 'P10-I001-MULTIPLE-IDENTITY-DOMAINS',
      finding: 'Canonical record_id, project id, deposit project_state identity, and IndexedDB item keys are distinct and need an explicit identity/provenance contract.',
      required_resolution: 'P10-U2'
    },
    {
      id: 'P10-I002-SECONDARY-NAMESPACES-OUTSIDE-NINE-KEY-SET',
      finding: 'Staging-transfer LocalStorage and IndexedDB namespaces and Connections IndexedDB payloads sit outside the nine P9 governed LocalStorage keys.',
      required_resolution: 'P10-U2'
    },
    {
      id: 'P10-I003-SCHEMA-VERSION-AND-LEGACY-ALIAS-DRIFT',
      finding: 'Continuous Run state intentionally retains legacy types and aliases while Bank records and project records use different versions and field sets.',
      required_resolution: 'P10-U2'
    },
    {
      id: 'P10-I004-OPTIONAL-PAYLOAD-SHAPES',
      finding: 'Canonical Bank records may carry payload, payload_key, or project_state_id without one universal payload schema.',
      required_resolution: 'P10-U2'
    },
    {
      id: 'P10-I005-HISTORIC-INVENTORY-IS-NOT-CANONICAL',
      finding: 'The older connection inventory scan wrote its own inventory, registry, and receipt namespaces and must remain historical evidence, not be merged silently.',
      required_resolution: 'P10-U2'
    },
    {
      id: 'P10-I006-NO-LIVE-USER-DATA-CENSUS-IN-STATIC-UNIT',
      finding: 'P10-U1 inventories declared repository schemas only; actual user records, unknown values, orphans, and corruption are deliberately not read.',
      required_resolution: 'Preserve unknown data and defer bounded representation/proof to P10-U3 through P10-U7.'
    }
  ];
  const complete = Object.values(reconciliation).every(value =>
    typeof value === 'boolean' ? value === true || ['live_user_inventory_read', 'browser_launched', 'persisted_user_data_changed', 'storage_migration_performed'].includes(
      Object.keys(reconciliation).find(key => reconciliation[key] === value)
    ) : true
  );
  const result = {
    type: TYPE,
    version: VERSION,
    status: complete ? 'BANK_INVENTORY_RECONCILIATION_PROVEN' : 'BANK_INVENTORY_RECONCILIATION_REQUIRES_REVIEW',
    mode: 'STATIC_REPOSITORY_SCHEMA_CENSUS_READ_ONLY',
    source_counts: sourceCounts,
    source_catalog_sha256: sourceCatalogSha256,
    source_records: bankNamedSources,
    governed_local_storage: {
      bank_owner_keys: BANK_KEYS,
      continuous_run_requested_keys: CONTINUOUS_RUN_KEYS,
      total: BANK_KEYS.length + CONTINUOUS_RUN_KEYS.length
    },
    declared_schemas: declaredSchemas,
    reconciliation,
    conflicts,
    policy: {
      canonical_inventory_key: BANK_KEYS[0],
      canonical_inventory_owner: 'bank_screen_owner',
      unknown_or_orphan_policy: 'QUARANTINE_PRESERVE_EXACT_BYTES_NEVER_SILENTLY_DELETE',
      historic_namespace_policy: 'CLASSIFY_AND_REFERENCE_NEVER_SILENTLY_MERGE',
      p10_u1_live_data_access: 'FORBIDDEN_AND_NOT_PERFORMED',
      p10_u1_writes: 'NONE'
    },
    next_step: {
      id: 'P10-U2',
      objective: 'Define canonical Bank inventory identity, provenance, schema-version, quarantine, compatibility, and no-deletion contracts from this reconciliation.',
      requires_user_app_check: false,
      requires_new_explicit_authority: false,
      persisted_user_data_change_allowed: false,
      storage_migration_allowed: false,
      stop_after: false
    },
    effects: {
      production_files_changed: false,
      runtime_integrity_changed: false,
      browser_launched: false,
      network_requests: false,
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
    claim_ceiling: 'P10-U1 static repository source and declared-schema reconciliation only. It does not inspect live user records, decide canonical migration, change the Bank tab, write storage, launch the app, perform an observation, or consume formal proof.'
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

if (require.main === module) process.stdout.write(JSON.stringify(scenarioResult(), null, 2) + '\n');
module.exports = {TYPE, VERSION, CANONICAL_SOURCES, BANK_KEYS, CONTINUOUS_RUN_KEYS, BANKS, stable, digest, scenarioResult, verifyResultHash};
