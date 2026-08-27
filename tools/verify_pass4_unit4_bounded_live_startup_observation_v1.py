#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
 '.github/workflows/pass4-unit4-bounded-live-startup-observation-v1.yml',
 'audit/pass4/pass4-boot-status-strip-unit4-bounded-live-observation-v1.json',
 'tools/run_pass4_unit4_bounded_live_startup_observation_v1.js',
 'tools/verify_pass4_unit4_bounded_live_startup_observation_v1.py',
}
PRESERVED={
 'pmp-boot-status-strip-owner-v1.js',
 'pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html',
 'pmp-app-orchestrator-v1.js','pmp-current-map-v12.json','pmp-current-route-resolver-v1.js',
 'pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html',
 'pmp-runtime-integrity-manifest-v1.json','audit/a003-manifest-seal.json','pmp-app-current.html',
}
def run(*a): return subprocess.check_output(a,cwd=ROOT,text=True).strip()
def main():
 base=sys.argv[1] if len(sys.argv)>1 and sys.argv[1] else 'HEAD^'
 changed=set(filter(None,run('git','diff','--name-only',f'{base}...HEAD').splitlines()))
 assert changed==EXPECTED,(sorted(changed),sorted(EXPECTED))
 assert not (changed & PRESERVED),sorted(changed & PRESERVED)
 receipt=json.loads((ROOT/'audit/pass4/pass4-boot-status-strip-unit4-bounded-live-observation-v1.json').read_text())
 assert receipt['status']=='OBSERVATION_CONSUMED'
 assert receipt['observation_count']==1
 assert receipt['success'] is True
 assert receipt['naturally_observed']['BOOTING'] is True
 assert receipt['naturally_observed']['READY_ACKNOWLEDGED'] is True
 assert receipt['no_forced_failure_or_delay'] is True
 assert receipt['production_runtime_changed'] is False
 assert receipt['integrity_identities_changed'] is False
 assert receipt['current_path']['current_path_only'] is True
 assert receipt['current_path']['current_map_sole_destination_authority'] is True
 assert all(v==0 for v in receipt['observed_strip_side_effects'].values())
 assert receipt['unit5_started'] is False and receipt['pass5_started'] is False
 print('PASS: exact four-file evidence-only Unit 4 scope and consumed single observation verified')
if __name__=='__main__': main()
