from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "pmp-diagnostics-writer-trace-v1.js").read_text(encoding="utf-8")
receipt = json.loads((ROOT / "receipts/whole_app_health_layout_trace_20260731N.json").read_text(encoding="utf-8"))
required = [
    "PMP_WHOLE_APP_HEALTH_LAYOUT_TRACE_V1",
    "Whole App Health Layout Trace",
    "Copy Whole App Health Layout Trace",
    "getBoundingClientRect",
    "getComputedStyle",
    "visualViewport",
]
missing = [token for token in required if token not in source]
assert not missing, missing
assert receipt["status"] == "READY_FOR_RUNTIME_VERIFICATION"
assert receipt["boundaries"]["read_only"] is True
print("WHOLE_APP_HEALTH_LAYOUT_TRACE_SOURCE_PASS")
