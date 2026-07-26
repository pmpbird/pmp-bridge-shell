#!/usr/bin/env node
'use strict';

const runner = require('./run_pass10_unit2_bank_inventory_contract_v1.js');

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

const contract = runner.policy();
equal(contract.contract_version, runner.CONTRACT_VERSION, 'contract version');
equal(contract.item_version, runner.ITEM_VERSION, 'item version');
equal(contract.model, 'OWNER_FACTS_TO_READ_ONLY_CANONICAL_PROJECTION_FAIL_CLOSED', 'contract model');
equal(contract.canonical_inventory.storage_key, 'pmp_master_bank_inventory_v1', 'canonical key');
equal(contract.canonical_inventory.owner_id, runner.BANK_OWNER, 'canonical owner');
equal(contract.canonical_inventory.identity_algorithm, 'SHA-256', 'identity algorithm');
equal(contract.canonical_inventory.identity_preimage_fields.length, 4, 'identity preimage fields');
equal(new Set(contract.canonical_inventory.identity_preimage_fields).size, 4, 'identity fields unique');
equal(contract.canonical_inventory.canonical_id_prefix, 'bank-item:v1:', 'canonical prefix');
equal(contract.canonical_inventory.missing_identity_prefix, 'bank-quarantine:v1:', 'quarantine prefix');
equal(contract.canonical_inventory.native_identity_preserved, true, 'native identity preserved');
equal(contract.canonical_inventory.payload_exact_bytes_preserved, true, 'payload bytes preserved');
equal(contract.canonical_inventory.bank_ids, runner.CANONICAL_BANKS, 'canonical banks');
equal(contract.canonical_inventory.bank_ids.length, 13, '13 banks');
equal(new Set(contract.canonical_inventory.bank_ids).size, 13, 'bank IDs unique');
equal(contract.required_source_fields.length, 9, 'required source fields');
equal(new Set(contract.required_source_fields).size, 9, 'source fields unique');
equal(contract.canonical_item_fields.length, 18, 'canonical item fields');
equal(new Set(contract.canonical_item_fields).size, 18, 'item fields unique');
equal(contract.namespace_rules.length, 16, 'namespace rules');
equal(new Set(contract.namespace_rules.map(row => `${row.storage_kind}:${row.namespace}`)).size, 16, 'namespace rules unique');
equal(contract.namespace_rules.filter(row => row.classification === 'HISTORIC_REFERENCE_ONLY').length, 3, 'historic namespaces');
equal(contract.namespace_rules.filter(row => row.classification === 'AUXILIARY_READ_ONLY_UNTIL_OWNER_UPDATE').length, 3, 'auxiliary namespaces');
equal(contract.namespace_rules.filter(row => row.owner_id === runner.RUN_OWNER).length, 8, 'Continuous Run namespaces');
equal(contract.namespace_rules.filter(row => row.owner_id === runner.BANK_OWNER).length, 5, 'Bank namespaces');
equal(contract.quarantine.reasons.length, 15, 'quarantine reasons');
equal(new Set(contract.quarantine.reasons).size, 15, 'quarantine reasons unique');
equal(contract.quarantine.policy, 'PRESERVE_EXACT_BYTES_NEVER_SILENTLY_DELETE', 'quarantine preservation');
equal(contract.quarantine.collision, 'QUARANTINE_ALL_COLLIDING_ITEMS_PRESERVE_EACH_PAYLOAD', 'collision policy');
equal(contract.quarantine.unknown, 'QUARANTINE', 'unknown policy');
equal(contract.quarantine.orphan, 'QUARANTINE', 'orphan policy');
equal(contract.quarantine.corrupt, 'QUARANTINE', 'corrupt policy');
equal(contract.quarantine.unavailable, 'PRESERVE_INDEX_FACT_AND_MARK_UNAVAILABLE', 'unavailable policy');
equal(contract.quarantine.stale, 'PRESERVE_AND_MARK_STALE', 'stale policy');
equal(contract.states.length, 8, 'states');
equal(new Set(contract.states).size, 8, 'states unique');
for (const state of ['ACTIVE', 'REFERENCE_ONLY', 'ORPHANED', 'STALE', 'UNAVAILABLE', 'CORRUPT', 'QUARANTINED']) {
  check(contract.states.includes(state), `${state} supported`);
}
equal(contract.delete_contract.default, 'DENY', 'delete default deny');
equal(contract.delete_contract.bank_tab_delete_api, 'FORBIDDEN', 'Bank tab delete forbidden');
equal(contract.delete_contract.quarantine_auto_delete, false, 'no quarantine auto-delete');
equal(contract.delete_contract.historic_auto_delete, false, 'no historic auto-delete');
equal(contract.delete_contract.unavailable_auto_delete, false, 'no unavailable auto-delete');
equal(contract.delete_contract.stale_auto_delete, false, 'no stale auto-delete');
equal(contract.delete_contract.exact_user_confirmation_required, true, 'confirmation required');
equal(contract.delete_contract.exact_owner_capability_required, true, 'owner capability required');
equal(contract.delete_contract.exact_expected_version_required, true, 'version required');
equal(contract.delete_contract.exact_payload_sha256_required, true, 'hash required');
equal(contract.delete_contract.append_only_receipt_required, true, 'receipt required');
equal(contract.delete_contract.production_delete_enabled_in_p10_u2, false, 'delete disabled');
equal(contract.compatibility.legacy_aliases_are_source_native_references, true, 'aliases native references');
equal(contract.compatibility.aliases_convey_authority, false, 'aliases no authority');
equal(contract.compatibility.adapters_are_pure_and_read_only, true, 'read-only adapters');
equal(contract.compatibility.active_tab_conveys_authority, false, 'tab no authority');
equal(contract.compatibility.helper_registration_conveys_bank_authority, false, 'helper registration no authority');
equal(contract.compatibility.historic_inventory_is_canonical, false, 'historic not canonical');
equal(contract.compatibility.silent_alias_merge, 'FORBIDDEN', 'no silent alias merge');
equal(contract.compatibility.silent_schema_upgrade, 'FORBIDDEN', 'no silent schema upgrade');
equal(contract.compatibility.storage_migration, 'FORBIDDEN_IN_P10_U2_THROUGH_P10_U5', 'no migration');
equal(contract.representation_contract.projection_mode, 'READ_ONLY_OWNER_FACTS', 'projection mode');
equal(contract.representation_contract.enumerate_only_declared_namespaces, false, 'unknown namespaces enumerated');
equal(contract.representation_contract.unknown_namespaces_visible_as_quarantine, true, 'unknown visible');
equal(contract.representation_contract.raw_payload_exposed_to_ui, false, 'raw payload hidden');
equal(contract.representation_contract.write_api_exposed_to_ui, false, 'no write API');
equal(contract.representation_contract.delete_api_exposed_to_ui, false, 'no delete API');
equal(contract.representation_contract.migration_api_exposed_to_ui, false, 'no migration API');
equal(contract.representation_contract.recurring_polling_required, false, 'no polling');
equal(contract.representation_contract.owner_event_updates_only, true, 'owner events only');

