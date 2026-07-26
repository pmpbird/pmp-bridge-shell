#!/usr/bin/env node
'use strict';

const crypto = require('crypto');

const CONTRACT_VERSION = 'PMP_BANK_CONTINUOUS_RUN_OWNER_CONTRACT_V1';
const RECEIPT_VERSION = 'PMP_BANK_CONTINUOUS_RUN_OWNER_RECEIPT_V1';
const BANK_OWNER = 'bank_screen_owner';
const RUN_OWNER = 'continuous_run_level_owner';
const EMPTY_SHA256 = crypto.createHash('sha256').update('').digest('hex');
const SAMPLE_SHA256 = crypto.createHash('sha256').update('p9-u2-sample').digest('hex');

function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

function sha256(value) {
  const bytes = Buffer.isBuffer(value) ? value : Buffer.from(typeof value === 'string' ? value : canonical(value));
  return crypto.createHash('sha256').update(bytes).digest('hex');
}

function policy() {
  return {
    contract_version: CONTRACT_VERSION,
    receipt_version: RECEIPT_VERSION,
    model: 'SEPARATE_OWNERS_FAIL_CLOSED_REQUEST_RECEIPT',
    owners: {
      bank: {
        owner_id: BANK_OWNER,
        section_id: 'bank',
        controls: [
          'bank facts',
          'authorized durable writes',
          'bank shell',
          'inventory identity',
          'persistence receipts'
        ],
        resource_prefix: 'bank:',
        accepted_actions: ['READ_FACTS', 'READ_INVENTORY', 'PROPOSE_WRITE', 'COMMIT_WRITE']
      },
      continuous_run: {
        owner_id: RUN_OWNER,
        section_id: 'continuous_run',
        controls: [
          'run lifecycle',
          'level progression',
          'concurrency',
          'cancellation',
          'resume intent'
        ],
        resource_prefix: 'continuous_run:',
        accepted_actions: [
          'READ_RUN_STATE',
          'START_RUN',
          'ADVANCE_LEVEL',
          'PAUSE_RUN',
          'CANCEL_RUN',
          'RESUME_RUN',
          'HANDOFF_RUN',
          'RESTORE_RUN'
        ]
      }
    },
    request_fields: [
      'contract_version',
      'operation_id',
      'request_id',
      'requester_owner',
      'target_owner',
      'action',
      'resource',
      'expected_version',
      'payload_sha256',
      'issued_at',
      'expires_at',
      'cancellation_epoch',
      'capability'
    ],
    receipt_fields: [
      'receipt_version',
      'operation_id',
      'request_id',
      'requester_owner',
      'target_owner',
      'action',
      'resource',
      'decision',
      'code',
      'resource_version_before',
      'resource_version_after',
      'cancellation_epoch',
      'request_sha256',
      'previous_receipt_sha256',
      'receipt_sha256'
    ],
    mutating_actions: [
      'COMMIT_WRITE',
      'START_RUN',
      'ADVANCE_LEVEL',
      'PAUSE_RUN',
      'CANCEL_RUN',
      'RESUME_RUN',
      'HANDOFF_RUN',
      'RESTORE_RUN'
    ],
    forbidden_actions: [
      'DELETE_BANK',
      'CLEAR_BANK',
      'CLEAR_CURRENT_STATE',
      'MANUAL_CLEAR',
      'DIRECT_STORAGE_WRITE',
      'MIGRATE_STORAGE',
      'TAKE_OWNERSHIP',
      'COPY_AUTHORITY_BETWEEN_FRAMES'
    ],
    failure_codes: [
      'DENIED_MALFORMED',
      'DENIED_CONTRACT_VERSION',
      'DENIED_OPERATION_ID',
      'DENIED_REQUEST_ID',
      'DENIED_OWNER',
      'DENIED_CROSS_DELEGATION',
      'DENIED_ACTION',
      'DENIED_RESOURCE',
      'DENIED_EXPECTED_VERSION',
      'DENIED_PAYLOAD_HASH',
      'DENIED_TIME',
      'DENIED_EXPIRED',
      'DENIED_CAPABILITY',
      'DENIED_DUPLICATE_CONFLICT',
      'DENIED_STALE_CANCELLATION',
      'DENIED_CANCELLATION_ADVANCE',
      'DENIED_RESTART_SHAPE'
    ],
    compatibility: {
      legacy_globals_are_identity_hints_only: true,
      copied_cross_frame_apis_convey_authority: false,
      active_tab_conveys_ownership: false,
      filename_conveys_authority: false,
      existing_persisted_keys_preserved: [
        'pmp_continuous_run_state_bank_v1',
        'pmp_continuous_run_state_receipts_v1',
        'pmp_continuous_run_state_manifest_v1'
      ],
      storage_migration: 'FORBIDDEN_IN_P9_U2_AND_P9_U3'
    },
    persistence: {
      durable_writer: BANK_OWNER,
      request_owner_for_run_state: RUN_OWNER,
      algorithm: 'SHA-256',
      append_only_receipt_chain: true,
      delete_or_clear_default: 'DENY'
    },
    concurrency: {
      exact_expected_version: true,
      one_active_lease_per_run_resource: true,
      duplicate_same_operation_and_digest: 'RETURN_IDENTICAL_RECEIPT_NO_NEW_EFFECT',
      duplicate_same_operation_different_digest: 'DENY',
      cancellation_epoch: 'MONOTONIC',
      restart: 'ATOMIC_SNAPSHOT_OR_EMPTY',
      handoff: 'EXACT_EXPECTED_VERSION_AND_CAPABILITY'
    }
  };
}

