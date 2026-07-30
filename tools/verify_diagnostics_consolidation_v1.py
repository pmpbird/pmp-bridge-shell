#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIEW = (ROOT / "pmp-diagnostics-consolidated-view-v1.js").read_text(encoding="utf-8")
ORCH = (ROOT / "pmp-app-orchestrator-v1.js").read_text(encoding="utf-8")

checks = {
    "same_diagnostics_owner": "const OWNER='diagnostics_owner'" in VIEW,
    "no_owner_registry_write": "localStorage.setItem" not in VIEW and "registerOwner" not in VIEW,
    "no_helper_registry_write": "registerHelper" not in VIEW and "createHelper" not in VIEW,
    "three_primary_areas": "Whole App Health" in VIEW and "App Orchestrator System" in VIEW and "Copy Full Diagnostic Report" in VIEW,
    "whole_app_evidence_preserved": all(token in VIEW for token in ["panel_order", "duplicate_panels", "flicker_recorder", "error_log", "bank_owner_split"]),
    "orchestrator_layers_present": all(token in VIEW for token in ["authority_layers", "protected_resources", "runtime_enforcement", "proof_and_maintenance", "transfer"]),
    "owners_helpers_present": "section_owners" in VIEW and "helpers" in VIEW,
    "registry_resources_read_only": "resources:registry.resources" in VIEW and "registry_write:false" in VIEW,
    "consolidated_view_loaded": "pmp-diagnostics-consolidated-view-v1.js" in ORCH,
    "boundary_receipt_declared": "owner_changes:false" in ORCH and "helper_changes:false" in ORCH and "registry_changes:false" in ORCH,
}

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(f"{'PASS' if ok else 'FAIL'} {name}")
if failed:
    raise SystemExit("Diagnostics consolidation verification failed: " + ", ".join(failed))
print("PASS Diagnostics consolidation preserves owner/helper boundaries")
