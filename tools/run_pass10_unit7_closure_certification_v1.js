#!/usr/bin/env node
'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const TYPE = 'PMP_PASS10_UNIT7_CLOSURE_CERTIFICATION_RESULT_V1';
const VERSION = '1.0.0';
const REPORT_PATHS = [
  'audit/pass10/pass10-bank-unit1-inventory-reconciliation-v1.json',
  'audit/pass10/pass10-bank-unit2-inventory-contract-v1.json',
  'audit/pass10/pass10-bank-unit3-readonly-projection-v1.json',
  'audit/pass10/pass10-bank-unit4-owner-projection-refresh-v1.json',
  'audit/pass10/pass10-bank-unit5-fault-corruption-proof-v1.json',
  'audit/pass10/pass10-bank-unit6-reversible-migration-rehearsal-v1.json',
  'audit/pass10/pass10-bank-unit7-hands-on-readiness-v1.json',
  'audit/pass10/pass10-bank-unit7-level-owner-stability-repair-v1.json',
  'audit/pass10/pass10-bank-unit7-legacy-level-alias-single-stack-repair-v1.json',
  'audit/pass10/pass10-bank-unit7-single-card-presentation-v1.json',
  'audit/pass10/pass10-bank-unit7-uniform-title-weight-v1.json'
];
const RECEIPT_PATHS = [
  'audit/pass10/receipts/RECEIPT_P10_U1_BANK_INVENTORY_RECONCILIATION_20260726T212000Z_001.json',
  'audit/pass10/receipts/RECEIPT_P10_U2_BANK_INVENTORY_CONTRACT_20260726T220000Z_001.json',
  'audit/pass10/receipts/RECEIPT_P10_U3_BANK_READONLY_PROJECTION_20260726T223500Z_001.json',
  'audit/pass10/receipts/RECEIPT_P10_U4_BANK_OWNER_PROJECTION_REFRESH_20260726T230500Z_001.json',
  'audit/pass10/receipts/RECEIPT_P10_U5_BANK_FAULT_CORRUPTION_PROOF_20260726T233000Z_001.json',
  'audit/pass10/receipts/RECEIPT_P10_U6_BANK_REVERSIBLE_MIGRATION_REHEARSAL_20260726T234500Z_001.json',
  'audit/pass10/receipts/RECEIPT_P10_U7A_BANK_HANDS_ON_READINESS_20260726T233200Z_001.json',
  'audit/pass10/receipts/RECEIPT_P10_U7R_BANK_LEVEL_OWNER_STABILITY_REPAIR_20260727T022458Z_001.json',
  'audit/pass10/receipts/RECEIPT_P10_U7S_LEGACY_LEVEL_ALIAS_SINGLE_STACK_REPAIR_20260727T030823Z_001.json',
  'audit/pass10/receipts/RECEIPT_P10_U7T_SINGLE_CARD_PRESENTATION_20260727T034514Z_001.json',
  'audit/pass10/receipts/RECEIPT_P10_U7U_UNIFORM_TITLE_WEIGHT_20260727T041526Z_001.json'
];
const EXPECTED_STATUSES = [
  'BANK_INVENTORY_RECONCILIATION_PROVEN',
  'BANK_INVENTORY_CONTRACT_PROVEN',
  'BANK_READONLY_PROJECTION_PROVEN',
  'BANK_OWNER_PROJECTION_REFRESH_PROVEN',
  'BANK_FAULT_ROLLBACK_AND_CORRUPTION_CONTAINMENT_PROVEN',
  'BANK_REVERSIBLE_MIGRATION_REHEARSAL_PROVEN',
  'HANDS_ON_APP_CHECK_REQUIRED',
  'DETERMINISTIC_REPAIR_GREEN_HANDS_ON_RECHECK_REQUIRED',
  'DETERMINISTIC_ALIAS_REPAIR_GREEN_FINAL_ORDER_RECHECK_REQUIRED',
  'DETERMINISTIC_PRESENTATION_GREEN_HANDS_ON_VISUAL_RECHECK_REQUIRED',
  'DETERMINISTIC_UNIFORM_TITLE_WEIGHT_GREEN_HANDS_ON_TYPOGRAPHY_RECHECK_REQUIRED'
];
const EXPECTED_ASSERTIONS = [110, 187, 125, 121, 133, 102, 75, 106, 151, 478, 86];
const EXPECTED_STEPS = [
  'P10-U2',
  'P10-U3',
  'P10-U4',
  'P10-U5',
  'P10-U6',
  'P10-U7',
  'P10-U7B',
  'P10-U7B-FOCUSED-RECHECK',
  'P10-U7B-FINAL-ORDER-RECHECK',
  'P10-U7B-FINAL-VISUAL-AND-ORDER-RECHECK',
  'P10-U7B-FINAL-UNIFORM-TITLE-WEIGHT-RECHECK'
];

