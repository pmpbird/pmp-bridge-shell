#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "audit/pass6/pass6-cross-system-invariant-catalog-v1.json"
RUNNER_PATH = ROOT / "tools/run_pass6_unit3_cross_system_invariant_matrix_v1.py"
spec = importlib.util.spec_from_file_location("p6u3_matrix", RUNNER_PATH)
assert spec and spec.loader
matrix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(matrix)
assertions = 0


def same(actual, expected, label):
    global assertions
    assertions += 1
    assert actual == expected, (label, actual, expected)


def yes(value, label):
    global assertions
    assertions += 1
    assert value, label


def no(value, label):
    global assertions
    assertions += 1
    assert not value, label


def codes(result):
    found = {row["code"] for row in result["errors"]}
    for row in result["errors"]:
        for detail in row.get("errors", []):
            found.add(detail["code"])
    return found


catalog = json.loads(CATALOG_PATH.read_text())
baseline = matrix.evaluate(catalog, ROOT)
same(baseline["type"], matrix.RESULT_TYPE, "result type")
same(baseline["version"], "1.0.0", "result version")
same(baseline["status"], "PASS", "baseline pass")
same(baseline["repository_ref"], catalog["repository_ref"], "repository ref")
same(baseline["summary"]["invariants_total"], 20, "invariant count")
same(baseline["summary"]["invariants_passed"], 20, "passed count")
same(baseline["summary"]["invariants_failed"], 0, "failed count")
same(baseline["summary"]["required_subsystems"], 9, "required subsystems")
same(baseline["summary"]["covered_subsystems"], 9, "covered subsystems")
same(baseline["summary"]["required_scenarios"], 9, "required scenarios")
same(baseline["summary"]["covered_scenarios"], 9, "covered scenarios")
same(baseline["summary"]["errors"], 0, "zero errors")
same(baseline["errors"], [], "empty error list")
same(
    baseline["catalog_sha256"],
    hashlib.sha256(matrix.stable(catalog).encode()).hexdigest(),
    "catalog digest",
)
same(set(baseline["subsystem_coverage"]), set(catalog["required_subsystems"]), "subsystems exact")
same(set(baseline["scenario_coverage"]), set(catalog["required_scenarios"]), "scenarios exact")
same(sum(baseline["subsystem_coverage"].values()), 20, "subsystem accounting")
yes(all(value > 0 for value in baseline["subsystem_coverage"].values()), "every subsystem covered")
yes(all(value > 0 for value in baseline["scenario_coverage"].values()), "every scenario covered")
yes(all(row["pass"] for row in baseline["results"]), "every invariant passes")
same(len({row["id"] for row in baseline["results"]}), 20, "unique result ids")
yes(all(row["probe_results"] for row in baseline["results"]), "every invariant probed")
yes(
    all(all(probe["pass"] for probe in row["probe_results"]) for row in baseline["results"]),
    "every probe passes",
)
yes(all(row["evidence_count"] > 0 for row in baseline["results"]), "evidence linked")
yes(
    all(row["deterministic_test_count"] > 0 for row in baseline["results"]),
    "tests linked",
)
same(baseline["side_effects"]["production_files_changed"], 0, "no production changes")
same(baseline["side_effects"]["storage_writes"], 0, "no storage writes")
same(baseline["side_effects"]["persisted_user_data_writes"], 0, "no user data writes")
same(baseline["side_effects"]["network_requests"], 0, "no network")
same(baseline["side_effects"]["route_changes"], 0, "no routes")
same(baseline["side_effects"]["repairs"], 0, "no repairs")
same(baseline["side_effects"]["live_observations"], 0, "no observation")
same(baseline["side_effects"]["formal_proofs"], 0, "no proof")
yes("no later-pass completion" in baseline["claim_ceiling"], "claim ceiling")
same(matrix.evaluate(catalog, ROOT), baseline, "deterministic repeated evaluation")

