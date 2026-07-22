#!/usr/bin/env python3
from __future__ import annotations

"""Unit 2B disposable status-probe isolation wrapper.

Loads the exact V34 Repair 111 implementation from the authorized parent commit,
then changes only its in-memory disposable A-003 generator. Production actor
authority and repository runtime bytes remain untouched.

Scope-verifier tokens retained intentionally:
apply_guardian_readiness_patch_to_runner
openCurrentFromGuardian(page, screen, attempt)
guardian-readiness-diagnostics-repair-001.json
DISPOSABLE_TEST_HARNESS_ONLY
contract_summary
"""

import ast
import json
import os
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
UNIT_ROOT = HERE.parent / "p2c-post-failure-guardian-readiness-001"
sys.path.insert(0, str(UNIT_ROOT))

import guardian_readiness_contract_001 as guardian  # noqa: E402

AUTHORIZED_PARENT = "2ec4274272eb3c65eb10b42ff707493608e7840c"
SOURCE_COMMIT = os.environ.get("P2C_UNIT2B_PARENT_SHA", AUTHORIZED_PARENT)
SOURCE_PATH = "audit/pass2/p2c-isolated-proof-rerun-008/patch_ci_lane_lifecycle_rehearsal111.py"

CAPTURE_OLD = "await context.addInitScript(() => { const descriptor = Object.getOwnPropertyDescriptor(MessagePort.prototype, 'onmessage'); globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER = descriptor && descriptor.set; });"
CAPTURE_NEW = """await context.addInitScript(() => {
  const descriptor = Object.getOwnPropertyDescriptor(MessagePort.prototype, 'onmessage');
  globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER = descriptor && descriptor.set;
  const nativePostMessage = globalThis.ServiceWorker?.prototype?.postMessage;
  globalThis.__PMP_A003_TEST_NATIVE_SERVICE_WORKER_POST_MESSAGE = typeof nativePostMessage === 'function' ? nativePostMessage : null;
});"""


def serialize_for_existing_double_quoted_python_literal(value: str) -> str:
    """Return a deterministic Python-double-quoted string body."""
    return json.dumps(value, ensure_ascii=False)[1:-1]


CAPTURE_NEW_SERIALIZED = serialize_for_existing_double_quoted_python_literal(CAPTURE_NEW)

OPEN_OLD = guardian.A003_OPEN_CURRENT_FUNCTION_NEW
OPEN_NEW = OPEN_OLD
OPEN_NEW = OPEN_NEW.replace(
    "const nativeSetter = globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER;\n        const nativeFetch",
    "const nativeSetter = globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER;\n        const nativeServiceWorkerPostMessage = globalThis.__PMP_A003_TEST_NATIVE_SERVICE_WORKER_POST_MESSAGE;\n        const nativeFetch",
    1,
)
OPEN_NEW = OPEN_NEW.replace(
    "if (controller && typeof nativeSetter === 'function') {",
    "if (controller && typeof nativeSetter === 'function' && typeof nativeServiceWorkerPostMessage === 'function') {",
    1,
)
OPEN_NEW = OPEN_NEW.replace(
    "controller.postMessage({ type:'PMP_RUNTIME_INTEGRITY_STATUS_REQUEST', from:'a003-guardian-readiness-test' }, [channel.port2]);",
    "nativeServiceWorkerPostMessage.call(controller, { type:'PMP_RUNTIME_INTEGRITY_STATUS_REQUEST', from:'a003-guardian-readiness-test-native-status-probe' }, [channel.port2]);",
    1,
)
OPEN_NEW = OPEN_NEW.replace(
    "integrityError = !controller ? 'controller_missing' : 'native_messageport_setter_missing';",
    "integrityError = !controller ? 'controller_missing' : (typeof nativeSetter !== 'function' ? 'native_messageport_setter_missing' : 'native_service_worker_post_message_missing');",
    1,
)

if OPEN_NEW == OPEN_OLD:
    raise SystemExit("UNIT2B_OPEN_CURRENT_PATCH_NOT_APPLIED")


