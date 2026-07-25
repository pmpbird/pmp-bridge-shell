#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
'.github/workflows/pass3-passive-runtime-consumer-unit2-v1.yml',
'audit/pass3/pass3-passive-runtime-consumer-integration-unit2-v1.json',
'pmp-route-guardian-current-loader-v22.html',
'pmp-runtime-integrity-manifest-v1.json',
'tools/test_pass3_passive_runtime_consumer_unit2_v1.py',
'tools/verify_pass3_passive_runtime_consumer_unit2_v1.py'}
def run(*a): return subprocess.check_output(a,cwd=ROOT,text=True).strip()
def main():
    audit=json.loads((ROOT/'audit/pass3/pass3-passive-runtime-consumer-integration-unit2-v1.json').read_text())
    assert audit['status']=='PASSIVE_RUNTIME_CONSUMER_INTEGRATED'
    assert audit['selected_consumer']=='pmp-route-guardian-current-loader-v22.html'
    assert audit['integrity']['current_map_changed'] is False
    assert audit['integrity']['resolver_changed'] is False
    base=sys.argv[1] if len(sys.argv)>1 and sys.argv[1] else 'HEAD^'
    changed=set(filter(None,run('git','diff','--name-only',f'{base}...HEAD').splitlines()))
    assert changed==EXPECTED, f'exact scope mismatch: {sorted(changed)}'
    subprocess.check_call([sys.executable,str(ROOT/'tools/test_pass3_passive_runtime_consumer_unit2_v1.py')],cwd=ROOT)
    print('PASS: exact six-file Pass 3 Unit 2 scope verified')
if __name__=='__main__': main()
