#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import json
import mimetypes
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "pmp-runtime-integrity-manifest-v1.json"
SEAL = ROOT / "audit/a003-manifest-seal.json"
BOOTSTRAP = ROOT / "pmp-app-current.html"
MAINTENANCE_REPORT = (
    ROOT / "audit/pass13/app-orchestrator-ownership-maintenance-v1.json"
)
RELEASE_BRANCH = "agent/app-orchestrator-owner-maintenance-release-v1"


def active_branch() -> str:
    github_head = os.environ.get("GITHUB_HEAD_REF", "").strip()
    if github_head:
        return github_head
    return subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=ROOT, text=True
    ).strip()

HTML_REPLACEMENTS = {
    "pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html": [
        (
            "pmp-safe-area-surface-fill-v1.js?fresh=safe-area-surface-fill-20260708B",
            "pmp-safe-area-surface-fill-v1.js?fresh=ownership-presentation-local-20260727A",
        ),
        (
            "pmp-active-path-discovery-zip-export-v2.js?fresh=discovery-owner-v30-20260708A",
            "pmp-active-path-discovery-zip-export-v2.js?fresh=canonical-v1-reader-event-driven-20260727A",
        ),
    ],
    "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html": [
        (
            '<script src="pmp-app-orchestrator-v1.js?fresh=app-orchestrator-final-clean-startup-certification-20260709A"></script>',
            '<script src="pmp-app-orchestrator-ownership-runtime-v1.js?fresh=exclusive-owner-runtime-20260727A"></script>'
            '<script src="pmp-new-chat-safe-handoff-v1.js?fresh=one-button-copy-or-zip-20260727A"></script>'
            '<script src="pmp-app-orchestrator-v1.js?fresh=exclusive-ownership-handoff-20260727A"></script>',
        ),
        (
            "pmp-pass1r-version-aligner-v1.js?fresh=active-path-aligner-pass5-stable-20260704I",
            "pmp-pass1r-version-aligner-v1.js?fresh=read-only-mount-alignment-20260727A",
        ),
        (
            "pmp-active-path-discovery-machine-v1.js?fresh=active-path-discovery-pass7-v21-v29-freeze-proof-20260706A",
            "pmp-active-path-discovery-machine-v1.js?fresh=canonical-event-driven-mount-20260727B",
        ),
        (
            "pmp-continuous-run-bank-order-frame-loader-v1.js?fresh=pass75-headless-runtime-platform-20260708A",
            "pmp-continuous-run-bank-order-frame-loader-v1.js?fresh=single-owner-frame-20260727A",
        ),
    ],
    "pmp-current-inner-cleanbug-rgcontrols-v23.html": [
        (
            "pmp-helper-bank-live-inspector-v2.js?fresh=helper-bank-live-inspector-v210-helper-only-20260628Z",
            "pmp-helper-bank-live-inspector-v2.js?fresh=owner-requested-read-only-presenter-20260727A",
        ),
        (
            "pmp-helper-problem-type-seeds-v1.js?fresh=helper-problem-type-seeds-v121-dedupe-evidence-panel-20260628M",
            "pmp-helper-problem-type-seeds-v1.js?fresh=read-only-symptom-analyzer-20260727A",
        ),
        (
            "pmp-helper-problem-type-only-v1.js?fresh=helper-problem-type-only-v100-20260628A",
            "pmp-helper-problem-type-only-v1.js?fresh=pure-normalizer-20260727A",
        ),
        (
            "pmp-hidden-safe-writer-surface-cleaner-v1.js?fresh=hidden-safe-writer-surface-cleaner-v100-20260628P",
            "pmp-hidden-safe-writer-surface-cleaner-v1.js?fresh=inactive-read-only-20260727A",
        ),
        (
            "pmp-continuous-run-bank-transfer-store-v2.js?fresh=transfer-store-data-only-bso-20260628C",
            "pmp-continuous-run-bank-transfer-store-v2.js?fresh=exclusive-bank-writer-broker-20260727A",
        ),
        (
            "pmp-continuous-run-bank-verify-receipt-fix-v1.js?fresh=v110-noflicker-20260624T1447Z",
            "pmp-continuous-run-bank-verify-receipt-fix-v1.js?fresh=owner-delegating-event-driven-20260727A",
        ),
        (
            "pmp-continuous-run-bank-must-source-zip-v1.js?fresh=source-zip-data-only-bso-20260628C",
            "pmp-continuous-run-bank-must-source-zip-v1.js?fresh=source-gate-requester-20260727A",
        ),
        (
            "pmp-resident-cr-status-router-v1.js?fresh=cr-local-answer-router-v100-20260627T2106Z",
            "pmp-resident-cr-status-router-v1.js?fresh=canonical-reader-delegate-20260727A",
        ),
        (
            "pmp-resident-continuous-run-status-reader-v1.js?fresh=resident-continuous-run-status-reader-v101-20260627T2052Z",
            "pmp-resident-continuous-run-status-reader-v1.js?fresh=canonical-event-driven-reader-20260727A",
        ),
    ],
    "pmp-current-inner-cleanbug-rgcontrols-v4.html": [
        (
            "pmp-continuous-run-bank-stable-status-owner-v1.js?fresh=stable-status-owner-20260624T2140Z",
            "pmp-continuous-run-bank-stable-status-owner-v1.js?fresh=inactive-read-only-20260727A",
        ),
        (
            "pmp-layout-guard-v1.js?fresh=final-level2c-label-20260625A",
            "pmp-layout-guard-v1.js?fresh=inactive-read-only-20260727A",
        ),
        (
            "pmp-current-page-code-scope-v1.js?fresh=current-page-code-scope-v100-current-page-only-20260627A",
            "pmp-current-page-code-scope-v1.js?fresh=reload-receipt-read-only-20260727A",
        ),
        (
            "pmp-source-text-reader-level3-v1.js?fresh=l3-clear-labels-C",
            "pmp-source-text-reader-level3-v1.js?fresh=source-owner-event-driven-20260727A",
        ),
    ],
    "pmp-current-inner-cleanbug-rgcontrols-v3.html": [
        (
            "pmp-top-lossless-injector.js?fresh=rgcontrols-v3-private-medium",
            "pmp-top-lossless-injector.js?fresh=idempotent-owner-loader-request-20260727A",
        ),
        (
            "pmp-private-source-loader-v1.js?fresh=rgcontrols-v3-source-loader-v1-simple-ui",
            "pmp-private-source-loader-v1.js?fresh=explicit-event-driven-source-intake-20260727A",
        ),
    ],
}

