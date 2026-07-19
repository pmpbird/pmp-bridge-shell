#!/usr/bin/env python3
import argparse
import pathlib
import subprocess
import sys

p = argparse.ArgumentParser()
p.add_argument('--bundle-root', required=True)
p.add_argument('--old-source-commit', required=True)
p.add_argument('--new-source-commit', required=True)
p.add_argument('--evidence-dir', required=True)
a = p.parse_args()

here = pathlib.Path(__file__).resolve().parent
original = here / 'patch_runtime_nodepath_and_source_bindings_receipt082.py'
messageport = here / 'patch_a002_native_messageport_setter_rehearsal088.py'
bundle_root = pathlib.Path(a.bundle_root)
target = bundle_root / 'run_full_isolated_proof_002.py'

subprocess.run([
    sys.executable,
    str(original),
    '--bundle-root', str(bundle_root),
    '--old-source-commit', a.old_source_commit,
    '--new-source-commit', a.new_source_commit,
    '--evidence-dir', a.evidence_dir,
], check=True)

if not target.is_file():
    raise SystemExit(f'REHEARSAL090_RUNNER_NOT_FOUND:{target}')

subprocess.run([
    sys.executable,
    str(messageport),
    '--path', str(target),
    '--evidence-dir', a.evidence_dir,
], check=True)

print('REHEARSAL090_RUNTIME_AND_MESSAGEPORT_PATCHES_APPLIED')
