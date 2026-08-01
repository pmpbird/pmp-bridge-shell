from pathlib import Path


def test_bottom_tab_forcer_has_no_whole_app_health_layout_authority():
    source = Path('pmp-diagnostics-bottom-tab-forcer-v1.js').read_text()
    forbidden = [
        'function styleWholeAppHealth',
        "host.style.paddingTop='82px'",
        'pmpWholeAppHealthReportWindow',
        'moving.forEach',
        "whole_app_health_white_scroll_window",
    ]
    for token in forbidden:
        assert token not in source, token
    assert "whole_app_health_presentation:'not_owned_not_modified'" in source
    assert "diagnostics_screen_style_write:'forbidden'" in source
    assert "diagnostics_report_node_move:'forbidden'" in source
