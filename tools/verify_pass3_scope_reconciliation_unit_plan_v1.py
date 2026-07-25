#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    ".github/workflows/pass3-scope-reconciliation-unit-plan-v1.yml",
    "audit/pass3/pass3-scope-reconciliation-unit-plan-v1.json",
    "tools/test_pass3_scope_reconciliation_unit_plan_v1.py",
    "tools/verify_pass3_scope_reconciliation_unit_plan_v1.py",
}


def run(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def main():
    plan = json.loads((ROOT / "audit/pass3/pass3-scope-reconciliation-unit-plan-v1.json").read_text(encoding="utf-8"))
    assert plan["status"] == "AUTHORITATIVE_FOR_CURRENT_ROADMAP_PASS3"
    assert plan["repair_scope"]["runtime_behavior_changed"] is False
    assert plan["repair_scope"]["persisted_user_data_changed"] is False
    assert plan["repair_scope"]["current_map_changed"] is False
    assert plan["repair_scope"]["pass3_implementation_advanced"] is False
    assert [unit["unit"] for unit in plan["units"]] == [1, 2, 3, 4, 5]

    base = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else "HEAD^"
    changed = set(filter(None, run("git", "diff", "--name-only", f"{base}...HEAD").splitlines()))
    assert changed == EXPECTED, f"exact scope mismatch: {sorted(changed)}"

    subprocess.check_call([sys.executable, str(ROOT / "tools/test_pass3_scope_reconciliation_unit_plan_v1.py")], cwd=ROOT)
    print("PASS: exact four-file documentation-only Pass 3 plan repair verified")


if __name__ == "__main__":
    main()
