#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

cmd = ['python3', 'tools/test_native_diagnostics_bootstrap_and_style_v1.py']
run = subprocess.run(cmd, text=True, capture_output=True)
result = {
    'type': 'PMP_NATIVE_DIAGNOSTICS_BOOTSTRAP_STYLE_VERIFICATION_V1',
    'status': 'PASS' if run.returncode == 0 else 'FAIL',
    'command': cmd,
    'stdout': run.stdout.strip(),
    'stderr': run.stderr.strip(),
    'returncode': run.returncode,
    'files': [
        'pmp-diagnostics-consolidated-view-v1.js',
        'tools/test_native_diagnostics_bootstrap_and_style_v1.py',
    ],
    'boundaries': {
        'owner_changes': False,
        'helper_changes': False,
        'route_changes': False,
        'bank_rebuild': False,
        'continuous_run_mutation': False,
        'storage_migration': False,
        'persisted_user_data_write': False,
    },
}
Path('audit/pass13/receipts/RECEIPT_NATIVE_DIAGNOSTICS_BOOTSTRAP_STYLE_20260730G_001.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
raise SystemExit(run.returncode)
