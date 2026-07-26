#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "4ed25e626ff36a6ef795a26a001cd44a920c2329"
REPORT = ROOT / "audit/pass7/pass7-section-owner-unit5-isolation-restart-denial-proof-v1.json"
RECEIPT = ROOT / "audit/pass7/receipts/RECEIPT_P7_U5_OWNER_ISOLATION_RESTART_DENIAL_20260726T171000Z_001.json"
RUNTIME = ROOT / "pmp-section-owner-mount-integration-v1.js"
MANIFEST = ROOT / "pmp-runtime-integrity-manifest-v1.json"
SEAL = ROOT / "audit/a003-manifest-seal.json"
BOOTSTRAP = ROOT / "pmp-app-current.html"
GENERATOR = ROOT / "tools/generate_pass7_unit5_integrity_updates_v1.py"
TEST = ROOT / "tools/test_pass7_unit5_owner_isolation_restart_denial_v1.js"
WORKFLOW = ROOT / ".github/workflows/pass7-unit5-owner-isolation-restart-denial-proof-v1.yml"
UNIT4_WORKFLOW = ROOT / ".github/workflows/pass7-unit4-owner-mount-diagnostics-integration-v1.yml"
GATE_RUNNER = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
EXPECTED = {
    ".github/workflows/pass7-unit4-owner-mount-diagnostics-integration-v1.yml",
    ".github/workflows/pass7-unit5-owner-isolation-restart-denial-proof-v1.yml",
    "audit/a003-manifest-seal.json",
    "audit/pass7/pass7-section-owner-unit5-isolation-restart-denial-proof-v1.json",
    "audit/pass7/receipts/RECEIPT_P7_U5_OWNER_ISOLATION_RESTART_DENIAL_20260726T171000Z_001.json",
    "pmp-app-current.html",
    "pmp-runtime-integrity-manifest-v1.json",
    "pmp-section-owner-mount-integration-v1.js",
    "tools/generate_pass7_unit5_integrity_updates_v1.py",
    "tools/test_pass7_unit5_owner_isolation_restart_denial_v1.js",
    "tools/verify_pass7_unit5_owner_isolation_restart_denial_v1.py",
}
IMPLEMENTATION = {
    "pmp-app-current.html",
    "pmp-section-owner-mount-integration-v1.js",
}
SOURCE_INPUTS = {
    "unit2_capability_contract_sha256": ROOT
    / "audit/pass7/pass7-section-owner-unit2-capability-contract-v1.json",
    "unit3_registration_events_sha256": ROOT
    / "audit/pass7/pass7-section-owner-unit3-registration-events-v1.json",
    "unit4_integration_sha256": ROOT
    / "audit/pass7/pass7-section-owner-unit4-mount-diagnostics-integration-v1.json",
    "unit4_compatibility_workflow_sha256": UNIT4_WORKFLOW,
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
    assert report["unit_id"] == "P7-U5"
    assert report["status"] == "OWNER_ISOLATION_RESTART_DENIAL_PROVEN"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert set(report["scope"]["implementation_paths"]) == IMPLEMENTATION
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["status"] == report["status"]
    for key, path in SOURCE_INPUTS.items():
        assert report["inputs"][key] == sha(path), (key, report["inputs"][key], sha(path))

    hardening = report["hardening"]
    assert hardening["runtime_sha256"] == sha(RUNTIME)
    assert hardening["runtime_version"] == "1.0.0"
    assert hardening["capability_before"] == "P7U3_PREFIX_ONLY"
    assert hardening["capability_after"] == "EXACT_CAPABILITY_ID_FOR_EVENT_OWNER"
    assert hardening["cross_owner_capability_result"] == "REJECTED_REGISTRATION_AUTHORITY"
    assert hardening["restart_api"] == "restore"
    assert hardening["restart_policy"] == "ATOMIC_REPLAY_ONLY_VALIDATED_CHAINED_JOURNAL"
    assert hardening["partial_restart_state_exposed"] is False
    assert hardening["replay_operation_identities_preserved"] is True
    assert hardening["appearance_grants_authority"] is False

    node = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"proof \((\d+)/(\d+)\)", node)
    assert match and match.group(1) == match.group(2)
    assertions = int(match.group(1))
    assert assertions == report["verification"]["assertions_passed"] == 218
    regression = output(
        "node", "tools/test_pass7_unit4_owner_mount_diagnostics_integration_v1.js"
    )
    assert "(137/137)" in regression

    runtime_source = RUNTIME.read_text()
    assert "authority.capability_id!==ownerCapability(event.owner_id)" in runtime_source
    assert "authority.capability_id.indexOf('cap:p7u3:')!==0" not in runtime_source
    assert "function restore(mountRuntime,journal)" in runtime_source
    assert "RESTART_REJECTED_MALFORMED_JOURNAL" in runtime_source
    assert "RESTART_REJECTED_JOURNAL_EVENT" in runtime_source
    assert "RESTART_REPLAY_ACCEPTED" in runtime_source
    for forbidden in (
        "localStorage",
        "sessionStorage",
        "indexedDB",
        "document.",
        "fetch(",
        "XMLHttpRequest",
        "WebSocket",
        "location.",
        ".src=",
        "setTimeout(",
        "setInterval(",
    ):
        assert forbidden not in runtime_source, forbidden

    integrity = report["runtime_integrity"]
    manifest = json.loads(MANIFEST.read_text())
    records = {row["path"]: row for row in manifest["records"]}
    assert len(records) == manifest["counts"]["runtime_records"] == 707
    assert records[RUNTIME.name]["sha256_hex"] == sha(RUNTIME)
    assert sha(MANIFEST) == integrity["manifest_sha256"]
    assert manifest["runtime_source_set_sha256"] == integrity["runtime_source_set_sha256"]
    seal = json.loads(SEAL.read_text())
    assert sha(SEAL) == integrity["seal_sha256"]
    assert seal["manifest_sha256"] == sha(MANIFEST)
    assert seal["runtime_source_set_sha256"] == manifest["runtime_source_set_sha256"]
    assert seal["sealed_branch"] == report["branch"]
    assert "P7-U5" in seal["pass7_context"]
    bootstrap = re.search(
        r"const MANIFEST_SHA256='([0-9a-f]{64})';", BOOTSTRAP.read_text()
    )
    assert bootstrap and bootstrap.group(1) == sha(MANIFEST)
    assert sha(BOOTSTRAP) == integrity["bootstrap_sha256"]

    matrix = report["proof_matrix"]
    assert len(matrix["invariants"]) == 6
    assert matrix["known_owner_positive_cases"] == 8
    assert matrix["cross_section_denials"] == 8
    assert matrix["cross_owner_capability_denials"] == 8
    assert matrix["stale_conflict_denials"] == 6
    assert matrix["assertions"] == 218
    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "deterministic_integration"
    assert binding["diagnostic_matrix_update"]["status"] == "ADDED"
    assert binding["diagnostic_matrix_update"]["applicable_matrix"] == REPORT.relative_to(
        ROOT
    ).as_posix()
    assert binding["fault_injection"]["status"] == "COVERED"
    assert len(binding["fault_injection"]["cases"]) == 24
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    gate = json.loads(output("python3", str(GATE_RUNNER.relative_to(ROOT)), "--base", BASE))
    assert gate["status"] == "PASS"
    assert gate["unit_id"] == "P7-U5"
    assert gate["gate_records"] == 1
    assert gate["summary"]["runtime_paths"] == 2
    assert gate["errors"] == []

    unit4_workflow = UNIT4_WORKFLOW.read_text()
    assert BASE not in unit4_workflow
    assert "3b54adf01a6dd39b16f5967b65069b295068524c" in unit4_workflow
    assert "immutable exact-scope verifier skipped" in unit4_workflow
    assert "tools/test_pass7_unit4_owner_mount_diagnostics_integration_v1.js" in unit4_workflow

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for required in (
        "if: always()",
        "actions/upload-artifact@v4",
        "Upload complete P7-U5 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert required in workflow
    assert workflow.index("Upload complete P7-U5 evidence") < workflow.index(
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
    assert report["next_step"]["id"] == "P7-U6"
    assert report["next_step"]["requires_user_app_check"] is False
    assert receipt["next_safe_move"]["step_id"] == "P7-U6"
    print(
        "PASS: exact eleven-file P7-U5 owner isolation, restart, growth, "
        f"and denial hardening verified ({assertions}/{assertions}, gate PASS)"
    )


if __name__ == "__main__":
    main()
