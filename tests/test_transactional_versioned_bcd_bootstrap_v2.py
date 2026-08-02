from pathlib import Path

BOOT = Path('pmp-diagnostics-writer-trace-v1.js').read_text(encoding='utf-8')
PINNED = Path('pmp-diagnostic-coverage-passes-bcd-v1-1-1-0.js').read_text(encoding='utf-8')

required = [
    "3.2.0-transactional-versioned-bcd-bootstrap-20260801B",
    "pmp-diagnostic-coverage-passes-bcd-v1-1-1-0.js",
    "const previous=read(BCD_RECEIPT_KEY)",
    "restore(previous)",
    "completeReceipt",
    "NEW_RECEIPT_INCOMPLETE",
    "rollback_applied:true",
    "transactional:true",
]
for token in required:
    assert token in BOOT, token

assert "localStorage.removeItem(BCD_RECEIPT_KEY)" not in BOOT
assert "createElement('button')" not in BOOT
assert 'MutationObserver(' not in BOOT
assert "1.1.0-final-two-live-proof-20260801A" in PINNED
for section in [
    'bridge_system',
    'library_system',
    'bank_system',
    'continuous_run_system',
    'errors_bug_watch_visual_stability',
]:
    assert section in PINNED, section

print('PASS transactional cache-proof BCD bootstrap')
