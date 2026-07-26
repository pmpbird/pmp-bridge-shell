#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "d6651068be6b07cdea79d80d02089ead1a66275e"
REPORT = ROOT / "audit/pass9/pass9-bank-continuous-run-unit2-owner-contract-v1.json"
RECEIPT = (
    ROOT
    / "audit/pass9/receipts/RECEIPT_P9_U2_BANK_CONTINUOUS_RUN_OWNER_CONTRACT_20260726T193000Z_001.json"
)
RUNNER = ROOT / "tools/run_pass9_unit2_bank_continuous_run_owner_contract_v1.js"
TEST = ROOT / "tools/test_pass9_unit2_bank_continuous_run_owner_contract_v1.js"
WORKFLOW = ROOT / ".github/workflows/pass9-unit2-bank-continuous-run-owner-contract-v1.yml"
GATE_RUNNER = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
EXPECTED = {
    ".github/workflows/pass9-unit2-bank-continuous-run-owner-contract-v1.yml",
    "audit/pass9/pass9-bank-continuous-run-unit2-owner-contract-v1.json",
    "audit/pass9/receipts/RECEIPT_P9_U2_BANK_CONTINUOUS_RUN_OWNER_CONTRACT_20260726T193000Z_001.json",
    "tools/run_pass9_unit2_bank_continuous_run_owner_contract_v1.js",
    "tools/test_pass9_unit2_bank_continuous_run_owner_contract_v1.js",
    "tools/verify_pass9_unit2_bank_continuous_run_owner_contract_v1.py",
}
SOURCE_INPUTS = {
    "unit1_inventory_sha256": ROOT
    / "audit/pass9/pass9-bank-continuous-run-unit1-inventory-v1.json",
    "pass7_owner_contract_sha256": ROOT
    / "audit/pass7/pass7-section-owner-unit2-capability-contract-v1.json",
    "cross_system_invariant_catalog_sha256": ROOT
    / "audit/pass6/pass6-cross-system-invariant-catalog-v1.json",
    "continuous_run_state_sha256": ROOT / "pmp-continuous-run-state-bank-v1.js",
    "bank_router_sha256": ROOT / "pmp-master-bank-inventory-router-v1.js",
    "runner_sha256": RUNNER,
    "test_sha256": TEST,
}


