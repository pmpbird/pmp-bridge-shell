#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "92069614248bce9aea81822ad6df1cf1a030f6a8"
REPORT = ROOT / "audit/pass9/pass9-bank-continuous-run-unit1-inventory-v1.json"
RECEIPT = ROOT / "audit/pass9/receipts/RECEIPT_P9_U1_BANK_CONTINUOUS_RUN_INVENTORY_20260726T192000Z_001.json"
RUNNER = ROOT / "tools/run_pass9_unit1_bank_continuous_run_inventory_v1.py"
TEST = ROOT / "tools/test_pass9_unit1_bank_continuous_run_inventory_v1.py"
WORKFLOW = ROOT / ".github/workflows/pass9-unit1-bank-continuous-run-inventory-v1.yml"
GATE_RUNNER = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
EXPECTED = {
    ".github/workflows/pass9-unit1-bank-continuous-run-inventory-v1.yml",
    "audit/pass9/pass9-bank-continuous-run-unit1-inventory-v1.json",
    "audit/pass9/receipts/RECEIPT_P9_U1_BANK_CONTINUOUS_RUN_INVENTORY_20260726T192000Z_001.json",
    "tools/run_pass9_unit1_bank_continuous_run_inventory_v1.py",
    "tools/test_pass9_unit1_bank_continuous_run_inventory_v1.py",
    "tools/verify_pass9_unit1_bank_continuous_run_inventory_v1.py",
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
    assert report["unit_id"] == "P9-U1"
    assert report["status"] == "BANK_CONTINUOUS_RUN_INVENTORY_PROVEN"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == []
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["status"] == report["status"]
    assert report["inputs"]["runner_sha256"] == sha(RUNNER)
    assert report["inputs"]["test_sha256"] == sha(TEST)

    test_output = output(sys.executable, str(TEST.relative_to(ROOT)))
    match = re.search(r"inventory \((\d+)/(\d+)\)", test_output)
    assert match and match.group(1) == match.group(2)
    assertions = int(match.group(1))
    assert assertions == report["verification"]["assertions_passed"]
    assert assertions == report["verification"]["assertions_total"]
    assert report["verification"]["assertions_failed"] == 0
    assert report["inventory"]["unique_relevant_sources"] == 35
    assert report["inventory"]["relevant_occurrences"] == 37
    assert report["inventory"]["storage_writer_sources"] == 24
    assert report["inventory"]["recurring_interval_sources"] == 19
    assert report["inventory"]["all_relevant_sources_integrity_sealed"] is True
    assert len(report["conflicts"]) == 9
    assert report["p9_u2_requirements"]["cross_delegation"] == "FORBIDDEN"
    assert report["next_step"]["id"] == "P9-U2"
    assert report["next_step"]["requires_user_app_check"] is False

    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "static_contract"
    assert binding["diagnostic_matrix_update"]["status"] == "CONFIRMED_UNCHANGED"
    assert binding["fault_injection"]["status"] == "NOT_APPLICABLE"
    assert binding["fault_injection"]["cases"] == []
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    gate = json.loads(output(sys.executable, str(GATE_RUNNER.relative_to(ROOT)), "--base", BASE))
    assert gate["status"] == "PASS"
    assert gate["unit_id"] == "P9-U1"
    assert gate["gate_records"] == 1
    assert gate["summary"]["runtime_paths"] == 0
    assert gate["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for required in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete P9-U1 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert required in workflow
    assert workflow.index("Upload complete P9-U1 evidence") < workflow.index("Enforce preserved result after upload")
    assert workflow.rstrip().endswith('run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"')

    assert all(value is False for value in report["effects"].values())
    assert all(value is False for value in receipt["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert receipt["next_safe_move"]["step_id"] == "P9-U2"
    print(
        "PASS: exact six-file P9-U1 Bank and Continuous Run inventory verified "
        f"({assertions}/{assertions}, gate PASS, zero effects)"
    )


if __name__ == "__main__":
    main()
