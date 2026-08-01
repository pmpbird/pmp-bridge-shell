from pathlib import Path

SRC = Path('pmp-diagnostics-writer-trace-v1.js').read_text()

required = [
    "2.2.0-attachment-proof-layout-trace-20260801A",
    "Whole App Health Layout Trace v2",
    "PMP_WHOLE_APP_HEALTH_LAYOUT_TRACE_V2",
    "ATTACHMENT_FAILED",
    "renderer_versions",
    "healthPending",
    "whole_app_health_click",
    "text:textOf(el)",
]

for token in required:
    assert token in SRC, token

assert "dom_writes:false" in SRC
assert "style_writes:false" in SRC
assert "navigation_changes:false" in SRC
print('PASS')
