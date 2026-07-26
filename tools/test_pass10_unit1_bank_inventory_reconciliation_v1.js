#!/usr/bin/env node
'use strict';

const assert = require('assert');
const runner = require('./run_pass10_unit1_bank_inventory_reconciliation_v1.js');

let assertions = 0;
function check(value, message) { assertions += 1; assert(value, message); }
function equal(actual, expected, message) { assertions += 1; assert.deepStrictEqual(actual, expected, message); }

const result = runner.scenarioResult();
equal(result.type, runner.TYPE, 'type');
equal(result.version, runner.VERSION, 'version');
equal(result.status, 'BANK_INVENTORY_RECONCILIATION_PROVEN', 'status');
equal(result.mode, 'STATIC_REPOSITORY_SCHEMA_CENSUS_READ_ONLY', 'mode');
equal(runner.verifyResultHash(result), true, 'result hash');

equal(result.source_counts.total, 63, 'source count');
equal(result.source_counts.js, 45, 'JavaScript sources');
equal(result.source_counts.html, 15, 'HTML sources');
equal(result.source_counts.json, 3, 'JSON sources');
equal(result.source_counts.canonical_owner_chain, 5, 'canonical sources');
equal(result.source_counts.total, result.source_counts.js + result.source_counts.html + result.source_counts.json, 'extension total');
equal(result.source_counts.total, result.source_counts.canonical_owner_chain + result.source_counts.diagnostic_or_rehearsal + result.source_counts.historical_compatibility_or_auxiliary, 'role total');
equal(result.source_records.length, 63, 'source records');
equal(new Set(result.source_records.map(row => row.path)).size, 63, 'unique source paths');
equal(result.source_records.every(row => /^[0-9a-f]{64}$/.test(row.sha256)), true, 'source hashes');
equal(result.source_records.every(row => row.bytes > 0), true, 'nonempty sources');
equal(result.source_records.filter(row => row.role === 'CANONICAL_OWNER_CHAIN').map(row => row.path).sort(), runner.CANONICAL_SOURCES.slice().sort(), 'canonical source set');
check(/^[0-9a-f]{64}$/.test(result.source_catalog_sha256), 'catalog hash');

const governed = result.governed_local_storage;
equal(governed.bank_owner_keys, runner.BANK_KEYS, 'Bank keys');
equal(governed.continuous_run_requested_keys, runner.CONTINUOUS_RUN_KEYS, 'Continuous Run keys');
equal(governed.total, 9, 'nine governed keys');
equal(new Set([...governed.bank_owner_keys, ...governed.continuous_run_requested_keys]).size, 9, 'unique governed keys');

const schemas = result.declared_schemas;
equal(schemas.master_inventory.storage_key, 'pmp_master_bank_inventory_v1', 'master inventory key');
equal(schemas.master_inventory.type, 'PMP_MASTER_BANK_INVENTORY_V1', 'master type');
equal(schemas.master_inventory.owner, 'bank_screen_owner', 'master owner');
equal(schemas.master_inventory.top_level_fields.length, 6, 'master top fields');
equal(schemas.master_inventory.bank_entry_fields, ['name', 'records', 'references'], 'bank entry fields');
equal(schemas.master_inventory.canonical_banks.length, 13, 'canonical banks');
equal(schemas.master_inventory.canonical_banks.map(row => row.bank_id), Object.keys(runner.BANKS), 'bank IDs');
equal(schemas.master_inventory.record_required_fields.length, 12, 'record core fields');
equal(schemas.master_inventory.record_optional_fields, ['payload', 'payload_key', 'project_state_id'], 'record optional fields');
equal(schemas.master_inventory.reference_fields.length, 5, 'reference fields');
equal(schemas.helper_index.storage_key, 'pmp_helper_bank_index_v1', 'helper key');
equal(schemas.helper_index.item_fields.length, 8, 'helper fields');
equal(schemas.project_registry.storage_key, 'pmp_bank_project_registry_v1', 'project key');
equal(schemas.project_registry.type, 'BANK_PROJECT_REGISTRY_V1', 'project type');
equal(schemas.project_registry.project_fields.length, 7, 'project fields');
equal(schemas.project_registry.protected_seed_ids.length, 3, 'protected projects');
equal(schemas.continuous_run_state.storage_keys.length, 3, 'run state keys');
equal(schemas.continuous_run_state.type, 'PMP_UNIVERSAL_CONTINUOUS_WORK_ENGINE_STATE_V1', 'run type');
equal(schemas.continuous_run_state.legacy_type, 'PMP_PERSISTENT_CONTINUOUS_RUN_STATE_BANK_V1', 'run legacy type');
equal(schemas.continuous_run_state.owner, 'continuous_run_level_owner', 'run owner');
equal(schemas.continuous_run_state.compatibility_aliases_retained, true, 'run aliases');
equal(schemas.connections_deposit_index.storage_key, 'pmp_connections_bank_chat_memory_deposits_v1', 'deposit key');
equal(schemas.connections_deposit_index.top_level_fields_observed, ['records', 'categories', 'updated_at'], 'deposit shape');
equal(schemas.connections_deposit_index.binary_store.database, 'pmp_connections_bank_deposits_db_v1', 'deposit DB');
equal(schemas.connections_deposit_index.binary_store.object_store, 'deposits', 'deposit store');
equal(schemas.staging_transfer_store.manifest_key, 'pmp_continuous_run_bank_transfer_store_manifest_v1', 'transfer manifest');
equal(schemas.staging_transfer_store.receipt_key, 'pmp_continuous_run_bank_transfer_store_receipts_v1', 'transfer receipts');
equal(schemas.staging_transfer_store.binary_store.database, 'pmp_continuous_run_bank_transfer_store_db_v1', 'transfer DB');
equal(schemas.staging_transfer_store.binary_store.object_store, 'items', 'transfer store');
check(schemas.staging_transfer_store.status.includes('REQUIRES_P10_CONTRACT_CLASSIFICATION'), 'transfer classification pending');
equal(schemas.historic_inventory_output.keys.length, 3, 'historic inventory keys');
equal(schemas.historic_inventory_output.status, 'HISTORIC_READ_SCAN_OUTPUT_NOT_CANONICAL_INVENTORY', 'historic output status');

