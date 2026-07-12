#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "pmp-pass2-actor-authority-registry-v1.json"
GATE = ROOT / "pmp-pass2-actor-authorization-gate-v1.js"
INNER = ROOT / "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html"
FIXTURE = ROOT / "audit/pass2/p2b-forbidden-action-fixture.html"

EXPECTED_COUNTS = {
    "p2a_actor_candidates": 576,
    "new_p2b_executable_actors": 3,
    "registered_actors": 579,
    "loadable_scripts": 311,
    "nonloadable_documents_or_gate": 268,
}
EXPECTED_INITIAL = [
    "pmp-current-route-resolver-v1.js",
    "pmp-app-orchestrator-v1.js",
    "pmp-pass2-atlas-adapter-v2.js",
    "pmp-mount-registry-v1.js",
    "pmp-authority-rules-v1.js",
    "pmp-active-bug-found-contract-v1.js",
    "pmp-bug-watch-passive-capture-v1.js",
    "pmp-safe-writer-current-return-fix-v1.js",
    "pmp-phase8-atlas-marker-v1.js",
    "pmp-pass1r-version-aligner-v1.js",
    "pmp-pass1w-live-proof-reader-v1.js",
    "pmp-active-path-discovery-machine-v1.js",
    "pmp-continuous-run-bank-order-frame-loader-v1.js",
]
GLOBAL_FORBIDDEN = {
    "cache.delete",
    "code.eval",
    "indexeddb.delete",
    "service_worker.register",
    "storage.local.clear",
    "storage.session.clear",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    registry = json.loads(REGISTRY.read_text("utf-8"))
    if registry.get("type") != "PMP_PASS2_ACTOR_AUTHORITY_REGISTRY_V1":
        fail("registry type")
    if registry.get("default_policy") != "FAIL_CLOSED":
        fail("registry is not fail closed")
    if registry.get("counts") != EXPECTED_COUNTS:
        fail(f"registry counts {registry.get('counts')}")
    if registry.get("active_inner_initial_actor_paths") != EXPECTED_INITIAL:
        fail("initial actor order changed")
    if set(registry.get("global_forbidden_capabilities", [])) != GLOBAL_FORBIDDEN:
        fail("global forbidden capabilities changed")
    if registry.get("pass_boundary") != {
        "overall_pass": "Pass 2",
        "phase": "P2-B",
        "pass2_complete": False,
        "pass3_started": False,
    }:
        fail("pass boundary is wrong")

    actors = registry["actors"]
    paths = [row["path"] for row in actors]
    if len(paths) != len(set(paths)):
        fail("duplicate actor paths")
    identity_errors = []
    permission_errors = []
    for row in actors:
        path = ROOT / row["path"]
        if not path.is_file():
            identity_errors.append({"path": row["path"], "error": "missing"})
            continue
        data = path.read_bytes()
        if sha256(data) != row["sha256"]:
            identity_errors.append({"path": row["path"], "error": "sha256"})
        if git_blob(data) != row["git_blob_sha"]:
            identity_errors.append({"path": row["path"], "error": "git_blob"})
        if row.get("id") != row["path"]:
            identity_errors.append({"path": row["path"], "error": "id"})
        allowed = set(row.get("allowed_capabilities", []))
        forbidden_overlap = allowed & GLOBAL_FORBIDDEN
        if forbidden_overlap:
            permission_errors.append({"path": row["path"], "forbidden": sorted(forbidden_overlap)})
    if identity_errors:
        fail(f"actor identity errors: {identity_errors[:10]}")
    if permission_errors:
        fail(f"global forbidden capability granted: {permission_errors[:10]}")

    inner = INNER.read_text("utf-8")
    gate_text = GATE.read_text("utf-8")
    fixture = FIXTURE.read_text("utf-8")
    first_script = re.search(r"<script\s+src=[\"']([^\"']+)[\"']", inner)
    if not first_script or first_script.group(1) != "pmp-pass2-actor-authorization-gate-v1.js":
        fail("authorization gate is not the first external inner script")
    for path in EXPECTED_INITIAL:
        if re.search(rf"<script\s+src=[\"'][^\"']*{re.escape(path)}", inner):
            fail(f"initial actor still bypasses gate through static script tag: {path}")
    required_inner_markers = [
        "await authorityGate.ready()",
        "authorityGate.runDocument",
        "authorityGate.loadActor('pmp-current-route-resolver-v1.js'",
        "authorityGate.loadActors(initialActorPaths",
        "authorityGate.sealBootstrap",
        "entry_blocked_before_unapproved_actor_side_effect",
    ]
    for marker in required_inner_markers:
        if marker not in inner:
            fail(f"inner marker missing: {marker}")

    required_gate_markers = [
        "P2_UNKNOWN_ACTOR",
        "P2_CAPABILITY_DENIED",
        "P2_CAPABILITY_GLOBALLY_FORBIDDEN",
        "P2_SOURCE_DIGEST_MISMATCH",
        "side_effect_executed:false",
        "storage.local.write",
        "requireInWindow(w,'timer.recurring'",
        "requireInWindow(w,'dom.write'",
        "requireInWindow(w,'network.fetch'",
        "requireInWindow(w,'indexeddb.delete'",
        "requireInWindow(w,'cache.delete'",
        "requireInWindow(w,'service_worker.register'",
        "requireInWindow(w,'code.eval'",
        "state.originals.removeAttribute.call(element,'src')",
        "if(actual!==actor.sha256)",
    ]
    for marker in required_gate_markers:
        if marker not in gate_text:
            fail(f"gate enforcement marker missing: {marker}")

    dynamic_loaders = [
        ROOT / "pmp-app-orchestrator-v1.js",
        ROOT / "pmp-safe-writer-current-return-fix-v1.js",
        ROOT / "pmp-continuous-run-bank-order-frame-loader-v1.js",
    ]
    for path in dynamic_loaders:
        text = path.read_text("utf-8")
        if "createElement('script')" in text or 'createElement("script")' in text:
            fail(f"direct dynamic script creation remains in {path.name}")
        if ".loadActor(" not in text:
            fail(f"authorized actor loader missing in {path.name}")

    fixture_names = re.findall(r"record\('([^']+)'", fixture)
    if len(fixture_names) != 14 or len(set(fixture_names)) != 14:
        fail(f"fixture must contain 14 unique assertions, found {len(fixture_names)}")
    for marker in [
        "unknown actor storage write blocked before effect",
        "known actor undeclared storage capability blocked",
        "globally forbidden storage clear blocked and sentinel preserved",
        "undeclared DOM mutation blocked before connection",
        "undeclared recurring timer blocked before scheduling",
        "undeclared network fetch blocked before request",
        "unregistered script path quarantined before append",
        "undeclared window navigation blocked before action",
        "IndexedDB deletion blocked before database loss",
        "cache deletion blocked before cache loss",
        "registered path with wrong bytes blocked before execution",
        "registered exact-source actor executes",
        "gate remains enforced",
        "quarantine ledger is append-history with denials",
    ]:
        if marker not in fixture_names:
            fail(f"fixture assertion missing: {marker}")

    report = {
        "type": "PMP_PASS2_P2B_STATIC_TEST_RESULT_V1",
        "status": "PASS",
        "tests_passed": 16,
        "tests_failed": 0,
        "registered_actors": len(actors),
        "exact_actor_identity_errors": 0,
        "global_forbidden_grants": 0,
        "initial_actor_paths": len(EXPECTED_INITIAL),
        "adversarial_fixture_assertions": len(fixture_names),
        "pass2_complete": False,
        "pass3_started": False,
    }
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output:
        output.write_text(text, "utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
