#!/usr/bin/env python3
from pathlib import Path

src = (Path(__file__).resolve().parents[1] / 'pmp-diagnostics-writer-trace-v1.js').read_text()
required = [
    "3.3.0-bounded-verified-bcd-publication-20260803C",
    "function boundedSection(row)",
    "function boundedReceipt(produced)",
    "function publishBounded(produced)",
    "NEW_EVALUATION_INCOMPLETE",
    "RECEIPT_PUBLICATION_FAILED",
    "publication_mode:publication.mode",
    "source_evaluation_status:produced.status",
]
missing = [token for token in required if token not in src]
assert not missing, f'missing bounded publication tokens: {missing}'
assert "if(!completeReceipt(produced))" in src
assert "if(!publication.ok)publication=publishBounded(produced)" in src
assert "NEW_RECEIPT_INCOMPLETE" not in src
print('PASS: complete B-D evaluations receive bounded verified publication instead of false rollback')