for row in baseline["results"]:
    same(row["errors"], [], row["id"] + " no errors")
    same(row["pass"], True, row["id"] + " pass")
    yes(row["subsystem"] in catalog["required_subsystems"], row["id"] + " subsystem")
    yes(row["scenarios"], row["id"] + " scenarios")
    yes(row["enforcement"], row["id"] + " enforcement")

reader = matrix.SourceReader(ROOT, catalog["repository_ref"])
yes(reader.exists("pmp-current-map-v12.json"), "reader current path")
yes(reader.exists("pmp-pass8-helper-rules-v1.js"), "reader sparse fallback path")
yes("helper_assists_owner_does_not_become_owner" in reader.text("pmp-pass8-helper-rules-v1.js"), "fallback bytes")
same(
    reader.json("pmp-current-map-v12.json")["route_contract"]["failure_mode"],
    "fail_closed",
    "reader json",
)
same(matrix.pointer({"a": [{"b": 7}]}, "/a/0/b"), 7, "json pointer list")
same(matrix.pointer({"a/b": {"~key": 9}}, "/a~1b/~0key"), 9, "json pointer escapes")


def mutated(change):
    candidate = copy.deepcopy(catalog)
    change(candidate)
    return matrix.evaluate(candidate, ROOT)


cases = [
    (
        "duplicate id",
        lambda value: value["invariants"].__setitem__(
            1, dict(value["invariants"][1], id=value["invariants"][0]["id"])
        ),
        "DUPLICATE_INVARIANT_ID",
    ),
    (
        "missing subsystem",
        lambda value: value.__setitem__(
            "invariants", [row for row in value["invariants"] if row["subsystem"] != "banks"]
        ),
        "MISSING_SUBSYSTEM_INVARIANT",
    ),
    (
        "missing scenario",
        lambda value: [
            row.__setitem__(
                "scenarios", [item for item in row["scenarios"] if item != "restart"]
            )
            for row in value["invariants"]
        ],
        "MISSING_SCENARIO_COVERAGE",
    ),
    (
        "missing evidence path",
        lambda value: value["invariants"][0].__setitem__(
            "evidence_paths", ["does-not-exist/evidence.json"]
        ),
        "MISSING_EVIDENCE",
    ),
    (
        "empty evidence",
        lambda value: value["invariants"][0].__setitem__("evidence_paths", []),
        "MISSING_EVIDENCE",
    ),
    (
        "missing test path",
        lambda value: value["invariants"][0].__setitem__(
            "deterministic_test_paths", ["does-not-exist/test.py"]
        ),
        "MISSING_DETERMINISTIC_TEST",
    ),
    (
        "empty tests",
        lambda value: value["invariants"][0].__setitem__("deterministic_test_paths", []),
        "MISSING_DETERMINISTIC_TEST",
    ),
    (
        "unknown probe",
        lambda value: value["invariants"][0]["probes"][0].__setitem__("kind", "network"),
        "UNKNOWN_PROBE",
    ),
    (
        "missing probe path",
        lambda value: value["invariants"][0]["probes"][0].__setitem__(
            "path", "does-not-exist/source.js"
        ),
        "FILE_MISSING",
    ),
    (
        "contains mismatch",
        lambda value: value["invariants"][0]["probes"][2].__setitem__(
            "token", "TOKEN_THAT_CANNOT_EXIST"
        ),
        "TOKEN_MISSING",
    ),
    (
        "excludes mismatch",
        lambda value: value["invariants"][2]["probes"][0].__setitem__(
            "token", "RG22_FAIL_CLOSED"
        ),
        "FORBIDDEN_TOKEN_PRESENT",
    ),
    (
        "json mismatch",
        lambda value: value["invariants"][0]["probes"][0].__setitem__(
            "expected", "not-the-map"
        ),
        "JSON_VALUE_MISMATCH",
    ),
    (
        "json pointer error",
        lambda value: value["invariants"][0]["probes"][0].__setitem__(
            "pointer", "/route_contract/not_present"
        ),
        "PROBE_EVALUATION_ERROR",
    ),
    (
        "empty probes",
        lambda value: value["invariants"][0].__setitem__("probes", []),
        "MISSING_PROBE",
    ),
    (
        "unknown subsystem",
        lambda value: value["invariants"][0].__setitem__("subsystem", "unknown"),
        "INVARIANT_SUBSYSTEM_INVALID",
    ),
    (
        "duplicate scenario",
        lambda value: value["invariants"][0]["scenarios"].append(
            value["invariants"][0]["scenarios"][0]
        ),
        "INVARIANT_SCENARIOS_INVALID",
    ),
    (
        "unknown scenario",
        lambda value: value["invariants"][0]["scenarios"].append("unbounded"),
        "UNKNOWN_SCENARIO",
    ),
    (
        "bad id",
        lambda value: value["invariants"][0].__setitem__("id", "ROUTE-1"),
        "INVARIANT_ID_INVALID",
    ),
    (
        "extra invariant field",
        lambda value: value["invariants"][0].__setitem__("authority_gain", True),
        "INVARIANT_SHAPE_INVALID",
    ),
    (
        "missing owner",
        lambda value: value["invariants"][0].__setitem__("owner", ""),
        "OWNER_INVALID",
    ),
    (
        "missing statement",
        lambda value: value["invariants"][0].__setitem__("statement", ""),
        "STATEMENT_INVALID",
    ),
    (
        "missing enforcement",
        lambda value: value["invariants"][0].__setitem__("enforcement", ""),
        "ENFORCEMENT_INVALID",
    ),
    (
        "missing failure behavior",
        lambda value: value["invariants"][0].__setitem__("failure_behavior", ""),
        "FAILURE_BEHAVIOR_INVALID",
    ),
    (
        "bad catalog type",
        lambda value: value.__setitem__("type", "WRONG"),
        "CATALOG_IDENTITY_INVALID",
    ),
    (
        "duplicate required subsystem",
        lambda value: value["required_subsystems"].append(
            value["required_subsystems"][0]
        ),
        "REQUIRED_SUBSYSTEMS_INVALID",
    ),
    (
        "duplicate required scenario",
        lambda value: value["required_scenarios"].append(
            value["required_scenarios"][0]
        ),
        "REQUIRED_SCENARIOS_INVALID",
    ),
]

