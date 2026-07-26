#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
GATE = json.loads((ROOT / "audit/pass6/pass6-permanent-no-blind-flying-gate-v1.json").read_text())
POLICY = json.loads((ROOT / "audit/pass6/pass6-ci-lane-artifact-policy-v1.json").read_text())
FIXTURE = json.loads(
    (ROOT / "audit/pass6/fixtures/pass6-unit7-no-blind-flying-positive-v1.json").read_text()
)
SPEC = importlib.util.spec_from_file_location("p6u7_gate", RUNNER_PATH)
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)
ASSERTIONS = 0


def check(condition: Any, message: str) -> None:
    global ASSERTIONS
    ASSERTIONS += 1
    assert condition, message


def equal(actual: Any, expected: Any, message: str) -> None:
    global ASSERTIONS
    ASSERTIONS += 1
    assert actual == expected, f"{message}: {actual!r} != {expected!r}"


def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    return RUNNER.evaluate(payload, GATE, POLICY)


def mutate(callback) -> dict[str, Any]:
    candidate = copy.deepcopy(FIXTURE)
    callback(candidate)
    return evaluate(candidate)


def expect_error(code: str, callback) -> dict[str, Any]:
    result = mutate(callback)
    equal(result["status"], "FAIL_CLOSED", f"{code}: status")
    check(any(item["code"] == code for item in result["errors"]), f"{code}: error")
    check(RUNNER.verify_result_hash(result), f"{code}: result hash")
    return result


first = evaluate(copy.deepcopy(FIXTURE))
second = evaluate(copy.deepcopy(FIXTURE))
equal(first, second, "fixture evaluation deterministic")
equal(first["type"], RUNNER.RESULT_TYPE, "result type")
equal(first["version"], "1.0.0", "result version")
equal(first["status"], "PASS", "positive status")
equal(first["mode"], "LATER_IMPLEMENTATION_UNIT", "positive mode")
equal(first["unit_id"], "P7-U1", "unit identity")
equal(first["gate_records"], 1, "one gate record")
equal(first["errors"], [], "no errors")
equal(first["summary"]["changed_paths"], 4, "four changed paths")
equal(first["summary"]["runtime_paths"], 0, "no runtime path")
equal(first["summary"]["later_audit_paths"], 2, "two later audit paths")
equal(first["summary"]["gate_records"], 1, "summary gate record")
equal(first["summary"]["errors"], 0, "summary errors")
check(RUNNER.verify_result_hash(first), "positive result hash")
check(all(value is False for value in first["effects"].values()), "positive effects all false")
check("no live" in first["claim_ceiling"], "claim ceiling excludes live")
check("formal-proof" in first["claim_ceiling"], "claim ceiling excludes formal proof")
equal(FIXTURE["expected"]["status"], first["status"], "fixture expected status")
equal(FIXTURE["expected"]["mode"], first["mode"], "fixture expected mode")
equal(FIXTURE["expected"]["unit_id"], first["unit_id"], "fixture expected unit")
equal(FIXTURE["expected"]["gate_records"], first["gate_records"], "fixture expected records")
equal(FIXTURE["expected"]["errors"], first["errors"], "fixture expected errors")

equal(GATE["type"], "PMP_PASS6_PERMANENT_NO_BLIND_FLYING_GATE_V1", "gate type")
equal(GATE["version"], "1.0.0", "gate version")
equal(GATE["status"], "ACTIVE_ON_MERGE", "gate activation status")
equal(GATE["applies_to_passes"], [7, 8, 9, 10, 11, 12, 13], "gate pass coverage")
equal(len(GATE["activation_scope"]), 8, "activation exact scope")
equal(GATE["no_retry_gates"]["retry_authorized"], False, "no retry remains")
equal(POLICY["policy"]["automatic_retry"], "FORBIDDEN", "policy automatic retry")
equal(POLICY["policy"]["failed_attempt_erasure"], "FORBIDDEN", "policy preserves failures")
equal(len(POLICY["artifact_roles"]), 9, "nine artifact roles")

activation = evaluate(
    {
        "changed_paths": copy.deepcopy(GATE["activation_scope"]),
        "existing_paths": copy.deepcopy(GATE["activation_scope"]),
        "records": [],
    }
)
equal(activation["status"], "PASS", "activation passes")
equal(activation["mode"], "ACTIVATION_SCOPE", "activation mode")
equal(activation["gate_records"], 0, "activation needs no later record")
check(RUNNER.verify_result_hash(activation), "activation hash")

