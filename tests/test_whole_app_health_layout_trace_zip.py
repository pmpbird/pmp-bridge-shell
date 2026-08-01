from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "pmp-diagnostics-writer-trace-v1.js").read_text(encoding="utf-8")

REQUIRED = [
    "2.1.0-whole-app-health-layout-trace-zip-20260731P",
    "Download Whole App Health Layout Trace ZIP",
    "PMP_WHOLE_APP_HEALTH_LAYOUT_TRACE.json",
    "TRACE_METADATA.json",
    "application/zip",
    "0x04034b50",
    "0x02014b50",
    "0x06054b50",
    "downloadZip",
    "read_only:true",
    "dom_writes:false",
    "style_writes:false",
    "navigation_changes:false",
]

missing = [token for token in REQUIRED if token not in SOURCE]
assert not missing, f"missing ZIP export tokens: {missing}"
assert "navigator.clipboard.writeText" not in SOURCE
assert "pmpDiagRunningV1" not in SOURCE
print("WHOLE_APP_HEALTH_LAYOUT_TRACE_ZIP_TEST_PASS")
