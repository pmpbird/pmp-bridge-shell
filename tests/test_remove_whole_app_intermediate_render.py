from pathlib import Path

SRC = Path('pmp-diagnostics-consolidated-view-v1.js').read_text()


def test_deferred_open_contract():
    assert "2.7.0-deferred-whole-app-open-20260731O" in SRC
    assert "openWholeAppWhenReady" in SRC
    assert "Preparing Whole App Health" in SRC
    assert "renderDetail(w,d,'whole_app',true)" in SRC
    assert "pmpDiagRunningV1" not in SRC
    assert "host.innerHTML='<button type=\"button\" class=\"pmpDiagBack\" id=\"pmpDiagBack\">← Back to Diagnostics</button><h1 class=\"pmpDiagTitle\">Whole App Health</h1>" not in SRC


def test_authority_boundaries_unchanged():
    assert "ownership_changes:false" in SRC
    assert "helper_changes:false" in SRC
    assert "route_changes:false" in SRC
    assert "storage_migration:false" in SRC
