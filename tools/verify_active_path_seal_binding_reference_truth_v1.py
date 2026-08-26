#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

p = subprocess.run([sys.executable, "tools/test_active_path_seal_binding_reference_truth_v1.py"], text=True, capture_output=True)
if p.returncode:
    print(p.stdout)
    print(p.stderr, file=sys.stderr)
    raise SystemExit(p.returncode)

gate = json.loads(Path("audit/pass13/active-path-seal-binding-reference-truth-gate-v1.json").read_text("utf-8"))
receipt = json.loads(Path("audit/pass13/receipts/RECEIPT_ACTIVE_PATH_SEAL_BINDING_REFERENCE_TRUTH_20260826A_001.json").read_text("utf-8"))
assert gate["no_blind_flying_gate"]["automatic_retry"] is False
assert gate["scope"]["implementation_paths"] == ["pmp-active-path-discovery-machine-v1.js", "pmp-app-current.html"]
assert receipt["verification"]["user_device_proof"] == "REQUIRED_AFTER_DEPLOYMENT"
for obj in (gate, receipt):
    b = obj.get("boundaries", {})
    assert b.get("owner_changes") is False
    assert b.get("helper_changes") is False
    assert b.get("route_changes") is False
    assert b.get("storage_migration") is False
    assert b.get("persisted_user_data_write") is False
print({"status": "PASS", "deterministic": True, "boundary_verification": True})
