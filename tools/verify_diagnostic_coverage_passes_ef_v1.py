#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
required = {
    'pmp-diagnostic-coverage-pass-e-integration-v1.js': ['PMP_DIAGNOSTIC_COVERAGE_PASS_E_V1', 'SECTION_EVIDENCE_MISMATCH', 'BANK_CONTINUOUS_RUN_COLLAPSED'],
    'pmp-diagnostic-coverage-pass-f-handoff-certification-v1.js': ['PMP_DIAGNOSTIC_COVERAGE_PASS_F_V1', 'HANDOFF_DIAGNOSTIC_SECTION_MISSING', 'PACKAGE_HASH_RULE_MISSING'],
    'pmp-new-chat-safe-handoff-pass-ef-integration-v1.js': ['diagnostic_completion', 'pass_e_cross_system_integration', 'pass_f_safe_handoff_certification'],
    'pmp-diagnostic-coverage-final-certification-v1.js': ['PASS_E_RECEIPT_MISSING', 'PASS_F_RECEIPT_MISSING', 'final-certification-through-pass-f'],
    'pmp-app-orchestrator-v1.js': ['PMPDiagnosticCoveragePassEV1', 'PMPDiagnosticCoveragePassFV1', 'PMPNewChatSafeHandoffPassEFIntegrationV1'],
}
errors = []
for name, tokens in required.items():
    path = ROOT / name
    if not path.exists():
        errors.append(f'missing file: {name}')
        continue
    text = path.read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{name}: missing token {token}')

orch = (ROOT / 'pmp-app-orchestrator-v1.js').read_text(encoding='utf-8')
order = ['PMPDiagnosticCoveragePassEV1', 'PMPNewChatSafeHandoffV1', 'PMPNewChatSafeHandoffPassEFIntegrationV1', 'PMPDiagnosticCoveragePassFV1', 'PMPDiagnosticCoverageFinalCertificationV1']
pos = [orch.find(token) for token in order]
if any(x < 0 for x in pos) or pos != sorted(pos):
    errors.append('App Orchestrator Pass E/F load order is incomplete or incorrect')

for forbidden in ['owner reassignment', 'storage migration attempted', 'persisted user data write attempted']:
    for name in required:
        if forbidden in (ROOT / name).read_text(encoding='utf-8').lower():
            errors.append(f'{name}: forbidden mutation language found')

if errors:
    print('FAIL')
    for error in errors:
        print('-', error)
    raise SystemExit(1)
print('PASS: diagnostic coverage Pass E and Pass F integration verified')
