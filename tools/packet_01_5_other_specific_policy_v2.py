#!/usr/bin/env python3
from __future__ import annotations

import re

from packet_01_5_other_specific_policy import *
import packet_01_5_other_specific_policy as base


def passages(text: str) -> list[str]:
    blocks = re.split(r"\n\s*\n|\n[─═-]{8,}\n", text)
    return [re.sub(r"\s+", " ", block).strip() for block in blocks if block.strip()]


def relevant(records, term_groups, minimum_groups=None):
    minimum = len(term_groups) if minimum_groups is None else minimum_groups
    matches = []
    for item in records:
        file_low = item["text"].lower()
        file_pass = any(marker in file_low for marker in base.PASS_MARKERS)
        best = None
        for passage in passages(item["text"]):
            low = passage.lower()
            count = sum(1 for group in term_groups if any(term in low for term in group))
            if count >= minimum and (best is None or count > best["matched_groups"]):
                best = {
                    "path": item["path"],
                    "sha256": item["sha256"],
                    "matched_groups": count,
                    "pass": file_pass,
                    "passage": passage[:1600],
                }
        if best:
            matches.append(best)
    return matches


base.relevant = relevant
_original_evaluate = base.evaluate


def local_segments(text: str, anchor_terms: tuple[str, ...], radius: int = 1800) -> list[str]:
    low = text.lower()
    segments = []
    for anchor in anchor_terms:
        start = 0
        while True:
            index = low.find(anchor, start)
            if index < 0:
                break
            segments.append(low[max(0, index - radius): min(len(low), index + radius)])
            start = index + len(anchor)
    return segments


def schema_outcome(records, anchor_terms, required_terms):
    partial = []
    complete = []
    for item in records:
        segments = local_segments(item["text"], anchor_terms)
        if not segments:
            continue
        file_pass = any(marker in item["text"].lower() for marker in base.PASS_MARKERS)
        best_found = set()
        for segment in segments:
            found = {term for term in required_terms if term in segment}
            if len(found) > len(best_found):
                best_found = found
        record = {
            "path": item["path"],
            "sha256": item["sha256"],
            "found_terms": sorted(best_found),
            "required_terms": list(required_terms),
            "pass": file_pass,
        }
        if set(required_terms).issubset(best_found) and file_pass:
            complete.append(record)
        else:
            partial.append(record)
    if complete:
        return "DISPROVED", {"complete_verified_matches": complete, "partial_matches": partial}, [{"path": item["path"], "sha256": item["sha256"]} for item in complete]
    return "SUPPORTED", {"complete_verified_matches": [], "partial_matches": partial}, [{"path": item["path"], "sha256": item["sha256"]} for item in partial[:20]]


def evaluate(predicate, repo, files, records, runtime_text, runtime_records):
    if predicate == "ACTIVE_WORK_THREAD_SCHEMA_MIGRATION_UNRESOLVED":
        return schema_outcome(records, ("active work thread",), ("schema", "migration", "version"))
    if predicate == "POINTER_AND_FREEZE_SCHEMAS_UNRESOLVED":
        return schema_outcome(records, ("safe-point", "safe point", "last good", "emergency pointer", "freeze record"), ("safe-point", "last good", "emergency pointer", "freeze record", "schema", "owner"))
    return _original_evaluate(predicate, repo, files, records, runtime_text, runtime_records)


base.evaluate = evaluate
