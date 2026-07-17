#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
import hashlib,json,os,pathlib,subprocess
root=pathlib.Path('audit/pass2/p2c-isolated-proof-rerun-008')
auth_path=root/'P2C_REFRESHED_EXACTLY_ONE_FORMAL_PROOF_AUTHORIZATION_RECEIPT_043.json'
directive_path=root/'P2C_RECEIPT043_EXACTLY_ONE_FORMAL_PROOF_EXECUTION_DIRECTIVE_044.json'
head_seal_path=root/'P2C_RECEIPT043_FORMAL_PROOF_PR_HEAD_SEAL_045.json'
manifest_path=root/'P2C_REHEARSAL_EQUIVALENCE_MANIFEST_036.json'
equivalence_seal_path=root/'P2C_REHEARSAL_EQUIVALENCE_SEAL_RECEIPT_037.json'
auth=json.loads(auth_path.read_text()); directive=json.loads(directive_path.read_text()); head_seal=json.loads(head_seal_path.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
blob=lambda p:subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
assert auth['authorized'] is True and auth['status']=='AUTHORIZED_UNCONSUMED_STATIC_ONLY'
assert auth['authorization_consumed'] is False and auth['proof_execution_started'] is False
assert auth['proof_run_count_authorized']==1 and auth['proof_run_count_executed_under_this_receipt']==0
assert directive['authorized'] is True and directive['status']=='AUTHORIZED_UNCONSUMED_EXACTLY_ONE_RUN'
assert directive['authorization_consumed'] is False and directive['proof_execution_started'] is False
assert directive['proof_run_count_authorized']==1 and directive['proof_run_count_executed']==0
assert directive['formal_proof_pr_open_authorized'] is True and directive['formal_proof_execution_authorized'] is True
assert directive['authorization_receipt_git_blob_sha']==blob(auth_path)
assert directive['authorization_receipt_sha256']==sha(auth_path)
assert auth['equivalence_manifest_sha256']==directive['equivalence_manifest_sha256']==sha(manifest_path)
assert auth['equivalence_seal_git_blob_sha']==directive['equivalence_seal_git_blob_sha']==blob(equivalence_seal_path)
assert directive['execution_wrapper_git_blob_sha']==blob(pathlib.Path(directive['execution_wrapper_path']))
assert directive['execution_workflow_git_blob_sha']==blob(pathlib.Path(directive['execution_workflow_path']))
assert directive['formal_controller_wrapper_git_blob_sha']==blob(pathlib.Path(auth['formal_wrapper_path']))
assert directive['formal_finalizer_git_blob_sha']==blob(pathlib.Path(auth['formal_finalizer_path']))
assert head_seal['status']=='SEALED_EXACT_FINAL_PR_HEAD'
assert head_seal['directive_git_blob_sha']==blob(directive_path)
assert head_seal['directive_sha256']==sha(directive_path)
assert os.environ['EVENT_ACTION']=='opened' and os.environ['RUN_ATTEMPT']=='1'
assert os.environ['BASE_SHA']==directive['current_main_sha']==auth['current_main_sha']==auth['source_repository_commit']
checkout_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
pr_head=os.environ['PR_HEAD_SHA']
assert os.environ['HEAD_SHA']==checkout_head
subprocess.run(['git','merge-base','--is-ancestor',pr_head,checkout_head],check=True)
assert subprocess.check_output(['git','rev-parse',f'{pr_head}^'],text=True).strip()==head_seal['sealed_parent_commit']
assert subprocess.check_output(['git','diff','--name-only',f'{pr_head}^',pr_head],text=True).splitlines()==[str(head_seal_path)]
subprocess.run(['git','merge-base','--is-ancestor',directive['authorization_state_ancestor'],pr_head],check=True)
subprocess.run(['git','merge-base','--is-ancestor',directive['execution_package_ancestor'],pr_head],check=True)
for key in ('production_application_authorized','production_activation_authorized','current_map_change_authorized','persisted_data_change_authorized','merge_authorized','second_proof_run_authorized'):
    assert directive[key] is False,key
changed=set(subprocess.check_output(['git','diff','--name-only',directive['current_main_sha'],pr_head],text=True).splitlines())
allowed={'.github/workflows/pass2-p2c-isolated-proof-rerun-006.yml','.github/workflows/pass2-p2c-exhaustive-preproof-discovery.yml','.github/workflows/pass2-p2c-full-rehearsal-equivalence-closure.yml','.github/workflows/pass2-p2c-receipt038-static-preflight.yml','audit/a002-live-runtime.cjs'}
extras=sorted(p for p in changed if p not in allowed and not p.startswith('audit/pass2/p2c-isolated-proof-rerun-006/') and not p.startswith('audit/pass2/p2c-isolated-proof-rerun-008/'))
assert not extras,extras
assert not any('/__pycache__/' in p or p.endswith('.pyc') for p in changed)
pathlib.Path(os.environ['EVIDENCE_DIR']).mkdir(parents=True,exist_ok=True)
(pathlib.Path(os.environ['EVIDENCE_DIR'])/'receipt043-execution-binding-check.json').write_text(json.dumps({
  'status':'PASS','authorization_receipt_sha256':sha(auth_path),'directive_sha256':sha(directive_path),
  'base_sha':os.environ['BASE_SHA'],'pr_head_sha':pr_head,'checkout_head':checkout_head,
  'sealed_parent_commit':head_seal['sealed_parent_commit'],'proof_run_count_authorized':1,
  'proof_run_count_previously_executed':0,'second_proof_run_authorized':False,
  'production_activation_authorized':False,'merge_authorized':False
},indent=2,sort_keys=True)+'\n')
PY
bash -n "$AUDIT_DIR/rerun008-controller-main-receipt024.sh"
bash -n "$AUDIT_DIR/rerun008-controller-finalize.sh"
bash "$AUDIT_DIR/rerun008-controller-main-receipt024.sh"
