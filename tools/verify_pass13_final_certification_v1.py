#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "e3e0fecfe4db33b6f6d7b447c4180b74409d8090"
TREE = "f1dca0d7aebe389986ada14481e34572896086aa"
WORKFLOW = ROOT / ".github/workflows/pass13-final-certification-v1.yml"
RUNNER = ROOT / "tools/run_pass13_end_to_end_regression_v1.py"
BUILDER = ROOT / "tools/build_pass13_release_packages_v1.py"
PERMANENT_GATE = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
LEDGER = ROOT / "audit/pass13/PMP_APP_ORCHESTRATOR_PASS_CLOSURE_LEDGER_V1.json"
AUTHORITY = ROOT / "audit/pass13/PMP_APP_ORCHESTRATOR_AUTHORITY_MATRIX_V1.json"
RELEASE = ROOT / "audit/pass13/PMP_APP_ORCHESTRATOR_RELEASE_INPUT_MANIFEST_V1.json"
POINTER = ROOT / "audit/pass13/PMP_APP_ORCHESTRATOR_FINAL_COMPLETION_POINTER_V1.json"

REPORTS = [
    ROOT / "audit/pass13/pass13-unit1-history-reconciliation-v1.json",
    ROOT / "audit/pass13/pass13-unit2-end-to-end-regression-v1.json",
    ROOT / "audit/pass13/pass13-unit3-release-identity-v1.json",
    ROOT / "audit/pass13/pass13-unit4-package-portability-v1.json",
    ROOT / "audit/pass13/pass13-unit5-locked-operations-packet-v1.json",
    ROOT / "audit/pass13/pass13-unit6-independent-final-audit-v1.json",
]
RECEIPTS = [
    ROOT / "audit/pass13/receipts/RECEIPT_P13_U1_HISTORY_RECONCILIATION_20260727T074000Z_001.json",
    ROOT / "audit/pass13/receipts/RECEIPT_P13_U2_END_TO_END_REGRESSION_20260727T074100Z_001.json",
    ROOT / "audit/pass13/receipts/RECEIPT_P13_U3_RELEASE_IDENTITY_20260727T074200Z_001.json",
    ROOT / "audit/pass13/receipts/RECEIPT_P13_U4_PACKAGE_PORTABILITY_20260727T074300Z_001.json",
    ROOT / "audit/pass13/receipts/RECEIPT_P13_U5_LOCKED_PACKET_20260727T074400Z_001.json",
    ROOT / "audit/pass13/receipts/RECEIPT_P13_U6_FINAL_COMPLETION_20260727T074500Z_001.json",
]
EXPECTED = {
    ".github/workflows/pass13-final-certification-v1.yml",
    "audit/pass13/PMP_APP_ORCHESTRATOR_AUTHORITY_MATRIX_V1.json",
    "audit/pass13/PMP_APP_ORCHESTRATOR_DIAGNOSTICS_GUIDE_V1.md",
    "audit/pass13/PMP_APP_ORCHESTRATOR_FINAL_COMPLETION_POINTER_V1.json",
    "audit/pass13/PMP_APP_ORCHESTRATOR_LOCKED_IMPLEMENTATION_PACKET_V1.md",
    "audit/pass13/PMP_APP_ORCHESTRATOR_MAINTENANCE_AND_FUTURE_CHANGE_RULES_V1.md",
    "audit/pass13/PMP_APP_ORCHESTRATOR_OPERATOR_GUIDE_V1.md",
    "audit/pass13/PMP_APP_ORCHESTRATOR_PASS_CLOSURE_LEDGER_V1.json",
    "audit/pass13/PMP_APP_ORCHESTRATOR_RECOVERY_GUIDE_V1.md",
    "audit/pass13/PMP_APP_ORCHESTRATOR_RELEASE_INPUT_MANIFEST_V1.json",
    "audit/pass13/pass13-unit1-history-reconciliation-v1.json",
    "audit/pass13/pass13-unit2-end-to-end-regression-v1.json",
    "audit/pass13/pass13-unit3-release-identity-v1.json",
    "audit/pass13/pass13-unit4-package-portability-v1.json",
    "audit/pass13/pass13-unit5-locked-operations-packet-v1.json",
    "audit/pass13/pass13-unit6-independent-final-audit-v1.json",
    "audit/pass13/receipts/RECEIPT_P13_U1_HISTORY_RECONCILIATION_20260727T074000Z_001.json",
    "audit/pass13/receipts/RECEIPT_P13_U2_END_TO_END_REGRESSION_20260727T074100Z_001.json",
    "audit/pass13/receipts/RECEIPT_P13_U3_RELEASE_IDENTITY_20260727T074200Z_001.json",
    "audit/pass13/receipts/RECEIPT_P13_U4_PACKAGE_PORTABILITY_20260727T074300Z_001.json",
    "audit/pass13/receipts/RECEIPT_P13_U5_LOCKED_PACKET_20260727T074400Z_001.json",
    "audit/pass13/receipts/RECEIPT_P13_U6_FINAL_COMPLETION_20260727T074500Z_001.json",
    "tools/build_pass13_release_packages_v1.py",
    "tools/run_pass13_end_to_end_regression_v1.py",
    "tools/verify_pass13_final_certification_v1.py",
}
STATUSES = [
    "COMPLETE_HISTORY_RECONCILIATION_GREEN",
    "FULL_DETERMINISTIC_E2E_AND_FAULT_SUITE_GREEN",
    "RELEASE_IDENTITY_INPUTS_VERIFIED",
    "PACKAGE_BUILD_CONTRACT_AND_PORTABILITY_REHEARSAL_GREEN",
    "LOCKED_IMPLEMENTATION_AND_OPERATIONS_PACKET_COMPLETE",
    "PASS13_FINAL_LOCKED_IMPLEMENTATION_PACKET_CERTIFIED",
]
NEXT = ["P13-U2", "P13-U3", "P13-U4", "P13-U5", "P13-U6", "POSTMERGE_BIND_AND_MAINTENANCE"]


