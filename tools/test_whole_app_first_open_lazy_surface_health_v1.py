#!/usr/bin/env python3
from pathlib import Path

SRC = Path('pmp-diagnostic-coverage-passes-bcd-v1-1-1-0.js').read_text('utf-8')
checks = {
    'revision': "1.3.0-first-open-lazy-surface-health-20260824A" in SRC,
    'diagnostics_active_probe': 'function diagnosticsActive()' in SRC,
    'bridge_deferred_surface': "surface_validation:diag?'DEFERRED_WHILE_DIAGNOSTICS_ACTIVE':'REQUIRED'" in SRC,
    'library_deferred_surface': "surface_validation:diag?'DEFERRED_WHILE_DIAGNOSTICS_ACTIVE':'REQUIRED'" in SRC,
    'bank_deferred_surface': "surface_validation:diag?'DEFERRED_WHILE_DIAGNOSTICS_ACTIVE':'REQUIRED'" in SRC,
    'library_machine_status_separate': 'machine_integration_status:machineIntegration' in SRC,
    'exact_label_scan': "labelNodes('Bridge')" in SRC and "labelNodes('Library')" in SRC and "labelNodes('Bank')" in SRC,
    'single_first_open_boot': "boot_first_open_stable" in SRC and "[300,1200,3500]" not in SRC,
    'continuous_run_closed_deferred': "DEFERRED_UNTIL_BANK_OPEN" in SRC,
    'no_forced_pass': "status:issues.length?'FAIL':'PASS'" in SRC,
    'read_only_boundary': 'persisted_user_data_write:false' in SRC and 'dom_repair:false' in SRC,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit('FAIL: ' + ', '.join(failed))
print(f"PASS: first-open lazy-surface health ({len(checks)}/{len(checks)})")
