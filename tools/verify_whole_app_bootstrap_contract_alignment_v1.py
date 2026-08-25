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
# The 3.3 gate is retained as immutable historical evidence. Current source and
# current A-002 certification must require the superseding exact-identity 3.4 contract.
assert "const REQUIRED_BOOT_VERSION='3.4.0-fresh-evaluation-source-identity-20260825A';" in view
assert "const REQUIRED_BCD_REVISION='1.4.0-fresh-evaluation-source-identity-20260825A';" in view
assert "const REQUIRED_BCD_SOURCE_IDENTITY='pmp-diagnostic-coverage-passes-bcd-v1-1-1-0-fresh-evaluation-20260825A.js';" in view
assert "const REQUIRED_BOOT_VERSION = '3.4.0-fresh-evaluation-source-identity-20260825A';" in cert
assert "const REQUIRED_BCD_REVISION = '1.4.0-fresh-evaluation-source-identity-20260825A';" in cert
assert "state.bcdReceipt?.evaluation_id===evaluationId" in cert
assert "function classifyPersistedBugBacklog(produced)" in bootstrap
assert "PERSISTED_BUG_BACKLOG_INFORMATIONAL" in bootstrap
assert "fresh_evaluation_bound=freshBound" in view
assert "3.2.0-transactional-versioned-bcd-bootstrap-20260801B" not in view
print('PASS: historical 3.3 evidence preserved while current Whole App certification enforces exact 3.4 identity')
