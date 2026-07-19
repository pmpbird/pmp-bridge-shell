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
original_bytes = path.read_bytes()
text = original_bytes.decode('utf-8')
original_sha256 = hashlib.sha256(original_bytes).hexdigest()
(out / 'run-full-isolated-proof-before-messageport-repair-092.py').write_bytes(original_bytes)

write_anchor = ' a002.write_text(s)'
injection = r''' # PMP_REHEARSAL092_A002_NATIVE_MESSAGEPORT_REPAIR_BEGIN
 a002_status_candidates=(
  "    channel.port1.onmessage = event => { resolve(event.data); };",
  "    channel.port1.onmessage = event => { clearTimeout(timer); resolve(event.data); };",
 )
 a002_status_matches=[candidate for candidate in a002_status_candidates if s.count(candidate)==1]
 if len(a002_status_matches)!=1:
  raise SystemExit(f'A002_NATIVE_MESSAGEPORT_STATUS_POINT_INVALID:{[(candidate,s.count(candidate)) for candidate in a002_status_candidates]}')
 a002_status_old=a002_status_matches[0]
 a002_status_new="""    const nativeSetter = globalThis.__PMP_A002_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER;
    if (typeof nativeSetter !== 'function') throw new Error('A002_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER_MISSING');
    nativeSetter.call(channel.port1, event => { resolve(event.data); });"""
 s=s.replace(a002_status_old,a002_status_new,1)
 a002_page_candidates=(
  ("    const page = await context.newPage();\n    page.setDefaultTimeout(30000);", "    const page = await context.newPage();\n    await page.addInitScript(() => {\n      const descriptor = Object.getOwnPropertyDescriptor(MessagePort.prototype, 'onmessage');\n      globalThis.__PMP_A002_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER = descriptor && descriptor.set;\n    });\n    page.setDefaultTimeout(30000);"),
  ("  const page = await context.newPage();\n  page.setDefaultTimeout(30000);", "  const page = await context.newPage();\n  await page.addInitScript(() => {\n    const descriptor = Object.getOwnPropertyDescriptor(MessagePort.prototype, 'onmessage');\n    globalThis.__PMP_A002_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER = descriptor && descriptor.set;\n  });\n  page.setDefaultTimeout(30000);"),
 )
 a002_page_matches=[pair for pair in a002_page_candidates if s.count(pair[0])==1]
 if len(a002_page_matches)!=1:
  raise SystemExit(f'A002_NATIVE_MESSAGEPORT_PAGE_POINT_INVALID:{[(pair[0],s.count(pair[0])) for pair in a002_page_candidates]}')
 s=s.replace(a002_page_matches[0][0],a002_page_matches[0][1],1)
 if s.count('__PMP_A002_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER')!=2:
  raise SystemExit(f'A002_NATIVE_MESSAGEPORT_TOKEN_COUNT_INVALID:{s.count("__PMP_A002_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER")}')
 if s.count('nativeSetter.call(channel.port1, event => { resolve(event.data); });')!=1:
  raise SystemExit(f'A002_NATIVE_MESSAGEPORT_CALL_COUNT_INVALID:{s.count("nativeSetter.call(channel.port1, event => { resolve(event.data); });")}')
 # PMP_REHEARSAL092_A002_NATIVE_MESSAGEPORT_REPAIR_END'''

anchor_count = text.count(write_anchor)
if anchor_count != 1:
    raise SystemExit(f'REHEARSAL092_A002_WRITE_ANCHOR_INVALID:{anchor_count}')
patched = text.replace(write_anchor, injection + '\n' + write_anchor, 1)
compile(patched, str(path), 'exec')
marker_count = patched.count('PMP_REHEARSAL092_A002_NATIVE_MESSAGEPORT_REPAIR_BEGIN')
if marker_count != 1:
    raise SystemExit(f'REHEARSAL092_PATCHED_RUNNER_MARKER_INVALID:{marker_count}')
path.write_text(patched)
patched_bytes = path.read_bytes()
patched_sha256 = hashlib.sha256(patched_bytes).hexdigest()
(out / 'run-full-isolated-proof-after-messageport-repair-092.py').write_bytes(patched_bytes)
verification = {
    'type': 'PMP_P2C_A002_NATIVE_MESSAGEPORT_SETTER_REPAIR_REHEARSAL_092',
    'status': 'PASS',
    'target': str(path),
    'original_sha256': original_sha256,
    'patched_sha256': patched_sha256,
    'runner_write_anchor_count': anchor_count,
    'runner_injection_marker_count': marker_count,
    'test_only': True,
    'production_actor_policy_changed': False,
    'unknown_actor_policy_weakened': False,
    'native_setter_captured_before_application_scripts': True,
}
(out / 'a002-native-messageport-setter-repair-rehearsal-092.json').write_text(json.dumps(verification, indent=2, sort_keys=True) + '\n')
print(json.dumps(verification, sort_keys=True))