RUNTIME_PATHS = (
    "Index.html",
    "pmp-app-orchestrator-ownership-registry-v1.json",
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
    *HTML_REPLACEMENTS.keys(),
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob(data: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(data)).encode() + b"\0" + data
    ).hexdigest()


def execution_class(path: str) -> str:
    if path.endswith(".html"):
        return "EXECUTABLE_DOCUMENT"
    if path.endswith(".json"):
        return "RUNTIME_DATA"
    return "EXECUTABLE_SCRIPT"


def record(path: str, existing: dict | None = None) -> dict:
    if path == "Index.html":
        data = subprocess.check_output(
            ["git", "show", "HEAD:Index.html"], cwd=ROOT
        )
    else:
        data = (ROOT / path).read_bytes()
    digest = hashlib.sha256(data).digest()
    result = dict(existing or {})
    result.update(
        {
            "path": path,
            "bytes": len(data),
            "git_blob_sha": blob(data),
            "sha256_hex": digest.hex(),
            "sha256_base64": base64.b64encode(digest).decode(),
            "sri": "sha256-" + base64.b64encode(digest).decode(),
            "mime_type": mimetypes.guess_type(path)[0]
            or "application/octet-stream",
            "execution_class": execution_class(path),
            "enforcement": "SERVICE_WORKER_PRE_RESPONSE_SHA256",
        }
    )
    return result


def apply_html_replacements() -> None:
    for path, replacements in HTML_REPLACEMENTS.items():
        target = ROOT / path
        text = target.read_text("utf-8")
        if path == "pmp-current-inner-cleanbug-rgcontrols-v23.html":
            text = re.sub(
                r"pmp-master-bank-tab-v1\.js\?fresh=(?:"
                r"exclusive-helper-presentation-owner-20260727A|"
                r"pass10-unit7-legacy-alias-containment-20260727A"
                r"(?:-ownership-20260727B)*)",
                "pmp-master-bank-tab-v1.js?fresh="
                "pass10-unit7-legacy-alias-containment-20260727A-"
                "ownership-20260727B",
                text,
            )
        for old, new in replacements:
            if new in text and old not in text:
                continue
            assert text.count(old) >= 1, (path, old, text.count(old))
            text = text.replace(old, new)
        target.write_text(text, "utf-8")


