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
prepare_getter = here / 'patch_event_handler_getter_authority_rehearsal097.py'
registration_scope = here / 'patch_explicit_document_registration_authority_rehearsal099.py'
original = here / 'patch_runtime_nodepath_and_source_bindings_receipt082.py'
messageport = here / 'patch_a002_native_messageport_setter_rehearsal088.py'
diagnostics = here / 'patch_runtime_source_and_landing_diagnostics_rehearsal096.py'
a003_compat = here / 'patch_a003_harness_patch_compatibility_rehearsal098.py'
bundle_root = pathlib.Path(a.bundle_root)
prepare_target = bundle_root / 'prepare_disposable_proof_002.py'
target = bundle_root / 'run_full_isolated_proof_002.py'

if not prepare_target.is_file():
    raise SystemExit(f'REHEARSAL097_PREPARE_NOT_FOUND:{prepare_target}')
subprocess.run([
    sys.executable,
    str(prepare_getter),
    '--path', str(prepare_target),
    '--evidence-dir', a.evidence_dir,
], check=True)

subprocess.run([
    sys.executable,
    str(registration_scope),
    '--bundle-root', str(bundle_root),
    '--prepare-path', str(prepare_target),
    '--evidence-dir', a.evidence_dir,
], check=True)

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

subprocess.run([
    sys.executable,
    str(diagnostics),
    '--path', str(target),
    '--evidence-dir', a.evidence_dir,
], check=True)

subprocess.run([
    sys.executable,
    str(a003_compat),
    '--path', str(target),
    '--evidence-dir', a.evidence_dir,
], check=True)

print('REHEARSAL099_EXPLICIT_DOCUMENT_REGISTRATION_AND_PRIOR_REPAIRS_APPLIED')
