#!/usr/bin/env python3
from pathlib import Path

p = Path('pmp-diagnostics-consolidated-view-v1.js')
s = p.read_text(encoding='utf-8')
required = [
    "2.4.0-native-bootstrap-isolated-health-ui-20260730G",
    "function produceEvidence",
    "PMPDiagnosticCoveragePassAV1",
    "PMPDiagnosticCoveragePassesBCDV1",
    "pmpDiagHealthRowV1",
    "Running current live diagnostics",
    "native_boot_",
    "pageshow",
    "visible_resume",
]
missing = [x for x in required if x not in s]
forbidden = ['<div class="pmpDiagCard" style="display:block">']
found = [x for x in forbidden if x in s]
assert not missing, f'missing contracts: {missing}'
assert not found, f'legacy shared health-card class remains: {found}'
assert s.count("const publicApi=") == 1
print('PASS native diagnostics bootstrap and isolated health UI contract')
