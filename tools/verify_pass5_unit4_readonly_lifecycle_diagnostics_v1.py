#!/usr/bin/env python3
import base64
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
    '.github/workflows/pass5-unit3-passive-lifecycle-integration-v1.yml',
    '.github/workflows/pass5-unit4-readonly-lifecycle-diagnostics-v1.yml',
    'audit/a003-manifest-seal.json',
    'audit/pass5/pass5-mount-registry-diagnostics-unit4-readonly-view-v1.json',
    'audit/pass5/receipts/RECEIPT_P5_U4_READONLY_DIAGNOSTICS_20260726T080923Z_001.json',
    'pmp-app-current.html',
    'pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html',
    'pmp-diagnostics-owner-v1.js',
    'pmp-mount-lifecycle-diagnostics-view-v1.js',
    'pmp-runtime-integrity-manifest-v1.json',
    'tools/generate_pass5_unit4_integrity_updates_v1.py',
    'tools/test_pass5_unit4_readonly_lifecycle_diagnostics_v1.js',
    'tools/verify_pass5_unit4_readonly_lifecycle_diagnostics_v1.py',
}
PROTECTED={
    'pmp-mount-lifecycle-contract-v1.js',
    'pmp-mount-lifecycle-runtime-v1.js',
    'pmp-mount-registry-v1.js',
    'pmp-pass2-atlas-adapter-v2.js',
    'pmp-diagnostics-bottom-tab-forcer-v1.js',
    'pmp-app-orchestrator-v1.js',
    'pmp-authority-rules-v1.js',
    'pmp-current-map-v12.json',
    'pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html',
}
INNER='pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html'
VIEW='pmp-mount-lifecycle-diagnostics-view-v1.js'
DIAGNOSTICS='pmp-diagnostics-owner-v1.js'
LOAD_ORDER=[
    'pmp-mount-lifecycle-runtime-v1.js',
    VIEW,
    'pmp-authority-rules-v1.js',
]

