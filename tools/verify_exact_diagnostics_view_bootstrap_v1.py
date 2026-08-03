#!/usr/bin/env python3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
result = subprocess.run(
    ['python3', 'tools/test_exact_diagnostics_view_bootstrap_v1.py'],
    cwd=ROOT,
    text=True,
    capture_output=True,
)
if result.stdout:
    print(result.stdout, end='')
if result.stderr:
    print(result.stderr, end='')
if result.returncode:
    raise SystemExit(result.returncode)

src = (ROOT / 'pmp-diagnostics-writer-trace-v1.js').read_text()
for forbidden in ["document.createElement('button')", 'navigation_changes:true', 'storage_migration:true']:
    if forbidden in src:
        raise SystemExit(f'forbidden token present: {forbidden}')
print('PASS: exact Diagnostics view bootstrap verifier')
