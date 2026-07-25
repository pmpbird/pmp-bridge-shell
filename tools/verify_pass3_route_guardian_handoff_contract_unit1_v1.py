#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    ".github/workflows/pass3-route-guardian-handoff-contract-unit1-v1.yml",
    "audit/pass3/pass3-route-guardian-handoff-contract-unit1-v1.json",
    "tools/test_pass3_route_guardian_handoff_contract_unit1_v1.py",
    "tools/verify_pass3_route_guardian_handoff_contract_unit1_v1.py",
}


def run(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def main():
    contract = json.loads((ROOT / "audit/pass3/pass3-route-guardian-handoff-contract-unit1-v1.json").read_text())
    current_map = json.loads((ROOT / "pmp-current-map-v12.json").read_text())
    assert contract["status"] == "CONTRACT_DEFINED_NOT_RUNTIME_ACTIVATED"
    assert contract["route_authority"] == "pmp-current-map-v12.json"
    assert current_map["route_contract"]["failure_mode"] == "fail_closed"
    assert current_map["route_contract"]["implicit_fallbacks"] is False
    assert current_map["route_guardian"]["path"]
    assert current_map["current_app"]["path"]

    base = sys.argv[1] if len(sys.argv) > 1 else "HEAD^"
    changed = set(filter(None, run("git", "diff", "--name-only", f"{base}...HEAD").splitlines()))
    assert changed == EXPECTED, f"exact scope mismatch: {sorted(changed)}"

    subprocess.check_call([sys.executable, str(ROOT / "tools/test_pass3_route_guardian_handoff_contract_unit1_v1.py")], cwd=ROOT)
    print("PASS: exact four-file Pass 3 unit 1 scope verified")


if __name__ == "__main__":
    main()
