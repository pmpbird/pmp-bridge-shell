#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
expected = {
    "revision": "1.4.0-fresh-evaluation-source-identity-20260825A",
    "source": "pmp-diagnostic-coverage-passes-bcd-v1-1-1-0-fresh-evaluation-20260825A.js",
    "bootstrap": "3.4.0-fresh-evaluation-source-identity-20260825A",
    "view": "2.9.2-fresh-bcd-evaluation-binding-20260825A",
}
evaluator = (ROOT / expected["source"]).read_text("utf-8")
boot = (ROOT / "pmp-diagnostics-writer-trace-v1.js").read_text("utf-8")
view = (ROOT / "pmp-diagnostics-consolidated-view-v1.js").read_text("utf-8")
whole_cert = (ROOT / "audit/a002-whole-app-diagnostics-v6.cjs").read_text("utf-8")
fresh_cert = (ROOT / "audit/a002-bcd-fresh-evaluation-source-identity-v1.cjs").read_text("utf-8")
assert f"const REV='{expected['revision']}';" in evaluator
assert f"const SOURCE_ID='{expected['source']}';" in evaluator
assert f"const V='{expected['bootstrap']}';" in boot
assert f"const V='{expected['view']}';" in view
assert "API_SOURCE_IDENTITY_MISMATCH" in boot
assert "RECEIPT_PUBLICATION_FAILED" in boot
assert "fresh_evaluation_bound" in view
assert "const REQUIRED_BOOT_VERSION = '3.4.0-fresh-evaluation-source-identity-20260825A';" in whole_cert
assert "const DIAGNOSTICS_TAB = '#pmpDiagnosticsTabBtn';" in fresh_cert
assert fresh_cert.index("locator(DIAGNOSTICS_TAB).click") < fresh_cert.index("locator(DIAGNOSTICS_SCREEN).waitFor")
assert fresh_cert.index("locator(DIAGNOSTICS_SCREEN).waitFor") < fresh_cert.index("locator(WHOLE_APP_CARD).click")
assert fresh_cert.index("locator(WHOLE_APP_CARD).click") < fresh_cert.index("locator(WHOLE_APP_COPY).click")

manifest_path = ROOT / "pmp-runtime-integrity-manifest-v1.json"
seal_path = ROOT / "audit/a003-manifest-seal.json"
root_path = ROOT / "pmp-app-current.html"
manifest_bytes = manifest_path.read_bytes()
manifest = json.loads(manifest_bytes)
seal = json.loads(seal_path.read_text("utf-8"))
index = {row["path"]: row for row in manifest["records"]}
for relative in [
    expected["source"],
    "pmp-diagnostics-writer-trace-v1.js",
    "pmp-diagnostics-consolidated-view-v1.js",
]:
    data = (ROOT / relative).read_bytes()
    row = index[relative]
    assert row["bytes"] == len(data)
    assert row["sha256_hex"] == hashlib.sha256(data).hexdigest()
digest = hashlib.sha256(manifest_bytes).hexdigest()
assert seal["manifest_sha256"] == digest
root = root_path.read_text("utf-8")
match = re.search(r"const MANIFEST_SHA256='([0-9a-f]{64})';", root)
assert match and match.group(1) == digest

receipt = json.loads((ROOT / "audit/pass13/receipts/RECEIPT_BCD_FRESH_EVALUATION_SOURCE_IDENTITY_20260825A_001.json").read_text("utf-8"))
assert receipt["status"] == "PASS"
assert receipt["repair"]["immutable_evaluator_source"] == expected["source"]
assert receipt["verification"]["exact_ui_path"] == [
    "Diagnostics bottom tab",
    "Whole App Health",
    "Copy Whole App Health Report",
]
assert receipt["verification"]["a002_pr_head_proof"] == "REQUIRED"
assert receipt["boundaries"] == {
    "bank_rebuild": False,
    "continuous_run_mutation": False,
    "dom_repair": False,
    "forced_pass": False,
    "helper_changes": False,
    "owner_changes": False,
    "persisted_user_data_delete": False,
    "persisted_user_data_write": False,
    "read_only": True,
    "route_changes": False,
    "storage_migration": False,
}
print("PASS: independent B-D freshness/source identity, maintenance alignment, and exact UI-path verifier")
