#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "audit/pass6/pass6-cross-system-invariant-catalog-v1.json"
CATALOG_TYPE = "PMP_PASS6_CROSS_SYSTEM_INVARIANT_CATALOG_V1"
RESULT_TYPE = "PMP_PASS6_CROSS_SYSTEM_INVARIANT_MATRIX_RESULT_V1"
ALLOWED_PROBES = {
    "file_exists",
    "contains",
    "excludes",
    "json_equals",
    "json_array_contains",
}
INVARIANT_KEYS = {
    "id",
    "subsystem",
    "statement",
    "owner",
    "enforcement",
    "failure_behavior",
    "scenarios",
    "evidence_paths",
    "deterministic_test_paths",
    "probes",
}


def stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(stable(value).encode()).hexdigest()


class SourceReader:
    def __init__(self, root: Path, repository_ref: str):
        self.root = root
        self.repository_ref = repository_ref

    def bytes(self, path: str) -> bytes:
        candidate = self.root / path
        if candidate.is_file():
            return candidate.read_bytes()
        return subprocess.check_output(
            ["git", "show", f"{self.repository_ref}:{path}"],
            cwd=self.root,
            stderr=subprocess.DEVNULL,
        )

    def exists(self, path: str) -> bool:
        try:
            self.bytes(path)
            return True
        except (OSError, subprocess.CalledProcessError):
            return False

    def text(self, path: str) -> str:
        return self.bytes(path).decode("utf-8")

    def json(self, path: str) -> Any:
        return json.loads(self.text(path))


def pointer(value: Any, expression: str) -> Any:
    if expression == "":
        return value
    if not expression.startswith("/"):
        raise ValueError("JSON_POINTER_INVALID")
    current = value
    for raw in expression[1:].split("/"):
        key = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            current = current[int(key)]
        else:
            current = current[key]
    return current


def probe(reader: SourceReader, spec: dict[str, Any]) -> tuple[bool, str]:
    kind = spec.get("kind")
    path = spec.get("path")
    if kind not in ALLOWED_PROBES:
        return False, "UNKNOWN_PROBE"
    if not isinstance(path, str) or not path:
        return False, "PROBE_PATH_INVALID"
    if kind == "file_exists":
        return (reader.exists(path), "PASS" if reader.exists(path) else "FILE_MISSING")
    if not reader.exists(path):
        return False, "FILE_MISSING"
    try:
        if kind == "contains":
            passed = isinstance(spec.get("token"), str) and spec["token"] in reader.text(path)
            return passed, "PASS" if passed else "TOKEN_MISSING"
        if kind == "excludes":
            passed = isinstance(spec.get("token"), str) and spec["token"] not in reader.text(path)
            return passed, "PASS" if passed else "FORBIDDEN_TOKEN_PRESENT"
        actual = pointer(reader.json(path), spec.get("pointer", ""))
        if kind == "json_equals":
            passed = actual == spec.get("expected")
            return passed, "PASS" if passed else "JSON_VALUE_MISMATCH"
        if kind == "json_array_contains":
            passed = isinstance(actual, list) and spec.get("expected") in actual
            return passed, "PASS" if passed else "JSON_ARRAY_VALUE_MISSING"
    except (KeyError, IndexError, ValueError, TypeError, json.JSONDecodeError, UnicodeDecodeError):
        return False, "PROBE_EVALUATION_ERROR"
    return False, "UNKNOWN_PROBE"


