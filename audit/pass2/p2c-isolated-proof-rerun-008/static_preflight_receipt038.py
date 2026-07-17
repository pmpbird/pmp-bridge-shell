#!/usr/bin/env python3
import hashlib,json,os,pathlib,subprocess
root=pathlib.Path('audit/pass2/p2c-isolated-proof-rerun-008')
auth_path=root/'P2C_FRESH_EXACTLY_ONE_FORMAL_PROOF_AUTHORIZATION_RECEIPT_038.json'
seal_path=root/'P2C_FRESH_FORMAL_PROOF_AUTHORIZATION_SEAL_RECEIPT_039.json'
auth=json.loads(auth_path.read_text()); seal=json.loads(seal_path.read_text())
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
blob=lambda p:subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
base=os.environ['BASE_SHA']
assert auth['authorized'] is True
assert auth['status']=='AUTHORIZED_UNCONSUMED_STATIC_ONLY'
assert auth['authorization_consumed'] is False
assert auth['proof_execution_started'] is False
assert auth['proof_run_count_authorized']==1
assert auth['proof_run_count_executed_under_this_receipt']==0
assert auth['static_preflight_only'] is True
assert auth['formal_proof_pr_open_authorized'] is False
assert auth['formal_proof_execution_authorized'] is False
assert auth['current_main_sha']==base=='98b2e293717b81289e3b372d1fff8f5832d29fd6'
assert auth['source_repository_commit']==base
subprocess.run(['git','merge-base','--is-ancestor',auth['authorization_state_ancestor'],head],check=True)
assert sha(auth_path)==seal['authorization_sha256']=='cd37eba96fffe9e99e68037301520a0ceafeb7ff2dd41efb35852dc5b48fec08'
assert auth_path.stat().st_size==seal['authorization_bytes']==2504
assert sha(auth['equivalence_manifest_path'])==auth['equivalence_manifest_sha256']==seal['equivalence_manifest_sha256']=='fc5089a4b6ee92f5092fc806f6838e979087529f9699e400273d8f0e3a34968f'
for path_key,blob_key in (
 ('equivalence_seal_path','equivalence_seal_git_blob_sha'),
 ('formal_workflow_path','formal_workflow_git_blob_sha'),
 ('formal_wrapper_path','formal_wrapper_git_blob_sha'),
 ('formal_finalizer_path','formal_finalizer_git_blob_sha'),
 ('legacy_execution_entry_path','legacy_execution_entry_git_blob_sha')):
    assert blob(auth[path_key])==auth[blob_key],(path_key,blob(auth[path_key]),auth[blob_key])
for key in ('production_application_authorized','production_activation_authorized','current_map_change_authorized','persisted_data_change_authorized','merge_authorized','second_proof_run_authorized'):
    assert auth[key] is False,key
for key in ('formal_proof_pr_open_authorized','formal_proof_execution_authorized','merge_authorized','production_activation_authorized','current_map_change_authorized','persisted_data_change_authorized','second_proof_run_authorized'):
    assert seal[key] is False,key
assert seal['proof_run_count_executed']==0
assert seal['status']=='SEALED_STATIC_PREFLIGHT_PENDING'
assert subprocess.check_output(['git','diff','--name-only',base,'HEAD'],text=True)
assert not any(p.endswith('.pyc') or '/__pycache__/' in p for p in subprocess.check_output(['git','diff','--name-only',base,'HEAD'],text=True).splitlines())
out={
 'type':'PMP_P2C_FRESH_FORMAL_PROOF_AUTHORIZATION_STATIC_PREFLIGHT_RESULT_040',
 'status':'PASS_STATIC_PREFLIGHT_ONLY',
 'head_sha':head,
 'base_sha':base,
 'authorization_sha256':sha(auth_path),
 'authorization_seal_sha256':sha(seal_path),
 'equivalence_manifest_sha256':sha(auth['equivalence_manifest_path']),
 'proof_run_count_executed':0,
 'formal_proof_pr_opened':False,
 'formal_proof_executed':False,
 'merge_authorized':False,
 'production_activation_authorized':False,
 'current_map_change_authorized':False,
 'persisted_data_change_authorized':False,
 'second_proof_run_authorized':False
}
pathlib.Path(os.environ['EVIDENCE_DIR']).mkdir(parents=True,exist_ok=True)
(pathlib.Path(os.environ['EVIDENCE_DIR'])/'static-preflight-result-040.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