function result(inputs) {
  const value = runner.reconcileInventory(inputs, contract);
  check(runner.verifyResultHash(value), 'result hash valid');
  check(Object.values(value.effects).every(flag => flag === false), 'zero effects');
  return value;
}
function item(overrides = {}) {
  return runner.normalizeItem(runner.sampleInput(overrides), contract);
}

const empty = result([]);
equal(empty.type, runner.RESULT_TYPE, 'result type');
equal(empty.version, '1.0.0', 'result version');
equal(empty.status, 'PASS', 'result status');
equal(empty.summary.items, 0, 'empty items');
equal(empty.summary.identities, 0, 'empty identities');
equal(empty.items, [], 'empty entries');
check(empty.claim_ceiling.includes('reads no live storage'), 'claim ceiling live storage');
check(empty.claim_ceiling.includes('mutates no user data'), 'claim ceiling data');
check(empty.claim_ceiling.includes('consumes no formal proof'), 'claim ceiling proof');

const canonical = item();
equal(Object.keys(canonical).sort(), contract.canonical_item_fields.slice().sort(), 'exact item fields');
equal(canonical.item_version, runner.ITEM_VERSION, 'canonical item version');
check(canonical.canonical_id.startsWith('bank-item:v1:'), 'canonical ID prefix');
equal(canonical.canonical_id.length, 'bank-item:v1:'.length + 64, 'canonical ID length');
equal(canonical.source_native_id, 'record:sample:001', 'native ID preserved');
equal(canonical.source_namespace, 'pmp_master_bank_inventory_v1', 'namespace preserved');
equal(canonical.source_storage_kind, 'LOCAL_STORAGE', 'storage kind preserved');
equal(canonical.owning_bank, 'master', 'bank preserved');
equal(canonical.owner_id, runner.BANK_OWNER, 'owner preserved');
equal(canonical.schema_type, 'PMP_MASTER_BANK_INVENTORY_V1', 'schema preserved');
equal(canonical.schema_version, '1.0.0', 'schema version preserved');
equal(canonical.payload_sha256, runner.sha256('{"sample":true}'), 'payload hash');
equal(canonical.payload_bytes, Buffer.byteLength('{"sample":true}'), 'payload bytes');
equal(Buffer.from(canonical.raw_bytes_base64, 'base64').toString(), '{"sample":true}', 'exact bytes round trip');
equal(canonical.compatibility_aliases, [], 'aliases preserved');
equal(canonical.namespace_classification, 'CANONICAL_INDEX', 'canonical classification');
equal(canonical.state, 'ACTIVE', 'canonical active');
equal(canonical.quarantine_reasons, [], 'canonical no quarantine');
equal(canonical.write_authority, 'BANK_OWNER_RECEIPTED_REQUEST_ONLY', 'write authority');
equal(canonical.delete_authority, 'DENY_BY_DEFAULT_EXACT_OWNER_CAPABILITY_AND_CONFIRMATION_REQUIRED', 'delete authority');

