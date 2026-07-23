#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
EXACT_PATHS={
 '.github/workflows/pass2-p2b-hardening-reseal-publisher.yml',
 '.github/workflows/pass2-p2b-hardening-v2.yml',
 '.github/workflows/pass2-p2b-authority-gate.yml',
 '.github/workflows/pass2-p2c-a002-native-messageport-rehearsal-088.yml',
 '.github/workflows/pass2-pr125-ci-routing-repair-v1.yml',
 'tools/test_automated_plan_real_app_v1.mjs',
 'tools/verify_pr125_ci_routing_repair_v1.py',
}
CANDIDATE_PATHS={
 'audit/a003-manifest-seal.json','pmp-active-bug-found-contract-v1.js','pmp-app-current.html',
 'pmp-authority-atlas-adapter-v1.js','pmp-authority-rules-v1.js','pmp-bug-bank-current-active-cleaner-v1.js',
 'pmp-bug-bank-fix-active-stabilizer-v1.js','pmp-bug-bank-legacy-overflow-active-blocker-v1.js',
 'pmp-bug-bank-owner-v1.js','pmp-bug-bank-storage-migration-v1.js','pmp-bug-bank-visual-detectors-v1.js',
 'pmp-bug-watch-passive-capture-v1.js','pmp-current-inner-cleanbug-rgcontrols-v23.html',
 'pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html',
 'pmp-helper-problem-display-sync-v1.js','pmp-helper-problem-memory-v1.js','pmp-pass8-helper-rules-v1.js',
 'pmp-runtime-integrity-manifest-v1.json',
}
WORKFLOW_BRANCHES={
 '.github/workflows/pass2-p2b-hardening-reseal-publisher.yml':'agent/pass2-p2b-hardening-v2',
 '.github/workflows/pass2-p2b-hardening-v2.yml':'agent/pass2-p2b-hardening-v2',
 '.github/workflows/pass2-p2b-authority-gate.yml':'agent/pass2-p2b-authority-gate',
 '.github/workflows/pass2-p2c-a002-native-messageport-rehearsal-088.yml':'agent/pass2-p2c-post-failure-guardian-readiness-001',
}
def git(*args:str)->str:
 return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--base-sha',required=True);ap.add_argument('--head-sha',required=True);ap.add_argument('--output',type=pathlib.Path,required=True);a=ap.parse_args()
 changed=set(filter(None,git('diff','--name-only',a.base_sha,a.head_sha).splitlines()))
 if changed!=EXACT_PATHS: raise SystemExit('ROUTING_REPAIR_EXACT_SCOPE_MISMATCH:'+json.dumps({'missing':sorted(EXACT_PATHS-changed),'extra':sorted(changed-EXACT_PATHS)}))
 if changed&CANDIDATE_PATHS: raise SystemExit('ROUTING_REPAIR_CANDIDATE_BYTE_CHANGE:'+json.dumps(sorted(changed&CANDIDATE_PATHS)))
 checks=[]
 for path,branch in WORKFLOW_BRANCHES.items():
  text=(ROOT/path).read_text()
  ok=branch in text and 'github.event.pull_request.head.repo.full_name == github.repository' in text
  if not ok: raise SystemExit('ROUTING_REPAIR_BRANCH_LOCK_MISSING:'+path)
  checks.append({'path':path,'expected_branch':branch,'same_repository_lock':True})
 visual=(ROOT/'tools/test_automated_plan_real_app_v1.mjs').read_text()
 for token in ('1.3.0-manual-release-startup-order','preRelease.released, false','#pmpPass75ReloadRuntimePlatformGateV1 button[data-run="1"]','manual_diagnostic_run_app_orchestrator'):
  if token not in visual: raise SystemExit('ROUTING_REPAIR_VISUAL_TOKEN_MISSING:'+token)
 syntax=subprocess.run(['node','--check','tools/test_automated_plan_real_app_v1.mjs'],cwd=ROOT,text=True,capture_output=True)
 if syntax.returncode: raise SystemExit('ROUTING_REPAIR_VISUAL_SYNTAX_FAILED:'+syntax.stderr)
 out={'type':'PMP_PASS2_PR125_CI_ROUTING_REPAIR_VERIFICATION_V1','status':'PASS','base_sha':a.base_sha,'head_sha':a.head_sha,'exact_paths':sorted(changed),'candidate_bytes_changed':False,'workflow_branch_locks':checks,'visual_manual_gate_contract':True,'pass3_started':False}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,sort_keys=True))
 return 0
if __name__=='__main__': raise SystemExit(main())