function request(overrides = {}) {
  const base = {
    contract_version: CONTRACT_VERSION,
    operation_id: 'op:p9u2:sample:001',
    request_id: 'req:p9u2:sample:001',
    requester_owner: RUN_OWNER,
    target_owner: BANK_OWNER,
    action: 'READ_FACTS',
    resource: 'bank:current',
    expected_version: 0,
    payload_sha256: EMPTY_SHA256,
    issued_at: '2026-07-26T19:30:00Z',
    expires_at: '2026-07-26T19:35:00Z',
    cancellation_epoch: 0,
    capability: `request:${BANK_OWNER}:READ_FACTS:bank:current`
  };
  return Object.assign(base, overrides);
}

function ownerRule(target, contract) {
  return Object.values(contract.owners).find(row => row.owner_id === target);
}

function exactCapability(row) {
  return `request:${row.target_owner}:${row.action}:${row.resource}`;
}

function shapeOkay(row, fields) {
  return row && typeof row === 'object' && fields.every(field => Object.prototype.hasOwnProperty.call(row, field));
}

function idOkay(value, prefix) {
  return typeof value === 'string' && value.startsWith(prefix) && /^[a-z0-9:._-]+$/i.test(value);
}

function timeOkay(value) {
  return typeof value === 'string' && Number.isFinite(Date.parse(value));
}

function initialState() {
  return {
    versions: {},
    cancellations: {},
    operations: {},
    previous_receipt_sha256: '0'.repeat(64)
  };
}

function decisionFor(row, state, contract) {
  if (!shapeOkay(row, contract.request_fields)) return ['DENY', 'DENIED_MALFORMED'];
  if (row.contract_version !== contract.contract_version) return ['DENY', 'DENIED_CONTRACT_VERSION'];
  if (!idOkay(row.operation_id, 'op:')) return ['DENY', 'DENIED_OPERATION_ID'];
  if (!idOkay(row.request_id, 'req:')) return ['DENY', 'DENIED_REQUEST_ID'];
  const owners = Object.values(contract.owners).map(owner => owner.owner_id);
  if (!owners.includes(row.requester_owner) || !owners.includes(row.target_owner)) return ['DENY', 'DENIED_OWNER'];
  if (row.requester_owner === row.target_owner) return ['DENY', 'DENIED_CROSS_DELEGATION'];
  const target = ownerRule(row.target_owner, contract);
  if (!target.accepted_actions.includes(row.action) || contract.forbidden_actions.includes(row.action)) {
    return ['DENY', 'DENIED_ACTION'];
  }
  if (typeof row.resource !== 'string' || !row.resource.startsWith(target.resource_prefix)) {
    return ['DENY', 'DENIED_RESOURCE'];
  }
  if (!Number.isInteger(row.expected_version) || row.expected_version < 0) {
    return ['DENY', 'DENIED_EXPECTED_VERSION'];
  }
  const currentVersion = state.versions[row.resource] || 0;
  if (row.expected_version !== currentVersion) return ['DENY', 'DENIED_EXPECTED_VERSION'];
  if (typeof row.payload_sha256 !== 'string' || !/^[0-9a-f]{64}$/.test(row.payload_sha256)) {
    return ['DENY', 'DENIED_PAYLOAD_HASH'];
  }
  if (!timeOkay(row.issued_at) || !timeOkay(row.expires_at) || Date.parse(row.expires_at) <= Date.parse(row.issued_at)) {
    return ['DENY', 'DENIED_TIME'];
  }
  if (Date.parse(row.expires_at) < Date.parse('2026-07-26T19:32:00Z')) return ['DENY', 'DENIED_EXPIRED'];
  if (row.capability !== exactCapability(row)) return ['DENY', 'DENIED_CAPABILITY'];
  if (!Number.isInteger(row.cancellation_epoch) || row.cancellation_epoch < 0) {
    return ['DENY', 'DENIED_STALE_CANCELLATION'];
  }
  const cancellationEpoch = state.cancellations[row.resource] || 0;
  if (row.action === 'CANCEL_RUN') {
    if (row.cancellation_epoch <= cancellationEpoch) return ['DENY', 'DENIED_CANCELLATION_ADVANCE'];
  } else if (row.cancellation_epoch < cancellationEpoch) {
    return ['DENY', 'DENIED_STALE_CANCELLATION'];
  }
  if (row.action === 'RESTORE_RUN' && ![EMPTY_SHA256, SAMPLE_SHA256].includes(row.payload_sha256)) {
    return ['DENY', 'DENIED_RESTART_SHAPE'];
  }
  return ['ALLOW', contract.mutating_actions.includes(row.action) ? 'AUTHORIZED_SIMULATED_TRANSITION' : 'AUTHORIZED_READ'];
}