equal(runner.canonicalIdentity(runner.sampleInput(), contract), canonical.canonical_id, 'identity deterministic');
equal(runner.canonicalIdentity(runner.sampleInput({raw_bytes: 'different'}), contract), canonical.canonical_id, 'identity independent of payload');
check(runner.canonicalIdentity(runner.sampleInput({source_native_id: 'record:sample:002'}), contract) !== canonical.canonical_id, 'native ID changes identity');
check(runner.canonicalIdentity(runner.sampleInput({source_namespace: 'pmp_helper_bank_index_v1'}), contract) !== canonical.canonical_id, 'namespace changes identity');
check(runner.canonicalIdentity(runner.sampleInput({source_storage_kind: 'INDEXED_DB'}), contract) !== canonical.canonical_id, 'storage kind changes identity');

const aliases = item({compatibility_aliases: ['legacy-record-1', 'PMP_PERSISTENT_CONTINUOUS_RUN_STATE_BANK_V1']});
equal(aliases.compatibility_aliases, ['legacy-record-1', 'PMP_PERSISTENT_CONTINUOUS_RUN_STATE_BANK_V1'], 'aliases exact');
equal(aliases.state, 'ACTIVE', 'aliases do not quarantine');

const runItem = item({
  source_namespace: 'pmp_continuous_run_state_bank_v1',
  source_native_id: 'run:primary',
  owning_bank: 'continuous_run',
  owner_id: runner.RUN_OWNER,
  schema_type: 'PMP_UNIVERSAL_CONTINUOUS_WORK_ENGINE_STATE_V1'
});
equal(runItem.namespace_classification, 'CONTINUOUS_RUN_OWNER_FACT', 'run fact classification');
equal(runItem.write_authority, 'CONTINUOUS_RUN_REQUEST_BANK_OWNER_COMMIT', 'run owner commit route');
equal(runItem.state, 'ACTIVE', 'run active');

const historic = item({
  source_namespace: 'pmp_connection_bank_inventory_v1',
  source_native_id: 'historic:inventory',
  owning_bank: 'connections',
  owner_id: 'historic_connection_inventory',
  schema_type: 'PMP_HISTORIC_CONNECTION_BANK_INVENTORY_V1'
});
equal(historic.namespace_classification, 'HISTORIC_REFERENCE_ONLY', 'historic classification');
equal(historic.state, 'REFERENCE_ONLY', 'historic state');
equal(historic.write_authority, 'NONE', 'historic no write');

const auxiliary = item({
  source_namespace: 'pmp_continuous_run_bank_transfer_store_manifest_v1',
  source_native_id: 'transfer:manifest',
  owning_bank: 'continuous_run',
  owner_id: runner.RUN_OWNER,
  schema_type: 'PMP_UNIVERSAL_CONTINUOUS_WORK_ENGINE_STATE_V1'
});
equal(auxiliary.namespace_classification, 'AUXILIARY_READ_ONLY_UNTIL_OWNER_UPDATE', 'auxiliary classification');
equal(auxiliary.write_authority, 'NO_CANONICAL_WRITE_UNTIL_P10_U4', 'auxiliary write denied until U4');