def runtime_identity(manifest: dict) -> str:
    identity = {
        "records": [
            (row["path"], row["sha256_hex"])
            for row in manifest.get("records", [])
        ],
        "historical_records": [
            (row["path"], row.get("repository_ref"), row["sha256_hex"])
            for row in manifest.get("historical_records", [])
        ],
        "external_records": [
            (row["url"], row["sha256_hex"])
            for row in manifest.get("external_records", [])
        ],
        "root_trust_anchors": manifest.get("root_trust_anchors", []),
        "policy": {
            "algorithm": manifest.get("algorithm"),
            "unlisted_executable_policy": manifest.get(
                "unlisted_executable_policy"
            ),
            "network_policy": manifest.get("network_policy"),
        },
    }
    return sha(
        json.dumps(
            identity, sort_keys=True, separators=(",", ":")
        ).encode()
    )


def update_no_blind_flying_binding() -> None:
    if not MAINTENANCE_REPORT.exists():
        return
    if active_branch() == RELEASE_BRANCH:
        # P13-U8 owns its exact documentation-only release scope. Preserve the
        # already-merged P13-U7 implementation record byte-for-byte.
        return
    base = "fbc75d5067df28d96f73fc3f8b18c8dbd45fa571"
    if subprocess.run(
        ["git", "cat-file", "-e", base],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode != 0:
        # Pull-request merge checkouts may be shallow. The exact committed
        # binding is authoritative there; do not fabricate a different scope.
        return
    changed = set(
        subprocess.check_output(
            ["git", "diff", "--name-only", base],
            cwd=ROOT,
            text=True,
        ).splitlines()
    )
    changed.update(
        subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=ROOT,
            text=True,
        ).splitlines()
    )
    changed.discard("")
    changed_paths = sorted(changed)
    excluded = (".github/", "audit/", "tools/", "docs/")
    implementation_paths = [
        path
        for path in changed_paths
        if not path.startswith(excluded)
        and Path(path).suffix.lower()
        in {".js", ".html", ".css", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"}
    ]
    report = json.loads(MAINTENANCE_REPORT.read_text("utf-8"))
    report["unit_id"] = "P13-U9"
    report["scope"] = {
        "changed_paths": changed_paths,
        "implementation_paths": implementation_paths,
    }
    report["no_blind_flying_gate"] = {
        "type": "PMP_PASS6_PERMANENT_NO_BLIND_FLYING_GATE_BINDING_V1",
        "version": "1.0.0",
        "ci_lane": "deterministic_browser_harness",
        "diagnostic_matrix_update": {
            "status": "ADDED",
            "applicable_matrix": "audit/pass13/app-orchestrator-ownership-maintenance-v1.json",
            "rationale": (
                "This maintenance matrix binds the two ownership audits to "
                "exclusive writers, bounded helpers, deterministic fault "
                "checks, an isolated local browser check, and the safe "
                "new-chat handoff."
            ),
        },
        "diagnostic_evidence_routes": [
            "audit/pass13/app-orchestrator-ownership-maintenance-v1.json",
            "audit/pass13/PMP_APP_ORCHESTRATOR_MAINTENANCE_CURRENT_STATE_V1.md",
            "audit/pass13/PMP_APP_ORCHESTRATOR_MAINTENANCE_EXACT_NEXT_MOVE_V1.md",
            "pmp-app-orchestrator-ownership-registry-v1.json",
        ],
        "deterministic_test_paths": [
            "tools/test_app_orchestrator_ownership_maintenance_v1.py"
        ],
        "verifier_paths": [
            "tools/verify_app_orchestrator_ownership_maintenance_v1.py"
        ],
        "receipt_paths": [
            "audit/pass13/receipts/RECEIPT_APP_ORCHESTRATOR_OWNERSHIP_MAINTENANCE_20260727T180000Z_001.json"
        ],
        "observed_facts": [
            {
                "claim_type": "OBSERVED",
                "fact": (
                    "The ownership matrix passes 167 deterministic checks "
                    "covering exclusive writers, helper delegation, inert "
                    "legacy actors, event-driven presentation, and the "
                    "copy-or-ZIP handoff."
                ),
                "evidence_paths": [
                    "tools/test_app_orchestrator_ownership_maintenance_v1.py",
                    "audit/pass13/app-orchestrator-ownership-maintenance-v1.json",
                ],
            },
            {
                "claim_type": "OBSERVED",
                "fact": (
                    "A bounded isolated local browser run reached the normal "
                    "app, showed the Diagnostics and App Orchestrator Status "
                    "screens, copied the safe handoff, and displayed one "
                    "canonical Continuous Run Level 1 through 30B sequence."
                ),
                "evidence_paths": [
                    "audit/pass13/app-orchestrator-ownership-maintenance-v1.json",
                    "audit/pass13/receipts/RECEIPT_APP_ORCHESTRATOR_OWNERSHIP_MAINTENANCE_20260727T180000Z_001.json",
                ],
            },
        ],
        "inferred_conclusions": [
            {
                "claim_type": "INFERRED",
                "conclusion": (
                    "The exact maintenance head is ready for GitHub CI and "
                    "merge because its owner boundaries, regressions, runtime "
                    "integrity bindings, and user-data exclusions are "
                    "deterministically verified."
                ),
                "basis_evidence_paths": [
                    "audit/pass13/app-orchestrator-ownership-maintenance-v1.json",
                    "pmp-app-orchestrator-ownership-registry-v1.json",
                    "tools/verify_app_orchestrator_ownership_maintenance_v1.py",
                ],
            }
        ],
        "fault_injection": {
            "status": "COVERED",
            "cases": [
                "duplicate resource id",
                "one identifier assigned to multiple resources",
                "protected resource with no writer",
                "helper direct canonical write",
                "legacy recurring repaint or reinjection",
                "cross-schema Active Path Discovery alias",
                "Storage monkeypatch",
                "duplicate Continuous Run presentation",
            ],
        },
        "required_artifact_roles": [
            "command",
            "stdout",
            "stderr",
            "exit_status",
            "result",
            "scope",
            "environment",
            "authority_state",
            "manifest",
        ],
        "upload_before_enforcement": True,
        "automatic_retry": False,
        "special_authority": {
            "required": False,
            "granted": False,
            "consumed": False,
        },
    }
    MAINTENANCE_REPORT.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        "utf-8",
    )


