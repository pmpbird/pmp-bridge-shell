#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_MAIN_COMMIT = "92069614248bce9aea81822ad6df1cf1a030f6a8"
MAP_PATH = "pmp-current-map-v12.json"
MANIFEST_PATH = "pmp-runtime-integrity-manifest-v1.json"
SAFE_AREA_PATH = "pmp-safe-area-surface-fill-v1.js"
FRAME_PATHS = [
    "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html",
    "pmp-current-inner-cleanbug-rgcontrols-v23.html",
    "pmp-current-inner-cleanbug-rgcontrols-v4.html",
    "pmp-current-inner-cleanbug-rgcontrols-v3.html",
]
HISTORIC_WORKING_POINT_PATHS = [
    "pmp-pass9-fix-001-bank-owner-slot-contract-20260710A.json",
    "pmp-pass9-fix-002-fill-continuous-run-owner-slot-20260710A.json",
    "pmp-restore-checkpoint-pass9-bank-control-diagnostics-stable-20260710A.json",
]
RELEVANT = re.compile(
    r"(?:bank|continuous|p15-continuous|resident-cr-status)",
    re.IGNORECASE,
)
SCRIPT_SRC = re.compile(r"<script[^>]+src=[\"']([^\"']+)", re.IGNORECASE)
CONST_STRING = re.compile(
    r"\b(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*[\"']([^\"']+)[\"']"
)
GLOBAL_EXPORT = re.compile(
    r"\b(?:window|top|w)\.([A-Za-z_$][A-Za-z0-9_$]*)\s*="
)

BANK_FACT_SOURCES = {
    "pmp-master-bank-inventory-router-v1.js",
    "pmp-master-bank-tab-v1.js",
    "pmp-bank-project-registry-v1.js",
    "pmp-bank-scoped-test-data-cleaner-v1.js",
    "pmp-bank-mode1-hide-unchecked-v1.js",
    "pmp-connections-bank-packet-delete-v1.js",
    "pmp-connections-bank-packet-name-v1.js",
}
CONTINUOUS_RUN_SOURCES = {
    "pmp-continuous-run-state-bank-v1.js",
    "pmp-continuous-run-dashboard-stable-v1.js",
    "pmp-p15-continuous-runner-stable-v1.js",
    "pmp-resident-continuous-run-status-reader-v1.js",
    "pmp-resident-cr-status-router-v1.js",
    "pmp-continuous-run-level-ui-scope-v1.js",
    "pmp-continuous-run-single-line-hold-v1.js",
    "pmp-continuous-run-bank-stable-status-owner-v1.js",
}
MIXED_BOUNDARY_SOURCES = {
    "pmp-continuous-run-bank-order-frame-loader-v1.js",
    "pmp-continuous-run-bank-transfer-store-v2.js",
    "pmp-continuous-run-bank-verify-receipt-fix-v1.js",
    "pmp-continuous-run-bank-zip-importer-v1.js",
    "pmp-continuous-run-bank-must-source-zip-v1.js",
    "pmp-bank-screen-owner-v1.js",
    "pmp-bank-owner-dependency-bridge-v1.js",
}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def payload(path: str) -> bytes:
    local = ROOT / path
    if local.is_file():
        return local.read_bytes()
    return git("show", f"HEAD:{path}")


def text(path: str) -> str:
    return payload(path).decode("utf-8", errors="replace")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def scripts(path: str) -> list[str]:
    return [match.split("?", 1)[0] for match in SCRIPT_SRC.findall(text(path))]


def storage_keys(source: str) -> list[str]:
    keys = {
        value
        for _name, value in CONST_STRING.findall(source)
        if re.search(r"(?:pmp|bank|run|receipt|manifest|state|store|inventory)", value, re.I)
        and not value.endswith((".js", ".json", ".html"))
    }
    keys.update(
        re.findall(
            r"(?:localStorage|sessionStorage)\.(?:getItem|setItem|removeItem)"
            r"\(\s*[\"']([^\"']+)",
            source,
        )
    )
    return sorted(keys)


def source_role(path: str) -> str:
    if path in MIXED_BOUNDARY_SOURCES:
        return "MIXED_BANK_CONTINUOUS_RUN_BOUNDARY"
    if path in BANK_FACT_SOURCES:
        return "BANK_FACT_OR_PERSISTENCE"
    if path in CONTINUOUS_RUN_SOURCES:
        return "CONTINUOUS_RUN_LIFECYCLE"
    if path.startswith("pmp-bug-bank-"):
        return "BUG_BANK_COMPATIBILITY"
    if path.startswith("pmp-helper-bank-"):
        return "HELPER_BANK_COMPATIBILITY"
    if "bank" in path:
        return "BANK_UI_OR_COMPATIBILITY"
    return "CONTINUOUS_RUN_UI_OR_COMPATIBILITY"


