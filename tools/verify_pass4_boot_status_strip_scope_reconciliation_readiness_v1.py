#!/usr/bin/env python3
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
'.github/workflows/pass4-boot-status-strip-scope-reconciliation-readiness-v1.yml',
'audit/pass4/pass4-boot-status-strip-scope-reconciliation-readiness-v1.json',
'tools/test_pass4_boot_status_strip_scope_reconciliation_readiness_v1.py',
'tools/verify_pass4_boot_status_strip_scope_reconciliation_readiness_v1.py',
}
def run(*a): return subprocess.check_output(a,cwd=ROOT,text=True).strip()
def main():
    base=sys.argv[1] if len(sys.argv)>1 else 'HEAD^'
    changed=set(filter(None,run('git','diff','--name-only',f'{base}...HEAD').splitlines()))
    assert changed==EXPECTED,(changed,EXPECTED)
    forbidden={'pmp-current-map-v12.json','pmp-current-route-resolver-v1.js','pmp-route-guardian-current-loader-v22.html','pmp-app-orchestrator-v1.js','pmp-runtime-integrity-manifest-v1.json','pmp-app-current.html'}
    assert not changed & forbidden
    print('PASS: exact four-file documentation-only Pass 4 readiness scope verified')
if __name__=='__main__': main()