function makeReceipt(row, decision, code, before, after, cancellationEpoch, requestHash, previousHash) {
  const body = {
    receipt_version: RECEIPT_VERSION,
    operation_id: typeof row?.operation_id === 'string' ? row.operation_id : 'op:invalid',
    request_id: typeof row?.request_id === 'string' ? row.request_id : 'req:invalid',
    requester_owner: typeof row?.requester_owner === 'string' ? row.requester_owner : 'invalid',
    target_owner: typeof row?.target_owner === 'string' ? row.target_owner : 'invalid',
    action: typeof row?.action === 'string' ? row.action : 'invalid',
    resource: typeof row?.resource === 'string' ? row.resource : 'invalid',
    decision,
    code,
    resource_version_before: before,
    resource_version_after: after,
    cancellation_epoch: cancellationEpoch,
    request_sha256: requestHash,
    previous_receipt_sha256: previousHash
  };
  return Object.assign(body, {receipt_sha256: sha256(body)});
}

function evaluate(rows, suppliedPolicy = policy()) {
  const state = initialState();
  const receipts = [];
  let replayed = 0;
  for (const row of rows) {
    const requestHash = sha256(row);
    const operationId = typeof row?.operation_id === 'string' ? row.operation_id : 'op:invalid';
    const previous = state.operations[operationId];
    if (previous) {
      if (previous.request_sha256 === requestHash) {
        receipts.push(previous.receipt);
        replayed += 1;
        continue;
      }
      const before = state.versions[row?.resource] || 0;
      const receipt = makeReceipt(
        row,
        'DENY',
        'DENIED_DUPLICATE_CONFLICT',
        before,
        before,
        state.cancellations[row?.resource] || 0,
        requestHash,
        state.previous_receipt_sha256
      );
      state.previous_receipt_sha256 = receipt.receipt_sha256;
      receipts.push(receipt);
      continue;
    }
    const [decision, code] = decisionFor(row, state, suppliedPolicy);
    const before = state.versions[row?.resource] || 0;
    let after = before;
    if (decision === 'ALLOW' && suppliedPolicy.mutating_actions.includes(row.action)) {
      after += 1;
      state.versions[row.resource] = after;
      if (row.action === 'CANCEL_RUN') state.cancellations[row.resource] = row.cancellation_epoch;
    }
    const receipt = makeReceipt(
      row,
      decision,
      code,
      before,
      after,
      state.cancellations[row?.resource] || 0,
      requestHash,
      state.previous_receipt_sha256
    );
    state.operations[operationId] = {request_sha256: requestHash, receipt};
    state.previous_receipt_sha256 = receipt.receipt_sha256;
    receipts.push(receipt);
  }
  const result = {
    type: 'PMP_PASS9_UNIT2_BANK_CONTINUOUS_RUN_OWNER_CONTRACT_RESULT_V1',
    version: '1.0.0',
    status: 'PASS',
    contract: suppliedPolicy,
    summary: {
      requests: rows.length,
      allowed: receipts.filter(row => row.decision === 'ALLOW').length,
      denied: receipts.filter(row => row.decision === 'DENY').length,
      replayed,
      simulated_resource_versions: state.versions,
      cancellation_epochs: state.cancellations
    },
    receipts,
    effects: {
      production_files_changed: false,
      runtime_integrity_changed: false,
      browser_launched: false,
      network_requests: false,
      storage_writes: false,
      route_changes: false,
      mounts: false,
      bank_mutations: false,
      continuous_run_mutations: false,
      repairs: false,
      live_observation_performed: false,
      formal_proof_performed: false,
      persisted_user_data_changed: false,
      storage_migration_performed: false,
      production_behavior_activated: false
    },
    claim_ceiling: 'Pure static P9-U2 contract simulation; no production behavior, Bank state, Continuous Run state, or persisted user data is changed.'
  };
  return Object.assign(result, {result_sha256: sha256(result)});
}

function verifyResultHash(result) {
  const copy = JSON.parse(JSON.stringify(result));
  const recorded = copy.result_sha256;
  delete copy.result_sha256;
  return typeof recorded === 'string' && recorded === sha256(copy);
}

module.exports = {
  BANK_OWNER,
  RUN_OWNER,
  EMPTY_SHA256,
  SAMPLE_SHA256,
  CONTRACT_VERSION,
  RECEIPT_VERSION,
  canonical,
  sha256,
  policy,
  request,
  evaluate,
  verifyResultHash
};

if (require.main === module) {
  process.stdout.write(`${JSON.stringify(evaluate([]), null, 2)}\n`);
}
