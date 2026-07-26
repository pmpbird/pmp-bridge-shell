#!/usr/bin/env node
'use strict';

const runner = require('./run_pass9_unit2_bank_continuous_run_owner_contract_v1.js');

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

const policy = runner.policy();
equal(policy.contract_version, runner.CONTRACT_VERSION, 'contract version');
equal(policy.receipt_version, runner.RECEIPT_VERSION, 'receipt version');
equal(policy.model, 'SEPARATE_OWNERS_FAIL_CLOSED_REQUEST_RECEIPT', 'model');
equal(policy.owners.bank.owner_id, runner.BANK_OWNER, 'Bank owner identity');
equal(policy.owners.bank.section_id, 'bank', 'Bank section');
equal(policy.owners.continuous_run.owner_id, runner.RUN_OWNER, 'Continuous Run owner identity');
equal(policy.owners.continuous_run.section_id, 'continuous_run', 'Continuous Run section');
check(runner.BANK_OWNER !== runner.RUN_OWNER, 'owners are separate');
equal(policy.owners.bank.controls, [
  'bank facts',
  'authorized durable writes',
  'bank shell',
  'inventory identity',
  'persistence receipts'
], 'Bank controls exact');
equal(policy.owners.continuous_run.controls, [
  'run lifecycle',
  'level progression',
  'concurrency',
  'cancellation',
  'resume intent'
], 'Continuous Run controls exact');
equal(policy.request_fields.length, 13, 'request field count');
equal(new Set(policy.request_fields).size, 13, 'request fields unique');
equal(policy.receipt_fields.length, 15, 'receipt field count');
equal(new Set(policy.receipt_fields).size, 15, 'receipt fields unique');
equal(policy.persistence.durable_writer, runner.BANK_OWNER, 'only Bank writes durable state');
equal(policy.persistence.request_owner_for_run_state, runner.RUN_OWNER, 'Run requests state persistence');
equal(policy.persistence.algorithm, 'SHA-256', 'receipt hash algorithm');
equal(policy.persistence.delete_or_clear_default, 'DENY', 'delete/clear default deny');
check(policy.persistence.append_only_receipt_chain, 'receipt chain append-only');
check(policy.compatibility.legacy_globals_are_identity_hints_only, 'legacy globals are hints');
equal(policy.compatibility.copied_cross_frame_apis_convey_authority, false, 'copied APIs no authority');
equal(policy.compatibility.active_tab_conveys_ownership, false, 'tab no authority');
equal(policy.compatibility.filename_conveys_authority, false, 'filename no authority');
equal(policy.compatibility.storage_migration, 'FORBIDDEN_IN_P9_U2_AND_P9_U3', 'no migration');
equal(policy.compatibility.existing_persisted_keys_preserved.length, 3, 'existing keys preserved');
equal(policy.concurrency.duplicate_same_operation_and_digest, 'RETURN_IDENTICAL_RECEIPT_NO_NEW_EFFECT', 'idempotency');
equal(policy.concurrency.duplicate_same_operation_different_digest, 'DENY', 'duplicate conflict');
equal(policy.concurrency.cancellation_epoch, 'MONOTONIC', 'cancellation monotonic');
equal(policy.concurrency.restart, 'ATOMIC_SNAPSHOT_OR_EMPTY', 'restart atomic');
equal(policy.concurrency.handoff, 'EXACT_EXPECTED_VERSION_AND_CAPABILITY', 'handoff exact');
check(policy.concurrency.one_active_lease_per_run_resource, 'single run lease');
equal(policy.forbidden_actions.length, 8, 'forbidden action count');
equal(new Set(policy.forbidden_actions).size, 8, 'forbidden actions unique');
for (const action of ['DELETE_BANK', 'CLEAR_BANK', 'CLEAR_CURRENT_STATE', 'MANUAL_CLEAR', 'MIGRATE_STORAGE']) {
  check(policy.forbidden_actions.includes(action), `${action} forbidden`);
}
equal(policy.failure_codes.length, 17, 'failure code count');
equal(new Set(policy.failure_codes).size, 17, 'failure codes unique');

function result(rows) {
  const value = runner.evaluate(rows, policy);
  check(runner.verifyResultHash(value), 'result hash');
  check(Object.values(value.effects).every(flag => flag === false), 'zero effects');
  return value;
}
function receipt(rows) {
  return result(rows).receipts.slice(-1)[0];
}
function row(overrides = {}) {
  return runner.request(overrides);
}
function runRow(action, resource, expectedVersion, index, overrides = {}) {
  return row(Object.assign({
    operation_id: `op:p9u2:run:${index}`,
    request_id: `req:p9u2:run:${index}`,
    requester_owner: runner.BANK_OWNER,
    target_owner: runner.RUN_OWNER,
    action,
    resource,
    expected_version: expectedVersion,
    capability: `request:${runner.RUN_OWNER}:${action}:${resource}`
  }, overrides));
}
function bankRow(action, resource, expectedVersion, index, overrides = {}) {
  return row(Object.assign({
    operation_id: `op:p9u2:bank:${index}`,
    request_id: `req:p9u2:bank:${index}`,
    action,
    resource,
    expected_version: expectedVersion,
    capability: `request:${runner.BANK_OWNER}:${action}:${resource}`
  }, overrides));
}

