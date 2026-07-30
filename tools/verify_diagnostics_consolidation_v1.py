#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIEW = (ROOT / "pmp-diagnostics-consolidated-view-v1.js").read_text(encoding="utf-8")
HANDOFF = (ROOT / "pmp-new-chat-safe-handoff-v1.js").read_text(encoding="utf-8")
ORCH = (ROOT / "pmp-app-orchestrator-v1.js").read_text(encoding="utf-8")

checks = {
    "same_diagnostics_owner": "const OWNER='diagnostics_owner'" in VIEW,
    "no_owner_registry_write": "localStorage.setItem" not in VIEW and "registerOwner" not in VIEW,
    "no_helper_registry_write": "registerHelper" not in VIEW and "createHelper" not in VIEW,
    "three_primary_areas": all(token in VIEW for token in ["Whole App Health", "Full Diagnostics", "New Chat Safe Handoff"]),
    "major_system_coverage": all(token in VIEW for token in [
        "app_orchestrator_system", "active_path_and_routing", "runtime_and_mount_lifecycle",
        "bridge_system", "library_system", "bank_system", "continuous_run_system",
        "errors_bug_watch_visual_stability",
    ]),
    "app_orchestrator_layers": all(token in VIEW for token in [
        "authority_layers", "protected_resources", "canonical_writers", "ownership_runtime",
        "maintenance_and_proof",
    ]),
    "whole_and_section_copy": all(token in VIEW for token in [
        "Copy Whole App Health Report", "Copy Full Diagnostics Report", "Copy This Section",
    ]),
    "missing_evidence_truthful": "NOT_PROVEN" in VIEW and "never silently treated as PASS" in VIEW,
    "full_report_api": "fullDiagnosticReport" in VIEW and "raw_diagnostics_owner_report" in VIEW,
    "safe_handoff_embeds_full_diagnostics": "full_diagnostics_package" in HANDOFF and "diagnosticsPackage" in HANDOFF,
    "safe_handoff_continuation_material": all(token in HANDOFF for token in [
        "repository_audit_instructions", "required_tests_and_gates", "exact_next_move",
        "authorization_boundaries", "recent_change_history", "evidence_manifest",
        "source_of_truth_pointers", "governing_rules_and_boundaries",
    ]),
    "library_and_bridge_in_both": all(token in VIEW and token in HANDOFF for token in ["Bridge", "Library"]),
    "bank_continuous_run_separated": "does not merge the two systems" in VIEW and "remain separate systems" in HANDOFF,
    "self_verifying_package": "payload_sha256" in HANDOFF and "PACKAGE_MANIFEST.json" in HANDOFF,
    "consolidated_view_loaded": "pmp-diagnostics-consolidated-view-v1.js" in ORCH,
    "boundary_receipt_declared": "owner_changes:false" in ORCH and "helper_changes:false" in ORCH and "registry_changes:false" in ORCH,
}

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(f"{'PASS' if ok else 'FAIL'} {name}")
if failed:
    raise SystemExit("Diagnostics and safe handoff verification failed: " + ", ".join(failed))
print("PASS expanded diagnostics and safe handoff preserve owner/helper boundaries")
