#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "b65f186429d155172fc59d62440cc78d9960823f"
WORKFLOW = ROOT / ".github/workflows/pass11-safety-no-deletion-v1.yml"
POLICY = ROOT / "pmp-safety-no-deletion-policy-v1.json"
GUARD = ROOT / "pmp-safety-no-deletion-guard-v1.js"
ROUTER = ROOT / "pmp-master-bank-inventory-router-v1.js"
CONNECTIONS = ROOT / "pmp-connections-bank-packet-delete-v1.js"
INNER = ROOT / "pmp-current-inner-cleanbug-rgcontrols-v23.html"
MANIFEST = ROOT / "pmp-runtime-integrity-manifest-v1.json"
SEAL = ROOT / "audit/a003-manifest-seal.json"
BOOTSTRAP = ROOT / "pmp-app-current.html"
GENERATOR = ROOT / "tools/generate_pass11_safety_no_deletion_integrity_updates_v1.py"
TEST = ROOT / "tools/test_pass11_safety_no_deletion_v1.js"
GATE = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"

REPORTS = [
    ROOT / "audit/pass11/pass11-unit1-safety-baseline-contract-v1.json",
    ROOT / "audit/pass11/pass11-unit2-no-deletion-archive-contract-v1.json",
    ROOT / "audit/pass11/pass11-unit3-safe-writer-transaction-recovery-v1.json",
    ROOT / "audit/pass11/pass11-unit4-adversarial-fault-proof-v1.json",
    ROOT / "audit/pass11/pass11-unit5-disposable-preservation-recovery-drill-v1.json",
    ROOT / "audit/pass11/pass11-unit6-closure-certification-v1.json",
]
RECEIPTS = [
    ROOT / "audit/pass11/receipts/RECEIPT_P11_U1_SAFETY_BASELINE_20260727T064300Z_001.json",
    ROOT / "audit/pass11/receipts/RECEIPT_P11_U2_NO_DELETION_ARCHIVE_20260727T064400Z_001.json",
    ROOT / "audit/pass11/receipts/RECEIPT_P11_U3_SAFE_WRITER_TRANSACTION_20260727T064500Z_001.json",
    ROOT / "audit/pass11/receipts/RECEIPT_P11_U4_ADVERSARIAL_FAULT_PROOF_20260727T064600Z_001.json",
    ROOT / "audit/pass11/receipts/RECEIPT_P11_U5_PRESERVATION_RECOVERY_DRILL_20260727T064700Z_001.json",
    ROOT / "audit/pass11/receipts/RECEIPT_P11_U6_PASS11_COMPLETE_20260727T064800Z_001.json",
]
EXPECTED = {
    ".github/workflows/pass11-safety-no-deletion-v1.yml",
    "audit/a003-manifest-seal.json",
    "audit/pass11/pass11-unit1-safety-baseline-contract-v1.json",
    "audit/pass11/pass11-unit2-no-deletion-archive-contract-v1.json",
    "audit/pass11/pass11-unit3-safe-writer-transaction-recovery-v1.json",
    "audit/pass11/pass11-unit4-adversarial-fault-proof-v1.json",
    "audit/pass11/pass11-unit5-disposable-preservation-recovery-drill-v1.json",
    "audit/pass11/pass11-unit6-closure-certification-v1.json",
    "audit/pass11/receipts/RECEIPT_P11_U1_SAFETY_BASELINE_20260727T064300Z_001.json",
    "audit/pass11/receipts/RECEIPT_P11_U2_NO_DELETION_ARCHIVE_20260727T064400Z_001.json",
    "audit/pass11/receipts/RECEIPT_P11_U3_SAFE_WRITER_TRANSACTION_20260727T064500Z_001.json",
    "audit/pass11/receipts/RECEIPT_P11_U4_ADVERSARIAL_FAULT_PROOF_20260727T064600Z_001.json",
    "audit/pass11/receipts/RECEIPT_P11_U5_PRESERVATION_RECOVERY_DRILL_20260727T064700Z_001.json",
    "audit/pass11/receipts/RECEIPT_P11_U6_PASS11_COMPLETE_20260727T064800Z_001.json",
    "pmp-app-current.html",
    "pmp-connections-bank-packet-delete-v1.js",
    "pmp-current-inner-cleanbug-rgcontrols-v23.html",
    "pmp-master-bank-inventory-router-v1.js",
    "pmp-runtime-integrity-manifest-v1.json",
    "pmp-safety-no-deletion-guard-v1.js",
    "pmp-safety-no-deletion-policy-v1.json",
    "tools/generate_pass11_safety_no_deletion_integrity_updates_v1.py",
    "tools/test_pass11_safety_no_deletion_v1.js",
    "tools/verify_pass11_safety_no_deletion_v1.py",
}
IMPLEMENTATION = {
    "pmp-app-current.html",
    "pmp-connections-bank-packet-delete-v1.js",
    "pmp-current-inner-cleanbug-rgcontrols-v23.html",
    "pmp-master-bank-inventory-router-v1.js",
    "pmp-safety-no-deletion-guard-v1.js",
}
STATUSES = [
    "SAFETY_BASELINE_CONSOLIDATED",
    "NO_DELETION_ARCHIVE_QUARANTINE_CONTRACT_ENFORCED",
    "SAFE_WRITER_TRANSACTION_ROLLBACK_RECOVERY_RULES_ENFORCED",
    "ADVERSARIAL_FAULT_PROOF_GREEN",
    "DISPOSABLE_PERSISTED_DATA_PRESERVATION_RECOVERY_DRILL_GREEN",
    "PASS11_SAFETY_NO_DELETION_COMPLETE",
]
NEXT = ["P11-U2", "P11-U3", "P11-U4", "P11-U5", "P11-U6", "P12-U1"]
REGRESSIONS = [
    ("tools/test_pass9_unit3_bank_continuous_run_owner_integration_v1.js", 234),
    ("tools/test_pass10_unit3_bank_readonly_projection_v1.js", 125),
    ("tools/test_pass10_unit4_bank_owner_projection_refresh_v1.js", 121),
    ("tools/test_pass10_unit7_bank_level_owner_stability_repair_v1.js", 106),
    ("tools/test_pass10_unit7_legacy_level_alias_single_stack_repair_v1.js", 151),
    ("tools/test_pass10_unit7_single_card_presentation_v1.js", 478),
    ("tools/test_pass10_unit7_uniform_title_weight_v1.js", 86),
]
GENERATED = [INNER, MANIFEST, SEAL, BOOTSTRAP]
RUNTIME_RECORDS = [
    GUARD,
    ROUTER,
    CONNECTIONS,
    INNER,
]


