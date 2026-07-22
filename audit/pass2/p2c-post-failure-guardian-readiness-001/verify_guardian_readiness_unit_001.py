#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MAIN_ANCHOR = 'd109cac3b89e67e28a2ae8ffae43e28b6a8009a7'
ALLOWED_EXACT = {
    '.github/workflows/pass2-p2c-a002-native-messageport-rehearsal-088.yml',
    'audit/pass2/p2c-isolated-proof-rerun-008/patch_ci_lane_closure_rehearsal109.py',
    'audit/pass2/p2c-isolated-proof-rerun-008/patch_ci_lane_lifecycle_rehearsal111.py',
}
ALLOWED_PREFIX = 'audit/pass2/p2c-post-failure-guardian-readiness-001/'
REQUIRED_CHANGED = {
    '.github/workflows/pass2-p2c-a002-native-messageport-rehearsal-088.yml',
    'audit/pass2/p2c-isolated-proof-rerun-008/patch_ci_lane_lifecycle_rehearsal111.py',
}
CRITICAL_PRESERVED = [
    'audit/pass2/p2c-isolated-proof-rerun-008/P2C_NODEPATH_ROLLBACK_SOURCE_REPAIR_AUTHORIZATION_RECEIPT_082.json',
    'audit/pass2/p2c-isolated-proof-rerun-008/P2C_RECEIPT082_EXACTLY_ONE_FORMAL_PROOF_EXECUTION_DIRECTIVE_083.json',
    'audit/pass2/p2c-isolated-proof-rerun-008/P2C_RECEIPT082_FORMAL_PROOF_PR_HEAD_SEAL_084.json',
    '.github/workflows/pass2-p2c-isolated-proof-rerun-006.yml',
    'audit/pass2/p2c-isolated-proof-rerun-008/run_receipt082_exactly_one_formal_proof.sh',
    'audit/pass2/p2c-isolated-proof-rerun-008/rerun008-controller-main-receipt082.sh',
    'audit/pass2/p2c-isolated-proof-rerun-008/patch_runtime_nodepath_and_source_bindings_receipt082.py',
    'audit/pass2/p2c-isolated-proof-rerun-008/rerun008-controller-finalize.sh',
    'pmp-current-map-v12.json',
    'pmp-safe-writer-current-return-fix-v1.js',
    'pmp-route-guardian-current-loader-v22.html',
    'pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html',
    'pmp-runtime-integrity-manifest-v1.json',
]
FORBIDDEN_WORKFLOW_TOKENS = (
    'workflow_dispatch',
    'run_receipt082_exactly_one_formal_proof.sh',
    'rerun008-controller-main-receipt082.sh',
    'pass2-p2c-isolated-proof-rerun-006.yml',
    'gh workflow run',
)


