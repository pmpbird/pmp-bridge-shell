#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "1c2ae85266e6ded5f62e4e45e956c5b3fb026d54"
REPORT = ROOT / "audit/pass9/pass9-bank-continuous-run-unit3-owner-integration-v1.json"
RECEIPT = (
    ROOT
    / "audit/pass9/receipts/RECEIPT_P9_U3_BANK_CONTINUOUS_RUN_OWNER_INTEGRATION_20260726T200000Z_001.json"
)
WORKFLOW = ROOT / ".github/workflows/pass9-unit3-bank-continuous-run-owner-integration-v1.yml"
MANIFEST = ROOT / "pmp-runtime-integrity-manifest-v1.json"
SEAL = ROOT / "audit/a003-manifest-seal.json"
BOOTSTRAP = ROOT / "pmp-app-current.html"
INNER = ROOT / "pmp-current-inner-cleanbug-rgcontrols-v23.html"
BOUNDARY = ROOT / "pmp-bank-continuous-run-owner-boundary-v1.js"
STATE = ROOT / "pmp-continuous-run-state-bank-v1.js"
ROUTER = ROOT / "pmp-master-bank-inventory-router-v1.js"
MASTER = ROOT / "pmp-master-bank-tab-v1.js"
RUN_OWNER = ROOT / "pmp-bank-screen-owner-v1.js"
BRIDGE = ROOT / "pmp-bank-owner-dependency-bridge-v1.js"
LOADER = ROOT / "pmp-continuous-run-bank-order-frame-loader-v1.js"
HELPER_OWNER = ROOT / "pmp-helper-owner-integration-v1.js"
CONNECTION_DELETE = ROOT / "pmp-connections-bank-packet-delete-v1.js"
DIAGNOSTIC = ROOT / "pmp-bank-continuous-run-owner-split-diagnostic-v1.js"
MODE_SHIM = ROOT / "pmp-bank-mode1-hide-unchecked-v1.js"
CLEANER_SHIM = ROOT / "pmp-bank-scoped-test-data-cleaner-v1.js"
GENERATOR = ROOT / "tools/generate_pass9_unit3_integrity_updates_v1.py"
TEST = ROOT / "tools/test_pass9_unit3_bank_continuous_run_owner_integration_v1.js"
GATE_RUNNER = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"

