from pathlib import Path

SRC = Path('pmp-diagnostics-writer-trace-v1.js').read_text(encoding='utf-8')

required = [
    "3.1.0-retired-trace-current-bcd-bootstrap-20260801A",
    "1.1.0-final-two-live-proof-20260801A",
    "PMPCurrentBCDDiagnosticsBootstrapV1",
    "API_VERSION_MISMATCH",
    "RECEIPT_VERSION_MISMATCH",
    "current-bcd-bootstrap-20260801A-",
    "localStorage.removeItem(BCD_RECEIPT_KEY)",
    "trace_ui:'retired'",
]
for token in required:
    assert token in SRC, token

for forbidden in [
    "createElement('button')",
    "MutationObserver(",
    "ResizeObserver(",
    "URL.createObjectURL",
]:
    assert forbidden not in SRC, forbidden

assert "owner_changes:false" in SRC
assert "helper_changes:false" in SRC
assert "route_changes:false" in SRC
assert "persisted_user_data_write:false" in SRC
print('CURRENT_BCD_DIAGNOSTICS_BOOTSTRAP_PASS')
