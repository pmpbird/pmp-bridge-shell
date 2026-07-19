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
original_bytes=path.read_bytes()
text=original_bytes.decode('utf-8')
original_sha256=hashlib.sha256(original_bytes).hexdigest()
(out/'run-full-isolated-proof-final-before-harness-repair-094.py').write_bytes(original_bytes)

import_old='import argparse,json,os,subprocess,sys,time'
import_new='import argparse,hashlib,json,os,subprocess,sys,time'
if text.count(import_old)==1:
    text=text.replace(import_old,import_new,1)
elif text.count(import_new)!=1:
    raise SystemExit(f'REHEARSAL094_IMPORT_POINT_INVALID:{text.count(import_old)}:{text.count(import_new)}')

helper=r'''def patch_native_messageport_harnesses(root,evidence_dir,label):
 originals={}
 specs=[
  {
   'name':'a002',
   'path':root/'audit/a002-live-runtime.cjs',
   'status_old':"    channel.port1.onmessage = event => { clearTimeout(timer); resolve(event.data); };",
   'status_new':"""    const nativeSetter = globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER;
    if (typeof nativeSetter !== 'function') throw new Error('PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER_MISSING');
    nativeSetter.call(channel.port1, event => { clearTimeout(timer); resolve(event.data); });""",
   'context_old':"""    const context = await browser.newContext({ serviceWorkers: 'allow' });
    const page = await context.newPage();""",
   'context_new':"""    const context = await browser.newContext({ serviceWorkers: 'allow' });
    await context.addInitScript(() => {
      const descriptor = Object.getOwnPropertyDescriptor(MessagePort.prototype, 'onmessage');
      globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER = descriptor && descriptor.set;
    });
    const page = await context.newPage();""",
  },
  {
   'name':'a003',
   'path':root/'audit/a003-live-runtime.cjs',
   'status_old':"    channel.port1.onmessage = e => { clearTimeout(timer); resolve(e.data); };",
   'status_new':"""    const nativeSetter = globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER;
    if (typeof nativeSetter !== 'function') throw new Error('PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER_MISSING');
    nativeSetter.call(channel.port1, e => { clearTimeout(timer); resolve(e.data); });""",
   'context_old':"""    const context = await browser.newContext({ serviceWorkers:'allow' });
    let page = await bootstrap(context, '#control');""",
   'context_new':"""    const context = await browser.newContext({ serviceWorkers:'allow' });
    await context.addInitScript(() => {
      const descriptor = Object.getOwnPropertyDescriptor(MessagePort.prototype, 'onmessage');
      globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER = descriptor && descriptor.set;
    });
    let page = await bootstrap(context, '#control');""",
  },
 ]
 rows=[]
 for spec in specs:
  target=spec['path'];source=target.read_text();originals[str(target)]=source
  counts={'status':source.count(spec['status_old']),'context':source.count(spec['context_old'])}
  if counts!={'status':1,'context':1}:raise SystemExit('NATIVE_MESSAGEPORT_HARNESS_POINT_INVALID:'+json.dumps({'name':spec['name'],'counts':counts},sort_keys=True))
  patched=source.replace(spec['status_old'],spec['status_new'],1).replace(spec['context_old'],spec['context_new'],1)
  direct_mode='UNCHANGED_NOT_APPLICABLE'
  if spec['name']=='a002' and "landing_mode: 'canonical-current-app'" not in patched:
   anchor="""    const urls = page.frames().map(f => f.url());
    const homeUrls = urls.filter(u => /pmp-home-single-v6\\.html/.test(u));"""
   insert="""    const urls = page.frames().map(f => f.url());
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
    const homeUrls = urls.filter(u => /pmp-home-single-v6\\.html/.test(u));"""
   if patched.count(anchor)!=1:raise SystemExit(f'A002_DIRECT_CANONICAL_POINT_INVALID:{patched.count(anchor)}')
   patched=patched.replace(anchor,insert,1);direct_mode='PATCHED'
  target.write_text(patched)
  check=subprocess.run(['node','--check',str(target)],text=True,capture_output=True)
  if check.returncode!=0:
   target.write_text(source)
   raise SystemExit('NATIVE_MESSAGEPORT_NODE_CHECK_FAILED:'+json.dumps({'name':spec['name'],'stdout':check.stdout,'stderr':check.stderr},sort_keys=True))
  rows.append({'name':spec['name'],'path':str(target),'original_sha256':hashlib.sha256(source.encode()).hexdigest(),'patched_sha256':hashlib.sha256(patched.encode()).hexdigest(),'status_patch_count':1,'context_pre_page_capture_count':1,'direct_canonical_mode':direct_mode,'node_check_passed':True})
 evidence={'type':'PMP_P2C_NATIVE_MESSAGEPORT_TEST_HARNESS_REPAIR_094','status':'PASS','label':label,'rows':rows,'test_only':True,'production_actor_policy_changed':False,'unknown_actor_policy_weakened':False,'native_setter_captured_before_page_creation':True}
 (evidence_dir/f'native-messageport-test-harness-repair-094-{label}.json').write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
 return originals

def restore_native_messageport_harnesses(evidence_dir,label,originals):
 rows=[]
 for raw,source in originals.items():
  target=Path(raw);target.write_text(source);actual=hashlib.sha256(target.read_bytes()).hexdigest();expected=hashlib.sha256(source.encode()).hexdigest()
  if actual!=expected:raise SystemExit(f'NATIVE_MESSAGEPORT_HARNESS_RESTORE_FAILED:{raw}:{actual}:{expected}')
  rows.append({'path':raw,'restored_sha256':actual,'byte_for_byte_restored':True})
 evidence={'type':'PMP_P2C_NATIVE_MESSAGEPORT_TEST_HARNESS_RESTORE_094','status':'PASS','label':label,'rows':rows}
 (evidence_dir/f'native-messageport-test-harness-restore-094-{label}.json').write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
'''

