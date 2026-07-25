#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
 '.github/workflows/pass3-route-guardian-handoff-unit3-isolated-proof-v1.yml',
 'audit/pass3/pass3-route-guardian-handoff-unit3-isolated-proof-v1.json',
 'tools/run_pass3_route_guardian_handoff_unit3_isolated_proof_v1.mjs',
 'tools/verify_pass3_route_guardian_handoff_unit3_isolated_proof_v1.py',
}
def run(*args): return subprocess.check_output(args,cwd=ROOT,text=True).strip()
def main():
 subprocess.check_call(['node','tools/run_pass3_route_guardian_handoff_unit3_isolated_proof_v1.mjs'],cwd=ROOT)
 receipt=json.loads((ROOT/'audit/pass3/pass3-route-guardian-handoff-unit3-isolated-proof-v1.json').read_text())
 assert receipt['status']=='PASS' and receipt['scope']=='isolated_node_vm_only'
 assert receipt['canonical_accepts']==1 and receipt['fail_closed_rejections']>=19
 assert receipt['zero_navigation_assignments'] is True and receipt['zero_persisted_user_data_writes'] is True
 assert all(c['storage_delta']==0 and c['navigation_delta']==0 for c in receipt['cases'])
 assert receipt['cases'][0]['name']=='canonical_current_map_handoff' and receipt['cases'][0]['accepted'] is True
 assert all(c['accepted'] is False for c in receipt['cases'][1:])
 base=sys.argv[1] if len(sys.argv)>1 and sys.argv[1] else 'HEAD^'
 changed=set(filter(None,run('git','diff','--name-only',f'{base}...HEAD').splitlines()))
 assert changed==EXPECTED,f'exact scope mismatch: {sorted(changed)}'
 print('PASS: exact four-file additive Unit 3 isolated proof verified')
if __name__=='__main__': main()
