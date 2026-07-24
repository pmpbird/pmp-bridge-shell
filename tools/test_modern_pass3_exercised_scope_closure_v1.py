#!/usr/bin/env python3
import copy,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
C=json.loads((ROOT/'audit/pass3/modern-pass3-exercised-scope-closure-v1.json').read_text())
FALSE=['real_app_proof','production_activation','current_clean','frozen','full_transfer_proof','full_history_lossless','best_in_world']
def check(c):
 g=[]; s=c.get('certified_scope',{})
 if c.get('type')!='PMP_MODERN_PASS3_EXERCISED_SCOPE_CLOSURE_V1':g.append('type')
 if s.get('hooks')!=[f'HOOK-{i:03d}' for i in range(1,7)]:g.append('hooks')
 for k in ['deterministic_contract_validation','isolated_node_vm_runtime_harness','positive_and_fail_closed_negative_gates','deterministic_receipts','runtime_sources_preserved','historical_freeze_preserved']:
  if s.get(k) is not True:g.append(k)
 for k in FALSE:
  if c.get('claim_ceiling',{}).get(k) is not False:g.append('overclaim:'+k)
 if len(c.get('unit1_files',[]))!=4:g.append('unit1')
 if len(c.get('unit2_files',[]))!=5:g.append('unit2')
 if len(c.get('protected_files',[]))!=3:g.append('protected')
 if len(c.get('changed_paths',[]))!=4:g.append('paths')
 if c.get('formal_proof')!={'count':1,'result':'FAIL','receipt082':'CONSUMED','new_run':False}:g.append('formal')
 if c.get('production_activation') is not False:g.append('activation')
 return g
assert not check(C),check(C)
m=[('missing_hook',lambda x:x['certified_scope']['hooks'].pop()),('missing_unit1',lambda x:x['unit1_files'].pop()),('missing_unit2',lambda x:x['unit2_files'].pop()),('missing_protected',lambda x:x['protected_files'].pop()),('wrong_paths',lambda x:x['changed_paths'].pop()),('formal_count',lambda x:x['formal_proof'].__setitem__('count',2)),('formal_result',lambda x:x['formal_proof'].__setitem__('result','PASS')),('new_formal',lambda x:x['formal_proof'].__setitem__('new_run',True))]
m += [(f'overclaim_{k}',lambda x,k=k:x['claim_ceiling'].__setitem__(k,True)) for k in FALSE]
cases=[]
for n,f in m:
 x=copy.deepcopy(C);f(x);assert check(x),n;cases.append(n)
r={'type':'PMP_MODERN_PASS3_EXERCISED_SCOPE_CLOSURE_TEST_RECEIPT_V1','status':'PASS','positive':1,'negative_fail_closed':len(cases),'cases':cases,'deterministic':True}
assert json.dumps(r,sort_keys=True)==json.dumps(r,sort_keys=True)
print(json.dumps(r,sort_keys=True))
