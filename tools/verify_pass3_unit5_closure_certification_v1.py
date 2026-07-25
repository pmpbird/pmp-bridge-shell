#!/usr/bin/env python3
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
'.github/workflows/pass3-unit5-closure-certification-v1.yml',
'audit/pass3/pass3-route-guardian-handoff-unit5-closure-certification-v1.json',
'tools/test_pass3_unit5_closure_certification_v1.py',
'tools/verify_pass3_unit5_closure_certification_v1.py',
}
def run(*a): return subprocess.check_output(a,cwd=ROOT,text=True).strip()
def main():
    base=sys.argv[1] if len(sys.argv)>1 else 'HEAD^'
    changed=set(filter(None,run('git','diff','--name-only',f'{base}...HEAD').splitlines()))
    assert changed==EXPECTED,(changed,EXPECTED)
    forbidden={'pmp-current-map-v12.json','pmp-current-route-resolver-v1.js','pmp-route-guardian-current-loader-v22.html','pmp-runtime-integrity-manifest-v1.json','pmp-app-current.html'}
    assert not (changed & forbidden)
    print('PASS: exact four-file evidence-only Unit 5 closure scope verified')
if __name__=='__main__': main()
