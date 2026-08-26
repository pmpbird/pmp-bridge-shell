#!/usr/bin/env python3
from pathlib import Path
import re

SRC = Path('pmp-mount-registry-v1.js').read_text(encoding='utf-8')
EXPECTED_VERSION = '1.7.0-registry-completeness-semantics-20260826A'

CURRENT_REQUIRED = {
    'pmp-runtime-integrity-manifest-v1.json',
    'pmp-integrity-service-worker-v1.js',
    'pmp-app-orchestrator-ownership-registry-v1.json',
}
SUPPORT_REQUIRED = {
    'code-safety-v13.html',
    'pmp-current-inner-cleanbug-rgcontrols-v2.html',
    'resident.html',
    'code-safety.html',
    'pmp-route-guardian-v1.js',
    'pmp.html',
    'safe-writer.html',
    'safety.html',
}
RECOVERY_REQUIRED = {
    'pmp-route-guardian-last-good-clean-v1.js',
    'pmp-current-inner-cleanbug-rgcontrols-v16.html',
    'pmp-route-guardian-last-good-v3-button-v1.js',
    'pmp-route-guardian-last-good-v1.html',
    'pmp-route-guardian-last-good-v18.html',
    'pmp-route-guardian-recovery-tools-v8.html',
    'pmp-move-ledger-candidate-follow-v1.html',
    'pmp-route-guardian-current-loader-v14.html',
    'pmp-current-inner-cleanbug-rgcontrols-v9.html',
    'pmp-current-inner-cleanbug-rgcontrols-v13.html',
}
INTENTIONAL_OUTSIDE = {
    'GO_TO_SAFETY.html',
    'Index.html',
    'automation/controller/v1/controller-contract.json',
    'automation/engine/v1/engine-policy.json',
    'automation/engine/v1/free-in-app-engine-contract.json',
    'automation/engine/v1/universal-contract.json',
    'automation/plans/packet-01-5.v1.json',
    'automation/state/active-plan.json',
    'automation/state/controller-status.json',
    'automation/state/free-in-app-engine-status.json',
    'automation/state/usage-ledger.json',
    'bm.html',
    'bridge-cloak.html',
    'bug-memory-current-clean-v2.html',
    'bug-memory-hub-link-v1.html',
    'hard-fresh.html',
    'pmp-continuous-run-helper-conflict-blocker-v1.js',
    'pmp-current-inner.html',
    'pmp-helper-bank-live-inspector-v1.js',
    'pmp-helper-symptom-watcher-v1.js',
    'pmp-inventory-eyes-manifest-v1.0.0.json',
    'pmp-p15-helper-tidy-v1.js',
}

def list_block(name: str):
    m = re.search(rf"const {name}=list\(`(.*?)`\);", SRC, re.S)
    assert m, f'missing {name} block'
    return {x for x in m.group(1).split() if x}

assert f"const V='{EXPECTED_VERSION}'" in SRC
current = list_block('STATIC_CURRENT')
support = list_block('SUPPORT_REACHABLE')
recovery = list_block('RECOVERY_REACHABLE')
outside = list_block('INTENTIONAL_OUTSIDE')

assert CURRENT_REQUIRED <= current
assert SUPPORT_REQUIRED <= support
assert recovery == RECOVERY_REQUIRED, (recovery ^ RECOVERY_REQUIRED)
assert outside == INTENTIONAL_OUTSIDE, (outside ^ INTENTIONAL_OUTSIDE)
assert 'pmp-route-guardian-last-good-clean-v1.js' not in current
assert not (outside & current)
assert not (outside & support)
assert not (outside & recovery)
assert "id:'RECOVERY_REACHABLE'" in SRC
assert "id:'INTENTIONAL_OUTSIDE_ACTIVE_ATLAS'" in SRC
assert "f.bucket!=='INTENTIONAL_OUTSIDE_ACTIVE_ATLAS'" in SRC
assert "RECOVERY_REACHABLE:recovery" in SRC
assert "INTENTIONAL_OUTSIDE_ACTIVE_ATLAS:outside" in SRC
assert "recovery_file_count" in SRC
assert "intentional_outside_file_count" in SRC
assert "ownership_takeover:'not_attempted'" in SRC
assert "route_change:'not_attempted'" in SRC
assert "storage_migration:'not_attempted'" in SRC

print('PASS atlas registry completeness and semantics deterministic test')
