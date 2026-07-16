#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import sys
from typing import Any

ROOT = pathlib.Path('audit/pass2/p2c-isolated-proof-rerun-008')
DEPS = pathlib.Path('audit/pass2/p2c-isolated-proof-rerun-006')
TARGET_PR_HEAD = 'a0d24ec35bd366b5856d84186447eae55290e0a4'
TARGET_MAIN = '98b2e293717b81289e3b372d1fff8f5832d29fd6'
AUTH_ANCESTOR = 'eb83fef9c982d9f5658ebbadd402d0d9931da4b8'
ORIGINAL_CONTROLLER_BLOB = 'cff2fffc59680e667abb53b0c18f508f6561e9eb'
OLD_CONTROLLER = 'repair_runner_009_controller002.py'
NEW_CONTROLLER = 'repair_runner_009_controller002_policycompat_022.py'
OLD_PATCHER = 'efe861570ea5d8e63e197d468bee287ca179f849938973b1ed977658fb75af57'
NEW_PATCHER = 'd4dd82c4787cb0464e6d7be1edff11174e0f05d7bd177a096300661f7fde2024'
OLD_MANIFEST = '72d664d3ddf1890da802a5b7e00138a487682fde9859ef1c036f05c69e840619'
NEW_MANIFEST = 'd53dc787298e8fec5f00227b680645dffd25774913ba34461d4969df6bf2b803'
OLD_CONTROLLER_SHA = 'ad10e91f9f8319747d08f6f882031eae48aee7c9d7813b1a3f63ad5d0e4a72f7'
NEW_CONTROLLER_SHA = '1a553e229078239f0d17e25ca813788b4b25aa1d33fd511cdc179f1a6ebecb13'


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(['git', *args], text=True, capture_output=True, check=check)


def blob(path: pathlib.Path) -> str:
    return git('hash-object', str(path)).stdout.strip()


