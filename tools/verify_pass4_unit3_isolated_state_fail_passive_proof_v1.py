#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
 '.github/workflows/pass4-unit3-isolated-state-fail-passive-proof-v1.yml',
 'audit/pass4/pass4-boot-status-strip-unit3-isolated-state-fail-passive-proof-v1.json',
 'tools/test_pass4_unit3_isolated_state_fail_passive_proof_v1.js',
 'tools/verify_pass4_unit3_isolated_state_fail_passive_proof_v1.py',
}
PRESERVED=[
 'pmp-boot-status-strip-owner-v1.js',
 'pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html',
 'pmp-app-orchestrator-v1.js','pmp-current-map-v12.json','pmp-current-route-resolver-v1.js',
 'pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html',
 'pmp-runtime-integrity-manifest-v1.json','audit/a003-manifest-seal.json','pmp-app-current.html',
]
def run(*a):return subprocess.check_output(a,cwd=ROOT,text=True).strip()
def main():
 base=sys.argv[1] if len(sys.argv)>1 and sys.argv[1] else 'HEAD^'
 changed=set(filter(None,run('git','diff','--name-only',f'{base}...HEAD').splitlines()))
 assert changed==EXPECTED,(sorted(changed),sorted(EXPECTED))
 audit=json.loads((ROOT/'audit/pass4/pass4-boot-status-strip-unit3-isolated-state-fail-passive-proof-v1.json').read_text())
 assert audit['status']=='PROVEN_PENDING_MERGE'
 assert audit['production_runtime_changed'] is False
 assert audit['authority_preservation']['current_map_sole_destination_authority'] is True
 assert audit['unit4_started'] is False and audit['pass5_started'] is False
 for rel in PRESERVED:
  assert rel not in changed,rel
 subprocess.check_call(['node',str(ROOT/'tools/test_pass4_unit3_isolated_state_fail_passive_proof_v1.js')],cwd=ROOT)
 print('PASS: exact four-file evidence-only Unit 3 scope verified')
if __name__=='__main__':main()
