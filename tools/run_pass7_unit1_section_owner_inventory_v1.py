#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = "pmp-section-owner-registry-v1.js"
FOUNDATION = "pmp-owner-diagnostics-foundation-v1.js"
DIAGNOSTICS = "pmp-diagnostics-owner-v1.js"
ORCHESTRATOR = "pmp-app-orchestrator-v1.js"
MOUNT_RUNTIME = "pmp-mount-lifecycle-runtime-v1.js"
RESULT_TYPE = "PMP_PASS7_SECTION_OWNER_UNIT1_INVENTORY_RESULT_V1"
VERSION = "1.0.0"

DEPENDENCIES = {
    "app_orchestrator_owner": {
        "section": "app_orchestrator",
        "source_candidates": ["pmp-app-orchestrator-v1.js"],
        "lifecycle_dependencies": [
            "mount_registry_owner",
            "diagnostics_owner",
        ],
        "consumers": ["boot_runtime", "diagnostics_owner"],
    },
    "reload_current_owner": {
        "section": "current_reload",
        "source_candidates": [
            "pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html"
        ],
        "lifecycle_dependencies": ["app_orchestrator_owner"],
        "consumers": ["route_guardian", "current_map"],
    },
    "mount_registry_owner": {
        "section": "mount_registry",
        "source_candidates": [
            "pmp-mount-registry-v1.js",
            "pmp-mount-lifecycle-runtime-v1.js",
        ],
        "lifecycle_dependencies": ["app_orchestrator_owner"],
        "consumers": ["diagnostics_owner", "section_owners"],
    },
    "bank_screen_owner": {
        "section": "bank",
        "source_candidates": [
            "pmp-bank-screen-owner-v1.js",
            "pmp-bank-owner-dependency-bridge-v1.js",
        ],
        "lifecycle_dependencies": [
            "mount_registry_owner",
            "continuous_run_level_owner",
        ],
        "consumers": ["bank_ui", "continuous_run"],
    },
    "continuous_run_level_owner": {
        "section": "continuous_run",
        "source_candidates": [
            "pmp-continuous-run-bank-display-owner-v1.js",
            "pmp-continuous-run-bank-stable-status-owner-v1.js",
        ],
        "lifecycle_dependencies": ["bank_screen_owner", "resident_30b_owner"],
        "consumers": ["continuous_run_ui", "diagnostics_owner"],
    },
    "resident_30b_owner": {
        "section": "resident_30b",
        "source_candidates": [],
        "lifecycle_dependencies": ["continuous_run_level_owner"],
        "consumers": ["continuous_run_level_owner"],
    },
    "source_gate_owner": {
        "section": "source_gate",
        "source_candidates": [],
        "lifecycle_dependencies": ["app_orchestrator_owner"],
        "consumers": ["zip_reader_helper", "text_reader_helper", "reference_gate_helper"],
    },
    "diagnostics_owner": {
        "section": "diagnostics",
        "source_candidates": [
            "pmp-diagnostics-owner-v1.js",
            "pmp-owner-diagnostics-foundation-v1.js",
        ],
        "lifecycle_dependencies": [
            "mount_registry_owner",
            "app_orchestrator_owner",
        ],
        "consumers": ["operator", "app_orchestrator_owner"],
    },
}


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def read_tracked(relative: str) -> str:
    path = ROOT / relative
    if path.is_file():
        return path.read_text()
    return git("show", f"HEAD:{relative}")


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def canonical(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: canonical(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [canonical(item) for item in value]
    return value


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(canonical(value), separators=(",", ":")).encode()
    ).hexdigest()


def parse_owners(source: str) -> list[dict[str, str]]:
    block_match = re.search(r"const OWNERS=\[(?P<body>.*?)\];", source, re.S)
    if not block_match:
        raise AssertionError("section owner registry OWNERS declaration missing")
    rows = []
    for match in re.finditer(
        r"\{id:'(?P<id>[^']+)',name:'(?P<name>[^']+)',"
        r"status:'(?P<status>[^']+)',scope:'(?P<scope>[^']+)'\}",
        block_match.group("body"),
    ):
        rows.append(match.groupdict())
    return rows


def root_owner_sources() -> list[str]:
    names = git("ls-tree", "-r", "--name-only", "HEAD").splitlines()
    suffixes = {".js", ".json", ".html"}
    return sorted(
        name
        for name in names
        if "/" not in name
        and "owner" in name.lower()
        and Path(name).suffix.lower() in suffixes
    )


def build_inventory() -> dict[str, Any]:
    sources = {
        REGISTRY: read_tracked(REGISTRY),
        FOUNDATION: read_tracked(FOUNDATION),
        DIAGNOSTICS: read_tracked(DIAGNOSTICS),
        ORCHESTRATOR: read_tracked(ORCHESTRATOR),
        MOUNT_RUNTIME: read_tracked(MOUNT_RUNTIME),
    }
    owners = parse_owners(sources[REGISTRY])
    owner_ids = [row["id"] for row in owners]
    if owner_ids != list(DEPENDENCIES):
        raise AssertionError((owner_ids, list(DEPENDENCIES)))

    rows = []
    for owner in owners:
        dependency = DEPENDENCIES[owner["id"]]
        rows.append(
            {
                **owner,
                **dependency,
                "source_candidate_count": len(dependency["source_candidates"]),
                "binding_status": (
                    "DECLARED_WITH_SOURCE_CANDIDATE"
                    if dependency["source_candidates"]
                    else "DECLARED_WITHOUT_DEDICATED_SOURCE_CANDIDATE"
                ),
            }
        )

    owner_sources = root_owner_sources()
    registered_tokens = {
        candidate
        for dependency in DEPENDENCIES.values()
        for candidate in dependency["source_candidates"]
    }
    unregistered_named = sorted(set(owner_sources) - registered_tokens)
    observations = [
        {
            "id": "P7-U1-OBS-001",
            "claim_type": "OBSERVED",
            "fact": "The section registry declares exactly eight owner identities.",
            "evidence_path": REGISTRY,
            "evidence_sha256": sha_text(sources[REGISTRY]),
        },
        {
            "id": "P7-U1-OBS-002",
            "claim_type": "OBSERVED",
            "fact": "The registry boot snapshot hard-codes only mount_registry_owner as present.",
            "evidence_path": REGISTRY,
            "evidence_sha256": sha_text(sources[REGISTRY]),
        },
        {
            "id": "P7-U1-OBS-003",
            "claim_type": "OBSERVED",
            "fact": "The legacy owner diagnostics foundation models every declared owner as present.",
            "evidence_path": FOUNDATION,
            "evidence_sha256": sha_text(sources[FOUNDATION]),
        },
        {
            "id": "P7-U1-OBS-004",
            "claim_type": "OBSERVED",
            "fact": "Diagnostics explicitly identifies diagnostics, bottom-tab, and mount-registry ownership boundaries.",
            "evidence_path": DIAGNOSTICS,
            "evidence_sha256": sha_text(sources[DIAGNOSTICS]),
        },
        {
            "id": "P7-U1-OBS-005",
            "claim_type": "OBSERVED",
            "fact": "The app orchestrator loads diagnostics and mount-registry diagnostics as background dependencies.",
            "evidence_path": ORCHESTRATOR,
            "evidence_sha256": sha_text(sources[ORCHESTRATOR]),
        },
        {
            "id": "P7-U1-OBS-006",
            "claim_type": "OBSERVED",
            "fact": "Mount lifecycle runtime names mount_registry_owner as its registry owner.",
            "evidence_path": MOUNT_RUNTIME,
            "evidence_sha256": sha_text(sources[MOUNT_RUNTIME]),
        },
    ]
    inferences = [
        {
            "id": "P7-U1-INF-001",
            "claim_type": "INFERRED",
            "conclusion": "Presence truth is not yet consistent between the boot registry and legacy diagnostics foundation.",
            "basis_observation_ids": ["P7-U1-OBS-002", "P7-U1-OBS-003"],
        },
        {
            "id": "P7-U1-INF-002",
            "claim_type": "INFERRED",
            "conclusion": "Owner-named files do not by themselves prove registry membership or authority.",
            "basis_observation_ids": ["P7-U1-OBS-001", "P7-U1-OBS-004"],
        },
        {
            "id": "P7-U1-INF-003",
            "claim_type": "INFERRED",
            "conclusion": "Bank and Continuous Run require an explicit contract before their overlapping source candidates can be treated as separate authority.",
            "basis_observation_ids": ["P7-U1-OBS-001", "P7-U1-OBS-004"],
        },
    ]
    unresolved = [
        {
            "id": "P7-U1-UNRESOLVED-001",
            "kind": "CONTRADICTORY_PRESENCE_MODELS",
            "owners": owner_ids,
            "blocking_effect": "Do not treat either snapshot as complete runtime truth.",
        },
        {
            "id": "P7-U1-UNRESOLVED-002",
            "kind": "NO_DEDICATED_SOURCE_CANDIDATE",
            "owners": [
                row["id"]
                for row in rows
                if row["source_candidate_count"] == 0
            ],
            "blocking_effect": "Do not infer implementation authority from declaration alone.",
        },
        {
            "id": "P7-U1-UNRESOLVED-003",
            "kind": "UNREGISTERED_OWNER_NAMED_SOURCES",
            "source_count": len(unregistered_named),
            "sources": unregistered_named,
            "blocking_effect": "Do not auto-register or grant authority based on filenames.",
        },
        {
            "id": "P7-U1-UNRESOLVED-004",
            "kind": "BANK_CONTINUOUS_RUN_OVERLAP",
            "owners": ["bank_screen_owner", "continuous_run_level_owner"],
            "blocking_effect": "Defer authority split to the documented Bank/Continuous Run pass.",
        },
    ]
    result = {
        "type": RESULT_TYPE,
        "version": VERSION,
        "status": "PASS",
        "registry": {
            "path": REGISTRY,
            "sha256": sha_text(sources[REGISTRY]),
            "declared_owner_count": len(rows),
        },
        "owners": rows,
        "owner_named_sources": owner_sources,
        "unregistered_owner_named_sources": unregistered_named,
        "observed_facts": observations,
        "inferred_conclusions": inferences,
        "unresolved_cases": unresolved,
        "summary": {
            "owners_declared": len(rows),
            "sections_inventory": len({row["section"] for row in rows}),
            "owners_with_source_candidates": sum(
                row["source_candidate_count"] > 0 for row in rows
            ),
            "owners_without_source_candidates": sum(
                row["source_candidate_count"] == 0 for row in rows
            ),
            "owner_named_root_sources": len(owner_sources),
            "unregistered_owner_named_sources": len(unregistered_named),
            "observed_facts": len(observations),
            "inferred_conclusions": len(inferences),
            "unresolved_cases": len(unresolved),
        },
        "effects": {
            "production_files_changed": False,
            "runtime_integrity_changed": False,
            "browser_launched": False,
            "network_requests": False,
            "storage_writes": False,
            "route_changes": False,
            "repairs": False,
            "live_observation_performed": False,
            "formal_proof_performed": False,
            "persisted_user_data_changed": False,
            "storage_migration_performed": False,
        },
        "claim_ceiling": "Read-only source inventory and bounded inferences only. No owner is registered, activated, delegated, or granted authority.",
    }
    result["result_sha256"] = digest(result)
    return result


def verify_result_hash(result: dict[str, Any]) -> bool:
    copy = json.loads(json.dumps(result))
    expected = copy.pop("result_sha256", None)
    return isinstance(expected, str) and digest(copy) == expected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    result = build_inventory()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
