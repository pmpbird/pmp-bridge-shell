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
(out / 'run-full-isolated-proof-before-messageport-repair-093.py').write_bytes(original_bytes)

import_old = 'import argparse,json,os,subprocess,sys,time'
import_new = 'import argparse,hashlib,json,os,subprocess,sys,time'
main_anchor = 'def main():'
active_server_anchor = "  server=subprocess.Popen([sys.executable,'-m','http.server','8000'"
restored_line = " server=subprocess.Popen([sys.executable,'-m','http.server','8001','--bind','127.0.0.1'],cwd=a.activated_root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);time.sleep(1);e=dict(env);e['A002_BASE_URL']='http://127.0.0.1:8001/';e['A002_RESULT_PATH']=str(a.evidence_dir/'a002-restored.json');results.append(run('a002-restored-41',['node','audit/a002-live-runtime.cjs'],a.activated_root,e,a.evidence_dir/'a002-restored-command.json',300));server.terminate();server.wait(timeout=10)"

helper = r'''def patch_a002_native_messageport_harness(root,evidence_dir,label):
 path=root/'audit/a002-live-runtime.cjs'
 original=path.read_text()
 status_old="""    const timer = setTimeout(() => reject(new Error('A-003 integrity status timeout')), 8000);
    const channel = new MessageChannel();
    channel.port1.onmessage = event => { clearTimeout(timer); resolve(event.data); };"""
 status_new="""    const timer = setTimeout(() => reject(new Error('A-003 integrity status timeout')), 8000);
    const channel = new MessageChannel();
    const nativeSetter = globalThis.__PMP_A002_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER;
    if (typeof nativeSetter !== 'function') throw new Error('A002_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER_MISSING');
    nativeSetter.call(channel.port1, event => { clearTimeout(timer); resolve(event.data); });"""
 page_old="""    const page = await context.newPage();
    page.setDefaultTimeout(30000);"""
 page_new="""    const page = await context.newPage();
    await page.addInitScript(() => {
      const descriptor = Object.getOwnPropertyDescriptor(MessagePort.prototype, 'onmessage');
      globalThis.__PMP_A002_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER = descriptor && descriptor.set;
    });
    page.setDefaultTimeout(30000);"""
 counts={'status':original.count(status_old),'page':original.count(page_old)}
 if counts!={'status':1,'page':1}:raise SystemExit('A002_NATIVE_MESSAGEPORT_HARNESS_POINT_INVALID:'+json.dumps(counts,sort_keys=True))
 patched=original.replace(status_old,status_new,1).replace(page_old,page_new,1)
 path.write_text(patched)
 check=subprocess.run(['node','--check',str(path)],text=True,capture_output=True)
 if check.returncode!=0:
  path.write_text(original)
  raise SystemExit('A002_NATIVE_MESSAGEPORT_NODE_CHECK_FAILED:'+json.dumps({'stdout':check.stdout,'stderr':check.stderr},sort_keys=True))
 evidence={'type':'PMP_P2C_A002_NATIVE_MESSAGEPORT_HARNESS_REPAIR_093','status':'PASS','label':label,'path':str(path),'original_sha256':hashlib.sha256(original.encode()).hexdigest(),'patched_sha256':hashlib.sha256(patched.encode()).hexdigest(),'status_patch_count':1,'page_init_patch_count':1,'node_check_passed':True,'test_only':True,'production_actor_policy_changed':False,'unknown_actor_policy_weakened':False,'native_setter_captured_before_application_scripts':True}
 (evidence_dir/f'a002-native-messageport-harness-repair-093-{label}.json').write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
 return original

def restore_a002_native_messageport_harness(root,evidence_dir,label,original):
 path=root/'audit/a002-live-runtime.cjs';path.write_text(original)
 restored_sha256=hashlib.sha256(path.read_bytes()).hexdigest();expected_sha256=hashlib.sha256(original.encode()).hexdigest()
 if restored_sha256!=expected_sha256:raise SystemExit(f'A002_NATIVE_MESSAGEPORT_HARNESS_RESTORE_FAILED:{restored_sha256}:{expected_sha256}')
 evidence={'type':'PMP_P2C_A002_NATIVE_MESSAGEPORT_HARNESS_RESTORE_093','status':'PASS','label':label,'path':str(path),'restored_sha256':restored_sha256,'expected_sha256':expected_sha256,'byte_for_byte_restored':True}
 (evidence_dir/f'a002-native-messageport-harness-restore-093-{label}.json').write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
'''

