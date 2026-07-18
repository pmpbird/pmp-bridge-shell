#!/usr/bin/env python3
import argparse, hashlib, json, pathlib

p=argparse.ArgumentParser()
p.add_argument('--path',required=True)
p.add_argument('--source-commit',required=True)
p.add_argument('--evidence-dir',required=True)
a=p.parse_args()
path=pathlib.Path(a.path)
text=path.read_text()
old='c618596f2b5c99ca7f355153a5bd31268170df80'
new=a.source_commit
count=text.count(old)
if count!=1:
    raise SystemExit(f'RECEIPT082_RUN_FULL_STALE_SOURCE_COMMIT_COUNT_INVALID:{count}')
patched=text.replace(old,new,1)
compile(patched,str(path),'exec')
path.write_text(patched)
verified=path.read_text()
if old in verified or verified.count(new)<1:
    raise SystemExit('RECEIPT082_RUN_FULL_SOURCE_COMMIT_VERIFY_FAILED')
evidence={
  'type':'PMP_P2C_RUN_FULL_SOURCE_COMMIT_REPAIR_082',
  'status':'PASS',
  'path':str(path),
  'old_source_commit':old,
  'new_source_commit':new,
  'replacement_count':1,
  'all_other_source_bytes_preserved':True,
  'patched_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
}
out=pathlib.Path(a.evidence_dir)
out.mkdir(parents=True,exist_ok=True)
(out/'run-full-source-commit-repair-082.json').write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
print('RECEIPT082_RUN_FULL_SOURCE_COMMIT_REPAIRED')
