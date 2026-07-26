#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from run_pass6_unit5_ci_evidence_policy_v1 import digest, evaluate, read_json  # noqa: E402

POLICY_PATH = ROOT / "audit/pass6/pass6-ci-lane-artifact-policy-v1.json"
ENVELOPE_PATH = ROOT / "audit/pass6/fixtures/pass6-unit5-ci-evidence-envelope-positive-v1.json"
POLICY = read_json(POLICY_PATH)
ENVELOPE = read_json(ENVELOPE_PATH)
ASSERTIONS = 0


def check(condition: bool, message: str) -> None:
    global ASSERTIONS
    ASSERTIONS += 1
    if not condition:
        raise AssertionError(message)


def equal(actual, expected, message: str) -> None:
    global ASSERTIONS
    ASSERTIONS += 1
    if actual != expected:
        raise AssertionError(f"{message}: {actual!r} != {expected!r}")


def mutated(fn):
    value = copy.deepcopy(ENVELOPE)
    fn(value)
    return value


def expect(code: str, fn, status: str | None = None):
    result = evaluate(POLICY, mutated(fn))
    check(result["status"] != "PASS", f"{code}: must fail")
    check(any(row["code"] == code for row in result["errors"]), f"{code}: code")
    check(len(result["result_sha256"]) == 64, f"{code}: hash")
    if status:
        equal(result["status"], status, f"{code}: status")
    equal(result["side_effects"], {key: 0 for key in (
        "network_requests",
        "storage_writes",
        "persisted_user_data_writes",
        "route_changes",
        "repairs",
        "live_observations",
        "formal_proofs",
        "production_files_changed",
    )}, f"{code}: side effects")
    return result


baseline = evaluate(POLICY, ENVELOPE)
repeat = evaluate(POLICY, ENVELOPE)
equal(baseline, repeat, "repeated evaluation is identical")
equal(baseline["status"], "PASS", "baseline status")
equal(baseline["errors"], [], "baseline errors")
equal(baseline["lane"], "deterministic_browser_harness", "baseline lane")
equal(baseline["lane_class"], "DETERMINISTIC_SYNTHETIC_BROWSER_ADAPTER", "lane class")
equal(baseline["attempts"], 1, "one attempt")
equal(baseline["artifacts"], 9, "nine artifacts")
equal(baseline["checks_required"], 6, "six checks required")
equal(baseline["checks_passed"], 6, "six checks pass")
equal(baseline["scope_paths"], 4, "four exact paths")
equal(baseline["flake_detected"], False, "no flake")
equal(baseline["authority"]["special_lane"], False, "ordinary lane")
equal(baseline["authority"]["consumed"], False, "authority unconsumed")
check(len(baseline["result_sha256"]) == 64, "baseline hash length")
copy_result = copy.deepcopy(baseline)
expected_hash = copy_result.pop("result_sha256")
equal(digest(copy_result), expected_hash, "baseline hash recomputes")
check("cannot authorize" in baseline["claim_ceiling"], "claim ceiling")

for check_name in POLICY["required_checks"]:
    check(ENVELOPE["checks"][check_name] == "PASS", f"{check_name}: baseline")
for role in POLICY["artifact_roles"]:
    check(any(row["role"] == role for row in ENVELOPE["attempts"][0]["artifacts"]), f"{role}: baseline")
for lane_name, lane in POLICY["lanes"].items():
    equal(lane["max_attempts"], 1, f"{lane_name}: attempt limit")
    equal(lane["required_artifact_roles"], "ALL", f"{lane_name}: artifact rule")
    check("retry" in lane["retry_policy"].lower(), f"{lane_name}: explicit retry policy")

expect("ENVELOPE_IDENTITY_INVALID", lambda x: x.update(type="BAD"))
expect("RUN_ID_INVALID", lambda x: x.update(run_id="../bad"))
expect("COMMIT_INVALID", lambda x: x.update(commit="abc"))
expect("LANE_UNKNOWN", lambda x: x.update(lane="unknown"))
expect("SCOPE_ALLOWED_INVALID", lambda x: x["scope"].update(allowed_paths=[]), "SCOPE_REJECTED")
expect("SCOPE_CHANGED_INVALID", lambda x: x["scope"].update(changed_paths=[]), "SCOPE_REJECTED")
expect("SCOPE_MISMATCH", lambda x: x["scope"]["changed_paths"].append("unexpected.js"), "SCOPE_REJECTED")
expect("SCOPE_ALLOWED_INVALID", lambda x: x["scope"]["allowed_paths"].append(x["scope"]["allowed_paths"][0]), "SCOPE_REJECTED")
expect("SCOPE_CHANGED_INVALID", lambda x: x["scope"]["changed_paths"].append(x["scope"]["changed_paths"][0]), "SCOPE_REJECTED")
expect("CHECK_SET_MISMATCH", lambda x: x["checks"].pop("receipt"))
expect("CHECK_SET_MISMATCH", lambda x: x["checks"].update(unknown="PASS"))
for name in POLICY["required_checks"]:
    expect("REQUIRED_CHECK_NOT_PASS", lambda x, key=name: x["checks"].update({key: "FAIL"}))
