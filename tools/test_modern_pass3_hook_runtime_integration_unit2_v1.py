#!/usr/bin/env python3
import json, pathlib, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
RUN=ROOT/'tools/run_modern_pass3_hook_runtime_integration_unit2_v1.mjs'
cases=['positive','missing_body','duplicate_body','missing_manifest','missing_support_slot','missing_body_raw_pointer','missing_support_raw_pointer','missing_marker','readiness_prerequisite_failure','overclaim_attempt']
results={}
for case in cases:
    a=subprocess.check_output(['node',str(RUN),case],cwd=ROOT,text=True)
    b=subprocess.check_output(['node',str(RUN),case],cwd=ROOT,text=True)
    if a!=b: raise AssertionError(f'non_deterministic:{case}')
    r=json.loads(a); results[case]=r['execution']['validation_state']
    if r['claim_ceiling']!={'real_app_proof':False,'current_clean':False,'frozen':False,'full_transfer_proof':False,'full_history_lossless':False,'best_in_world':False,'production_activation':False}: raise AssertionError('claim_ceiling')
    if case=='positive':
        if r['readiness']['readiness_state']!='phase3_hook_validation_ready_with_watch' or r['execution']['validation_state']!='phase3_hooks_001_006_validated_with_watch': raise AssertionError('positive_failed')
    elif case=='overclaim_attempt':
        if r['execution']['validation_state']!='phase3_hooks_001_006_validated_with_watch': raise AssertionError('overclaim_changed_runtime_result')
    else:
        if r['execution']['validation_state']!='phase3_hook_validation_blocked_or_with_gaps': raise AssertionError(f'fail_closed_missing:{case}')
print(json.dumps({'status':'PASS','cases':results,'deterministic':True},sort_keys=True))