for label, change, expected_code in cases:
    result = mutated(change)
    same(result["status"], "FAIL", label + " fails")
    yes(result["summary"]["errors"] > 0, label + " error count")
    yes(expected_code in codes(result), label + " exact code")
    same(result["side_effects"]["storage_writes"], 0, label + " no storage")
    same(result["side_effects"]["network_requests"], 0, label + " no network")
    same(result["side_effects"]["repairs"], 0, label + " no repair")

runner_source = RUNNER_PATH.read_text()
for forbidden in (
    "requests.",
    "urllib.",
    "http.client",
    "socket.",
    "localStorage",
    "indexedDB",
    "document.",
    "window.",
    "git push",
    "git commit",
    "gh ",
):
    no(forbidden in runner_source, "runner forbidden token " + forbidden)
yes('"persisted_user_data_writes": 0' in runner_source, "user data zero declared")
yes('"formal_proofs": 0' in runner_source, "formal proof zero declared")
yes('"live_observations": 0' in runner_source, "observation zero declared")
yes("MISSING_EVIDENCE" in runner_source, "missing evidence fails")
yes("MISSING_DETERMINISTIC_TEST" in runner_source, "missing test fails")
yes("UNKNOWN_PROBE" in runner_source, "unknown probe fails")
yes("MISSING_SUBSYSTEM_INVARIANT" in runner_source, "missing subsystem fails")
yes("MISSING_SCENARIO_COVERAGE" in runner_source, "missing scenario fails")

print(
    f"PASS: P6-U3 cross-system invariant and regression matrix ({assertions}/{assertions})"
)
