from pathlib import Path

trace = Path('pmp-diagnostics-writer-trace-v1.js').read_text(encoding='utf-8')
html = Path('pmp-current-inner-cleanbug-rgcontrols-v25.html').read_text(encoding='utf-8')
required = [
    "1.0.0-diagnostics-writer-trace-20260730L",
    "pmp_diagnostics_writer_trace_v1",
    "DIAGNOSTICS_WRITE_TRACE",
    "innerHTML_set",
    "replaceChildren",
    "insertAdjacentHTML",
    "Copy Writer Trace",
    "read_only:true",
]
for token in required:
    assert token in trace, f'missing trace contract: {token}'
assert html.index('pmp-diagnostics-writer-trace-v1.js') < html.index('pmp-app-orchestrator-v1.js')
for forbidden in ['location.replace(', 'localStorage.clear(', 'indexedDB.deleteDatabase(']:
    assert forbidden not in trace, f'forbidden mutation: {forbidden}'
print('PASS Diagnostics writer trace installs before App Orchestrator and remains read-only')
