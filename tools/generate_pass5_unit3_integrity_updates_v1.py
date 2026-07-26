#!/usr/bin/env python3
from __future__ import annotations
import base64
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'pmp-runtime-integrity-manifest-v1.json'
SEAL=ROOT/'audit/a003-manifest-seal.json'
BOOTSTRAP=ROOT/'pmp-app-current.html'
INNER=ROOT/'pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html'
RUNTIME='pmp-mount-lifecycle-runtime-v1.js'
INNER_REL=INNER.name
ATLAS='<script src="pmp-pass2-atlas-adapter-v2.js?fresh=pass2-atlas-pass5-stable-20260704I"></script>'
CONTRACT='<script src="pmp-mount-lifecycle-contract-v1.js?fresh=pass5-unit3-lifecycle-contract-20260726A"></script>'
LEGACY='<script src="pmp-mount-registry-v1.js?fresh=mount-registry-pass7-v21-v29-atlas-minimal-20260706B"></script>'
RUNTIME_TAG='<script src="pmp-mount-lifecycle-runtime-v1.js?fresh=pass5-unit3-passive-integration-20260726A"></script>'
OLD_BLOCK=ATLAS+'\n'+LEGACY
NEW_BLOCK=ATLAS+'\n'+CONTRACT+'\n'+LEGACY+'\n'+RUNTIME_TAG

def sha(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def blob(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def record(path:str,existing:dict|None=None)->dict:
    data=(ROOT/path).read_bytes()
    digest=hashlib.sha256(data).digest()
    result=dict(existing or {})
    result.update({
        'path':path,
        'bytes':len(data),
        'git_blob_sha':blob(data),
        'sha256_hex':digest.hex(),
        'sha256_base64':base64.b64encode(digest).decode(),
        'sri':'sha256-'+base64.b64encode(digest).decode(),
        'mime_type':'text/html' if path.endswith('.html') else 'text/javascript',
        'execution_class':'EXECUTABLE_DOCUMENT' if path.endswith('.html') else 'EXECUTABLE_SCRIPT',
        'enforcement':'SERVICE_WORKER_PRE_RESPONSE_SHA256',
    })
    return result

def main():
    inner=INNER.read_text('utf-8')
    if NEW_BLOCK not in inner:
        assert inner.count(OLD_BLOCK)==1
        inner=inner.replace(OLD_BLOCK,NEW_BLOCK)
        INNER.write_text(inner,'utf-8')

    manifest=json.loads(MANIFEST.read_text('utf-8'))
    index={row['path']:row for row in manifest['records']}
    index[RUNTIME]=record(RUNTIME,index.get(RUNTIME))
    index[INNER_REL]=record(INNER_REL,index.get(INNER_REL))
    manifest['records']=[index[path] for path in sorted(index)]
    manifest['counts']['runtime_records']=len(manifest['records'])
    manifest['counts']['executable_records']=sum(
        1 for row in manifest['records'] if row['execution_class']!='STYLE_SOURCE'
    )
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
    manifest['runtime_source_set_sha256']=sha(
        json.dumps(identity,sort_keys=True,separators=(',',':')).encode()
    )
    manifest_bytes=(json.dumps(manifest,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode()
    MANIFEST.write_bytes(manifest_bytes)

    manifest_sha=sha(manifest_bytes)
    seal=json.loads(SEAL.read_text('utf-8'))
    seal.update(
        manifest_bytes=len(manifest_bytes),
        manifest_sha256=manifest_sha,
        runtime_source_set_sha256=manifest['runtime_source_set_sha256'],
        sealed_branch='agent/pass5-unit3-passive-lifecycle-integration-v1',
        pass5_context='Pass 5 Unit 3 passively loads the proven lifecycle contract and explicit-owner-event runtime behind the preserved legacy atlas boundary; no automatic transitions or storage migration are introduced.',
    )
    SEAL.write_text(json.dumps(seal,indent=2,sort_keys=True)+'\n','utf-8')

    bootstrap=BOOTSTRAP.read_text('utf-8')
    updated,count=re.subn(
        r"const MANIFEST_SHA256='[0-9a-f]{64}';",
        f"const MANIFEST_SHA256='{manifest_sha}';",
        bootstrap,
        count=1,
    )
    assert count==1
    BOOTSTRAP.write_text(updated,'utf-8')
    print('PASS: Pass 5 Unit 3 runtime identities regenerated')

if __name__=='__main__':
    main()
