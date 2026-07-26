#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = ROOT / "audit/pass6/pass6-permanent-no-blind-flying-gate-v1.json"
POLICY_PATH = ROOT / "audit/pass6/pass6-ci-lane-artifact-policy-v1.json"
RESULT_TYPE = "PMP_PASS6_NO_BLIND_FLYING_GATE_RESULT_V1"
VERSION = "1.0.0"
UNIT_PATTERN = re.compile(r"^P(?:[7-9]|1[0-3])-U[1-9][0-9]*$")
LATER_AUDIT_PATTERN = re.compile(r"^audit/pass(?:[7-9]|1[0-3])/")
RUNTIME_EXTENSIONS = {".js", ".html", ".css", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"}
RUNTIME_EXCLUDED_PREFIXES = (".github/", "audit/", "tools/", "docs/")


def canonical(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: canonical(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [canonical(item) for item in value]
    return value


def stable_json(value: Any) -> str:
    return json.dumps(canonical(value), separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    payload = value if isinstance(value, bytes) else stable_json(value).encode()
    return hashlib.sha256(payload).hexdigest()


def output(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def changed_paths(base: str) -> list[str]:
    paths: set[str] = set()
    for command in (
        ("git", "diff", "--name-only", f"{base}...HEAD"),
        ("git", "diff", "--name-only", base),
        ("git", "ls-files", "--others", "--exclude-standard"),
    ):
        paths.update(filter(None, output(*command).splitlines()))
    return sorted(paths)


def path_exists(relative: str) -> bool:
    local = ROOT / relative
    if local.is_file():
        return True
    completed = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{relative}"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.returncode == 0


def is_runtime_path(relative: str) -> bool:
    if relative.startswith(RUNTIME_EXCLUDED_PREFIXES):
        return False
    return Path(relative).suffix.lower() in RUNTIME_EXTENSIONS


def is_candidate_record(relative: str) -> bool:
    return (
        bool(LATER_AUDIT_PATTERN.match(relative))
        and relative.endswith(".json")
        and "/fixtures/" not in relative
        and "/receipts/" not in relative
    )


def add_error(errors: list[dict[str, Any]], code: str, **evidence: Any) -> None:
    errors.append({"code": code, "evidence": canonical(evidence)})


def required_list(
    binding: dict[str, Any],
    key: str,
    errors: list[dict[str, Any]],
    code: str,
) -> list[Any]:
    value = binding.get(key)
    if not isinstance(value, list) or not value:
        add_error(errors, code, key=key)
        return []
    return value


def validate_record(
    record_path: str,
    record: dict[str, Any],
    changed: list[str],
    existing: set[str],
    policy: dict[str, Any],
) -> tuple[list[dict[str, Any]], str | None]:
    errors: list[dict[str, Any]] = []
    unit_id = record.get("unit_id")
    if not isinstance(unit_id, str) or not UNIT_PATTERN.fullmatch(unit_id):
        add_error(errors, "UNIT_ID_INVALID", value=unit_id)

    scope = record.get("scope")
    if not isinstance(scope, dict):
        add_error(errors, "SCOPE_MISSING")
        scope = {}
    declared_changed = scope.get("changed_paths")
    if not isinstance(declared_changed, list) or sorted(declared_changed) != changed:
        add_error(
            errors,
            "EXACT_SCOPE_MISMATCH",
            declared=sorted(declared_changed) if isinstance(declared_changed, list) else None,
            actual=changed,
        )
    implementation_paths = scope.get("implementation_paths")
    if not isinstance(implementation_paths, list):
        add_error(errors, "IMPLEMENTATION_PATHS_MISSING")
        implementation_paths = []
    runtime_paths = sorted(path for path in changed if is_runtime_path(path))
    if sorted(implementation_paths) != runtime_paths:
        add_error(
            errors,
            "IMPLEMENTATION_PATHS_MISMATCH",
            declared=sorted(implementation_paths),
            actual=runtime_paths,
        )

    binding = record.get("no_blind_flying_gate")
    if not isinstance(binding, dict):
        add_error(errors, "GATE_BINDING_MISSING", record_path=record_path)
        return errors, unit_id if isinstance(unit_id, str) else None
    if binding.get("type") != "PMP_PASS6_PERMANENT_NO_BLIND_FLYING_GATE_BINDING_V1":
        add_error(errors, "GATE_BINDING_TYPE_INVALID")
    if binding.get("version") != VERSION:
        add_error(errors, "GATE_BINDING_VERSION_INVALID")

    lane = binding.get("ci_lane")
    if lane not in policy.get("lanes", {}):
        add_error(errors, "CI_LANE_UNCLASSIFIED", lane=lane)

    matrix = binding.get("diagnostic_matrix_update")
    if not isinstance(matrix, dict):
        add_error(errors, "DIAGNOSTIC_MATRIX_UPDATE_MISSING")
    else:
        if matrix.get("status") not in {"ADDED", "UPDATED", "CONFIRMED_UNCHANGED"}:
            add_error(errors, "DIAGNOSTIC_MATRIX_STATUS_INVALID")
        if not isinstance(matrix.get("applicable_matrix"), str):
            add_error(errors, "DIAGNOSTIC_MATRIX_PATH_MISSING")
        elif matrix["applicable_matrix"] not in existing:
            add_error(
                errors,
                "DIAGNOSTIC_MATRIX_PATH_NOT_FOUND",
                path=matrix["applicable_matrix"],
            )
        if not isinstance(matrix.get("rationale"), str) or not matrix["rationale"].strip():
            add_error(errors, "DIAGNOSTIC_MATRIX_RATIONALE_MISSING")

    evidence_routes = required_list(
        binding, "diagnostic_evidence_routes", errors, "DIAGNOSTIC_EVIDENCE_ROUTE_MISSING"
    )
    tests = required_list(
        binding, "deterministic_test_paths", errors, "DETERMINISTIC_TEST_PATH_MISSING"
    )
    verifiers = required_list(binding, "verifier_paths", errors, "VERIFIER_PATH_MISSING")
    receipts = required_list(binding, "receipt_paths", errors, "RECEIPT_PATH_MISSING")
    for key, paths in (
        ("diagnostic", evidence_routes),
        ("test", tests),
        ("verifier", verifiers),
        ("receipt", receipts),
    ):
        for path in paths:
            if not isinstance(path, str) or path not in existing:
                add_error(errors, "REQUIRED_EVIDENCE_PATH_MISSING", role=key, path=path)
    for receipt in receipts:
        if isinstance(receipt, str) and receipt not in changed:
            add_error(errors, "RECEIPT_NOT_IN_EXACT_SCOPE", path=receipt)
    for test in tests:
        if isinstance(test, str) and test not in changed:
            add_error(errors, "TEST_NOT_IN_EXACT_SCOPE", path=test)
    for verifier in verifiers:
        if isinstance(verifier, str) and verifier not in changed:
            add_error(errors, "VERIFIER_NOT_IN_EXACT_SCOPE", path=verifier)

    observed = required_list(binding, "observed_facts", errors, "OBSERVED_FACT_MISSING")
    for index, claim in enumerate(observed):
        if not isinstance(claim, dict) or claim.get("claim_type") != "OBSERVED":
            add_error(errors, "OBSERVED_FACT_TYPE_INVALID", index=index)
            continue
        if not isinstance(claim.get("fact"), str) or not claim["fact"].strip():
            add_error(errors, "OBSERVED_FACT_TEXT_MISSING", index=index)
        evidence = claim.get("evidence_paths")
        if not isinstance(evidence, list) or not evidence:
            add_error(errors, "OBSERVED_FACT_EVIDENCE_MISSING", index=index)
        else:
            for path in evidence:
                if not isinstance(path, str) or path not in existing:
                    add_error(errors, "OBSERVED_FACT_EVIDENCE_PATH_MISSING", index=index, path=path)

    inferred = binding.get("inferred_conclusions")
    if not isinstance(inferred, list):
        add_error(errors, "INFERRED_CONCLUSIONS_FIELD_MISSING")
        inferred = []
    for index, claim in enumerate(inferred):
        if not isinstance(claim, dict) or claim.get("claim_type") != "INFERRED":
            add_error(errors, "INFERRED_CONCLUSION_TYPE_INVALID", index=index)
            continue
        if not isinstance(claim.get("conclusion"), str) or not claim["conclusion"].strip():
            add_error(errors, "INFERRED_CONCLUSION_TEXT_MISSING", index=index)
        basis = claim.get("basis_evidence_paths")
        if not isinstance(basis, list) or not basis:
            add_error(errors, "INFERRED_CONCLUSION_BASIS_MISSING", index=index)
        else:
            for path in basis:
                if not isinstance(path, str) or path not in existing:
                    add_error(errors, "INFERRED_CONCLUSION_BASIS_PATH_MISSING", index=index, path=path)

    fault = binding.get("fault_injection")
    if not isinstance(fault, dict):
        add_error(errors, "FAULT_INJECTION_DECISION_MISSING")
    elif fault.get("status") == "NOT_APPLICABLE":
        if not isinstance(fault.get("rationale"), str) or not fault["rationale"].strip():
            add_error(errors, "FAULT_NOT_APPLICABLE_RATIONALE_MISSING")
        if fault.get("cases") != []:
            add_error(errors, "FAULT_NOT_APPLICABLE_CASES_NONEMPTY")
    elif fault.get("status") == "COVERED":
        if not isinstance(fault.get("cases"), list) or not fault["cases"]:
            add_error(errors, "FAULT_CASES_MISSING")
    else:
        add_error(errors, "FAULT_INJECTION_STATUS_INVALID")

    expected_roles = policy.get("artifact_roles", [])
    roles = binding.get("required_artifact_roles")
    if roles != expected_roles:
        add_error(errors, "ARTIFACT_ROLES_MISMATCH", declared=roles, required=expected_roles)
    if binding.get("upload_before_enforcement") is not True:
        add_error(errors, "UPLOAD_BEFORE_ENFORCEMENT_REQUIRED")
    if binding.get("automatic_retry") is not False:
        add_error(errors, "AUTOMATIC_RETRY_FORBIDDEN")

    authority = binding.get("special_authority")
    if not isinstance(authority, dict):
        add_error(errors, "SPECIAL_AUTHORITY_STATE_MISSING")
    else:
        lane_contract = policy.get("lanes", {}).get(lane, {})
        special_lane = lane_contract.get("authority") not in (None, "NONE")
        if special_lane and authority.get("required") is not True:
            add_error(errors, "SPECIAL_AUTHORITY_REQUIRED_FOR_LANE", lane=lane)
        if authority.get("consumed") is True and authority.get("granted") is not True:
            add_error(errors, "CONSUMED_AUTHORITY_NOT_GRANTED")

    return errors, unit_id if isinstance(unit_id, str) else None


def evaluate(payload: dict[str, Any], gate: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    changed = sorted(set(payload.get("changed_paths", [])))
    existing = set(payload.get("existing_paths", []))
    raw_records = payload.get("records", [])
    records = [
        item for item in raw_records
        if isinstance(item, dict)
        and isinstance(item.get("payload"), dict)
        and isinstance(item["payload"].get("no_blind_flying_gate"), dict)
    ]
    errors: list[dict[str, Any]] = []
    unit_id: str | None = None

    if changed == sorted(gate["activation_scope"]):
        mode = "ACTIVATION_SCOPE"
    elif len(records) == 0:
        has_later_audit = any(LATER_AUDIT_PATTERN.match(path) for path in changed)
        has_runtime = any(is_runtime_path(path) for path in changed)
        if has_later_audit or has_runtime:
            mode = "LATER_IMPLEMENTATION_UNIT"
            add_error(errors, "LATER_UNIT_GATE_RECORD_MISSING")
        else:
            mode = "NON_IMPLEMENTATION_SCOPE"
    else:
        mode = "LATER_IMPLEMENTATION_UNIT"
        if len(records) != 1:
            add_error(errors, "GATE_RECORD_COUNT_INVALID", count=len(records))
        if records:
            item = records[0]
            record_errors, unit_id = validate_record(
                item["path"], item["payload"], changed, existing, policy
            )
            errors.extend(record_errors)

    status = "PASS" if not errors else "FAIL_CLOSED"
    result = {
        "type": RESULT_TYPE,
        "version": VERSION,
        "status": status,
        "mode": mode,
        "unit_id": unit_id,
        "changed_paths": changed,
        "gate_records": len(records),
        "errors": errors,
        "summary": {
            "changed_paths": len(changed),
            "runtime_paths": sum(1 for path in changed if is_runtime_path(path)),
            "later_audit_paths": sum(1 for path in changed if LATER_AUDIT_PATTERN.match(path)),
            "gate_records": len(records),
            "errors": len(errors),
        },
        "effects": {
            "production_files_changed": False,
            "browser_launched": False,
            "network_requests": False,
            "storage_writes": False,
            "live_observation_performed": False,
            "formal_proof_performed": False,
            "persisted_user_data_changed": False,
        },
        "claim_ceiling": "Static no-blind-flying evidence completeness only; no live, production, repair, migration, persisted-user-data, or formal-proof outcome is implied.",
    }
    result["result_sha256"] = digest(result)
    return result


def verify_result_hash(result: dict[str, Any]) -> bool:
    if not isinstance(result, dict) or not isinstance(result.get("result_sha256"), str):
        return False
    copy = json.loads(json.dumps(result))
    expected = copy.pop("result_sha256")
    return digest(copy) == expected


def repo_payload(base: str) -> dict[str, Any]:
    changed = changed_paths(base)
    records: list[dict[str, Any]] = []
    for relative in changed:
        if not is_candidate_record(relative):
            continue
        path = ROOT / relative
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        records.append({"path": relative, "payload": payload})
    existing = sorted(path for path in changed if path_exists(path))
    for record in records:
        binding = record["payload"].get("no_blind_flying_gate", {})
        matrix = binding.get("diagnostic_matrix_update", {})
        matrix_path = matrix.get("applicable_matrix") if isinstance(matrix, dict) else None
        if isinstance(matrix_path, str) and path_exists(matrix_path):
            existing.append(matrix_path)
        for key in (
            "diagnostic_evidence_routes",
            "deterministic_test_paths",
            "verifier_paths",
            "receipt_paths",
        ):
            for relative in binding.get(key, []):
                if isinstance(relative, str) and path_exists(relative):
                    existing.append(relative)
        for claim in binding.get("observed_facts", []):
            for relative in claim.get("evidence_paths", []):
                if isinstance(relative, str) and path_exists(relative):
                    existing.append(relative)
        for claim in binding.get("inferred_conclusions", []):
            for relative in claim.get("basis_evidence_paths", []):
                if isinstance(relative, str) and path_exists(relative):
                    existing.append(relative)
    return {
        "changed_paths": changed,
        "existing_paths": sorted(set(existing)),
        "records": records,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base")
    parser.add_argument("--fixture")
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    gate = json.loads(GATE_PATH.read_text())
    policy = json.loads(POLICY_PATH.read_text())
    if args.fixture:
        payload = json.loads((ROOT / args.fixture).read_text())
    else:
        if not args.base:
            raise SystemExit("--base is required without --fixture")
        payload = repo_payload(args.base)
    result = evaluate(payload, gate, policy)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    print(text, end="")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
