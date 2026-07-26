#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "3e29393933c2b8ce71cc6f9ddcc70aff96f4416f"
REPORT = ROOT / "audit/pass10/pass10-bank-unit3-readonly-projection-v1.json"
RECEIPT = ROOT / "audit/pass10/receipts/RECEIPT_P10_U3_BANK_READONLY_PROJECTION_20260726T223500Z_001.json"
WORKFLOW = ROOT / ".github/workflows/pass10-unit3-bank-readonly-projection-v1.yml"
CONTRACT = ROOT / "audit/pass10/pass10-bank-unit2-inventory-contract-v1.json"
PROJECTION = ROOT / "pmp-bank-inventory-readonly-projection-v1.js"
MASTER = ROOT / "pmp-master-bank-tab-v1.js"
INNER = ROOT / "pmp-current-inner-cleanbug-rgcontrols-v23.html"
MOUNTS = ROOT / "pmp-mount-registry-v1.js"
MANIFEST = ROOT / "pmp-runtime-integrity-manifest-v1.json"
SEAL = ROOT / "audit/a003-manifest-seal.json"
BOOTSTRAP = ROOT / "pmp-app-current.html"
GENERATOR = ROOT / "tools/generate_pass10_unit3_integrity_updates_v1.py"
TEST = ROOT / "tools/test_pass10_unit3_bank_readonly_projection_v1.js"
GATE = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
EXPECTED = {
    ".github/workflows/pass10-unit3-bank-readonly-projection-v1.yml",
    "audit/a003-manifest-seal.json",
    "audit/pass10/pass10-bank-unit3-readonly-projection-v1.json",
    "audit/pass10/receipts/RECEIPT_P10_U3_BANK_READONLY_PROJECTION_20260726T223500Z_001.json",
    "pmp-app-current.html",
    "pmp-bank-inventory-readonly-projection-v1.js",
    "pmp-current-inner-cleanbug-rgcontrols-v23.html",
    "pmp-master-bank-tab-v1.js",
    "pmp-mount-registry-v1.js",
    "pmp-runtime-integrity-manifest-v1.json",
    "tools/generate_pass10_unit3_integrity_updates_v1.py",
    "tools/test_pass10_unit3_bank_readonly_projection_v1.js",
    "tools/verify_pass10_unit3_bank_readonly_projection_v1.py",
}
IMPLEMENTATION = {
    "pmp-app-current.html",
    "pmp-bank-inventory-readonly-projection-v1.js",
    "pmp-current-inner-cleanbug-rgcontrols-v23.html",
    "pmp-master-bank-tab-v1.js",
    "pmp-mount-registry-v1.js",
}
INPUTS = {
    "unit2_contract_sha256": CONTRACT,
    "projection_sha256": PROJECTION,
    "bank_tab_sha256": MASTER,
    "active_inner_sha256": INNER,
    "mount_registry_sha256": MOUNTS,
    "integrity_generator_sha256": GENERATOR,
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
    assert changed_paths(base) == EXPECTED, (
        sorted(changed_paths(base)),
        sorted(EXPECTED),
    )

    report = json.loads(REPORT.read_text())
    receipt = json.loads(RECEIPT.read_text())
    contract = json.loads(CONTRACT.read_text())
    assert report["base_main_commit"] == BASE
    assert report["unit_id"] == "P10-U3"
    assert report["status"] == "BANK_READONLY_PROJECTION_PROVEN"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert set(report["scope"]["implementation_paths"]) == IMPLEMENTATION
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["status"] == report["status"]
    for key, path in INPUTS.items():
        assert report["inputs"][key] == sha(path), (
            key,
            report["inputs"][key],
            sha(path),
        )
    assert contract["status"] == "BANK_INVENTORY_CONTRACT_PROVEN"
    assert contract["next_step"]["id"] == "P10-U3"

    test_output = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"projection \((\d+)/(\d+)\)", test_output)
    assert match and match.group(1) == match.group(2) == "125"
    assertions = int(match.group(1))
    assert report["verification"]["assertions_total"] == assertions
    assert report["verification"]["assertions_passed"] == assertions
    assert report["verification"]["assertions_failed"] == 0
    assert receipt["coverage"]["assertions"] == assertions

    integration = report["integration"]
    assert integration["model"] == (
        "ONE_BANK_OWNER_READONLY_PROJECTION_EVENT_OR_USER_REFRESH"
    )
    assert integration["contract_version"] == (
        "PMP_CANONICAL_BANK_INVENTORY_CONTRACT_V1"
    )
    assert integration["owner"] == "bank_screen_owner"
    assert integration["canonical_bank_families"] == 13
    assert integration["local_storage_namespace_rules"] == 14
    assert integration["indexeddb_namespace_declarations"] == 2
    for key in (
        "indexeddb_opened_by_unit",
        "load_storage_reads",
        "load_storage_writes",
        "load_storage_deletes",
        "snapshot_storage_writes",
        "snapshot_storage_deletes",
        "raw_payloads_exposed",
        "write_apis_exposed",
        "delete_apis_exposed",
        "migration_apis_exposed",
        "recurring_projection_painters",
    ):
        assert integration[key] == 0, key
    for key in (
        "helper_registration_conveys_authority",
        "active_tab_conveys_authority",
        "filename_conveys_authority",
    ):
        assert integration[key] is False, key
    assert integration["unknown_or_orphan_policy"] == (
        "QUARANTINE_PRESERVE_EXACT_BYTES_NEVER_SILENTLY_DELETE"
    )
    assert integration["historic_namespace_policy"] == (
        "REFERENCE_ONLY_NEVER_SILENTLY_MERGE"
    )
    assert integration["refresh_mode"] == "EXPLICIT_USER_OR_OWNER_EVENT_ONLY"
    assert integration["single_projection_load"] is True
    assert integration["single_bank_tab_load"] is True
    assert integration["mount_registry_binding"] is True

    projection = PROJECTION.read_text()
    master = MASTER.read_text()
    inner = INNER.read_text()
    mounts = MOUNTS.read_text()
    for token in (
        "PMP_CANONICAL_BANK_INVENTORY_CONTRACT_V1",
        "PMP_CANONICAL_BANK_INVENTORY_ITEM_V1",
        "QUARANTINE_PRESERVE_EXACT_BYTES_NEVER_SILENTLY_DELETE",
        "REFERENCE_ONLY_NEVER_SILENTLY_MERGE",
        "helper_registration_conveys_authority:false",
        "active_tab_conveys_authority:false",
        "refresh_mode:'EXPLICIT_USER_OR_OWNER_EVENT_ONLY'",
    ):
        assert token in projection
    for forbidden in (
        "setInterval(",
        "setTimeout(",
        ".setItem(",
        ".removeItem(",
        "indexedDB.open",
    ):
        assert forbidden not in projection, forbidden
    assert "PMPBankInventoryReadonlyProjectionV1" in master
    assert "PMP_BANK_TAB_READONLY_EXPORT_V1" in master
    assert "raw_payload_exposed:false" in master
    assert "Helper registration and active tab convey no authority" in master
    assert ".recordWrite(" not in master
    assert ".recordDelete(" not in master
    assert "setInterval(" not in master
    assert "localStorage.setItem" not in master
    boundary_index = inner.index("pmp-bank-continuous-run-owner-boundary-v1.js")
    router_index = inner.index("pmp-master-bank-inventory-router-v1.js")
    projection_index = inner.index("pmp-bank-inventory-readonly-projection-v1.js")
    tab_index = inner.index("pmp-master-bank-tab-v1.js")
    assert 0 <= boundary_index < router_index < projection_index < tab_index
    assert inner.count("pmp-bank-inventory-readonly-projection-v1.js") == 1
    assert inner.count("pmp-master-bank-tab-v1.js") == 1
    assert mounts.count("pmp-bank-inventory-readonly-projection-v1.js") == 1

    before = {
        path: sha(path)
        for path in (MANIFEST, SEAL, BOOTSTRAP)
    }
    subprocess.check_call(
        ["python3", str(GENERATOR.relative_to(ROOT))],
        cwd=ROOT,
    )
    after = {
        path: sha(path)
        for path in (MANIFEST, SEAL, BOOTSTRAP)
    }
    assert before == after, (before, after)
    manifest = json.loads(MANIFEST.read_text())
    seal = json.loads(SEAL.read_text())
    records = {row["path"]: row for row in manifest["records"]}
    assert manifest["counts"]["runtime_records"] == 711
    assert manifest["counts"]["executable_records"] == 711
    assert len(manifest["records"]) == 711
    for path in (PROJECTION, MASTER, INNER, MOUNTS):
        relative = path.relative_to(ROOT).as_posix()
        assert records[relative]["sha256_hex"] == sha(path), relative
    assert report["runtime_integrity"] == {
        "runtime_records": 711,
        "manifest_sha256": sha(MANIFEST),
        "runtime_source_set_sha256": manifest["runtime_source_set_sha256"],
        "seal_sha256": sha(SEAL),
        "bootstrap_sha256": sha(BOOTSTRAP),
    }
    assert seal["status"] == "SEALED"
    assert seal["sealed_branch"] == report["branch"]
    assert seal["manifest_sha256"] == sha(MANIFEST)
    assert seal["runtime_source_set_sha256"] == (
        manifest["runtime_source_set_sha256"]
    )
    assert (
        f"const MANIFEST_SHA256='{sha(MANIFEST)}';"
        in BOOTSTRAP.read_text()
    )
    assert "Helper registration and active-tab state no Bank authority" in (
        seal["pass10_context"]
    )

    binding = report["no_blind_flying_gate"]
    assert binding["ci_lane"] == "deterministic_integration"
    assert binding["diagnostic_matrix_update"]["status"] == "ADDED"
    assert len(binding["fault_injection"]["cases"]) == 9
    assert len(binding["required_artifact_roles"]) == 9
    assert binding["upload_before_enforcement"] is True
    assert binding["automatic_retry"] is False
    assert binding["special_authority"] == {
        "required": False,
        "granted": False,
        "consumed": False,
    }
    gate = json.loads(
        output("python3", str(GATE.relative_to(ROOT)), "--base", BASE)
    )
    assert gate["status"] == "PASS", gate
    assert gate["unit_id"] == "P10-U3"
    assert gate["summary"]["runtime_paths"] == 5
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
        "Upload complete P10-U3 evidence",
        "Enforce preserved result after upload",
        "artifact-manifest.json",
        "authority-state.json",
        "exit-status.json",
        "scope.json",
        "retention-days: 90",
    ):
        assert token in workflow
    assert workflow.index("Upload complete P10-U3 evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert workflow.rstrip().endswith(
        'run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"'
    )

    assert report["effects"]["persisted_user_data_changed"] is False
    assert report["effects"]["storage_migration_performed"] is False
    assert report["effects"]["live_observation_performed"] is False
    assert report["effects"]["formal_proof_performed"] is False
    assert receipt["effects"]["persisted_user_data_changed"] is False
    assert report["authority"]["special_authority_consumed"] is False
    assert report["next_step"]["id"] == "P10-U4"
    assert report["next_step"]["requires_user_app_check"] is False
    assert report["next_step"]["persisted_user_data_change_allowed"] is False
    assert receipt["next_safe_move"]["step_id"] == "P10-U4"
    print(
        "PASS: exact thirteen-file P10-U3 Bank read-only projection verified "
        "(125/125, gate PASS, integrity resealed, P10-U4 ready)"
    )


if __name__ == "__main__":
    main()
