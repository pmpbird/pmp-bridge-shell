#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path
from typing import Any

EXCLUDED_PREFIXES = (
    "audit/applicability/",
    "audit/routing-inventory/",
    "audit/routing-batches/",
    "audit/baseline-source/",
    ".git/",
)
EXCLUDED_TERMS = (
    "historical",
    "reconstructed",
    "provisional",
    "discovery",
    "working_register",
    "working-register",
    "limitation_register",
    "limitation-register",
    "other_record_specific_family",
    "other-record-specific-family",
    "other_specific_evidence",
    "other-specific-evidence",
    "routing_status_v87",
    "routing-status-v87",
)
PASS_MARKERS = (
    "status: pass",
    '"status": "pass"',
    "status: approved",
    '"status": "approved"',
    "independently verified",
    "verification: pass",
)

REASONS = {
    "NO_HALLUCINATION_ACCEPTANCE_THRESHOLDS": "The current filtered authority and proof corpus contains no measured, approved acceptance thresholds covering hallucination rate, uncertainty calibration, and unsupported citations together. The preserved claim is therefore a current proof and acceptance limitation.",
    "NO_FEATURE_FLAG_LIFECYCLE_PROOF": "The current source, configuration, and governing corpus contains no complete feature-flag registry and lifecycle proof covering disabled-by-default state, activation authority, retirement, and accidental-activation tests. This is a current control limitation.",
    "ACTIVE_WORK_THREAD_SCHEMA_MIGRATION_UNRESOLVED": "No current authoritative artifact provides both an exact Active Work Thread schema and a verified migration path. The preserved schema-and-migration claim remains currently applicable.",
    "POINTER_AND_FREEZE_SCHEMAS_UNRESOLVED": "No current authoritative artifact completely defines the safe-point, Last Good, emergency pointer, and freeze-record schemas together with ownership. Partial pointer references do not close the complete claim.",
    "DATA_COMPATIBILITY_RULES_NOT_ENFORCED": "The effective current runtime does not contain complete enforcement for unknown-field preservation, duplicate handling, old-version handling, and archive/current separation together. The preserved implementation claim is currently applicable.",
    "NO_GLOBAL_RECEIPT_INDEX": "The current repository contains completion receipts but no single global receipt index that covers them with stable immutable identifiers and content digests. This is a current provenance limitation.",
    "HISTORICAL_COVERAGE_LIMITS_LOSSLESS_CLAIMS": "The current authoritative map explicitly limits its proof to the current route and does not prove every historical or external state. Full-history lossless claims therefore remain limited by unavailable raw history and possible hidden historical dependencies.",
    "NO_MONITORING_ALERT_OPERATOR": "No current implementation or governing artifact completely defines a monitoring signal, alert-delivery mechanism, and responsible responding operator together. This is a current operational-control limitation.",
    "NO_USER_EXPLANATION_STANDARD_PROOF": "The current governing and proof corpus contains no approved plain-language explanation standard plus execution proof for accuracy, completeness, and disclosure of technical risk. The preserved claim is currently applicable.",
    "SHORTCUT_SUCCESS_FAILURE_PATHS_UNTESTED": "The current proof corpus contains no verified test receipt covering both successful Shortcut completion and failure handling. The preserved test-coverage claim is currently applicable.",
    "NO_ACCESSIBILITY_STANDARD_EXECUTION_PROOF": "The current repository contains control-surface accessibility references but no approved accessibility standard and independently verified execution proof. This is a current compliance-proof limitation.",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tracked_files(repo: Path) -> list[str]:
    return subprocess.check_output(["git", "ls-files"], cwd=repo, text=True).splitlines()


def main_anchor(repo: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "origin/main"], cwd=repo, text=True).strip()
    except subprocess.CalledProcessError:
        return subprocess.check_output(["git", "rev-parse", "HEAD^"], cwd=repo, text=True).strip()


