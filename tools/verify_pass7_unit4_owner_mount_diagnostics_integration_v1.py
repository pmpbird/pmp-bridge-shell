#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "3b54adf01a6dd39b16f5967b65069b295068524c"
REPORT = ROOT / "audit/pass7/pass7-section-owner-unit4-mount-diagnostics-integration-v1.json"
RECEIPT = ROOT / "audit/pass7/receipts/RECEIPT_P7_U4_OWNER_MOUNT_DIAGNOSTICS_INTEGRATION_20260726T165000Z_001.json"
RUNTIME = ROOT / "pmp-section-owner-mount-integration-v1.js"
VIEW = ROOT / "pmp-section-owner-diagnostics-view-v1.js"
DIAGNOSTICS = ROOT / "pmp-diagnostics-owner-v1.js"
INNER = ROOT / "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html"
MANIFEST = ROOT / "pmp-runtime-integrity-manifest-v1.json"
SEAL = ROOT / "audit/a003-manifest-seal.json"
BOOTSTRAP = ROOT / "pmp-app-current.html"
GENERATOR = ROOT / "tools/generate_pass7_unit4_integrity_updates_v1.py"
TEST = ROOT / "tools/test_pass7_unit4_owner_mount_diagnostics_integration_v1.js"
WORKFLOW = ROOT / ".github/workflows/pass7-unit4-owner-mount-diagnostics-integration-v1.yml"
GATE_RUNNER = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
EXPECTED = {
    ".github/workflows/pass7-unit4-owner-mount-diagnostics-integration-v1.yml",
    "audit/a003-manifest-seal.json",
    "audit/pass7/pass7-section-owner-unit4-mount-diagnostics-integration-v1.json",
    "audit/pass7/receipts/RECEIPT_P7_U4_OWNER_MOUNT_DIAGNOSTICS_INTEGRATION_20260726T165000Z_001.json",
    "pmp-app-current.html",
    "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html",
    "pmp-diagnostics-owner-v1.js",
    "pmp-runtime-integrity-manifest-v1.json",
    "pmp-section-owner-diagnostics-view-v1.js",
    "pmp-section-owner-mount-integration-v1.js",
    "tools/generate_pass7_unit4_integrity_updates_v1.py",
    "tools/test_pass7_unit4_owner_mount_diagnostics_integration_v1.js",
    "tools/verify_pass7_unit4_owner_mount_diagnostics_integration_v1.py",
}
IMPLEMENTATION = {
    "pmp-app-current.html",
    "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html",
    "pmp-diagnostics-owner-v1.js",
    "pmp-section-owner-diagnostics-view-v1.js",
    "pmp-section-owner-mount-integration-v1.js",
}
SOURCE_INPUTS = {
    "unit2_capability_contract_sha256": ROOT / "audit/pass7/pass7-section-owner-unit2-capability-contract-v1.json",
    "unit3_registration_events_sha256": ROOT / "audit/pass7/pass7-section-owner-unit3-registration-events-v1.json",
    "generator_sha256": GENERATOR,
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
    assert report["base_main_commit"] == BASE
    assert report["unit_id"] == "P7-U4"
    assert report["status"] == "OWNER_MOUNT_DIAGNOSTICS_INTEGRATION_PROVEN"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert set(report["scope"]["implementation_paths"]) == IMPLEMENTATION
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["status"] == report["status"]
    for key, path in SOURCE_INPUTS.items():
        assert report["inputs"][key] == sha(path), (key, report["inputs"][key], sha(path))

    integration = report["integration"]
    assert integration["runtime_sha256"] == sha(RUNTIME)
    assert integration["diagnostics_view_sha256"] == sha(VIEW)
    assert integration["diagnostics_owner_sha256"] == sha(DIAGNOSTICS)
    assert integration["runtime_owner"] == "mount_registry_owner"
    assert integration["runtime_mode"] == "PASSIVE_EXPLICIT_OWNER_EVENTS_ONLY"
    assert integration["known_owners"] == integration["known_sections"] == 8
    assert integration["appearance_grants_authority"] is False
    assert integration["mount_lifecycle_events"] == 0
    assert integration["legacy_atlas_calls"] == 0
    assert integration["shared_operation_identities"] is True
    assert integration["capability_ids_exposed"] is False
    assert integration["raw_authority_payloads_exposed"] is False

    node = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"integration \((\d+)/(\d+)\)", node)
    assert match and match.group(1) == match.group(2)
    assertions = int(match.group(1))
    assert assertions == report["verification"]["assertions_passed"] == 137
    for path in (RUNTIME, VIEW):
        source = path.read_text()
        for forbidden in (
            "localStorage", "sessionStorage", "indexedDB", "document.", "fetch(",
            "XMLHttpRequest", "WebSocket", "location.", ".src=", "setTimeout(", "setInterval(",
        ):
            assert forbidden not in source, (path.name, forbidden)
    view_source = VIEW.read_text()
    assert "applyOwnerEvent" not in view_source
    diagnostics_source = DIAGNOSTICS.read_text()
    assert "readSectionOwners=sectionOwnerView" in diagnostics_source
    assert "renderSectionOwners" in diagnostics_source
    assert "PMPSectionOwnerMountRuntimeV1.applyOwnerEvent" not in diagnostics_source
    inner = INNER.read_text()
    mount_pos = inner.index("pmp-mount-lifecycle-runtime-v1.js?fresh=")
    runtime_pos = inner.index("pmp-section-owner-mount-integration-v1.js?fresh=")
    view_pos = inner.index("pmp-section-owner-diagnostics-view-v1.js?fresh=")
    authority_pos = inner.index("pmp-authority-rules-v1.js?fresh=")
    assert mount_pos < runtime_pos < view_pos < authority_pos

    integrity = report["runtime_integrity"]
    manifest = json.loads(MANIFEST.read_text())
    records = {row["path"]: row for row in manifest["records"]}
    assert len(records) == manifest["counts"]["runtime_records"] == 707
    for path in (RUNTIME, VIEW, DIAGNOSTICS, INNER):
        relative = path.relative_to(ROOT).as_posix()
        assert records[relative]["sha256_hex"] == sha(path), relative
    assert sha(MANIFEST) == integrity["manifest_sha256"]
    assert manifest["runtime_source_set_sha256"] == integrity["runtime_source_set_sha256"]
    seal = json.loads(SEAL.read_text())
    assert sha(SEAL) == integrity["seal_sha256"]
    assert seal["manifest_sha256"] == sha(MANIFEST)
    assert seal["runtime_source_set_sha256"] == manifest["runtime_source_set_sha256"]
    assert seal["sealed_branch"] == report["branch"]
    assert "P7-U4" in seal["pass7_context"]
    bootstrap = re.search(
        r"const MANIFEST_SHA256='([0-9a-f]{64})';", BOOTSTRAP.read_text()
    )
    assert bootstrap and bootstrap.group(1) == sha(MANIFEST)
    assert sha(BOOTSTRAP) == integrity["bootstrap_sha256"]
    assert sha(INNER) == integrity["inner_sha256"]

    matrix = report["diagnostic_and_proof_matrix"]
    assert len(matrix["invariants"]) == 5
    assert matrix["assertions"] == 137
    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "deterministic_integration"
    assert binding["diagnostic_matrix_update"]["status"] == "ADDED"
    assert binding["diagnostic_matrix_update"]["applicable_matrix"] == REPORT.relative_to(ROOT).as_posix()
    assert binding["fault_injection"]["status"] == "COVERED"
    assert len(binding["fault_injection"]["cases"]) == 16
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    gate = json.loads(output("python3", str(GATE_RUNNER.relative_to(ROOT)), "--base", BASE))
    assert gate["status"] == "PASS"
    assert gate["unit_id"] == "P7-U4"
    assert gate["gate_records"] == 1
    assert gate["summary"]["runtime_paths"] == 5
    assert gate["errors"] == []

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for required in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete P7-U4 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert required in workflow
    assert workflow.index("Upload complete P7-U4 evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )
    effects = report["effects"]
    assert effects["production_files_changed"] is True
    assert effects["runtime_integrity_changed"] is True
    for key, value in effects.items():
        if key not in {"production_files_changed", "runtime_integrity_changed"}:
            assert value is False, (key, value)
    assert report["authority"]["special_authority_consumed"] is False
    assert report["next_step"]["id"] == "P7-U5"
    assert report["next_step"]["requires_user_app_check"] is False
    assert receipt["next_safe_move"]["step_id"] == "P7-U5"
    print(
        "PASS: exact thirteen-file P7-U4 bounded owner Mount Registry and "
        f"Diagnostics integration verified ({assertions}/{assertions}, gate PASS)"
    )


if __name__ == "__main__":
    main()
