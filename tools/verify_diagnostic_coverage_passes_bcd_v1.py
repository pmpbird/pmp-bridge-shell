from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
required = {
    'pmp-diagnostic-coverage-passes-bcd-v1.js': [
        'PMP_BRIDGE_LIVE_DIAGNOSTIC_V1',
        'PMP_LIBRARY_LIVE_DIAGNOSTIC_V1',
        'PMP_BANK_LIVE_DIAGNOSTIC_V1',
        'PMP_CONTINUOUS_RUN_LIVE_DIAGNOSTIC_V1',
        'PMP_ERRORS_VISUAL_LIVE_DIAGNOSTIC_V1',
        'persisted_user_data_write:false',
    ],
    'pmp-diagnostic-coverage-passes-bcd-integration-v1.js': [
        'patchWhole', 'patchFull', 'bridge_system', 'library_system',
        'bank_system', 'continuous_run_system',
        'errors_bug_watch_visual_stability',
    ],
    'pmp-diagnostic-coverage-final-certification-v1.js': [
        'all_sections_evaluated', 'SECTION_NOT_FULLY_EVALUATED',
        "x.status==='PASS'||x.status==='FAIL'",
    ],
    'pmp-app-orchestrator-v1.js': [
        'PMPDiagnosticCoveragePassesBCDV1',
        'PMPDiagnosticCoveragePassesBCDIntegrationV1',
        'PMPDiagnosticCoverageFinalCertificationV1',
        'bank_rebuild:false', 'continuous_run_mutation:false',
    ],
}

failures = []
for path, needles in required.items():
    text = (ROOT / path).read_text(encoding='utf-8')
    for needle in needles:
        if needle not in text:
            failures.append(f'{path}: missing {needle}')

if failures:
    raise SystemExit('\n'.join(failures))
print('diagnostic coverage passes B-C-D verification: PASS')
