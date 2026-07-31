from pathlib import Path

SOURCE = Path('pmp-diagnostics-consolidated-view-v1.js')
text = SOURCE.read_text(encoding='utf-8')

required = [
    "const V='2.5.0-preserve-active-diagnostics-view-20260730H'",
    "let ORIGINAL_RENDER_HOME=null,EVIDENCE_RUN=null,ACTIVE_VIEW='home',ACTIVE_CONTEXT=null;",
    "function remember(view,w,d)",
    "if(ACTIVE_VIEW==='whole_app'",
    "docs().forEach(c=>ensureStyles(c.document));",
    "Installation and evidence retries never navigate the user."
]
for token in required:
    assert token in text, f'missing required token: {token}'

for forbidden in [
    "if(host&&host.classList.contains('on'))renderHome",
    "if (host && host.classList.contains('on')) renderHome"
]:
    assert forbidden not in text, f'forbidden forced-home behavior present: {forbidden}'

print('PASS diagnostics active-view preservation source contract')
