from pathlib import Path

SOURCE = Path('pmp-diagnostics-bottom-tab-forcer-v1.js').read_text()

required = [
    "1.2.0-event-driven-whole-app-window-20260801B",
    "MutationObserver",
    "presentWholeApp",
    "pmpWholeAppHealthReportWindow",
    "scrollbar-gutter:stable both-edges",
    "recurring_health_repaint:false",
    "diagnostics_screen_style_write:'none'",
]
for token in required:
    assert token in SOURCE, token

for forbidden in [
    "host.style.paddingTop",
    "styleWholeAppHealth",
    "padding-top:82px",
    "setInterval(presentWholeApp",
]:
    assert forbidden not in SOURCE, forbidden

assert SOURCE.count("box=d.createElement('div')") == 1
assert "observer.observe(root,{subtree:true,childList:true,attributes:true,attributeFilter:['class']})" in SOURCE
print('PASS: Whole App Health uses one event-driven stable report window')