const empty = result([]);
equal(empty.type, 'PMP_PASS9_UNIT2_BANK_CONTINUOUS_RUN_OWNER_CONTRACT_RESULT_V1', 'result type');
equal(empty.status, 'PASS', 'empty status');
equal(empty.summary.requests, 0, 'empty requests');
equal(empty.summary.allowed, 0, 'empty allowed');
equal(empty.summary.denied, 0, 'empty denied');
equal(empty.summary.replayed, 0, 'empty replayed');
check(empty.claim_ceiling.includes('Pure static P9-U2'), 'claim ceiling');

const read = result([row()]);
equal(read.summary.allowed, 1, 'read allowed');
equal(read.summary.denied, 0, 'read no denial');
equal(read.receipts[0].code, 'AUTHORIZED_READ', 'read code');
equal(read.receipts[0].resource_version_before, 0, 'read version before');
equal(read.receipts[0].resource_version_after, 0, 'read no version change');

const commit = result([
  bankRow('PROPOSE_WRITE', 'bank:run-state', 0, 'proposal'),
  bankRow('COMMIT_WRITE', 'bank:run-state', 0, 'commit', {payload_sha256: runner.SAMPLE_SHA256})
]);
equal(commit.receipts.map(item => item.code), ['AUTHORIZED_READ', 'AUTHORIZED_SIMULATED_TRANSITION'], 'proposal/commit codes');
equal(commit.receipts[1].resource_version_after, 1, 'commit simulated version');
equal(commit.summary.simulated_resource_versions['bank:run-state'], 1, 'commit version state');

const lifecycleRows = [
  runRow('START_RUN', 'continuous_run:primary', 0, 'start'),
  runRow('ADVANCE_LEVEL', 'continuous_run:primary', 1, 'advance'),
  runRow('PAUSE_RUN', 'continuous_run:primary', 2, 'pause'),
  runRow('RESUME_RUN', 'continuous_run:primary', 3, 'resume'),
  runRow('HANDOFF_RUN', 'continuous_run:primary', 4, 'handoff'),
  runRow('CANCEL_RUN', 'continuous_run:primary', 5, 'cancel', {cancellation_epoch: 1})
];
const lifecycle = result(lifecycleRows);
equal(lifecycle.summary.allowed, 6, 'lifecycle allowed');
equal(lifecycle.summary.denied, 0, 'lifecycle no denials');
equal(lifecycle.summary.simulated_resource_versions['continuous_run:primary'], 6, 'lifecycle version');
equal(lifecycle.summary.cancellation_epochs['continuous_run:primary'], 1, 'cancellation epoch state');
equal(lifecycle.receipts.map(item => item.resource_version_after), [1, 2, 3, 4, 5, 6], 'monotonic versions');
equal(lifecycle.receipts[5].cancellation_epoch, 1, 'cancellation recorded');
for (let index = 0; index < lifecycle.receipts.length; index += 1) {
  const item = lifecycle.receipts[index];
  equal(Object.keys(item).sort(), policy.receipt_fields.slice().sort(), `receipt ${index} exact fields`);
  const copy = JSON.parse(JSON.stringify(item));
  const recorded = copy.receipt_sha256;
  delete copy.receipt_sha256;
  equal(recorded, runner.sha256(copy), `receipt ${index} hash`);
  if (index === 0) equal(item.previous_receipt_sha256, '0'.repeat(64), 'chain root');
  else equal(item.previous_receipt_sha256, lifecycle.receipts[index - 1].receipt_sha256, `chain ${index}`);
}

const staleAfterCancel = result([
  runRow('CANCEL_RUN', 'continuous_run:cancelled', 0, 'cancel-first', {cancellation_epoch: 2}),
  runRow('RESUME_RUN', 'continuous_run:cancelled', 1, 'stale-resume', {cancellation_epoch: 1})
]);
equal(staleAfterCancel.receipts[0].decision, 'ALLOW', 'cancel allowed');
equal(staleAfterCancel.receipts[1].code, 'DENIED_STALE_CANCELLATION', 'stale resume denied');
equal(staleAfterCancel.receipts[1].resource_version_after, 1, 'stale resume no transition');

equal(
  receipt([runRow('CANCEL_RUN', 'continuous_run:new', 0, 'zero-cancel')]).code,
  'DENIED_CANCELLATION_ADVANCE',
  'non-advancing cancellation denied'
);
equal(
  receipt([runRow('RESTORE_RUN', 'continuous_run:restore-empty', 0, 'restore-empty', {payload_sha256: runner.EMPTY_SHA256})]).decision,
  'ALLOW',
  'empty restart allowed'
);
equal(
  receipt([runRow('RESTORE_RUN', 'continuous_run:restore-snapshot', 0, 'restore-snapshot', {payload_sha256: runner.SAMPLE_SHA256})]).decision,
  'ALLOW',
  'sealed snapshot restart allowed'
);
equal(
  receipt([runRow('RESTORE_RUN', 'continuous_run:restore-bad', 0, 'restore-bad', {payload_sha256: 'f'.repeat(64)})]).code,
  'DENIED_RESTART_SHAPE',
  'unbound restart denied'
);

