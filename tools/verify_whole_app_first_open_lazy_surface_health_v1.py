#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

TEST = ['python3', 'tools/test_whole_app_first_open_lazy_surface_health_v1.py']
subprocess.run(TEST, check=True)

gate = json.loads(Path('audit/pass13/whole-app-first-open-lazy-surface-health-gate-v1.json').read_text('utf-8'))
receipt = json.loads(Path('audit/pass13/receipts/RECEIPT_WHOLE_APP_FIRST_OPEN_LAZY_SURFACE_HEALTH_20260824A_001.json').read_text('utf-8'))
assert gate['status'] == 'PASS'
assert gate['revision'] == '1.3.0-first-open-lazy-surface-health-20260824A'
assert receipt['status'] == 'PASS'
assert receipt['revision'] == gate['revision']
assert 'pmp-diagnostic-coverage-passes-bcd-v1-1-1-0.js' in gate['scope']['implementation_paths']
assert gate['no_blind_flying_gate']['special_authority']['required'] is False
print('PASS: first-open lazy-surface verifier')
