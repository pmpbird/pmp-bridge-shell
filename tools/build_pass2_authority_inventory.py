#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

EXECUTABLE_CLASSES = {"EXECUTABLE_SCRIPT", "EXECUTABLE_DOCUMENT"}

CAPABILITY_PATTERNS = {
    "dom_write": [
        r"\.innerHTML\s*=", r"\.outerHTML\s*=", r"\.textContent\s*=",
        r"\.appendChild\s*\(", r"\.insertAdjacentHTML\s*\(", r"\.replaceChildren\s*\(",
        r"document\.write\s*\(", r"\.removeChild\s*\(", r"\.remove\s*\(",
    ],
    "local_storage_read": [r"localStorage\.getItem\s*\("],
    "local_storage_write": [r"localStorage\.setItem\s*\("],
    "local_storage_delete": [r"localStorage\.removeItem\s*\(", r"localStorage\.clear\s*\("],
    "session_storage_write": [r"sessionStorage\.setItem\s*\(", r"sessionStorage\.removeItem\s*\(", r"sessionStorage\.clear\s*\("],
    "indexeddb": [r"\bindexedDB\b", r"\bIDBDatabase\b", r"\bIDBObjectStore\b"],
    "indexeddb_delete": [r"indexedDB\.deleteDatabase\s*\("],
    "cache_api": [r"\bcaches\.(?:open|match|keys|has)\s*\(", r"\bCacheStorage\b"],
    "cache_delete": [r"\bcaches\.delete\s*\(", r"\.delete\s*\([^)]*\)"],
    "navigation": [r"location\.(?:href|replace|assign)\b", r"window\.open\s*\(", r"\.src\s*="],
    "network_fetch": [r"\bfetch\s*\(", r"\bXMLHttpRequest\b", r"\bWebSocket\b"],
    "service_worker": [r"serviceWorker\.(?:register|getRegistration|getRegistrations)\s*\(", r"\bServiceWorkerGlobalScope\b"],
    "worker": [r"\bnew\s+(?:Shared)?Worker\s*\(", r"\bimportScripts\s*\("],
    "timer": [r"\bsetTimeout\s*\(", r"\bsetInterval\s*\("],
    "recurring_timer": [r"\bsetInterval\s*\("],
    "timer_stop": [r"\bclearInterval\s*\(", r"\bclearTimeout\s*\("],
    "observer": [r"\b(?:Mutation|Resize|Intersection)Observer\s*\("],
    "observer_stop": [r"\.disconnect\s*\("],
    "event_listener": [r"\.addEventListener\s*\("],
    "frame_access": [r"\biframe\b", r"\bframe\b", r"contentWindow", r"contentDocument"],
    "dynamic_script_injection": [
        r"createElement\s*\(\s*['\"]script['\"]\s*\)", r"\.src\s*=\s*[^;]+\.js",
        r"appendChild\s*\(\s*script\s*\)",
    ],
    "eval_like": [r"\beval\s*\(", r"\bnew\s+Function\s*\("],
    "migration_or_cleanup": [r"\bmigrat(?:e|ion)\b", r"\bcleanup\b", r"\bcleaner\b", r"\breset\b"],
    "destructive_language": [r"\bdelete\b", r"\bclear\b", r"\bpurge\b", r"\bremove\b", r"\boverwrite\b"],
    "bug_capture": [r"\bbug\b", r"\berror\b", r"unhandledrejection", r"Active Bugs Found"],
    "receipt_write": [r"\breceipt\b", r"RECEIPT"],
}

CLASS_RULES = {
    "root_bootstrap": ["pmp-app-current.html"],
    "route_guardian": ["route-guardian", "current-map", "route-resolver", "reload-world", "screen-pointer"],
    "reload_owner": ["reload-owner"],
    "app_orchestrator": ["app-orchestrator"],
    "nested_runtime": ["current-inner", "home-single"],
    "service_worker_cache": ["service-worker", "cache-governor", "integrity-service-worker"],
    "diagnostics": ["diagnostic", "diagnostics", "probe", "test-result", "audit"],
    "bug_watch": ["bug-watch", "active-bug", "bug-bank"],
    "mount_registry": ["mount-registry", "registry"],
    "owner_actor": ["owner"],
    "helper_actor": ["helper", "adapter", "bridge", "fix", "guard"],
    "migration_cleanup": ["migration", "migrate", "cleanup", "cleaner", "reset", "purge"],
    "rescue_recovery": ["rescue", "recovery", "last-good", "emergency", "safe-writer", "code-safety"],
    "bank_actor": ["bank", "continuous-run"],
    "automation_actor": ["automation", "automated-plan"],
}

