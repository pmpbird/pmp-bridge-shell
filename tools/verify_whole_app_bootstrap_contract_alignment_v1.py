#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
view = (root / 'pmp-diagnostics-consolidated-view-v1.js').read_text()
bootstrap = (root / 'pmp-diagnostics-writer-trace-v1.js').read_text()
cert = (root / 'audit/a002-whole-app-diagnostics-v6.cjs').read_text()
gate = json.loads((root / 'audit/pass13/whole-app-bootstrap-contract-alignment-gate-v1.json').read_text())
receipt = json.loads((root / 'audit/pass13/receipts/RECEIPT_WHOLE_APP_BOOTSTRAP_CONTRACT_ALIGNMENT_20260803D_001.json').read_text())
assert gate['status'] == 'PASS'
assert receipt['status'] == 'PASS'
assert gate['required_bootstrap_version'] == '3.3.0-bounded-verified-bcd-publication-20260803C'
assert receipt['required_bootstrap_version'] == gate['required_bootstrap_version']
assert gate['classification_revision'] == '1.0.0-persisted-bug-backlog-informational-20260803E'
assert receipt['classification_revision'] == gate['classification_revision']
assert "const REQUIRED_BOOT_VERSION='3.3.0-bounded-verified-bcd-publication-20260803C';" in view
assert "const REQUIRED_BOOT_VERSION = '3.3.0-bounded-verified-bcd-publication-20260803C';" in cert
assert "function classifyPersistedBugBacklog(produced)" in bootstrap
assert "PERSISTED_BUG_BACKLOG_INFORMATIONAL" in bootstrap
assert "3.2.0-transactional-versioned-bcd-bootstrap-20260801B" not in view
print('PASS: Whole App bootstrap 3.3 alignment and bounded backlog classification independently verified')
