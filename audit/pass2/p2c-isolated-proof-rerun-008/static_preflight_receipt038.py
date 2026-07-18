#!/usr/bin/env python3
import hashlib,json,os,pathlib,subprocess
root=pathlib.Path('audit/pass2/p2c-isolated-proof-rerun-008')
auth_path=root/'P2C_FRESH_EXACTLY_ONE_FORMAL_PROOF_AUTHORIZATION_RECEIPT_047.json'
directive_path=root/'P2C_RECEIPT047_EXACTLY_ONE_FORMAL_PROOF_EXECUTION_DIRECTIVE_048.json'
auth=json.loads(auth_path.read_text()); directive=json.loads(directive_path.read_text())
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
blob=lambda p:subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(); base=os.environ['BASE_SHA']
assert auth['authorized'] is True and auth['status']=='AUTHORIZED_UNCONSUMED_STATIC_ONLY'
assert auth['authorization_consumed'] is False and auth['proof_execution_started'] is False
assert auth['proof_run_count_authorized']==1 and auth['proof_run_count_executed_under_this_receipt']==0
assert auth['static_preflight_only'] is True
assert auth['formal_proof_pr_open_authorized'] is False and auth['formal_proof_execution_authorized'] is False
assert directive['authorized'] is True and directive['status']=='AUTHORIZED_UNCONSUMED_EXACTLY_ONE_RUN'
assert directive['authorization_consumed'] is False and directive['proof_execution_started'] is False
assert directive['proof_run_count_authorized']==1 and directive['proof_run_count_executed']==0
assert directive['formal_proof_pr_open_authorized'] is True and directive['formal_proof_execution_authorized'] is True
assert directive['rerun_authorized'] is False
assert auth['current_main_sha']==directive['current_main_sha']==base
assert auth['source_repository_commit']==directive['source_repository_commit']==base
assert directive['authorization_receipt_git_blob_sha']==blob(auth_path)
assert directive['authorization_receipt_sha256']==sha(auth_path)
assert blob(auth['formal_workflow_path'])==auth['formal_workflow_git_blob_sha']==directive['execution_workflow_git_blob_sha']
assert blob(directive['execution_wrapper_path'])==directive['execution_wrapper_git_blob_sha']
assert blob(auth['formal_wrapper_path'])==auth['formal_wrapper_git_blob_sha']==directive['formal_controller_wrapper_git_blob_sha']
assert blob(auth['formal_finalizer_path'])==auth['formal_finalizer_git_blob_sha']==directive['formal_finalizer_git_blob_sha']
assert sha(auth['equivalence_manifest_path'])==auth['equivalence_manifest_sha256']==directive['equivalence_manifest_sha256']
assert blob(auth['equivalence_seal_path'])==auth['equivalence_seal_git_blob_sha']==directive['equivalence_seal_git_blob_sha']
subprocess.run(['git','merge-base','--is-ancestor',auth['authorization_state_ancestor'],head],check=True)
subprocess.run(['git','merge-base','--is-ancestor',directive['execution_package_ancestor'],head],check=True)
for key in ('production_application_authorized','production_activation_authorized','current_map_change_authorized','persisted_data_change_authorized','merge_authorized','second_proof_run_authorized'):
    assert auth[key] is False,key
    assert directive[key] is False,key
changed=subprocess.check_output(['git','diff','--name-only',base,'HEAD'],text=True).splitlines()
assert changed and not any(p.endswith('.pyc') or '/__pycache__/' in p for p in changed)
out={'type':'PMP_P2C_RECEIPT047_FORMAL_PROOF_AUTHORIZATION_STATIC_PREFLIGHT_RESULT_051','status':'PASS_STATIC_PREFLIGHT_ONLY','head_sha':head,'base_sha':base,'authorization_receipt':'047','execution_directive':'048','authorization_sha256':sha(auth_path),'authorization_git_blob_sha':blob(auth_path),'execution_wrapper_git_blob_sha':blob(directive['execution_wrapper_path']),'formal_workflow_git_blob_sha':blob(auth['formal_workflow_path']),'formal_controller_wrapper_git_blob_sha':blob(auth['formal_wrapper_path']),'formal_finalizer_git_blob_sha':blob(auth['formal_finalizer_path']),'proof_run_count_executed':0,'formal_proof_executed':False,'merge_authorized':False,'production_activation_authorized':False,'current_map_change_authorized':False,'persisted_data_change_authorized':False,'second_proof_run_authorized':False}
pathlib.Path(os.environ['EVIDENCE_DIR']).mkdir(parents=True,exist_ok=True)
(pathlib.Path(os.environ['EVIDENCE_DIR'])/'static-preflight-result-051.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