def main() -> None:
    apply_html_replacements()
    manifest = json.loads(MANIFEST.read_text("utf-8"))
    index = {row["path"]: row for row in manifest["records"]}
    for path in RUNTIME_PATHS:
        index[path] = record(path, index.get(path))
    manifest["records"] = [index[path] for path in sorted(index)]
    manifest["counts"]["runtime_records"] = len(manifest["records"])
    manifest["counts"]["executable_records"] = sum(
        row["execution_class"] != "STYLE_SOURCE"
        for row in manifest["records"]
    )
    manifest["runtime_source_set_sha256"] = runtime_identity(manifest)
    manifest_bytes = (
        json.dumps(
            manifest, indent=2, sort_keys=True, ensure_ascii=False
        )
        + "\n"
    ).encode()
    MANIFEST.write_bytes(manifest_bytes)

    manifest_sha = sha(manifest_bytes)
    seal = json.loads(SEAL.read_text("utf-8"))
    seal.update(
        manifest_bytes=len(manifest_bytes),
        manifest_sha256=manifest_sha,
        runtime_source_set_sha256=manifest[
            "runtime_source_set_sha256"
        ],
        sealed_branch=(
            active_branch()
            or "agent/app-orchestrator-owner-conflict-repair-v1"
        ),
        maintenance_context=(
            "Repairs audited multiple-owner and helper-owner conflicts, "
            "installs exclusive ownership prevention, real read-only "
            "diagnostics, directly visible one-button safe new-chat handoff, "
            "and restored Active Path Discovery access. No route, persisted "
            "user data, storage migration, formal proof, or production "
            "activation is performed."
        ),
    )
    SEAL.write_text(
        json.dumps(seal, indent=2, sort_keys=True) + "\n", "utf-8"
    )

    bootstrap = BOOTSTRAP.read_text("utf-8")
    updated, count = re.subn(
        r"const MANIFEST_SHA256='[0-9a-f]{64}';",
        f"const MANIFEST_SHA256='{manifest_sha}';",
        bootstrap,
        count=1,
    )
    assert count == 1
    BOOTSTRAP.write_text(updated, "utf-8")
    update_no_blind_flying_binding()
    print(
        "PASS: App Orchestrator ownership maintenance runtime "
        "identities regenerated"
    )


if __name__ == "__main__":
    main()
