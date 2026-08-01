from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "pmp-diagnostics-writer-trace-v1.js"


def test_layout_trace_contract():
    text = SOURCE.read_text(encoding="utf-8")
    required = [
        "PMP_WHOLE_APP_HEALTH_LAYOUT_TRACE_V1",
        "Whole App Health Layout Trace",
        "Copy Whole App Health Layout Trace",
        "getBoundingClientRect",
        "getComputedStyle",
        "visualViewport",
        "fonts_loadingdone",
        "DURATION_MS=5000",
        "read_only:true",
        "dom_writes:false",
        "style_writes:false",
        "navigation_changes:false",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, f"missing layout trace contract tokens: {missing}"
    assert "Copy Writer Trace" not in text
    assert "PMP_DIAGNOSTICS_WRITER_TRACE_REPORT_V1" not in text