def included(path: str) -> bool:
    low = path.lower()
    if any(low.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
        return False
    if any(term in low for term in EXCLUDED_TERMS):
        return False
    return Path(path).suffix.lower() in {".md", ".json", ".txt", ".html", ".js", ".toml", ".yml", ".yaml"}


def corpus(repo: Path, files: list[str]) -> tuple[list[dict[str, Any]], str]:
    records: list[dict[str, Any]] = []
    for name in files:
        if not included(name):
            continue
        path = repo / name
        if not path.is_file():
            continue
        records.append({
            "path": name,
            "sha256": sha256(path.read_bytes()),
            "text": path.read_text(encoding="utf-8", errors="replace"),
        })
    census = "\n".join(f"{item['sha256']}|{item['path']}" for item in records) + "\n"
    return records, sha256(census.encode("utf-8"))


def effective_runtime(repo: Path, files: list[str]) -> tuple[str, list[dict[str, str]]]:
    tracked = set(files)
    pending = [
        "pmp-app-current.html",
        "pmp-current-map-v9.json",
        "pmp-route-guardian-current-loader-v14.html",
        "pmp-current-inner-cleanbug-rgcontrols-v4.html",
        "pmp-worker.js",
        "wrangler.toml",
    ]
    seen: list[str] = []
    records: list[dict[str, str]] = []
    pattern = re.compile(r"[A-Za-z0-9._-]+\.(?:html|js|json)")
    while pending:
        name = pending.pop(0)
        if name in seen or name not in tracked or "/" in name:
            continue
        path = repo / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        seen.append(name)
        records.append({"path": name, "sha256": sha256(path.read_bytes()), "text": text})
        for reference in pattern.findall(text):
            if reference in tracked and reference not in seen and reference not in pending:
                pending.append(reference)
    return "\n".join(item["text"] for item in records), records


def claim_from_queue(item: dict[str, Any]) -> str:
    text = item["missing_proof"]
    return text.split("Preserved claim: ", 1)[1] if "Preserved claim: " in text else text


def relevant(records: list[dict[str, Any]], term_groups: list[tuple[str, ...]], minimum_groups: int | None = None) -> list[dict[str, Any]]:
    minimum = len(term_groups) if minimum_groups is None else minimum_groups
    matches: list[dict[str, Any]] = []
    for item in records:
        low = item["text"].lower()
        count = sum(1 for group in term_groups if any(term in low for term in group))
        if count >= minimum:
            matches.append({"path": item["path"], "sha256": item["sha256"], "matched_groups": count, "pass": any(marker in low for marker in PASS_MARKERS)})
    return matches


def three_way(matches: list[dict[str, Any]], complete_groups: int) -> tuple[str, dict[str, Any], list[dict[str, str]]]:
    complete = [item for item in matches if item["matched_groups"] >= complete_groups and item["pass"]]
    if complete:
        return "DISPROVED", {"complete_verified_matches": complete, "partial_matches": matches}, [{"path": item["path"], "sha256": item["sha256"]} for item in complete]
    if matches:
        return "UNRESOLVED", {"complete_verified_matches": [], "partial_matches": matches}, [{"path": item["path"], "sha256": item["sha256"]} for item in matches[:20]]
    return "SUPPORTED", {"complete_verified_matches": [], "partial_matches": []}, []


def evaluate(predicate: str, repo: Path, files: list[str], records: list[dict[str, Any]], runtime_text: str, runtime_records: list[dict[str, str]]) -> tuple[str, dict[str, Any], list[dict[str, str]]]:
    low_runtime = runtime_text.lower()
    if predicate == "NO_HALLUCINATION_ACCEPTANCE_THRESHOLDS":
        groups = [("hallucination",), ("uncertainty calibration", "calibration"), ("unsupported citation", "citation accuracy"), ("threshold", "maximum", "minimum", "percent", "%")]
        matches = relevant(records, groups, 3)
        return three_way(matches, 4)
    if predicate == "NO_FEATURE_FLAG_LIFECYCLE_PROOF":
        groups = [("feature flag", "feature-flag"), ("disabled by default", "disabled-by-default"), ("activation", "enable"), ("retirement", "deprecation"), ("accidental activation", "activation test")]
        matches = relevant(records, groups, 3)
        return three_way(matches, 5)
    if predicate == "ACTIVE_WORK_THREAD_SCHEMA_MIGRATION_UNRESOLVED":
        groups = [("active work thread",), ("schema",), ("migration",), ("version", "upgrade")]
        matches = relevant(records, groups, 2)
        return three_way(matches, 4)
    if predicate == "POINTER_AND_FREEZE_SCHEMAS_UNRESOLVED":
        groups = [("safe-point", "safe point"), ("last good",), ("emergency pointer",), ("freeze record",), ("schema",), ("owner", "ownership")]
        matches = relevant(records, groups, 3)
        return three_way(matches, 6)
    if predicate == "DATA_COMPATIBILITY_RULES_NOT_ENFORCED":
        groups = [("unknown field", "unknown-field"), ("duplicate",), ("old version", "older version", "version handling"), ("archive",), ("current separation", "archive/current")]
        found = [group for group in groups if any(term in low_runtime for term in group)]
        if len(found) == len(groups):
            return "DISPROVED", {"runtime_groups_found": len(found), "required_groups": len(groups)}, runtime_records
        if not found:
            return "SUPPORTED", {"runtime_groups_found": 0, "required_groups": len(groups)}, runtime_records
        return "UNRESOLVED", {"runtime_groups_found": len(found), "required_groups": len(groups)}, runtime_records
    if predicate == "NO_GLOBAL_RECEIPT_INDEX":
        receipt_files = [item for item in records if "receipt" in Path(item["path"]).name.lower()]
        index_candidates = [item for item in records if any(term in Path(item["path"]).name.lower() for term in ("receipt-index", "receipt_index", "receipt-registry", "receipt_registry"))]
        complete = []
        for item in index_candidates:
            low = item["text"].lower()
            covered = sum(1 for receipt in receipt_files if Path(receipt["path"]).name.lower() in low)
            if receipt_files and covered / len(receipt_files) >= 0.9 and "sha256" in low and ("immutable id" in low or "receipt_id" in low or "receipt id" in low):
                complete.append({"path": item["path"], "sha256": item["sha256"], "covered": covered})
        if complete:
            return "DISPROVED", {"receipt_files": len(receipt_files), "complete_indexes": complete}, complete
        if index_candidates:
            return "UNRESOLVED", {"receipt_files": len(receipt_files), "index_candidates": [{"path": item["path"], "sha256": item["sha256"]} for item in index_candidates]}, index_candidates
        return "SUPPORTED", {"receipt_files": len(receipt_files), "index_candidates": []}, []
    if predicate == "HISTORICAL_COVERAGE_LIMITS_LOSSLESS_CLAIMS":
        path = repo / "pmp-current-map-v9.json"
        text = path.read_text(encoding="utf-8")
        low = text.lower()
        supported = "does not prove" in low and ("historical" in low or "external state" in low or "frozen" in low)
        return ("SUPPORTED" if supported else "UNRESOLVED"), {"current_map_limitation_present": supported}, [{"path": "pmp-current-map-v9.json", "sha256": sha256(path.read_bytes())}]
    if predicate == "NO_MONITORING_ALERT_OPERATOR":
        groups = [("monitoring", "health check", "telemetry"), ("alert", "notification"), ("delivery", "email", "pagerduty", "slack", "webhook"), ("operator", "owner", "on-call")]
        matches = relevant(records, groups, 2)
        return three_way(matches, 4)
    if predicate == "NO_USER_EXPLANATION_STANDARD_PROOF":
        groups = [("plain language", "plain-language"), ("accuracy",), ("complete", "completeness"), ("technical risk", "risk disclosure"), ("standard",), ("execution proof", "verified")]
        matches = relevant(records, groups, 3)
        return three_way(matches, 6)
    if predicate == "SHORTCUT_SUCCESS_FAILURE_PATHS_UNTESTED":
        groups = [("shortcut",), ("success", "completion"), ("failure", "error"), ("test", "verification"), ("status: pass", '"status": "pass"')]
        matches = relevant(records, groups, 3)
        return three_way(matches, 5)
    if predicate == "NO_ACCESSIBILITY_STANDARD_EXECUTION_PROOF":
        groups = [("accessibility",), ("wcag", "accessibility standard"), ("execution", "runtime"), ("test", "audit"), ("status: pass", '"status": "pass"')]
        matches = relevant(records, groups, 2)
        return three_way(matches, 5)
    return "UNRESOLVED", {"error": "unknown predicate"}, []
