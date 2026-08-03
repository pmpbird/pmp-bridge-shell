#!/usr/bin/env python3
from pathlib import Path

src = (Path(__file__).resolve().parents[1] / 'pmp-diagnostics-consolidated-view-v1.js').read_text()
required = [
    "2.9.1-bootstrap-contract-alignment-20260803D",
    "3.3.0-bounded-verified-bcd-publication-20260803C",
    "const REQUIRED_BOOT_VERSION=",
    "boot.version!==REQUIRED_BOOT_VERSION",
    "await boot.run(reason||'native_consolidated_diagnostics')",
]
missing = [token for token in required if token not in src]
assert not missing, f'missing aligned bootstrap contract tokens: {missing}'
assert "3.2.0-transactional-versioned-bcd-bootstrap-20260801B" not in src
print('PASS: Whole App Health requires and awaits current B-D bootstrap 3.3')
