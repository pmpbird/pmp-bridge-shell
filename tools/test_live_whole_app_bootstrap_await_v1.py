#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "pmp-diagnostics-consolidated-view-v1.js"
text = SOURCE.read_text(encoding="utf-8")

required = [
    "2.9.0-live-bootstrap-await-20260803A",
    "PMPCurrentBCDDiagnosticsBootstrapV1",
    "await boot.run(reason||'native_consolidated_diagnostics')",
    "REQUIRED_BOOT_VERSION='3.2.0-transactional-versioned-bcd-bootstrap-20260801B'",
    "REQUIRED_BCD_VERSION='1.1.0-final-two-live-proof-20260801A'",
    "completeBcd(br)",
    "whole.textContent='Running current live diagnostics…'",
    "await produceEvidence('copy_whole_app')",
]
for marker in required:
    assert marker in text, marker

for forbidden in [
    "const BCD_SRC='pmp-diagnostic-coverage-passes-bcd-v1.js?fresh=native-diagnostics-bootstrap-20260730G'",
    "await b.run('native_consolidated_diagnostics')",
]:
    assert forbidden not in text, forbidden

print("PASS: live Whole App Health awaits transactional B-D bootstrap")
