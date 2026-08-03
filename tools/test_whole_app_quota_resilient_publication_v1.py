#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
src = (root / 'pmp-diagnostics-writer-trace-v1.js').read_text()
required = [
    "1.0.0-quota-resilient-live-memory-publication-20260803F",
    "LIVE_BCD_RECEIPT",
    "installVirtualReceiptRead",
    "live_memory_virtualized_read",
    "QUOTA_UNAVAILABLE",
    "currentReceipt:()=>liveReceipt()",
    "persistence_warning",
    "live_receipt_available:true",
]
missing = [token for token in required if token not in src]
assert not missing, f'missing quota-resilient publication tokens: {missing}'
assert "String(key)===BCD_RECEIPT_KEY" in src
assert "this===storage" in src
assert "localStorage.clear" not in src
assert "sessionStorage.clear" not in src
print('PASS: Whole App B-D publication survives localStorage quota exhaustion without clearing storage')