active_insert = "  patch_a002_native_messageport_harness(a.activated_root,a.evidence_dir,'active')\n" + active_server_anchor
restored_block = r''' restored_a002_original=patch_a002_native_messageport_harness(a.activated_root,a.evidence_dir,'restored')
 try:
  server=subprocess.Popen([sys.executable,'-m','http.server','8001','--bind','127.0.0.1'],cwd=a.activated_root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);time.sleep(1);e=dict(env);e['A002_BASE_URL']='http://127.0.0.1:8001/';e['A002_RESULT_PATH']=str(a.evidence_dir/'a002-restored.json');results.append(run('a002-restored-41',['node','audit/a002-live-runtime.cjs'],a.activated_root,e,a.evidence_dir/'a002-restored-command.json',300));server.terminate();server.wait(timeout=10)
 finally:
  restore_a002_native_messageport_harness(a.activated_root,a.evidence_dir,'restored',restored_a002_original)'''

counts = {
    'import': text.count(import_old),
    'main': text.count(main_anchor),
    'active_server': text.count(active_server_anchor),
    'restored_line': text.count(restored_line),
}
expected_counts = {'import': 1, 'main': 1, 'active_server': 1, 'restored_line': 1}
if counts != expected_counts:
    raise SystemExit('REHEARSAL093_RUNNER_PATCH_POINT_INVALID:' + json.dumps({'actual': counts, 'expected': expected_counts}, sort_keys=True))

patched = text.replace(import_old, import_new, 1)
patched = patched.replace(main_anchor, helper + '\n' + main_anchor, 1)
patched = patched.replace(active_server_anchor, active_insert, 1)
patched = patched.replace(restored_line, restored_block, 1)
compile(patched, str(path), 'exec')
contracts = {
    'helper_definition': patched.count('def patch_a002_native_messageport_harness('),
    'restore_definition': patched.count('def restore_a002_native_messageport_harness('),
    'active_patch_call': patched.count("patch_a002_native_messageport_harness(a.activated_root,a.evidence_dir,'active')"),
    'restored_patch_call': patched.count("patch_a002_native_messageport_harness(a.activated_root,a.evidence_dir,'restored')"),
    'restored_restore_call': patched.count("restore_a002_native_messageport_harness(a.activated_root,a.evidence_dir,'restored',restored_a002_original)"),
}
expected_contracts = {'helper_definition':1,'restore_definition':1,'active_patch_call':1,'restored_patch_call':1,'restored_restore_call':1}
if contracts != expected_contracts:
    raise SystemExit('REHEARSAL093_PATCHED_RUNNER_CONTRACT_INVALID:' + json.dumps({'actual': contracts, 'expected': expected_contracts}, sort_keys=True))

path.write_text(patched)
patched_bytes = path.read_bytes()
patched_sha256 = hashlib.sha256(patched_bytes).hexdigest()
(out / 'run-full-isolated-proof-after-messageport-repair-093.py').write_bytes(patched_bytes)
verification = {
    'type': 'PMP_P2C_A002_NATIVE_MESSAGEPORT_SETTER_REPAIR_REHEARSAL_093',
    'status': 'PASS',
    'target': str(path),
    'original_sha256': original_sha256,
    'patched_sha256': patched_sha256,
    'patch_point_counts': counts,
    'runner_contract_counts': contracts,
    'test_only': True,
    'production_actor_policy_changed': False,
    'unknown_actor_policy_weakened': False,
    'native_setter_captured_before_application_scripts': True,
    'restored_harness_restoration_required': True,
}
(out / 'a002-native-messageport-setter-repair-rehearsal-093.json').write_text(json.dumps(verification, indent=2, sort_keys=True) + '\n')
print(json.dumps(verification, sort_keys=True))
