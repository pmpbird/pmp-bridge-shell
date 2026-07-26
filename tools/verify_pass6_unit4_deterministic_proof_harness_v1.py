#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "8720d27964d715bcd3f1b29289ab8381b61e0711"
CATALOG = ROOT / "audit/pass6/pass6-cross-system-invariant-catalog-v1.json"
FIXTURE = ROOT / "audit/pass6/fixtures/pass6-unit4-deterministic-proof-harness-positive-v1.json"
REPORT = ROOT / "audit/pass6/pass6-deterministic-browser-frame-event-unit4-proof-v1.json"
RECEIPT = ROOT / "audit/pass6/receipts/RECEIPT_P6_U4_DETERMINISTIC_PROOF_HARNESS_20260726T102000Z_001.json"
HARNESS = ROOT / "tools/pass6_deterministic_browser_frame_event_harness_v1.js"
RUNNER = ROOT / "tools/run_pass6_unit4_deterministic_proof_harness_v1.js"
TEST = ROOT / "tools/test_pass6_unit4_deterministic_proof_harness_v1.js"
P6_U3_WORKFLOW = ROOT / ".github/workflows/pass6-unit3-cross-system-invariant-matrix-v1.yml"
EXPECTED = {
    ".github/workflows/pass6-unit3-cross-system-invariant-matrix-v1.yml",
    ".github/workflows/pass6-unit4-deterministic-proof-harness-v1.yml",
    "audit/pass6/fixtures/pass6-unit4-deterministic-proof-harness-positive-v1.json",
    "audit/pass6/pass6-deterministic-browser-frame-event-unit4-proof-v1.json",
    "audit/pass6/receipts/RECEIPT_P6_U4_DETERMINISTIC_PROOF_HARNESS_20260726T102000Z_001.json",
    "tools/pass6_deterministic_browser_frame_event_harness_v1.js",
    "tools/run_pass6_unit4_deterministic_proof_harness_v1.js",
    "tools/test_pass6_unit4_deterministic_proof_harness_v1.js",
    "tools/verify_pass6_unit4_deterministic_proof_harness_v1.py",
}
EXPECTED_P6_U3_SENTINELS = {
    "audit/pass6/pass6-cross-system-invariant-catalog-v1.json",
    "audit/pass6/pass6-cross-system-invariant-unit3-matrix-v1.json",
    "audit/pass6/receipts/RECEIPT_P6_U3_CROSS_SYSTEM_MATRIX_20260726T095500Z_001.json",
    "tools/run_pass6_unit3_cross_system_invariant_matrix_v1.py",
    "tools/test_pass6_unit3_cross_system_invariant_matrix_v1.py",
    "tools/verify_pass6_unit3_cross_system_invariant_matrix_v1.py",
}
PROTECTED_PREFIXES = (
    "pmp-",
    "safe-writer",
    "resident",
    "bug-memory",
)


