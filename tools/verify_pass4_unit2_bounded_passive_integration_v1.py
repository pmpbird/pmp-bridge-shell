#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    ".github/workflows/pass4-unit2-bounded-passive-strip-integration-v1.yml",
    "audit/a003-manifest-seal.json",
    "audit/pass4/pass4-boot-status-strip-unit2-bounded-passive-integration-v1.json",
    "pmp-app-current.html",
    "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html",
    "pmp-runtime-integrity-manifest-v1.json",
    "tools/apply_pass4_unit2_bounded_passive_integration_v1.py",
    "tools/test_pass4_unit2_bounded_passive_integration_v1.py",
    "tools/verify_pass4_unit2_bounded_passive_integration_v1.py",
}


def run(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def main() -> None:
    base = sys.argv[1] if len(sys.argv) > 1 else "HEAD^"
    changed = set(filter(None, run("git", "diff", "--name-only", f"{base}...HEAD").splitlines()))
    assert changed == EXPECTED, (sorted(changed), sorted(EXPECTED))
    forbidden = {
        "pmp-current-map-v12.json",
        "pmp-current-route-resolver-v1.js",
        "pmp-route-guardian-current-loader-v22.html",
        "pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html",
        "pmp-app-orchestrator-v1.js",
        "pmp-boot-status-strip-owner-v1.js",
    }
    assert not (changed & forbidden)
    subprocess.check_call([sys.executable, str(ROOT / "tools/apply_pass4_unit2_bounded_passive_integration_v1.py")], cwd=ROOT)
    assert not run("git", "status", "--porcelain"), "bounded integration generator is not idempotent"
    subprocess.check_call([sys.executable, str(ROOT / "tools/test_pass4_unit2_bounded_passive_integration_v1.py")], cwd=ROOT)
    print("PASS: exact nine-file bounded Pass 4 Unit 2 scope verified")


if __name__ == "__main__":
    main()
