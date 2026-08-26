#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "pmp-app-orchestrator-ownership-registry-v1.json"
MANIFEST = ROOT / "pmp-runtime-integrity-manifest-v1.json"
SEAL = ROOT / "audit/a003-manifest-seal.json"
BOOTSTRAP = ROOT / "pmp-app-current.html"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"HEAD:{path}"], cwd=ROOT)


def main() -> None:
    registry = json.loads(REGISTRY.read_text("utf-8"))
    manifest = json.loads(MANIFEST.read_text("utf-8"))
    assert registry["type"] == "PMP_APP_ORCHESTRATOR_OWNERSHIP_REGISTRY_V1"
    assert registry["owner"] == "app_orchestrator_owner"
    assert registry["single_owner_rule"] is True
    assert registry["status"] == "ACTIVE"

    resources = registry["resources"]
    helpers = registry["helpers"]
    resource_ids = [row["resource_id"] for row in resources]
    assert len(resource_ids) == len(set(resource_ids))
    helper_ids = [row["helper_id"] for row in helpers]
    assert len(helper_ids) == len(set(helper_ids))

    owners = {row["resource_id"]: row["owner"] for row in resources}
    writers = {row["resource_id"]: row["writers"] for row in resources}
    assert owners["active_path_discovery_canonical_report"] == "active_path_discovery_owner"
    assert writers["active_path_discovery_canonical_report"] == [
        "pmp-active-path-discovery-machine-v1.js"
    ]
    assert owners["mount_registry"] == "mount_registry_owner"
    assert writers["mount_registry"] == ["pmp-mount-registry-v1.js"]
    assert owners["diagnostics_surface"] == "diagnostics_owner"
    assert writers["diagnostics_surface"] == ["pmp-diagnostics-owner-v1.js"]
    assert owners["helper_bank_presentation"] == "bank_screen_owner"

    helper_map = {row["helper_id"]: row for row in helpers}
    assert helper_map["active_path_discovery_helper"]["owner"] == "app_orchestrator_owner"
    assert helper_map["active_path_discovery_helper"]["authority"] == "read_inspect_request_present"
    assert helper_map["mount_registry_helper"]["owner"] == "app_orchestrator_owner"
    assert helper_map["section_owner_registry_helper"]["owner"] == "diagnostics_owner"
    assert helper_map["resident_status_reader_helper"]["owner"] == "resident_30b_owner"
    assert helper_map["zip_reader_helper"]["owner"] == "source_gate_owner"

    protected = registry["protected_resources"]
    assert protected["single_writer_required"] is True
    assert protected["unknown_helpers_fail_closed"] is True
    assert protected["diagnostics_read_only"] is True
    assert protected["persisted_user_data_rewrite_forbidden"] is True

    manifest_records = manifest["records"]
    index = {row["path"]: row for row in manifest_records}
    assert index["pmp-app-orchestrator-ownership-registry-v1.json"]["sha256_hex"] == sha(
        REGISTRY
    )
    assert index["pmp-app-current.html"]["sha256_hex"] == sha(BOOTSTRAP)
    assert index["index.html"]["sha256_hex"] == hashlib.sha256(
        git_bytes("index.html")
    ).hexdigest()
    assert index["Index.html"]["sha256_hex"] != index["index.html"]["sha256_hex"]

    seal = json.loads(SEAL.read_text("utf-8"))
    assert seal["manifest_sha256"] == sha(MANIFEST)
    bootstrap = BOOTSTRAP.read_text("utf-8")
    match = re.search(r"const MANIFEST_SHA256='([0-9a-f]{64})';", bootstrap)
    assert match and match.group(1) == seal["manifest_sha256"]
    assert (
        seal["runtime_source_set_sha256"]
        == manifest["runtime_source_set_sha256"]
    )
    assert seal["sealed_branch"].startswith(("chatgpt/diagnostics-", "chatgpt/full-diagnostics-", "chatgpt/atlas-")) or seal["sealed_branch"] in {
        "agent/app-orchestrator-owner-conflict-repair-v1",
        "agent/app-orchestrator-owner-maintenance-release-v1",
        "agent/diagnostics-handoff-active-path-restoration-v1",
        "agent/private-library-research-line",
        "main",
    }

    report = ROOT / "audit/pass13/app-orchestrator-ownership-maintenance-v1.json"
    receipt = ROOT / "audit/pass13/receipts/RECEIPT_APP_ORCHESTRATOR_OWNERSHIP_MAINTENANCE_20260727T180000Z_001.json"
    if report.exists() or receipt.exists():
        assert report.exists() and receipt.exists()
        report_data = json.loads(report.read_text("utf-8"))
        receipt_data = json.loads(receipt.read_text("utf-8"))
        assert report_data["type"] == "PMP_APP_ORCHESTRATOR_OWNERSHIP_MAINTENANCE_V1"
        assert receipt_data["type"] == "PMP_APP_ORCHESTRATOR_OWNERSHIP_MAINTENANCE_RECEIPT_V1"
        assert report_data["status"] == "OWNERSHIP_MAINTENANCE_GREEN"
        assert receipt_data["status"] == "PASS"
        assert report_data["owner_changes"] is False
        assert report_data["helper_authority_changes"] is False
        assert report_data["route_changes"] is False
        assert report_data["persisted_user_data_changes"] is False

    print(json.dumps({"status": "PASS", "registry_sha256": sha(REGISTRY), "manifest_sha256": sha(MANIFEST)}, sort_keys=True))


if __name__ == "__main__":
    main()