const binary = item({
  source_storage_kind: 'INDEXED_DB',
  source_namespace: 'pmp_connections_bank_deposits_db_v1/deposits',
  source_native_id: 'deposit:001',
  owning_bank: 'connections',
  owner_id: runner.BANK_OWNER,
  schema_type: 'PMP_BANK_BINARY_PAYLOAD_V1',
  raw_bytes: Buffer.from([0, 1, 2, 255])
});
equal(binary.namespace_classification, 'OWNER_GOVERNED_BINARY_PAYLOAD', 'binary classification');
equal(binary.payload_bytes, 4, 'binary byte length');
equal(Buffer.from(binary.raw_bytes_base64, 'base64'), Buffer.from([0, 1, 2, 255]), 'binary exact bytes');
equal(binary.state, 'ACTIVE', 'binary active');

const missingBinary = item({
  source_storage_kind: 'INDEXED_DB',
  source_namespace: 'pmp_connections_bank_deposits_db_v1/deposits',
  source_native_id: 'deposit:empty',
  owning_bank: 'connections',
  owner_id: runner.BANK_OWNER,
  schema_type: 'PMP_BANK_BINARY_PAYLOAD_V1',
  raw_bytes: ''
});
equal(missingBinary.state, 'QUARANTINED', 'missing binary quarantined');
check(missingBinary.quarantine_reasons.includes('MISSING_BINARY_PAYLOAD'), 'missing binary reason');

const unknownNamespace = item({source_namespace: 'unknown_storage_key'});
equal(unknownNamespace.state, 'QUARANTINED', 'unknown namespace quarantined');
equal(unknownNamespace.namespace_classification, 'UNKNOWN_NAMESPACE', 'unknown classification');
equal(unknownNamespace.write_authority, 'NONE', 'unknown no write');
check(unknownNamespace.quarantine_reasons.includes('UNKNOWN_NAMESPACE'), 'unknown namespace reason');
check(unknownNamespace.quarantine_reasons.includes('UNKNOWN_OWNER'), 'unknown owner rule reason');

const unknownBank = item({owning_bank: 'not_a_bank'});
equal(unknownBank.state, 'QUARANTINED', 'unknown bank quarantined');
check(unknownBank.quarantine_reasons.includes('UNKNOWN_OWNING_BANK'), 'unknown bank reason');

const wrongOwner = item({owner_id: runner.RUN_OWNER});
equal(wrongOwner.state, 'QUARANTINED', 'wrong owner quarantined');
check(wrongOwner.quarantine_reasons.includes('UNKNOWN_OWNER'), 'wrong owner reason');

const unknownType = item({schema_type: 'NEW_UNDECLARED_SCHEMA'});
equal(unknownType.state, 'QUARANTINED', 'unknown schema quarantined');
check(unknownType.quarantine_reasons.includes('UNKNOWN_SCHEMA_TYPE'), 'unknown schema reason');

const unknownVersion = item({schema_version: '99'});
equal(unknownVersion.state, 'QUARANTINED', 'unknown version quarantined');
check(unknownVersion.quarantine_reasons.includes('UNKNOWN_SCHEMA_VERSION'), 'unknown version reason');

const hashMismatch = item({declared_payload_sha256: 'f'.repeat(64)});
equal(hashMismatch.state, 'QUARANTINED', 'hash mismatch quarantined');
check(hashMismatch.quarantine_reasons.includes('PAYLOAD_HASH_MISMATCH'), 'hash mismatch reason');

const badAlias = item({compatibility_aliases: ['valid', '']});
equal(badAlias.state, 'QUARANTINED', 'bad alias quarantined');
check(badAlias.quarantine_reasons.includes('MALFORMED_COMPATIBILITY_ALIAS'), 'bad alias reason');

const unavailable = item({source_available: false});
equal(unavailable.state, 'UNAVAILABLE', 'unavailable state');
equal(unavailable.raw_bytes_base64, canonical.raw_bytes_base64, 'unavailable bytes preserved');
check(unavailable.quarantine_reasons.includes('SOURCE_UNAVAILABLE'), 'unavailable reason');

const stale = item({stale: true});
equal(stale.state, 'STALE', 'stale state');
equal(stale.raw_bytes_base64, canonical.raw_bytes_base64, 'stale bytes preserved');
check(stale.quarantine_reasons.includes('STALE_SOURCE'), 'stale reason');

const orphaned = item({orphaned: true});
equal(orphaned.state, 'QUARANTINED', 'orphan quarantined');
check(orphaned.quarantine_reasons.includes('ORPHANED_OWNER'), 'orphan reason');
equal(orphaned.raw_bytes_base64, canonical.raw_bytes_base64, 'orphan bytes preserved');

