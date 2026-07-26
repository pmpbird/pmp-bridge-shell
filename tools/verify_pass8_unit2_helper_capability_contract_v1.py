#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "40a3334564aa1d8385c523a40835ad085580da2e"
REPORT = ROOT / "audit/pass8/pass8-helper-unit2-capability-contract-v1.json"
RECEIPT = (
    ROOT
    / "audit/pass8/receipts/RECEIPT_P8_U2_HELPER_CAPABILITY_CONTRACT_20260726T175000Z_001.json"
)
RUNNER = ROOT / "tools/run_pass8_unit2_helper_capability_contract_v1.js"
TEST = ROOT / "tools/test_pass8_unit2_helper_capability_contract_v1.js"
WORKFLOW = ROOT / ".github/workflows/pass8-unit2-helper-capability-contract-v1.yml"
GATE_RUNNER = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
EXPECTED = {
    ".github/workflows/pass8-unit2-helper-capability-contract-v1.yml",
    "audit/pass8/pass8-helper-unit2-capability-contract-v1.json",
    "audit/pass8/receipts/RECEIPT_P8_U2_HELPER_CAPABILITY_CONTRACT_20260726T175000Z_001.json",
    "tools/run_pass8_unit2_helper_capability_contract_v1.js",
    "tools/test_pass8_unit2_helper_capability_contract_v1.js",
    "tools/verify_pass8_unit2_helper_capability_contract_v1.py",
}
SOURCE_INPUTS = {
    "unit1_inventory_sha256": ROOT / "audit/pass8/pass8-helper-unit1-inventory-v1.json",
    "helper_rules_sha256": ROOT / "pmp-pass8-helper-rules-v1.js",
    "pass7_owner_contract_sha256": ROOT
    / "audit/pass7/pass7-section-owner-unit2-capability-contract-v1.json",
    "cross_system_invariant_catalog_sha256": ROOT
    / "audit/pass6/pass6-cross-system-invariant-catalog-v1.json",
    "runner_sha256": RUNNER,
    "test_sha256": TEST,
}
EXPECTED_COUNTS = {
    "declared_helpers": 14,
    "eligible_helpers": 12,
    "held_declared_helpers": 2,
    "owner_bindings": 8,
    "guarded_helpers": 2,
    "growth_helpers": 1,
    "legacy_helpers": 1,
    "unknown_helper_sources": 9,
}
EXPECTED_ALIASES = {
    "app_orchestrator": ("app_orchestrator_owner", "app_orchestrator", "OWNER_ALIAS"),
    "mount_registry": ("mount_registry_owner", "mount_registry", "OWNER_ALIAS"),
    "continuous_run_owner": (
        "continuous_run_level_owner",
        "continuous_run",
        "OWNER_ALIAS",
    ),
    "active_path_discovery_owner": (
        "app_orchestrator_owner",
        "app_orchestrator",
        "BOUNDED_SUBDOMAIN",
    ),
    "runtime_health_monitor": ("diagnostics_owner", "diagnostics", "BOUNDED_SUBDOMAIN"),
    "runtime_version_manager": ("diagnostics_owner", "diagnostics", "BOUNDED_SUBDOMAIN"),
    "bug_bank_owner": ("bank_screen_owner", "bank", "GUARDED_SUBDOMAIN"),
    "safe_writer_owner": ("reload_current_owner", "current_reload", "HELD_SUBDOMAIN"),
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
    assert report["base_main_commit"] == BASE
    assert report["unit_id"] == "P8-U2"
    assert report["status"] == "HELPER_CAPABILITY_CONTRACT_PROVEN"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == []
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["status"] == report["status"]
    for key, path in SOURCE_INPUTS.items():
        assert report["inputs"][key] == sha(path), (key, report["inputs"][key], sha(path))

    runtime = json.loads(output("node", str(RUNNER.relative_to(ROOT))))
    assert runtime["type"] == "PMP_PASS8_UNIT2_HELPER_CAPABILITY_RESULT_V1"
    assert runtime["status"] == "PASS"
    assert runtime["inventory"]["counts"] == EXPECTED_COUNTS
    assert runtime["outcomes"] == []
    assert runtime["summary"]["events"] == 0
    assert runtime["result_sha256"] == report["contract_verification"]["result_sha256"]
    assert all(value is False for value in runtime["effects"].values())

    test_output = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"contract \((\d+)/(\d+)\)", test_output)
    assert match and match.group(1) == match.group(2)
    assertions = int(match.group(1))
    assert assertions == report["verification"]["assertions_passed"] == 255
    assert report["verification"]["assertions_failed"] == 0
    assert receipt["coverage"]["assertions"] == assertions

    contract = report["helper_contract"]
    assert contract["contract_version"] == "PMP_HELPER_CAPABILITY_CONTRACT_V1"
    assert contract["model"] == "EXPLICIT_HELPER_CAPABILITY_FAIL_CLOSED"
    assert contract["root_grant_authority"] == "app_orchestrator_owner"
    assert len(contract["required_capability_fields"]) == 18
    assert len(set(contract["required_capability_fields"])) == 18
    assert set(contract["owner_bindings"]) == set(EXPECTED_ALIASES)
    for label, expected in EXPECTED_ALIASES.items():
        binding = contract["owner_bindings"][label]
        assert (
            binding["canonical_owner_id"],
            binding["section_id"],
            binding["binding_kind"],
        ) == expected
    assert contract["owner_bindings"]["bug_bank_owner"]["guard_requirements"] == [
        "bounded_bug_authority_lease",
        "private_owner_token",
        "unexpired_lease",
        "formal_handoff",
    ]
    assert contract["explicit_helper_holds"] == {
        "safe_writer_current_return_fix": (
            "DECLARATION_AND_SOURCE_ROUTE_BEHAVIOR_REQUIRE_LATER_EXPLICIT_OWNER_RECONCILIATION"
        )
    }
    unit1 = json.loads(SOURCE_INPUTS["unit1_inventory_sha256"].read_text())
    assert contract["unknown_helper_sources"] == (
        unit1["conflicts"]["helper_named_sources_without_pass8_declaration"]
    )
    assert contract["legacy_policy"] == "HOLD_NO_ACTIVE_CAPABILITY"
    assert contract["unknown_source_policy"] == "HOLD_NO_CAPABILITY"
    assert contract["filename_authority_policy"] == "NEVER_INFER_AUTHORITY"
    assert contract["growth_policy"] == (
        "EXACT_DECLARED_SOURCE_OWNER_SLOT_AND_GROWTH_BINDING"
    )
    assert contract["revocation_policy"] == "MONOTONIC_FAIL_CLOSED"
    assert len(contract["failure_codes"]) == len(set(contract["failure_codes"])) == 36
    assert report["contract_verification"] == {
        "declared_helpers": 14,
        "eligible_static_capabilities": 12,
        "held_declared_helpers": 2,
        "owner_labels_resolved": 8,
        "guarded_helpers": 2,
        "growth_helpers": 1,
        "legacy_helpers_held": 1,
        "unknown_sources_held": 9,
        "result_sha256": runtime["result_sha256"],
    }

    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "static_contract"
    assert binding["diagnostic_matrix_update"]["status"] == "CONFIRMED_UNCHANGED"
    assert binding["fault_injection"]["status"] == "COVERED"
    assert len(binding["fault_injection"]["cases"]) >= 16
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
    assert gate["unit_id"] == "P8-U2"
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
        "Upload complete P8-U2 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert required in workflow
    assert workflow.index("Upload complete P8-U2 evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )

    assert all(value is False for value in report["effects"].values())
    assert all(value is False for value in receipt["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["next_step"]["id"] == "P8-U3"
    assert report["next_step"]["requires_user_app_check"] is False
    assert report["next_step"]["requires_new_explicit_authority"] is False
    assert receipt["next_safe_move"]["step_id"] == "P8-U3"
    print(
        "PASS: exact six-file P8-U2 Helper capability contract verified "
        f"({assertions}/{assertions}, gate PASS, zero effects)"
    )


if __name__ == "__main__":
    main()
