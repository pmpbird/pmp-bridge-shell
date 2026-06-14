#!/usr/bin/env python3
"""Mechanical integrity audit for Packet 01.5 discovery records.

Counts provisional record headings directly from the source files, compares them
with each file's declared count, checks required fields, and writes reproducible
Markdown/JSON audit outputs. This script does not deduplicate, route, close, or
judge semantic validity.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO / "audit"
BASELINE = 122

PASS_RE = re.compile(r"Packet_01\.5_Discovery_Pass_(\d+)_.*\.md$")
DECLARED_RE = re.compile(r"^New provisional records:\s*(\d+)\s*$", re.MULTILINE)
RECORD_RE = re.compile(r"^###\s+([^\n]+)$", re.MULTILINE)
ID_RE = re.compile(r"^([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3})\s+[—-]\s+(.+)$")


def pass_number(path: Path) -> int:
    if path.name == "Packet_01.5_Discovery_Working_Register_v1.md":
        return 1
    match = PASS_RE.search(path.name)
    if not match:
        raise ValueError(f"Not a discovery pass file: {path}")
    return int(match.group(1))


def source_files() -> list[Path]:
    files: list[Path] = []
    working = AUDIT_DIR / "Packet_01.5_Discovery_Working_Register_v1.md"
    if working.exists():
        files.append(working)
    files.extend(AUDIT_DIR.glob("Packet_01.5_Discovery_Pass_*.md"))
    return sorted(files, key=pass_number)


def record_area(text: str) -> str:
    # Count only the provisional-record area, never headings in result/status text.
    result_match = re.search(r"^##\s+Pass\s+\d+\s+result\s*$", text, re.MULTILINE)
    return text[: result_match.start()] if result_match else text


def audit_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    area = record_area(text)
    headings = RECORD_RE.findall(area)
    declared_match = DECLARED_RE.search(text)
    declared = int(declared_match.group(1)) if declared_match else None

    records: list[dict] = []
    malformed_headings: list[str] = []
    missing_harm: list[str] = []
    missing_overlap: list[str] = []

    heading_matches = list(re.finditer(r"^###\s+([^\n]+)$", area, re.MULTILINE))
    for index, heading_match in enumerate(heading_matches):
        heading = heading_match.group(1).strip()
        end = heading_matches[index + 1].start() if index + 1 < len(heading_matches) else len(area)
        block = area[heading_match.end() : end]
        parsed = ID_RE.match(heading)
        if parsed:
            record_id, title = parsed.groups()
        else:
            record_id, title = "", heading
            malformed_headings.append(heading)
        if "HARM:" not in block:
            missing_harm.append(record_id or heading)
        if "OVERLAP TO CHECK:" not in block:
            missing_overlap.append(record_id or heading)
        records.append({"id": record_id, "title": title})

    return {
        "pass": pass_number(path),
        "path": str(path.relative_to(REPO)),
        "actual_count": len(headings),
        "declared_count": declared,
        "count_match": declared is None or declared == len(headings),
        "malformed_headings": malformed_headings,
        "missing_harm": missing_harm,
        "missing_overlap": missing_overlap,
        "records": records,
    }


def main() -> None:
    files = source_files()
    if not files:
        raise SystemExit("No Packet 01.5 discovery files found")

    results = [audit_file(path) for path in files]
    all_records = [record for result in results for record in result["records"]]
    ids = [record["id"] for record in all_records if record["id"]]
    headings = [f'{record["id"]} — {record["title"]}' if record["id"] else record["title"] for record in all_records]

    duplicate_ids = {key: value for key, value in Counter(ids).items() if value > 1}
    duplicate_headings = {key: value for key, value in Counter(headings).items() if value > 1}
    prefix_counts: Counter[str] = Counter()
    for record_id in ids:
        prefix_counts[record_id.rsplit("-", 1)[0]] += 1

    actual_provisional = sum(result["actual_count"] for result in results)
    declared_known = sum(result["declared_count"] or 0 for result in results)
    mismatches = [result for result in results if not result["count_match"]]
    malformed = sum(len(result["malformed_headings"]) for result in results)
    missing_harm = sum(len(result["missing_harm"]) for result in results)
    missing_overlap = sum(len(result["missing_overlap"]) for result in results)

    payload = {
        "audit_date": date.today().isoformat(),
        "scope": "Packet 01.5 mechanical discovery integrity only",
        "baseline_count": BASELINE,
        "files_audited": len(results),
        "actual_provisional_count": actual_provisional,
        "combined_actual_count": BASELINE + actual_provisional,
        "sum_of_declared_counts_where_present": declared_known,
        "count_mismatch_count": len(mismatches),
        "duplicate_id_count": len(duplicate_ids),
        "duplicate_exact_heading_count": len(duplicate_headings),
        "malformed_heading_count": malformed,
        "missing_harm_count": missing_harm,
        "missing_overlap_count": missing_overlap,
        "passes": results,
        "duplicate_ids": duplicate_ids,
        "duplicate_exact_headings": duplicate_headings,
        "category_prefix_counts": dict(sorted(prefix_counts.items())),
    }

    json_path = AUDIT_DIR / "Packet_01.5_Discovery_Integrity_Audit_v1.json"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Packet 01.5 — Discovery Integrity Audit v1",
        "",
        "STATUS: MECHANICAL AUDIT COMPLETE",
        "ROUTING: NOT STARTED",
        f"DATE: {payload['audit_date']}",
        "",
        "This audit counts source records mechanically. It does not deduplicate, route, close, validate relevance, or claim saturation.",
        "",
        "## Result",
        "",
        f"- Source files audited: {len(results)}",
        f"- Preserved baseline: {BASELINE}",
        f"- Actual provisional headings: {actual_provisional}",
        f"- Actual combined working total: {BASELINE + actual_provisional}",
        f"- Files with declared-count mismatch: {len(mismatches)}",
        f"- Duplicate record IDs: {len(duplicate_ids)}",
        f"- Duplicate exact headings: {len(duplicate_headings)}",
        f"- Malformed record headings: {malformed}",
        f"- Records missing HARM: {missing_harm}",
        f"- Records missing OVERLAP TO CHECK: {missing_overlap}",
        "",
        "## Per-pass count audit",
        "",
        "| Pass | Actual | Declared | Match | File |",
        "|---:|---:|---:|:---:|---|",
    ]
    for result in results:
        declared = "—" if result["declared_count"] is None else str(result["declared_count"])
        match = "YES" if result["count_match"] else "NO"
        lines.append(f"| {result['pass']} | {result['actual_count']} | {declared} | {match} | `{result['path']}` |")

    lines.extend(["", "## Declared-count mismatches", ""])
    if mismatches:
        for result in mismatches:
            lines.append(
                f"- Pass {result['pass']}: actual {result['actual_count']}; declared {result['declared_count']}; `{result['path']}`"
            )
    else:
        lines.append("- None.")

    lines.extend(["", "## Structural exceptions", ""])
    if malformed or missing_harm or missing_overlap:
        for result in results:
            if result["malformed_headings"]:
                lines.append(f"- Pass {result['pass']} malformed headings: {result['malformed_headings']}")
            if result["missing_harm"]:
                lines.append(f"- Pass {result['pass']} missing HARM: {result['missing_harm']}")
            if result["missing_overlap"]:
                lines.append(f"- Pass {result['pass']} missing OVERLAP TO CHECK: {result['missing_overlap']}")
    else:
        lines.append("- None detected.")

    lines.extend(["", "## Duplicate exact identifiers", ""])
    if duplicate_ids:
        for key, count in sorted(duplicate_ids.items()):
            lines.append(f"- `{key}` appears {count} times.")
    else:
        lines.append("- None detected.")

    lines.extend([
        "",
        "## Governing interpretation",
        "",
        "- This report supersedes hand-maintained arithmetic only after its output has been reviewed and accepted.",
        "- Semantic duplicates and out-of-scope candidates remain unresolved.",
        "- Major-domain coverage must be audited separately.",
        "- Saturation testing must not begin from an uncorrected count ledger.",
        "",
        "END PACKET 01.5 — DISCOVERY INTEGRITY AUDIT v1",
        "",
    ])

    md_path = AUDIT_DIR / "Packet_01.5_Discovery_Integrity_Audit_v1.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
