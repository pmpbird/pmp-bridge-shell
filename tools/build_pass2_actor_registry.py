#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from build_pass2_authority_inventory import (
    EXECUTABLE_CLASSES,
    actor_classes,
    capabilities,
    infer_owner,
    infer_version,
    stop_condition,
)

P2B_NEW_ACTORS = {
    "pmp-pass2-actor-authorization-gate-v1.js",
    "audit/pass2/p2b-forbidden-action-fixture.html",
    "audit/pass2/p2b-registered-marker.js",
}
ACTIVE_INNER_INITIAL_ACTORS = [
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
GLOBAL_FORBIDDEN = [
    "cache.delete",
    "code.eval",
    "indexeddb.delete",
    "service_worker.register",
    "storage.local.clear",
    "storage.session.clear",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text("utf-8"))


def recursive_paths(value: Any, out: dict[str, list[str]], breadcrumb: str = "map") -> None:
    if isinstance(value, dict):
        if isinstance(value.get("path"), str):
            out[value["path"]].append(breadcrumb)
        for key, child in value.items():
            recursive_paths(child, out, f"{breadcrumb}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            recursive_paths(child, out, f"{breadcrumb}[{index}]")


def map_capabilities(signals: list[str]) -> list[str]:
    source = set(signals)
    result: set[str] = set()
    if "dom_write" in source:
        result.add("dom.write")
    if "local_storage_write" in source:
        result.add("storage.local.write")
    if "local_storage_delete" in source:
        result.add("storage.local.delete")
    if "session_storage_write" in source:
        result.update({"storage.session.write", "storage.session.delete"})
    if "indexeddb" in source:
        result.add("indexeddb.open")
    if "cache_api" in source:
        result.add("cache.open")
    if "network_fetch" in source:
        result.add("network.fetch")
    if "navigation" in source:
        result.update({"navigation.frame", "navigation.window"})
    if "timer" in source:
        result.add("timer.once")
    if "recurring_timer" in source:
        result.add("timer.recurring")
    if "event_listener" in source:
        result.add("event.listen")
    if "observer" in source:
        result.add("observer.observe")
    if "dynamic_script_injection" in source:
        result.add("script.load")
    if "frame_access" in source:
        result.add("gate.extend_window")
    return sorted(result)


def row_for(root: Path, path: str, execution_class: str, map_roles: list[str], policy_source: str) -> dict[str, Any]:
    data = (root / path).read_bytes()
    text = data.decode("utf-8", errors="replace")
    signals = capabilities(text)
    classes = actor_classes(path, text, map_roles)
    allowed = set(map_capabilities(signals))

    explicit: dict[str, set[str]] = {
        "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html": {
            "script.load", "network.fetch", "navigation.frame", "navigation.window", "gate.extend_window"
        },
        "pmp-app-orchestrator-v1.js": {"script.load"},
        "pmp-safe-writer-current-return-fix-v1.js": {"script.load", "navigation.window", "gate.extend_window"},
        "pmp-continuous-run-bank-order-frame-loader-v1.js": {"script.load", "gate.extend_window"},
        "pmp-bug-watch-passive-capture-v1.js": {"gate.extend_window"},
        "audit/pass2/p2b-forbidden-action-fixture.html": {
            "dom.write", "storage.local.write", "storage.local.delete", "timer.once", "timer.recurring",
            "event.listen", "script.load", "indexeddb.open", "cache.open", "cache.write",
            "network.fetch", "navigation.frame", "navigation.window"
        },
    }
    allowed.update(explicit.get(path, set()))
    allowed.difference_update(GLOBAL_FORBIDDEN)

    if path == "pmp-pass2-actor-authorization-gate-v1.js":
        classes = ["pass2_authority_gate"]
        allowed = set()
    elif path == "audit/pass2/p2b-forbidden-action-fixture.html":
        classes = ["p2b_adversarial_fixture"]
    elif path == "audit/pass2/p2b-registered-marker.js":
        classes = ["p2b_registered_fixture_actor"]

    return {
        "id": path,
        "path": path,
        "sha256": sha256(data),
        "git_blob_sha": git_blob(data),
        "bytes": len(data),
        "execution_class": execution_class,
        "owner_signal": infer_owner(path, text),
        "version_signal": infer_version(text),
        "current_map_roles": sorted(map_roles),
        "actor_classes": sorted(set(classes)),
        "capabilities": sorted(signals),
        "allowed_capabilities": sorted(allowed),
        "activation_phase": (
            "p2b_gate_bootstrap" if path == "pmp-pass2-actor-authorization-gate-v1.js"
            else "test_only" if path.startswith("audit/pass2/p2b-")
            else "bootstrap_or_route" if map_roles or any(
                item in classes for item in ["root_bootstrap", "route_guardian", "reload_owner"]
            ) else "post_entry_or_conditional"
        ),
        "stop_condition": stop_condition(set(signals), text),
        "source_identity": "runtime_manifest_exact_sha256_and_current_git_blob",
        "loadable": execution_class == "EXECUTABLE_SCRIPT" and path != "pmp-pass2-actor-authorization-gate-v1.js",
        "policy_source": policy_source,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("pmp-pass2-actor-authority-registry-v1.json"))
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = load_json(root / "pmp-runtime-integrity-manifest-v1.json")
    current_map = load_json(root / "pmp-current-map-v12.json")
    map_index: dict[str, list[str]] = defaultdict(list)
    recursive_paths(current_map, map_index)

    actors: list[dict[str, Any]] = []
    base_paths: set[str] = set()
    for record in manifest["records"]:
        path = record["path"]
        if record["execution_class"] not in EXECUTABLE_CLASSES or path in P2B_NEW_ACTORS:
            continue
        if not (root / path).is_file():
            raise SystemExit(f"Protected executable source missing: {path}")
        base_paths.add(path)
        actors.append(row_for(root, path, record["execution_class"], map_index.get(path, []), "CURRENT_A003_EXECUTABLE_SET_MAPPED_TO_P2B"))

    for path in sorted(P2B_NEW_ACTORS):
        source = root / path
        if not source.is_file():
            raise SystemExit(f"P2-B actor missing: {path}")
        execution_class = "EXECUTABLE_SCRIPT" if source.suffix.lower() == ".js" else "EXECUTABLE_DOCUMENT"
        actors.append(row_for(root, path, execution_class, map_index.get(path, []), "P2B_EXPLICIT_NEW_ACTOR_POLICY"))

    actors.sort(key=lambda row: row["path"])
    paths = [row["path"] for row in actors]
    if len(paths) != len(set(paths)):
        raise SystemExit("Duplicate actor path in generated registry")
    if len(base_paths) != 576:
        raise SystemExit(f"Expected 576 P2-A executable actors, found {len(base_paths)}")
    if len(actors) != 579:
        raise SystemExit(f"Expected 579 P2-B actors, found {len(actors)}")

    registry = {
        "type": "PMP_PASS2_ACTOR_AUTHORITY_REGISTRY_V1",
        "version": "1.0.0-p2b-active-current-runtime-plus-fixtures",
        "default_policy": "FAIL_CLOSED",
        "source_inventory": "PMP_PASS2_P2A_ACTIVE_ACTOR_INVENTORY_V1_RECONSTRUCTED_FROM_SEALED_A003_SET",
        "source_main_commit": "c767844d53b4b393928170387b6f988e49fe1fc6",
        "runtime_source_baseline_commit": "e7ba1b9384303abbbc67d3e9b0522e51bec65493",
        "identity_rule": "An actor may execute only when its path is registered and current bytes match the exact SHA-256 in both this registry and the sealed A-003 manifest.",
        "authorization_rule": "Protected side effects are blocked before native execution unless the current exact-source actor declares the required capability.",
        "global_forbidden_capabilities": GLOBAL_FORBIDDEN,
        "pass_boundary": {"overall_pass": "Pass 2", "phase": "P2-B", "pass2_complete": False, "pass3_started": False},
        "counts": {
            "p2a_actor_candidates": len(base_paths),
            "new_p2b_executable_actors": len(P2B_NEW_ACTORS),
            "registered_actors": len(actors),
            "loadable_scripts": sum(1 for row in actors if row["loadable"]),
            "nonloadable_documents_or_gate": sum(1 for row in actors if not row["loadable"]),
        },
        "active_inner_initial_actor_paths": ACTIVE_INNER_INITIAL_ACTORS,
        "actors": actors,
    }
    args.output.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", "utf-8")
    print(json.dumps({"status": "PASS", "output": str(args.output), "counts": registry["counts"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