expect("UNEXPECTED_AUTHORITY_STATE", lambda x: x["authority"].update(required=True))
expect("UNEXPECTED_AUTHORITY_STATE", lambda x: x["authority"].update(granted=True))
expect("UNEXPECTED_AUTHORITY_STATE", lambda x: x["authority"].update(consumed_before=True))
expect("UNEXPECTED_AUTHORITY_STATE", lambda x: x["authority"].update(consumed_after=True))
expect("UNEXPECTED_AUTHORITY_BINDING", lambda x: x["authority"].update(authorization_id="AUTH-1"))
expect("UNEXPECTED_AUTHORITY_BINDING", lambda x: x["authority"].update(authorized_commit=x["commit"]))
expect("ATTEMPTS_MISSING", lambda x: x.update(attempts=[]))
expect("RETRY_POLICY_VIOLATION", lambda x: x["attempts"].append(copy.deepcopy(x["attempts"][0])))
expect("ATTEMPT_ID_INVALID", lambda x: x["attempts"][0].update(attempt_id="../bad"))
expect("ATTEMPT_COMMIT_MISMATCH", lambda x: x["attempts"][0].update(commit="a" * 40))
expect("ATTEMPT_SEQUENCE_INVALID", lambda x: x["attempts"][0].update(sequence_completed=1))
expect("ATTEMPT_SEQUENCE_INVALID", lambda x: x["attempts"][0].update(sequence_started=-1))
expect("ATTEMPT_STATUS_INVALID", lambda x: x["attempts"][0].update(status="UNKNOWN"))
expect("ATTEMPT_EXIT_CODE_INVALID", lambda x: x["attempts"][0].update(exit_code=-1))
expect("ATTEMPT_STATUS_EXIT_MISMATCH", lambda x: x["attempts"][0].update(exit_code=1))
expect("ATTEMPT_STATUS_EXIT_MISMATCH", lambda x: x["attempts"][0].update(status="FAIL", exit_code=0))
expect("FAILED_ATTEMPT_PRESERVED", lambda x: x["attempts"][0].update(status="FAIL", exit_code=1))
expect("ARTIFACTS_MALFORMED", lambda x: x["attempts"][0].update(artifacts=None), "ARTIFACT_INCOMPLETE")

for index, role in enumerate(POLICY["artifact_roles"]):
    expect(
        "ARTIFACT_ROLE_SET_MISMATCH",
        lambda x, i=index: x["attempts"][0]["artifacts"].pop(i),
        "ARTIFACT_INCOMPLETE",
    )
    expect(
        "ARTIFACT_ROLE_UNKNOWN",
        lambda x, i=index: x["attempts"][0]["artifacts"][i].update(role=f"unknown-{i}"),
        "ARTIFACT_INCOMPLETE",
    )
    expect(
        "ARTIFACT_PATH_INVALID",
        lambda x, i=index: x["attempts"][0]["artifacts"][i].update(path="../escape"),
        "ARTIFACT_INCOMPLETE",
    )
    expect(
        "ARTIFACT_BYTES_INVALID",
        lambda x, i=index: x["attempts"][0]["artifacts"][i].update(bytes=0),
        "ARTIFACT_INCOMPLETE",
    )
    expect(
        "ARTIFACT_SHA256_INVALID",
        lambda x, i=index: x["attempts"][0]["artifacts"][i].update(sha256="bad"),
        "ARTIFACT_INCOMPLETE",
    )

expect(
    "ARTIFACT_ROLE_DUPLICATE",
    lambda x: x["attempts"][0]["artifacts"][1].update(role="command"),
    "ARTIFACT_INCOMPLETE",
)
expect(
    "ARTIFACT_PATH_DUPLICATE",
    lambda x: x["attempts"][0]["artifacts"][1].update(
        path=x["attempts"][0]["artifacts"][0]["path"]
    ),
    "ARTIFACT_INCOMPLETE",
)
expect(
    "ARTIFACT_SHA256_DUPLICATE",
    lambda x: x["attempts"][0]["artifacts"][1].update(
        sha256=x["attempts"][0]["artifacts"][0]["sha256"]
    ),
    "ARTIFACT_INCOMPLETE",
)
expect("EXPECTED_STATUS_MISMATCH", lambda x: x.update(expected_final_status="FAIL_CLOSED"))

