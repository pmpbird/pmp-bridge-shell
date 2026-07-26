#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "audit/pass6/pass6-ci-lane-artifact-policy-v1.json"
ENVELOPE_PATH = ROOT / "audit/pass6/fixtures/pass6-unit5-ci-evidence-envelope-positive-v1.json"
POLICY_TYPE = "PMP_PASS6_CI_LANE_ARTIFACT_POLICY_V1"
ENVELOPE_TYPE = "PMP_PASS6_CI_EVIDENCE_ENVELOPE_V1"
RESULT_TYPE = "PMP_PASS6_CI_EVIDENCE_EVALUATION_RESULT_V1"
VERSION = "1.0.0"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")


def canonical(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: canonical(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [canonical(item) for item in value]
    return value


def digest(value: Any) -> str:
    payload = json.dumps(canonical(value), separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(payload).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text())
    relative = path.relative_to(ROOT).as_posix()
    payload = subprocess.check_output(["git", "show", f"HEAD:{relative}"], cwd=ROOT)
    return json.loads(payload)


def add_error(errors: list[dict[str, Any]], code: str, message: str, evidence: Any = None) -> None:
    errors.append({"code": code, "message": message, "evidence": evidence})


def unique_strings(
    value: Any,
    errors: list[dict[str, Any]],
    code: str,
    label: str,
    *,
    allow_empty: bool = False,
) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        add_error(errors, code, f"{label} must be a non-empty array")
        return []
    out: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not item:
            add_error(errors, code, f"{label} entries must be non-empty strings", item)
            continue
        if item in seen:
            add_error(errors, code, f"{label} contains a duplicate", item)
            continue
        seen.add(item)
        out.append(item)
    return out


def safe_artifact_path(path: Any, attempt_id: str) -> bool:
    if not isinstance(path, str) or not path:
        return False
    pure = PurePosixPath(path)
    return (
        not pure.is_absolute()
        and ".." not in pure.parts
        and "." not in pure.parts
        and pure.parts[:2] == ("artifacts", attempt_id)
        and len(pure.parts) >= 3
    )


def validate_policy(policy: Any, errors: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(policy, dict):
        add_error(errors, "POLICY_MALFORMED", "policy must be an object")
        return {}
    if policy.get("type") != POLICY_TYPE or policy.get("version") != VERSION:
        add_error(errors, "POLICY_IDENTITY_INVALID", "unsupported policy type or version")
    checks = unique_strings(
        policy.get("required_checks"),
        errors,
        "POLICY_CHECKS_INVALID",
        "policy.required_checks",
    )
    roles = unique_strings(
        policy.get("artifact_roles"),
        errors,
        "POLICY_ARTIFACT_ROLES_INVALID",
        "policy.artifact_roles",
    )
    lanes = policy.get("lanes")
    if not isinstance(lanes, dict) or not lanes:
        add_error(errors, "POLICY_LANES_INVALID", "policy.lanes must be a non-empty object")
        lanes = {}
    for name, lane in lanes.items():
        if not IDENTIFIER.fullmatch(name) or not isinstance(lane, dict):
            add_error(errors, "POLICY_LANE_MALFORMED", "lane is malformed", name)
            continue
        if lane.get("authority") not in {
            "NONE",
            "EXPLICIT_SEALED_SINGLE_USE",
            "EXPLICIT_SEALED_EXACTLY_ONCE",
        }:
            add_error(errors, "POLICY_LANE_AUTHORITY_INVALID", "lane authority is invalid", name)
        if lane.get("max_attempts") != 1:
            add_error(errors, "POLICY_LANE_ATTEMPT_LIMIT_INVALID", "every lane must allow exactly one attempt", name)
        if lane.get("required_artifact_roles") != "ALL":
            add_error(errors, "POLICY_LANE_ARTIFACT_RULE_INVALID", "every lane must require all artifacts", name)
    return {"checks": checks, "roles": roles, "lanes": lanes}


def evaluate(policy: Any, envelope: Any) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    policy_state = validate_policy(policy, errors)
    if not isinstance(envelope, dict):
        add_error(errors, "ENVELOPE_MALFORMED", "evidence envelope must be an object")
        envelope = {}
    if envelope.get("type") != ENVELOPE_TYPE or envelope.get("version") != VERSION:
        add_error(errors, "ENVELOPE_IDENTITY_INVALID", "unsupported envelope type or version")

    run_id = envelope.get("run_id")
    if not isinstance(run_id, str) or not IDENTIFIER.fullmatch(run_id):
        add_error(errors, "RUN_ID_INVALID", "run_id must be a stable identifier", run_id)
    commit = envelope.get("commit")
    if not isinstance(commit, str) or not COMMIT.fullmatch(commit):
        add_error(errors, "COMMIT_INVALID", "commit must be an exact lowercase SHA-1", commit)

    lane_name = envelope.get("lane")
    lane = policy_state["lanes"].get(lane_name)
    if lane is None:
        add_error(errors, "LANE_UNKNOWN", "envelope lane is not declared", lane_name)
        lane = {}

    scope = envelope.get("scope")
    if not isinstance(scope, dict):
        add_error(errors, "SCOPE_MALFORMED", "scope must be an object")
        scope = {}
    allowed = unique_strings(
        scope.get("allowed_paths"),
        errors,
        "SCOPE_ALLOWED_INVALID",
        "scope.allowed_paths",
    )
    changed = unique_strings(
        scope.get("changed_paths"),
        errors,
        "SCOPE_CHANGED_INVALID",
        "scope.changed_paths",
    )
    if set(allowed) != set(changed):
        add_error(
            errors,
            "SCOPE_MISMATCH",
            "changed paths must equal allowed paths exactly",
            {
                "unexpected": sorted(set(changed) - set(allowed)),
                "missing": sorted(set(allowed) - set(changed)),
            },
        )

    checks = envelope.get("checks")
    if not isinstance(checks, dict):
        add_error(errors, "CHECKS_MALFORMED", "checks must be an object")
        checks = {}
    expected_checks = set(policy_state["checks"])
    actual_checks = set(checks)
    if actual_checks != expected_checks:
        add_error(
            errors,
            "CHECK_SET_MISMATCH",
            "check names must equal the policy set",
            {
                "missing": sorted(expected_checks - actual_checks),
                "unknown": sorted(actual_checks - expected_checks),
            },
        )
    for name in sorted(expected_checks):
        if checks.get(name) != "PASS":
            add_error(errors, "REQUIRED_CHECK_NOT_PASS", "required check did not pass", name)

    authority = envelope.get("authority")
    if not isinstance(authority, dict):
        add_error(errors, "AUTHORITY_STATE_MALFORMED", "authority must be an object")
        authority = {}
    authority_rule = lane.get("authority")
    special_lane = authority_rule in {
        "EXPLICIT_SEALED_SINGLE_USE",
        "EXPLICIT_SEALED_EXACTLY_ONCE",
    }
    if special_lane:
        if authority.get("required") is not True or authority.get("granted") is not True:
            add_error(errors, "AUTHORITY_NOT_GRANTED", "special lane requires explicit granted authority")
        if not isinstance(authority.get("authorization_id"), str) or not IDENTIFIER.fullmatch(
            authority.get("authorization_id", "")
        ):
            add_error(errors, "AUTHORIZATION_ID_INVALID", "special lane requires a stable authorization id")
        if authority.get("authorized_commit") != commit:
            add_error(errors, "AUTHORIZED_COMMIT_MISMATCH", "authority commit must match the run commit")
        if authority.get("consumed_before") is not False:
            add_error(errors, "AUTHORITY_ALREADY_CONSUMED", "authority was consumed before this run")
        if authority.get("consumed_after") is not True:
            add_error(errors, "AUTHORITY_CONSUMPTION_MISSING", "special lane must preserve consumption")
    else:
        for key in ("required", "granted", "consumed_before", "consumed_after"):
            if authority.get(key) is not False:
                add_error(errors, "UNEXPECTED_AUTHORITY_STATE", "ordinary lane cannot consume special authority", key)
        if authority.get("authorization_id") is not None or authority.get("authorized_commit") is not None:
            add_error(errors, "UNEXPECTED_AUTHORITY_BINDING", "ordinary lane cannot carry a special binding")

    attempts = envelope.get("attempts")
    if not isinstance(attempts, list) or not attempts:
        add_error(errors, "ATTEMPTS_MISSING", "at least one attempt is required")
        attempts = []
    max_attempts = lane.get("max_attempts", 0)
    if len(attempts) > max_attempts:
        add_error(
            errors,
            "RETRY_POLICY_VIOLATION",
            "the lane permits exactly one preserved attempt",
            {"attempts": len(attempts), "max_attempts": max_attempts},
        )
    attempt_ids: set[str] = set()
    statuses: list[str] = []
    artifacts_total = 0
    expected_roles = set(policy_state["roles"])
    for index, attempt in enumerate(attempts):
        if not isinstance(attempt, dict):
            add_error(errors, "ATTEMPT_MALFORMED", "attempt must be an object", index)
            continue
        attempt_id = attempt.get("attempt_id")
        if not isinstance(attempt_id, str) or not IDENTIFIER.fullmatch(attempt_id):
            add_error(errors, "ATTEMPT_ID_INVALID", "attempt id is invalid", attempt_id)
            attempt_id = f"invalid-{index}"
        elif attempt_id in attempt_ids:
            add_error(errors, "ATTEMPT_ID_DUPLICATE", "attempt id is duplicated", attempt_id)
        attempt_ids.add(attempt_id)
        if attempt.get("commit") != commit:
            add_error(errors, "ATTEMPT_COMMIT_MISMATCH", "attempt commit differs from the run", attempt_id)
        start = attempt.get("sequence_started")
        end = attempt.get("sequence_completed")
        if not isinstance(start, int) or not isinstance(end, int) or start < 0 or end <= start:
            add_error(errors, "ATTEMPT_SEQUENCE_INVALID", "attempt sequence is not monotonic", attempt_id)
        status = attempt.get("status")
        exit_code = attempt.get("exit_code")
        if status not in {"PASS", "FAIL"}:
            add_error(errors, "ATTEMPT_STATUS_INVALID", "attempt status must be PASS or FAIL", attempt_id)
        else:
            statuses.append(status)
        if not isinstance(exit_code, int) or exit_code < 0:
            add_error(errors, "ATTEMPT_EXIT_CODE_INVALID", "exit code must be a non-negative integer", attempt_id)
        elif (status == "PASS" and exit_code != 0) or (status == "FAIL" and exit_code == 0):
            add_error(errors, "ATTEMPT_STATUS_EXIT_MISMATCH", "status and exit code disagree", attempt_id)

        artifacts = attempt.get("artifacts")
        if not isinstance(artifacts, list):
            add_error(errors, "ARTIFACTS_MALFORMED", "attempt artifacts must be an array", attempt_id)
            artifacts = []
        artifacts_total += len(artifacts)
        roles: set[str] = set()
        paths: set[str] = set()
        hashes: set[str] = set()
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                add_error(errors, "ARTIFACT_MALFORMED", "artifact must be an object", attempt_id)
                continue
            role = artifact.get("role")
            if role not in expected_roles:
                add_error(errors, "ARTIFACT_ROLE_UNKNOWN", "artifact role is not declared", role)
            elif role in roles:
                add_error(errors, "ARTIFACT_ROLE_DUPLICATE", "artifact role is duplicated", role)
            roles.add(role)
            artifact_path = artifact.get("path")
            if not safe_artifact_path(artifact_path, attempt_id):
                add_error(errors, "ARTIFACT_PATH_INVALID", "artifact path is unsafe or outside its attempt", artifact_path)
            elif artifact_path in paths:
                add_error(errors, "ARTIFACT_PATH_DUPLICATE", "artifact path is duplicated", artifact_path)
            paths.add(artifact_path)
            size = artifact.get("bytes")
            if not isinstance(size, int) or size <= 0:
                add_error(errors, "ARTIFACT_BYTES_INVALID", "artifact bytes must be positive", {"role": role, "bytes": size})
            sha256 = artifact.get("sha256")
            if not isinstance(sha256, str) or not SHA256.fullmatch(sha256):
                add_error(errors, "ARTIFACT_SHA256_INVALID", "artifact SHA-256 is invalid", role)
            elif sha256 in hashes:
                add_error(errors, "ARTIFACT_SHA256_DUPLICATE", "artifact SHA-256 is duplicated", role)
            hashes.add(sha256)
        if roles != expected_roles:
            add_error(
                errors,
                "ARTIFACT_ROLE_SET_MISMATCH",
                "attempt must preserve every required artifact role exactly once",
                {
                    "attempt_id": attempt_id,
                    "missing": sorted(expected_roles - roles),
                    "unknown": sorted(roles - expected_roles),
                },
            )

    flake_detected = len(set(statuses)) > 1
    if flake_detected:
        add_error(errors, "FLAKE_DETECTED", "attempt outcomes differ; green is forbidden", statuses)
    if any(status == "FAIL" for status in statuses):
        add_error(errors, "FAILED_ATTEMPT_PRESERVED", "a failed attempt makes the run non-green", statuses)

    if any(error["code"].startswith("AUTH") for error in errors):
        final_status = "AUTHORITY_REJECTED"
    elif any(error["code"].startswith("SCOPE") for error in errors):
        final_status = "SCOPE_REJECTED"
    elif any(error["code"].startswith("ARTIFACT") for error in errors):
        final_status = "ARTIFACT_INCOMPLETE"
    elif flake_detected:
        final_status = "FLAKE_DETECTED_FAIL"
    elif errors:
        final_status = "FAIL_CLOSED"
    else:
        final_status = "PASS"
    if envelope.get("expected_final_status") != final_status:
        add_error(
            errors,
            "EXPECTED_STATUS_MISMATCH",
            "envelope expected status differs from evaluation",
            {"expected": envelope.get("expected_final_status"), "actual": final_status},
        )
        if final_status == "PASS":
            final_status = "FAIL_CLOSED"

    result = {
        "type": RESULT_TYPE,
        "version": VERSION,
        "status": final_status,
        "run_id": run_id,
        "commit": commit,
        "lane": lane_name,
        "lane_class": lane.get("class"),
        "attempts": len(attempts),
        "artifacts": artifacts_total,
        "checks_required": len(expected_checks),
        "checks_passed": sum(checks.get(name) == "PASS" for name in expected_checks),
        "scope_paths": len(changed),
        "flake_detected": flake_detected,
        "errors": errors,
        "authority": {
            "rule": authority_rule,
            "special_lane": special_lane,
            "consumed": authority.get("consumed_after") is True,
        },
        "side_effects": {
            "network_requests": 0,
            "storage_writes": 0,
            "persisted_user_data_writes": 0,
            "route_changes": 0,
            "repairs": 0,
            "live_observations": 0,
            "formal_proofs": 0,
            "production_files_changed": 0,
        },
        "claim_ceiling": policy.get("claim_ceiling"),
    }
    result["result_sha256"] = digest(result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", type=Path, default=POLICY_PATH)
    parser.add_argument("--envelope", type=Path, default=ENVELOPE_PATH)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = evaluate(read_json(args.policy), read_json(args.envelope))
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload)
    print(payload, end="")
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