def main() -> int:
    output = pathlib.Path(sys.argv[1])
    queue: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []

    def record(label: str, expected: Any, actual: Any, passed: bool, order: int, affected: str, repair: str) -> None:
        row = {'label': label, 'expected': expected, 'actual': actual, 'pass': bool(passed), 'affected_file_or_binding': affected}
        checks.append(row)
        if not passed:
            queue.append({'dependency_order': order, **row, 'consolidated_repair': repair})

    receipt_path = ROOT / 'P2C_FINAL_ONE_RUN_PROOF_AUTHORIZATION_RECEIPT_026.json'
    repair_path = ROOT / 'P2C_RECEIPT024_WRAPPER_STATIC_REPAIR_RECEIPT_025.json'
    reseal_path = ROOT / 'P2C_EXHAUSTIVE_PREPROOF_STATIC_RESEAL_RECEIPT_023.json'
    wrapper = ROOT / 'rerun008-controller-main-receipt024.sh'
    finalizer = ROOT / 'rerun008-controller-finalize.sh'
    policy = DEPS / NEW_CONTROLLER
    manifest = DEPS / 'repair009-normalized-source-manifest-002.json'
    patcher = DEPS / 'repair-continuation-003/apply_prepare_repair_003.py'
    receipt = json.loads(receipt_path.read_text())
    repair = json.loads(repair_path.read_text())
    reseal = json.loads(reseal_path.read_text())

    event_action = os.environ.get('EVENT_ACTION')
    run_attempt = os.environ.get('RUN_ATTEMPT')
    checkout_head = git('rev-parse', 'HEAD').stdout.strip()
    github_sha = os.environ.get('HEAD_SHA')
    diagnostic_pr_head = os.environ.get('PR_HEAD_SHA')
    base_sha = os.environ.get('BASE_SHA')

    record('EVENT_ACTION_OPENED', 'opened', event_action, event_action == 'opened', 1, 'workflow event', 'retain pull_request.opened gate')
    record('RUN_ATTEMPT_ONE', '1', run_attempt, run_attempt == '1', 2, 'workflow attempt', 'retain first-attempt gate')
    record('CHECKOUT_EQUALS_GITHUB_SHA', checkout_head, github_sha, checkout_head == github_sha, 3, 'GitHub checkout identity', 'bind checkout HEAD to github.sha')
    # This explicitly diagnoses the broken PR #90 assertion without treating normal merge-checkout behavior as a closure failure.
    old_equality = github_sha == diagnostic_pr_head == checkout_head
    record('LEGACY_HEAD_EQUALS_PR_HEAD_ASSERTION', 'not required; merge SHA and PR head are distinct', {'github_sha': github_sha, 'pr_head_sha': diagnostic_pr_head, 'checkout_head': checkout_head}, not old_equality, 4, '.github/workflows/pass2-p2c-isolated-proof-rerun-006.yml', 'replace chained equality with two independent checks: checkout==github.sha and Receipt-026 branch head is ancestor of checkout')
    target_exists = git('cat-file', '-e', TARGET_PR_HEAD + '^{commit}', check=False).returncode == 0
    record('TARGET_PR90_HEAD_EXISTS', True, target_exists, target_exists, 5, 'PR #90 head', 'fetch exact PR head before closure')
    ancestor = target_exists and git('merge-base', '--is-ancestor', TARGET_PR_HEAD, checkout_head, check=False).returncode == 0
    record('TARGET_PR90_HEAD_ANCESTOR_OF_DIAGNOSTIC_CHECKOUT', True, ancestor, ancestor, 6, 'PR-head relationship', 'require target proof-state head to be an ancestor of diagnostic merge checkout')
    record('BASE_SHA_CURRENT_MAIN', TARGET_MAIN, base_sha, base_sha == TARGET_MAIN, 7, 'current-main binding', 'bind base SHA independently')
    auth_ancestor = git('merge-base', '--is-ancestor', AUTH_ANCESTOR, TARGET_PR_HEAD, check=False).returncode == 0
    record('AUTHORIZATION_STATE_ANCESTOR', True, auth_ancestor, auth_ancestor, 8, 'Receipt 026 state ancestry', 'preserve Receipt 026 ancestor binding')

    identities = [
        ('RECEIPT026_BLOB', receipt_path, '5042d0e1886ef02d02750fc4900c3a7f16ab67d9'),
        ('RECEIPT025_BLOB', repair_path, '014900ec0a9618e1f130e5ecc3ff0a9b568142e1'),
        ('RECEIPT023_BLOB', reseal_path, 'ffdfd2e8a991c22bb95d68b57205486ec2734ead'),
        ('WRAPPER_BLOB', wrapper, '58b647d1c3c73f249541a29803609185fbf5da32'),
        ('FINALIZER_BLOB', finalizer, '87e86c533d5d630121ded31334c46457ef4a7ad6'),
        ('POLICY_CONTROLLER_BLOB', policy, '3818d7ae0ea3bf2de98a23e334515ca0fd6da052'),
    ]
    for n, (label, path, expected) in enumerate(identities, 20):
        actual = blob(path)
        record(label, expected, actual, actual == expected, n, str(path), 'rebind only if the authoritative file changed')

    hashes = [
        ('WRAPPER_SHA256', wrapper, '85d92efb342655524399dfcd1efb2e8b337650150c544ededcd4149b533b3550'),
        ('FINALIZER_SHA256', finalizer, '5b092ffc4c8b37b0ed6a1d32c67445aec96ae4af149630f32446700e5a86d1d4'),
        ('PATCHER_SHA256', patcher, NEW_PATCHER),
        ('MANIFEST_SHA256', manifest, NEW_MANIFEST),
        ('POLICY_CONTROLLER_SHA256', policy, NEW_CONTROLLER_SHA),
    ]
    for n, (label, path, expected) in enumerate(hashes, 40):
        actual = sha(path)
        record(label, expected, actual, actual == expected, n, str(path), 'rebind only to the exact authoritative SHA-256')

    record('RECEIPT026_AUTHORIZED_UNCONSUMED', True, receipt.get('authorized') is True and receipt.get('status') == 'AUTHORIZED_UNCONSUMED' and receipt.get('authorization_consumed') is False, receipt.get('authorized') is True and receipt.get('status') == 'AUTHORIZED_UNCONSUMED' and receipt.get('authorization_consumed') is False, 60, str(receipt_path), 'preserve unconsumed receipt semantics during closure only')
    record('RECEIPT026_COUNTS', {'authorized': 1, 'executed': 0}, {'authorized': receipt.get('proof_run_count_authorized'), 'executed': receipt.get('proof_run_count_executed_under_this_receipt')}, receipt.get('proof_run_count_authorized') == 1 and receipt.get('proof_run_count_executed_under_this_receipt') == 0, 61, str(receipt_path), 'preserve exactly-one future run and zero executed')
    prohibited = ('production_application_authorized','production_activation_authorized','current_map_change_authorized','persisted_data_change_authorized','merge_authorized','second_proof_run_authorized')
    for n, key in enumerate(prohibited, 62):
        record('PROHIBITION_' + key.upper(), False, receipt.get(key), receipt.get(key) is False, n, str(receipt_path), 'retain false authorization boundary')
    record('RECEIPT025_STATIC_PASS', True, repair.get('status') == 'PASS_STATIC_PREFLIGHT' and repair.get('old_controller_path_replacement_count') == 4 and repair.get('new_controller_path_expected_count') == 4, repair.get('status') == 'PASS_STATIC_PREFLIGHT' and repair.get('old_controller_path_replacement_count') == 4 and repair.get('new_controller_path_expected_count') == 4, 70, str(repair_path), 'preserve corrected four-occurrence wrapper repair')
    record('RECEIPT023_RESEAL_PASS', True, reseal.get('status') == 'PASS_STATIC_RESEALED' and reseal.get('repair_queue_count') == 0 and reseal.get('compile_checks_passed') == 5, reseal.get('status') == 'PASS_STATIC_RESEALED' and reseal.get('repair_queue_count') == 0 and reseal.get('compile_checks_passed') == 5, 71, str(reseal_path), 'preserve exhaustive pre-proof reseal')

    changed = set(git('diff', '--name-only', TARGET_MAIN, TARGET_PR_HEAD).stdout.splitlines())
    allowed = {'.github/workflows/pass2-p2c-isolated-proof-rerun-006.yml', 'audit/a002-live-runtime.cjs'}
    extras = sorted(p for p in changed if p not in allowed and not p.startswith('audit/pass2/p2c-isolated-proof-rerun-006/') and not p.startswith('audit/pass2/p2c-isolated-proof-rerun-008/'))
    record('TARGET_PR90_CHANGED_PATH_ALLOWLIST', [], extras, not extras, 80, 'changed-path allowlist', 'remove any unrelated target-proof path')
    cache = sorted(p for p in changed if '/__pycache__/' in p or p.endswith('.pyc'))
    record('TARGET_PR90_CACHE_EXCLUSION', [], cache, not cache, 81, 'cache/.pyc exclusion', 'remove cache artifacts')

    materialized = pathlib.Path('/tmp/p2c-proof-entry-closure-materialized-027.sh')
    original = git('cat-file', 'blob', ORIGINAL_CONTROLLER_BLOB).stdout
    counts_before = {
        'old_controller': original.count(OLD_CONTROLLER),
        'old_patcher': original.count(OLD_PATCHER),
        'old_manifest': original.count(OLD_MANIFEST),
        'old_controller_sha': original.count(OLD_CONTROLLER_SHA),
    }
    expected_before = {'old_controller': 4, 'old_patcher': 1, 'old_manifest': 1, 'old_controller_sha': 1}
    for n, key in enumerate(expected_before, 90):
        record('MATERIALIZATION_COUNT_BEFORE_' + key.upper(), expected_before[key], counts_before[key], counts_before[key] == expected_before[key], n, str(wrapper), 'correct replacement census before materialization')
    text = original.replace(OLD_PATCHER, NEW_PATCHER).replace(OLD_MANIFEST, NEW_MANIFEST).replace(OLD_CONTROLLER, NEW_CONTROLLER).replace(OLD_CONTROLLER_SHA, NEW_CONTROLLER_SHA)
    materialized.write_text(text)
    counts_after = {'old_controller': text.count(OLD_CONTROLLER), 'new_controller': text.count(NEW_CONTROLLER), 'new_patcher': text.count(NEW_PATCHER), 'new_manifest': text.count(NEW_MANIFEST), 'new_controller_sha': text.count(NEW_CONTROLLER_SHA)}
    expected_after = {'old_controller': 0, 'new_controller': 4, 'new_patcher': 1, 'new_manifest': 1, 'new_controller_sha': 1}
    for n, key in enumerate(expected_after, 100):
        record('MATERIALIZATION_COUNT_AFTER_' + key.upper(), expected_after[key], counts_after[key], counts_after[key] == expected_after[key], n, str(materialized), 'ensure exact final replacement state')
    syntax = subprocess.run(['bash', '-n', str(materialized)], text=True, capture_output=True)
    record('MATERIALIZED_SHELL_SYNTAX', 0, {'returncode': syntax.returncode, 'stderr': syntax.stderr}, syntax.returncode == 0, 110, str(materialized), 'repair shell syntax without changing proof logic')

    # Produce a diagnostic hard-stop copy immediately before the first worktree-add command.
    marker = 'echo "=== Create exact detached baseline and active worktrees ==="'
    marker_count = text.count(marker)
    record('PRE_WORKTREE_HARD_STOP_MARKER_COUNT', 1, marker_count, marker_count == 1, 111, str(materialized), 'retain one unambiguous worktree boundary')
    prework_rc = None
    prework_stdout = ''
    prework_stderr = ''
    reached_hard_stop = False
    if marker_count == 1 and not any(x['dependency_order'] < 111 for x in queue):
        prefix = text.split(marker, 1)[0]
        diagnostic = pathlib.Path('/tmp/p2c-proof-entry-closure-preworktree-027.sh')
        diagnostic.write_text(prefix + "\nprintf '%s\\n' 'PROOF_ENTRY_CLOSURE_HARD_STOP_BEFORE_GIT_WORKTREE_ADD'\n")
        env = os.environ.copy()
        env.update({
            'EVENT_ACTION': 'opened',
            'RUN_ATTEMPT': '1',
            'HEAD_SHA': checkout_head,
            'BASE_SHA': TARGET_MAIN,
            'SOURCE_COMMIT': TARGET_MAIN,
            'AUDIT_DIR': str(ROOT),
            'DEPS_DIR': str(DEPS),
            'REPAIR_DIR': str(DEPS / 'repair-continuation-003'),
            'BUNDLE_DIR': '/tmp/p2c-closure-bundle-027',
            'BUNDLE_TAR': '/tmp/p2c-closure-bundle-027.tar.gz',
            'BASELINE_ROOT': '/tmp/p2c-closure-baseline-027',
            'ACTIVE_ROOT': '/tmp/p2c-closure-active-027',
            'EVIDENCE_DIR': '/tmp/p2c-closure-evidence-027',
            'NORMALIZED_ROOT': '/tmp/p2c-closure-normalized-027',
            'NODE_HOME': '/tmp/p2c-closure-node-027',
            'RUN_ID': 'DIAGNOSTIC_ONLY_027',
        })
        run = subprocess.run(['bash', str(diagnostic)], text=True, capture_output=True, env=env)
        prework_rc, prework_stdout, prework_stderr = run.returncode, run.stdout, run.stderr
        reached_hard_stop = run.returncode == 0 and 'PROOF_ENTRY_CLOSURE_HARD_STOP_BEFORE_GIT_WORKTREE_ADD' in run.stdout
        record('CONTROLLER_REACHES_PRE_WORKTREE_HARD_STOP', True, {'returncode': run.returncode, 'stdout_tail': run.stdout[-4000:], 'stderr_tail': run.stderr[-4000:]}, reached_hard_stop, 120, str(diagnostic), 'repair the complete independent pre-worktree failure set together')

    queue.sort(key=lambda x: (x['dependency_order'], x['label']))
    report = {
        'type': 'PMP_PASS2_PROOF_ENTRY_CLOSURE_027',
        'status': 'PASS_ZERO_REPAIR_QUEUE_REACHED_PRE_WORKTREE_HARD_STOP' if not queue and reached_hard_stop else 'COMPLETE_PROOF_ENTRY_FAILURE_SET_COLLECTED',
        'target_pr': 90,
        'target_pr_head': TARGET_PR_HEAD,
        'repair_queue_count': len(queue),
        'repair_queue_dependency_ordered': queue,
        'checks': checks,
        'materialized_controller': str(materialized),
        'preworktree_returncode': prework_rc,
        'preworktree_stdout_tail': prework_stdout[-8000:],
        'preworktree_stderr_tail': prework_stderr[-8000:],
        'hard_stop': {
            'reached_immediately_before_git_worktree_add': reached_hard_stop,
            'git_worktree_add_executed': False,
            'playwright_or_chromium_install_executed': False,
            'disposable_copy_preparation_executed': False,
            'browser_proof_executed': False,
            'proof_run_count_executed': 0,
            'proof_authorized_by_closure_pass': False,
            'production_files_modified': False,
            'current_map_modified': False,
            'persisted_data_modified': False,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
