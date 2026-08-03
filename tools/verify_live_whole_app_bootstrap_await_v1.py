#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
subprocess.run(["python3", str(ROOT / "tools/test_live_whole_app_bootstrap_await_v1.py")], cwd=ROOT, check=True)
receipt = json.loads((ROOT / "audit/pass13/receipts/RECEIPT_LIVE_WHOLE_APP_BOOTSTRAP_AWAIT_20260803A_001.json").read_text())
gate = json.loads((ROOT / "audit/pass13/live-whole-app-bootstrap-await-gate-v1.json").read_text())
assert receipt["status"] == "PASS"
assert gate["status"] == "PASS"
assert gate["unit_id"] == "P13-U23"
assert gate["scope"]["implementation_paths"] == ["pmp-diagnostics-consolidated-view-v1.js"]
print("PASS: live Whole App bootstrap await package verified")