def output(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def changed(base: str) -> set[str]:
    paths: set[str] = set()
    for command in (
        ("git", "diff", "--name-only", f"{base}...HEAD"),
        ("git", "diff", "--name-only", base),
        ("git", "ls-files", "--others", "--exclude-standard"),
    ):
        paths.update(filter(None, output(*command).splitlines()))
    return paths


def workflow_paths(text: str) -> set[str]:
    match = re.search(r"(?m)^    paths:\n(?P<rows>(?:      - [^\n]+\n)+)", text)
    assert match
    return {
        row.strip()[2:].strip().strip("'\"")
        for row in match.group("rows").splitlines()
    }


def main() -> None:
    base = sys.argv[1] if len(sys.argv) > 1 else BASE
    assert base == BASE, (base, BASE)
    actual = changed(base)
    assert actual == EXPECTED, (sorted(actual), sorted(EXPECTED))

    reports = [json.loads(path.read_text()) for path in REPORTS]
    receipts = [json.loads(path.read_text()) for path in RECEIPTS]
    for index, (report, receipt) in enumerate(zip(reports, receipts), 1):
        assert report["base_main_commit"] == BASE
        assert report["unit_id"] == f"P13-U{index}"
        assert report["status"] == STATUSES[index - 1]
        assert report["next_step"]["id"] == NEXT[index - 1]
        assert receipt["base_main_commit"] == BASE
        assert receipt["unit"] == f"P13-U{index}"
        assert receipt["status"] == report["status"]
        assert receipt["evidence"] == REPORTS[index - 1].relative_to(ROOT).as_posix()
        assert receipt["next_safe_move"]["step_id"] == NEXT[index - 1]
        for record in (report, receipt):
            assert record["effects"]["persisted_user_data_changed"] is False
            assert record["effects"]["production_migration_performed"] is False
            assert record["effects"]["formal_proof_performed"] is False
            assert record["effects"]["special_authority_consumed"] is False

    ledger = json.loads(LEDGER.read_text())
    assert len(ledger["entries"]) == 13
    assert [row["pass"] for row in ledger["entries"]] == list(range(1, 14))
    for row in ledger["entries"][:12]:
        assert (ROOT / row["closure_evidence"]).is_file()
        assert (ROOT / row["closure_receipt"]).is_file()
    assert ledger["reconciliation"]["passes_with_traceable_closure_evidence"] == 13
    assert ledger["reconciliation"]["historical_receipts_rewritten"] == 0
    assert ledger["reconciliation"]["historical_failures_erased"] == 0
    assert ledger["reconciliation"]["unresolved_claims_presented_as_complete"] == 0
    assert len(ledger["historical_exceptions"]) == 4

    authority = json.loads(AUTHORITY.read_text())
    assert authority["default_decision"] == "DENY"
    assert len(authority["rules"]) == 9
    assert authority["formal_proof_state"]["historical_pr122_receipt082"].startswith("CONSUMED_FAILED")
    assert authority["formal_proof_state"]["later_contingent_authorization"] == "UNCONSUMED"
    assert authority["formal_proof_state"]["formal_proof_run_by_pass13"] is False
    assert authority["production_migration_state"]["gate"] == "INACTIVE"
    assert authority["production_migration_state"]["performed"] is False
    assert authority["production_migration_state"]["persisted_user_data_changed"] is False

    release = json.loads(RELEASE.read_text())
    assert release["certification_base_main_commit"] == BASE
    assert release["certification_base_tree"] == TREE
    assert release["certification_base_blob_count"] == 2076
    assert release["runtime_manifest_records"] == 716
    for row in release["inputs"]:
        payload = subprocess.check_output(
            ["git", "show", f"{BASE}:{row['path']}"], cwd=ROOT
        )
        assert len(payload) == row["bytes"], row["path"]
        assert sha(payload) == row["sha256"], row["path"]

    pointer = json.loads(POINTER.read_text())
    assert pointer["status"] == "CERTIFIED_PENDING_EXACT_GREEN_MERGE_AND_POSTMERGE_PACKAGE_BINDING"
    assert pointer["completed_roadmap"]["first_pass"] == 1
    assert pointer["completed_roadmap"]["last_pass"] == 13
    assert pointer["completed_roadmap"]["passes_with_traceable_closure_evidence"] == 13
    assert len(pointer["postmerge_activation_conditions"]) == 6
    assert pointer["next_safe_move_after_activation"]["id"] == "MAINTENANCE_ONLY"
    assert pointer["authority_state"]["later_contingent_formal_proof_authorization"] == "UNCONSUMED"
    assert pointer["authority_state"]["production_migration_performed"] is False

    documents = [
        ROOT / "audit/pass13/PMP_APP_ORCHESTRATOR_LOCKED_IMPLEMENTATION_PACKET_V1.md",
        ROOT / "audit/pass13/PMP_APP_ORCHESTRATOR_OPERATOR_GUIDE_V1.md",
        ROOT / "audit/pass13/PMP_APP_ORCHESTRATOR_RECOVERY_GUIDE_V1.md",
        ROOT / "audit/pass13/PMP_APP_ORCHESTRATOR_DIAGNOSTICS_GUIDE_V1.md",
        ROOT / "audit/pass13/PMP_APP_ORCHESTRATOR_MAINTENANCE_AND_FUTURE_CHANGE_RULES_V1.md",
    ]
    assert all(path.stat().st_size > 700 for path in documents)
    combined = "\n".join(path.read_text() for path in documents)
    for token in (
        "No silent authority gain",
        "PRODUCTION_GATE_INACTIVE",
        "PR #122",
        "Pass 14",
        "case-insensitive",
        "append-only",
        "no-blind-flying",
    ):
        assert token.lower() in combined.lower(), token

    runner_lines = output(
        "python3", RUNNER.relative_to(ROOT).as_posix()
    ).splitlines()
    result = json.loads(runner_lines[-1])
    assert result["status"] == "PASS"
    assert result["component_suites"] == 12
    assert result["component_assertions"] == 1673
    assert result["orchestration_assertions"] == 1522
    assert result["assertions_total"] == 3195
    assert result["assertions_failed"] == 0
    assert len(result["fault_classes"]) == 11
    assert result["effects"]["persisted_user_data_changed"] is False
    assert result["effects"]["formal_proof_performed"] is False

    with tempfile.TemporaryDirectory(prefix="pmp-pass13-package-") as tmp:
        temp = Path(tmp)
        package_text = output(
            "python3",
            BUILDER.relative_to(ROOT).as_posix(),
            "--repo",
            ".",
            "--commit",
            BASE,
            "--metadata-dir",
            "audit/pass13",
            "--full",
            str(temp / "full.zip"),
            "--full-sidecar",
            str(temp / "full.zip.sha256"),
            "--compact",
            str(temp / "compact.zip"),
            "--compact-sidecar",
            str(temp / "compact.zip.sha256"),
        )
        package = json.loads(package_text)
        assert package["status"] == "PASS"
        assert package["commit"] == BASE
        assert package["tree"] == TREE
        assert package["full"]["repository_records"] == 2076
        assert package["full"]["crc"] == "PASS"
        assert package["compact"]["crc"] == "PASS"
        assert package["casefold_collision_preserved_in_full"] is True
        assert package["earlier_packages_modified"] is False

    closure = reports[-1]
    assert set(closure["scope"]["changed_paths"]) == EXPECTED
    assert closure["scope"]["implementation_paths"] == []
    assert closure["pass13_result"] == "PASS_CERTIFIED_PENDING_POSTMERGE_BINDING"
    assert closure["closure"]["completed_units"] == 6
    assert closure["closure"]["passes_reconciled"] == 13
    assert closure["closure"]["deterministic_assertions"] == 3195
    assert closure["closure"]["deterministic_assertions_failed"] == 0
    assert closure["closure"]["runtime_behavior_changed_by_pass13"] is False
    assert all(closure["premerge_exit_criteria"].values())
    assert len(closure["postmerge_completion_conditions"]) == 6
    assert closure["authority"]["later_contingent_formal_proof_authorization_consumed"] is False
    assert closure["next_step"]["id"] == "POSTMERGE_BIND_AND_MAINTENANCE"

    binding = closure["no_blind_flying_gate"]
    assert binding["ci_lane"] == "deterministic_integration"
    assert binding["diagnostic_matrix_update"]["status"] == "ADDED"
    assert len(binding["diagnostic_evidence_routes"]) == 6
    assert binding["fault_injection"]["status"] == "COVERED"
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    gate = json.loads(
        output("python3", PERMANENT_GATE.relative_to(ROOT).as_posix(), "--base", BASE)
    )
    assert gate["status"] == "PASS", gate
    assert gate["unit_id"] == "P13-U6"
    assert gate["summary"]["runtime_paths"] == 0
    assert gate["summary"]["changed_paths"] == 25
    assert gate["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for token in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete Pass 13 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert token in workflow, token
    assert workflow.index("Upload complete Pass 13 evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    print(
        "PASS: exact 25-path Pass 13 final locked packet verified "
        "(3195/3195, 13-pass ledger, exact release identities, full/compact "
        "package rehearsal, permanent gate PASS; post-merge binding ready)"
    )


if __name__ == "__main__":
    main()
