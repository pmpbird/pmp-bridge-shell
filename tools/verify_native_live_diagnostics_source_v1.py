#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "audit/pass13/receipts/RECEIPT_NATIVE_LIVE_DIAGNOSTICS_SOURCE_20260730E_001.json"


def main() -> None:
    output = subprocess.check_output(
        ["python3", "tools/test_native_live_diagnostics_source_v1.py"],
        cwd=ROOT,
        text=True,
    )
    assert output.startswith("PASS:"), output
    receipt = json.loads(RECEIPT.read_text("utf-8"))
    assert receipt["status"] == "PASS"
    assert receipt["source_mode"] == "NATIVE_CONSOLIDATED_DIAGNOSTICS_SOURCE"
    assert receipt["whole_app_health_version"] == "2.3.0-native-live-receipts-20260730E"
    print("PASS: native live diagnostics source verifier")


if __name__ == "__main__":
    main()
