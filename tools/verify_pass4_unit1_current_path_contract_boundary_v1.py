#!/usr/bin/env python3
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
'.github/workflows/pass4-unit1-current-path-contract-boundary-v1.yml',
'audit/pass4/pass4-boot-status-strip-unit1-current-path-contract-boundary-v1.json',
'tools/test_pass4_unit1_current_path_contract_boundary_v1.py',
'tools/verify_pass4_unit1_current_path_contract_boundary_v1.py',
}
def run(*args): return subprocess.check_output(args,cwd=ROOT,text=True).strip()
def main():
    base=sys.argv[1] if len(sys.argv)>1 else 'HEAD^'
    changed=set(filter(None,run('git','diff','--name-only',f'{base}...HEAD').splitlines()))
    assert changed==EXPECTED,(changed,EXPECTED)
    forbidden={
      'pmp-current-map-v12.json','pmp-current-route-resolver-v1.js',
      'pmp-route-guardian-current-loader-v22.html',
      'pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html',
      'pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html',
      'pmp-app-orchestrator-v1.js','pmp-boot-status-strip-owner-v1.js',
      'pmp-runtime-integrity-manifest-v1.json','pmp-app-current.html'
    }
    assert not (changed & forbidden)
    print('PASS: exact four-file evidence-only Pass 4 Unit 1 scope verified')
if __name__=='__main__': main()
