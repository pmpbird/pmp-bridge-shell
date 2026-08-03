#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
src = (root / 'pmp-diagnostics-writer-trace-v1.js').read_text()
gate = json.loads((root / 'audit/pass13/bcd-bounded-receipt-publication-gate-v1.json').read_text())
receipt = json.loads((root / 'audit/pass13/receipts/RECEIPT_BCD_BOUNDED_RECEIPT_PUBLICATION_20260803C_001.json').read_text())

assert gate['status'] == 'PASS'
assert receipt['status'] == 'PASS'
assert gate['no_blind_flying_gate']['upload_before_enforcement'] is True
assert gate['no_blind_flying_gate']['automatic_retry'] is False
assert gate['claim_ceiling']
for token in [
    '3.3.0-bounded-verified-bcd-publication-20260803C',
    'function boundedReceipt(produced)',
    'function publishBounded(produced)',
    'RECEIPT_PUBLICATION_FAILED',
    'NEW_EVALUATION_INCOMPLETE',
]:
    assert token in src, token
assert 'NEW_RECEIPT_INCOMPLETE' not in src
print('PASS: bounded B-D publication gate, receipt, implementation and claim ceiling verified')
