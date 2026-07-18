#!/usr/bin/env python3
import argparse, hashlib, json, pathlib

p=argparse.ArgumentParser()
p.add_argument('--bundle-root',required=True)
p.add_argument('--old-source-commit',required=True)
p.add_argument('--new-source-commit',required=True)
p.add_argument('--evidence-dir',required=True)
a=p.parse_args()
root=pathlib.Path(a.bundle_root)
out=pathlib.Path(a.evidence_dir)
out.mkdir(parents=True,exist_ok=True)
allowed_suffixes={'.py','.js','.cjs','.mjs','.json','.sh'}
changed=[]
replacement_count=0
binding_tokens=('SOURCE_COMMIT','source_commit','source_repository_commit')
for path in sorted(p for p in root.rglob('*') if p.is_file() and p.suffix in allowed_suffixes):
    text=path.read_text(errors='strict')
    lines=text.splitlines(keepends=True)
    new_lines=[]
    local=0
    for line in lines:
        if a.old_source_commit in line and any(token in line for token in binding_tokens):
            count=line.count(a.old_source_commit)
            line=line.replace(a.old_source_commit,a.new_source_commit)
            local += count
        new_lines.append(line)
    if local:
        patched=''.join(new_lines)
        if path.suffix=='.py':
            compile(patched,str(path),'exec')
        path.write_text(patched)
        replacement_count += local
        changed.append({'path':str(path.relative_to(root)),'replacement_count':local,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
remaining=[]
for path in sorted(p for p in root.rglob('*') if p.is_file() and p.suffix in allowed_suffixes):
    for lineno,line in enumerate(path.read_text(errors='strict').splitlines(),1):
        if a.old_source_commit in line and any(token in line for token in binding_tokens):
            remaining.append({'path':str(path.relative_to(root)),'line':lineno,'text':line})
if replacement_count < 1:
    raise SystemExit('RECEIPT082_NO_STALE_SOURCE_BINDINGS_FOUND')
if remaining:
    raise SystemExit('RECEIPT082_STALE_SOURCE_BINDINGS_REMAIN:'+json.dumps(remaining,sort_keys=True))
evidence={
  'type':'PMP_P2C_RUNTIME_NODEPATH_AND_SOURCE_BINDING_REPAIR_082',
  'status':'PASS',
  'old_source_commit':a.old_source_commit,
  'new_source_commit':a.new_source_commit,
  'replacement_count':replacement_count,
  'changed_files':changed,
  'all_other_lines_preserved':True,
  'node_path_required':'$NODE_HOME/node_modules',
}
(out/'runtime-nodepath-and-source-binding-repair-082.json').write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
print(json.dumps(evidence,sort_keys=True))
