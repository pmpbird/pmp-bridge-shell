#!/usr/bin/env python3
import json, os, pathlib, shutil, subprocess, sys, tempfile

if len(sys.argv) < 3:
    raise SystemExit('RECEIPT066_PROXY_ARGUMENTS_INVALID')
script = pathlib.Path(sys.argv[1])
target = sys.argv[2]
original_args = sys.argv[3:]
if len(target) != 40 or any(c not in '0123456789abcdef' for c in target):
    raise SystemExit('RECEIPT066_SOURCE_COMMIT_FORMAT_INVALID')

repairs = []
observed = []
temp_root = pathlib.Path(tempfile.mkdtemp(prefix='p2c-receipt066-'))

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

def patched_file_argument(raw, index):
    prefix = ''
    candidate_text = raw
    if '=' in raw and raw.startswith('--'):
        prefix, candidate_text = raw.split('=', 1)
        prefix += '='
    candidate = pathlib.Path(candidate_text)
    if not candidate.is_file():
        return raw
    try:
        data = json.loads(candidate.read_text())
    except Exception:
        return raw
    count = rewrite(data, str(candidate))
    if count == 0:
        return raw
    copy_path = temp_root / f'{index:03d}-{candidate.name}'
    copy_path.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
    verify = json.loads(copy_path.read_text())
    mismatches = []
    def check(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == 'source_repository_commit' and value != target:
                    mismatches.append(value)
                else:
                    check(value)
        elif isinstance(node, list):
            for value in node:
                check(value)
    check(verify)
    if mismatches:
        raise SystemExit(f'RECEIPT066_REPAIRED_COPY_VERIFY_FAILED:{candidate}:{mismatches}')
    return prefix + str(copy_path)

patched_args = [patched_file_argument(arg, i) for i, arg in enumerate(original_args)]
evidence_dir = pathlib.Path(os.environ['EVIDENCE_DIR'])
evidence_dir.mkdir(parents=True, exist_ok=True)
evidence = {
    'status': 'PASS' if repairs else 'NO_EXACT_RECEIPT_ARGUMENT_REPAIRED',
    'target_source_repository_commit': target,
    'script': str(script),
    'original_args': original_args,
    'patched_args': patched_args,
    'observed': observed,
    'repairs': repairs,
    'repair_count': len(repairs),
}
(evidence_dir / 'prepare-receipt-exact-argument-repair-066.json').write_text(json.dumps(evidence, indent=2, sort_keys=True) + '\n')
if not repairs:
    raise SystemExit('RECEIPT066_EXACT_RECEIPT_FILE_ARGUMENT_NOT_FOUND')
print(f'RECEIPT066_EXACT_RECEIPT_ARGUMENT_BINDINGS_REPAIRED:{len(repairs)}:{target}')
completed = subprocess.run([sys.executable, str(script), *patched_args])
raise SystemExit(completed.returncode)
