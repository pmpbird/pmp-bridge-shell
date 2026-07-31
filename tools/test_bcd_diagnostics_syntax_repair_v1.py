#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'pmp-diagnostic-coverage-passes-bcd-v1.js'
text = TARGET.read_text(encoding='utf-8')
checks = {
    'old_function_name_removed': 'function api(names)' not in text,
    'finder_present': 'function findApi(names)' in text,
    'public_api_present': 'const publicApi=' in text,
    'old_public_declaration_removed': 'const api={version:V,run,last:' not in text,
    'receipt_key_preserved': 'pmp_diagnostic_coverage_passes_bcd_v1_receipt' in text,
    'read_only_boundary_preserved': 'persisted_user_data_write:false' in text,
}
node = subprocess.run(['node', '--check', str(TARGET)], capture_output=True, text=True)
checks['node_syntax'] = node.returncode == 0
failed = [name for name, ok in checks.items() if not ok]
print({'status': 'PASS' if not failed else 'FAIL', 'checks': checks, 'stderr': node.stderr})
raise SystemExit(1 if failed else 0)
