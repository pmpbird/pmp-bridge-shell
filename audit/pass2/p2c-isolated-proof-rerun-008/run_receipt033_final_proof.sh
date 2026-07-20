#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
import hashlib,json,os,pathlib,subprocess
root=pathlib.Path('audit/pass2/p2c-isolated-proof-rerun-008')
auth_path=root/'P2C_FINAL_ONE_RUN_PROOF_AUTHORIZATION_RECEIPT_033.json'
reseal_path=root/'P2C_BROWSER_ENVIRONMENT_STATIC_RESEAL_RECEIPT_032.json'
auth=json.loads(auth_path.read_text()); reseal=json.loads(reseal_path.read_text())
wrapper=pathlib.Path(auth['corrected_wrapper_path']); finalizer=pathlib.Path(auth['unchanged_finalizer_path'])
policy=pathlib.Path(auth['policy_compatibility_controller_path']); patcher=pathlib.Path(auth['repaired_patcher_path']); manifest=pathlib.Path(auth['repaired_manifest_path'])
assert auth['authorized'] is True and auth['status']=='AUTHORIZED_UNCONSUMED' and auth['authorization_consumed'] is False
assert auth['proof_run_count_authorized']==1 and auth['proof_run_count_executed_under_this_receipt']==0 and auth['proof_execution_started'] is False
assert auth['current_main_sha']==os.environ['BASE_SHA']==os.environ['SOURCE_COMMIT']
assert os.environ['EVENT_ACTION']=='opened' and os.environ['RUN_ATTEMPT']=='1'
checkout_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(); assert os.environ['HEAD_SHA']==checkout_head
subprocess.run(['git','merge-base','--is-ancestor',os.environ['PR_HEAD_SHA'],checkout_head],check=True)
subprocess.run(['git','merge-base','--is-ancestor',auth['authorization_state_ancestor'],os.environ['PR_HEAD_SHA']],check=True)
assert subprocess.check_output(['git','hash-object',str(auth_path)],text=True).strip()=='f3d7d45396ae98f017eec23187451c0b91ea7ee7'
assert subprocess.check_output(['git','hash-object',str(reseal_path)],text=True).strip()==auth['reseal_receipt_git_blob_sha']
assert subprocess.check_output(['git','hash-object',str(wrapper)],text=True).strip()==auth['corrected_wrapper_git_blob_sha']
assert subprocess.check_output(['git','hash-object',str(finalizer)],text=True).strip()==auth['unchanged_finalizer_git_blob_sha']
assert hashlib.sha256(policy.read_bytes()).hexdigest()==auth['policy_compatibility_controller_sha256']
assert hashlib.sha256(patcher.read_bytes()).hexdigest()==auth['repaired_patcher_sha256']
assert hashlib.sha256(manifest.read_bytes()).hexdigest()==auth['repaired_manifest_sha256']
assert reseal['status']=='PASS_STATIC_RESEALED' and reseal['browser_setup_closure_passed'] is True and reseal['reached_hard_stop_before_preparation'] is True
for key in ('production_application_authorized','production_activation_authorized','current_map_change_authorized','persisted_data_change_authorized','merge_authorized','second_proof_run_authorized'): assert auth[key] is False,key
changed=set(subprocess.check_output(['git','diff','--name-only',auth['current_main_sha'],os.environ['PR_HEAD_SHA']],text=True).splitlines())
allowed={'.github/workflows/pass2-p2c-isolated-proof-rerun-006.yml','.github/workflows/pass2-p2c-exhaustive-preproof-discovery.yml','audit/a002-live-runtime.cjs'}
extras=sorted(p for p in changed if p not in allowed and not p.startswith('audit/pass2/p2c-isolated-proof-rerun-006/') and not p.startswith('audit/pass2/p2c-isolated-proof-rerun-008/'))
assert not extras,extras
assert not any('/__pycache__/' in p or p.endswith('.pyc') for p in changed)
PY
bash -n "$AUDIT_DIR/rerun008-controller-main-receipt024.sh"
bash -n "$AUDIT_DIR/rerun008-controller-finalize.sh"
bash "$AUDIT_DIR/rerun008-controller-main-receipt024.sh"