nonimplementation = evaluate(
    {
        "changed_paths": ["docs/operator-note.md"],
        "existing_paths": ["docs/operator-note.md"],
        "records": [],
    }
)
equal(nonimplementation["status"], "PASS", "nonimplementation passes")
equal(nonimplementation["mode"], "NON_IMPLEMENTATION_SCOPE", "nonimplementation mode")
equal(nonimplementation["unit_id"], None, "nonimplementation has no unit")
check(RUNNER.verify_result_hash(nonimplementation), "nonimplementation hash")

runtime_missing = evaluate(
    {
        "changed_paths": ["pmp-example-owner-v1.js"],
        "existing_paths": ["pmp-example-owner-v1.js"],
        "records": [],
    }
)
equal(runtime_missing["status"], "FAIL_CLOSED", "runtime without record fails")
check(
    any(item["code"] == "LATER_UNIT_GATE_RECORD_MISSING" for item in runtime_missing["errors"]),
    "runtime missing record error",
)
check(RUNNER.verify_result_hash(runtime_missing), "runtime missing hash")

expect_error("UNIT_ID_INVALID", lambda x: x["records"][0]["payload"].update(unit_id="P6-U9"))
expect_error("SCOPE_MISSING", lambda x: x["records"][0]["payload"].pop("scope"))
expect_error(
    "EXACT_SCOPE_MISMATCH",
    lambda x: x["records"][0]["payload"]["scope"]["changed_paths"].pop(),
)
expect_error(
    "IMPLEMENTATION_PATHS_MISSING",
    lambda x: x["records"][0]["payload"]["scope"].pop("implementation_paths"),
)
expect_error(
    "IMPLEMENTATION_PATHS_MISMATCH",
    lambda x: x["records"][0]["payload"]["scope"]["implementation_paths"].append("pmp-fake.js"),
)
expect_error(
    "GATE_BINDING_TYPE_INVALID",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"].update(type="BAD"),
)
expect_error(
    "GATE_BINDING_VERSION_INVALID",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"].update(version="2.0.0"),
)
expect_error(
    "CI_LANE_UNCLASSIFIED",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"].update(ci_lane="mystery"),
)
expect_error(
    "DIAGNOSTIC_MATRIX_UPDATE_MISSING",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"].pop(
        "diagnostic_matrix_update"
    ),
)
expect_error(
    "DIAGNOSTIC_MATRIX_STATUS_INVALID",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"][
        "diagnostic_matrix_update"
    ].update(status="IGNORED"),
)
expect_error(
    "DIAGNOSTIC_MATRIX_PATH_MISSING",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"][
        "diagnostic_matrix_update"
    ].pop("applicable_matrix"),
)
expect_error(
    "DIAGNOSTIC_MATRIX_PATH_NOT_FOUND",
    lambda x: x["existing_paths"].remove(
        "audit/pass6/pass6-cross-system-invariant-catalog-v1.json"
    ),
)
expect_error(
    "DIAGNOSTIC_MATRIX_RATIONALE_MISSING",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"][
        "diagnostic_matrix_update"
    ].update(rationale=""),
)

for key, code in (
    ("diagnostic_evidence_routes", "DIAGNOSTIC_EVIDENCE_ROUTE_MISSING"),
    ("deterministic_test_paths", "DETERMINISTIC_TEST_PATH_MISSING"),
    ("verifier_paths", "VERIFIER_PATH_MISSING"),
    ("receipt_paths", "RECEIPT_PATH_MISSING"),
):
    expect_error(
        code,
        lambda x, key=key: x["records"][0]["payload"]["no_blind_flying_gate"].update(
            {key: []}
        ),
    )

