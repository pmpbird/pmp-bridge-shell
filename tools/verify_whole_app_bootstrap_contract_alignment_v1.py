#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
src = (root / 'pmp-diagnostics-consolidated-view-v1.js').read_text()
gate = json.loads((root / 'audit/pass13/whole-app-bootstrap-contract-alignment-gate-v1.json').read_text())
receipt = json.loads((root / 'audit/pass13/receipts/RECEIPT_WHOLE_APP_BOOTSTRAP_CONTRACT_ALIGNMENT_20260803D_001.json').read_text())
assert gate['status'] == 'PASS'
assert receipt['status'] == 'PASS'
assert gate['required_bootstrap_version'] == '3.3.0-bounded-verified-bcd-publication-20260803C'
assert receipt['required_bootstrap_version'] == gate['required_bootstrap_version']
assert "const REQUIRED_BOOT_VERSION='3.3.0-bounded-verified-bcd-publication-20260803C';" in src
assert "3.2.0-transactional-versioned-bcd-bootstrap-20260801B" not in src
print('PASS: Whole App bootstrap contract alignment independently verified')
