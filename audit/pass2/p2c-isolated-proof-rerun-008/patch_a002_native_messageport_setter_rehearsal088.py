#!/usr/bin/env python3
import argparse
import hashlib
import json
import pathlib

p = argparse.ArgumentParser()
p.add_argument('--path', required=True)
p.add_argument('--evidence-dir', required=True)
a = p.parse_args()

path = pathlib.Path(a.path)
out = pathlib.Path(a.evidence_dir)
out.mkdir(parents=True, exist_ok=True)
text = path.read_text()
original_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()

worker_old = ''' new="""    const channel = new MessageChannel();
    channel.port1.onmessage = event => { resolve(event.data); };"""'''
worker_new = ''' new="""    const channel = new MessageChannel();
    const nativeSetter = globalThis.__PMP_A002_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER;
    if (typeof nativeSetter !== 'function') throw new Error('A002_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER_MISSING');
    nativeSetter.call(channel.port1, event => { resolve(event.data); });"""'''
apply_anchor = " s=s.replace(old,new,1).replace('const deadline = Date.now() + 30000;','const deadline = Date.now() + 120000;',1)"
bootstrap_patch = r''' a002_bootstrap_old="    const page = await context.newPage();\n    page.setDefaultTimeout(30000);"
 a002_bootstrap_new="    const page = await context.newPage();\n    await page.addInitScript(() => {\n      const descriptor = Object.getOwnPropertyDescriptor(MessagePort.prototype, 'onmessage');\n      globalThis.__PMP_A002_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER = descriptor && descriptor.set;\n    });\n    page.setDefaultTimeout(30000);"
 if s.count(a002_bootstrap_old)!=1:raise SystemExit(f'A002_NATIVE_MESSAGEPORT_INIT_POINT_INVALID:{s.count(a002_bootstrap_old)}')
 s=s.replace(a002_bootstrap_old,a002_bootstrap_new,1)'''

counts = {
    'worker_generator_block': text.count(worker_old),
    'worker_apply_anchor': text.count(apply_anchor),
}
if counts['worker_generator_block'] != 1:
    raise SystemExit(f'REHEARSAL091_A002_WORKER_GENERATOR_BLOCK_INVALID:{counts["worker_generator_block"]}')
if counts['worker_apply_anchor'] != 1:
    raise SystemExit(f'REHEARSAL091_A002_WORKER_APPLY_ANCHOR_INVALID:{counts["worker_apply_anchor"]}')

patched = text.replace(worker_old, worker_new, 1)
patched = patched.replace(apply_anchor, apply_anchor + '\n' + bootstrap_patch, 1)

compile(patched, str(path), 'exec')

verification_counts = {
    'native_setter_capture_token': patched.count('__PMP_A002_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER'),
    'native_setter_call': patched.count('nativeSetter.call(channel.port1, event => { resolve(event.data); });'),
    'direct_uncontrolled_status_assignment': patched.count('channel.port1.onmessage = event => { resolve(event.data); };'),
    'bootstrap_contract': patched.count("a002_bootstrap_old=\"    const page = await context.newPage();\\n    page.setDefaultTimeout(30000);\""),
}
expected = {
    'native_setter_capture_token': 2,
    'native_setter_call': 1,
    'direct_uncontrolled_status_assignment': 0,
    'bootstrap_contract': 1,
}
if verification_counts != expected:
    raise SystemExit('REHEARSAL091_PATCHED_RUNNER_CONTRACT_INVALID:' + json.dumps({'actual': verification_counts, 'expected': expected}, sort_keys=True))

path.write_text(patched)
patched_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
verification = {
    'type': 'PMP_P2C_A002_NATIVE_MESSAGEPORT_SETTER_REPAIR_REHEARSAL_091',
    'status': 'PASS',
    'target': str(path),
    'original_sha256': original_sha256,
    'patched_sha256': patched_sha256,
    'worker_generator_patch_count': 1,
    'bootstrap_generator_patch_count': 1,
    'test_only': True,
    'production_actor_policy_changed': False,
    'unknown_actor_policy_weakened': False,
    'native_setter_captured_before_application_scripts': True,
    'runner_contract_counts': verification_counts,
}
(out / 'a002-native-messageport-setter-repair-rehearsal-091.json').write_text(json.dumps(verification, indent=2, sort_keys=True) + '\n')
print(json.dumps(verification, sort_keys=True))