def evaluate(catalog: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    invariants = catalog.get("invariants")
    required_subsystems = catalog.get("required_subsystems")
    required_scenarios = catalog.get("required_scenarios")
    if catalog.get("type") != CATALOG_TYPE or catalog.get("version") != "1.0.0":
        errors.append({"code": "CATALOG_IDENTITY_INVALID"})
    if not isinstance(catalog.get("repository_ref"), str):
        errors.append({"code": "REPOSITORY_REF_INVALID"})
    if not isinstance(required_subsystems, list) or len(required_subsystems) != len(set(required_subsystems)):
        errors.append({"code": "REQUIRED_SUBSYSTEMS_INVALID"})
        required_subsystems = []
    if not isinstance(required_scenarios, list) or len(required_scenarios) != len(set(required_scenarios)):
        errors.append({"code": "REQUIRED_SCENARIOS_INVALID"})
        required_scenarios = []
    if not isinstance(invariants, list):
        errors.append({"code": "INVARIANTS_INVALID"})
        invariants = []
    ids = [item.get("id") for item in invariants if isinstance(item, dict)]
    if len(ids) != len(set(ids)):
        errors.append({"code": "DUPLICATE_INVARIANT_ID"})
    reader = SourceReader(root, str(catalog.get("repository_ref", "HEAD")))
    results: list[dict[str, Any]] = []
    seen_subsystems: set[str] = set()
    seen_scenarios: set[str] = set()

    for index, item in enumerate(invariants):
        row_errors: list[dict[str, Any]] = []
        if not isinstance(item, dict) or set(item) != INVARIANT_KEYS:
            row_errors.append({"code": "INVARIANT_SHAPE_INVALID"})
            item = item if isinstance(item, dict) else {}
        invariant_id = item.get("id", f"INVALID-{index}")
        if not isinstance(invariant_id, str) or not invariant_id.startswith("P6-INV-"):
            row_errors.append({"code": "INVARIANT_ID_INVALID"})
        subsystem = item.get("subsystem")
        if subsystem not in required_subsystems:
            row_errors.append({"code": "INVARIANT_SUBSYSTEM_INVALID"})
        else:
            seen_subsystems.add(subsystem)
        scenarios = item.get("scenarios")
        if not isinstance(scenarios, list) or not scenarios or len(scenarios) != len(set(scenarios)):
            row_errors.append({"code": "INVARIANT_SCENARIOS_INVALID"})
            scenarios = []
        unknown_scenarios = sorted(set(scenarios) - set(required_scenarios))
        if unknown_scenarios:
            row_errors.append({"code": "UNKNOWN_SCENARIO", "values": unknown_scenarios})
        seen_scenarios.update(scenarios)
        for field, code in (
            ("statement", "STATEMENT_INVALID"),
            ("owner", "OWNER_INVALID"),
            ("enforcement", "ENFORCEMENT_INVALID"),
            ("failure_behavior", "FAILURE_BEHAVIOR_INVALID"),
        ):
            if not isinstance(item.get(field), str) or not item.get(field):
                row_errors.append({"code": code})
        evidence_paths = item.get("evidence_paths")
        if not isinstance(evidence_paths, list) or not evidence_paths:
            row_errors.append({"code": "MISSING_EVIDENCE"})
            evidence_paths = []
        for path in evidence_paths:
            if not isinstance(path, str) or not reader.exists(path):
                row_errors.append({"code": "MISSING_EVIDENCE", "path": path})
        test_paths = item.get("deterministic_test_paths")
        if not isinstance(test_paths, list) or not test_paths:
            row_errors.append({"code": "MISSING_DETERMINISTIC_TEST"})
            test_paths = []
        for path in test_paths:
            if not isinstance(path, str) or not reader.exists(path):
                row_errors.append({"code": "MISSING_DETERMINISTIC_TEST", "path": path})
        probes = item.get("probes")
        if not isinstance(probes, list) or not probes:
            row_errors.append({"code": "MISSING_PROBE"})
            probes = []
        probe_results = []
        for spec in probes:
            if not isinstance(spec, dict):
                passed, code = False, "PROBE_SHAPE_INVALID"
                spec = {}
            else:
                passed, code = probe(reader, spec)
            probe_results.append(
                {
                    "kind": spec.get("kind"),
                    "path": spec.get("path"),
                    "pass": passed,
                    "code": code,
                }
            )
            if not passed:
                row_errors.append(
                    {
                        "code": code,
                        "path": spec.get("path"),
                        "kind": spec.get("kind"),
                    }
                )
        results.append(
            {
                "id": invariant_id,
                "subsystem": subsystem,
                "enforcement": item.get("enforcement"),
                "pass": not row_errors,
                "errors": row_errors,
                "probe_results": probe_results,
                "evidence_count": len(evidence_paths),
                "deterministic_test_count": len(test_paths),
                "scenarios": scenarios,
            }
        )

    for subsystem in sorted(set(required_subsystems) - seen_subsystems):
        errors.append({"code": "MISSING_SUBSYSTEM_INVARIANT", "subsystem": subsystem})
    for scenario in sorted(set(required_scenarios) - seen_scenarios):
        errors.append({"code": "MISSING_SCENARIO_COVERAGE", "scenario": scenario})
    errors.extend(
        {"code": "INVARIANT_FAILED", "id": row["id"], "errors": row["errors"]}
        for row in results
        if not row["pass"]
    )
    subsystem_counts = Counter(row["subsystem"] for row in results if row["subsystem"])
    scenario_counts = Counter(
        scenario for row in results for scenario in row.get("scenarios", [])
    )
    passed = not errors
    return {
        "type": RESULT_TYPE,
        "version": "1.0.0",
        "status": "PASS" if passed else "FAIL",
        "catalog_sha256": digest(catalog),
        "repository_ref": catalog.get("repository_ref"),
        "summary": {
            "invariants_total": len(results),
            "invariants_passed": sum(row["pass"] for row in results),
            "invariants_failed": sum(not row["pass"] for row in results),
            "required_subsystems": len(required_subsystems),
            "covered_subsystems": len(seen_subsystems),
            "required_scenarios": len(required_scenarios),
            "covered_scenarios": len(seen_scenarios),
            "errors": len(errors),
        },
        "subsystem_coverage": dict(sorted(subsystem_counts.items())),
        "scenario_coverage": dict(sorted(scenario_counts.items())),
        "results": results,
        "errors": errors,
        "claim_ceiling": (
            "Invariant coverage and exact-source anchors only; no later-pass completion, "
            "production mutation, or live app outcome is claimed."
        ),
        "side_effects": {
            "production_files_changed": 0,
            "storage_writes": 0,
            "persisted_user_data_writes": 0,
            "network_requests": 0,
            "route_changes": 0,
            "repairs": 0,
            "live_observations": 0,
            "formal_proofs": 0,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG))
    parser.add_argument("--output")
    args = parser.parse_args()
    catalog = json.loads(Path(args.catalog).read_text())
    result = evaluate(catalog)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(payload)
    print(payload, end="")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
