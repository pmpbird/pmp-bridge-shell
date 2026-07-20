#!/usr/bin/env python3
import hashlib
import json
import os
import pathlib
import subprocess

root = pathlib.Path('audit/pass2/p2c-isolated-proof-rerun-008')
auth_path = root / 'P2C_NODEPATH_ROLLBACK_SOURCE_REPAIR_AUTHORIZATION_RECEIPT_082.json'
directive_path = root / 'P2C_RECEIPT082_EXACTLY_ONE_FORMAL_PROOF_EXECUTION_DIRECTIVE_083.json'
reseal_path = root / 'P2C_RECEIPT082_MERGED_MAIN_STATIC_RESEAL_RECEIPT_115.json'
auth = json.loads(auth_path.read_text())
directive = json.loads(directive_path.read_text())
reseal = json.loads(reseal_path.read_text())


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def blob(path):
    return subprocess.check_output(['git', 'hash-object', str(path)], text=True).strip()


head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
base = os.environ['BASE_SHA']

assert auth['authorized'] is True and auth['status'] == 'AUTHORIZED_UNCONSUMED_STATIC_ONLY'
assert auth['authorization_consumed'] is False and auth['proof_execution_started'] is False
assert auth['proof_run_count_authorized'] == 1
assert auth['proof_run_count_executed_under_this_receipt'] == 0
assert auth['static_preflight_only'] is True
assert auth['formal_proof_pr_open_authorized'] is False
assert auth['formal_proof_execution_authorized'] is False

assert directive['authorized'] is True
assert directive['status'] == 'AUTHORIZED_UNCONSUMED_EXACTLY_ONE_RUN'
assert directive['authorization_consumed'] is False and directive['proof_execution_started'] is False
assert directive['proof_run_count_authorized'] == 1 and directive['proof_run_count_executed'] == 0
assert directive['formal_proof_pr_open_authorized'] is True
assert directive['formal_proof_execution_authorized'] is True
assert directive['rerun_authorized'] is False

assert auth['current_main_sha'] == directive['current_main_sha'] == reseal['current_main_sha'] == base
assert auth['resealed_against_merged_main_sha'] == base
assert auth['source_repository_commit'] == directive['source_repository_commit'] == reseal['source_repository_commit']

assert directive['authorization_receipt_git_blob_sha'] == blob(auth_path)
assert directive['authorization_receipt_sha256'] == sha(auth_path)
assert reseal['authorization_receipt_git_blob_sha'] == blob(auth_path)
assert reseal['authorization_receipt_sha256'] == sha(auth_path)
assert reseal['execution_directive_git_blob_sha'] == blob(directive_path)
assert reseal['execution_directive_sha256'] == sha(directive_path)

workflow_path = pathlib.Path(auth['formal_workflow_path'])
workflow_blob = blob(workflow_path)
assert workflow_blob == auth['formal_workflow_git_blob_sha'] == directive['execution_workflow_git_blob_sha']
assert workflow_blob == reseal['formal_workflow_git_blob_sha']
trigger_path = auth['formal_proof_trigger_path']
assert trigger_path == directive['formal_proof_trigger_path'] == reseal['formal_proof_trigger_path']
workflow_text = workflow_path.read_text()
assert workflow_text.count('    paths:\n      - ' + trigger_path + '\n') == 1
assert workflow_text.count('      SOURCE_COMMIT: ' + auth['source_repository_commit'] + '\n') == 1

execution_wrapper_path = pathlib.Path(directive['execution_wrapper_path'])
formal_wrapper_path = pathlib.Path(auth['formal_wrapper_path'])
patcher_path = pathlib.Path(auth['runtime_binding_patcher_path'])
finalizer_path = pathlib.Path(auth['formal_finalizer_path'])
assert blob(execution_wrapper_path) == directive['execution_wrapper_git_blob_sha']
assert blob(execution_wrapper_path) == reseal['execution_wrapper_git_blob_sha']
assert blob(formal_wrapper_path) == auth['formal_wrapper_git_blob_sha'] == directive['formal_controller_wrapper_git_blob_sha']
assert blob(formal_wrapper_path) == reseal['formal_controller_wrapper_git_blob_sha']
assert blob(patcher_path) == auth['runtime_binding_patcher_git_blob_sha'] == directive['runtime_binding_patcher_git_blob_sha']
assert blob(patcher_path) == reseal['runtime_binding_patcher_git_blob_sha']
assert blob(finalizer_path) == auth['formal_finalizer_git_blob_sha'] == directive['formal_finalizer_git_blob_sha']
assert blob(finalizer_path) == reseal['formal_finalizer_git_blob_sha']

assert reseal['status'] == 'SEALED_STATIC_PREFLIGHT_ONLY'
assert reseal['authorization_consumed'] is False
assert reseal['proof_execution_started'] is False
assert reseal['proof_run_count_executed'] == 0
assert reseal['formal_proof_executed_during_reseal'] is False

subprocess.run(['git', 'merge-base', '--is-ancestor', auth['authorization_state_ancestor'], head], check=True)
subprocess.run(['git', 'merge-base', '--is-ancestor', directive['execution_package_ancestor'], head], check=True)
subprocess.run(['git', 'merge-base', '--is-ancestor', auth['source_repository_commit'], head], check=True)

safety_keys = (
    'production_application_authorized',
    'production_activation_authorized',
    'current_map_change_authorized',
    'persisted_data_change_authorized',
    'merge_authorized',
    'second_proof_run_authorized',
)
for key in safety_keys:
    assert auth[key] is False, key
    assert directive[key] is False, key
    assert reseal[key] is False, key

changed = subprocess.check_output(['git', 'diff', '--name-only', base, 'HEAD'], text=True).splitlines()
assert changed
assert trigger_path not in changed
assert not any(path.endswith('.pyc') or '/__pycache__/' in path for path in changed)

out = {
    'type': 'PMP_P2C_RECEIPT082_MERGED_MAIN_STATIC_RESEAL_PREFLIGHT_RESULT_115',
    'status': 'PASS_STATIC_PREFLIGHT_ONLY',
    'head_sha': head,
    'base_sha': base,
    'source_repository_commit': auth['source_repository_commit'],
    'authorization_receipt': '082',
    'execution_directive': '083',
    'static_reseal_receipt': '115',
    'authorization_sha256': sha(auth_path),
    'authorization_git_blob_sha': blob(auth_path),
    'execution_directive_sha256': sha(directive_path),
    'execution_directive_git_blob_sha': blob(directive_path),
    'execution_wrapper_git_blob_sha': blob(execution_wrapper_path),
    'formal_workflow_git_blob_sha': workflow_blob,
    'formal_controller_wrapper_git_blob_sha': blob(formal_wrapper_path),
    'runtime_binding_patcher_git_blob_sha': blob(patcher_path),
    'formal_finalizer_git_blob_sha': blob(finalizer_path),
    'formal_proof_trigger_path': trigger_path,
    'formal_proof_trigger_path_changed': False,
    'proof_run_count_executed': 0,
    'formal_proof_executed': False,
    'authorization_consumed': False,
    'production_activation_authorized': False,
    'current_map_change_authorized': False,
    'persisted_data_change_authorized': False,
    'second_proof_run_authorized': False,
    'changed_files': changed,
}
evidence_dir = pathlib.Path(os.environ['EVIDENCE_DIR'])
evidence_dir.mkdir(parents=True, exist_ok=True)
(evidence_dir / 'static-preflight-result-115.json').write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
print(json.dumps(out, indent=2, sort_keys=True))
