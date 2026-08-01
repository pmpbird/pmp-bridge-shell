from pathlib import Path

SRC = Path('pmp-diagnostics-writer-trace-v1.js').read_text(encoding='utf-8')

assert "3.0.0-retired-layout-trace-button-20260801A" in SRC
assert "status:'RETIRED'" in SRC
assert "node.remove()" in SRC
assert "Compatibility stub only" in SRC
assert "createElement('button')" not in SRC
assert 'MutationObserver(' not in SRC
assert 'ResizeObserver(' not in SRC
assert 'setInterval(' not in SRC
assert 'URL.createObjectURL' not in SRC
assert "dom_writes:false" in SRC
assert "style_writes:false" in SRC
assert "navigation_changes:false" in SRC
print('REMOVE_WHOLE_APP_HEALTH_LAYOUT_TRACE_BUTTON_PASS')