def git(*args: str) -> str:
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def is_ancestor(ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ['git', 'merge-base', '--is-ancestor', ancestor, descendant],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_blob(commit: str, path: str) -> str:
    return git('rev-parse', f'{commit}:{path}')


def current_blob(path: str) -> str:
    return git('hash-object', path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-sha', required=True)
    parser.add_argument('--head-sha', required=True)
    parser.add_argument('--evidence-dir', type=pathlib.Path, required=True)
    args = parser.parse_args()
    args.evidence_dir.mkdir(parents=True, exist_ok=True)

    head = git('rev-parse', 'HEAD')
    if head != args.head_sha and not is_ancestor(args.head_sha, head):
        raise SystemExit(f'GUARDIAN001_CHECKOUT_HEAD_INVALID:{head}:{args.head_sha}')
    subprocess.run(['git', 'merge-base', '--is-ancestor', MAIN_ANCHOR, args.base_sha], cwd=ROOT, check=True)

    changed = git('diff', '--name-only', args.base_sha, args.head_sha).splitlines()
    if not changed:
        raise SystemExit('GUARDIAN001_CHANGED_SET_EMPTY')
    outside = sorted(path for path in changed if path not in ALLOWED_EXACT and not path.startswith(ALLOWED_PREFIX))
    if outside:
        raise SystemExit('GUARDIAN001_SCOPE_VIOLATION:' + json.dumps(outside))
    missing_required = sorted(REQUIRED_CHANGED - set(changed))
    if missing_required:
        raise SystemExit('GUARDIAN001_REQUIRED_CHANGE_MISSING:' + json.dumps(missing_required))
    if not any(path.startswith(ALLOWED_PREFIX) for path in changed):
        raise SystemExit('GUARDIAN001_BOUNDED_DIRECTORY_MISSING')
    if any(path.endswith('.pyc') or '/__pycache__/' in path for path in changed):
        raise SystemExit('GUARDIAN001_COMPILED_PYTHON_FORBIDDEN')

    preserved = []
    for path in CRITICAL_PRESERVED:
        base_blob = tree_blob(args.base_sha, path)
        head_blob = tree_blob(args.head_sha, path)
        if base_blob != head_blob:
            raise SystemExit(f'GUARDIAN001_CRITICAL_BLOB_CHANGED:{path}:{base_blob}:{head_blob}')
        preserved.append({'path': path, 'git_blob_sha': head_blob})

    workflow_path = ROOT / '.github/workflows/pass2-p2c-a002-native-messageport-rehearsal-088.yml'
    workflow_text = workflow_path.read_text()
    for token in FORBIDDEN_WORKFLOW_TOKENS:
        if token in workflow_text:
            raise SystemExit('GUARDIAN001_WORKFLOW_FORBIDDEN_TOKEN:' + token)
    required_workflow_tokens = (
        'test_guardian_readiness_diagnostics_001.py',
        'verify_guardian_readiness_unit_001.py',
        'rerun008-controller-main-rehearsal088.sh',
        'if: github.event.action == \'opened\' && github.run_attempt == 1',
    )
    for token in required_workflow_tokens:
        if token not in workflow_text:
            raise SystemExit('GUARDIAN001_WORKFLOW_REQUIRED_TOKEN_MISSING:' + token)

    python_paths = [
        ROOT / 'audit/pass2/p2c-isolated-proof-rerun-008/patch_ci_lane_lifecycle_rehearsal111.py',
        HERE / 'guardian_readiness_contract_001.py',
        HERE / 'test_guardian_readiness_diagnostics_001.py',
        HERE / 'verify_guardian_readiness_unit_001.py',
    ]
    for path in python_paths:
        ast.parse(path.read_text(), filename=str(path))

    test = subprocess.run(
        [sys.executable, str(HERE / 'test_guardian_readiness_diagnostics_001.py')],
        cwd=HERE,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if test.returncode:
        raise SystemExit('GUARDIAN001_STATIC_TESTS_FAILED:' + test.stdout[-8000:])
    test_lines = [line for line in test.stdout.splitlines() if line.startswith('{')]
    test_result = json.loads(test_lines[-1]) if test_lines else {'status': 'PASS', 'raw_output': test.stdout[-4000:]}

    runner_patch = (ROOT / 'audit/pass2/p2c-isolated-proof-rerun-008/patch_ci_lane_lifecycle_rehearsal111.py').read_text()
    required_runner_tokens = (
        'apply_guardian_readiness_patch_to_runner',
        'openCurrentFromGuardian(page, screen, attempt)',
        'guardian-readiness-diagnostics-repair-001.json',
        'DISPOSABLE_TEST_HARNESS_ONLY',
        'contract_summary',

    )
    for token in required_runner_tokens:
        if token not in runner_patch:
            raise SystemExit('GUARDIAN001_RUNNER_PATCH_TOKEN_MISSING:' + token)

    output = {
        'type': 'PMP_APP_ORCHESTRATOR_P2C_POST_FAILURE_GUARDIAN_READINESS_VERIFICATION_001',
        'status': 'PASS_STATIC_SCOPE_AND_TESTS',
        'base_sha': args.base_sha,
        'head_sha': args.head_sha,
        'checkout_head': head,
        'changed_files': changed,
        'critical_preserved_blobs': preserved,
        'static_tests': test_result,
        'authorization_consumed': True,
        'proof_run_count_executed': 1,
        'formal_proof_result': 'FAIL',
        'formal_proof_executed_during_unit': False,
        'controller_invoked': False,
        'workflow_dispatch_or_rerun': False,
        'production_changed': False,
        'candidate_runtime_changed': False,
        'current_map_changed': False,
        'persisted_data_changed': False,
        'merge_authorized': False,
        'pass3_started': False,
        'files': [{'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size, 'sha256': sha256(path)} for path in python_paths + [workflow_path]],
    }
    out_path = args.evidence_dir / 'guardian-readiness-unit-verification-001.json'
    out_path.write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