OWNER_RE = re.compile(r"\b(?:const|let|var)\s+OWNER\s*=\s*['\"]([^'\"]+)['\"]")
VERSION_RE = re.compile(r"\b(?:const|let|var)\s+V(?:ERSION)?\s*=\s*['\"]([^'\"]+)['\"]")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def recursive_paths(value: Any, out: dict[str, list[str]], breadcrumb: str = "map") -> None:
    if isinstance(value, dict):
        if isinstance(value.get("path"), str):
            out[value["path"]].append(breadcrumb)
        for key, child in value.items():
            recursive_paths(child, out, f"{breadcrumb}.{key}")
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            recursive_paths(child, out, f"{breadcrumb}[{idx}]")


def infer_owner(path: str, text: str) -> str:
    match = OWNER_RE.search(text)
    return match.group(1) if match else Path(path).stem


def infer_version(text: str) -> str | None:
    match = VERSION_RE.search(text)
    return match.group(1) if match else None


def capabilities(text: str) -> list[str]:
    found = []
    for name, patterns in CAPABILITY_PATTERNS.items():
        if any(re.search(pattern, text, re.I) for pattern in patterns):
            found.append(name)
    return found


def actor_classes(path: str, text: str, map_roles: list[str]) -> list[str]:
    lower = path.lower()
    classes = []
    for name, needles in CLASS_RULES.items():
        if any(needle in lower for needle in needles):
            classes.append(name)
    if map_roles:
        classes.append("current_map_declared")
    if "setinterval" in text.lower() or "mutationobserver" in text.lower():
        classes.append("recurring_actor")
    if not classes:
        classes.append("unclassified_executable")
    return sorted(set(classes))


def stop_condition(caps: set[str], text: str) -> str:
    if not ({"recurring_timer", "observer"} & caps):
        return "not_recurring"
    if "timer_stop" in caps or "observer_stop" in caps or re.search(r"\bAbortController\b|\bonce\s*:\s*true", text):
        return "static_stop_signal_detected"
    return "no_static_stop_or_handoff_detected"


