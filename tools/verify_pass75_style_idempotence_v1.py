#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "pmp-pass75-reload-runtime-platform-gate-v1.js").read_text(encoding="utf-8")

checks = {
    "style_id_constant": "STYLE_ID='pmp75ReloadGateStyle'" in SRC,
    "style_reused": "styles.shift()||document.createElement('style')" in SRC,
    "extra_styles_removed": "styles.forEach(node=>node.remove())" in SRC,
    "paint_does_not_append_style_markup": "css()+'<div id='" not in SRC,
    "paint_uses_ensure_style": "ensureStyle();let root=document.getElementById(ID)" in SRC,
    "release_removes_all_duplicates": "document.querySelectorAll('#'+STYLE_ID).forEach(s=>s.remove())" in SRC,
    "receipt_reports_style_count": "style_count:document.querySelectorAll('#'+STYLE_ID).length" in SRC,
}

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(f"{'PASS' if ok else 'FAIL'} {name}")
if failed:
    raise SystemExit("Pass75 style idempotence verification failed: " + ", ".join(failed))
print("PASS Pass75 reload gate style injection is idempotent")
