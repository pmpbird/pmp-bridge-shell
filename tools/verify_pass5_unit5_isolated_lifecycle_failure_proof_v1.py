#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'audit/pass5/pass5-mount-registry-unit5-isolated-transition-failure-proof-v1.json'
RUNNER=ROOT/'tools/run_pass5_unit5_isolated_lifecycle_failure_proof_v1.js'
RECEIPT=ROOT/'audit/pass5/receipts/RECEIPT_P5_U5_ISOLATED_PROOF_20260726T082400Z_001.json'
EXPECTED={
    '.github/workflows/pass5-unit5-isolated-lifecycle-proof-v1.yml',
    'audit/pass5/pass5-mount-registry-unit5-isolated-transition-failure-proof-v1.json',
    'audit/pass5/receipts/RECEIPT_P5_U5_ISOLATED_PROOF_20260726T082400Z_001.json',
    'tools/run_pass5_unit5_isolated_lifecycle_failure_proof_v1.js',
    'tools/verify_pass5_unit5_isolated_lifecycle_failure_proof_v1.py',
}
PROTECTED={
    'pmp-app-current.html',
    'pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html',
    'pmp-current-map-v12.json',
    'pmp-runtime-integrity-manifest-v1.json',
    'audit/a003-manifest-seal.json',
    'pmp-mount-lifecycle-contract-v1.js',
    'pmp-mount-lifecycle-runtime-v1.js',
    'pmp-mount-lifecycle-diagnostics-view-v1.js',
    'pmp-mount-registry-v1.js',
    'pmp-diagnostics-owner-v1.js',
    'pmp-diagnostics-bottom-tab-forcer-v1.js',
    'pmp-app-orchestrator-v1.js',
}

def output(*args):
    return subprocess.check_output(args,cwd=ROOT,text=True).strip()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    base=sys.argv[1] if len(sys.argv)>1 and sys.argv[1] else 'HEAD^'
    changed=set(filter(None,output('git','diff','--name-only',f'{base}...HEAD').splitlines()))
    assert changed==EXPECTED,(sorted(changed),sorted(EXPECTED))
    assert not changed&PROTECTED
    assert all(
        Path(path).parts[0] in {'.github','audit','tools'}
        for path in changed
    )

    report=json.loads(REPORT.read_text())
    coverage=report['coverage']
    assert report['status']=='PASS_ISOLATED_PROOF'
    assert report['base_main_commit']=='6f19ca6594b6a8950caed60d027075d2ba30eb46'
    assert report['mode']=='ISOLATED_DETERMINISTIC_FIXTURES_ONLY'
    assert coverage['assertions_total']==138
    assert coverage['assertions_passed']==138
    assert coverage['assertions_failed']==0
    assert len(report['assertions'])==138
    assert all(row['pass'] is True for row in report['assertions'])
    assert set(coverage['category_counts'])=={
        'identity',
        'happy_path',
        'slow_degraded_recovery',
        'terminal_paths',
        'schema_failures',
        'authority_failures',
        'ordering_failures',
        'retention',
        'restart',
        'compatibility',
        'runtime',
        'diagnostics',
        'zero_effect_source',
    }
    assert sum(coverage['category_counts'].values())==138

    for field,value in report['effects'].items():
        if isinstance(value,bool):
            assert value is False,(field,value)
        elif isinstance(value,int):
            assert value==0,(field,value)
    assert report['authority']['special_authority_type']=='NONE'
    assert report['authority']['special_authority_consumed'] is False
    assert report['next_step']['id']=='P5-U6'
    assert report['next_step']['requires_user_app_check'] is False

    for rel,digest in report['components']['source_sha256'].items():
        assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest,rel

    receipt=json.loads(RECEIPT.read_text())
    assert receipt['schema']=='PMP_APP_ORCHESTRATOR_STEP_RECEIPT_V1'
    assert receipt['status']=='PASS_BOUNDED'
    assert receipt['scope']['changed_paths']==sorted(EXPECTED)
    assert receipt['verification']['assertions_total']==138
    assert receipt['verification']['assertions_failed']==0
    assert receipt['verification']['proof_report_sha256']==sha(REPORT)
    assert receipt['verification']['proof_runner_sha256']==sha(RUNNER)
    assert receipt['authority']['special_authority_type']=='NONE'
    assert receipt['authority']['special_authority_consumed'] is False
    assert receipt['effects']['production_runtime_changed'] is False
    assert receipt['effects']['live_observation_performed'] is False
    assert receipt['effects']['formal_proof_performed'] is False

    workflow=(ROOT/'.github/workflows/pass5-unit5-isolated-lifecycle-proof-v1.yml').read_text()
    for forbidden in (
        'workflow_dispatch',
        'playwright',
        'http.server',
        'npm install',
        'pip install',
        'pmp-app-current.html',
        'pmp-runtime-integrity-manifest-v1.json',
    ):
        assert forbidden not in workflow,forbidden

    with tempfile.TemporaryDirectory(prefix='p5-u5-proof-') as temp:
        generated=Path(temp)/'proof.json'
        subprocess.check_call(['node',str(RUNNER),str(generated)],cwd=ROOT)
        assert generated.read_bytes()==REPORT.read_bytes(),'committed proof is not deterministic'

    assert not output('git','status','--porcelain'),'proof verification changed the worktree'
    print('PASS: exact five-file P5-U5 isolated lifecycle proof verified (138/138)')

if __name__=='__main__':
    main()
