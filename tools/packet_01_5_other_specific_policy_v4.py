#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

from packet_01_5_other_specific_policy_v3 import *
import packet_01_5_other_specific_policy as base

_original_included = base.included

def version_of(path: str) -> int:
    matches = re.findall(r"(?:^|[-_.])v(\d+)(?=[-_.]|$)", path, flags=re.I)
    return max((int(value) for value in matches), default=0)


def family_of(path: str) -> str:
    return re.sub(r"(?:^|[-_.])v\d+(?=[-_.]|$)", "-v#", path.lower())


def authoritative_path(path: str) -> bool:
    low = path.lower()
    if not _original_included(path):
        return False
    if low.startswith("audit/routing-evidence/"):
        return False
    if "/plans/" in low or "-plan-" in low or "_plan_" in low:
        return False
    if "draft" in low or "candidate" in low or "temporary" in low or "-test" in low or "_test" in low:
        return False
    return True


def corpus(repo: Path, files: list[str]):
    candidates = [name for name in files if authoritative_path(name)]
    max_versions = {}
    for name in candidates:
        family = family_of(name)
        max_versions[family] = max(max_versions.get(family, 0), version_of(name))
    records = []
    for name in candidates:
        version = version_of(name)
        if version and version < max_versions[family_of(name)]:
            continue
        path = repo / name
        if not path.is_file():
            continue
        records.append({
            "path": name,
            "sha256": base.sha256(path.read_bytes()),
            "text": path.read_text(encoding="utf-8", errors="replace"),
        })
    census = "\n".join(f"{item['sha256']}|{item['path']}" for item in records) + "\n"
    return records, base.sha256(census.encode("utf-8"))


base.corpus = corpus
