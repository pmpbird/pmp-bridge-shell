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
registration_ledger = here / 'patch_event_property_registration_ledger_rehearsal100.py'
resolver_timer = here / 'patch_resolver_timer_schedule_capability_rehearsal102.py'
resolver_event_listener = here / 'patch_resolver_event_listener_capability_rehearsal103.py'
actor_global_eventtarget_receiver = here / 'patch_actor_global_eventtarget_receiver_rehearsal106.py'
original = here / 'patch_runtime_nodepath_and_source_bindings_receipt082.py'
messageport = here / 'patch_a002_native_messageport_setter_rehearsal088.py'
diagnostics = here / 'patch_runtime_source_and_landing_diagnostics_rehearsal096.py'
a003_compat = here / 'patch_a003_harness_patch_compatibility_rehearsal098.py'
a002_no_waitforfunction = here / 'patch_a002_no_waitforfunction_rehearsal104.py'
a002_navigation_stable_receipt = here / 'patch_a002_navigation_stable_receipt_rehearsal105.py'
a002_historic_navigation_isolation = here / 'patch_a002_historic_navigation_isolation_rehearsal107.py'
a002_historic_context_isolation = here / 'patch_a002_historic_context_isolation_rehearsal108.py'
ci_lane_closure = here / 'patch_ci_lane_closure_rehearsal109.py'
a002_historic_lane_lifecycle = here / 'patch_a002_historic_lane_lifecycle_rehearsal110.py'
ci_lane_lifecycle = here / 'patch_ci_lane_lifecycle_rehearsal111.py'
a002_single_page_historic_matrix = here / 'patch_a002_single_page_historic_matrix_rehearsal112.py'
a002_bounded_fresh_process_retry = here / 'patch_a002_bounded_fresh_process_retry_rehearsal113.py'
http_server_log_backpressure = here / 'patch_http_server_log_backpressure_rehearsal114.py'
a002_bounded_navigation_wait_retry = here / 'patch_a002_bounded_navigation_wait_retry_rehearsal115.py'
bundle_root = pathlib.Path(a.bundle_root)
prepare_target = bundle_root / 'prepare_disposable_proof_002.py'
policy_target = bundle_root / 'policy-template.json'
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
    str(registration_ledger),
    '--path', str(prepare_target),
    '--evidence-dir', a.evidence_dir,
], check=True)

subprocess.run([
    sys.executable,
    str(resolver_timer),
    '--policy-path', str(policy_target),
    '--evidence-dir', a.evidence_dir,
], check=True)

subprocess.run([
    sys.executable,
    str(resolver_event_listener),
    '--policy-path', str(policy_target),
    '--evidence-dir', a.evidence_dir,
], check=True)

subprocess.run([
    sys.executable,
    str(actor_global_eventtarget_receiver),
    '--bundle-root', str(bundle_root),
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

subprocess.run([
    sys.executable,
    str(a002_no_waitforfunction),
    '--path', str(target),
    '--evidence-dir', a.evidence_dir,
], check=True)

subprocess.run([
    sys.executable,
    str(a002_navigation_stable_receipt),
    '--path', str(target),
    '--evidence-dir', a.evidence_dir,
], check=True)

subprocess.run([
    sys.executable,
    str(a002_historic_navigation_isolation),
    '--path', str(target),
    '--evidence-dir', a.evidence_dir,
], check=True)

subprocess.run([
    sys.executable,
    str(a002_historic_context_isolation),
    '--path', str(target),
    '--evidence-dir', a.evidence_dir,
], check=True)

subprocess.run([
    sys.executable,
    str(ci_lane_closure),
    '--bundle-root', str(bundle_root),
    '--runner-path', str(target),
    '--evidence-dir', a.evidence_dir,
], check=True)

subprocess.run([
    sys.executable,
    str(a002_historic_lane_lifecycle),
    '--path', str(target),
    '--evidence-dir', a.evidence_dir,
], check=True)

subprocess.run([
    sys.executable,
    str(ci_lane_lifecycle),
    '--path', str(target),
    '--evidence-dir', a.evidence_dir,
], check=True)

subprocess.run([
    sys.executable,
    str(a002_single_page_historic_matrix),
    '--path', str(target),
    '--evidence-dir', a.evidence_dir,
], check=True)

subprocess.run([
    sys.executable,
    str(a002_bounded_fresh_process_retry),
    '--path', str(target),
    '--evidence-dir', a.evidence_dir,
], check=True)

subprocess.run([
    sys.executable,
    str(http_server_log_backpressure),
    '--path', str(target),
    '--evidence-dir', a.evidence_dir,
], check=True)

subprocess.run([
    sys.executable,
    str(a002_bounded_navigation_wait_retry),
    '--path', str(target),
    '--evidence-dir', a.evidence_dir,
], check=True)

print('REHEARSAL115_BOUNDED_NAVIGATION_WAIT_RETRY_AND_PRIOR_REPAIRS_APPLIED')
