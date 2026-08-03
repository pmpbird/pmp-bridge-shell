#!/usr/bin/env python3
from __future__ import annotations
import base64, hashlib, json, re, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'pmp-runtime-integrity-manifest-v1.json'
SEAL=ROOT/'audit/a003-manifest-seal.json'
BOOT=ROOT/'pmp-app-current.html'
OUT=ROOT/'generated-pr250-reseal'
PATHS=('pmp-diagnostics-writer-trace-v1.js','pmp-diagnostic-coverage-passes-bcd-v1-1-1-0.js')

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def blob(b:bytes)->str:return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def rec(path:str,old:dict|None=None)->dict:
    b=(ROOT/path).read_bytes(); d=hashlib.sha256(b).digest(); r=dict(old or {})
    r.update({'path':path,'bytes':len(b),'git_blob_sha':blob(b),'sha256_hex':d.hex(),'sha256_base64':base64.b64encode(d).decode(),'sri':'sha256-'+base64.b64encode(d).decode(),'mime_type':'text/javascript','execution_class':'EXECUTABLE_SCRIPT','enforcement':'SERVICE_WORKER_PRE_RESPONSE_SHA256'})
    return r

def main():
    m=json.loads(MANIFEST.read_text())
    idx={r['path']:r for r in m['records']}
    for p in PATHS: idx[p]=rec(p,idx.get(p))
    m['records']=[idx[p] for p in sorted(idx)]
    m['counts']['runtime_records']=len(m['records'])
    m['counts']['executable_records']=sum(1 for r in m['records'] if r.get('execution_class')!='STYLE_SOURCE')
    identity={'records':[(r['path'],r['sha256_hex']) for r in m.get('records',[])],'historical_records':[(r['path'],r.get('repository_ref'),r['sha256_hex']) for r in m.get('historical_records',[])],'external_records':[(r['url'],r['sha256_hex']) for r in m.get('external_records',[])],'root_trust_anchors':m.get('root_trust_anchors',[]),'policy':{'algorithm':m.get('algorithm'),'unlisted_executable_policy':m.get('unlisted_executable_policy'),'network_policy':m.get('network_policy')}}
    m['runtime_source_set_sha256']=sha(json.dumps(identity,sort_keys=True,separators=(',',':')).encode())
    mb=(json.dumps(m,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode(); MANIFEST.write_bytes(mb); ms=sha(mb)
    s=json.loads(SEAL.read_text()); s.update(manifest_bytes=len(mb),manifest_sha256=ms,runtime_source_set_sha256=m['runtime_source_set_sha256'],sealed_branch='chatgpt/reseal-pr250-runtime',diagnostics_context='PR250 transactional cache-proof Passes B-D bootstrap and immutable 1.1.0 runtime source reseal; no owner/helper/route/storage authority change.')
    SEAL.write_text(json.dumps(s,indent=2,sort_keys=True)+'\n')
    text=BOOT.read_text()
    text,n1=re.subn(r"const target='[0-9a-f]{64}'",f"const target='{ms}'",text,count=1)
    text,n2=re.subn(r"const MANIFEST_SHA256='[0-9a-f]{64}';",f"const MANIFEST_SHA256='{ms}';",text,count=1)
    assert n1==1 and n2==1
    BOOT.write_text(text)
    OUT.mkdir(exist_ok=True)
    for p in (MANIFEST,SEAL,BOOT): shutil.copy2(p,OUT/p.name)
    (OUT/'summary.json').write_text(json.dumps({'status':'PASS','manifest_sha256':ms,'runtime_source_set_sha256':m['runtime_source_set_sha256'],'runtime_records':len(m['records']),'paths':list(PATHS)},indent=2)+'\n')
if __name__=='__main__':main()
