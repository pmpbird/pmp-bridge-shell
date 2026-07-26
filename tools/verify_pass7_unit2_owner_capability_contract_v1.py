#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "be269c98b703a0a5b1695c9e6f7bc5b333ab1ac7"
REPORT = ROOT / "audit/pass7/pass7-section-owner-unit2-capability-contract-v1.json"
RECEIPT = ROOT / "audit/pass7/receipts/RECEIPT_P7_U2_OWNER_CAPABILITY_CONTRACT_20260726T162500Z_001.json"
RUNNER = ROOT / "tools/run_pass7_unit2_owner_capability_contract_v1.py"
TEST = ROOT / "tools/test_pass7_unit2_owner_capability_contract_v1.py"
WORKFLOW = ROOT / ".github/workflows/pass7-unit2-owner-capability-contract-v1.yml"
GATE_RUNNER = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
EXPECTED = {
    ".github/workflows/pass7-unit2-owner-capability-contract-v1.yml",
    "audit/pass7/pass7-section-owner-unit2-capability-contract-v1.json",
    "audit/pass7/receipts/RECEIPT_P7_U2_OWNER_CAPABILITY_CONTRACT_20260726T162500Z_001.json",
    "tools/run_pass7_unit2_owner_capability_contract_v1.py",
    "tools/test_pass7_unit2_owner_capability_contract_v1.py",
    "tools/verify_pass7_unit2_owner_capability_contract_v1.py",
}
SOURCE_INPUTS = {
    "unit1_inventory_sha256": ROOT / "audit/pass7/pass7-section-owner-unit1-inventory-v1.json",
    "section_owner_registry_sha256": ROOT / "pmp-section-owner-registry-v1.js",
    "actor_authority_policy_sha256": ROOT / "pmp-actor-authority-policy-v1.json",
    "cross_system_invariant_catalog_sha256": ROOT / "audit/pass6/pass6-cross-system-invariant-catalog-v1.json",
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
    assert not any(
        Path(path).suffix.lower() in {".js", ".html", ".css", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"}
        and not path.startswith((".github/", "audit/", "tools/", "docs/"))
        for path in changed
    )

    report = json.loads(REPORT.read_text())
    receipt = json.loads(RECEIPT.read_text())
    contract = report["capability_contract"]
    assert report["base_main_commit"] == BASE
    assert report["unit_id"] == "P7-U2"
    assert report["status"] == "SECTION_OWNER_CAPABILITY_CONTRACT_PROVEN"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == []
    assert receipt["status"] == report["status"]
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["evidence"] == REPORT.relative_to(ROOT).as_posix()
    for key, path in SOURCE_INPUTS.items():
        assert report["inputs"][key] == sha(path), (key, report["inputs"][key], sha(path))

    assert contract["contract_version"] == "PMP_SECTION_OWNER_CAPABILITY_CONTRACT_V1"
    assert contract["model"] == "EXPLICIT_CAPABILITY_FAIL_CLOSED"
    assert contract["root_grant_authority"] == "app_orchestrator_owner"
    assert len(contract["owners"]) == 8
    assert len({row["section_id"] for row in contract["owners"].values()}) == 8
    assert contract["delegation"]["maximum_depth"] == 2
    assert contract["delegation"]["authority_expansion"] == "FORBIDDEN"
    assert contract["delegation"]["revocation"] == "MONOTONIC_CASCADING"
    assert contract["unknown_owner_policy"] == "REJECT_BEFORE_SIDE_EFFECT"
    assert contract["duplicate_owner_policy"] == "FAIL_CLOSED_AND_DIAGNOSE"
    assert contract["stale_capability_policy"] == "REJECT_BEFORE_SIDE_EFFECT"
    assert {
        "route_mutation",
        "bank_mutation",
        "helper_ownership",
        "other_section_mutation",
        "storage_migration",
        "persisted_user_data_write",
        "production_activation",
        "ownership_takeover",
    } <= set(contract["globally_forbidden_actions"])

    test_output = output("python3", str(TEST.relative_to(ROOT)))
    match = re.search(r"owner capability contract \((\d+)/(\d+)\)", test_output)
    assert match and match.group(1) == match.group(2)
    assertions = int(match.group(1))
    assert assertions >= 100
    result = json.loads(output("python3", str(RUNNER.relative_to(ROOT))))
    assert result["status"] == "PASS"
    assert result["summary"]["owners_contract_bound"] == 8
    assert result["summary"]["positive_events"] == 5
    assert result["summary"]["positive_accepted"] == 4
    assert result["summary"]["revocation_cascade_members"] == 2
    assert result["summary"]["denial_scenarios"] == 4
    assert result["summary"]["denial_scenarios_matched"] == 4
    assert result["result_sha256"] == report["contract_verification"]["result_sha256"]
    assert assertions == report["verification"]["assertions_passed"]
    assert all(value is False for value in result["effects"].values())

    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "static_contract"
    assert binding["diagnostic_matrix_update"]["status"] == "CONFIRMED_UNCHANGED"
    assert binding["diagnostic_matrix_update"]["applicable_matrix"] == (
        "audit/pass6/pass6-cross-system-invariant-catalog-v1.json"
    )
    assert binding["fault_injection"]["status"] == "COVERED"
    assert len(binding["fault_injection"]["cases"]) >= 10
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    assert binding["special_authority"]["consumed"] is False
    gate = json.loads(
        output(
            "python3",
            str(GATE_RUNNER.relative_to(ROOT)),
            "--base",
            BASE,
        )
    )
    assert gate["status"] == "PASS"
    assert gate["mode"] == "LATER_IMPLEMENTATION_UNIT"
    assert gate["unit_id"] == "P7-U2"
    assert gate["gate_records"] == 1
    assert gate["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for required in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete P7-U2 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert required in workflow
    assert workflow.index("Upload complete P7-U2 evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )

    assert all(value is False for value in report["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["authority"]["retry_authorized"] is False
    assert report["next_step"]["id"] == "P7-U3"
    assert report["next_step"]["requires_user_app_check"] is False
    assert receipt["next_safe_move"]["step_id"] == "P7-U3"
    assert receipt["next_safe_move"]["requires_user_app_check"] is False
    print(
        "PASS: exact six-file P7-U2 owner capability contract verified "
        f"(8 owners, {assertions}/{assertions} assertions, permanent gate PASS)"
    )


if __name__ == "__main__":
    main()
