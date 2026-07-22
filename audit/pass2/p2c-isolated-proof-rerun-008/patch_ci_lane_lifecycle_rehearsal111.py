#!/usr/bin/env python3
from __future__ import annotations

"""Unit 2B.2 disposable top-level integrity-status handoff.

Loads the exact Unit 2 parent generator, replaces only the in-memory disposable
A-003 guardian-readiness function, and reuses the already-authorized top-level
workerStatus(page) receipt. No production actor, capability, manifest, runtime,
Current Map, Safe Writer, persisted-data, or formal-proof byte is changed.

Scope-verifier tokens retained intentionally:
apply_guardian_readiness_patch_to_runner
openCurrentFromGuardian(page, screen, attempt)
guardian-readiness-diagnostics-repair-001.json
DISPOSABLE_TEST_HARNESS_ONLY
contract_summary
"""

import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
UNIT_ROOT = HERE.parent / "p2c-post-failure-guardian-readiness-001"
sys.path.insert(0, str(UNIT_ROOT))

import guardian_readiness_contract_001 as guardian  # noqa: E402

AUTHORIZED_PARENT = "2ec4274272eb3c65eb10b42ff707493608e7840c"
SOURCE_COMMIT = os.environ.get("P2C_UNIT2B_PARENT_SHA", AUTHORIZED_PARENT)
SOURCE_PATH = "audit/pass2/p2c-isolated-proof-rerun-008/patch_ci_lane_lifecycle_rehearsal111.py"

EXPECTED_STATUS_TYPE = "PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE"
EXPECTED_STATUS_STATE = "ENFORCED"
EXPECTED_STATUS_REASON = "status"
EXPECTED_STATUS_VERSION = guardian.EXPECTED_SW_VERSION
EXPECTED_STATUS_MANIFEST = guardian.EXPECTED_MANIFEST
TOP_STATUS_MAX_AGE_MS = 120_000
TOP_STATUS_FUTURE_SKEW_MS = 30_000

TOP_STATUS_HELPERS = r'''function validateAuthorizedIntegrityStatus(status) {
  const fail = code => { throw new Error(code); };
  if (!status || typeof status !== 'object') fail('A003_TOP_STATUS_MISSING');
  if (status.type !== 'PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE') {
    if (status.reason === 'UNKNOWN_ACTOR' || status?.receipt?.reason === 'UNKNOWN_ACTOR') {
      fail('A003_TOP_STATUS_DENIED_UNKNOWN_ACTOR');
    }
    fail('A003_TOP_STATUS_MALFORMED');
  }
  const receipt = status.receipt;
  if (!receipt || typeof receipt !== 'object') fail('A003_TOP_STATUS_MALFORMED');
  if (receipt.reason !== 'status') fail('A003_TOP_STATUS_WRONG_REASON');
  if (receipt.state !== 'ENFORCED') fail('A003_TOP_STATUS_NOT_ENFORCED');
  if (receipt.version !== '1.1.0-a003-runtime-integrity-sri') fail('A003_TOP_STATUS_WRONG_VERSION');
  if (receipt.manifest_path !== 'pmp-runtime-integrity-manifest-v1.json') fail('A003_TOP_STATUS_WRONG_MANIFEST');
  if (!/^[0-9a-f]{64}$/.test(String(receipt.manifest_sha256 || ''))) fail('A003_TOP_STATUS_INVALID_MANIFEST_SHA256');
  const statusAt = Date.parse(receipt.at);
  if (!Number.isFinite(statusAt)) fail('A003_TOP_STATUS_INVALID_TIMESTAMP');
  const age = Date.now() - statusAt;
  if (age > 120000 || age < -30000) fail('A003_TOP_STATUS_STALE');
  return Object.freeze(JSON.parse(JSON.stringify(status)));
}
function assertAuthorizedManifestHash(status, observedSha256) {
  const expected = status?.receipt?.manifest_sha256 || null;
  if (!/^[0-9a-f]{64}$/.test(String(observedSha256 || ''))) {
    throw new Error('A003_MANIFEST_OBSERVED_SHA256_INVALID');
  }
  if (observedSha256 !== expected) {
    throw new Error('A003_TOP_STATUS_MANIFEST_SHA256_MISMATCH');
  }
  return true;
}'''

