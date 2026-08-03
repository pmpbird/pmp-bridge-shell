#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
view = (root / 'pmp-diagnostics-consolidated-view-v1.js').read_text()
bootstrap = (root / 'pmp-diagnostics-writer-trace-v1.js').read_text()
cert = (root / 'audit/a002-whole-app-diagnostics-v6.cjs').read_text()
required_view = [
    "2.9.1-bootstrap-contract-alignment-20260803D",
    "3.3.0-bounded-verified-bcd-publication-20260803C",
    "const REQUIRED_BOOT_VERSION=",
    "boot.version!==REQUIRED_BOOT_VERSION",
    "await boot.run(reason||'native_consolidated_diagnostics')",
]
required_bootstrap = [
    "1.0.0-persisted-bug-backlog-informational-20260803E",
    "function classifyPersistedBugBacklog(produced)",
    "PERSISTED_BUG_BACKLOG_INFORMATIONAL",
    "Persisted Bug Watch backlog is reported but does not fail current app health",
    "persisted_bug_backlog_classification_applied:classified.applied",
]
missing_view = [token for token in required_view if token not in view]
missing_bootstrap = [token for token in required_bootstrap if token not in bootstrap]
assert not missing_view, f'missing aligned bootstrap contract tokens: {missing_view}'
assert not missing_bootstrap, f'missing persisted backlog classification tokens: {missing_bootstrap}'
assert "3.2.0-transactional-versioned-bcd-bootstrap-20260801B" not in view
assert "const REQUIRED_BOOT_VERSION = '3.3.0-bounded-verified-bcd-publication-20260803C';" in cert
assert "ACTIVE_BUGS_REMAIN" in bootstrap
assert "issues.every(issue=>String(issue&&issue.code||'')==='ACTIVE_BUGS_REMAIN')" in bootstrap
assert "duplicate_id_count||0)===0" in bootstrap
assert "journal_present===true" in bootstrap
print('PASS: Whole App Health awaits bootstrap 3.3 and treats only persisted bug backlog as informational')
