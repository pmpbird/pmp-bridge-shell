from pathlib import Path

src = Path('pmp-diagnostics-consolidated-view-v1.js').read_text()
assert "2.6.0-single-final-health-render-20260730I" in src
assert "if(id==='whole_app'&&!evidenceReady){renderWholeAfterEvidence" in src
assert "!read(AKEY)&&!read(BKEY)" not in src
assert "Running current live diagnostics…" in src
assert "renderDetail(w,d,'whole_app',true)" in src
print('PASS: Whole App Health renders only after the current evidence run completes')
