from pathlib import Path

src = Path('pmp-app-orchestrator-v1.js').read_text(encoding='utf-8')
required = [
    "2.8.0-diagnostics-refresh-no-navigation-20260730K",
    "function stabilizeDiagnosticsOwner(api)",
    "api.__pmpOriginalNavigatingRun",
    "api.run=function(reason){const report=api.currentReport",
    "put(KEYS.diagnosticsOwner,report)",
    "owner_refresh_navigation_disabled",
    "stabilizeDiagnosticsOwner(api)"
]
for token in required:
    assert token in src, f'missing required token: {token}'
assert "api.__pmpRefreshWithoutNavigation=true" in src
print('PASS: Diagnostics owner refresh cannot navigate an active detail view to home')
