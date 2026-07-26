#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "83e0e46918ad3dc7253b7f6c3de918fdc4812c4f"
REPORT = ROOT / "audit/pass10/pass10-bank-unit2-inventory-contract-v1.json"
RECEIPT = ROOT / "audit/pass10/receipts/RECEIPT_P10_U2_BANK_INVENTORY_CONTRACT_20260726T220000Z_001.json"
WORKFLOW = ROOT / ".github/workflows/pass10-unit2-bank-inventory-contract-v1.yml"
RUNNER = ROOT / "tools/run_pass10_unit2_bank_inventory_contract_v1.js"
TEST = ROOT / "tools/test_pass10_unit2_bank_inventory_contract_v1.js"
GATE = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
EXPECTED = {
    ".github/workflows/pass10-unit2-bank-inventory-contract-v1.yml",
    "audit/pass10/pass10-bank-unit2-inventory-contract-v1.json",
    "audit/pass10/receipts/RECEIPT_P10_U2_BANK_INVENTORY_CONTRACT_20260726T220000Z_001.json",
    "tools/run_pass10_unit2_bank_inventory_contract_v1.js",
    "tools/test_pass10_unit2_bank_inventory_contract_v1.js",
    "tools/verify_pass10_unit2_bank_inventory_contract_v1.py",
}
INPUTS = {
    "unit1_inventory_sha256": ROOT
    / "audit/pass10/pass10-bank-unit1-inventory-reconciliation-v1.json",
    "pass9_closure_sha256": ROOT
    / "audit/pass9/pass9-bank-continuous-run-unit7-closure-certification-v1.json",
    "runner_sha256": RUNNER,
    "test_sha256": TEST,
}