def output(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed_paths(base: str) -> set[str]:
    changed: set[str] = set()
    for command in (
        ("git", "diff", "--name-only", f"{base}...HEAD"),
        ("git", "diff", "--name-only", base),
        ("git", "ls-files", "--others", "--exclude-standard"),
    ):
        changed.update(filter(None, output(*command).splitlines()))
    return changed


def workflow_paths(text: str) -> set[str]:
    match = re.search(r"(?m)^    paths:\n(?P<rows>(?:      - [^\n]+\n)+)", text)
    assert match
    return {
        row.strip()[2:].strip().strip("'\"")
        for row in match.group("rows").splitlines()
    }


def main() -> None:
    base = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else BASE
    assert base == BASE
    changed = changed_paths(base)
    assert changed == EXPECTED, (sorted(changed), sorted(EXPECTED))

    report = json.loads(REPORT.read_text())
    receipt = json.loads(RECEIPT.read_text())
    unit1 = json.loads(SOURCE_INPUTS["unit1_inventory_sha256"].read_text())
    assert report["base_main_commit"] == BASE
    assert report["unit_id"] == "P9-U2"
    assert report["status"] == "BANK_CONTINUOUS_RUN_OWNER_CONTRACT_PROVEN"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == []
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["status"] == report["status"]
    for key, path in SOURCE_INPUTS.items():
        assert report["inputs"][key] == sha(path), (
            key,
            report["inputs"][key],
            sha(path),
        )

    runtime = json.loads(output("node", str(RUNNER.relative_to(ROOT))))
    assert runtime["type"] == (
        "PMP_PASS9_UNIT2_BANK_CONTINUOUS_RUN_OWNER_CONTRACT_RESULT_V1"
    )
    assert runtime["status"] == "PASS"
    assert runtime["contract"] == report["owner_contract"]
    assert runtime["summary"] == {
        "requests": 0,
        "allowed": 0,
        "denied": 0,
        "replayed": 0,
        "simulated_resource_versions": {},
        "cancellation_epochs": {},
    }
    assert runtime["receipts"] == []
    assert (
        runtime["result_sha256"]
        == report["contract_verification"]["result_sha256"]
    )
    assert all(value is False for value in runtime["effects"].values())

    test_output = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"contract \((\d+)/(\d+)\)", test_output)
    assert match and match.group(1) == match.group(2)
    assertions = int(match.group(1))
    assert assertions == report["verification"]["assertions_passed"] == 229
    assert report["verification"]["assertions_total"] == assertions
    assert report["verification"]["assertions_failed"] == 0
    assert receipt["coverage"]["assertions"] == assertions

    contract = report["owner_contract"]
    assert contract["contract_version"] == (
        "PMP_BANK_CONTINUOUS_RUN_OWNER_CONTRACT_V1"
    )
    assert contract["receipt_version"] == (
        "PMP_BANK_CONTINUOUS_RUN_OWNER_RECEIPT_V1"
    )
    assert contract["model"] == "SEPARATE_OWNERS_FAIL_CLOSED_REQUEST_RECEIPT"
    assert set(contract["owners"]) == {"bank", "continuous_run"}
    bank = contract["owners"]["bank"]
    run = contract["owners"]["continuous_run"]
    assert (bank["owner_id"], bank["section_id"], bank["resource_prefix"]) == (
        "bank_screen_owner",
        "bank",
        "bank:",
    )
    assert (run["owner_id"], run["section_id"], run["resource_prefix"]) == (
        "continuous_run_level_owner",
        "continuous_run",
        "continuous_run:",
    )
    assert bank["owner_id"] != run["owner_id"]
    assert bank["controls"] == unit1["p9_u2_requirements"]["bank_owner_controls"]
    assert (
        run["controls"]
        == unit1["p9_u2_requirements"]["continuous_run_owner_controls"]
    )
    assert contract["request_fields"] == (
        unit1["p9_u2_requirements"]["required_cross_owner_request_fields"]
    )
    assert len(contract["request_fields"]) == len(set(contract["request_fields"])) == 13
    assert len(contract["receipt_fields"]) == len(set(contract["receipt_fields"])) == 15
    assert len(bank["accepted_actions"]) == 4
    assert len(run["accepted_actions"]) == 8
    assert set(bank["accepted_actions"]).isdisjoint(run["accepted_actions"])
    assert len(contract["forbidden_actions"]) == len(
        set(contract["forbidden_actions"])
    ) == 8
    for action in (
        "DELETE_BANK",
        "CLEAR_BANK",
        "CLEAR_CURRENT_STATE",
        "MANUAL_CLEAR",
        "DIRECT_STORAGE_WRITE",
        "MIGRATE_STORAGE",
        "TAKE_OWNERSHIP",
        "COPY_AUTHORITY_BETWEEN_FRAMES",
    ):
        assert action in contract["forbidden_actions"]
    assert len(contract["failure_codes"]) == len(set(contract["failure_codes"])) == 17
    assert contract["persistence"] == {
        "durable_writer": "bank_screen_owner",
        "request_owner_for_run_state": "continuous_run_level_owner",
        "algorithm": "SHA-256",
        "append_only_receipt_chain": True,
        "delete_or_clear_default": "DENY",
    }
    assert contract["compatibility"]["existing_persisted_keys_preserved"] == (
        unit1["critical_sources"]["continuous_run_state"]["persisted_keys"]
    )
    assert (
        contract["compatibility"]["storage_migration"]
        == "FORBIDDEN_IN_P9_U2_AND_P9_U3"
    )
    for key in (
        "copied_cross_frame_apis_convey_authority",
        "active_tab_conveys_ownership",
        "filename_conveys_authority",
    ):
        assert contract["compatibility"][key] is False
    assert contract["concurrency"] == {
        "exact_expected_version": True,
        "one_active_lease_per_run_resource": True,
        "duplicate_same_operation_and_digest": (
            "RETURN_IDENTICAL_RECEIPT_NO_NEW_EFFECT"
        ),
        "duplicate_same_operation_different_digest": "DENY",
        "cancellation_epoch": "MONOTONIC",
        "restart": "ATOMIC_SNAPSHOT_OR_EMPTY",
        "handoff": "EXACT_EXPECTED_VERSION_AND_CAPABILITY",
    }
    assert report["contract_verification"] == {
        "canonical_owners": 2,
        "bank_actions": 4,
        "continuous_run_actions": 8,
        "forbidden_actions": 8,
        "failure_codes": 17,
        "request_fields": 13,
        "receipt_fields": 15,
        "assertions": assertions,
        "result_sha256": runtime["result_sha256"],
    }

    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "static_contract"
    assert binding["diagnostic_matrix_update"]["status"] == "CONFIRMED_UNCHANGED"
    assert binding["fault_injection"]["status"] == "COVERED"
    assert len(binding["fault_injection"]["cases"]) >= 15
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    assert binding["special_authority"] == {
        "required": False,
        "granted": False,
        "consumed": False,
    }
    gate = json.loads(
        output("python3", str(GATE_RUNNER.relative_to(ROOT)), "--base", BASE)
    )
    assert gate["status"] == "PASS"
    assert gate["unit_id"] == "P9-U2"
    assert gate["gate_records"] == 1
    assert gate["summary"]["runtime_paths"] == 0
    assert gate["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for required in (
        "actions/setup-node@v4",
        "node-version: '22'",
        "actions/setup-python@v5",
        "python-version: '3.12'",
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete P9-U2 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert required in workflow
    assert workflow.index("Upload complete P9-U2 evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )

    assert all(value is False for value in report["effects"].values())
    assert all(value is False for value in receipt["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["next_step"]["id"] == "P9-U3"
    assert report["next_step"]["requires_user_app_check"] is False
    assert report["next_step"]["requires_new_explicit_authority"] is False
    assert receipt["next_safe_move"]["step_id"] == "P9-U3"
    print(
        "PASS: exact six-file P9-U2 Bank/Continuous Run owner contract verified "
        f"({assertions}/{assertions}, gate PASS, zero effects)"
    )


if __name__ == "__main__":
    main()
