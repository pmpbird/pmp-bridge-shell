#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path
from typing import Any

EXCLUDED_PREFIXES = (
    "audit/applicability/", "audit/routing-inventory/", "audit/routing-batches/",
    "audit/baseline-source/", "tools/packet_01_5_deployment", ".git/"
)
EXCLUDED_TERMS = (
    "historical", "reconstructed", "provisional", "discovery", "working_register",
    "working-register", "limitation_register", "limitation-register",
    "deployment_live_family", "deployment-live-family", "deployment_live_evidence",
    "deployment-live-evidence", "routing_status_v86", "routing-status-v86"
)
COMPLETION_MARKERS = ("status: pass", '"status": "pass"', "status: approved", '"status": "approved"', "verified", "completed")

REASONS = {
    "NO_AI_PROVIDER_PIPELINE": "The repository-configured worker is pmp-worker.js, and the complete current runtime source contains no AI-provider adapter, model-call route, provider request, or response parser. The preserved claim is therefore a current implementation limitation.",
    "NO_BACKEND_DATA_LIFECYCLE_PROOF": "The complete current authoritative proof corpus contains no digest-bound verification covering backend retention, deletion, backup, restore, and regional or data-residency behavior together. Because the claim is explicitly about verification status, this absence is a current proof limitation.",
    "NO_CREDENTIAL_LIFECYCLE_IMPLEMENTATION": "Current runtime and configuration contain no implemented credential creation, secret lifecycle, rotation, revocation, compromise-response, or least-privilege mechanism for the application backend. This is a current implementation limitation.",
    "NO_AI_RESPONSE_VALIDATION_PIPELINE": "The current runtime has no AI request and response pipeline and therefore no implemented AI-response schema validator or semantic-grounding stage. This directly supports the preserved implementation claim.",
    "NO_CANDIDATE_SANDBOX_OR_EGRESS_CONTROLS": "The current tracked implementation contains no candidate-code executor with sandboxing, resource caps, or network-egress restrictions. The planned candidate surface therefore lacks an implemented containment layer.",
    "NO_ENCRYPTION_BACKUP_SECRET_PROOF": "The current authoritative proof corpus contains no verification receipt covering encryption at rest and backup-secret handling for private exports or backend records. The claim concerns proof existence and is currently applicable.",
    "NO_INCIDENT_RESPONSE_PLAN": "Current governing and operational records assign incident-response ownership but contain no implemented incident-response procedure covering the named credential, exposure, candidate, promotion, benchmark, and evidence incidents. Ownership alone is not a plan.",
    "NO_EXPOSURE_MODE_DECISION": "Current configuration exposes permissive cross-origin behavior without authentication, while no approved product decision defines the intended public, private, authenticated, obscurity-based, or local-only exposure mode. This is a current governance and deployment limitation.",
    "NO_COMPREHENSIVE_DELETION_EXPORT_PROOF": "The current authoritative proof corpus contains no single verified deletion and export receipt covering local state, backend records, Notes, logs, receipts, and caches together. The preserved proof-status claim is currently applicable.",
    "NO_SAFE_DEGRADATION_PLAN": "Current governing records assign safe-degradation ownership but contain no implemented plan defining what remains usable when AI, backend, GitHub, Shortcuts, Notes, and network access are unavailable together.",
    "NO_LIVE_DEPLOYED_RUNTIME_AUDIT_RECEIPT": "The completed current audit corpus contains source and repository verification but no digest-bound receipt showing execution of the deployed public runtime with its serving revision, URL, headers, and observed behavior.",
    "OFFLINE_EXTERNAL_DEPENDENCY_RISK": "Current runtime source contains network fetches and external or integration dependencies used by the app path. These dependencies can be unavailable offline, making the preserved claim an active conditional risk.",
    "NO_PWA_CACHE_LIFECYCLE_PROOF": "The current tracked repository contains no service-worker lifecycle implementation or verified cache-install, update, invalidation, and rollback proof for the PWA path.",
    "NO_COMPREHENSIVE_DISASTER_RECOVERY_PROCEDURE": "Current records assign disaster-recovery ownership but contain no implemented procedure covering simultaneous loss of device, browser data, GitHub access, backend, and Notes.",
    "NO_CANARY_STAGED_ROLLOUT_OR_ROLLBACK_DRILL": "Current deployment configuration and workflows contain no canary or staged rollout mechanism and no verified post-deploy rollback drill. This is a current deployment-control limitation."
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
        text = path.read_text(encoding="utf-8", errors="replace")
        records.append({"path": name, "sha256": sha256(path.read_bytes()), "text": text})
    census = "\n".join(f"{item['sha256']}|{item['path']}" for item in records) + "\n"
    return records, sha256(census.encode("utf-8"))


def runtime_corpus(repo: Path, files: list[str]) -> tuple[str, list[dict[str, str]]]:
    records: list[dict[str, str]] = []
    for name in files:
        suffix = Path(name).suffix.lower()
        base = Path(name).name.lower()
        if suffix not in {".html", ".js", ".json", ".toml"}:
            continue
        if "/" in name and not name.startswith(".github/"):
            continue
        if not (base.startswith("pmp-") or base in {"worker.js", "cloudflare-worker.js", "wrangler.toml"}):
            continue
        path = repo / name
        if path.is_file():
            records.append({"path": name, "sha256": sha256(path.read_bytes()), "text": path.read_text(encoding="utf-8", errors="replace")})
    return "\n".join(item["text"] for item in records), records


def claim_from_queue(item: dict[str, Any]) -> str:
    text = item["missing_proof"]
    return text.split("Preserved claim: ", 1)[1] if "Preserved claim: " in text else text


def has_completed_proof(records: list[dict[str, Any]], term_groups: list[tuple[str, ...]], minimum_groups: int | None = None) -> tuple[bool, list[dict[str, Any]]]:
    minimum = minimum_groups if minimum_groups is not None else len(term_groups)
    matches: list[dict[str, Any]] = []
    for item in records:
        low = item["text"].lower()
        groups = sum(1 for group in term_groups if any(term in low for term in group))
        if groups >= minimum and any(marker in low for marker in COMPLETION_MARKERS):
            matches.append({"path": item["path"], "sha256": item["sha256"], "matched_groups": groups})
    return bool(matches), matches


def no_explicit_decision(records: list[dict[str, Any]], term_groups: list[tuple[str, ...]]) -> tuple[bool, list[dict[str, Any]]]:
    matches: list[dict[str, Any]] = []
    for item in records:
        low = item["text"].lower()
        if all(any(term in low for term in group) for group in term_groups) and any(term in low for term in ("approved", "decision", "shall", "must", "selected")):
            matches.append({"path": item["path"], "sha256": item["sha256"]})
    return not matches, matches


def evaluate(predicate: str, repo: Path, files: list[str], records: list[dict[str, Any]], runtime_text: str, runtime_records: list[dict[str, str]]) -> tuple[bool, dict[str, Any], list[dict[str, str]]]:
    low = runtime_text.lower()
    evidence_files: list[dict[str, str]] = []
    if predicate == "NO_AI_PROVIDER_PIPELINE":
        wrangler = (repo / "wrangler.toml").read_text(encoding="utf-8")
        worker = (repo / "pmp-worker.js").read_text(encoding="utf-8")
        absent = all(term not in worker.lower() for term in ("/api/ai", "/api/model", "/api/provider", "/api/chat", "openai", "anthropic"))
        ok = 'main = "pmp-worker.js"' in wrangler and absent
        evidence_files = [item for item in runtime_records if item["path"] in {"pmp-worker.js", "wrangler.toml"}]
        return ok, {"configured_worker": "pmp-worker.js", "provider_markers_absent": absent}, evidence_files
    if predicate == "NO_BACKEND_DATA_LIFECYCLE_PROOF":
        found, matches = has_completed_proof(records, [("retention",), ("deletion",), ("backup",), ("restore",), ("data residency", "regional")])
        return not found, {"completed_proof_matches": matches}, []
    if predicate == "NO_CREDENTIAL_LIFECYCLE_IMPLEMENTATION":
        markers = ("credential rotation", "secret rotation", "revoke credential", "revocation", "least privilege", "compromise response")
        implemented = any(marker in low for marker in markers)
        return not implemented, {"implementation_markers_found": [marker for marker in markers if marker in low]}, runtime_records
    if predicate == "NO_AI_RESPONSE_VALIDATION_PIPELINE":
        ai_pipeline = any(term in low for term in ("/api/ai", "/api/model", "/api/provider", "openai", "anthropic"))
        validator = any(term in low for term in ("response schema", "semantic grounding", "grounded response", "validateairesponse"))
        return not ai_pipeline and not validator, {"ai_pipeline_present": ai_pipeline, "validator_present": validator}, runtime_records
    if predicate == "NO_CANDIDATE_SANDBOX_OR_EGRESS_CONTROLS":
        controls = ("sandbox", "resource cap", "resource_limit", "network egress", "deny network", "isolated vm", "webassembly sandbox")
        found = [term for term in controls if term in low]
        return not found, {"containment_markers_found": found}, runtime_records
    if predicate == "NO_ENCRYPTION_BACKUP_SECRET_PROOF":
        found, matches = has_completed_proof(records, [("encryption at rest", "encryption-at-rest"), ("backup secret", "backup-secret", "backup key")])
        return not found, {"completed_proof_matches": matches}, []
    if predicate == "NO_INCIDENT_RESPONSE_PLAN":
        found, matches = has_completed_proof(records, [("incident response",), ("credential leak", "data exposure"), ("malicious candidate", "bad promotion"), ("benchmark leak", "corrupted evidence")], minimum_groups=3)
        return not found, {"implemented_plan_matches": matches}, []
    if predicate == "NO_EXPOSURE_MODE_DECISION":
        absent, matches = no_explicit_decision(records, [("public", "private-by-obscurity", "local-only"), ("authenticated", "authentication"), ("endpoint", "app exposure", "exposure mode")])
        worker = (repo / "pmp-worker.js").read_text(encoding="utf-8")
        practical = {"wildcard_cors": '"Access-Control-Allow-Origin": "*"' in worker, "authorization_check": "authorization" in worker.lower()}
        return absent, {"explicit_decision_matches": matches, "practical_source_state": practical}, [item for item in runtime_records if item["path"] == "pmp-worker.js"]
    if predicate == "NO_COMPREHENSIVE_DELETION_EXPORT_PROOF":
        found, matches = has_completed_proof(records, [("deletion",), ("export",), ("local",), ("backend",), ("notes",), ("logs",), ("receipts",), ("caches",)], minimum_groups=7)
        return not found, {"completed_proof_matches": matches}, []
    if predicate == "NO_SAFE_DEGRADATION_PLAN":
        found, matches = has_completed_proof(records, [("safe degradation",), ("ai",), ("backend",), ("github",), ("shortcuts",), ("notes",), ("network",)], minimum_groups=6)
        return not found, {"implemented_plan_matches": matches}, []
    if predicate == "NO_LIVE_DEPLOYED_RUNTIME_AUDIT_RECEIPT":
        found, matches = has_completed_proof(records, [("deployed public runtime", "live deployed runtime", "production runtime"), ("url", "endpoint"), ("headers",), ("executed", "observed behavior", "live probe")], minimum_groups=3)
        return not found, {"live_audit_receipt_matches": matches}, []
    if predicate == "OFFLINE_EXTERNAL_DEPENDENCY_RISK":
        markers = {
            "network_fetch": "fetch(" in low,
            "external_url": "https://" in low,
            "jszip": "jszip" in low,
            "backend": "/api/" in low or "backend" in low,
            "shortcuts": "shortcut" in low,
        }
        return sum(1 for value in markers.values() if value) >= 4, markers, runtime_records
    if predicate == "NO_PWA_CACHE_LIFECYCLE_PROOF":
        service_workers = [name for name in files if re.search(r"(?:service[-_.]?worker|sw)\.(?:js|mjs)$", Path(name).name, flags=re.I)]
        found, matches = has_completed_proof(records, [("service worker",), ("cache invalidation", "cache update"), ("install",), ("rollback",)], minimum_groups=3)
        return not service_workers and not found, {"service_worker_files": service_workers, "proof_matches": matches}, []
    if predicate == "NO_COMPREHENSIVE_DISASTER_RECOVERY_PROCEDURE":
        found, matches = has_completed_proof(records, [("disaster recovery",), ("device",), ("browser data",), ("github access",), ("backend",), ("notes",)], minimum_groups=5)
        return not found, {"implemented_procedure_matches": matches}, []
    if predicate == "NO_CANARY_STAGED_ROLLOUT_OR_ROLLBACK_DRILL":
        found, matches = has_completed_proof(records, [("canary", "staged rollout"), ("post-deploy", "deployment"), ("rollback drill", "rollback test")], minimum_groups=2)
        return not found, {"rollout_or_drill_matches": matches}, []
    return False, {"error": "unknown predicate"}, []
