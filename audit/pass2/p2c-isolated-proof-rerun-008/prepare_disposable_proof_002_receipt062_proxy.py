#!/usr/bin/env python3
import json, os, pathlib, runpy, sys

if len(sys.argv) < 3:
    raise SystemExit('RECEIPT062_PROXY_ARGUMENTS_INVALID')
script = pathlib.Path(sys.argv[1])
target = sys.argv[2]
original_args = sys.argv[3:]
if len(target) != 40 or any(c not in '0123456789abcdef' for c in target):
    raise SystemExit('RECEIPT062_SOURCE_COMMIT_FORMAT_INVALID')

original_loads = json.loads
original_load = json.load
repairs = []
observed = []

def rewrite(node, location):
    count = 0
    if isinstance(node, dict):
        for key, value in list(node.items()):
            if key == 'source_repository_commit':
                observed.append({'location': location, 'value': value})
                if value != target:
                    node[key] = target
                    repairs.append({'location': location, 'old': value, 'new': target})
                    count += 1
            else:
                count += rewrite(value, location)
    elif isinstance(node, list):
        for value in node:
            count += rewrite(value, location)
    return count

def patched_loads(s, *args, **kwargs):
    data = original_loads(s, *args, **kwargs)
    rewrite(data, 'json.loads')
    return data

def patched_load(fp, *args, **kwargs):
    data = original_load(fp, *args, **kwargs)
    rewrite(data, getattr(fp, 'name', 'json.load'))
    return data

json.loads = patched_loads
json.load = patched_load
sys.argv = [str(script)] + original_args
try:
    runpy.run_path(str(script), run_name='__main__')
finally:
    evidence_dir = pathlib.Path(os.environ['EVIDENCE_DIR'])
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / 'prepare-receipt-source-binding-proxy-062.json').write_text(
        json.dumps({
            'status': 'PASS' if repairs else 'NO_REPAIR_OBSERVED',
            'target_source_repository_commit': target,
            'observed': observed,
            'repairs': repairs,
            'repair_count': len(repairs),
        }, indent=2, sort_keys=True) + '\n'
    )

if not repairs:
    raise SystemExit('RECEIPT062_PREPARE_RECEIPT_SOURCE_BINDING_NOT_OBSERVED')
print(f'RECEIPT062_PREPARE_RECEIPT_SOURCE_BINDINGS_REPAIRED:{len(repairs)}:{target}')
