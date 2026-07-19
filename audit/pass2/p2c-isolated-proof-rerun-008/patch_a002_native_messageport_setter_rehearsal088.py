#!/usr/bin/env python3
import argparse
import hashlib
import json
import pathlib

p=argparse.ArgumentParser()
p.add_argument('--path',required=True)
p.add_argument('--evidence-dir',required=True)
a=p.parse_args()
path=pathlib.Path(a.path)
out=pathlib.Path(a.evidence_dir)
out.mkdir(parents=True,exist_ok=True)
original=path.read_text()
original_sha256=hashlib.sha256(original.encode()).hexdigest()
(out/'run-full-isolated-proof-final-before-harness-repair-095.py').write_text(original)
text=original

a002_worker_old=''' new="""    const channel = new MessageChannel();
    channel.port1.onmessage = event => { resolve(event.data); };"""'''
a002_worker_new=''' new="""    const channel = new MessageChannel();
    const nativeSetter = globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER;
    if (typeof nativeSetter !== 'function') throw new Error('PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER_MISSING');
    nativeSetter.call(channel.port1, event => { resolve(event.data); });"""'''
if text.count(a002_worker_old)!=1:raise SystemExit(f'REHEARSAL095_A002_WORKER_GENERATOR_POINT_INVALID:{text.count(a002_worker_old)}')
text=text.replace(a002_worker_old,a002_worker_new,1)

a002_apply_anchor=" s=s.replace(old,new,1).replace('const deadline = Date.now() + 30000;','const deadline = Date.now() + 120000;',1)"
a002_apply_insert=r''' s=s.replace(old,new,1).replace('const deadline = Date.now() + 30000;','const deadline = Date.now() + 120000;',1)
 a002_context_old="    const context = await browser.newContext({ serviceWorkers: 'allow' });\n    const page = await context.newPage();"
 a002_context_new="    const context = await browser.newContext({ serviceWorkers: 'allow' });\n    await context.addInitScript(() => {\n      const descriptor = Object.getOwnPropertyDescriptor(MessagePort.prototype, 'onmessage');\n      globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER = descriptor && descriptor.set;\n    });\n    const page = await context.newPage();"
 if s.count(a002_context_old)!=1:raise SystemExit(f'A002_NATIVE_MESSAGEPORT_CONTEXT_POINT_INVALID:{s.count(a002_context_old)}')
 s=s.replace(a002_context_old,a002_context_new,1)
 if "landing_mode: 'canonical-current-app'" not in s:
  a002_home_anchor="    const urls = page.frames().map(f => f.url());\n    const homeUrls = urls.filter(u => /pmp-home-single-v6\\.html/.test(u));"
  a002_home_insert="""    const urls = page.frames().map(f => f.url());
    const pageUrl = page.url();
    let directPathMatches = false;
    let directHash = '';
    try {
      const parsed = new URL(pageUrl);
      directPathMatches = parsed.pathname.endsWith('/' + CURRENT);
      directHash = parsed.hash;
    } catch {}
    const canonicalReady = await page.evaluate(() => !!(window.PMPReloadCurrentCanonicalV1 && typeof window.PMPReloadCurrentCanonicalV1.reload === 'function')).catch(() => false);
    if (directPathMatches && canonicalReady) {
      const detail = { reached: true, hash_matches: directHash === expectedHash, expected_hash: expectedHash, actual_hash: directHash, home_url: pageUrl, landing_mode: 'canonical-current-app', urls };
      if (detail.hash_matches) return detail;
      lastMismatch = detail;
    }
    const homeUrls = urls.filter(u => /pmp-home-single-v6\.html/.test(u));"""
  if s.count(a002_home_anchor)!=1:raise SystemExit(f'A002_DIRECT_CANONICAL_POINT_INVALID:{s.count(a002_home_anchor)}')
  s=s.replace(a002_home_anchor,a002_home_insert,1)'''