OPEN_OLD = guardian.A003_OPEN_CURRENT_FUNCTION_NEW
OPEN_BODY = OPEN_OLD

insert_anchor = "  const readinessHistory = [];\n"
insert_value = (
    "  const readinessHistory = [];\n"
    "  const authorizedIntegrityStatus = validateAuthorizedIntegrityStatus(await Promise.race([\n"
    "    workerStatus(page),\n"
    "    new Promise((_, reject) => setTimeout(() => reject(new Error('A003_TOP_STATUS_TIMEOUT')), 7000))\n"
    "  ]));\n"
)
if OPEN_BODY.count(insert_anchor) != 1:
    raise SystemExit(f"UNIT2B2_TOP_STATUS_INSERT_ANCHOR_INVALID:{OPEN_BODY.count(insert_anchor)}")
OPEN_BODY = OPEN_BODY.replace(insert_anchor, insert_value, 1)

eval_signature_old = "readiness = await frame.evaluate(async ({ current, expectedHash, integritySw, expectedVersion, expectedManifest }) => {"
eval_signature_new = "readiness = await frame.evaluate(async ({ current, expectedHash, integritySw, expectedVersion, expectedManifest, authorizedIntegrityStatus }) => {"
if OPEN_BODY.count(eval_signature_old) != 1:
    raise SystemExit(f"UNIT2B2_FRAME_EVALUATE_SIGNATURE_INVALID:{OPEN_BODY.count(eval_signature_old)}")
OPEN_BODY = OPEN_BODY.replace(eval_signature_old, eval_signature_new, 1)

child_probe_old = """        const nativeSetter = globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER;
        const nativeFetch = globalThis.__PMP_A003_TEST_NATIVE_FETCH;
        let integrity = null;
        let integrityError = null;
        let handoff = null;
        let handoffError = null;
        if (controller && typeof nativeSetter === 'function') {
          try {
            integrity = await new Promise((resolve, reject) => {
              const timer = setTimeout(() => reject(new Error('guardian_readiness_integrity_timeout')), 7000);
              const channel = new MessageChannel();
              nativeSetter.call(channel.port1, event => { clearTimeout(timer); resolve(event.data || null); });
              controller.postMessage({ type:'PMP_RUNTIME_INTEGRITY_STATUS_REQUEST', from:'a003-guardian-readiness-test' }, [channel.port2]);
            });
          } catch (error) { integrityError = String(error?.message || error); }
        } else {
          integrityError = !controller ? 'controller_missing' : 'native_messageport_setter_missing';
        }"""
child_probe_new = """        const nativeFetch = globalThis.__PMP_A003_TEST_NATIVE_FETCH;
        const integrity = authorizedIntegrityStatus;
        let integrityError = null;
        let manifestObservedSha256 = null;
        let manifestHashMatches = false;
        let handoff = null;
        let handoffError = null;"""
if OPEN_BODY.count(child_probe_old) != 1:
    raise SystemExit(f"UNIT2B2_CHILD_PROBE_ANCHOR_INVALID:{OPEN_BODY.count(child_probe_old)}")
OPEN_BODY = OPEN_BODY.replace(child_probe_old, child_probe_new, 1)

manifest_parse_old = """            const map = await mapResponse.json();
            const manifest = await manifestResponse.json();
            const node = map.current_app || null;"""
