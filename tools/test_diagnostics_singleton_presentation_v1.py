from pathlib import Path

src = Path('pmp-app-orchestrator-v1.js').read_text(encoding='utf-8')
required = [
    "2.7.0-singleton-diagnostics-presentation-20260730J",
    "version:'2.6.0-single-final-health-render-20260730I'",
    "singleton:true",
    "singleton_already_active",
    "function contexts()",
    "function loadedScript(path)",
    "!api.__pmpSingletonInstalled",
    "singleton_enforced:true",
]
for token in required:
    assert token in src, f'missing required token: {token}'
assert "version:'2.3.0-native-live-receipts-20260730E'" not in src
assert "owner_changes:false" in src
assert "persisted_user_data_write:false" in src
print('PASS: consolidated Diagnostics presentation is singleton-safe')
