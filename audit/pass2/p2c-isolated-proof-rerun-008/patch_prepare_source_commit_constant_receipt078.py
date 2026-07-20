#!/usr/bin/env python3
import argparse, hashlib, json, pathlib

p=argparse.ArgumentParser()
p.add_argument('--path',required=True)
p.add_argument('--source-commit',required=True)
p.add_argument('--evidence-dir',required=True)
a=p.parse_args()
path=pathlib.Path(a.path)
text=path.read_text()
old="SOURCE_COMMIT='c618596f2b5c99ca7f355153a5bd31268170df80'"
new=f"SOURCE_COMMIT='{a.source_commit}'"
count=text.count(old)
if count!=1:
    raise SystemExit(f'RECEIPT078_SOURCE_COMMIT_LITERAL_COUNT_INVALID:{count}')
patched=text.replace(old,new,1)
compile(patched,str(path),'exec')
path.write_text(patched)
if path.read_text().count(new)!=1 or old in path.read_text():
    raise SystemExit('RECEIPT078_SOURCE_COMMIT_REPLACEMENT_VERIFY_FAILED')
evidence={
  'type':'PMP_P2C_PREPARE_SOURCE_COMMIT_CONSTANT_REPAIR_078',
  'status':'PASS',
  'path':str(path),
  'old_source_repository_commit':'c618596f2b5c99ca7f355153a5bd31268170df80',
  'new_source_repository_commit':a.source_commit,
  'replacement_count':1,
  'all_other_source_bytes_preserved':True,
  'patched_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
}
out=pathlib.Path(a.evidence_dir)
out.mkdir(parents=True,exist_ok=True)
(out/'prepare-source-commit-constant-repair-078.json').write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
print('RECEIPT078_PREPARE_SOURCE_COMMIT_CONSTANT_REPAIRED')