const duplicateRequest = bankRow('READ_INVENTORY', 'bank:inventory', 0, 'duplicate');
const replay = result([duplicateRequest, JSON.parse(JSON.stringify(duplicateRequest))]);
equal(replay.summary.replayed, 1, 'duplicate replay count');
equal(replay.receipts[0], replay.receipts[1], 'duplicate returns identical receipt');
equal(replay.summary.simulated_resource_versions, {}, 'duplicate no effects');
const conflictRequest = JSON.parse(JSON.stringify(duplicateRequest));
conflictRequest.request_id = 'req:p9u2:bank:duplicate-conflict';
const conflict = result([duplicateRequest, conflictRequest]);
equal(conflict.receipts[1].code, 'DENIED_DUPLICATE_CONFLICT', 'duplicate conflict denied');
equal(conflict.receipts[1].resource_version_before, conflict.receipts[1].resource_version_after, 'conflict no effect');

const malformed = row();
delete malformed.request_id;
equal(receipt([malformed]).code, 'DENIED_MALFORMED', 'missing field denied');
const negativeCases = [
  [{contract_version: 'wrong'}, 'DENIED_CONTRACT_VERSION'],
  [{operation_id: 'bad'}, 'DENIED_OPERATION_ID'],
  [{request_id: 'bad'}, 'DENIED_REQUEST_ID'],
  [{requester_owner: 'unknown_owner'}, 'DENIED_OWNER'],
  [{target_owner: 'unknown_owner', capability: 'request:unknown_owner:READ_FACTS:bank:current'}, 'DENIED_OWNER'],
  [{requester_owner: runner.BANK_OWNER}, 'DENIED_CROSS_DELEGATION'],
  [{action: 'DELETE_BANK', capability: `request:${runner.BANK_OWNER}:DELETE_BANK:bank:current`}, 'DENIED_ACTION'],
  [{action: 'UNKNOWN', capability: `request:${runner.BANK_OWNER}:UNKNOWN:bank:current`}, 'DENIED_ACTION'],
  [{resource: 'continuous_run:wrong', capability: `request:${runner.BANK_OWNER}:READ_FACTS:continuous_run:wrong`}, 'DENIED_RESOURCE'],
  [{expected_version: -1}, 'DENIED_EXPECTED_VERSION'],
  [{expected_version: 1}, 'DENIED_EXPECTED_VERSION'],
  [{payload_sha256: 'bad'}, 'DENIED_PAYLOAD_HASH'],
  [{issued_at: 'bad'}, 'DENIED_TIME'],
  [{expires_at: '2026-07-26T19:29:00Z'}, 'DENIED_TIME'],
  [{issued_at: '2026-07-26T19:20:00Z', expires_at: '2026-07-26T19:31:00Z'}, 'DENIED_EXPIRED'],
  [{capability: 'wrong'}, 'DENIED_CAPABILITY'],
  [{cancellation_epoch: -1}, 'DENIED_STALE_CANCELLATION']
];
for (const [overrides, code] of negativeCases) {
  equal(receipt([row(overrides)]).code, code, `${code} covered`);
}

for (const action of policy.owners.bank.accepted_actions) {
  const payload = action === 'COMMIT_WRITE' ? runner.SAMPLE_SHA256 : runner.EMPTY_SHA256;
  equal(receipt([bankRow(action, `bank:matrix-${action.toLowerCase()}`, 0, `matrix-${action}`, {payload_sha256: payload})]).decision, 'ALLOW', `Bank ${action} accepted`);
}
for (const action of policy.owners.continuous_run.accepted_actions) {
  const payload = action === 'RESTORE_RUN' ? runner.SAMPLE_SHA256 : runner.EMPTY_SHA256;
  const cancellation = action === 'CANCEL_RUN' ? 1 : 0;
  equal(receipt([runRow(action, `continuous_run:matrix-${action.toLowerCase()}`, 0, `matrix-${action}`, {
    payload_sha256: payload,
    cancellation_epoch: cancellation
  })]).decision, 'ALLOW', `Run ${action} accepted`);
}
for (const action of policy.forbidden_actions) {
  equal(receipt([row({
    action,
    capability: `request:${runner.BANK_OWNER}:${action}:bank:current`
  })]).code, 'DENIED_ACTION', `${action} fail closed`);
}

const deterministicRows = [
  row(),
  runRow('START_RUN', 'continuous_run:deterministic', 0, 'deterministic-start')
];
equal(runner.evaluate(deterministicRows, policy), runner.evaluate(deterministicRows, policy), 'deterministic result');
const tampered = runner.evaluate(deterministicRows, policy);
tampered.summary.allowed = 99;
equal(runner.verifyResultHash(tampered), false, 'tampered result rejected');

console.log(`PASS: P9-U2 Bank/Continuous Run owner contract (${assertions}/${assertions})`);
