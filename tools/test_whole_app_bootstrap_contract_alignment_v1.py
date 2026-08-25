#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
view = (root / 'pmp-diagnostics-consolidated-view-v1.js').read_text()
bootstrap = (root / 'pmp-diagnostics-writer-trace-v1.js').read_text()
cert = (root / 'audit/a002-whole-app-diagnostics-v6.cjs').read_text()
required_view = [
    "2.9.2-fresh-bcd-evaluation-binding-20260825A",
    "3.4.0-fresh-evaluation-source-identity-20260825A",
    "1.4.0-fresh-evaluation-source-identity-20260825A",
    "pmp-diagnostic-coverage-passes-bcd-v1-1-1-0-fresh-evaluation-20260825A.js",
    "expectedEvaluationId=bootResult&&bootResult.evaluation_id||null",
    "fresh_evaluation_bound=freshBound",
]
required_bootstrap = [
    "1.0.0-persisted-bug-backlog-informational-20260803E",
    "function classifyPersistedBugBacklog(produced)",
    "PERSISTED_BUG_BACKLOG_INFORMATIONAL",
    "Persisted Bug Watch backlog is reported but does not fail current app health",
    "persisted_bug_backlog_classification_applied:classified.applied",
    "requiredRevision:REQUIRED_BCD_REVISION",
    "requiredSourceIdentity:REQUIRED_BCD_SOURCE_IDENTITY",
]
required_cert = [
    "const REQUIRED_BOOT_VERSION = '3.4.0-fresh-evaluation-source-identity-20260825A';",
    "const REQUIRED_BCD_REVISION = '1.4.0-fresh-evaluation-source-identity-20260825A';",
    "const REQUIRED_BCD_SOURCE = 'pmp-diagnostic-coverage-passes-bcd-v1-1-1-0-fresh-evaluation-20260825A.js';",
    "state.bcdReceipt?.evaluation_id===evaluationId",
]
missing_view = [token for token in required_view if token not in view]
missing_bootstrap = [token for token in required_bootstrap if token not in bootstrap]
missing_cert = [token for token in required_cert if token not in cert]
assert not missing_view, f'missing aligned fresh-evaluation view tokens: {missing_view}'
assert not missing_bootstrap, f'missing current bootstrap tokens: {missing_bootstrap}'
assert not missing_cert, f'missing current browser certification tokens: {missing_cert}'
assert "3.2.0-transactional-versioned-bcd-bootstrap-20260801B" not in view
assert "const REQUIRED_BOOT_VERSION = '3.3.0-bounded-verified-bcd-publication-20260803C';" not in cert
assert "ACTIVE_BUGS_REMAIN" in bootstrap
assert "issues.every(issue=>String(issue&&issue.code||'')==='ACTIVE_BUGS_REMAIN')" in bootstrap
assert "duplicate_id_count||0)===0" in bootstrap
assert "journal_present===true" in bootstrap
print('PASS: Whole App Health awaits bootstrap 3.4 and binds exact B-D revision, source, and evaluation ID')
