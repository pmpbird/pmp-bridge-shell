#!/usr/bin/env python3
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "f6eb161eceb269cb2a15e02f52683b2f6ad835e4"
AUDIT_PATH = "audit/pass5/pass5-mount-registry-diagnostics-unit1-readiness-inventory-v1.json"


def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def payload(path):
    return subprocess.check_output(["git", "show", f"HEAD:{path}"], cwd=ROOT)


def text(path):
    return payload(path).decode()


def main():
    audit = json.loads((ROOT / AUDIT_PATH).read_text())
    assert audit["status"] == "READINESS_AUDIT_PASS"
    assert audit["base_main_commit"] == BASE
    assert audit["pass"] == 5 and audit["unit"] == 1

    for path, identity in audit["source_identities"].items():
        raw = payload(path)
        assert output("git", "rev-parse", f"HEAD:{path}") == identity["git_blob_sha"], path
        assert len(raw) == identity["bytes"], path
        assert hashlib.sha256(raw).hexdigest() == identity["sha256"], path

    current_map = json.loads(text("pmp-current-map-v12.json"))
    route = audit["current_route"]
    assert current_map["route_contract"]["sole_authority"] == route["authority"]
    assert current_map["route_guardian"]["path"] == route["route_guardian"]
    assert current_map["current_app"]["path"] == route["reload_owner"]
    assert current_map["runtime_chain"]["inner_v30"]["path"] == route["current_inner"]
    assert current_map["route_contract"]["failure_mode"] == "fail_closed"
    assert current_map["route_contract"]["implicit_fallbacks"] is False

    registry = text("pmp-mount-registry-v1.js")
    for name, expected in (
        ("STATIC_CURRENT", 81),
        ("SUPPORT_REACHABLE", 66),
        ("HISTORIC", 18),
    ):
        match = re.search(rf"const {name}=list\(`(.*?)`\);", registry, re.S)
        assert match, name
        values = match.group(1).split()
        assert len(values) == expected and len(set(values)) == expected, name
    assert "mode:'active_path_registry_only'" in registry
    assert "default_for_unlisted_files:'NON_BOOT_OUTSIDE_ACTIVE_ATLAS'" in registry
    for key in audit["current_registry"]["persistent_system_keys"]:
        assert f"'{key}'" in registry
    assert "setInterval(()=>scan('slow_watch_9000'),9000)" in registry
    assert "localStorage.setItem" in registry
    for state in audit["unit2_contract_lock"]["shared_states"]:
        assert f"'{state}'" not in registry and f'"{state}"' not in registry

    inner = text("pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html")
    ordered = [
        "pmp-app-orchestrator-v1.js",
        "pmp-pass2-atlas-adapter-v2.js",
        "pmp-mount-registry-v1.js",
        "pmp-phase8-atlas-marker-v1.js",
        "pmp-pass1r-version-aligner-v1.js",
        "pmp-active-path-discovery-machine-v1.js",
    ]
    offsets = [inner.index(name) for name in ordered]
    assert offsets == sorted(offsets)

    orchestrator = text("pmp-app-orchestrator-v1.js")
    assert "{id:'mount_registry',path:'pmp-mount-registry-v1.js'" in orchestrator
    assert "loadScript(def)" in orchestrator
    assert "api[def.run]" in orchestrator

    adapter = text("pmp-pass2-atlas-adapter-v2.js")
    for stale in (
        "pmp-current-map-v10.json",
        "pmp-route-guardian-current-loader-v17.html",
        "pmp-current-reload-owner-v27.html",
        "pmp-current-inner-cleanbug-rgcontrols-v26.html",
    ):
        assert stale in adapter
    assert "Object.defineProperty(window,'PMPMountRegistryV1'" in adapter

    phase8 = text("pmp-phase8-atlas-marker-v1.js")
    aligner = text("pmp-pass1r-version-aligner-v1.js")
    assert "r.version=V" in phase8
    assert "api.scan&&api.scan('phase8_marker_post_aligner_boot')" in phase8
    assert "r.version=R" in aligner
    assert "p('pmp_mount_registry_v1',r)" in aligner
    assert "p('pmp_mount_registry_v1_receipt',rec)" in aligner

    reload_owner = text("pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html")
    cachelift = text("pmp-mount-registry-v1-cachelift-20260706b.js")
    assert "pmp-mount-registry-v1-cachelift-20260706b.js" in reload_owner
    assert "pmp-continuous-run-bank-order-frame-loader-v1.js" in cachelift
    assert audit["reload_owner_bridge"]["classification"].startswith("Compatibility bridge")

    diagnostics = text("pmp-diagnostics-owner-v1.js")
    tab = text("pmp-diagnostics-bottom-tab-forcer-v1.js")
    assert "{id:'mount_registry',title:'Mount Registry Status'" in diagnostics
    assert "mount=read('pmp_mount_registry_v1_receipt')" in diagnostics
    assert "host.appendChild(make(w,d,bank))" in tab
    assert "PMPDiagnosticsBottomTabForcerV1" in tab

    owner_registry = text("pmp-section-owner-registry-v1.js")
    helper_registry = text("pmp-helper-registry-v1.js")
    assert "scope:'active_path_atlas_only'" in owner_registry
    assert "id:'mount_registry_helper'" in helper_registry
    assert "parent_owner:'app_orchestrator_owner'" in helper_registry

    required_boundary = set(audit["compatibility_map"]["required_additive_boundary"])
    assert "A separately versioned mount-lifecycle contract and event API" in required_boundary
    assert "A compatibility facade for legacy atlas consumers" in required_boundary
    assert audit["effects"] == {
        "production_runtime_changed": False,
        "runtime_integrity_changed": False,
        "persisted_user_data_changed": False,
        "existing_system_evidence_changed": False,
        "live_observation_performed": False,
        "formal_proof_performed": False,
        "pr122_touched": False,
    }
    assert audit["next_step"]["id"] == "P5-U2"
    assert audit["next_step"]["requires_user_app_check"] is False
    print("PASS: P5-U1 current mount inventory, compatibility map, and Unit 2 contract boundary")


if __name__ == "__main__":
    main()
