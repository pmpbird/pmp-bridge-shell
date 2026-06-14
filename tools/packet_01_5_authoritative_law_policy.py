#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path
from typing import Any

STOPWORDS = {
    "a","an","and","are","as","at","be","by","for","from","has","have","in","is","it","its","of","on","or","that","the","their","there","this","to","was","were","with"
}
NEGATIVE_MARKERS = (" no ", " not ", " cannot ", " can't ", " missing ", " absent ", " unverified ", " without ", " only ")
POSITIVE_MARKERS = (" implemented ", " implementation ", " authorized ", " enforced ", " executed ", " execution ", " completed ", " exists ", " provides ", " includes ", " owns ", " own ")
EXCLUDED_PREFIXES = (
    ".github/", "tools/", "audit/applicability/", "audit/routing-inventory/", "audit/routing-batches/", "audit/baseline-source/"
)
EXCLUDED_TERMS = (
    "archive", "historical", "reconstructed", "provisional", "discovery", "working_register", "working-register",
    "limitation_register", "limitation-register", "applicability_batch", "applicability-batch",
    "authoritative_packet_law_family", "authoritative-packet-law-family"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tracked_files(repo: Path) -> list[str]:
    return subprocess.check_output(["git", "ls-files"], cwd=repo, text=True).splitlines()


def main_anchor(repo: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "origin/main"], cwd=repo, text=True).strip()
    except subprocess.CalledProcessError:
        return subprocess.check_output(["git", "rev-parse", "HEAD^"], cwd=repo, text=True).strip()


def version_of(name: str) -> int:
    matches = re.findall(r"(?:^|[-_.])v(\d+)(?=[-_.]|$)", name, flags=re.I)
    return max((int(x) for x in matches), default=0)


def normalized_family(name: str) -> str:
    return re.sub(r"(?:^|[-_.])v\d+(?=[-_.]|$)", "-v#", name.lower())


