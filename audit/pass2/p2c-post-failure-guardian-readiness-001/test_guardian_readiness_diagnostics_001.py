#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import pathlib
import subprocess
import tempfile
import unittest

import verify_guardian_readiness_unit_001 as scope_verifier
from guardian_readiness_contract_001 import (
    A003_OPEN_CURRENT_FUNCTION_NEW,
    CURRENT,
    EXPECTED_MANIFEST,
    EXPECTED_SW_VERSION,
    INTEGRITY_SW,
    NAVIGATION_TIMEOUT_MS,
    POLL_MS,
    READINESS_TIMEOUT_MS,
    ContractViolation,
    apply_guardian_readiness_patch_to_runner,
    assert_navigation_success,
    patch_generated_harness_source,
    validate_failure_evidence,
    validate_readiness_snapshot,
)


HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]


def valid_snapshot() -> dict:
    return {
        'controller_url': 'http://127.0.0.1:8013/' + INTEGRITY_SW,
        'integrity_status': {
            'type': 'PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE',
            'receipt': {
                'state': 'ENFORCED',
                'version': EXPECTED_SW_VERSION,
                'manifest_path': EXPECTED_MANIFEST,
            },
        },
        'current_map_handoff': {
            'path': CURRENT,
            'source_sha256': 'a' * 64,
            'integrity_manifest_sha256': 'b' * 64,
        },
        'launch_state': {'present': True, 'disabled': False, 'visible': True},
        'canonical_reload_ready': True,
    }


def valid_failure() -> dict:
    return {
        'screen': 'bank',
        'attempt': 2,
        'observed_top_level_url': 'http://127.0.0.1:8013/pmp-app-current.html#bank',
        'guardian_frame_url': 'http://127.0.0.1:8013/pmp-route-guardian-current-loader-v22.html#bank',
        'guardian_message': 'Verified handoff accepted. Launching...',
        'guardian_report': '{}',
        'guardian_receipt': {'type': 'RG22_RUN'},
        'request_ledger': [],
        'controller_url': 'http://127.0.0.1:8013/' + INTEGRITY_SW,
        'top_controller_url': 'http://127.0.0.1:8013/' + INTEGRITY_SW,
        'launch_state': {'present': True, 'disabled': True, 'visible': True},
        'navigation_assignment_observed': False,
        'timeout_evidence': {
            'timed_out': True,
            'readiness_timeout_ms': READINESS_TIMEOUT_MS,
            'navigation_timeout_ms': NAVIGATION_TIMEOUT_MS,
            'poll_ms': POLL_MS,
            'elapsed_ms': 30001,
        },
        'error': {'name': 'TimeoutError', 'message': 'timeout'},
    }


