#!/usr/bin/env python3
import base64,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
 '.github/workflows/pass4-unit2-passive-strip-integration-v1.yml',
 'audit/a003-manifest-seal.json',
 'audit/pass4/pass4-boot-status-strip-unit2-bounded-passive-integration-v1.json',
 'pmp-app-current.html',
 'pmp-boot-status-strip-owner-v1.js',
 'pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html',
 'pmp-runtime-integrity-manifest-v1.json',
 'tools/generate_pass4_unit2_integrity_updates_v1.py',
 'tools/test_pass4_unit2_passive_strip_integration_v1.js',
 'tools/verify_pass4_unit2_passive_strip_integration_v1.py',
}
def run(*a):return subprocess.check_output(a,cwd=ROOT,text=True).strip()
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def main():
 base=sys.argv[1] if len(sys.argv)>1 and sys.argv[1] else 'HEAD^'
 changed=set(filter(None,run('git','diff','--name-only',f'{base}...HEAD').splitlines()))
 assert changed==EXPECTED,(sorted(changed),sorted(EXPECTED))
 audit=json.loads((ROOT/'audit/pass4/pass4-boot-status-strip-unit2-bounded-passive-integration-v1.json').read_text())
 assert audit['status']=='IMPLEMENTED_PENDING_MERGE' and audit['base_main_commit']=='824dd590313e44cd3d038ecf94b8fc91462ff9e5'
 assert audit['preservation']['unit3_started'] is False and audit['preservation']['pass5_started'] is False
 manifest_bytes=(ROOT/'pmp-runtime-integrity-manifest-v1.json').read_bytes();manifest=json.loads(manifest_bytes)
 index={x['path']:x for x in manifest['records']}
 for rel in ['pmp-boot-status-strip-owner-v1.js','pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html']:
  b=(ROOT/rel).read_bytes();r=index[rel];d=hashlib.sha256(b).digest()
  assert r['bytes']==len(b) and r['git_blob_sha']==blob(b) and r['sha256_hex']==d.hex()
  assert r['sha256_base64']==base64.b64encode(d).decode() and r['sri']=='sha256-'+base64.b64encode(d).decode()
 seal=json.loads((ROOT/'audit/a003-manifest-seal.json').read_text())
 digest=sha(manifest_bytes)
 assert seal['manifest_sha256']==digest and seal['manifest_bytes']==len(manifest_bytes)
 bootstrap=(ROOT/'pmp-app-current.html').read_text()
 assert re.search(r"const MANIFEST_SHA256='"+digest+r"';",bootstrap)
 forbidden={'pmp-current-map-v12.json','pmp-current-route-resolver-v1.js','pmp-route-guardian-current-loader-v22.html','pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html','pmp-app-orchestrator-v1.js'}
 assert not(changed&forbidden)
 subprocess.check_call([sys.executable,str(ROOT/'tools/generate_pass4_unit2_integrity_updates_v1.py')],cwd=ROOT)
 assert not run('git','status','--porcelain'),'integrity generation is not idempotent'
 print('PASS: exact ten-file Unit 2 scope and required runtime integrity identities verified')
if __name__=='__main__':main()