const corrupt = item({corrupt: true});
equal(corrupt.state, 'QUARANTINED', 'corrupt quarantined');
check(corrupt.quarantine_reasons.includes('CORRUPT_RECORD'), 'corrupt reason');
equal(corrupt.raw_bytes_base64, canonical.raw_bytes_base64, 'corrupt bytes preserved');

const missingId = item({source_native_id: ''});
equal(missingId.state, 'QUARANTINED', 'missing ID quarantined');
check(missingId.canonical_id.startsWith('bank-quarantine:v1:'), 'missing ID quarantine identity');
check(missingId.quarantine_reasons.includes('MISSING_NATIVE_ID'), 'missing ID reason');
equal(missingId.canonical_id, item({source_native_id: ''}).canonical_id, 'missing ID identity deterministic');

const missingFieldsSource = runner.sampleInput();
delete missingFieldsSource.schema_version;
delete missingFieldsSource.compatibility_aliases;
const missingFields = runner.normalizeItem(missingFieldsSource, contract);
equal(missingFields.state, 'QUARANTINED', 'missing fields quarantined');
check(missingFields.quarantine_reasons.includes('MISSING_REQUIRED_FIELD'), 'missing fields reason');
check(missingFields.quarantine_reasons.includes('UNKNOWN_SCHEMA_VERSION'), 'missing schema version reason');
check(missingFields.quarantine_reasons.includes('MALFORMED_COMPATIBILITY_ALIAS'), 'missing aliases reason');

const collisionInputs = [
  runner.sampleInput({raw_bytes: 'first'}),
  runner.sampleInput({raw_bytes: 'second'})
];
const collision = result(collisionInputs);
equal(collision.summary.items, 2, 'collision item count');
equal(collision.summary.identities, 1, 'collision single identity');
equal(collision.summary.quarantined, 2, 'both collision rows quarantined');
equal(collision.items.every(row => row.quarantine_reasons.includes('IDENTITY_COLLISION')), true, 'collision reason on both');
equal(collision.items.map(row => Buffer.from(row.raw_bytes_base64, 'base64').toString()), ['first', 'second'], 'collision bytes both preserved');

const samePayloadDuplicate = result([
  runner.sampleInput({raw_bytes: 'same'}),
  runner.sampleInput({raw_bytes: 'same'})
]);
equal(samePayloadDuplicate.summary.identities, 1, 'same payload duplicate identity');
equal(samePayloadDuplicate.summary.quarantined, 0, 'same payload duplicate not collision');
equal(samePayloadDuplicate.summary.active, 2, 'same payload preserved as two source facts');

const matrix = result([
  runner.sampleInput(),
  runner.sampleInput({
    source_namespace: 'pmp_connection_bank_inventory_v1',
    source_native_id: 'historic:1',
    owning_bank: 'connections',
    owner_id: 'historic_connection_inventory',
    schema_type: 'PMP_HISTORIC_CONNECTION_BANK_INVENTORY_V1'
  }),
  runner.sampleInput({source_native_id: 'stale:1', stale: true}),
  runner.sampleInput({source_native_id: 'unavailable:1', source_available: false}),
  runner.sampleInput({source_native_id: 'orphan:1', orphaned: true}),
  runner.sampleInput({source_native_id: 'corrupt:1', corrupt: true}),
  runner.sampleInput({source_native_id: 'unknown:1', source_namespace: 'unknown'})
]);
equal(matrix.summary.items, 7, 'matrix items');
equal(matrix.summary.active, 1, 'matrix active');
equal(matrix.summary.reference_only, 1, 'matrix reference');
equal(matrix.summary.stale, 1, 'matrix stale');
equal(matrix.summary.unavailable, 1, 'matrix unavailable');
equal(matrix.summary.quarantined, 3, 'matrix quarantined');
equal(matrix.summary.orphaned, 0, 'orphan promoted to quarantine');
equal(matrix.summary.corrupt, 0, 'corrupt promoted to quarantine');
equal(matrix.summary.exact_payload_bytes_preserved, matrix.items.reduce((sum, row) => sum + row.payload_bytes, 0), 'matrix bytes total');

const deterministicInputs = [
  runner.sampleInput(),
  runner.sampleInput({source_native_id: 'deterministic:2', stale: true})
];
equal(runner.reconcileInventory(deterministicInputs, contract), runner.reconcileInventory(deterministicInputs, contract), 'deterministic reconciliation');
const tampered = runner.reconcileInventory(deterministicInputs, contract);
tampered.summary.active = 99;
equal(runner.verifyResultHash(tampered), false, 'tampered result rejected');

console.log(`PASS: P10-U2 Bank inventory contract (${assertions}/${assertions})`);