def output(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def tracked_bytes(path: Path) -> bytes:
    if path.exists():
        return path.read_bytes()
    relative = path.relative_to(ROOT).as_posix()
    return subprocess.check_output(["git", "show", f"HEAD:{relative}"], cwd=ROOT)


def sha(path: Path) -> str:
    return hashlib.sha256(tracked_bytes(path)).hexdigest()


def changed_paths(base: str) -> set[str]:
    changed: set[str] = set()
    for command in (
        ("git", "diff", "--name-only", f"{base}...HEAD"),
        ("git", "diff", "--name-only", base),
        ("git", "ls-files", "--others", "--exclude-standard"),
    ):
        changed.update(filter(None, output(*command).splitlines()))
    return changed


def workflow_paths(text: str) -> set[str]:
    match = re.search(r"(?m)^    paths:\n(?P<rows>(?:      - [^\n]+\n)+)", text)
    assert match
    return {
        row.strip()[2:].strip().strip("'\"")
        for row in match.group("rows").splitlines()
    }


def main() -> None:
    base = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else BASE
    assert base == BASE
    changed = changed_paths(base)
    assert changed == EXPECTED, (sorted(changed), sorted(EXPECTED))
    assert not any(path.startswith(PROTECTED_PREFIXES) for path in changed)

    report = json.loads(REPORT.read_text())
    receipt = json.loads(RECEIPT.read_text())
    fixture = json.loads(FIXTURE.read_text())
    assert report["base_main_commit"] == BASE
    assert report["status"] == "DETERMINISTIC_PROOF_HARNESS_PROVEN"
    assert set(report["changed_paths"]) == EXPECTED
    assert receipt["status"] == "DETERMINISTIC_PROOF_HARNESS_PROVEN"
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["evidence"] == REPORT.relative_to(ROOT).as_posix()
    assert receipt["fixture"] == FIXTURE.relative_to(ROOT).as_posix()

    assert report["harness"]["sha256"] == sha(HARNESS)
    assert report["inputs"]["catalog_sha256"] == sha(CATALOG)
    assert report["inputs"]["fixture_sha256"] == sha(FIXTURE)
    assert report["inputs"]["runner_sha256"] == sha(RUNNER)
    assert report["inputs"]["test_sha256"] == sha(TEST)

    test_output = output("node", str(TEST.relative_to(ROOT)))
    assert "deterministic browser/frame/event proof harness (372/372)" in test_output
    proof = json.loads(output("node", str(RUNNER.relative_to(ROOT))))
    assert proof["status"] == "PASS"
    assert proof["summary"] == {
        "invariants_required": 20,
        "invariants_passed": 20,
        "events_captured": 8,
        "frames_observed": 2,
        "final_tick": 8,
        "failures": 0,
    }
    assert proof["failure"] is None
    assert proof["secondary_failures"] == []
    assert proof["teardown"] == {"status": "PASS", "calls": 1, "final_tick": 8}
    assert proof["result_sha256"] == report["baseline_proof"]["result_sha256"]
    assert all(value == 0 for value in proof["effects"].values())
    assert len(proof["selected_invariants"]) == 20
    assert len({row["subsystem"] for row in proof["selected_invariants"]}) == 9
    assert len(proof["assertions"]) == 20
    assert len(proof["events"]) == 8
    assert [row["monotonic_tick"] for row in proof["events"]] == list(range(1, 9))
    assert fixture["id"] == proof["scenario_id"]

    harness_text = HARNESS.read_text()
    for forbidden in (
        "require('playwright')",
        'require("playwright")',
        "require('puppeteer')",
        "localStorage.",
        "fetch(",
        "http.server",
        "playwright install",
    ):
        assert forbidden not in harness_text
    assert "PMP_PASS6_DETERMINISTIC_BROWSER_ADAPTER_V1" in harness_text
    assert "MONOTONIC_INTEGER_TICKS" in harness_text
    assert "FORBIDDEN_EFFECT_OBSERVED" in harness_text
    assert "secondary_failures" in harness_text

    assert workflow_paths(P6_U3_WORKFLOW.read_text()) == EXPECTED_P6_U3_SENTINELS
    assert report["ci_routing_repair"]["standing_a003_coverage_preserved"] is True
    assert report["failure_policy"]["silent_pass_path"] is False
    assert report["failure_policy"]["primary_failure_overwritten_by_teardown"] is False
    assert all(value is False for value in report["effects"].values())
    assert report["authority"]["special_authority_consumed"] is False
    assert report["authority"]["retry_authorized"] is False
    assert report["next_step"]["id"] == "P6-U5"
    assert report["next_step"]["requires_user_app_check"] is False
    assert report["next_step"]["requires_new_explicit_authority"] is False
    assert receipt["next_safe_move"]["step_id"] == "P6-U5"
    assert receipt["next_safe_move"]["requires_user_app_check"] is False

    print(
        "PASS: exact nine-file P6-U4 deterministic proof harness and "
        "completed-workflow routing verified (20/20 invariants, 372/372 assertions)"
    )


if __name__ == "__main__":
    main()