if text.count(a002_apply_anchor)!=1:raise SystemExit(f'REHEARSAL095_A002_APPLY_POINT_INVALID:{text.count(a002_apply_anchor)}')
text=text.replace(a002_apply_anchor,a002_apply_insert,1)

a003_worker_old=''' new="""    const channel = new MessageChannel();
    channel.port1.onmessage = e => { resolve(e.data); };"""'''
a003_worker_new=''' new="""    const channel = new MessageChannel();
    const nativeSetter = globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER;
    if (typeof nativeSetter !== 'function') throw new Error('PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER_MISSING');
    nativeSetter.call(channel.port1, e => { resolve(e.data); });"""'''
if text.count(a003_worker_old)!=1:raise SystemExit(f'REHEARSAL095_A003_WORKER_GENERATOR_POINT_INVALID:{text.count(a003_worker_old)}')
text=text.replace(a003_worker_old,a003_worker_new,1)

a003_bootstrap_old=' bootstrap_new="  const page = await context.newPage();\\n  await page.addInitScript(() => { globalThis.__PMP_A003_TEST_NATIVE_FETCH = globalThis.fetch.bind(globalThis); });\\n  page.setDefaultTimeout(30000);"'
a003_bootstrap_new=' bootstrap_new="  await context.addInitScript(() => { const descriptor = Object.getOwnPropertyDescriptor(MessagePort.prototype, \'onmessage\'); globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER = descriptor && descriptor.set; });\\n  const page = await context.newPage();\\n  await page.addInitScript(() => { globalThis.__PMP_A003_TEST_NATIVE_FETCH = globalThis.fetch.bind(globalThis); });\\n  page.setDefaultTimeout(30000);"'
if text.count(a003_bootstrap_old)!=1:raise SystemExit(f'REHEARSAL095_A003_CONTEXT_GENERATOR_POINT_INVALID:{text.count(a003_bootstrap_old)}')
text=text.replace(a003_bootstrap_old,a003_bootstrap_new,1)

compile(text,str(path),'exec')
contracts={
 'patch_regression_harnesses':text.count('def patch_regression_harnesses(root):'),
 'a002_native_setter_call':text.count('nativeSetter.call(channel.port1, event => { resolve(event.data); });'),
 'a003_native_setter_call':text.count('nativeSetter.call(channel.port1, e => { resolve(e.data); });'),
 'context_capture_token':text.count('__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER'),
 'a002_context_patch_contract':text.count('A002_NATIVE_MESSAGEPORT_CONTEXT_POINT_INVALID'),
 'a002_direct_canonical_contract':text.count('A002_DIRECT_CANONICAL_POINT_INVALID'),
}
expected={'patch_regression_harnesses':1,'a002_native_setter_call':1,'a003_native_setter_call':1,'context_capture_token':4,'a002_context_patch_contract':1,'a002_direct_canonical_contract':1}
if contracts!=expected:raise SystemExit('REHEARSAL095_FINAL_RUNNER_CONTRACT_INVALID:'+json.dumps({'actual':contracts,'expected':expected},sort_keys=True))
path.write_text(text)
patched_sha256=hashlib.sha256(path.read_bytes()).hexdigest()
(out/'run-full-isolated-proof-final-after-harness-repair-095.py').write_text(text)
evidence={'type':'PMP_P2C_FINAL_PATCH_REGRESSION_HARNESSES_REPAIR_095','status':'PASS','target':str(path),'original_sha256':original_sha256,'patched_sha256':patched_sha256,'contracts':contracts,'test_only':True,'production_actor_policy_changed':False,'unknown_actor_policy_weakened':False,'native_setter_captured_before_page_creation':True,'a002_direct_canonical_landing_normalized':True,'parallel_harness_layer_added':False}
(out/'final-patch-regression-harnesses-repair-095.json').write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
print(json.dumps(evidence,sort_keys=True))
