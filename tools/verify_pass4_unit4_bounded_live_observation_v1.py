#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={'.github/workflows/pass4-unit4-bounded-live-observation-v1.yml','audit/pass4/pass4-boot-status-strip-unit4-bounded-live-observation-v1.json','tools/run_pass4_unit4_bounded_live_observation_v1.js','tools/verify_pass4_unit4_bounded_live_observation_v1.py'}
PRESERVED={'pmp-boot-status-strip-owner-v1.js','pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html','pmp-app-orchestrator-v1.js','pmp-current-map-v12.json','pmp-current-route-resolver-v1.js','pmp-route-guardian-current-loader-v22.html','pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html','pmp-runtime-integrity-manifest-v1.json','audit/a003-manifest-seal.json','pmp-app-current.html'}
def run(*a):return subprocess.check_output(a,cwd=ROOT,text=True).strip()
def main():
 base=sys.argv[1] if len(sys.argv)>1 and sys.argv[1] else 'HEAD^'
 changed=set(filter(None,run('git','diff','--name-only',f'{base}...HEAD').splitlines()))
 assert changed==EXPECTED,(sorted(changed),sorted(EXPECTED)); assert not changed&PRESERVED
 r=json.loads((ROOT/'audit/pass4/pass4-boot-status-strip-unit4-bounded-live-observation-v1.json').read_text())
 assert r['observation_consumed'] is True and r['observation_count']==1 and r['browser_navigation_count']==1
 assert r['status']=='PASS',r.get('failure_reason')
 assert r['booting_observed'] is True and r['ready_acknowledged_observed'] is True
 assert r['current_path_observed'] is True and r['selected_consumer_observed'] is True
 z=r['zero_effect_evidence']; assert z['strip_declared_side_effects'] and all(v==0 for v in z['strip_declared_side_effects'].values())
 for k,v in z.items():
  if k!='strip_declared_side_effects': assert v==0,(k,v)
 assert r['production_runtime_changed'] is False and r['runtime_integrity_changed'] is False
 assert r['unit5_started'] is False and r['pass5_started'] is False and r['pr122_touched'] is False
 print('PASS: exact four-file evidence-only Unit 4 scope and single live observation receipt verified')
if __name__=='__main__':main()
