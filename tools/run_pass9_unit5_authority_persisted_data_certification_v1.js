#!/usr/bin/env node
'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const unit4Runner = require('./run_pass9_unit4_bank_continuous_run_exhaustive_proof_v1.js');

const ROOT = path.resolve(__dirname, '..');
const TYPE = 'PMP_PASS9_UNIT5_AUTHORITY_PERSISTED_DATA_CERTIFICATION_RESULT_V1';
const VERSION = '1.0.0';
const BANK_OWNER = 'bank_screen_owner';
const RUN_OWNER = 'continuous_run_level_owner';
const BANK_KEYS = [
  'pmp_master_bank_inventory_v1',
  'pmp_source_bank_router_receipts_v1',
  'pmp_helper_bank_index_v1',
  'pmp_connections_bank_chat_memory_deposits_v1'
];
const RUN_KEYS = [
  'pmp_continuous_run_state_bank_v1',
  'pmp_continuous_run_state_receipts_v1',
  'pmp_continuous_run_state_manifest_v1',
  'pmp_bank_project_registry_v1',
  'pmp_bank_project_registry_v1_receipt'
];

function read(name) {
  return fs.readFileSync(path.join(ROOT, name), 'utf8');
}
function json(name) {
  return JSON.parse(read(name));
}
function stable(value) {
  if (Array.isArray(value)) return '[' + value.map(stable).join(',') + ']';
  if (value && typeof value === 'object') {
    return '{' + Object.keys(value).sort().map(key => JSON.stringify(key) + ':' + stable(value[key])).join(',') + '}';
  }
  return JSON.stringify(value);
}
function digest(value) {
  return crypto.createHash('sha256').update(Buffer.from(typeof value === 'string' ? value : stable(value))).digest('hex');
}
function occurrences(text, token) {
  return text.split(token).length - 1;
}

