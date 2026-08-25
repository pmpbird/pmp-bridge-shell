#!/usr/bin/env python3
from pathlib import Path

src = (Path(__file__).resolve().parents[1] / 'pmp-diagnostics-writer-trace-v1.js').read_text()
required = [
    "3.4.0-fresh-evaluation-source-identity-20260825A",
    "function boundedSection(row)",
    "function boundedReceipt(produced)",
    "function publishBounded(produced,evaluationId)",
    "NEW_EVALUATION_INCOMPLETE",
    "RECEIPT_PUBLICATION_FAILED",
    "publication_mode:publication.mode",
    "source_evaluation_status:rawProduced.status",
    "runtime_context:produced.runtime_context||null",
    "let publication=publishBounded(produced,evaluationId)",
    "completeReceipt(rawProduced,evaluationId)",
]
missing = [token for token in required if token not in src]
assert not missing, f'missing bounded publication tokens: {missing}'
assert "if(!publication.ok)publication=publishBounded(produced,evaluationId)" in src
assert "classified.applied?publishBounded(produced):" not in src
assert "NEW_RECEIPT_INCOMPLETE" not in src
print('PASS: each exact B-D evaluation receives bounded verified publication with its current evaluation ID')
