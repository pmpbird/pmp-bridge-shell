#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
evaluator = (ROOT / "pmp-diagnostic-coverage-passes-bcd-v1-1-1-0-fresh-evaluation-20260825A.js").read_text("utf-8")
boot = (ROOT / "pmp-diagnostics-writer-trace-v1.js").read_text("utf-8")
view = (ROOT / "pmp-diagnostics-consolidated-view-v1.js").read_text("utf-8")

required = {
    "evaluator_revision": "1.4.0-fresh-evaluation-source-identity-20260825A" in evaluator,
    "evaluator_source_identity": "sourceIdentity:SOURCE_ID" in evaluator and "source_identity:SOURCE_ID" in evaluator,
    "evaluator_request_id": "evaluation_id:meta.evaluation_id" in evaluator,
    "bootstrap_version": "3.4.0-fresh-evaluation-source-identity-20260825A" in boot,
    "bootstrap_exact_api": "function apiMatches(api)" in boot and "requiredSourceIdentity:REQUIRED_BCD_SOURCE_IDENTITY" in boot,
    "bootstrap_always_publishes": "let publication=publishBounded(produced,evaluationId)" in boot,
    "bootstrap_evaluation_match": "value.evaluation_id===evaluationId" in boot,
    "bounded_receipt_preserves_context": "runtime_context:produced.runtime_context||null" in boot,
    "view_version": "2.9.2-fresh-bcd-evaluation-binding-20260825A" in view,
    "view_exact_binding": "fresh_evaluation_bound=freshBound" in view and "br.evaluation_id===expectedEvaluationId" in view,
    "read_only_boundaries": "persisted_user_data_write:false" in evaluator and "storage_migration:false" in boot,
}
failed = [name for name, ok in required.items() if not ok]
if failed:
    raise SystemExit("FAIL: " + ", ".join(failed))
forbidden = [
    "classified.applied?publishBounded(produced):",
    "localStorage.clear",
    "sessionStorage.clear",
    "indexedDB.deleteDatabase",
]
combined = evaluator + "\n" + boot + "\n" + view
present = [token for token in forbidden if token in combined]
if present:
    raise SystemExit("FAIL forbidden: " + ", ".join(present))
for path in [
    ROOT / "pmp-diagnostic-coverage-passes-bcd-v1-1-1-0-fresh-evaluation-20260825A.js",
    ROOT / "pmp-diagnostics-writer-trace-v1.js",
    ROOT / "pmp-diagnostics-consolidated-view-v1.js",
    ROOT / "audit/a002-bcd-fresh-evaluation-source-identity-v1.cjs",
]:
    subprocess.run(["node", "--check", str(path)], cwd=ROOT, check=True)
print(f"PASS: B-D fresh evaluation/source identity ({len(required)}/{len(required)})")
