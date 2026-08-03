#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / 'pmp-diagnostics-writer-trace-v1.js').read_text()

required = [
    "const REQUIRED_VIEW_VERSION='2.9.0-live-bootstrap-await-20260803A'",
    "const CURRENT_VIEW_SRC='pmp-diagnostics-consolidated-view-v1.js'",
    "PMPCurrentDiagnosticsViewBootstrapV1",
    "exact-diagnostics-view-20260803B-",
    "api.version===REQUIRED_VIEW_VERSION",
    "typeof api.install==='function'",
    "pmp_current_diagnostics_view_bootstrap_v1_receipt",
    "removeRetiredControl",
]
missing = [token for token in required if token not in SRC]
assert not missing, f'missing required exact-view bootstrap tokens: {missing}'
assert "Whole App Health Layout Trace v2" in SRC
assert "document.createElement('button')" not in SRC
print('PASS: exact Diagnostics view bootstrap rejects stale singleton and keeps trace UI retired')