EXPECTED = {
    ".github/workflows/pass9-unit3-bank-continuous-run-owner-integration-v1.yml",
    "audit/a003-manifest-seal.json",
    "audit/pass9/pass9-bank-continuous-run-unit3-owner-integration-v1.json",
    "audit/pass9/receipts/RECEIPT_P9_U3_BANK_CONTINUOUS_RUN_OWNER_INTEGRATION_20260726T200000Z_001.json",
    "pmp-app-current.html",
    "pmp-bank-continuous-run-owner-boundary-v1.js",
    "pmp-bank-continuous-run-owner-split-diagnostic-v1.js",
    "pmp-bank-mode1-hide-unchecked-v1.js",
    "pmp-bank-owner-dependency-bridge-v1.js",
    "pmp-bank-scoped-test-data-cleaner-v1.js",
    "pmp-bank-screen-owner-v1.js",
    "pmp-connections-bank-packet-delete-v1.js",
    "pmp-continuous-run-bank-order-frame-loader-v1.js",
    "pmp-continuous-run-state-bank-v1.js",
    "pmp-current-inner-cleanbug-rgcontrols-v23.html",
    "pmp-helper-owner-integration-v1.js",
    "pmp-master-bank-inventory-router-v1.js",
    "pmp-master-bank-tab-v1.js",
    "pmp-runtime-integrity-manifest-v1.json",
    "tools/generate_pass9_unit3_integrity_updates_v1.py",
    "tools/test_pass9_unit3_bank_continuous_run_owner_integration_v1.js",
    "tools/verify_pass9_unit3_bank_continuous_run_owner_integration_v1.py",
}
IMPLEMENTATION = {
    "pmp-app-current.html",
    "pmp-bank-continuous-run-owner-boundary-v1.js",
    "pmp-bank-continuous-run-owner-split-diagnostic-v1.js",
    "pmp-bank-mode1-hide-unchecked-v1.js",
    "pmp-bank-owner-dependency-bridge-v1.js",
    "pmp-bank-scoped-test-data-cleaner-v1.js",
    "pmp-bank-screen-owner-v1.js",
    "pmp-connections-bank-packet-delete-v1.js",
    "pmp-continuous-run-bank-order-frame-loader-v1.js",
    "pmp-continuous-run-state-bank-v1.js",
    "pmp-current-inner-cleanbug-rgcontrols-v23.html",
    "pmp-helper-owner-integration-v1.js",
    "pmp-master-bank-inventory-router-v1.js",
    "pmp-master-bank-tab-v1.js",
}
MANIFEST_RUNTIME = IMPLEMENTATION - {"pmp-app-current.html"}
SOURCE_INPUTS = {
    "unit1_inventory_sha256": ROOT
    / "audit/pass9/pass9-bank-continuous-run-unit1-inventory-v1.json",
    "unit2_owner_contract_sha256": ROOT
    / "audit/pass9/pass9-bank-continuous-run-unit2-owner-contract-v1.json",
    "legacy_inner_v4_sha256": ROOT
    / "pmp-current-inner-cleanbug-rgcontrols-v4.html",
    "generator_sha256": GENERATOR,
    "test_sha256": TEST,
}
INTEGRATION_HASHES = {
    "boundary_sha256": BOUNDARY,
    "continuous_run_state_sha256": STATE,
    "bank_router_sha256": ROUTER,
    "bank_shell_owner_sha256": MASTER,
    "continuous_run_surface_owner_sha256": RUN_OWNER,
    "helper_owner_integration_sha256": HELPER_OWNER,
    "inner_sha256": INNER,
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
    assert report["unit_id"] == "P9-U3"
    assert report["status"] == "BANK_CONTINUOUS_RUN_OWNER_INTEGRATION_PROVEN"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert set(report["scope"]["implementation_paths"]) == IMPLEMENTATION
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["status"] == report["status"]
    for key, path in SOURCE_INPUTS.items():
        assert report["inputs"][key] == sha(path), (
            key,
            report["inputs"][key],
            sha(path),
        )

    integration = report["integration"]
    assert integration["model"] == (
        "SEPARATE_OWNERS_ATOMIC_BANK_COMMIT_EVENT_DRIVEN_RENDER"
    )
    assert integration["contract_version"] == (
        "PMP_BANK_CONTINUOUS_RUN_OWNER_CONTRACT_V1"
    )
    assert integration["receipt_version"] == (
        "PMP_BANK_CONTINUOUS_RUN_OWNER_RECEIPT_V1"
    )
    assert integration["bank_owner"] == "bank_screen_owner"
    assert integration["continuous_run_owner"] == "continuous_run_level_owner"
    assert integration["bank_owner"] != integration["continuous_run_owner"]
    assert integration["request_fields"] == 13
    assert integration["receipt_fields"] == 15
    assert integration["receipt_algorithm"] == "SHA-256_CHAINED"
    assert integration["existing_persisted_keys_preserved"] == [
        "pmp_continuous_run_state_bank_v1",
        "pmp_continuous_run_state_receipts_v1",
        "pmp_continuous_run_state_manifest_v1",
    ]
    for key in (
        "boundary_and_state_load_storage_reads",
        "boundary_and_state_load_storage_writes",
        "boundary_and_state_load_storage_deletes",
        "copied_mutable_cross_frame_apis",
        "recurring_bank_painters",
        "duplicate_active_owner_injections",
    ):
        assert integration[key] == 0, key
    assert integration["boundary_and_state_load_persisted_user_data_changed"] is False
    assert integration["atomic_write_rollback"] is True
    assert integration["unrelated_storage_preserved"] is True
    assert integration["expired_requests_denied"] is True
    assert integration["cancellation_epoch"] == "MONOTONIC_NO_GAPS"
    assert integration["bank_detail_open_is_read_only"] is True
    assert integration["storage_migration"] == "FORBIDDEN"
    assert integration["delete_or_clear_default"] == "DENY"
    assert integration["explicit_delete_confirmation_required"] is True
    assert integration["render_mode"] == "EVENT_DRIVEN_NEW_DOCUMENT_ONCE"
    for key, path in INTEGRATION_HASHES.items():
        assert integration[key] == sha(path), (key, integration[key], sha(path))

    test_output = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"integration \((\d+)/(\d+)\)", test_output)
    assert match and match.group(1) == match.group(2)
    assertions = int(match.group(1))
    assert assertions == report["verification"]["assertions_passed"] == 234
    assert report["verification"]["assertions_total"] == assertions
    assert report["verification"]["assertions_failed"] == 0
    assert receipt["coverage"]["assertions"] == assertions

    boundary_source = BOUNDARY.read_text()
    state_source = STATE.read_text()
    router_source = ROUTER.read_text()
    master_source = MASTER.read_text()
    run_owner_source = RUN_OWNER.read_text()
    bridge_source = BRIDGE.read_text()
    loader_source = LOADER.read_text()
    mode_source = MODE_SHIM.read_text()
    cleaner_source = CLEANER_SHIM.read_text()
    diagnostic_source = DIAGNOSTIC.read_text()
    connection_source = CONNECTION_DELETE.read_text()

    assert "version:VERSION" in boundary_source
    assert "resourceVersion,requestFor" in boundary_source
    assert "SHA-256_CHAINED" in boundary_source
    assert "DENIED_ATOMIC_WRITE_FAILED" in boundary_source
    assert "storage_migration:'FORBIDDEN'" in boundary_source
    assert "localStorage.removeItem" not in boundary_source
    assert "Math.imul" not in state_source
    assert "hash_algorithm:'SHA-256'" in state_source
    assert "READ_PATH_CANNOT_WRITE_MANIFEST" in state_source
    assert "CLEAR_DENIED_BY_DEFAULT" in state_source
    assert "localStorage.removeItem" not in state_source
    assert "input.user_confirmed!==true" in router_source
    assert "DELETE_DENIED_BY_DEFAULT" in router_source
    assert "The active tab or active system creates ownership" not in router_source
    assert "setInterval(" not in master_source
    assert ".recordWrite(" not in master_source
    assert "setInterval(" not in run_owner_source
    assert "setInterval(" not in bridge_source
    assert "setTimeout(" not in bridge_source
    assert "w[name]=api" not in bridge_source
    assert "mutable_apis_copied:0" in bridge_source
    assert "setInterval(" not in loader_source
    assert "EVENT_DRIVEN_NEW_DOCUMENT_ONCE" in loader_source
    assert "bank_owner_duplicate_injection_attempted:false" in loader_source
    assert "document." not in mode_source
    assert "localStorage" not in mode_source
    assert "PASSIVE_COMPATIBILITY_HELD" in mode_source
    assert "document." not in cleaner_source
    assert "localStorage" not in cleaner_source
    assert "DELETE_DENIED_BY_DEFAULT" in cleaner_source
    assert "boundarySnapshot" in diagnostic_source
    assert "setTimeout(evaluate" not in diagnostic_source
    assert (
        "capability:'manual:bank_screen_owner:delete_record:connections'"
        in connection_source
    )
    assert "connections_deposits_after_delete:deposits" in connection_source
    assert "localStorage.setItem" not in connection_source
    assert "setInterval(" not in connection_source
    assert (
        "capability:'manual:bank_screen_owner:delete_record:project_registry'"
        in run_owner_source
    )
    assert "window.confirm('Delete this Bank project?" in run_owner_source

    inner = INNER.read_text()
    boundary_pos = inner.index(
        "pmp-bank-continuous-run-owner-boundary-v1.js?fresh="
    )
    state_pos = inner.index("pmp-continuous-run-state-bank-v1.js?fresh=")
    router_pos = inner.index("pmp-master-bank-inventory-router-v1.js?fresh=")
    master_pos = inner.index("pmp-master-bank-tab-v1.js?fresh=")
    run_owner_pos = inner.index("pmp-bank-screen-owner-v1.js?fresh=")
    assert boundary_pos < state_pos < router_pos < master_pos < run_owner_pos
    assert "pmp-bank-mode1-hide-unchecked-v1.js" not in inner
    assert "pmp-bank-scoped-test-data-cleaner-v1.js" not in inner

    integrity = report["runtime_integrity"]
    manifest = json.loads(MANIFEST.read_text())
    records = {row["path"]: row for row in manifest["records"]}
    assert len(records) == manifest["counts"]["runtime_records"] == 710
    for relative in MANIFEST_RUNTIME:
        assert records[relative]["sha256_hex"] == sha(ROOT / relative), relative
    assert sha(MANIFEST) == integrity["manifest_sha256"]
    assert (
        manifest["runtime_source_set_sha256"]
        == integrity["runtime_source_set_sha256"]
    )
    seal = json.loads(SEAL.read_text())
    assert sha(SEAL) == integrity["seal_sha256"]
    assert seal["manifest_sha256"] == sha(MANIFEST)
    assert (
        seal["runtime_source_set_sha256"]
        == manifest["runtime_source_set_sha256"]
    )
    assert seal["sealed_branch"] == report["branch"]
    assert "P9-U3" in seal["pass9_context"]
    bootstrap = re.search(
        r"const MANIFEST_SHA256='([0-9a-f]{64})';", BOOTSTRAP.read_text()
    )
    assert bootstrap and bootstrap.group(1) == sha(MANIFEST)
    assert sha(BOOTSTRAP) == integrity["bootstrap_sha256"]

    matrix = report["diagnostic_and_proof_matrix"]
    assert len(matrix["invariants"]) == 6
    assert matrix["assertions"] == assertions
    assert matrix["fault_cases"] == 16
    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "deterministic_integration"
    assert binding["diagnostic_matrix_update"]["status"] == "ADDED"
    assert (
        binding["diagnostic_matrix_update"]["applicable_matrix"]
        == REPORT.relative_to(ROOT).as_posix()
    )
    assert binding["fault_injection"]["status"] == "COVERED"
    assert len(binding["fault_injection"]["cases"]) == 16
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
    assert gate["status"] == "PASS", gate
    assert gate["unit_id"] == "P9-U3"
    assert gate["gate_records"] == 1
    assert gate["summary"]["runtime_paths"] == 14
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
        "Upload complete P9-U3 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert required in workflow
    assert workflow.index("Upload complete P9-U3 evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )

    effects = report["effects"]
    for key in (
        "production_files_changed",
        "runtime_integrity_changed",
        "repairs",
        "production_behavior_activated",
    ):
        assert effects[key] is True, key
        assert receipt["effects"][key] is True, key
    for key, value in effects.items():
        if key not in {
            "production_files_changed",
            "runtime_integrity_changed",
            "repairs",
            "production_behavior_activated",
        }:
            assert value is False, (key, value)
    assert effects["persisted_user_data_changed"] is False
    assert effects["storage_migration_performed"] is False
    assert report["authority"]["special_authority_consumed"] is False
    assert report["next_step"]["id"] == "P9-U4"
    assert report["next_step"]["requires_user_app_check"] is False
    assert report["next_step"]["requires_new_explicit_authority"] is False
    assert receipt["next_safe_move"]["step_id"] == "P9-U4"
    print(
        "PASS: exact twenty-two-file P9-U3 Bank/Continuous Run owner integration "
        f"verified ({assertions}/{assertions}, gate PASS)"
    )


if __name__ == "__main__":
    main()
