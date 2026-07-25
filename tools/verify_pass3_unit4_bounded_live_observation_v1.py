#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
'.github/workflows/pass3-unit4-bounded-live-observation-v1.yml',
'audit/pass3/pass3-route-guardian-handoff-unit4-live-observation-v1.json',
'audit/pass3/pass3-unit4-bounded-live-observation.cjs',
'tools/verify_pass3_unit4_bounded_live_observation_v1.py',
}
def run(*args): return subprocess.check_output(args,cwd=ROOT,text=True).strip()
def main():
    record=json.loads((ROOT/'audit/pass3/pass3-route-guardian-handoff-unit4-live-observation-v1.json').read_text())
    assert record['pass']==3 and record['unit']==4
    assert record['observation']['canonical_runs']==1
    assert record['observation']['controlled_invalid_probes']==1
    assert record['preservation']['runtime_files_changed'] is False
    assert record['preservation']['unit5_started'] is False
    base=sys.argv[1] if len(sys.argv)>1 else 'HEAD^'
    changed=set(filter(None,run('git','diff','--name-only',f'{base}...HEAD').splitlines()))
    assert changed==EXPECTED,(changed,EXPECTED)
    print('PASS: exact four-file evidence-only Unit 4 scope verified')
if __name__=='__main__': main()
