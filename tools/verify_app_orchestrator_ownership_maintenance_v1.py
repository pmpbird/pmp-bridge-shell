#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "pmp-runtime-integrity-manifest-v1.json"
SEAL = ROOT / "audit/a003-manifest-seal.json"
BOOTSTRAP = ROOT / "pmp-app-current.html"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True)


def git_bytes(path: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"HEAD:{path}"], cwd=ROOT
    )


def main() -> None:
    test = output(
        sys.executable,
        "tools/test_app_orchestrator_ownership_maintenance_v1.py",
    )
    assert "PASS:" in test or '"status": "PASS"' in test

    changed_js = [
        "pmp-app-orchestrator-ownership-runtime-v1.js",
        "pmp-new-chat-safe-handoff-v1.js",
        "pmp-active-path-discovery-machine-v1.js",
        "pmp-active-path-discovery-machine-v2.js",
        "pmp-active-path-discovery-zip-export-v2.js",
        "pmp-app-orchestrator-v1.js",
        "pmp-diagnostics-bottom-tab-forcer-v1.js",
        "pmp-pass8-helper-rules-v1.js",
        "pmp-helper-owner-integration-v1.js",
        "pmp-pass1r-version-aligner-v1.js",
        "pmp-continuous-run-bank-transfer-store-v1.js",
        "pmp-continuous-run-bank-transfer-store-v2.js",
        "pmp-continuous-run-bank-must-source-zip-v1.js",
        "pmp-continuous-run-bank-verify-receipt-fix-v1.js",
        "pmp-continuous-run-bank-long-packet-option-v1.js",
        "pmp-continuous-run-bank-source-zip-gate-fix-v1.js",
        "pmp-source-zip-reader-level2-v1.js",
        "pmp-source-zip-extractor-level2b-v1.js",
        "pmp-source-pdf-text-level2c-v1.js",
        "pmp-source-reference-gate-level4-v1.js",
        "pmp-resident-cr-status-router-v1.js",
        "pmp-resident-continuous-run-status-reader-v1.js",
        "pmp-source-text-reader-level3-v1.js",
        "pmp-private-source-loader-v1.js",
        "pmp-top-lossless-injector.js",
        "pmp-top-lossless-loader.js",
        "pmp-helper-bank-live-inspector-v2.js",
        "pmp-helper-problem-type-seeds-v1.js",
        "pmp-helper-problem-type-only-v1.js",
        "pmp-hidden-safe-writer-surface-cleaner-v1.js",
        "pmp-master-bank-tab-v1.js",
        "pmp-owner-diagnostics-foundation-v1.js",
        "pmp-continuous-run-bank-order-frame-loader-v1.js",
        "pmp-safe-area-surface-fill-v1.js",
        "pmp-layout-guard-v1.js",
        "pmp-continuous-run-bank-stable-status-owner-v1.js",
        "pmp-bank-zero-loading-flash-guard-v1.js",
        "pmp-current-page-code-scope-v1.js",
        "pmp-route-code-map-adapter-v1.js",
        "pmp-diagnostics-owner-v1.js",
    ]
    node = shutil.which("node")
    if not node:
        bundled = Path(
            "/Users/phillippowers/.cache/codex-runtimes/"
            "codex-primary-runtime/dependencies/node/bin/node"
        )
        node = str(bundled) if bundled.exists() else None
    assert node, "Node.js runtime unavailable"
    for path in changed_js:
        subprocess.check_call(
            [node, "--check", path],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
        )

    manifest = json.loads(MANIFEST.read_text("utf-8"))
    index = {row["path"]: row for row in manifest["records"]}
    runtime_paths = json.loads(
        (ROOT / "pmp-app-orchestrator-ownership-registry-v1.json").read_text()
    )
    assert runtime_paths["type"] == "PMP_APP_ORCHESTRATOR_OWNERSHIP_REGISTRY_V1"
    required = set(changed_js) | {
        "pmp-app-orchestrator-ownership-registry-v1.json",
        "pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html",
        "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html",
        "pmp-current-inner-cleanbug-rgcontrols-v23.html",
        "pmp-current-inner-cleanbug-rgcontrols-v4.html",
    }
    for path in required:
        assert path in index, path
        assert index[path]["sha256_hex"] == sha(ROOT / path), path
    assert index["Index.html"]["sha256_hex"] == hashlib.sha256(
        git_bytes("Index.html")
    ).hexdigest()
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
        assert report_data["status"] == "OWNERSHIP_MAINTENANCE_GREEN"
        assert receipt_data["status"] == "PASS"
        assert report_data["effects"]["persisted_user_data_changed"] is False
        assert report_data["effects"]["storage_migration_performed"] is False
        assert report_data["effects"]["formal_proof_performed"] is False

    print("PASS: App Orchestrator ownership maintenance verified")


if __name__ == "__main__":
    main()
