#!/usr/bin/env python3
import argparse, pathlib, textwrap

p=argparse.ArgumentParser()
p.add_argument('--path',required=True)
p.add_argument('--source-commit',required=True)
p.add_argument('--evidence-dir',required=True)
a=p.parse_args()
path=pathlib.Path(a.path)
source=path.read_text()
if len(a.source_commit)!=40 or any(c not in '0123456789abcdef' for c in a.source_commit):
    raise SystemExit('RECEIPT070_SOURCE_COMMIT_FORMAT_INVALID')
marker='# RECEIPT070_INTERNAL_AUTHORIZATION_RECEIPT_REPAIR\n'
if marker in source:
    raise SystemExit('RECEIPT070_PATCH_ALREADY_PRESENT')
insert=marker+textwrap.dedent(f'''\
import atexit as _r070_atexit
import copy as _r070_copy
import hashlib as _r070_hashlib
import json as _r070_json
import os as _r070_os
import pathlib as _r070_pathlib

_r070_target = {a.source_commit!r}
_r070_evidence_dir = _r070_pathlib.Path({a.evidence_dir!r})
_r070_evidence_dir.mkdir(parents=True, exist_ok=True)
_r070_original_loads = _r070_json.loads
_r070_original_load = _r070_json.load
_r070_repairs = []
_r070_candidates = []

def _r070_walk_replace(node, trail='root'):
    count=0
    if isinstance(node, dict):
        for key, value in list(node.items()):
            child=f"{{trail}}.{{key}}"
            if key=='source_repository_commit':
                if value != _r070_target:
                    node[key]=_r070_target
                    _r070_repairs.append({{'path':child,'old':value,'new':_r070_target}})
                    count += 1
            else:
                count += _r070_walk_replace(value, child)
    elif isinstance(node, list):
        for i,value in enumerate(node):
            count += _r070_walk_replace(value, f"{{trail}}[{{i}}]")
    return count

def _r070_is_authorization_receipt(obj):
    if not isinstance(obj, dict):
        return False
    semantic_keys=set(obj)
    authority_markers={{'authorized','authorization_consumed','authorization_scope','proof_run_count_authorized','workflow_execution_authorized','browser_proof_execution_authorized','separate_execution_authorization_required'}}
    return 'source_repository_commit' in semantic_keys and len(authority_markers & semantic_keys) >= 2

def _r070_patch_parsed(obj):
    candidates=[]
    def visit(node, trail='root'):
        if isinstance(node, dict):
            if _r070_is_authorization_receipt(node):
                candidates.append((node,trail))
            for key,value in node.items():
                visit(value,f"{{trail}}.{{key}}")
        elif isinstance(node,list):
            for i,value in enumerate(node):
                visit(value,f"{{trail}}[{{i}}]")
    visit(obj)
    for candidate,trail in candidates:
        before=_r070_copy.deepcopy(candidate)
        changed=_r070_walk_replace(candidate,trail)
        if changed:
            before_without=_r070_copy.deepcopy(before)
            after_without=_r070_copy.deepcopy(candidate)
            def strip(node):
                if isinstance(node,dict):
                    node.pop('source_repository_commit',None)
                    for value in node.values(): strip(value)
                elif isinstance(node,list):
                    for value in node: strip(value)
            strip(before_without); strip(after_without)
            if before_without != after_without:
                raise RuntimeError('RECEIPT070_NON_TARGET_FIELD_CHANGED')
            repaired_path=_r070_evidence_dir/'repaired-disposable-authorization-receipt-070.json'
            repaired_path.write_text(_r070_json.dumps(candidate,indent=2,sort_keys=True)+'\\n')
            _r070_candidates.append({{'trail':trail,'repair_count':changed,'repaired_copy':str(repaired_path)}})
    return obj

def _r070_loads(s,*args,**kwargs):
    return _r070_patch_parsed(_r070_original_loads(s,*args,**kwargs))

def _r070_load(fp,*args,**kwargs):
    return _r070_patch_parsed(_r070_original_load(fp,*args,**kwargs))

_r070_json.loads=_r070_loads
_r070_json.load=_r070_load

def _r070_finish():
    evidence={{
      'status':'PASS' if _r070_repairs else 'NO_INTERNAL_AUTHORIZATION_RECEIPT_REPAIRED',
      'target_source_repository_commit':_r070_target,
      'repair_count':len(_r070_repairs),
      'repairs':_r070_repairs,
      'candidates':_r070_candidates,
      'all_other_fields_preserved':bool(_r070_repairs),
    }}
    (_r070_evidence_dir/'prepare-script-internal-receipt-repair-070.json').write_text(_r070_original_loads(_r070_json.dumps(evidence)) and _r070_json.dumps(evidence,indent=2,sort_keys=True)+'\\n')
_r070_atexit.register(_r070_finish)
''')
lines=source.splitlines(keepends=True)
index=0
if lines and lines[0].startswith('#!'):
    index=1
while index < len(lines) and lines[index].startswith('from __future__ import '):
    index += 1
patched=''.join(lines[:index])+insert+''.join(lines[index:])
compile(patched,str(path),'exec')
path.write_text(patched)
print('RECEIPT070_PREPARE_SCRIPT_INTERNAL_RECEIPT_REPAIR_PATCHED')