def load_a001_candidates(repo: Path) -> dict[str, str]:
    manifest = load_json(repo / "audit/pmp-active-source-identity-manifest-v1.json")
    rows: list[list[Any]] = []
    for entry in manifest["identity_shards"]:
        rows.extend(load_json(repo / entry["path"])["rows"])
    result = {row[0]: row[1] for row in rows}
    supplement = load_json(repo / "audit/a001-supplements/a001-a002-route-authority-supplement-v1.json")
    for record in supplement["records"]:
        result[record["path"]] = record["git_blob_sha"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("dist/pass2-p2a"))
    args = parser.parse_args()
    repo = args.repo.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    runtime = load_json(repo / "pmp-runtime-integrity-manifest-v1.json")
    current_map = load_json(repo / "pmp-current-map-v12.json")
    map_index: dict[str, list[str]] = defaultdict(list)
    recursive_paths(current_map, map_index)

    inventory = []
    capability_counts = Counter()
    class_counts = Counter()
    stop_counts = Counter()
    integrity_errors = []

    for record in runtime["records"]:
        path = record["path"]
        if record["execution_class"] not in EXECUTABLE_CLASSES:
            continue
        source = repo / path
        if not source.is_file():
            integrity_errors.append({"path": path, "error": "manifest_source_missing"})
            continue
        data = source.read_bytes()
        actual = sha256(data)
        if actual != record["sha256_hex"]:
            integrity_errors.append({"path": path, "error": "sha256_mismatch", "expected": record["sha256_hex"], "actual": actual})
        text = data.decode("utf-8", errors="replace")
        caps = set(capabilities(text))
        classes = actor_classes(path, text, map_index.get(path, []))
        stop = stop_condition(caps, text)
        inventory.append({
            "path": path,
            "git_blob_sha": record["git_blob_sha"],
            "sha256": record["sha256_hex"],
            "bytes": record["bytes"],
            "execution_class": record["execution_class"],
            "owner_signal": infer_owner(path, text),
            "version_signal": infer_version(text),
            "current_map_roles": sorted(map_index.get(path, [])),
            "actor_classes": classes,
            "capabilities": sorted(caps),
            "activation_phase": "bootstrap_or_route" if map_index.get(path) or any(c in classes for c in ["root_bootstrap", "route_guardian", "reload_owner"]) else "post_entry_or_conditional",
            "stop_condition": stop,
            "source_identity": "runtime_manifest_exact_sha256",
        })
        capability_counts.update(caps)
        class_counts.update(classes)
        stop_counts.update([stop])

    a001 = load_a001_candidates(repo)
    runtime_by_path = {record["path"]: record for record in runtime["records"]}
    reconciliation = []
    reconciliation_counts = Counter()
    for path, old_blob in sorted(a001.items()):
        current = runtime_by_path.get(path)
        if current is None:
            state, current_blob = "not_in_runtime_manifest", None
        elif current["git_blob_sha"] == old_blob:
            state, current_blob = "same_blob", current["git_blob_sha"]
        else:
            state, current_blob = "changed_blob", current["git_blob_sha"]
        reconciliation_counts[state] += 1
        reconciliation.append({"path": path, "a001_or_supplement_blob": old_blob, "current_runtime_blob": current_blob, "state": state})

    authority_text = (repo / "pmp-authority-rules-v1.js").read_text(encoding="utf-8")
    bug_text = (repo / "pmp-bug-watch-passive-capture-v1.js").read_text(encoding="utf-8")
    freeze = load_json(repo / "pmp-pass2-freeze-receipt-v1.json")
    blockers = [
        {
            "id": "P2-B01", "severity": "critical",
            "finding": "Authority rules are passive descriptions, not a pre-side-effect enforcement gate.",
            "evidence": {"path": "pmp-authority-rules-v1.js", "signals": ["MODE='passive_authority_map_only'", "report.passive_only=true", "No runtime registration/block/quarantine API"]},
            "required_repair": "Create one exact-source actor registration and authorization gate that blocks unregistered or forbidden actions before side effects."
        },
        {
            "id": "P2-B02", "severity": "critical",
            "finding": "The historical Pass 2 freeze was active-path-only and cannot certify the full current actor set.",
            "evidence": {"path": "pmp-pass2-freeze-receipt-v1.json", "scope": freeze.get("scope"), "status": freeze.get("status"), "frozen_route_uses_obsolete_map": "pmp-current-map-v10.json" in freeze.get("frozen_support_files", [])},
            "required_repair": "Replace the old freeze with an exact-current-main whole-active-set authority receipt."
        },
        {
            "id": "P2-B03", "severity": "high",
            "finding": "Bug Watch overwrites one receipt key instead of preserving an append-only event/receipt history.",
            "evidence": {"path": "pmp-bug-watch-passive-capture-v1.js", "single_receipt_key": "pmp_bug_watch_passive_capture_v1_receipt", "set_item_receipt_present": "save(RECEIPT" in bug_text},
            "required_repair": "Use an append-only or history-preserving Bug Watch receipt ledger with immutable lineage."
        },
        {
            "id": "P2-B04", "severity": "high",
            "finding": "Bug Watch is a recurring actor with no static stop, expiry, or formal handoff condition.",
            "evidence": {"path": "pmp-bug-watch-passive-capture-v1.js", "set_interval_present": "setInterval(" in bug_text, "clear_interval_present": "clearInterval(" in bug_text},
            "required_repair": "Add activation phase, expiry/handoff, stop receipt, and owner-controlled dispatch."
        },
        {
            "id": "P2-B05", "severity": "critical",
            "finding": "No runtime injection allowlist or unknown-actor pre-side-effect quarantine is proven by the old Pass 2 files.",
            "evidence": {"authority_file": "pmp-authority-rules-v1.js", "dynamic_actor_registration_api_present": "registerActor" in authority_text or "register_actor" in authority_text, "quarantine_api_present": "quarantine" in authority_text.lower()},
            "required_repair": "Enforce declared actor identity, source digest, phase, owner, capabilities, stop condition, and quarantine before execution/action."
        },
    ]

    inventory_obj = {
        "type": "PMP_PASS2_P2A_ACTIVE_ACTOR_INVENTORY_V1",
        "status": "BASELINE_CENSUS_COMPLETE_NOT_YET_ENFORCED",
        "base": {
            "repository": runtime["repository"],
            "main_commit": "e7ba1b9384303abbbc67d3e9b0522e51bec65493",
            "pass1_receipt": "PMP-APP-ORCH-PASS1-253111b7-CLOSED-001",
            "runtime_manifest_sha256": sha256((repo / "pmp-runtime-integrity-manifest-v1.json").read_bytes()),
            "runtime_source_set_sha256": runtime["runtime_source_set_sha256"],
        },
        "counts": {
            "protected_runtime_records": len(runtime["records"]),
            "executable_actor_candidates": len(inventory),
            "runtime_data_records": sum(1 for record in runtime["records"] if record["execution_class"] == "RUNTIME_DATA"),
            "current_map_declared_paths": len(map_index),
            "integrity_errors": len(integrity_errors),
        },
        "class_counts": dict(sorted(class_counts.items())),
        "capability_counts": dict(sorted(capability_counts.items())),
        "stop_condition_counts": dict(sorted(stop_counts.items())),
        "integrity_errors": integrity_errors,
        "actors": sorted(inventory, key=lambda row: row["path"]),
    }
    reconciliation_obj = {
        "type": "PMP_PASS2_P2A_SOURCE_RECONCILIATION_V1",
        "status": "COMPLETE",
        "base_main_commit": "e7ba1b9384303abbbc67d3e9b0522e51bec65493",
        "a001_plus_supplement_candidates": len(a001),
        "counts": dict(sorted(reconciliation_counts.items())),
        "rows": reconciliation,
        "meaning": "A-001 and its A-002 supplement are historical source-identity inputs. Current Pass 2 authority must use the exact A-003 runtime manifest identities for every active actor and must not inherit old blobs as current.",
    }
    blockers_obj = {
        "type": "PMP_PASS2_P2A_HARD_BLOCKERS_V1",
        "status": "PASS2_RUNTIME_ENFORCEMENT_NOT_YET_COMPLETE",
        "base_main_commit": "e7ba1b9384303abbbc67d3e9b0522e51bec65493",
        "blocker_count": len(blockers),
        "blockers": blockers,
        "next_phase": "P2-B — actor authorization gate architecture and forbidden-action fixtures",
    }
    verification_obj = {
        "type": "PMP_PASS2_P2A_VERIFICATION_V1",
        "status": "PASS" if not integrity_errors else "FAIL",
        "checks": {
            "pass1_closure_receipt_present": (repo / "audit/pass1-final-closure-receipt.json").is_file(),
            "runtime_manifest_exact": not integrity_errors,
            "actor_inventory_nonempty": len(inventory) > 0,
            "all_executable_manifest_records_inventoried": len(inventory) == sum(1 for record in runtime["records"] if record["execution_class"] in EXECUTABLE_CLASSES),
            "old_pass2_passive_foundation_detected": "passive_authority_map_only" in authority_text,
            "old_pass2_active_path_only_detected": freeze.get("scope") == "active_path_only",
            "bug_watch_recurring_without_static_stop_detected": "setInterval(" in bug_text and "clearInterval(" not in bug_text,
            "hard_blockers_recorded": len(blockers) == 5,
        },
        "decision": "P2A_SCOPE_AND_CENSUS_COMPLETE_START_P2B" if not integrity_errors else "P2A_BLOCKED_BY_RUNTIME_IDENTITY_ERROR",
    }

    outputs = {
        "pass2-p2a-active-actor-inventory.json": inventory_obj,
        "pass2-p2a-source-reconciliation.json": reconciliation_obj,
        "pass2-p2a-hard-blockers.json": blockers_obj,
        "pass2-p2a-verification.json": verification_obj,
    }
    for name, value in outputs.items():
        (out / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": verification_obj["status"],
        "decision": verification_obj["decision"],
        "counts": inventory_obj["counts"],
        "reconciliation": reconciliation_obj["counts"],
        "blockers": len(blockers),
        "output_dir": str(out),
    }, indent=2, sort_keys=True))
    return 0 if verification_obj["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