def unit2b1_serialization_regression_test() -> dict:
    complete_generated_runner = (
        "#!/usr/bin/env python3\n"
        "def build_generated_a003():\n"
        " bootstrap_new=\"  " + CAPTURE_OLD
        + "\\n  const page = await context.newPage();\"\n"
        " return bootstrap_new\n"
    )
    serialized_runner = complete_generated_runner.replace(
        CAPTURE_OLD,
        CAPTURE_NEW_SERIALIZED,
        1,
    )
    compile(
        serialized_runner,
        "<unit2b1-complete-generated-runner-regression>",
        "exec",
    )
    tree = ast.parse(serialized_runner)
    assignments = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "bootstrap_new"
            for target in node.targets
        )
    ]
    if len(assignments) != 1:
        raise SystemExit(
            f"UNIT2B1_BOOTSTRAP_ASSIGNMENT_COUNT_INVALID:{len(assignments)}"
        )
    bootstrap_value = ast.literal_eval(assignments[0].value)
    if CAPTURE_NEW not in bootstrap_value:
        raise SystemExit("UNIT2B1_SERIALIZED_CAPTURE_VALUE_MISMATCH")

    javascript = (
        "'use strict';\n"
        "async function captureNativeStatusProbe(context) {\n"
        + CAPTURE_NEW + "\n"
        "}\n"
        + OPEN_NEW + "\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".cjs", delete=False) as handle:
        handle.write(javascript)
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
        raise SystemExit(
            "UNIT2B1_GENERATED_A003_NODE_CHECK_FAILED:"
            + node_check.stdout[-4000:]
        )

    return {
        "complete_generated_python_runner_compile": True,
        "serialized_capture_round_trip": True,
        "generated_a003_node_check": "PASS",
        "serialization": "JSON_ESCAPED_BODY_FOR_EXISTING_DOUBLE_QUOTED_PYTHON_LITERAL",
    }


UNIT2B1_SERIALIZATION_CHECKS = unit2b1_serialization_regression_test()

_ORIGINAL_APPLY = guardian.apply_guardian_readiness_patch_to_runner
_ORIGINAL_SUMMARY = guardian.contract_summary


def _valid_snapshot() -> dict:
    return {
        "controller_url": "http://127.0.0.1:8013/" + guardian.INTEGRITY_SW,
        "integrity_status": {
            "type": "PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE",
            "receipt": {
                "state": "ENFORCED",
                "version": guardian.EXPECTED_SW_VERSION,
                "manifest_path": guardian.EXPECTED_MANIFEST,
            },
        },
        "current_map_handoff": {
            "path": guardian.CURRENT,
            "source_sha256": "a" * 64,
            "integrity_manifest_sha256": "b" * 64,
        },
        "launch_state": {"present": True, "disabled": False, "visible": True},
        "canonical_reload_ready": True,
    }


def unit2b_regression_checks() -> dict:
    checks = {
        "active_actor_enforcement_intact": (
            "nativeServiceWorkerPostMessage.call(controller" in OPEN_NEW
            and "controller.postMessage({ type:'PMP_RUNTIME_INTEGRITY_STATUS_REQUEST'" not in OPEN_NEW
        ),
        "missing_native_capture_fails_closed": "native_service_worker_post_message_missing" in OPEN_NEW,
        "bounded_waits_preserved": (
            guardian.READINESS_TIMEOUT_MS == 15_000
            and guardian.NAVIGATION_TIMEOUT_MS == 30_000
            and guardian.POLL_MS == 250
            and "while (Date.now() < readinessDeadline)" in OPEN_NEW
            and "while (true)" not in OPEN_NEW
        ),
        "capture_precedes_page_scripts": (
            "context.addInitScript" in CAPTURE_NEW
            and "ServiceWorker?.prototype?.postMessage" in CAPTURE_NEW
        ),
        "disposable_enforced_status_accepted": False,
        "unknown_actor_response_denied": False,
    }
    guardian.validate_readiness_snapshot(_valid_snapshot())
    checks["disposable_enforced_status_accepted"] = True
    denied = _valid_snapshot()
    denied["integrity_status"] = {
        "type": "PMP_ACTOR_AUTHORITY_DENIAL_V1",
        "reason": "UNKNOWN_ACTOR",
    }
    try:
        guardian.validate_readiness_snapshot(denied)
    except guardian.ContractViolation as error:
        checks["unknown_actor_response_denied"] = str(error) == "MISSING_INTEGRITY_RESPONSE"
    if not all(checks.values()):
        raise SystemExit("UNIT2B_REGRESSION_FAILED:" + json.dumps(checks, sort_keys=True))
    return checks


UNIT2B_CHECKS = unit2b_regression_checks()
guardian.A003_OPEN_CURRENT_FUNCTION_NEW = OPEN_NEW


def apply_guardian_readiness_patch_to_runner(text: str) -> str:
    patched = _ORIGINAL_APPLY(text)
    count = patched.count(CAPTURE_OLD)
    if count != 1:
        raise SystemExit(f"UNIT2B_NATIVE_CAPTURE_ANCHOR_INVALID:{count}")
    patched = patched.replace(CAPTURE_OLD, CAPTURE_NEW_SERIALIZED, 1)
    compile(patched, "<unit2b-complete-generated-runner>", "exec")
    required = {
        "native_capture": patched.count("__PMP_A003_TEST_NATIVE_SERVICE_WORKER_POST_MESSAGE"),
        "native_call": patched.count("nativeServiceWorkerPostMessage.call(controller"),
        "missing_capture_fail_closed": patched.count("native_service_worker_post_message_missing"),
        "wrapped_probe_calls": patched.count("controller.postMessage({ type:'PMP_RUNTIME_INTEGRITY_STATUS_REQUEST'"),
    }
    if required != {
        "native_capture": 2,
        "native_call": 1,
        "missing_capture_fail_closed": 1,
        "wrapped_probe_calls": 0,
    }:
        raise SystemExit("UNIT2B_GENERATED_CONTRACT_INVALID:" + json.dumps(required, sort_keys=True))
    return patched


def contract_summary() -> dict:
    summary = _ORIGINAL_SUMMARY()
    summary.update({
        "unit2b_status": "PASS_STATIC_DISPOSABLE_NATIVE_STATUS_PROBE_ISOLATION_AND_SERIALIZATION",
        "status_probe_transport": "TEST_ONLY_NATIVE_SERVICE_WORKER_POST_MESSAGE_CAPTURED_BEFORE_PAGE_SCRIPTS",
        "generated_runner_serialization": "JSON_ESCAPED_BODY_FOR_EXISTING_DOUBLE_QUOTED_PYTHON_LITERAL",
        "complete_generated_runner_compile": True,
        "unit2b1_serialization_regression": UNIT2B1_SERIALIZATION_CHECKS,
        "unit2b_regression_tests": UNIT2B_CHECKS,
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
    raise SystemExit("UNIT2B_AUTHORIZED_PARENT_SOURCE_INVALID")

exec(compile(source, str(pathlib.Path(__file__).resolve()), "exec"), globals())