def main() -> None:
    current_map = json.loads(text(MAP_PATH))
    manifest = json.loads(text(MANIFEST_PATH))
    manifest_rows = {row["path"]: row for row in manifest["records"]}
    expected_frames = [
        current_map["runtime_chain"]["inner_v30"]["path"],
        current_map["runtime_chain"]["inner_v23"]["path"],
        current_map["runtime_chain"]["inner_v4"]["path"],
        current_map["runtime_chain"]["inner_v3"]["path"],
    ]
    assert expected_frames == FRAME_PATHS

    occurrences = []
    all_direct_scripts = []
    for frame in FRAME_PATHS:
        frame_scripts = scripts(frame)
        all_direct_scripts.extend(frame_scripts)
        for position, path in enumerate(frame_scripts, 1):
            if RELEVANT.search(path):
                occurrences.append(
                    {
                        "load_kind": "DIRECT_FRAME_SCRIPT",
                        "frame": frame,
                        "position": position,
                        "path": path,
                    }
                )

    safe_area = text(SAFE_AREA_PATH)
    dynamic_rows = []
    for name, source in CONST_STRING.findall(safe_area):
        if name.endswith("_SRC") and source.split("?", 1)[0].endswith(".js"):
            path = source.split("?", 1)[0]
            dynamic_rows.append({"constant": name, "path": path})
            if RELEVANT.search(path):
                occurrences.append(
                    {
                        "load_kind": "DYNAMIC_SAFE_AREA_DEPENDENCY",
                        "frame": "pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html",
                        "position": len(dynamic_rows),
                        "path": path,
                    }
                )

    counts = Counter(row["path"] for row in occurrences)
    unique_paths = sorted(counts)
    source_rows = []
    for path in unique_paths:
        data = payload(path)
        source = data.decode("utf-8", errors="replace")
        manifest_row = manifest_rows.get(path)
        source_rows.append(
            {
                "path": path,
                "role": source_role(path),
                "occurrences": counts[path],
                "bytes": len(data),
                "sha256": sha(data),
                "integrity_manifest_present": manifest_row is not None,
                "integrity_manifest_sha256_matches": bool(
                    manifest_row and manifest_row["sha256_hex"] == sha(data)
                ),
                "storage_get_calls": len(re.findall(r"\.getItem\s*\(", source)),
                "storage_set_calls": len(re.findall(r"\.setItem\s*\(", source)),
                "storage_remove_calls": len(re.findall(r"\.removeItem\s*\(", source)),
                "timeout_calls": len(re.findall(r"\bsetTimeout\s*\(", source)),
                "interval_calls": len(re.findall(r"\bsetInterval\s*\(", source)),
                "storage_keys": storage_keys(source),
                "global_exports": sorted(set(GLOBAL_EXPORT.findall(source))),
            }
        )

    historic = []
    for path in HISTORIC_WORKING_POINT_PATHS:
        data = json.loads(text(path))
        historic.append(
            {
                "path": path,
                "type": data["type"],
                "status": data["status"],
                "user_verified": data.get("user_verified"),
                "certification_status": data.get("certification_status"),
                "sha256": sha(payload(path)),
            }
        )

    duplicate_paths = [
        {"path": path, "occurrences": count}
        for path, count in sorted(counts.items())
        if count > 1
    ]
    storage_writers = [
        row["path"]
        for row in source_rows
        if row["storage_set_calls"] or row["storage_remove_calls"]
    ]
    intervals = [
        {"path": row["path"], "interval_calls": row["interval_calls"]}
        for row in source_rows
        if row["interval_calls"]
    ]

    conflicts = [
        {
            "id": "P9-I001-ACTIVE-TAB-CREATES-OWNERSHIP",
            "severity": "BLOCKS_EXPLICIT_OWNER_CONTRACT",
            "paths": ["pmp-master-bank-inventory-router-v1.js"],
            "fact": "The active inventory rule says the active tab or active system creates ownership.",
            "required_resolution": "P9-U2 must replace implicit tab/system ownership with exact Bank Owner grants and receipted cross-owner requests.",
        },
        {
            "id": "P9-I002-BANK-ROUTER-DELETE-EXPOSED",
            "severity": "PERSISTED_DATA_RISK",
            "paths": ["pmp-master-bank-inventory-router-v1.js"],
            "fact": "The active Bank router exposes recordDelete and directly rewrites the inventory.",
            "required_resolution": "P9-U2 must deny delete by default; P9-U3 may not migrate or delete persisted user data.",
        },
        {
            "id": "P9-I003-RUN-STATE-SELF-PERSISTS-AND-CLEARS",
            "severity": "CROSS_OWNER_PERSISTENCE",
            "paths": ["pmp-continuous-run-state-bank-v1.js"],
            "fact": "Continuous Run state writes three localStorage namespaces and exposes clearCurrentState and manualClear.",
            "required_resolution": "Continuous Run Owner must own lifecycle intent while Bank Owner exclusively authorizes durable fact writes and clear remains separately gated.",
        },
        {
            "id": "P9-I004-CONTINUOUS-OWNER-MISNAMED-BANK-SCREEN",
            "severity": "OWNER_IDENTITY_AMBIGUITY",
            "paths": ["pmp-bank-screen-owner-v1.js"],
            "fact": "PMPBankScreenOwnerV1 declares scope continuous_run_owner_slot_level1_level2, writes the project registry, and repeatedly scans the Bank DOM.",
            "required_resolution": "P9-U2 must name separate canonical owners; P9-U3 must retain compatibility without confusing Bank shell ownership with Continuous Run content ownership.",
        },
        {
            "id": "P9-I005-CROSS-FRAME-API-COPY-AND-SCAN",
            "severity": "UNRECEIPTED_CROSS_OWNER_CALL",
            "paths": [
                "pmp-safe-area-surface-fill-v1.js",
                "pmp-bank-owner-dependency-bridge-v1.js",
            ],
            "fact": "A repeated loader copies Bank APIs between same-origin frames and calls Bank scans without an exact operation-scoped owner request.",
            "required_resolution": "P9-U2 must define operation IDs, capabilities, request/receipt shape, timeout, cancellation, duplicate, and restart behavior.",
        },
        {
            "id": "P9-I006-DUPLICATE-ACTIVE-LOADS",
            "severity": "DUPLICATE_EXECUTION_RISK",
            "paths": [row["path"] for row in duplicate_paths],
            "fact": "Two Bank compatibility scripts are directly loaded in both inner v23 and inner v4.",
            "required_resolution": "P9-U3 must provide idempotent compatibility and P9-U4 must prove duplicate-load behavior.",
        },
        {
            "id": "P9-I007-REPEATING-DOM-PAINTERS",
            "severity": "FLICKER_AND-CONCURRENCY-RISK",
            "paths": [
                "pmp-bank-screen-owner-v1.js",
                "pmp-continuous-run-level-ui-scope-v1.js",
                "pmp-safe-area-surface-fill-v1.js",
            ],
            "fact": "Continuous Run placement and dependency exposure use recurring scans while older compatibility painters remain loaded.",
            "required_resolution": "P9-U3 must establish one owner per surface and event-driven idempotent reconciliation; P9-U4 must prove concurrent and cancelled runs cannot repaint or orphan state.",
        },
        {
            "id": "P9-I008-WORKING-POINT-NOT-CERTIFIED",
            "severity": "CLAIM-BOUNDARY",
            "paths": HISTORIC_WORKING_POINT_PATHS,
            "fact": "Existing Pass 9 fix records say IMPLEMENTED_NEEDS_VISUAL_TEST or PASS9_WORKING_POINT_NOT_CERTIFIED.",
            "required_resolution": "Treat them as historical working evidence only; certify against the current active chain and new P9-U1 through P9-U7 receipts.",
        },
        {
            "id": "P9-I009-NONCRYPTO-PERSISTENCE-HASHES",
            "severity": "INTEGRITY-WEAKNESS",
            "paths": [
                "pmp-continuous-run-state-bank-v1.js",
                "pmp-master-bank-inventory-router-v1.js",
                "pmp-bank-screen-owner-v1.js",
            ],
            "fact": "Active persisted state and registry paths use FNV-style short hashes or no sealed digest chain.",
            "required_resolution": "P9-U2 must define SHA-256 receipts and atomic restore validation without migrating current user data.",
        },
    ]

    result = {
        "type": "PMP_PASS9_UNIT1_BANK_CONTINUOUS_RUN_INVENTORY_RESULT_V1",
        "version": "1.0.0",
        "repository_commit": BASE_MAIN_COMMIT,
        "active_chain": {
            "map": MAP_PATH,
            "frames": FRAME_PATHS,
            "direct_script_occurrences": len(all_direct_scripts),
            "dynamic_safe_area_dependencies": dynamic_rows,
        },
        "inventory": {
            "relevant_occurrences": len(occurrences),
            "unique_relevant_sources": len(source_rows),
            "duplicate_relevant_sources": duplicate_paths,
            "storage_writer_sources": storage_writers,
            "interval_sources": intervals,
            "role_counts": dict(sorted(Counter(row["role"] for row in source_rows).items())),
            "sources": source_rows,
            "historic_working_points": historic,
        },
        "conflicts": conflicts,
        "boundaries": {
            "bank_owner": "bank_screen_owner",
            "bank_section": "bank",
            "continuous_run_owner": "continuous_run_level_owner",
            "continuous_run_section": "continuous_run",
            "cross_delegation": "FORBIDDEN",
            "persisted_data_mutation_in_p9_u1": "FORBIDDEN",
            "production_behavior_change_in_p9_u1": "FORBIDDEN",
            "actual_repair_target": "P9-U3",
        },
        "effects": {
            "production_files_changed": False,
            "browser_launched": False,
            "network_requests": False,
            "storage_writes": False,
            "bank_mutations": False,
            "persisted_user_data_changed": False,
            "live_observation_performed": False,
            "formal_proof_performed": False,
        },
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if len(sys.argv) == 3 and sys.argv[1] == "--output":
        Path(sys.argv[2]).write_text(encoded)
    elif len(sys.argv) == 1:
        sys.stdout.write(encoded)
    else:
        raise SystemExit("usage: run_pass9_unit1_bank_continuous_run_inventory_v1.py [--output PATH]")


if __name__ == "__main__":
    main()