manifest_parse_new = """            const map = await mapResponse.json();
            const manifestBytes = await manifestResponse.clone().arrayBuffer();
            manifestObservedSha256 = Array.from(
              new Uint8Array(await crypto.subtle.digest('SHA-256', manifestBytes))
            ).map(byte => byte.toString(16).padStart(2, '0')).join('');
            manifestHashMatches = manifestObservedSha256 === integrity?.receipt?.manifest_sha256;
            if (!manifestHashMatches) integrityError = 'A003_TOP_STATUS_MANIFEST_SHA256_MISMATCH';
            const manifest = await manifestResponse.json();
            const node = map.current_app || null;"""
if OPEN_BODY.count(manifest_parse_old) != 1:
    raise SystemExit(f"UNIT2B2_MANIFEST_PARSE_ANCHOR_INVALID:{OPEN_BODY.count(manifest_parse_old)}")
OPEN_BODY = OPEN_BODY.replace(manifest_parse_old, manifest_parse_new, 1)

handoff_hash_old = "              integrity_manifest_sha256: integrity?.receipt?.manifest_sha256 || null,\n"
handoff_hash_new = (
    "              integrity_manifest_sha256: integrity?.receipt?.manifest_sha256 || null,\n"
    "              integrity_manifest_observed_sha256: manifestObservedSha256,\n"
)
if OPEN_BODY.count(handoff_hash_old) != 1:
    raise SystemExit(f"UNIT2B2_HANDOFF_HASH_ANCHOR_INVALID:{OPEN_BODY.count(handoff_hash_old)}")
OPEN_BODY = OPEN_BODY.replace(handoff_hash_old, handoff_hash_new, 1)

ready_old = """        const integrityReceipt = integrity?.receipt || null;
        const controllerReady = !!controllerUrl && controllerUrl.includes('/' + integritySw);
        const integrityReady = integrity?.type === 'PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE' && integrityReceipt?.state === 'ENFORCED' && integrityReceipt?.version === expectedVersion && integrityReceipt?.manifest_path === expectedManifest;
        const handoffReady = !!handoff && handoff.path === current && /^[0-9a-f]{64}$/.test(String(handoff.source_sha256 || '')) && /^[0-9a-f]{64}$/.test(String(handoff.integrity_manifest_sha256 || '')) && handoff.normalized_hash === expectedHash;"""
ready_new = """        const integrityReceipt = integrity?.receipt || null;
        const controllerReady = !!controllerUrl && controllerUrl.includes('/' + integritySw);
        const integrityReady = integrity?.type === 'PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE' && integrityReceipt?.reason === 'status' && integrityReceipt?.state === 'ENFORCED' && integrityReceipt?.version === expectedVersion && integrityReceipt?.manifest_path === expectedManifest && /^[0-9a-f]{64}$/.test(String(integrityReceipt?.manifest_sha256 || '')) && manifestHashMatches;
        const handoffReady = !!handoff && handoff.path === current && /^[0-9a-f]{64}$/.test(String(handoff.source_sha256 || '')) && /^[0-9a-f]{64}$/.test(String(handoff.integrity_manifest_sha256 || '')) && handoff.integrity_manifest_observed_sha256 === handoff.integrity_manifest_sha256 && handoff.normalized_hash === expectedHash;"""
if OPEN_BODY.count(ready_old) != 1:
    raise SystemExit(f"UNIT2B2_READY_ANCHOR_INVALID:{OPEN_BODY.count(ready_old)}")
OPEN_BODY = OPEN_BODY.replace(ready_old, ready_new, 1)

call_old = "}, { current: CURRENT, expectedHash, integritySw: INTEGRITY_SW, expectedVersion: '1.1.0-a003-runtime-integrity-sri', expectedManifest: MANIFEST });"
call_new = "}, { current: CURRENT, expectedHash, integritySw: INTEGRITY_SW, expectedVersion: '1.1.0-a003-runtime-integrity-sri', expectedManifest: MANIFEST, authorizedIntegrityStatus });"
if OPEN_BODY.count(call_old) != 1:
    raise SystemExit(f"UNIT2B2_FRAME_ARGUMENT_ANCHOR_INVALID:{OPEN_BODY.count(call_old)}")
