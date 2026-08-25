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
# The 2026-08-03 gate/receipt remain immutable historical evidence. Current
# production must extend that bounded publication contract with exact freshness.
for token in [
    '3.4.0-fresh-evaluation-source-identity-20260825A',
    'function boundedReceipt(produced)',
    'function publishBounded(produced,evaluationId)',
    'RECEIPT_PUBLICATION_FAILED',
    'NEW_EVALUATION_INCOMPLETE',
    'runtime_context:produced.runtime_context||null',
    'source_identity:produced.source_identity||null',
    'evaluation_id:produced.evaluation_id||null',
]:
    assert token in src, token
assert 'classified.applied?publishBounded(produced):' not in src
assert 'NEW_RECEIPT_INCOMPLETE' not in src
print('PASS: historical bounded-publication evidence preserved and current evaluation-ID publication verified')
