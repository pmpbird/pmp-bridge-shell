#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    ".github/workflows/pass3-route-guardian-handoff-unit2-passive-consumer-v1.yml",
    "audit/pass3/pass3-route-guardian-handoff-unit2-passive-consumer-v1.json",
    "pmp-app-current.html",
    "pmp-route-guardian-current-loader-v22.html",
    "pmp-runtime-integrity-manifest-v1.json",
    "tools/generate_pass3_unit2_integrity_updates_v1.py",
    "tools/test_pass3_route_guardian_handoff_unit2_passive_consumer_v1.py",
    "tools/verify_pass3_route_guardian_handoff_unit2_passive_consumer_v1.py",
}


def run(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def main():
    audit = json.loads((ROOT / "audit/pass3/pass3-route-guardian-handoff-unit2-passive-consumer-v1.json").read_text(encoding="utf-8"))
    assert audit["status"] == "IMPLEMENTED_PENDING_MERGE"
    assert audit["base_main_commit"] == "4ab0e7bf9b046109c973455a2bd6ce724819e190"
    assert audit["preservation"]["current_map_destination_truth_changed"] is False
    assert audit["preservation"]["resolver_changed"] is False
    assert audit["preservation"]["new_persisted_user_state_added"] is False
    assert audit["preservation"]["unit3_started"] is False
    assert audit["preservation"]["pass4_started"] is False

    base = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else "HEAD^"
    changed = set(filter(None, run("git", "diff", "--name-only", f"{base}...HEAD").splitlines()))
    assert changed == EXPECTED, f"exact scope mismatch: {sorted(changed)}"

    subprocess.check_call([sys.executable, str(ROOT / "tools/generate_pass3_unit2_integrity_updates_v1.py")], cwd=ROOT)
    assert not run("git", "status", "--porcelain"), "integrity generation is not idempotent"
    subprocess.check_call([sys.executable, str(ROOT / "tools/test_pass3_route_guardian_handoff_unit2_passive_consumer_v1.py")], cwd=ROOT)
    print("PASS: exact eight-file Unit 2 scope verified")


if __name__ == "__main__":
    main()
