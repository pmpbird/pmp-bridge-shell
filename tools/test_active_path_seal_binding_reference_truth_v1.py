#!/usr/bin/env python3
from pathlib import Path

s = Path("pmp-active-path-discovery-machine-v1.js").read_text("utf-8")
checks = {
    "version": "1.5.0-served-a003-reference-truth-20260826A" in s,
    "revision": "1.1.0-served-a003-reference-truth-20260826A" in s,
    "served_manifest": "SERVED_A003_MANIFEST" in s and "response.arrayBuffer()" in s and "crypto.subtle.digest('SHA-256',bytes)" in s,
    "no_route_receipt_integrity": "function integrityEvidence()" not in s and "pmp_route_guardian_v22_receipt" not in s,
    "scan_bound": "integrity.scan_id===requestedScanId" in s,
    "comment_strip": "function stripStaticComments(text,path)" in s,
    "path_aware_extract": "extract(text,item.path)" in s,
    "weak_outputs": "!/^(?:metadata|packet|report)\\.json$/i.test(c)" in s,
    "strong_fetch": "(?:fetch|importScripts|import)" in s,
    "freeze_integrity": "policy.map_fetch_ok&&integrity.fetch_ok&&!!integrity.manifest_sha256" in s,
    "boundaries": "persisted_user_data_write:'not_attempted'" in s and "reroute:'not_attempted'" in s,
}
failed = [k for k, v in checks.items() if not v]
print({"status": "PASS" if not failed else "FAIL", "checks": checks, "failed": failed})
raise SystemExit(1 if failed else 0)
