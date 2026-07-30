#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORCH = (ROOT / "pmp-app-orchestrator-v1.js").read_text(encoding="utf-8")
RUNTIME = (ROOT / "pmp-app-orchestrator-ownership-runtime-v1.js").read_text(encoding="utf-8")
REGISTRY = (ROOT / "pmp-app-orchestrator-ownership-registry-v1.json").read_text(encoding="utf-8")

checks = {
    "runtime_source_declared": "pmp-app-orchestrator-ownership-runtime-v1.js?fresh=ownership-runtime-loader-20260729A" in ORCH,
    "runtime_version_declared": "1.0.0-exclusive-owner-runtime-20260727A" in ORCH,
    "runtime_loaded_before_reports": "await load('pmp-app-orchestrator-ownership-runtime-v1.js'" in ORCH,
    "runtime_load_invoked": "typeof ownershipApi.load==='function'" in ORCH and "await ownershipApi.load()" in ORCH,
    "loader_status_reported": "ownership_runtime_loader" in ORCH,
    "receipt_key_matches": "pmp_app_orchestrator_ownership_runtime_v1_receipt" in ORCH and "pmp_app_orchestrator_ownership_runtime_v1_receipt" in RUNTIME,
    "registry_is_current_authority": "pmp-app-orchestrator-ownership-registry-v1.json" in ORCH and "PMP_APP_ORCHESTRATOR_OWNERSHIP_REGISTRY_V1" in REGISTRY,
    "no_new_owner_or_helper": "const OWNER='app_orchestrator_owner'" in ORCH,
}

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(f"{'PASS' if ok else 'FAIL'} {name}")
if failed:
    raise SystemExit("Ownership runtime loader verification failed: " + ", ".join(failed))
print("PASS App Orchestrator ownership runtime loader contract")
