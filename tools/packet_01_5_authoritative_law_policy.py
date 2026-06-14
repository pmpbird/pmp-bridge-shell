#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

STOPWORDS = {
    "a","an","and","are","as","at","be","by","for","from","has","have","in","is","it","its","of","on","or","that","the","their","there","this","to","was","were","with"
}
NEGATIVE_MARKERS = (" no ", " not ", " cannot ", " can't ", " missing ", " absent ", " unverified ", " without ", " only ")
POSITIVE_MARKERS = (" implemented ", " authorized ", " enforced ", " executed ", " completed ", " exists ", " provides ", " includes ")
EXCLUDED_PREFIXES = (
    ".github/", "tools/", "audit/applicability/", "audit/routing-inventory/", "audit/baseline-source/"
)
EXCLUDED_TERMS = ("archive", "historical", "reconstructed", "provisional")


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
    governing = any(term in low for term in (
        "packet", "pmp-current", "status", "receipt", "roadmap", "law", "protocol", "ledger", "active-work", "completion"
    ))
    if not governing:
        return None
    if any(term in base for term in (
        "routing_status", "routing-status", "master-status-ledger", "active-work-card", "continuation-protocol", "independent_verification"
    )):
        return 1
    if any(term in base for term in ("completion-receipt", "packet", "roadmap", "law", "plan", "status")):
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
        text = path.read_text(encoding="utf-8", errors="replace")
        selected.append({
            **item,
            "tier": effective_tier,
            "active_version": active,
            "sha256": sha256(path.read_bytes()),
            "text": text,
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
    if not claim_tokens:
        return 0.0
    return len(claim_tokens & tokens(passage)) / len(claim_tokens)


def is_negative(text: str) -> bool:
    padded = " " + text.lower() + " "
    return any(marker in padded for marker in NEGATIVE_MARKERS)


def is_positive(text: str) -> bool:
    padded = " " + text.lower() + " "
    return any(marker in padded for marker in POSITIVE_MARKERS) and not is_negative(text)


def direct_matches(claim: str, sources: list[dict[str, Any]], threshold: float = 0.82) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    support: list[dict[str, Any]] = []
    conflict: list[dict[str, Any]] = []
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
        if best_coverage >= threshold:
            match = {
                "path": source["path"], "tier": source["tier"], "version": source["version"],
                "sha256": source["sha256"], "coverage": round(best_coverage, 4), "passage": best_passage[:1200]
            }
            if claim_negative and is_positive(best_passage):
                conflict.append(match)
            else:
                support.append(match)
        elif claim_negative and best_coverage >= 0.65 and is_positive(best_passage):
            conflict.append({
                "path": source["path"], "tier": source["tier"], "version": source["version"],
                "sha256": source["sha256"], "coverage": round(best_coverage, 4), "passage": best_passage[:1200]
            })
    return support, conflict


def find_passage(sources: list[dict[str, Any]], groups: list[tuple[str, ...]]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for source in sources:
        if source["tier"] > 2 or not source["active_version"]:
            continue
        for passage in paragraphs(source["text"]):
            low = passage.lower()
            if all(any(term in low for term in group) for group in groups):
                matches.append({
                    "path": source["path"], "tier": source["tier"], "version": source["version"],
                    "sha256": source["sha256"], "coverage": None, "passage": passage[:1200]
                })
                break
    return matches


def reviewed_predicate(predicate: str, claim: str, sources: list[dict[str, Any]], files: list[str]) -> tuple[bool, list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    support: list[dict[str, Any]] = []
    detail: dict[str, Any] = {}
    if predicate == "PACKET_06_5_AI_BRIDGE_ONLY_IMPLEMENTATION_SCOPE":
        support = find_passage(sources, [("packet 06.5", "packet_06.5"), ("ai bridge",), ("implementation",), ("candidate", "promotion")])
    elif predicate == "FREE_CONSTRAINT_PRESENT_NO_ENFORCEMENT_GATE":
        constraint = find_passage(sources, [("free",), ("subscription", "paid", "cost")])
        gates = [path for path in files if re.search(r"(?:free|cost|subscription).*(?:gate|check)|(?:gate|check).*(?:free|cost|subscription)", path, flags=re.I)]
        support = constraint if constraint and not gates else []
        detail = {"constraint_sources": [x["path"] for x in constraint], "gate_like_files": gates}
    elif predicate == "PACKET_23_NO_CODE_ASSEMBLY_NOT_IMPLEMENTATION":
        support = find_passage(sources, [("packet 23", "packet_23"), ("no-code", "no code"), ("assembly",), ("not implementation", "not an implementation")])
    elif predicate == "PACKET_24_RUNBOOK_NOT_EXECUTION":
        support = find_passage(sources, [("packet 24", "packet_24"), ("runbook",), ("not execution", "not integration", "not acceptance", "specification")])
    elif predicate == "NO_COMPLETE_PIPELINE_IMPLEMENTATION_AUTHORITY":
        support = find_passage(sources, [("no authorized packet", "not authorized"), ("candidate pipeline", "candidate"), ("promotion",), ("rollback",)])
    elif predicate == "NO_REPAIR_RETEST_ITERATION_AUTHORITY":
        support = find_passage(sources, [("repair",), ("retest",), ("packet",), ("no explicit", "not authorized", "missing")])
    generic_support, conflicts = direct_matches(claim, sources)
    if not support:
        support = generic_support
    if support:
        best_tier = min(x["tier"] for x in support)
        equal_or_higher_conflicts = [x for x in conflicts if x["tier"] <= best_tier]
        if equal_or_higher_conflicts:
            return False, support, equal_or_higher_conflicts, {**detail, "reason": "equal_or_higher_precedence_conflict"}
    return bool(support), support, conflicts, detail


def generic_direct(claim: str, sources: list[dict[str, Any]], threshold: float, minimum_tokens: int) -> tuple[bool, list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if len(tokens(claim)) < minimum_tokens:
        return False, [], [], {"reason": "claim_too_short"}
    support, conflicts = direct_matches(claim, sources, threshold)
    if not support:
        return False, [], conflicts, {"reason": "no_direct_current_authority"}
    best_tier = min(x["tier"] for x in support)
    blocking = [x for x in conflicts if x["tier"] <= best_tier]
    if blocking:
        return False, support, blocking, {"reason": "equal_or_higher_precedence_conflict"}
    return True, support, conflicts, {"reason": "direct_current_authority_support"}