def output(*args):
    return subprocess.check_output(args,cwd=ROOT,text=True).strip()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def main():
    base=sys.argv[1] if len(sys.argv)>1 and sys.argv[1] else 'HEAD^'
    changed=set(filter(None,output('git','diff','--name-only',f'{base}...HEAD').splitlines()))
    assert changed==EXPECTED,(sorted(changed),sorted(EXPECTED))
    assert not changed&PROTECTED

    inner=(ROOT/INNER).read_text('utf-8')
    positions=[]
    for path in LOAD_ORDER:
        matches=list(re.finditer(r'<script src="'+re.escape(path)+r'\?[^"]+"></script>',inner))
        assert len(matches)==1,(path,len(matches))
        positions.append(matches[0].start())
    assert positions==sorted(positions)

    source=(ROOT/VIEW).read_text('utf-8')
    for forbidden in (
        'localStorage',
        'sessionStorage',
        'indexedDB',
        'document.',
        'fetch(',
        'XMLHttpRequest',
        'setTimeout(',
        'setInterval(',
        'location.',
        '.src=',
        'applyOwnerEvent',
        'registry.apply',
    ):
        assert forbidden not in source,forbidden
    assert source.count('runtime.lifecycleSnapshot()')==1

    diagnostics=(ROOT/DIAGNOSTICS).read_text('utf-8')
    assert diagnostics.count("{id:'mount_registry'")==1
    assert "mount_lifecycle:lifecycle" in diagnostics
    assert "readMountLifecycle:lifecycleView" in diagnostics
    assert "lifecycle_event_application:'not_attempted'" in diagnostics
    assert 'applyOwnerEvent' not in diagnostics

    manifest_bytes=(ROOT/'pmp-runtime-integrity-manifest-v1.json').read_bytes()
    manifest=json.loads(manifest_bytes)
    assert manifest['counts']['runtime_records']==703
    assert manifest['counts']['executable_records']==703
    index={row['path']:row for row in manifest['records']}
    assert len(index)==703
    for rel in (VIEW,DIAGNOSTICS,INNER):
        data=(ROOT/rel).read_bytes()
        digest=hashlib.sha256(data).digest()
        row=index[rel]
        assert row['bytes']==len(data)
        assert row['git_blob_sha']==blob(data)
        assert row['sha256_hex']==digest.hex()
        assert row['sha256_base64']==base64.b64encode(digest).decode()
        assert row['sri']=='sha256-'+base64.b64encode(digest).decode()

    identity={
        'records':[(row['path'],row['sha256_hex']) for row in manifest.get('records',[])],
        'historical_records':[
            (row['path'],row.get('repository_ref'),row['sha256_hex'])
            for row in manifest.get('historical_records',[])
        ],
        'external_records':[
            (row['url'],row['sha256_hex']) for row in manifest.get('external_records',[])
        ],
        'root_trust_anchors':manifest.get('root_trust_anchors',[]),
        'policy':{
            'algorithm':manifest.get('algorithm'),
            'unlisted_executable_policy':manifest.get('unlisted_executable_policy'),
            'network_policy':manifest.get('network_policy'),
        },
    }
    expected_runtime_hash=sha(json.dumps(identity,sort_keys=True,separators=(',',':')).encode())
    assert manifest['runtime_source_set_sha256']==expected_runtime_hash

    manifest_sha=sha(manifest_bytes)
    seal=json.loads((ROOT/'audit/a003-manifest-seal.json').read_text('utf-8'))
    assert seal['manifest_sha256']==manifest_sha
    assert seal['manifest_bytes']==len(manifest_bytes)
    assert seal['runtime_source_set_sha256']==expected_runtime_hash
    bootstrap=(ROOT/'pmp-app-current.html').read_text('utf-8')
    assert re.search(r"const MANIFEST_SHA256='"+manifest_sha+r"';",bootstrap)

    audit=json.loads(
        (ROOT/'audit/pass5/pass5-mount-registry-diagnostics-unit4-readonly-view-v1.json').read_text()
    )
    assert audit['status']=='READ_ONLY_DIAGNOSTICS_PROVEN_PENDING_MERGE'
    assert audit['authority']['event_application_entrypoint_available_to_view'] is False
    assert audit['redaction']['raw_events_exposed'] is False
    assert audit['effects']['lifecycle_events_applied'] is False
    assert audit['effects']['persisted_user_data_changed'] is False
    assert audit['effects']['live_observation_performed'] is False
    assert audit['next_step']['id']=='P5-U5'
    assert audit['next_step']['requires_user_app_check'] is False

    receipt=json.loads(
        (ROOT/'audit/pass5/receipts/RECEIPT_P5_U4_READONLY_DIAGNOSTICS_20260726T080923Z_001.json').read_text()
    )
    assert receipt['schema']=='PMP_APP_ORCHESTRATOR_STEP_RECEIPT_V1'
    assert receipt['status']=='PASS_BOUNDED'
    assert receipt['scope']['changed_paths']==sorted(EXPECTED)
    assert receipt['authority']['special_authority_type']=='NONE'
    assert receipt['authority']['special_authority_consumed'] is False

    workflow=(ROOT/'.github/workflows/pass5-unit4-readonly-lifecycle-diagnostics-v1.yml').read_text()
    for forbidden in ('workflow_dispatch','playwright','http.server','npm install','pip install'):
        assert forbidden not in workflow,forbidden
    unit3_workflow=(ROOT/'.github/workflows/pass5-unit3-passive-lifecycle-integration-v1.yml').read_text()
    assert "git diff --quiet \"$BASE_SHA...HEAD\" -- pmp-mount-lifecycle-runtime-v1.js" in unit3_workflow
    assert "'pmp-app-current.html'" not in unit3_workflow
    assert "'pmp-runtime-integrity-manifest-v1.json'" not in unit3_workflow

    subprocess.check_call(['node','tools/test_pass5_unit2_mount_lifecycle_contract_v1.js'],cwd=ROOT)
    subprocess.check_call(['node','tools/test_pass5_unit3_passive_lifecycle_integration_v1.js'],cwd=ROOT)
    subprocess.check_call(['node','tools/test_pass5_unit4_readonly_lifecycle_diagnostics_v1.js'],cwd=ROOT)
    subprocess.check_call([sys.executable,'tools/generate_pass5_unit4_integrity_updates_v1.py'],cwd=ROOT)
    assert not output('git','status','--porcelain'),'integrity generation is not idempotent'
    print('PASS: exact thirteen-file P5-U4 read-only lifecycle Diagnostics integration verified')

if __name__=='__main__':
    main()
