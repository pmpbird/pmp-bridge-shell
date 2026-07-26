#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    ".github/workflows/pass4-unit4-route-guardian-interaction-repair-readiness-v1.yml",
    "audit/pass4/pass4-boot-status-strip-unit4-route-guardian-interaction-repair-readiness-v1.json",
    "tools/pass4_unit4_route_guardian_interaction_boundary_v1.js",
    "tools/test_pass4_unit4_route_guardian_interaction_repair_v1.js",
    "tools/verify_pass4_unit4_route_guardian_interaction_repair_v1.py",
}
PROTECTED = {
    "pmp-route-guardian-current-loader-v22.html",
    "pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html",
    "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html",
    "pmp-boot-status-strip-owner-v1.js",
    "pmp-current-map-v12.json",
    "pmp-current-route-resolver-v1.js",
    "pmp-app-current.html",
    "pmp-app-orchestrator-v1.js",
    "pmp-runtime-integrity-manifest-v1.json",
    "audit/a003-manifest-seal.json",
}


def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def main():
    base = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else "HEAD^"
    changed = set(filter(None, output("git", "diff", "--name-only", f"{base}...HEAD").splitlines()))
    assert changed == EXPECTED, (sorted(changed), sorted(EXPECTED))
    assert not changed & PROTECTED

    helper = (ROOT / "tools/pass4_unit4_route_guardian_interaction_boundary_v1.js").read_text()
    assert "locator.evaluate" in helper
    assert "button.click()" in helper
    for forbidden in ("force: true", ".goto(", "location.assign(", "location.replace(", ".src=", "launch("):
        assert forbidden not in helper, forbidden

    workflow = (
        ROOT / ".github/workflows/pass4-unit4-route-guardian-interaction-repair-readiness-v1.yml"
    ).read_text()
    for forbidden in (
        "workflow_dispatch",
        "playwright install",
        "http.server",
        "run_pass4_unit4_replacement_observation_v1.js",
        "run_pass4_unit4_bounded_live_observation_v1.js",
    ):
        assert forbidden not in workflow, forbidden

    receipt_path = (
        ROOT
        / "audit/pass4/pass4-boot-status-strip-unit4-route-guardian-interaction-repair-readiness-v1.json"
    )
    receipt = json.loads(receipt_path.read_text())
    assert receipt["status"] == "DETERMINISTIC_REPAIR_READY"
    assert receipt["current_substep"] == "P4-U4R"
    assert receipt["live_observation_performed"] is False
    assert receipt["live_observation_count"] == 0
    assert receipt["new_live_observation_authorized"] is False
    assert receipt["production_runtime_changed"] is False
    assert receipt["runtime_integrity_changed"] is False
    assert receipt["persisted_user_data_changed"] is False
    assert receipt["unit5_started"] is False
    assert receipt["pass5_started"] is False
    assert receipt["pr122_touched"] is False
    assert receipt["next_gate"]["status"] == "BLOCKED_AUTHORITY"

    subprocess.check_call(
        ["node", "tools/test_pass4_unit4_route_guardian_interaction_repair_v1.js"],
        cwd=ROOT,
    )
    print("PASS: exact five-file evidence-harness-only interaction repair scope verified")


if __name__ == "__main__":
    main()