def candidate_tier(path: str) -> int | None:
    low = path.lower()
    if any(low.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
        return None
    if any(term in low for term in EXCLUDED_TERMS):
        return None
    if Path(path).suffix.lower() not in {".md", ".json", ".txt"}:
        return None
    base = Path(path).name.lower()
    if not any(term in low for term in (
        "packet", "pmp-current", "status", "receipt", "roadmap", "law", "protocol", "ledger", "active-work", "completion", "approved"
    )):
        return None
    if any(term in base for term in (
        "approved_existing_packet_role_amendment", "approved-existing-packet-role-amendment",
        "routing_status", "routing-status", "master-status-ledger", "active-work-card",
        "continuation-protocol", "independent_verification"
    )):
        return 1
    if any(term in base for term in ("completion-receipt", "packet", "roadmap", "law", "plan", "status", "approved")):
        return 2
    return 3


def authority_sources(repo: Path, files: list[str]) -> tuple[list[dict[str, Any]], str]:
    candidates: list[dict[str, Any]] = []
    max_versions: dict[str, int] = {}
    for path in files:
        tier = candidate_tier(path)
        if tier is None:
            continue
        family = normalized_family(path)
        version = version_of(path)
        max_versions[family] = max(max_versions.get(family, 0), version)
        candidates.append({"path": path, "tier": tier, "family": family, "version": version})
    selected: list[dict[str, Any]] = []
    for item in candidates:
        path = repo / item["path"]
        if not path.is_file():
            continue
        active = item["version"] == max_versions[item["family"]]
        effective_tier = item["tier"] if active else 3
        selected.append({
            **item,
            "tier": effective_tier,
            "active_version": active,
            "sha256": sha256(path.read_bytes()),
            "text": path.read_text(encoding="utf-8", errors="replace"),
        })
    census = "\n".join(f"{x['tier']}|{x['active_version']}|{x['version']}|{x['sha256']}|{x['path']}" for x in selected) + "\n"
    return selected, sha256(census.encode("utf-8"))


def tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", text.lower())
    return {word for word in words if len(word) > 1 and word not in STOPWORDS}


def paragraphs(text: str) -> list[str]:
    blocks = re.split(r"\n\s*\n|(?<=\.)\s+(?=[A-Z#])", text)
    return [re.sub(r"\s+", " ", block).strip() for block in blocks if block.strip()]


def coverage(claim: str, passage: str) -> float:
    claim_tokens = tokens(claim)
    return len(claim_tokens & tokens(passage)) / len(claim_tokens) if claim_tokens else 0.0


def is_negative(text: str) -> bool:
    padded = " " + text.lower() + " "
    return any(marker in padded for marker in NEGATIVE_MARKERS)


def is_positive(text: str) -> bool:
    padded = " " + text.lower() + " "
    return any(marker in padded for marker in POSITIVE_MARKERS) and not is_negative(text)


def source_match(sources: list[dict[str, Any]], path_fragment: str, required_terms: tuple[str, ...]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for source in sources:
        if source["tier"] > 2 or not source["active_version"] or path_fragment.lower() not in source["path"].lower():
            continue
        low = source["text"].lower()
        if all(term.lower() in low for term in required_terms):
            matches.append({
                "path": source["path"], "tier": source["tier"], "version": source["version"],
                "sha256": source["sha256"], "coverage": None, "passage": source["text"][:1600]
            })
    return matches


def direct_matches(claim: str, sources: list[dict[str, Any]], threshold: float = 0.82) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    support: list[dict[str, Any]] = []
    disproof: list[dict[str, Any]] = []
    claim_negative = is_negative(claim)
    for source in sources:
        if source["tier"] > 2 or not source["active_version"]:
            continue
        best_passage = ""
        best_coverage = 0.0
        for passage in paragraphs(source["text"]):
            score = coverage(claim, passage)
            if score > best_coverage:
                best_coverage, best_passage = score, passage
        if best_coverage < threshold:
            continue
        match = {
            "path": source["path"], "tier": source["tier"], "version": source["version"],
            "sha256": source["sha256"], "coverage": round(best_coverage, 4), "passage": best_passage[:1200]
        }
        if claim_negative and is_positive(best_passage):
            disproof.append(match)
        else:
            support.append(match)
    return support, disproof


def resolve_lists(support: list[dict[str, Any]], disproof: list[dict[str, Any]], detail: dict[str, Any] | None = None) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    detail = dict(detail or {})
    if not support and not disproof:
        return "UNRESOLVED", [], [], {**detail, "reason": "no_direct_current_authority"}
    support_tier = min((item["tier"] for item in support), default=99)
    disproof_tier = min((item["tier"] for item in disproof), default=99)
    if support_tier < disproof_tier:
        return "SUPPORTED", support, disproof, {**detail, "reason": "higher_precedence_support"}
    if disproof_tier < support_tier:
        return "DISPROVED", support, disproof, {**detail, "reason": "higher_precedence_disproof"}
    if support and disproof:
        return "UNRESOLVED", support, disproof, {**detail, "reason": "same_tier_conflict"}
    if support:
        return "SUPPORTED", support, [], {**detail, "reason": "direct_current_authority_support"}
    return "DISPROVED", [], disproof, {**detail, "reason": "direct_current_authority_disproof"}


def reviewed_predicate(predicate: str, claim: str, sources: list[dict[str, Any]], files: list[str]) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    support, disproof = direct_matches(claim, sources)
    amendment = "Packet_03.5_Approved_Existing_Packet_Role_Amendment_v1.json"
    if predicate == "PACKET_06_5_ONLY_IMPLEMENTATION_CLAIM":
        disproof += source_match(sources, amendment, ("status\": \"approved", "\"23\"", "actual resident safe change implementation execution"))
    elif predicate == "PACKET_23_IMPLEMENTATION_ROLE_CLAIM":
        disproof += source_match(sources, amendment, ("\"23\"", "actual resident safe change implementation execution", "assembly plan"))
    elif predicate == "PACKET_24_EXECUTION_ROLE_CLAIM":
        disproof += source_match(sources, amendment, ("\"24\"", "execution of integration", "acceptance", "runbook"))
    elif predicate == "COMPLETE_PIPELINE_AUTHORITY_CLAIM":
        direct_disproof = source_match(sources, amendment, ("resolve every packet 03.5 lifecycle gap", "actual resident safe change implementation execution", "execution of integration"))
        # This amendment may still be incomplete for every named sub-capability; treat it as related, not decisive.
        detail = {"related_role_amendment": [item["path"] for item in direct_disproof]}
        return resolve_lists(support, disproof, detail)
    elif predicate == "FREE_CONSTRAINT_ENFORCEMENT_CLAIM":
        # Ownership of free-operation rules is not itself proof of an enforcement gate.
        related = source_match(sources, amendment, ("free-operation", "boundary rules"))
        return resolve_lists(support, disproof, {"related_free_operation_authority": [item["path"] for item in related]})
    elif predicate == "REPAIR_RETEST_AUTHORITY_CLAIM":
        return resolve_lists(support, disproof)
    return resolve_lists(support, disproof)


def generic_direct(claim: str, sources: list[dict[str, Any]], threshold: float, minimum_tokens: int) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if len(tokens(claim)) < minimum_tokens:
        return "UNRESOLVED", [], [], {"reason": "claim_too_short"}
    support, disproof = direct_matches(claim, sources, threshold)
    return resolve_lists(support, disproof)