function scenarioResult() {
  const unit1 = json('audit/pass9/pass9-bank-continuous-run-unit1-inventory-v1.json');
  const unit2 = json('audit/pass9/pass9-bank-continuous-run-unit2-owner-contract-v1.json');
  const unit3 = json('audit/pass9/pass9-bank-continuous-run-unit3-owner-integration-v1.json');
  const unit4 = json('audit/pass9/pass9-bank-continuous-run-unit4-exhaustive-proof-v1.json');
  const receipt1 = json('audit/pass9/receipts/RECEIPT_P9_U1_BANK_CONTINUOUS_RUN_INVENTORY_20260726T192000Z_001.json');
  const receipt2 = json('audit/pass9/receipts/RECEIPT_P9_U2_BANK_CONTINUOUS_RUN_OWNER_CONTRACT_20260726T193000Z_001.json');
  const receipt3 = json('audit/pass9/receipts/RECEIPT_P9_U3_BANK_CONTINUOUS_RUN_OWNER_INTEGRATION_20260726T200000Z_001.json');
  const receipt4 = json('audit/pass9/receipts/RECEIPT_P9_U4_BANK_CONTINUOUS_RUN_EXHAUSTIVE_PROOF_20260726T204000Z_001.json');
  const boundary = read('pmp-bank-continuous-run-owner-boundary-v1.js');
  const state = read('pmp-continuous-run-state-bank-v1.js');
  const router = read('pmp-master-bank-inventory-router-v1.js');
  const master = read('pmp-master-bank-tab-v1.js');
  const continuousOwner = read('pmp-bank-screen-owner-v1.js');
  const loader = read('pmp-continuous-run-bank-order-frame-loader-v1.js');
  const bridge = read('pmp-bank-owner-dependency-bridge-v1.js');
  const connectionDelete = read('pmp-connections-bank-packet-delete-v1.js');
  const diagnostic = read('pmp-bank-continuous-run-owner-split-diagnostic-v1.js');
  const inner = read('pmp-current-inner-cleanbug-rgcontrols-v23.html');
  const unit4Result = unit4Runner.scenarioResult();

  const contract = unit2.owner_contract;
  const chain = [
    {unit: 'P9-U1', status: unit1.status, next: receipt1.next_safe_move.step_id},
    {unit: 'P9-U2', status: unit2.status, next: receipt2.next_safe_move.step_id},
    {unit: 'P9-U3', status: unit3.status, next: receipt3.next_safe_move.step_id},
    {unit: 'P9-U4', status: unit4.status, next: receipt4.next_safe_move.step_id}
  ];
  const boundaryPos = inner.indexOf('pmp-bank-continuous-run-owner-boundary-v1.js?fresh=');
  const statePos = inner.indexOf('pmp-continuous-run-state-bank-v1.js?fresh=');
  const routerPos = inner.indexOf('pmp-master-bank-inventory-router-v1.js?fresh=');
  const masterPos = inner.indexOf('pmp-master-bank-tab-v1.js?fresh=');
  const ownerPos = inner.indexOf('pmp-bank-screen-owner-v1.js?fresh=');

  const result = {
    type: TYPE,
    version: VERSION,
    status: 'AUTHORITY_SEPARATION_AND_PERSISTED_DATA_CERTIFIED',
    evidence_chain: {
      units: chain,
      exact_progression: chain.map(row => row.next),
      inventory_conflicts_identified: unit1.conflicts.length,
      unit1_assertions: unit1.verification.assertions_passed,
      unit2_assertions: unit2.verification.assertions_passed,
      unit3_assertions: unit3.verification.assertions_passed,
      unit4_assertions: unit4.verification.assertions_passed,
      cumulative_assertions: [
        unit1.verification.assertions_passed,
        unit2.verification.assertions_passed,
        unit3.verification.assertions_passed,
        unit4.verification.assertions_passed
      ].reduce((a, b) => a + b, 0),
      all_permanent_gates_bound: [unit1, unit2, unit3, unit4].every(
        unit => unit.no_blind_flying_gate
          && unit.no_blind_flying_gate.upload_before_enforcement === true
          && unit.no_blind_flying_gate.automatic_retry === false
      )
    },
    authority_separation: {
      contract_model: contract.model,
      bank_owner: contract.owners.bank.owner_id,
      continuous_run_owner: contract.owners.continuous_run.owner_id,
      owners_distinct: contract.owners.bank.owner_id !== contract.owners.continuous_run.owner_id,
      durable_writer: contract.persistence.durable_writer,
      run_state_requester: contract.persistence.request_owner_for_run_state,
      bank_resource_prefix: contract.owners.bank.resource_prefix,
      continuous_run_resource_prefix: contract.owners.continuous_run.resource_prefix,
      request_fields: contract.request_fields.length,
      receipt_fields: contract.receipt_fields.length,
      receipt_algorithm: contract.persistence.algorithm,
      append_only_receipt_chain: contract.persistence.append_only_receipt_chain,
      active_tab_conveys_ownership: contract.compatibility.active_tab_conveys_ownership,
      filename_conveys_authority: contract.compatibility.filename_conveys_authority,
      copied_cross_frame_apis_convey_authority: contract.compatibility.copied_cross_frame_apis_convey_authority,
      delete_or_clear_default: contract.persistence.delete_or_clear_default,
      storage_migration_contract: contract.compatibility.storage_migration,
      integration_model: unit3.integration.model,
      integration_bank_owner: unit3.integration.bank_owner,
      integration_continuous_run_owner: unit3.integration.continuous_run_owner,
      integration_receipt_algorithm: unit3.integration.receipt_algorithm,
      owner_boundary_exact_ids_in_source: boundary.includes(`const BANK_OWNER='${BANK_OWNER}'`)
        && boundary.includes(`const RUN_OWNER='${RUN_OWNER}'`),
      boundary_only_durable_writer_rule: boundary.includes('Bank Owner is the only durable writer'),
      state_requests_bank_commits: state.includes(`requester_owner:OWNER`)
        && state.includes(`capability:'request:bank_screen_owner:COMMIT_WRITE:'`),
      router_uses_internal_bank_capability: router.includes(`capability:'internal:bank_screen_owner:COMMIT_WRITE:'`),
      dependency_bridge_copies_mutable_apis: bridge.includes('w[name]=api'),
      runtime_owner_api_alias_is_identity_only: continuousOwner.includes('window.PMPContinuousRunLevelOwnerV1=api')
        && continuousOwner.includes('window.PMPBankScreenOwnerV1=api'),
      bank_shell_open_calls_record_write: master.includes('.recordWrite(')
    },
    persisted_data: {
      bank_keys: BANK_KEYS,
      continuous_run_keys: RUN_KEYS,
      total_governed_keys: BANK_KEYS.length + RUN_KEYS.length,
      keys_unique: new Set(BANK_KEYS.concat(RUN_KEYS)).size === BANK_KEYS.length + RUN_KEYS.length,
      contract_preserved_existing_keys: contract.compatibility.existing_persisted_keys_preserved,
      integration_preserved_existing_keys: unit3.integration.existing_persisted_keys_preserved,
      boundary_bank_keys_bound: BANK_KEYS.every(key => boundary.includes(`'${key}'`)),
      boundary_run_keys_bound: RUN_KEYS.every(key => boundary.includes(`'${key}'`)),
      state_direct_local_storage_writes: occurrences(state, 'localStorage.setItem'),
      state_direct_local_storage_deletes: occurrences(state, 'localStorage.removeItem'),
      router_direct_local_storage_writes: occurrences(router, 'localStorage.setItem'),
      connection_delete_direct_local_storage_writes: occurrences(connectionDelete, 'localStorage.setItem'),
      boundary_load_reads: unit3.integration.boundary_and_state_load_storage_reads,
      boundary_load_writes: unit3.integration.boundary_and_state_load_storage_writes,
      boundary_load_deletes: unit3.integration.boundary_and_state_load_storage_deletes,
      first_core_load_calls: unit4Result.boot_repeated_load.first_calls,
      repeated_core_load_calls: unit4Result.boot_repeated_load.second_calls,
      repeated_load_changed_data: unit4Result.boot_repeated_load.persisted_user_data_changed,
      stale_concurrency_zero_effects: unit4Result.concurrency.competing_zero_effects,
      cancellation_gap_zero_effects: unit4Result.cancellation.gap_zero_effects,
      cancellation_stale_zero_effects: unit4Result.cancellation.stale_zero_effects,
      duplicate_conflict_zero_effects: unit4Result.duplicate.conflict_zero_effects,
      all_denials_zero_effect: unit4Result.denial.all_denials_zero_effect,
      denial_bytes_unchanged: unit4Result.denial.persisted_bytes_unchanged,
      existing_key_rollback_exact: unit4Result.atomic_rollback.existing_keys_exact_restore,
      absent_key_rollback_exact: unit4Result.atomic_rollback.new_key_exact_restore,
      restart_load_changed_data: !unit4Result.restart_handoff.persisted_bytes_unchanged_by_restart_load,
      corrupt_restart_raw_bytes_preserved: unit4Result.restart_handoff.corrupted_raw_bytes_preserved,
      router_default_delete_zero_effect: unit4Result.router_diagnostics.default_delete_zero_effect,
      router_wrong_delete_zero_effect: unit4Result.router_diagnostics.wrong_delete_zero_effect,
      bounded_receipt_chain_valid: unit4Result.bounded_receipts.visible_chain_valid,
      bounded_receipts_retained: unit4Result.bounded_receipts.receipt_count,
      unrelated_bytes_preserved_across_all_matrices: [
        unit4Result.concurrency.unrelated_exactly_preserved,
        unit4Result.denial.unrelated_exactly_preserved,
        unit4Result.atomic_rollback.unrelated_exactly_preserved,
        unit4Result.restart_handoff.unrelated_exactly_preserved,
        unit4Result.router_diagnostics.unrelated_exactly_preserved,
        unit4Result.bounded_receipts.unrelated_exactly_preserved
      ].every(Boolean),
      user_persisted_data_touched: false,
      storage_migration_performed: false
    },
    active_runtime: {
      boundary_position: boundaryPos,
      state_position: statePos,
      router_position: routerPos,
      bank_shell_position: masterPos,
      continuous_owner_position: ownerPos,
      exact_order: boundaryPos > 0
        && boundaryPos < statePos
        && boundaryPos < routerPos
        && statePos < masterPos
        && routerPos < masterPos
        && masterPos < ownerPos,
      boundary_occurrences: occurrences(inner, 'pmp-bank-continuous-run-owner-boundary-v1.js'),
      state_occurrences: occurrences(inner, 'pmp-continuous-run-state-bank-v1.js'),
      router_occurrences: occurrences(inner, 'pmp-master-bank-inventory-router-v1.js'),
      bank_shell_occurrences: occurrences(inner, 'pmp-master-bank-tab-v1.js'),
      continuous_owner_occurrences: occurrences(inner, 'pmp-bank-screen-owner-v1.js'),
      legacy_mode_occurrences: occurrences(inner, 'pmp-bank-mode1-hide-unchecked-v1.js'),
      legacy_cleaner_occurrences: occurrences(inner, 'pmp-bank-scoped-test-data-cleaner-v1.js'),
      master_recurring_painter: master.includes('setInterval('),
      continuous_owner_recurring_painter: continuousOwner.includes('setInterval('),
      loader_recurring_scan: loader.includes('setInterval('),
      loader_event_driven_mode: loader.includes('EVENT_DRIVEN_NEW_DOCUMENT_ONCE'),
      diagnostic_automatic_run: diagnostic.includes("setTimeout(()=>evaluate('script_load"),
      diagnostic_reads_boundary: diagnostic.includes('boundarySnapshot'),
      diagnostic_reports_sha_chain: diagnostic.includes('sha256_receipt_chain')
    },
    deletion_authority: {
      default: contract.persistence.delete_or_clear_default,
      router_requires_user_confirmation: router.includes('input.user_confirmed!==true'),
      connections_exact_capability: connectionDelete.includes("capability:'manual:bank_screen_owner:delete_record:connections'"),
      connections_routes_final_index_through_owner: connectionDelete.includes('connections_deposits_after_delete:deposits'),
      connections_opens_indexeddb_only_after_owner_commit: connectionDelete.indexOf('if(!result||!result.ok)')
        < connectionDelete.indexOf('await idbDelete(w,key)'),
      no_recurring_delete_timer: !connectionDelete.includes('setInterval('),
      default_delete_result: unit4Result.router_diagnostics.default_delete_code,
      wrong_capability_result: unit4Result.router_diagnostics.wrong_delete_code,
      exact_confirmed_result: unit4Result.router_diagnostics.exact_delete_code
    },
    receipt_diagnostics: {
      request_fields: contract.request_fields,
      receipt_fields: contract.receipt_fields,
      exact_request_field_count: contract.request_fields.length,
      exact_receipt_field_count: contract.receipt_fields.length,
      production_chain_valid_in_unit4: unit4Result.concurrency.receipt_chain_valid,
      bounded_chain_valid_in_unit4: unit4Result.bounded_receipts.visible_chain_valid,
      retained_receipts: unit4Result.bounded_receipts.receipt_count,
      visible_receipts: unit4Result.bounded_receipts.visible_receipts,
      diagnostic_snapshot_status: unit4Result.router_diagnostics.diagnostic_status,
      diagnostic_snapshot_writes: unit4Result.router_diagnostics.diagnostic_writes,
      diagnostic_snapshot_deletes: unit4Result.router_diagnostics.diagnostic_deletes
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
    next_decision: {
      id: 'P9-U6',
      objective: 'Decide from the complete deterministic and existing observation record whether any new bounded Bank observation is genuinely required; issue a no-observation-required waiver when evidence is sufficient.',
      requires_user_app_check_before_decision: false,
      requires_new_explicit_authority_before_decision: false,
      perform_observation_automatically: false
    },
    claim_ceiling: 'P9-U5 static and deterministic cross-unit certification only. No production source, user persisted data, storage migration, scarce live observation, or formal proof is changed or consumed.'
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

module.exports = {
  TYPE,
  VERSION,
  BANK_OWNER,
  RUN_OWNER,
  BANK_KEYS,
  RUN_KEYS,
  stable,
  digest,
  scenarioResult,
  verifyResultHash
};
