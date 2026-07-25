#!/usr/bin/env python3
import copy,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
I=json.loads((ROOT/'audit/passes1-2/canonical-authority-index-v1.json').read_text())
X=json.loads((ROOT/'audit/pass2/pass2-scope-precedence-crosswalk-v1.json').read_text())
P=json.loads((ROOT/'audit/pass1/pass1-post-merge-confirmation-v1.json').read_text())
FALSE_CLAIMS=['active_chain_enforcement','real_app_proof','production_activation','later_pass_completion','new_formal_proof']
def check(i,x,p):
 g=[]
 if i.get('precedence_rule')!='CURRENT_SCOPED_AUTHORITY_OVERRIDES_OLDER_RECORDS_ONLY_WITHIN_THE_SAME_SCOPE;HISTORICAL_EVIDENCE_REMAINS_IMMUTABLE':g.append('index_precedence')
 records=i.get('records',[])
 if len(records)<6:g.append('index_records')
 if any(not r.get('scope') or not r.get('classification') for r in records):g.append('missing_scope')
 current=[r for r in records if r.get('current_status')=='AUTHORITATIVE']
 if not any(r.get('path')=='audit/pass2/pass2-full-roadmap-authority-definition-closure-v1.json' for r in current):g.append('pass2_current')
 old=next((r for r in records if r.get('path')=='pmp-actor-authority-policy-v1.json'),{})
 if old.get('classification')!='HISTORICAL_P2B_POLICY':g.append('old_policy_scope')
 if old.get('current_status')!='HISTORICAL_SCOPED_AUTHORITY':g.append('historical_override')
 if x.get('precedence_rule')!='NO_RECORD_OVERRIDES_ANOTHER_OUTSIDE_ITS_DECLARED_SCOPE':g.append('crosswalk_precedence')
 stages=x.get('stages',[])
 if len(stages)!=5 or any(not s.get('scope') or not s.get('status') for s in stages):g.append('crosswalk_stages')
 p2b=next((s for s in stages if s.get('stage')=='P2B_FIXTURE_GATE_CERTIFICATION'),{})
 if p2b.get('pass2_complete_false_interpretation')!='P2B_SCOPE_ONLY_NOT_GLOBAL_ROADMAP_STATUS':g.append('p2b_interpretation')
 proof=next((s for s in stages if s.get('stage')=='P2C_PROOF_HISTORY'),{})
 if proof.get('status')!='FAIL_PRESERVED' or proof.get('receipt082')!='CONSUMED':g.append('receipt082')
 if p.get('historical_creation_state_preserved') is not True or p.get('historical_pending_merge_language_interpretation')!='CREATION_TIME_ONLY':g.append('pass1_history')
 if p.get('installed_in_main') is not True:g.append('pass1_install')
 for obj,name in [(i,'index'),(x,'crosswalk')]:
  for k in FALSE_CLAIMS:
   if obj.get('claim_ceiling',{}).get(k) is not False:g.append(name+'_overclaim_'+k)
  if obj.get('pr122',{}).get('modified') is not False or obj.get('pr122',{}).get('merge_authorized') is not False:g.append(name+'_pr122')
  if obj.get('runtime_files_modified') is not False or obj.get('persisted_data_modified') is not False:g.append(name+'_data')
  if obj.get('pass3_started') is not False:g.append(name+'_pass3')
 return g
assert not check(I,X,P),check(I,X,P)
mutations=[
 ('historical_override',lambda i,x,p:i['records'][3].__setitem__('current_status','AUTHORITATIVE')),
 ('missing_scope',lambda i,x,p:i['records'][0].__setitem__('scope','')),
 ('claim_expansion',lambda i,x,p:i['claim_ceiling'].__setitem__('production_activation',True)),
 ('pr122_authorized',lambda i,x,p:i['pr122'].__setitem__('merge_authorized',True)),
 ('pass3_started',lambda i,x,p:i.__setitem__('pass3_started',True)),
 ('runtime_change',lambda i,x,p:i.__setitem__('runtime_files_modified',True)),
]
for name,mut in mutations:
 i,x,p=copy.deepcopy(I),copy.deepcopy(X),copy.deepcopy(P);mut(i,x,p);assert check(i,x,p),name
print(json.dumps({'type':'PMP_PASSES1_2_REPOSITORY_COMPLETENESS_REPAIR_TEST_RECEIPT_V1','status':'PASS','positive':1,'negative_fail_closed':len(mutations),'cases':[n for n,_ in mutations],'deterministic':True},sort_keys=True))