for (const [key, value] of Object.entries(result.reconciliation)) {
  if (['live_user_inventory_read', 'browser_launched', 'persisted_user_data_changed', 'storage_migration_performed'].includes(key)) equal(value, false, `negative reconciliation ${key}`);
  else if (key === 'canonical_owner_source_hashes') {
    equal(Object.keys(value).sort(), runner.CANONICAL_SOURCES.slice().sort(), 'canonical hashes keys');
    equal(Object.values(value).every(hash => /^[0-9a-f]{64}$/.test(hash)), true, 'canonical hashes values');
  } else equal(value, true, `reconciliation ${key}`);
}

equal(result.conflicts.length, 6, 'six reconciliation findings');
equal(new Set(result.conflicts.map(row => row.id)).size, 6, 'unique findings');
equal(result.conflicts.slice(0, 5).every(row => row.required_resolution === 'P10-U2'), true, 'contract findings route to U2');
check(result.conflicts[5].required_resolution.includes('P10-U3'), 'live data boundary routes forward');
equal(result.policy.canonical_inventory_key, 'pmp_master_bank_inventory_v1', 'canonical key policy');
equal(result.policy.canonical_inventory_owner, 'bank_screen_owner', 'canonical owner policy');
equal(result.policy.unknown_or_orphan_policy, 'QUARANTINE_PRESERVE_EXACT_BYTES_NEVER_SILENTLY_DELETE', 'orphan policy');
equal(result.policy.historic_namespace_policy, 'CLASSIFY_AND_REFERENCE_NEVER_SILENTLY_MERGE', 'historic policy');
equal(result.policy.p10_u1_live_data_access, 'FORBIDDEN_AND_NOT_PERFORMED', 'live data policy');
equal(result.policy.p10_u1_writes, 'NONE', 'write policy');

equal(result.next_step.id, 'P10-U2', 'next step');
check(result.next_step.objective.includes('identity'), 'next identity');
check(result.next_step.objective.includes('provenance'), 'next provenance');
check(result.next_step.objective.includes('no-deletion'), 'next no deletion');
equal(result.next_step.requires_user_app_check, false, 'no app check');
equal(result.next_step.requires_new_explicit_authority, false, 'no new authority');
equal(result.next_step.persisted_user_data_change_allowed, false, 'no data change');
equal(result.next_step.storage_migration_allowed, false, 'no migration');
equal(result.next_step.stop_after, false, 'continue');
for (const [key, value] of Object.entries(result.effects)) equal(value, false, `effect ${key}`);
check(result.claim_ceiling.includes('does not inspect live user records'), 'no live records');
check(result.claim_ceiling.includes('change the Bank tab'), 'no Bank tab change');
check(result.claim_ceiling.includes('perform an observation'), 'no observation');
check(result.claim_ceiling.includes('formal proof'), 'no formal proof');

console.log(`PASS: P10-U1 Bank inventory and schema reconciliation (${assertions}/${assertions})`);