expect_error(
    "REQUIRED_EVIDENCE_PATH_MISSING",
    lambda x: x["existing_paths"].remove(
        "audit/pass7/pass7-section-owner-unit1-inventory-v1.json"
    ),
)
expect_error(
    "RECEIPT_NOT_IN_EXACT_SCOPE",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"]["receipt_paths"].append(
        "audit/pass7/receipts/EXTRA.json"
    )
    or x["existing_paths"].append("audit/pass7/receipts/EXTRA.json"),
)
expect_error(
    "TEST_NOT_IN_EXACT_SCOPE",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"][
        "deterministic_test_paths"
    ].append("tools/test_extra.py")
    or x["existing_paths"].append("tools/test_extra.py"),
)
expect_error(
    "VERIFIER_NOT_IN_EXACT_SCOPE",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"][
        "verifier_paths"
    ].append("tools/verify_extra.py")
    or x["existing_paths"].append("tools/verify_extra.py"),
)
expect_error(
    "OBSERVED_FACT_MISSING",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"].update(
        observed_facts=[]
    ),
)
expect_error(
    "OBSERVED_FACT_TYPE_INVALID",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"][
        "observed_facts"
    ][0].update(claim_type="INFERRED"),
)
expect_error(
    "OBSERVED_FACT_TEXT_MISSING",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"][
        "observed_facts"
    ][0].update(fact=""),
)
expect_error(
    "OBSERVED_FACT_EVIDENCE_MISSING",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"][
        "observed_facts"
    ][0].update(evidence_paths=[]),
)
expect_error(
    "INFERRED_CONCLUSIONS_FIELD_MISSING",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"].pop(
        "inferred_conclusions"
    ),
)
expect_error(
    "INFERRED_CONCLUSION_TYPE_INVALID",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"][
        "inferred_conclusions"
    ][0].update(claim_type="OBSERVED"),
)
expect_error(
    "INFERRED_CONCLUSION_TEXT_MISSING",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"][
        "inferred_conclusions"
    ][0].update(conclusion=""),
)
expect_error(
    "INFERRED_CONCLUSION_BASIS_MISSING",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"][
        "inferred_conclusions"
    ][0].update(basis_evidence_paths=[]),
)
expect_error(
    "FAULT_INJECTION_DECISION_MISSING",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"].pop("fault_injection"),
)
expect_error(
    "FAULT_NOT_APPLICABLE_RATIONALE_MISSING",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"][
        "fault_injection"
    ].update(rationale=""),
)
expect_error(
    "FAULT_NOT_APPLICABLE_CASES_NONEMPTY",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"][
        "fault_injection"
    ].update(cases=["unexpected"]),
)
expect_error(
    "FAULT_CASES_MISSING",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"][
        "fault_injection"
    ].update(status="COVERED", cases=[]),
)
expect_error(
    "FAULT_INJECTION_STATUS_INVALID",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"][
        "fault_injection"
    ].update(status="SKIPPED"),
)
expect_error(
    "ARTIFACT_ROLES_MISMATCH",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"][
        "required_artifact_roles"
    ].pop(),
)
expect_error(
    "UPLOAD_BEFORE_ENFORCEMENT_REQUIRED",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"].update(
        upload_before_enforcement=False
    ),
)
expect_error(
    "AUTOMATIC_RETRY_FORBIDDEN",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"].update(
        automatic_retry=True
    ),
)
expect_error(
    "SPECIAL_AUTHORITY_STATE_MISSING",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"].pop(
        "special_authority"
    ),
)
expect_error(
    "SPECIAL_AUTHORITY_REQUIRED_FOR_LANE",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"].update(
        ci_lane="bounded_live_observation"
    ),
)
expect_error(
    "CONSUMED_AUTHORITY_NOT_GRANTED",
    lambda x: x["records"][0]["payload"]["no_blind_flying_gate"][
        "special_authority"
    ].update(consumed=True, granted=False),
)

multiple = copy.deepcopy(FIXTURE)
multiple["records"].append(copy.deepcopy(multiple["records"][0]))
multiple_result = evaluate(multiple)
equal(multiple_result["status"], "FAIL_CLOSED", "multiple records fail")
check(
    any(item["code"] == "GATE_RECORD_COUNT_INVALID" for item in multiple_result["errors"]),
    "multiple record error",
)
check(RUNNER.verify_result_hash(multiple_result), "multiple result hash")

tampered = copy.deepcopy(first)
tampered["summary"]["errors"] = 1
equal(RUNNER.verify_result_hash(tampered), False, "tampered result hash rejected")

print(
    f"PASS: P6-U7 permanent no-blind-flying gate "
    f"({ASSERTIONS}/{ASSERTIONS})"
)