def output(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed_paths(base: str) -> set[str]:
    rows: set[str] = set()
    for command in (
        ("git", "diff", "--name-only", f"{base}...HEAD"),
        ("git", "diff", "--name-only", base),
        ("git", "ls-files", "--others", "--exclude-standard"),
    ):
        rows.update(filter(None, output(*command).splitlines()))
    return rows


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
    unit1 = json.loads(INPUTS["unit1_inventory_sha256"].read_text())
    assert report["base_main_commit"] == BASE
    assert report["unit_id"] == "P10-U2"
    assert report["status"] == "BANK_INVENTORY_CONTRACT_PROVEN"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == []
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["status"] == report["status"]
    for key, path in INPUTS.items():
        assert report["inputs"][key] == sha(path), (
            key,
            report["inputs"][key],
            sha(path),
        )

    runtime = json.loads(output("node", str(RUNNER.relative_to(ROOT))))
    assert runtime["type"] == "PMP_PASS10_UNIT2_BANK_INVENTORY_CONTRACT_RESULT_V1"
    assert runtime["status"] == "PASS"
    assert runtime["summary"] == {
        "items": 0,
        "active": 0,
        "reference_only": 0,
        "quarantined": 0,
        "orphaned": 0,
        "stale": 0,
        "unavailable": 0,
        "corrupt": 0,
        "identities": 0,
        "exact_payload_bytes_preserved": 0,
    }
    assert runtime["items"] == []
    assert runtime["result_sha256"] == report["contract_verification"]["result_sha256"]
    assert all(value is False for value in runtime["effects"].values())

    test_output = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"contract \((\d+)/(\d+)\)", test_output)
    assert match and match.group(1) == match.group(2) == "187"
    assertions = int(match.group(1))
    assert report["verification"]["assertions_total"] == assertions
    assert report["verification"]["assertions_passed"] == assertions
    assert report["verification"]["assertions_failed"] == 0
    assert receipt["coverage"]["assertions"] == assertions

    contract = runtime["contract"]
    summary = report["inventory_contract"]
    assert contract["contract_version"] == summary["contract_version"]
    assert contract["item_version"] == summary["item_version"]
    assert contract["model"] == summary["model"]
    stable_policy = output(
        "node",
        "-e",
        "const r=require('./tools/run_pass10_unit2_bank_inventory_contract_v1.js');"
        "process.stdout.write(r.sha256(r.policy()))",
    )
    assert stable_policy == summary["contract_sha256"]
    assert contract["canonical_inventory"]["storage_key"] == "pmp_master_bank_inventory_v1"
    assert contract["canonical_inventory"]["owner_id"] == "bank_screen_owner"
    assert len(contract["canonical_inventory"]["bank_ids"]) == 13
    assert len(set(contract["canonical_inventory"]["bank_ids"])) == 13
    assert len(contract["required_source_fields"]) == 9
    assert len(set(contract["required_source_fields"])) == 9
    assert len(contract["canonical_item_fields"]) == 18
    assert len(set(contract["canonical_item_fields"])) == 18
    assert len(contract["namespace_rules"]) == 16
    assert len(
        {
            (row["storage_kind"], row["namespace"])
            for row in contract["namespace_rules"]
        }
    ) == 16
    assert len(contract["quarantine"]["reasons"]) == 15
    assert contract["quarantine"]["policy"] == (
        "PRESERVE_EXACT_BYTES_NEVER_SILENTLY_DELETE"
    )
    assert contract["delete_contract"]["default"] == "DENY"
    assert contract["delete_contract"]["bank_tab_delete_api"] == "FORBIDDEN"
    assert contract["delete_contract"]["production_delete_enabled_in_p10_u2"] is False
    assert contract["compatibility"]["silent_alias_merge"] == "FORBIDDEN"
    assert contract["compatibility"]["silent_schema_upgrade"] == "FORBIDDEN"
    assert contract["compatibility"]["helper_registration_conveys_bank_authority"] is False
    assert contract["representation_contract"] == {
        "projection_mode": "READ_ONLY_OWNER_FACTS",
        "enumerate_only_declared_namespaces": False,
        "unknown_namespaces_visible_as_quarantine": True,
        "raw_payload_exposed_to_ui": False,
        "write_api_exposed_to_ui": False,
        "delete_api_exposed_to_ui": False,
        "migration_api_exposed_to_ui": False,
        "recurring_polling_required": False,
        "owner_event_updates_only": True,
    }

    assert len(unit1["findings"]) == 6
    assert [row["finding_id"] for row in report["finding_resolutions"]] == [
        row["id"] for row in unit1["findings"]
    ]
    assert len(report["finding_resolutions"]) == 6
    assert report["contract_verification"] == {
        "namespace_rules": 16,
        "canonical_banks": 13,
        "required_source_fields": 9,
        "canonical_item_fields": 18,
        "quarantine_reason_codes": 15,
        "inventory_states": 8,
        "finding_resolutions": 6,
        "assertions": 187,
        "result_sha256": runtime["result_sha256"],
    }

    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "static_contract"
    assert binding["diagnostic_matrix_update"]["status"] == "ADDED"
    assert len(binding["fault_injection"]["cases"]) == 18
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    assert binding["special_authority"] == {
        "required": False,
        "granted": False,
        "consumed": False,
    }
    gate = json.loads(output("python3", str(GATE.relative_to(ROOT)), "--base", BASE))
    assert gate["status"] == "PASS", gate
    assert gate["unit_id"] == "P10-U2"
    assert gate["summary"]["runtime_paths"] == 0
    assert gate["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for token in (
        "actions/setup-node@v4",
        "node-version: '22'",
        "actions/setup-python@v5",
        "python-version: '3.12'",
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete P10-U2 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert token in workflow
    assert workflow.index("Upload complete P10-U2 evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )

    assert all(value is False for value in report["effects"].values())
    assert all(value is False for value in receipt["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["next_step"]["id"] == "P10-U3"
    assert report["next_step"]["requires_user_app_check"] is False
    assert report["next_step"]["persisted_user_data_change_allowed"] is False
    assert receipt["next_safe_move"]["step_id"] == "P10-U3"
    print(
        "PASS: exact six-file P10-U2 Bank inventory contract verified "
        "(187/187, gate PASS, zero effects, P10-U3 ready)"
    )


if __name__ == "__main__":
    main()
