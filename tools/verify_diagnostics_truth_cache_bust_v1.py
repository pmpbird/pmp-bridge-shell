#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORCH = (ROOT / "pmp-app-orchestrator-v1.js").read_text(encoding="utf-8")
DIAG = (ROOT / "pmp-diagnostics-owner-v1.js").read_text(encoding="utf-8")

EXPECTED = "2.5.0-truth-confidence-20260729A"
TOKEN = "pmp-diagnostics-owner-v1.js?fresh=truth-confidence-20260729A"

checks = {
    "diagnostics_declares_expected_version": f"const V='{EXPECTED}'" in DIAG,
    "orchestrator_requires_expected_version": f"const DIAGNOSTICS_VERSION='{EXPECTED}'" in ORCH,
    "orchestrator_uses_new_cache_token": TOKEN in ORCH,
    "old_cache_token_removed": "ownership-maintenance-20260727A" not in ORCH,
    "version_mismatch_forces_reload": "api.version!==expectedVersion" in ORCH and "reloaded_version_mismatch" in ORCH,
    "diagnostics_runtime_version_reported": "diagnostics_runtime" in ORCH and "loaded_version" in ORCH,
    "no_new_helper_registration": "helper_registry" not in ORCH.lower(),
}

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(f"{'PASS' if ok else 'FAIL'} {name}")
if failed:
    raise SystemExit("Diagnostics cache-bust verification failed: " + ", ".join(failed))
print("PASS diagnostics truth cache-bust contract")
