#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path

FUNCTION = r'''
def patch_a003_root_receipt_authority(root:Path):
 p=root/'pmp-app-current.html';s=p.read_text()
 marker="  function receipt(status,extra){"
 insert="""  const P2C_A003_NATIVE_FETCH=globalThis.fetch.bind(globalThis);\n  const P2C_A003_NATIVE_STORAGE_SET_ITEM=Storage.prototype.setItem;\n  function p2cA003RootReceiptWrite(key,value){if(key!=='pmp_a003_bootstrap_receipt_v1'&&key!=='pmp_current_entry_route_handoff_receipt_v1')throw fail('P2C_A003_ROOT_RECEIPT_KEY_DENIED','Root receipt authority is restricted to fixed A-003 keys.',{key});return P2C_A003_NATIVE_STORAGE_SET_ITEM.call(localStorage,key,value)}\n"""
 if s.count(marker)!=1:raise SystemExit('A003_ROOT_RECEIPT_INSERTION_POINT_INVALID')
 s=s.replace(marker,insert+marker,1)
 old_boot="localStorage.setItem('pmp_a003_bootstrap_receipt_v1',JSON.stringify(value,null,2))"
 new_boot="p2cA003RootReceiptWrite('pmp_a003_bootstrap_receipt_v1',JSON.stringify(value,null,2))"
 old_handoff="localStorage.setItem('pmp_current_entry_route_handoff_receipt_v1',JSON.stringify(finalReceipt,null,2))"
 new_handoff="p2cA003RootReceiptWrite('pmp_current_entry_route_handoff_receipt_v1',JSON.stringify(finalReceipt,null,2))"
 old_fetch="response=await fetch(path+'?pmp_a003_bootstrap_verify='+encodeURIComponent(String(Date.now())),{cache:'no-store',credentials:'same-origin'})"
 new_fetch="response=await P2C_A003_NATIVE_FETCH(path+'?pmp_a003_bootstrap_verify='+encodeURIComponent(String(Date.now())),{cache:'no-store',credentials:'same-origin'})"
 if s.count(old_boot)!=1 or s.count(old_handoff)!=1:raise SystemExit('A003_ROOT_RECEIPT_WRITE_POINT_INVALID')
 if s.count(old_fetch)!=1:raise SystemExit('A003_ROOT_FETCH_POINT_INVALID')
 s=s.replace(old_boot,new_boot,1).replace(old_handoff,new_handoff,1).replace(old_fetch,new_fetch,1)
 p.write_text(s)
 return {'status':'APPLIED','authority':'A003_ROOT_TRUST_ANCHOR','capture_timing':'BEFORE_ACTOR_GATE_INSTALL','native_operations':['Storage.prototype.setItem','globalThis.fetch'],'native_fetch_scope':'fetchBytes only','allowed_keys':['pmp_a003_bootstrap_receipt_v1','pmp_current_entry_route_handoff_receipt_v1'],'ordinary_actor_storage_authority_changed':False,'ordinary_actor_network_authority_changed':False}
'''

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--path',type=Path,required=True);a=ap.parse_args()
 s=a.path.read_text()
 anchor="def main():\n"
 if s.count(anchor)!=1:raise SystemExit('PREP_MAIN_ANCHOR_INVALID')
 s=s.replace(anchor,FUNCTION+'\n'+anchor,1)
 old=""" for actor in policy['actors']:
  p=a.activated_root/actor['path'];actual=file_sha(p)
  if actual!=actor['sha256']:mism.append({'path':actor['path'],'expected':actor['sha256'],'actual':actual})
 if mism:raise SystemExit('POLICY_SOURCE_MISMATCH:'+json.dumps(mism[:5]))
"""
 new=""" for actor in policy['actors']:
  p=a.activated_root/actor['path'];actual=file_sha(p)
  if actual!=actor['sha256']:mism.append({'path':actor['path'],'expected':actor['sha256'],'actual':actual})
  if actor['path']=='pmp-app-current.html':
   actor['source_identity']='A003_ROOT_TRUST_ANCHOR_PRE_SEAL_EXACT_SOURCE_NOT_GATE_EXECUTED'
   actor['root_receipt_authority_exception']='CAPTURED_NATIVE_SET_ITEM_FIXED_KEYS_ONLY'
 if mism:raise SystemExit('POLICY_SOURCE_MISMATCH:'+json.dumps(mism[:5]))
"""
 if old not in s:raise SystemExit('POLICY_LOOP_PATCH_POINT_MISSING')
 s=s.replace(old,new,1)
 old2=" msha,mcount=finalize_a003(a.activated_root,a.evidence_dir,auth_sha)\n"
 new2=" root_receipt_exception=patch_a003_root_receipt_authority(a.activated_root)\n msha,mcount=finalize_a003(a.activated_root,a.evidence_dir,auth_sha)\n"
 if old2 not in s:raise SystemExit('FINALIZE_PATCH_POINT_MISSING')
 s=s.replace(old2,new2,1)
 old3="'proof_only_prelude_repair':'PREFETCH_ALL_VERIFIED_BYTES_BEFORE_GATE_INSTALL','production_changed':False"
 new3="'proof_only_prelude_repair':'PREFETCH_ALL_VERIFIED_BYTES_BEFORE_GATE_INSTALL','a003_root_receipt_authority_exception':root_receipt_exception,'production_changed':False"
 if old3 not in s:raise SystemExit('OUTPUT_PATCH_POINT_MISSING')
 s=s.replace(old3,new3,1)
 a.path.write_text(s)
if __name__=='__main__':main()
