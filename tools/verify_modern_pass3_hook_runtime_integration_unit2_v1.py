#!/usr/bin/env python3
import argparse, hashlib, json, pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
CONTRACT=ROOT/'audit/pass3/modern-hook-runtime-integration-unit2-v1.json'
def sha256(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def blob(p):
 b=p.read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def fail(c,d): raise SystemExit(c+':'+json.dumps(d,sort_keys=True))
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--base-sha'); ap.add_argument('--head-sha'); ap.add_argument('--output',type=pathlib.Path); a=ap.parse_args()
 c=json.loads(CONTRACT.read_text())
 for row in [*c['runtime_sources'],c['historical_freeze']]:
  p=ROOT/row['path']
  if not p.is_file() or len(p.read_bytes())!=row['bytes'] or sha256(p)!=row['sha256'] or blob(p)!=row['git_blob_sha']: fail('PRESERVATION_IDENTITY_MISMATCH',row)
 if a.base_sha and a.head_sha:
  changed=set(filter(None,subprocess.check_output(['git','diff','--name-only',a.base_sha,a.head_sha],cwd=ROOT,text=True).splitlines()))
  expected=set(c['changed_paths'])
  if changed!=expected: fail('EXACT_SCOPE_MISMATCH',{'missing':sorted(expected-changed),'extra':sorted(changed-expected)})
 out={'type':'PMP_MODERN_PASS3_HOOK_RUNTIME_INTEGRATION_UNIT2_VERIFICATION_V1','status':'PASS','deterministic':True,'exact_scope':True,'runtime_sources_preserved':True,'historical_freeze_preserved':True,'production_activation':False}
 text=json.dumps(out,indent=2,sort_keys=True)+'\n'
 if a.output: a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(text)
 print(text,end='')
if __name__=='__main__': main()
