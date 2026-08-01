#!/usr/bin/env python3
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "pmp-diagnostics-consolidated-view-v1.js"
text = SOURCE.read_text(encoding="utf-8")

required = [
    "2.8.0-stable-health-skeleton-20260731Q",
    "function renderWholeAppPending",
    "data-pmp-health-pending=\"true\"",
    "— CHECKING",
    "scrollbar-gutter:stable both-edges",
    "pmpDiagWholeAppStableV1",
    "renderWholeAppPending(w,d);await produceEvidence('whole_app_open')",
]
for token in required:
    assert token in text, f"missing required stable-skeleton token: {token}"

forbidden = [
    "label.textContent='Preparing Whole App Health'",
    "sub.textContent='Running current live diagnostics before opening…'",
]
for token in forbidden:
    assert token not in text, f"old intermediate-card mutation remains: {token}"

print("PASS: Whole App Health opens in stable final geometry without mutating the home card")
