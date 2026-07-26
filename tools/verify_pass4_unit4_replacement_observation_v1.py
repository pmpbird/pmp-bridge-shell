#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
'.github/workflows/pass4-unit4-replacement-observation-v1.yml',
'audit/pass4/pass4-boot-status-strip-unit4-replacement-observation-v1.json',
'tools/run_pass4_unit4_replacement_observation_v1.js',
'tools/test_pass4_unit4_nested_frame_observer_v1.js',
'tools/verify_pass4_unit4_replacement_observation_v1.py'}
def run(*a): return subprocess.check_output(a,cwd=ROOT,text=True).strip()
base=sys.argv[1] if len(sys.argv)>1 else 'HEAD^'
changed=set(filter(None,run('git','diff','--name-only',f'{base}...HEAD').splitlines()))
assert changed==EXPECTED,(sorted(changed),sorted(EXPECTED))
r=json.loads((ROOT/'audit/pass4/pass4-boot-status-strip-unit4-replacement-observation-v1.json').read_text())
assert r['status']=='PASS'
assert r['observation_consumed'] is True and r['observation_count']==1 and r['browser_navigation_count']==1
assert r['booting_observed'] is True and r['ready_acknowledged_observed'] is True
roles={x['role'] for x in r['frame_chain']}
assert {'top','route_guardian_v22','reload_owner_v30','current_inner_v30'}<=roles
side=r['zero_effect_evidence']['strip_declared_side_effects']
assert side=={'routeAssignments':0,'persistedUserDataWrites':0,'appOrchestratorOwnershipTransfers':0,'startupRepairs':0}
assert not r['production_runtime_changed'] and not r['runtime_integrity_changed']
subprocess.check_call(['node','tools/test_pass4_unit4_nested_frame_observer_v1.js'],cwd=ROOT)
print('PASS: exact Unit 4 replacement evidence scope and receipt verified')