def live_envelope(authority_rule: str):
    value = copy.deepcopy(ENVELOPE)
    value["lane"] = authority_rule
    value["authority"] = {
        "required": True,
        "granted": True,
        "authorization_id": "AUTH-P6-U5-TEST-001",
        "authorized_commit": value["commit"],
        "consumed_before": False,
        "consumed_after": True,
    }
    return value


for lane in ("bounded_live_observation", "formal_proof_exactly_once"):
    special = live_envelope(lane)
    result = evaluate(POLICY, special)
    equal(result["status"], "PASS", f"{lane}: exact authority passes")
    equal(result["authority"]["special_lane"], True, f"{lane}: special")
    equal(result["authority"]["consumed"], True, f"{lane}: consumed")
    for key, code in (
        ("required", "AUTHORITY_NOT_GRANTED"),
        ("granted", "AUTHORITY_NOT_GRANTED"),
        ("consumed_before", "AUTHORITY_ALREADY_CONSUMED"),
        ("consumed_after", "AUTHORITY_CONSUMPTION_MISSING"),
    ):
        bad = copy.deepcopy(special)
        bad["authority"][key] = not bad["authority"][key]
        bad["expected_final_status"] = "AUTHORITY_REJECTED"
        checked = evaluate(POLICY, bad)
        equal(checked["status"], "AUTHORITY_REJECTED", f"{lane}:{key}: status")
        check(any(row["code"] == code for row in checked["errors"]), f"{lane}:{key}: code")
    bad = copy.deepcopy(special)
    bad["authority"]["authorization_id"] = None
    bad["expected_final_status"] = "AUTHORITY_REJECTED"
    check(any(row["code"] == "AUTHORIZATION_ID_INVALID" for row in evaluate(POLICY, bad)["errors"]), f"{lane}: auth id")
    bad = copy.deepcopy(special)
    bad["authority"]["authorized_commit"] = "a" * 40
    bad["expected_final_status"] = "AUTHORITY_REJECTED"
    check(any(row["code"] == "AUTHORIZED_COMMIT_MISMATCH" for row in evaluate(POLICY, bad)["errors"]), f"{lane}: commit")
    bad = copy.deepcopy(special)
    second = copy.deepcopy(bad["attempts"][0])
    second["attempt_id"] = "attempt-002"
    second["sequence_started"] = 3
    second["sequence_completed"] = 4
    for artifact in second["artifacts"]:
        artifact["path"] = artifact["path"].replace("attempt-001", "attempt-002")
        artifact["sha256"] = ("a" if artifact["sha256"][0] != "a" else "b") * 64
    bad["attempts"].append(second)
    bad["expected_final_status"] = "FAIL_CLOSED"
    checked = evaluate(POLICY, bad)
    check(any(row["code"] == "RETRY_POLICY_VIOLATION" for row in checked["errors"]), f"{lane}: retry")

flake = copy.deepcopy(ENVELOPE)
second = copy.deepcopy(flake["attempts"][0])
second["attempt_id"] = "attempt-002"
second["sequence_started"] = 3
second["sequence_completed"] = 4
second["status"] = "FAIL"
second["exit_code"] = 1
for position, artifact in enumerate(second["artifacts"]):
    artifact["path"] = artifact["path"].replace("attempt-001", "attempt-002")
    artifact["sha256"] = f"{position + 10:064x}"
flake["attempts"].append(second)
flake["expected_final_status"] = "FLAKE_DETECTED_FAIL"
flake_result = evaluate(POLICY, flake)
equal(flake_result["status"], "FLAKE_DETECTED_FAIL", "flake is never green")
equal(flake_result["flake_detected"], True, "flake detected")
check(any(row["code"] == "FLAKE_DETECTED" for row in flake_result["errors"]), "flake code")
check(any(row["code"] == "FAILED_ATTEMPT_PRESERVED" for row in flake_result["errors"]), "failed attempt preserved")

command = subprocess.check_output(
    [
        sys.executable,
        "tools/run_pass6_unit5_ci_evidence_policy_v1.py",
        "--policy",
        str(POLICY_PATH.relative_to(ROOT)),
        "--envelope",
        str(ENVELOPE_PATH.relative_to(ROOT)),
    ],
    cwd=ROOT,
    text=True,
)
cli_result = json.loads(command)
equal(cli_result, baseline, "CLI matches direct evaluation")

print(f"PASS: P6-U5 CI lane, exact-scope, flake, and artifact policy ({ASSERTIONS}/{ASSERTIONS})")
