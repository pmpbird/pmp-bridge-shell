#!/usr/bin/env python3
from __future__ import annotations

import json
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "be12da5ed841b4f80ba78b7203c6b7cf91567334"
WORKFLOW = ROOT / ".github/workflows/pass12-migration-plan-v1.yml"
PLAN = ROOT / "pmp-migration-plan-v1.json"
GATE_SOURCE = ROOT / "pmp-migration-inactive-gate-v1.js"
TEST = ROOT / "tools/test_pass12_migration_plan_v1.js"
MANIFEST = ROOT / "pmp-runtime-integrity-manifest-v1.json"
SEAL = ROOT / "audit/a003-manifest-seal.json"
BOOTSTRAP = ROOT / "pmp-app-current.html"
GENERATOR = ROOT / "tools/generate_pass12_migration_integrity_updates_v1.py"
PERMANENT_GATE = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"

REPORTS = [
    ROOT / "audit/pass12/pass12-unit1-source-target-inventory-v1.json",
    ROOT / "audit/pass12/pass12-unit2-migration-contract-v1.json",
    ROOT / "audit/pass12/pass12-unit3-disposable-dry-run-v1.json",
    ROOT / "audit/pass12/pass12-unit4-shadow-dual-read-v1.json",
    ROOT / "audit/pass12/pass12-unit5-inactive-gate-implementation-v1.json",
    ROOT / "audit/pass12/pass12-unit6-fault-rollback-proof-v1.json",
    ROOT / "audit/pass12/pass12-unit7-production-authority-gate-v1.json",
    ROOT / "audit/pass12/pass12-unit8-safe-closure-v1.json",
]
RECEIPTS = [
    ROOT / "audit/pass12/receipts/RECEIPT_P12_U1_SOURCE_TARGET_INVENTORY_20260727T073000Z_001.json",
    ROOT / "audit/pass12/receipts/RECEIPT_P12_U2_MIGRATION_CONTRACT_20260727T073100Z_001.json",
    ROOT / "audit/pass12/receipts/RECEIPT_P12_U3_DISPOSABLE_DRY_RUN_20260727T073200Z_001.json",
    ROOT / "audit/pass12/receipts/RECEIPT_P12_U4_SHADOW_DUAL_READ_20260727T073300Z_001.json",
    ROOT / "audit/pass12/receipts/RECEIPT_P12_U5_INACTIVE_GATE_20260727T073400Z_001.json",
    ROOT / "audit/pass12/receipts/RECEIPT_P12_U6_FAULT_ROLLBACK_20260727T073500Z_001.json",
    ROOT / "audit/pass12/receipts/RECEIPT_P12_U7_AUTHORITY_GATE_20260727T073600Z_001.json",
    ROOT / "audit/pass12/receipts/RECEIPT_P12_U8_SAFE_CLOSURE_20260727T073700Z_001.json",
]
EXPECTED = {
    ".github/workflows/pass12-migration-plan-v1.yml",
    "audit/a003-manifest-seal.json",
    "audit/pass12/pass12-unit1-source-target-inventory-v1.json",
    "audit/pass12/pass12-unit2-migration-contract-v1.json",
    "audit/pass12/pass12-unit3-disposable-dry-run-v1.json",
    "audit/pass12/pass12-unit4-shadow-dual-read-v1.json",
    "audit/pass12/pass12-unit5-inactive-gate-implementation-v1.json",
    "audit/pass12/pass12-unit6-fault-rollback-proof-v1.json",
    "audit/pass12/pass12-unit7-production-authority-gate-v1.json",
    "audit/pass12/pass12-unit8-safe-closure-v1.json",
    "audit/pass12/receipts/RECEIPT_P12_U1_SOURCE_TARGET_INVENTORY_20260727T073000Z_001.json",
    "audit/pass12/receipts/RECEIPT_P12_U2_MIGRATION_CONTRACT_20260727T073100Z_001.json",
    "audit/pass12/receipts/RECEIPT_P12_U3_DISPOSABLE_DRY_RUN_20260727T073200Z_001.json",
    "audit/pass12/receipts/RECEIPT_P12_U4_SHADOW_DUAL_READ_20260727T073300Z_001.json",
    "audit/pass12/receipts/RECEIPT_P12_U5_INACTIVE_GATE_20260727T073400Z_001.json",
    "audit/pass12/receipts/RECEIPT_P12_U6_FAULT_ROLLBACK_20260727T073500Z_001.json",
    "audit/pass12/receipts/RECEIPT_P12_U7_AUTHORITY_GATE_20260727T073600Z_001.json",
    "audit/pass12/receipts/RECEIPT_P12_U8_SAFE_CLOSURE_20260727T073700Z_001.json",
    "pmp-migration-inactive-gate-v1.js",
    "pmp-migration-plan-v1.json",
    "pmp-app-current.html",
    "pmp-runtime-integrity-manifest-v1.json",
    "tools/generate_pass12_migration_integrity_updates_v1.py",
    "tools/test_pass12_migration_plan_v1.js",
    "tools/verify_pass12_migration_plan_v1.py",
}
IMPLEMENTATION = {"pmp-app-current.html", "pmp-migration-inactive-gate-v1.js"}
STATUSES = [
    "SOURCE_TARGET_INVENTORY_COMPLETE",
    "MIGRATION_CONTRACT_LOCKED",
    "DISPOSABLE_FIXTURE_DRY_RUN_GREEN",
    "PURE_SHADOW_DUAL_READ_GREEN",
    "INACTIVE_MIGRATION_GATE_IMPLEMENTED",
    "FAULT_ROLLBACK_PRESERVATION_PROOF_GREEN",
    "BLOCKED_AUTHORITY",
    "PASS12_SAFE_BOUNDARY_COMPLETE_PRODUCTION_MIGRATION_BLOCKED_AUTHORITY",
]
NEXT = ["P12-U2", "P12-U3", "P12-U4", "P12-U5", "P12-U6", "P12-U7", "P12-U8", "P13-U1"]