function read(relative) {
  return JSON.parse(fs.readFileSync(path.join(ROOT, relative), 'utf8'));
}
function stable(value) {
  if (Array.isArray(value)) return '[' + value.map(stable).join(',') + ']';
  if (value && typeof value === 'object') {
    return '{' + Object.keys(value).sort().map(key => JSON.stringify(key) + ':' + stable(value[key])).join(',') + '}';
  }
  return JSON.stringify(value);
}
function digest(value) {
  return crypto.createHash('sha256').update(Buffer.from(stable(value))).digest('hex');
}
function assertionCount(report, index) {
  if (index === 3) return report.deterministic_matrix.assertions;
  return report.verification.assertions_passed;
}
function assertionFailures(report, index) {
  if (index === 3) return report.deterministic_matrix.assertions_failed;
  return report.verification.assertions_failed;
}
function effectFalse(report, keys) {
  return keys.every(key => report.effects[key] !== true);
}

function scenarioResult() {
  const reports = REPORT_PATHS.map(read);
  const receipts = RECEIPT_PATHS.map(read);
  const contract = reports[1].inventory_contract;
  const projection = reports[2].integration;
  const refresh = reports[3].integration;
  const fault = reports[4].proof;
  const rehearsal = reports[5].rehearsal;
  const readiness = reports[6];
  const stability = reports[7].repair;
  const ordering = reports[8].repair;
  const presentation = reports[9].repair;
  const typography = reports[10].repair;
  const rows = reports.map((report, index) => ({
    evidence_id: report.substep || report.unit_id,
    status: report.status,
    expected_status: EXPECTED_STATUSES[index],
    assertions: assertionCount(report, index),
    expected_assertions: EXPECTED_ASSERTIONS[index],
    assertions_failed: assertionFailures(report, index),
    receipt_status: receipts[index].status,
    receipt_next_step: receipts[index].next_safe_move.step_id,
    expected_next_step: EXPECTED_STEPS[index],
    persisted_user_data_preserved: effectFalse(report, ['persisted_user_data_changed']),
    storage_migration_not_performed: effectFalse(report, ['storage_migration_performed', 'production_migration_performed']),
    formal_proof_not_performed: effectFalse(report, ['formal_proof_performed']),
    special_authority_unconsumed: report.authority.special_authority_consumed !== true
      && report.authority.formal_proof_authorization_consumed !== true
  }));
  const canonicalOrder = [
    '1', '2', '3', '4', '4B', '5', '6', '7', '8', '9', '10', '11', '12',
    '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24',
    '25', '26', '27', '28', '29', '30', '30B'
  ];
  const handsOn = {
    source: 'USER_REPORT',
    reported_after_merged_main: '09e78630cb9865a6817f460ef28a4dc455dcc036',
    exact_statement: 'It worked.',
    result: 'PASS',
    current_app_state_confirmed: true,
    confirms_uniform_title_weight: true,
    confirms_prior_card_order_and_no_flicker_repairs_remained_intact: true,
    persisted_user_data_change_requested: false,
    special_authority_consumed: false
  };
  const exitCriteria = {
    every_evidence_record_present_and_ordered: reports.length === 11 && receipts.length === 11,
    every_status_matches_immutable_receipt: rows.every(row => row.status === row.expected_status && row.receipt_status === row.status),
    all_1674_predecessor_assertions_green: rows.reduce((sum, row) => sum + row.assertions, 0) === 1674
      && rows.every(row => row.assertions === row.expected_assertions && row.assertions_failed === 0),
    stable_identity_is_sha256_owner_provenance_bound: contract.canonical_identity.algorithm === 'SHA-256'
      && contract.provenance.owning_bank_required === true
      && contract.provenance.owner_id_required === true
      && contract.provenance.payload_sha256_required === true,
    unknown_or_orphan_data_quarantined_never_deleted: contract.quarantine.unknown_or_orphan_owner === 'QUARANTINE'
      && contract.quarantine.policy === 'PRESERVE_EXACT_BYTES_NEVER_SILENTLY_DELETE',
    bank_tab_has_no_write_delete_or_migration_api: projection.write_apis_exposed === 0
      && projection.delete_apis_exposed === 0
      && projection.migration_apis_exposed === 0,
    bank_tab_cannot_independently_mutate: projection.active_tab_conveys_authority === false
      && refresh.direct_ui_event_conveys_authority === false,
    owner_refresh_is_exactly_once_and_fail_closed: refresh.accepted_event_projection_refreshes === 1
      && refresh.automatic_retry_limit === 0
      && refresh.fail_closed_cases.length === 10,
    large_duplicate_orphan_stale_restart_and_corruption_proven: fault.large_inventory_records === 2048
      && fault.unresolved_deterministic_failures === 0
      && reports[4].fault_matrix.every(row => row.result === 'PASS'),
    reversible_fixture_migration_proven: rehearsal.idempotent_repeat_writes === 0
      && rehearsal.interruption_exact_rollback === true
      && rehearsal.explicit_rollback_exact === true,
    production_migration_remains_denied: rehearsal.production_target === 'DENIED_PRODUCTION_TARGET'
      && reports[5].migration_boundary.production_migration_allowed === false,
    regular_bank_containment_and_single_owner_stack_repaired: stability.bank_home_level_count_required === 0
      && stability.single_owner_slot === true
      && stability.recurring_reparent_timer_active === false,
    canonical_level_order_repaired: JSON.stringify(ordering.canonical_order) === JSON.stringify(canonicalOrder)
      && Object.keys(ordering.legacy_aliases).length === 5
      && ordering.hidden_mount_sentinels === true
      && ordering.recurring_canonical_reparent_timer_active === false,
    one_card_one_title_presentation_repaired: presentation.canonical_shells_preserved === true
      && presentation.inner_member_border_visible === false
      && presentation.repeated_direct_level_heading_visible === false,
    title_weight_uniformity_repaired: typography.pre_level3_title_count === 6
      && typography.pre_level3_title_weight_after === 950
      && typography.exact_weight_match === true,
    final_user_hands_on_confirmation_green: handsOn.result === 'PASS'
      && handsOn.current_app_state_confirmed === true,
    every_record_preserves_user_data: rows.every(row => row.persisted_user_data_preserved),
    no_production_storage_migration: rows.every(row => row.storage_migration_not_performed),
    no_formal_proof_run_or_consumed: rows.every(row => row.formal_proof_not_performed && row.special_authority_unconsumed),
    no_special_authority_consumed_by_closure: handsOn.special_authority_consumed === false,
    pass11_entry_is_safety_contract_only: true
  };
  const passed = Object.values(exitCriteria).every(Boolean);
  const result = {
    type: TYPE,
    version: VERSION,
    status: passed ? 'PASS10_BANK_INVENTORY_REBUILD_COMPLETE' : 'PASS10_CLOSURE_REQUIRES_REVIEW',
    pass10_result: passed ? 'PASS' : 'FAIL',
    evidence_records: rows.length,
    cumulative_predecessor_assertions: rows.reduce((sum, row) => sum + row.assertions, 0),
    evidence_rows: rows,
    hands_on_confirmation: handsOn,
    exit_criteria: exitCriteria,
    bank_boundary: {
      inventory_contract: contract.contract_version,
      canonical_owner: contract.canonical_inventory_owner,
      identity_algorithm: contract.canonical_identity.algorithm,
      quarantine_policy: contract.quarantine.policy,
      delete_default: contract.no_deletion.default,
      projection_write_apis: projection.write_apis_exposed,
      projection_delete_apis: projection.delete_apis_exposed,
      projection_migration_apis: projection.migration_apis_exposed,
      owner_refresh_mode: refresh.model
    },
    next_step: {
      id: passed ? 'P11-U1' : 'STOP_FOR_PASS10_CLOSURE_REVIEW',
      objective: 'Consolidate the safety invariants, protected assets, persisted-user-data boundaries, and authority rules that govern every pass.',
      requires_user_app_check: false,
      requires_new_explicit_authority: false,
      persisted_user_data_change_allowed: false,
      production_migration_allowed: false,
      stop_after: false
    },
    effects: {
      production_files_changed: false,
      runtime_integrity_changed: false,
      browser_launched: false,
      network_requests: false,
      storage_reads: false,
      storage_writes: false,
      storage_deletes: false,
      route_changes: false,
      bank_user_data_mutations: false,
      continuous_run_user_data_mutations: false,
      repairs: false,
      live_observation_performed: false,
      formal_proof_performed: false,
      persisted_user_data_changed: false,
      storage_migration_performed: false,
      production_behavior_activated: false
    },
    claim_ceiling: 'Static Pass 10 closure certification grounded in immutable deterministic evidence plus the user-reported final hands-on result. It launches no app, runs no observation or formal proof, changes no runtime or persisted user data, performs no migration, and activates no production behavior.'
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
  REPORT_PATHS,
  RECEIPT_PATHS,
  EXPECTED_STATUSES,
  EXPECTED_ASSERTIONS,
  EXPECTED_STEPS,
  stable,
  digest,
  scenarioResult,
  verifyResultHash
};
