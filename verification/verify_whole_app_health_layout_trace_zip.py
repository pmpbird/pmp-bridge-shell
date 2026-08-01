from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "pmp-diagnostics-writer-trace-v1.js").read_text(encoding="utf-8")
scope = json.loads((ROOT / "exact_scope/P13_WHOLE_APP_HEALTH_LAYOUT_TRACE_ZIP_EXACT_SCOPE.json").read_text(encoding="utf-8"))
receipt = json.loads((ROOT / "receipts/whole_app_health_layout_trace_zip_20260731P.json").read_text(encoding="utf-8"))

required = [
    "Download Whole App Health Layout Trace ZIP",
    "PMP_WHOLE_APP_HEALTH_LAYOUT_TRACE.json",
    "TRACE_METADATA.json",
    "application/zip",
    "zipStored",
    "downloadZip",
]
missing = [token for token in required if token not in source]
assert not missing, missing
assert scope["required_behavior"]["external_zip_dependency"] is False
assert scope["required_behavior"]["read_only_trace"] is True
assert receipt["status"] == "READY_FOR_RUNTIME_VERIFICATION"
assert receipt["boundaries"]["read_only"] is True
print("WHOLE_APP_HEALTH_LAYOUT_TRACE_ZIP_SOURCE_PASS")