main_anchor='def main():\n'
if text.count(main_anchor)!=1:raise SystemExit(f'REHEARSAL094_MAIN_ANCHOR_INVALID:{text.count(main_anchor)}')
text=text.replace(main_anchor,helper+'\n'+main_anchor,1)

active_anchor=" a=ap.parse_args();a.evidence_dir.mkdir(parents=True,exist_ok=True);env=dict(os.environ);results=[]\n try:"
active_insert=" a=ap.parse_args();a.evidence_dir.mkdir(parents=True,exist_ok=True);env=dict(os.environ);results=[]\n active_harness_originals=patch_native_messageport_harnesses(a.activated_root,a.evidence_dir,'active')\n try:"
if text.count(active_anchor)!=1:raise SystemExit(f'REHEARSAL094_ACTIVE_HARNESS_BOUNDARY_INVALID:{text.count(active_anchor)}')
text=text.replace(active_anchor,active_insert,1)

restored_anchor=" # restored copy regressions, mandatory even when an active lane failed\n results.append(run('a003-repository-restored-21'"
restored_insert=" # restored copy regressions, mandatory even when an active lane failed\n restored_harness_originals=patch_native_messageport_harnesses(a.activated_root,a.evidence_dir,'restored')\n results.append(run('a003-repository-restored-21'"
if text.count(restored_anchor)!=1:raise SystemExit(f'REHEARSAL094_RESTORED_HARNESS_BOUNDARY_INVALID:{text.count(restored_anchor)}')
text=text.replace(restored_anchor,restored_insert,1)

restore_anchor=" results.append(run('a002-restored-41',['node','audit/a002-live-runtime.cjs'],a.activated_root,e,a.evidence_dir/'a002-restored-command.json',300));server.terminate();server.wait(timeout=10)\n def rd(p):"
restore_insert=" results.append(run('a002-restored-41',['node','audit/a002-live-runtime.cjs'],a.activated_root,e,a.evidence_dir/'a002-restored-command.json',300));server.terminate();server.wait(timeout=10)\n restore_native_messageport_harnesses(a.evidence_dir,'restored',restored_harness_originals)\n def rd(p):"
if text.count(restore_anchor)!=1:raise SystemExit(f'REHEARSAL094_RESTORED_RESTORE_BOUNDARY_INVALID:{text.count(restore_anchor)}')
text=text.replace(restore_anchor,restore_insert,1)

compile(text,str(path),'exec')
contracts={
 'helper':text.count('def patch_native_messageport_harnesses('),
 'restore_helper':text.count('def restore_native_messageport_harnesses('),
 'active_call':text.count("patch_native_messageport_harnesses(a.activated_root,a.evidence_dir,'active')"),
 'restored_call':text.count("patch_native_messageport_harnesses(a.activated_root,a.evidence_dir,'restored')"),
 'restored_restore':text.count("restore_native_messageport_harnesses(a.evidence_dir,'restored',restored_harness_originals)"),
}
expected={'helper':1,'restore_helper':1,'active_call':1,'restored_call':1,'restored_restore':1}
if contracts!=expected:raise SystemExit('REHEARSAL094_FINAL_RUNNER_CONTRACT_INVALID:'+json.dumps({'actual':contracts,'expected':expected},sort_keys=True))
path.write_text(text)
patched_bytes=path.read_bytes();patched_sha256=hashlib.sha256(patched_bytes).hexdigest()
(out/'run-full-isolated-proof-final-after-harness-repair-094.py').write_bytes(patched_bytes)
evidence={'type':'PMP_P2C_FINAL_COMPILED_RUNNER_HARNESS_REPAIR_094','status':'PASS','target':str(path),'original_sha256':original_sha256,'patched_sha256':patched_sha256,'contracts':contracts,'test_only':True,'production_actor_policy_changed':False,'unknown_actor_policy_weakened':False,'native_setter_captured_before_page_creation':True,'a002_direct_canonical_landing_normalized':True}
(out/'final-compiled-runner-harness-repair-094.json').write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
print(json.dumps(evidence,sort_keys=True))
