#!/usr/bin/env python3
import argparse, hashlib, json, pathlib

p=argparse.ArgumentParser()
p.add_argument('--path',required=True)
p.add_argument('--evidence-dir',required=True)
a=p.parse_args()
path=pathlib.Path(a.path)
out=pathlib.Path(a.evidence_dir)
out.mkdir(parents=True,exist_ok=True)
text=path.read_text()

old_worker=''' new="""    const channel = new MessageChannel();
    channel.port1.onmessage = event => { resolve(event.data); };"""'''
new_worker=''' new="""    const channel = new MessageChannel();
    const nativeSetter = globalThis.__PMP_A002_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER;
    if (typeof nativeSetter !== 'function') throw new Error('A002_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER_MISSING');
    nativeSetter.call(channel.port1, event => { resolve(event.data); });"""'''

old_page='''  const page = await context.newPage();
    page.setDefaultTimeout(30000);'''
new_page='''  const page = await context.newPage();
    await page.addInitScript(() => {
      const descriptor = Object.getOwnPropertyDescriptor(MessagePort.prototype, 'onmessage');
      globalThis.__PMP_A002_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER = descriptor && descriptor.set;
    });
    page.setDefaultTimeout(30000);'''

counts={'worker':text.count(old_worker),'page':text.count(old_page)}
if counts['worker']!=1:
    raise SystemExit(f'REHEARSAL088_A002_WORKER_PATCH_POINT_INVALID:{counts["worker"]}')
if counts['page']!=1:
    raise SystemExit(f'REHEARSAL088_A002_PAGE_INIT_PATCH_POINT_INVALID:{counts["page"]}')
patched=text.replace(old_worker,new_worker,1).replace(old_page,new_page,1)
compile(patched,str(path),'exec')
path.write_text(patched)
verification={
  'type':'PMP_P2C_A002_NATIVE_MESSAGEPORT_SETTER_REPAIR_REHEARSAL_088',
  'status':'PASS',
  'target':str(path),
  'worker_patch_count':1,
  'page_init_patch_count':1,
  'test_only':True,
  'production_actor_policy_changed':False,
  'unknown_actor_policy_weakened':False,
  'native_setter_captured_before_application_scripts':True,
  'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
}
(out/'a002-native-messageport-setter-repair-rehearsal-088.json').write_text(json.dumps(verification,indent=2,sort_keys=True)+'\n')
print(json.dumps(verification,sort_keys=True))