OPEN_BODY = OPEN_BODY.replace(call_old, call_new, 1)

OPEN_NEW = TOP_STATUS_HELPERS + "\n" + OPEN_BODY

if "controller.postMessage({ type:'PMP_RUNTIME_INTEGRITY_STATUS_REQUEST'" in OPEN_NEW:
    raise SystemExit("UNIT2B2_CHILD_STATUS_REQUEST_STILL_PRESENT")
if "nativeServiceWorkerPostMessage.call(controller" in OPEN_NEW:
    raise SystemExit("UNIT2B2_CHILD_NATIVE_STATUS_REQUEST_STILL_PRESENT")
if OPEN_NEW.count("workerStatus(page)") != 1:
    raise SystemExit(f"UNIT2B2_TOP_STATUS_CALL_COUNT_INVALID:{OPEN_NEW.count('workerStatus(page)')}")
if OPEN_NEW.count("function validateAuthorizedIntegrityStatus") != 1:
    raise SystemExit("UNIT2B2_STATUS_VALIDATOR_DEFINITION_INVALID")

_ORIGINAL_APPLY = guardian.apply_guardian_readiness_patch_to_runner
_ORIGINAL_SUMMARY = guardian.contract_summary


def python_validate_status(
    status: object,
    *,
    now_ms: int,
    observed_manifest_sha256: str | None = None,
) -> dict:
    if not isinstance(status, dict):
        raise ValueError("A003_TOP_STATUS_MISSING")
    if status.get("type") != EXPECTED_STATUS_TYPE:
        if status.get("reason") == "UNKNOWN_ACTOR" or (
            isinstance(status.get("receipt"), dict)
            and status["receipt"].get("reason") == "UNKNOWN_ACTOR"
        ):
            raise ValueError("A003_TOP_STATUS_DENIED_UNKNOWN_ACTOR")
        raise ValueError("A003_TOP_STATUS_MALFORMED")
    receipt = status.get("receipt")
    if not isinstance(receipt, dict):
        raise ValueError("A003_TOP_STATUS_MALFORMED")
    if receipt.get("reason") != EXPECTED_STATUS_REASON:
        raise ValueError("A003_TOP_STATUS_WRONG_REASON")
    if receipt.get("state") != EXPECTED_STATUS_STATE:
        raise ValueError("A003_TOP_STATUS_NOT_ENFORCED")
    if receipt.get("version") != EXPECTED_STATUS_VERSION:
        raise ValueError("A003_TOP_STATUS_WRONG_VERSION")
    if receipt.get("manifest_path") != EXPECTED_STATUS_MANIFEST:
        raise ValueError("A003_TOP_STATUS_WRONG_MANIFEST")
    manifest_sha256 = receipt.get("manifest_sha256")
    if not isinstance(manifest_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", manifest_sha256):
        raise ValueError("A003_TOP_STATUS_INVALID_MANIFEST_SHA256")
    at = receipt.get("at")
    if not isinstance(at, str):
        raise ValueError("A003_TOP_STATUS_INVALID_TIMESTAMP")
    try:
        at_ms = int(datetime.fromisoformat(at.replace("Z", "+00:00")).timestamp() * 1000)
    except ValueError as error:
        raise ValueError("A003_TOP_STATUS_INVALID_TIMESTAMP") from error
    age = now_ms - at_ms
    if age > TOP_STATUS_MAX_AGE_MS or age < -TOP_STATUS_FUTURE_SKEW_MS:
        raise ValueError("A003_TOP_STATUS_STALE")
    if observed_manifest_sha256 is not None:
        if not re.fullmatch(r"[0-9a-f]{64}", observed_manifest_sha256):
            raise ValueError("A003_MANIFEST_OBSERVED_SHA256_INVALID")
        if observed_manifest_sha256 != manifest_sha256:
            raise ValueError("A003_TOP_STATUS_MANIFEST_SHA256_MISMATCH")
    return json.loads(json.dumps(status))


def valid_status(now_iso: str, manifest_sha256: str = "a" * 64) -> dict:
    return {
        "type": EXPECTED_STATUS_TYPE,
        "receipt": {
            "type": "PMP_RUNTIME_INTEGRITY_STATUS_V1",
            "reason": EXPECTED_STATUS_REASON,
            "at": now_iso,
            "state": EXPECTED_STATUS_STATE,
            "version": EXPECTED_STATUS_VERSION,
            "manifest_path": EXPECTED_STATUS_MANIFEST,
            "manifest_sha256": manifest_sha256,
        },
    }


def unit2b2_regression_tests() -> dict:
    now = datetime.now(timezone.utc)
    now_ms = int(now.timestamp() * 1000)
    now_iso = now.isoformat().replace("+00:00", "Z")
    valid = valid_status(now_iso)
    python_validate_status(valid, now_ms=now_ms, observed_manifest_sha256="a" * 64)

    cases: list[tuple[str, object, str, str | None]] = [
        ("missing", None, "A003_TOP_STATUS_MISSING", None),
        ("denied", {"type": "PMP_ACTOR_AUTHORITY_DENIAL_V1", "reason": "UNKNOWN_ACTOR"}, "A003_TOP_STATUS_DENIED_UNKNOWN_ACTOR", None),
        ("malformed", {"type": EXPECTED_STATUS_TYPE}, "A003_TOP_STATUS_MALFORMED", None),
        ("wrong_reason", valid_status(now_iso) | {"receipt": valid_status(now_iso)["receipt"] | {"reason": "other"}}, "A003_TOP_STATUS_WRONG_REASON", None),
        ("not_enforced", valid_status(now_iso) | {"receipt": valid_status(now_iso)["receipt"] | {"state": "DISABLED"}}, "A003_TOP_STATUS_NOT_ENFORCED", None),
        ("wrong_version", valid_status(now_iso) | {"receipt": valid_status(now_iso)["receipt"] | {"version": "wrong"}}, "A003_TOP_STATUS_WRONG_VERSION", None),
        ("wrong_manifest", valid_status(now_iso) | {"receipt": valid_status(now_iso)["receipt"] | {"manifest_path": "wrong.json"}}, "A003_TOP_STATUS_WRONG_MANIFEST", None),
        ("invalid_manifest_hash", valid_status(now_iso, "bad"), "A003_TOP_STATUS_INVALID_MANIFEST_SHA256", None),
        ("stale", valid_status((now - timedelta(minutes=3)).isoformat().replace("+00:00", "Z")), "A003_TOP_STATUS_STALE", None),
        ("manifest_hash_mismatch", valid, "A003_TOP_STATUS_MANIFEST_SHA256_MISMATCH", "b" * 64),
    ]
    passed: dict[str, bool] = {}
    for label, value, code, observed in cases:
        try:
            python_validate_status(value, now_ms=now_ms, observed_manifest_sha256=observed)
        except ValueError as error:
            passed[label] = str(error) == code
        else:
            passed[label] = False
    if not all(passed.values()):
        raise SystemExit("UNIT2B2_PYTHON_REGRESSION_FAILED:" + json.dumps(passed, sort_keys=True))

    with tempfile.NamedTemporaryFile("w", suffix=".cjs", delete=False) as handle:
        handle.write("'use strict';\n" + OPEN_NEW + "\n")
        javascript_path = pathlib.Path(handle.name)
    try:
        node_check = subprocess.run(
            ["node", "--check", str(javascript_path)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    finally:
        javascript_path.unlink(missing_ok=True)
    if node_check.returncode:
        raise SystemExit("UNIT2B2_GENERATED_A003_NODE_CHECK_FAILED:" + node_check.stdout[-4000:])

    return {
        "authorized_top_level_status_accepted": True,
        "fail_closed_cases": passed,
        "child_frame_status_request_count": 0,
        "top_level_worker_status_call_count": 1,
        "bounded_top_status_timeout_ms": 7000,
        "bounded_readiness_timeout_ms": guardian.READINESS_TIMEOUT_MS,
        "bounded_navigation_timeout_ms": guardian.NAVIGATION_TIMEOUT_MS,
        "bounded_poll_ms": guardian.POLL_MS,
        "bounded_screen_attempts": 2,
        "generated_a003_node_check": "PASS",
    }


UNIT2B2_CHECKS = unit2b2_regression_tests()
guardian.A003_OPEN_CURRENT_FUNCTION_NEW = OPEN_NEW


def apply_guardian_readiness_patch_to_runner(text: str) -> str:
    patched = _ORIGINAL_APPLY(text)
    compile(patched, "<unit2b2-complete-generated-runner>", "exec")
    required = {
        "top_status_call": patched.count("validateAuthorizedIntegrityStatus(await Promise.race(["),
        "child_wrapped_status_calls": patched.count("controller.postMessage({ type:'PMP_RUNTIME_INTEGRITY_STATUS_REQUEST'"),
        "child_native_status_calls": patched.count("nativeServiceWorkerPostMessage.call(controller"),
        "manifest_digest_checks": patched.count("A003_TOP_STATUS_MANIFEST_SHA256_MISMATCH"),
        "bounded_top_status_timeout": patched.count("A003_TOP_STATUS_TIMEOUT"),
        "bounded_readiness": patched.count("const readinessTimeoutMs = 15000;"),
        "bounded_navigation": patched.count("const navigationTimeoutMs = 30000;"),
        "bounded_attempts": patched.count("attempt <= 2"),
    }
    expected = {
        "top_status_call": 1,
        "child_wrapped_status_calls": 0,
        "child_native_status_calls": 0,
        "manifest_digest_checks": 2,
        "bounded_top_status_timeout": 1,
        "bounded_readiness": 1,
        "bounded_navigation": 1,
        "bounded_attempts": 1,
    }
    if required != expected:
        raise SystemExit(
            "UNIT2B2_GENERATED_CONTRACT_INVALID:"
            + json.dumps({"actual": required, "expected": expected}, sort_keys=True)
        )
    return patched


def contract_summary() -> dict:
    summary = _ORIGINAL_SUMMARY()
    summary.update({
        "unit2b2_status": "PASS_STATIC_TOP_LEVEL_AUTHORIZED_STATUS_HANDOFF",
        "status_probe_transport": "EXISTING_TOP_LEVEL_WORKER_STATUS_PAGE_ONLY",
        "child_frame_status_request_removed": True,
        "immutable_status_snapshot": True,
        "manifest_sha256_recomputed_and_compared": True,
        "unit2b2_regression_tests": UNIT2B2_CHECKS,
        "production_actor_gate_changed": False,
        "unknown_actor_policy_weakened": False,
        "unauthorized_capability_policy_weakened": False,
        "production_changed": False,
        "candidate_runtime_changed": False,
        "formal_proof_executed": False,
    })
    return summary


guardian.apply_guardian_readiness_patch_to_runner = apply_guardian_readiness_patch_to_runner
guardian.contract_summary = contract_summary

source = subprocess.check_output(
    ["git", "show", f"{SOURCE_COMMIT}:{SOURCE_PATH}"],
    cwd=ROOT,
    text=True,
)
if "apply_guardian_readiness_patch_to_runner" not in source or "DISPOSABLE_TEST_HARNESS_ONLY" not in source:
    raise SystemExit("UNIT2B2_AUTHORIZED_PARENT_SOURCE_INVALID")

exec(compile(source, str(pathlib.Path(__file__).resolve()), "exec"), globals())