class GuardianReadinessContractTests(unittest.TestCase):
    def _ancestry_fixture(self) -> tuple[pathlib.Path, str, str, str]:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        repo = pathlib.Path(temp.name)
        subprocess.run(['git', 'init', '-q', str(repo)], check=True)
        subprocess.run(['git', '-C', str(repo), 'config', 'user.name', 'PMP Unit 2A Test'], check=True)
        subprocess.run(['git', '-C', str(repo), 'config', 'user.email', 'unit2a@example.invalid'], check=True)
        (repo / 'base.txt').write_text('base\n')
        subprocess.run(['git', '-C', str(repo), 'add', 'base.txt'], check=True)
        subprocess.run(['git', '-C', str(repo), 'commit', '-q', '-m', 'base'], check=True)
        base = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
        subprocess.run(['git', '-C', str(repo), 'checkout', '-q', '-b', 'pr-head'], check=True)
        (repo / 'repair.txt').write_text('repair\n')
        subprocess.run(['git', '-C', str(repo), 'add', 'repair.txt'], check=True)
        subprocess.run(['git', '-C', str(repo), 'commit', '-q', '-m', 'repair'], check=True)
        pr_head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
        subprocess.run(['git', '-C', str(repo), 'checkout', '-q', '--detach', base], check=True)
        subprocess.run(['git', '-C', str(repo), 'merge', '-q', '--no-ff', pr_head, '-m', 'temporary PR merge'], check=True)
        merge_head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
        unrelated_tree = subprocess.check_output(['git', '-C', str(repo), 'mktree'], input='', text=True).strip()
        unrelated = subprocess.check_output(
            ['git', '-C', str(repo), 'commit-tree', unrelated_tree, '-m', 'unrelated'],
            text=True,
        ).strip()
        return repo, pr_head, merge_head, unrelated

    def test_pr_merge_checkout_accepts_pr_head_ancestor(self) -> None:
        repo, pr_head, merge_head, _ = self._ancestry_fixture()
        original_root = scope_verifier.ROOT
        try:
            scope_verifier.ROOT = repo
            self.assertTrue(scope_verifier.is_ancestor(pr_head, merge_head))
        finally:
            scope_verifier.ROOT = original_root

    def test_unrelated_commit_is_rejected_by_ancestry_check(self) -> None:
        repo, _, merge_head, unrelated = self._ancestry_fixture()
        original_root = scope_verifier.ROOT
        try:
            scope_verifier.ROOT = repo
            self.assertFalse(scope_verifier.is_ancestor(unrelated, merge_head))
        finally:
            scope_verifier.ROOT = original_root

    def test_valid_readiness_snapshot(self) -> None:
        validate_readiness_snapshot(valid_snapshot())

    def test_missing_controller_fails_closed(self) -> None:
        row = valid_snapshot(); row['controller_url'] = None
        with self.assertRaisesRegex(ContractViolation, 'MISSING_CONTROLLER'):
            validate_readiness_snapshot(row)

    def test_missing_integrity_response_fails_closed(self) -> None:
        row = valid_snapshot(); row['integrity_status'] = None
        with self.assertRaisesRegex(ContractViolation, 'MISSING_INTEGRITY_RESPONSE'):
            validate_readiness_snapshot(row)

    def test_missing_current_map_handoff_fails_closed(self) -> None:
        row = valid_snapshot(); row['current_map_handoff'] = None
        with self.assertRaisesRegex(ContractViolation, 'MISSING_CURRENT_MAP_HANDOFF'):
            validate_readiness_snapshot(row)

    def test_no_navigation_assignment_fails_closed(self) -> None:
        with self.assertRaisesRegex(ContractViolation, 'NO_NAVIGATION_ASSIGNMENT'):
            assert_navigation_success({'navigation_assignment_observed': False}, 'bank')

    def test_wrong_final_url_fails_closed(self) -> None:
        row = {'navigation_assignment_observed': True, 'observed_top_level_url': 'http://127.0.0.1:8013/not-current.html#bank'}
        with self.assertRaisesRegex(ContractViolation, 'WRONG_FINAL_URL'):
            assert_navigation_success(row, 'bank')

    def test_wrong_final_hash_fails_closed(self) -> None:
        row = {'navigation_assignment_observed': True, 'observed_top_level_url': f'http://127.0.0.1:8013/{CURRENT}#control'}
        with self.assertRaisesRegex(ContractViolation, 'WRONG_FINAL_HASH'):
            assert_navigation_success(row, 'bank')

    def test_absent_timeout_evidence_fails_closed(self) -> None:
        row = valid_failure(); row.pop('timeout_evidence')
        with self.assertRaisesRegex(ContractViolation, 'FAILURE_EVIDENCE_MISSING'):
            validate_failure_evidence(row)

    def test_complete_failure_evidence_is_accepted(self) -> None:
        validate_failure_evidence(valid_failure())

    def test_canonical_reload_not_ready_fails_closed(self) -> None:
        row = valid_snapshot(); row['canonical_reload_ready'] = False
        with self.assertRaisesRegex(ContractViolation, 'CANONICAL_RELOAD_NOT_READY'):
            validate_readiness_snapshot(row)

    def test_launch_not_ready_fails_closed(self) -> None:
        row = valid_snapshot(); row['launch_state']['disabled'] = True
        with self.assertRaisesRegex(ContractViolation, 'LAUNCH_NOT_READY'):
            validate_readiness_snapshot(row)

    def test_timeout_flag_is_required(self) -> None:
        row = valid_failure(); row['timeout_evidence'].pop('timed_out')
        with self.assertRaisesRegex(ContractViolation, 'TIMEOUT_EVIDENCE_INVALID'):
            validate_failure_evidence(row)

    def test_generated_harness_patch_is_syntax_valid_and_bounded(self) -> None:
        original = """'use strict';
const state = { tamperPath: null, offlinePath: null, requests: [] };
const results = []; let fatalError = null;
function writeOutput(){ const output={fatal_error: fatalError, results, request_count: state.requests.length}; return output; }
async function guardianFrame(page){ return page; }
async function frameReachedHome(page, hash){ return {reached:true, hash_matches:true}; }
async function openCurrentFromGuardian(page, screen) {
  const frame = await guardianFrame(page);
  await frame.click('#openBtn',{force:true});
  await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#' + screen, { timeout: 30000, waitUntil: 'commit' });
  return frameReachedHome(page, '#' + screen);
}
"""
        patched = patch_generated_harness_source(original)
        self.assertEqual(patched.count('guardian_diagnostics: state.guardianDiagnostics'), 1)
        self.assertEqual(patched.count('guardian_evidence_path: A003_GUARDIAN_EVIDENCE_PATH'), 1)
        self.assertEqual(patched.count('const readinessTimeoutMs = 15000;'), 1)
        self.assertEqual(patched.count('const navigationTimeoutMs = 30000;'), 1)
        self.assertEqual(patched.count('const pollMs = 250;'), 1)
        self.assertNotIn('while (true)', A003_OPEN_CURRENT_FUNCTION_NEW)
        self.assertNotIn('setInterval(', A003_OPEN_CURRENT_FUNCTION_NEW)
        for token in ('observed_top_level_url', 'guardian_frame_url', 'guardian_receipt', 'guardian_message', 'guardian_report', 'request_ledger', 'controller_url', 'top_controller_url', 'launch_state', 'screen', 'attempt', 'elapsed_ms', 'A003_GUARDIAN_EVIDENCE_PATH', 'persistGuardianAttempt'):
            self.assertIn(token, A003_OPEN_CURRENT_FUNCTION_NEW)
        with tempfile.NamedTemporaryFile('w', suffix='.cjs', delete=False) as handle:
            handle.write(patched)
            temp_path = pathlib.Path(handle.name)
        try:
            result = subprocess.run(['node', '--check', str(temp_path)], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_runner_injection_is_single_and_static_only(self) -> None:
        runner = "prefix\n a003.write_text(s)\nsuffix\n"
        patched = apply_guardian_readiness_patch_to_runner(runner)
        self.assertEqual(patched.count(' a003.write_text(s)'), 1)
        self.assertIn('GUARDIAN001_OPEN_CURRENT_ANCHOR_INVALID', patched)
        for forbidden in ('rerun008-controller-main-receipt082.sh', 'run_receipt082_exactly_one_formal_proof.sh', 'workflow_dispatch', 'gh workflow run'):
            self.assertNotIn(forbidden, patched)

    def test_contract_is_disposable_harness_only(self) -> None:
        forbidden = ('production activation', 'persisted data write', 'current map mutation')
        lower = A003_OPEN_CURRENT_FUNCTION_NEW.lower()
        for token in forbidden:
            self.assertNotIn(token, lower)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(GuardianReadinessContractTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary = {
        'type': 'PMP_APP_ORCHESTRATOR_P2C_GUARDIAN_READINESS_STATIC_TEST_RESULT_001',
        'status': 'PASS' if result.wasSuccessful() else 'FAIL',
        'tests_run': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'authorization_consumed': True,
        'proof_run_count_executed': 1,
        'formal_proof_executed': False,
        'controller_invoked': False,
        'production_changed': False,
    }
    print(json.dumps(summary, sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() else 1)
