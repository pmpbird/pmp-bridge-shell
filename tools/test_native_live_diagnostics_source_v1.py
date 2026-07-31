#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "pmp-diagnostics-consolidated-view-v1.js"


def main() -> None:
    text = SOURCE.read_text("utf-8")
    checks = {
        "native_version": "2.3.0-native-live-receipts-20260730E" in text,
        "native_source_mode": "NATIVE_CONSOLIDATED_DIAGNOSTICS_SOURCE" in text,
        "pass_a_receipt": "pmp_diagnostic_coverage_pass_a_v1_receipt" in text,
        "passes_bcd_receipt": "pmp_diagnostic_coverage_passes_bcd_v1_receipt" in text,
        "warnings_empty": "warnings:[]" in text,
        "not_proven_empty": "not_proven:[]" in text,
        "missing_is_fail": "status:pass?'PASS':'FAIL'" in text,
        "legacy_version_absent": "2.1.0-section-health-rules-compact-summary-20260730A" not in text,
    }
    failed = [name for name, passed in checks.items() if not passed]
    assert not failed, failed
    print(f"PASS: native live diagnostics source ({len(checks)}/{len(checks)})")


if __name__ == "__main__":
    main()