def output(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def sha(item: Path) -> str:
    return hashlib.sha256(item.read_bytes()).hexdigest()


def changed(base: str) -> set[str]:
    rows: set[str] = set()
    for command in (
        ("git", "diff", "--name-only", f"{base}...HEAD"),
        ("git", "diff", "--name-only", base),
        ("git", "ls-files", "--others", "--exclude-standard"),
    ):
        rows.update(filter(None, output(*command).splitlines()))
    return rows


def workflow_paths(text: str) -> set[str]:
    match = re.search(
        r"(?m)^    paths:\n(?P<rows>(?:      - [^\n]+\n)+)", text
    )
    assert match
    return {
        row.strip()[2:].strip().strip("'\"")
        for row in match.group("rows").splitlines()
    }


def assertion_total(text: str) -> int:
    match = re.search(r"\((\d+)/(\d+)\)", text)
    assert match and match.group(1) == match.group(2), text
    return int(match.group(1))


def main() -> None:
    base = sys.argv[1] if len(sys.argv) > 1 else BASE
    assert base == BASE
    assert changed(base) == EXPECTED, (sorted(changed(base)), sorted(EXPECTED))

    reports = [json.loads(item.read_text()) for item in REPORTS]
    receipts = [json.loads(item.read_text()) for item in RECEIPTS]
    for index, (report, receipt) in enumerate(zip(reports, receipts), 1):
        assert report["base_main_commit"] == BASE
        assert report["unit_id"] == f"P11-U{index}"
        assert report["status"] == STATUSES[index - 1]
        assert report["next_step"]["id"] == NEXT[index - 1]
        assert receipt["base_main_commit"] == BASE
        assert receipt["unit"] == f"P11-U{index}"
        assert receipt["status"] == report["status"]
        assert receipt["evidence"] == REPORTS[index - 1].relative_to(ROOT).as_posix()
        assert receipt["next_safe_move"]["step_id"] == NEXT[index - 1]
        assert report["effects"]["persisted_user_data_changed"] is False
        assert report["effects"]["formal_proof_performed"] is False
        assert report["effects"]["special_authority_consumed"] is False
        assert receipt["effects"]["persisted_user_data_changed"] is False
        assert receipt["effects"]["formal_proof_performed"] is False
        assert receipt["effects"]["special_authority_consumed"] is False

    closure = reports[-1]
    assert set(closure["scope"]["changed_paths"]) == EXPECTED
    assert set(closure["scope"]["implementation_paths"]) == IMPLEMENTATION
    assert closure["pass11_result"] == "PASS"
    assert closure["closure"]["deterministic_assertions"] == 186
    assert closure["closure"]["deterministic_assertions_failed"] == 0
    assert closure["closure"]["default_delete"] == "DENY"
    assert closure["closure"]["active_connections_action"] == "RECOVERABLE_ARCHIVE"
    assert closure["closure"]["physical_indexeddb_delete_paths"] == 0
    assert closure["closure"]["physical_localstorage_delete_paths"] == 0
    assert closure["pass12_boundary"]["entry_unit"] == "P12-U1"
    assert closure["pass12_boundary"]["production_activation_allowed"] is False
    assert closure["pass12_boundary"]["persisted_user_data_change_allowed"] is False
    assert closure["pass12_boundary"]["production_migration_allowed"] is False
    assert all(closure["exit_criteria"].values())

    policy = json.loads(POLICY.read_text())
    assert policy["default_decision"] == "DENY"
    assert len(policy["protected_assets"]) == 10
    assert policy["operation_classes"]["ARCHIVE"]["physical_delete_allowed"] is False
    assert policy["operation_classes"]["MIGRATION"]["default"] == "INACTIVE_GATE"
    assert policy["operation_classes"]["DELETE_EXCEPTION"]["wildcards_allowed"] is False
    assert policy["operation_classes"]["DELETE_EXCEPTION"]["automatic_retry_allowed"] is False
    assert policy["safe_writer_rules"]["partial_write"] == "ROLLBACK_EXACT_BYTES"
    assert policy["active_connections_bank"]["physical_indexeddb_delete"] is False
    assert policy["formal_proof"]["performed"] is False
    assert policy["formal_proof"]["authorization_consumed"] is False

    guard_text = GUARD.read_text()
    for token in (
        "authorizeArchive",
        "authorizeDeleteException",
        "planTransaction",
        "PMP_EXACT_DELETE_EXCEPTION_AUTHORITY_V1",
        "DENIED_EXACT_AUTHORITY_REPLAY",
        "ROLLBACK_ON_ANY_FAILURE",
        "wildcards_allowed:false",
        "automatic_retry:false",
    ):
        assert token in guard_text
    router_text = ROUTER.read_text()
    for token in (
        "recordArchive",
        "authorizeDeleteException",
        "archive_record_exact_payload_preserved",
        "deleted_count:0",
        "connections_deposits_after_archive",
    ):
        assert token in router_text

    connections_text = CONNECTIONS.read_text()
    for forbidden in (
        "indexedDB.open",
        "objectStore(",
        ".delete(",
        "localStorage.removeItem",
    ):
        assert forbidden not in connections_text, forbidden
    for required in (
        "Archive Selected Packet",
        "Nothing will be deleted",
        "archived_records",
        "indexeddb_key",
        "physical_payload_deleted:false",
        "recordArchive",
        "delete deposits.records[id]",
    ):
        assert required in connections_text, required

    test_text = output("node", TEST.relative_to(ROOT).as_posix())
    assert assertion_total(test_text) == 186
    for path, expected in REGRESSIONS:
        assert assertion_total(output("node", path)) == expected, path

    before = {item: sha(item) for item in GENERATED}
    assert "PASS:" in output("python3", GENERATOR.relative_to(ROOT).as_posix())
    after = {item: sha(item) for item in GENERATED}
    assert before == after

    manifest = json.loads(MANIFEST.read_text())
    records = {row["path"]: row for row in manifest["records"]}
    for item in RUNTIME_RECORDS:
        relative = item.relative_to(ROOT).as_posix()
        row = records[relative]
        assert row["sha256_hex"] == sha(item), relative
        assert row["bytes"] == len(item.read_bytes()), relative
        assert row["enforcement"] == "SERVICE_WORKER_PRE_RESPONSE_SHA256"
    seal = json.loads(SEAL.read_text())
    assert seal["status"] == "SEALED"
    assert seal["sealed_branch"] == "agent/pass11-safety-no-deletion-complete-v1"
    assert seal["manifest_sha256"] == sha(MANIFEST)
    assert seal["manifest_bytes"] == len(MANIFEST.read_bytes())
    assert seal["runtime_source_set_sha256"] == manifest["runtime_source_set_sha256"]
    anchor = re.search(
        r"const MANIFEST_SHA256='([0-9a-f]{64})';", BOOTSTRAP.read_text()
    )
    assert anchor and anchor.group(1) == sha(MANIFEST)
    inner = INNER.read_text()
    assert inner.count("pmp-safety-no-deletion-guard-v1.js?fresh=") == 1
    assert inner.index("pmp-safety-no-deletion-guard-v1.js") < inner.index(
        "pmp-master-bank-inventory-router-v1.js"
    )
    assert "fresh=pass11-recoverable-archive-20260727A" in inner

    binding = closure["no_blind_flying_gate"]
    assert binding["ci_lane"] == "deterministic_integration"
    assert binding["diagnostic_matrix_update"]["status"] == "ADDED"
    assert len(binding["diagnostic_evidence_routes"]) == 6
    assert binding["fault_injection"]["status"] == "COVERED"
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    gate = json.loads(
        output("python3", GATE.relative_to(ROOT).as_posix(), "--base", BASE)
    )
    assert gate["status"] == "PASS", gate
    assert gate["unit_id"] == "P11-U6"
    assert gate["summary"]["runtime_paths"] == 5
    assert gate["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for token in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete Pass 11 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert token in workflow
    assert workflow.index("Upload complete Pass 11 evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert closure["authority"]["formal_proof_authorization_consumed"] is False
    assert closure["no_retry_gates"]["consumed_failed_formal_proof_pr"] == 122
    assert closure["no_retry_gates"]["retry_authorized"] is False
    print(
        "PASS: exact 24-path Pass 11 safety/no-deletion closure verified "
        "(186/186, seven regressions green, integrity sealed, gate PASS, "
        "P12-U1 ready)"
    )


if __name__ == "__main__":
    main()
