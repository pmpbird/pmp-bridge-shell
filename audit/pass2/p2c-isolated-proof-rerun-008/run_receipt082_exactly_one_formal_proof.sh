#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
import hashlib,json,os,pathlib,subprocess
root=pathlib.Path('audit/pass2/p2c-isolated-proof-rerun-008')
auth_path=root/'P2C_NODEPATH_ROLLBACK_SOURCE_REPAIR_AUTHORIZATION_RECEIPT_082.json'
directive_path=root/'P2C_RECEIPT082_EXACTLY_ONE_FORMAL_PROOF_EXECUTION_DIRECTIVE_083.json'
seal_path=root/'P2C_RECEIPT082_FORMAL_PROOF_PR_HEAD_SEAL_084.json'
auth=json.loads(auth_path.read_text()); directive=json.loads(directive_path.read_text()); seal=json.loads(seal_path.read_text())
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
blob=lambda p:subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
tree_blob=lambda commit,p:subprocess.check_output(['git','rev-parse',f'{commit}:{pathlib.Path(p).as_posix()}'],text=True).strip()
assert auth['authorized'] and auth['status']=='AUTHORIZED_UNCONSUMED_STATIC_ONLY'
assert not auth['authorization_consumed'] and not auth['proof_execution_started']
assert auth['proof_run_count_authorized']==1 and auth['proof_run_count_executed_under_this_receipt']==0
assert directive['authorized'] and directive['status']=='AUTHORIZED_UNCONSUMED_EXACTLY_ONE_RUN'
assert directive['formal_proof_pr_open_authorized'] and directive['formal_proof_execution_authorized']
assert directive['authorization_receipt_sha256']==sha(auth_path)
assert directive['authorization_receipt_git_blob_sha']==blob(auth_path)
assert directive['execution_wrapper_git_blob_sha']==blob(pathlib.Path(directive['execution_wrapper_path']))
assert auth['formal_workflow_git_blob_sha']==blob(pathlib.Path(auth['formal_workflow_path']))==directive['execution_workflow_git_blob_sha']
assert auth['formal_wrapper_git_blob_sha']==blob(pathlib.Path(auth['formal_wrapper_path']))==directive['formal_controller_wrapper_git_blob_sha']
assert auth['runtime_binding_patcher_git_blob_sha']==blob(pathlib.Path(auth['runtime_binding_patcher_path']))==directive['runtime_binding_patcher_git_blob_sha']
assert auth['formal_finalizer_git_blob_sha']==blob(pathlib.Path(auth['formal_finalizer_path']))==directive['formal_finalizer_git_blob_sha']
assert seal['status']=='SEALED_EXACT_FINAL_PR_HEAD'
assert seal['directive_sha256']==sha(directive_path) and seal['directive_git_blob_sha']==blob(directive_path)
assert os.environ['EVENT_ACTION']=='opened' and os.environ['RUN_ATTEMPT']=='1'
assert os.environ['SOURCE_COMMIT']==auth['source_repository_commit']==directive['source_repository_commit']
base=os.environ['BASE_SHA']; pr_head=os.environ['PR_HEAD_SHA']; checkout=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert auth['current_main_sha']==directive['current_main_sha']
subprocess.run(['git','merge-base','--is-ancestor',auth['current_main_sha'],base],check=True)
for path in (
    auth_path,
    directive_path,
    pathlib.Path(directive['execution_wrapper_path']),
    pathlib.Path(auth['formal_workflow_path']),
    pathlib.Path(auth['formal_wrapper_path']),
    pathlib.Path(auth['runtime_binding_patcher_path']),
    pathlib.Path(auth['formal_finalizer_path']),
):
    assert tree_blob(base,path)==blob(path),path
assert checkout==os.environ['HEAD_SHA']
subprocess.run(['git','merge-base','--is-ancestor',pr_head,checkout],check=True)
assert subprocess.check_output(['git','rev-parse',f'{pr_head}^'],text=True).strip()==seal['sealed_parent_commit']
assert subprocess.check_output(['git','diff','--name-only',f'{pr_head}^',pr_head],text=True).splitlines()==[str(seal_path)]
for key in ('production_application_authorized','production_activation_authorized','current_map_change_authorized','persisted_data_change_authorized','merge_authorized','second_proof_run_authorized'):
    assert auth[key] is False and directive[key] is False,key
PY
bash -n "$AUDIT_DIR/rerun008-controller-main-receipt082.sh"
bash -n "$AUDIT_DIR/rerun008-controller-finalize.sh"
bash "$AUDIT_DIR/rerun008-controller-main-receipt082.sh"