def output(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


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


def assertion_total(text: str) -> int:
    match = re.search(r"\((\d+)/(\d+)\)", text)
    assert match and match.group(1) == match.group(2), text
    return int(match.group(1))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    base = sys.argv[1] if len(sys.argv) > 1 else BASE
    assert base == BASE, (base, BASE)
    actual = changed(base)
    assert actual == EXPECTED, (sorted(actual), sorted(EXPECTED))

    reports = [json.loads(path.read_text()) for path in REPORTS]
    receipts = [json.loads(path.read_text()) for path in RECEIPTS]
    for index, (report, receipt) in enumerate(zip(reports, receipts), 1):
        assert report["base_main_commit"] == BASE
        assert report["unit_id"] == f"P12-U{index}"
        assert report["status"] == STATUSES[index - 1]
        assert report["next_step"]["id"] == NEXT[index - 1]
        assert receipt["base_main_commit"] == BASE
        assert receipt["unit"] == f"P12-U{index}"
        assert receipt["status"] == report["status"]
        assert receipt["evidence"] == REPORTS[index - 1].relative_to(ROOT).as_posix()
        assert receipt["next_safe_move"]["step_id"] == NEXT[index - 1]
        for record in (report, receipt):
            assert record["effects"]["persisted_user_data_changed"] is False
            assert record["effects"]["production_migration_performed"] is False
            assert record["effects"]["formal_proof_performed"] is False
            assert record["effects"]["special_authority_consumed"] is False

    plan = json.loads(PLAN.read_text())
    assert plan["type"] == "PMP_MIGRATION_PLAN_V1"
    assert plan["base_main_commit"] == BASE
    assert plan["mode"] == "INACTIVE_NONPRODUCTION_PLAN"
    assert plan["default_decision"] == "DENY"
    assert plan["target"]["activation"] == "INACTIVE"
    assert plan["target"]["production_commit_available"] is False
    assert len(plan["inventory"]) == 7
    assert len({row["id"] for row in plan["inventory"]}) == 7
    assert len({row["owner"] for row in plan["inventory"]}) == 7
    assert len(plan["phases"]) == 8
    assert plan["checkpoints"]["append_only"] is True
    assert plan["checkpoints"]["overwrite_allowed"] is False
    assert plan["idempotency"]["repeat_dry_run"] == "EXACT_SAME_RESULT"
    assert plan["idempotency"]["automatic_retry"] is False
    assert plan["rollback"]["source_is_never_deleted"] is True
    assert plan["rollback"]["old_application_remains_recoverable"] is True
    assert plan["rollback"]["unrelated_storage_preserved"] is True
    assert plan["authority_gate"]["state"] == "INACTIVE"
    assert plan["authority_gate"]["production_migration_authorized"] is False
    assert plan["authority_gate"]["persisted_user_data_change_authorized"] is False
    assert plan["authority_gate"]["wildcards_allowed"] is False
    assert plan["authority_gate"]["automatic_retry"] is False
    for forbidden in (
        "PRODUCTION_STORAGE_READ",
        "PRODUCTION_STORAGE_WRITE",
        "PRODUCTION_STORAGE_DELETE",
        "PERSISTED_USER_DATA_CHANGE",
        "LIVE_MIGRATION",
        "SOURCE_DELETION",
        "AUTOMATIC_RETRY",
        "FORMAL_PROOF",
        "CONSUMED_OBSERVATION_RETRY",
    ):
        assert forbidden in plan["forbidden_pass12_operations"]

    source = GATE_SOURCE.read_text()
    for required in (
        "PRODUCTION_GATE_INACTIVE",
        "DISPOSABLE_FIXTURE",
        "ALLOW_DISPOSABLE_FIXTURE_ONLY",
        "QUARANTINE_UNKNOWN_OWNER",
        "DENIED_DUPLICATE_IDENTITY",
        "DENIED_RECORD_PAYLOAD_HASH",
        "INJECTED_PARTIAL_STAGE_FAILURE",
        "ROLLBACK_PLAN_READY",
        "requestProductionMigration",
        "authority_consumed:false",
    ):
        assert required in source, required
    for forbidden in (
        "localStorage",
        "sessionStorage",
        "indexedDB",
        "XMLHttpRequest",
        "WebSocket",
        "navigator.storage",
        "caches.open",
        "fetch(",
    ):
        assert forbidden not in source, forbidden

    runtime_extensions = {".js", ".mjs", ".cjs", ".html", ".css", ".ts", ".tsx", ".jsx"}
    runtime_refs: list[str] = []
    for item in ROOT.iterdir():
        if (
            item.is_file()
            and item != GATE_SOURCE
            and item.suffix.lower() in runtime_extensions
            and "pmp-migration-inactive-gate-v1.js" in item.read_text(errors="ignore")
        ):
            runtime_refs.append(item.name)
    assert runtime_refs == [], runtime_refs

    test_text = output("node", TEST.relative_to(ROOT).as_posix())
    assert assertion_total(test_text) == 389
    assert assertion_total(output("node", "tools/test_pass11_safety_no_deletion_v1.js")) == 186
    assert assertion_total(output("node", "tools/test_pass10_unit7_uniform_title_weight_v1.js")) == 86

    generated = [MANIFEST, SEAL, BOOTSTRAP]
    before = {path: sha(path) for path in generated}
    assert "PASS:" in output("python3", GENERATOR.relative_to(ROOT).as_posix())
    after = {path: sha(path) for path in generated}
    assert before == after
    manifest = json.loads(MANIFEST.read_text())
    records = {row["path"]: row for row in manifest["records"]}
    for path in (PLAN, GATE_SOURCE):
        relative = path.relative_to(ROOT).as_posix()
        assert records[relative]["sha256_hex"] == sha(path)
        assert records[relative]["bytes"] == len(path.read_bytes())
        assert records[relative]["enforcement"] == "SERVICE_WORKER_PRE_RESPONSE_SHA256"
    seal = json.loads(SEAL.read_text())
    assert seal["status"] == "SEALED"
    assert seal["sealed_branch"] == "agent/pass12-migration-plan-safe-closure-v1"
    assert seal["manifest_sha256"] == sha(MANIFEST)
    assert seal["manifest_bytes"] == len(MANIFEST.read_bytes())
    assert seal["runtime_source_set_sha256"] == manifest["runtime_source_set_sha256"]
    anchor = re.search(
        r"const MANIFEST_SHA256='([0-9a-f]{64})';", BOOTSTRAP.read_text()
    )
    assert anchor and anchor.group(1) == sha(MANIFEST)

    closure = reports[-1]
    assert set(closure["scope"]["changed_paths"]) == EXPECTED
    assert set(closure["scope"]["implementation_paths"]) == IMPLEMENTATION
    assert closure["pass12_result"] == "PASS_BOUNDED"
    assert closure["closure"]["completed_units"] == 8
    assert closure["closure"]["deterministic_assertions"] == 389
    assert closure["closure"]["deterministic_assertions_failed"] == 0
    assert closure["closure"]["production_gate"] == "INACTIVE"
    assert closure["closure"]["production_migration_status"] == "BLOCKED_AUTHORITY"
    assert closure["safe_blocked_packet"]["roadmap_disposition"].startswith("Pass 12 closes")
    assert all(closure["exit_criteria"].values())
    assert closure["next_step"]["id"] == "P13-U1"
    assert closure["authority"]["production_migration_authorized"] is False
    assert closure["authority"]["persisted_user_data_change_authorized"] is False
    assert closure["authority"]["formal_proof_authorization_consumed"] is False
    assert closure["no_retry_gates"]["consumed_failed_formal_proof_pr"] == 122
    assert closure["no_retry_gates"]["retry_authorized"] is False

    binding = closure["no_blind_flying_gate"]
    assert binding["ci_lane"] == "deterministic_integration"
    assert binding["diagnostic_matrix_update"]["status"] == "ADDED"
    assert len(binding["diagnostic_evidence_routes"]) == 8
    assert binding["fault_injection"]["status"] == "COVERED"
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    gate_result = json.loads(
        output("python3", PERMANENT_GATE.relative_to(ROOT).as_posix(), "--base", BASE)
    )
    assert gate_result["status"] == "PASS", gate_result
    assert gate_result["unit_id"] == "P12-U8"
    assert gate_result["summary"]["runtime_paths"] == 2
    assert gate_result["summary"]["changed_paths"] == 25
    assert gate_result["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for token in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete Pass 12 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
        "PRODUCTION_GATE_INACTIVE",
    ):
        assert token in workflow, token
    assert workflow.index("Upload complete Pass 12 evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    print(
        "PASS: exact 25-path Pass 12 migration-plan bounded safe closure verified "
        "(389/389, two regressions green, A003 exact source identities, "
        "inactive gate, permanent gate PASS, "
        "production migration BLOCKED_AUTHORITY, P13-U1 ready)"
    )


if __name__ == "__main__":
    main()
