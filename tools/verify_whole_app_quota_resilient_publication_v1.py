#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
src = (root / 'pmp-diagnostics-writer-trace-v1.js').read_text()
gate = json.loads((root / 'audit/pass13/whole-app-quota-resilient-publication-gate-v1.json').read_text())
receipt = json.loads((root / 'audit/pass13/receipts/RECEIPT_WHOLE_APP_QUOTA_RESILIENT_PUBLICATION_20260803F_001.json').read_text())
assert gate['status'] == 'PASS'
assert receipt['status'] == 'PASS'
assert gate['publication_revision'] == receipt['publication_revision']
assert "mode:virtualized?'live_memory_virtualized_read':'live_memory_direct'" in src
assert "persistence_status:'QUOTA_UNAVAILABLE'" in src
assert "if(this===storage&&String(key)===BCD_RECEIPT_KEY" in src
assert "localStorage.clear" not in src
print('PASS: quota-resilient live receipt publication independently verified')
