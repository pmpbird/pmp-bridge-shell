#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json, subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

R=Path(__file__).resolve().parents[1]
A='1ef9b2268cd045d6c96e357539bbe09db137b5fe'
CID='P01.5-MASTER-CONSOLIDATION-v1'
INV='audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl'
OLD='audit/routing-inventory/Packet_01.5_Applicability_Inventory_v9_Batch_008.jsonl'
WIN='audit/applicability/Packet_01.5_Scalable_Pass_001_Window_v1.json'
PLAN='audit/applicability/Packet_01.5_Scalable_Pass_001_Plan_v1.json'
BD='audit/applicability/Packet_01.5_Scalable_Pass_001_Decisions_v1.jsonl'
BQ='audit/applicability/Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl'
BC='audit/Packet_01.5_Scalable_Pass_001_Coverage_v1.json'
BR='audit/Packet_01.5_Scalable_Pass_001_Independent_Verification_v1.json'
F=[
('CURRENT_RUNTIME_SOURCE','audit/applicability/Packet_01.5_Current_Runtime_Source_Corrected_Decisions_v1.jsonl','audit/applicability/Packet_01.5_Current_Runtime_Source_Corrected_Remaining_Queue_v1.jsonl','audit/Packet_01.5_Current_Runtime_Source_Corrected_Coverage_v1.json','audit/Packet_01.5_Current_Runtime_Source_Corrected_Independent_Verification_v1.json'),
('AUTHORITATIVE_PACKET_LAW','audit/applicability/Packet_01.5_Authoritative_Packet_Law_Family_Decisions_v1.jsonl','audit/applicability/Packet_01.5_Authoritative_Packet_Law_Family_Remaining_Queue_v1.jsonl','audit/Packet_01.5_Authoritative_Packet_Law_Family_Coverage_v1.json','audit/Packet_01.5_Authoritative_Packet_Law_Family_Independent_Verification_v1.json'),
('DEPLOYMENT_AND_LIVE_BEHAVIOR','audit/applicability/Packet_01.5_Deployment_Live_Family_Decisions_v1.jsonl','audit/applicability/Packet_01.5_Deployment_Live_Family_Remaining_Queue_v1.jsonl','audit/Packet_01.5_Deployment_Live_Family_Coverage_v1.json','audit/Packet_01.5_Deployment_Live_Family_Independent_Verification_v1.json'),
('OTHER_RECORD_SPECIFIC_PROOF','audit/applicability/Packet_01.5_Other_Record_Specific_Family_Decisions_v1.jsonl','audit/applicability/Packet_01.5_Other_Record_Specific_Family_Remaining_Queue_v1.jsonl','audit/Packet_01.5_Other_Record_Specific_Family_Coverage_v1.json','audit/Packet_01.5_Other_Record_Specific_Family_Independent_Verification_v1.json'),
('DEPENDENCY_OR_PLATFORM_STATE','audit/applicability/Packet_01.5_Dependency_Platform_Family_Decisions_v1.jsonl','audit/applicability/Packet_01.5_Dependency_Platform_Family_Remaining_Queue_v1.jsonl','audit/Packet_01.5_Dependency_Platform_Family_Coverage_v1.json','audit/Packet_01.5_Dependency_Platform_Independent_Verification_v1.json'),
('CROSS_SOURCE_CONFLICT','audit/applicability/Packet_01.5_Cross_Source_Conflict_Decisions_v1.jsonl','audit/applicability/Packet_01.5_Cross_Source_Conflict_Remaining_Queue_v1.jsonl','audit/Packet_01.5_Cross_Source_Conflict_Coverage_v1.json','audit/Packet_01.5_Cross_Source_Conflict_Independent_Verification_v1.json'),
('PRIVATE_OR_UNCAPTURED_EVIDENCE','audit/applicability/Packet_01.5_Private_Evidence_Family_Decisions_v1.jsonl','audit/applicability/Packet_01.5_Private_Evidence_Family_Remaining_Queue_v1.jsonl','audit/Packet_01.5_Private_Evidence_Family_Coverage_v1.json','audit/Packet_01.5_Private_Evidence_Family_Independent_Verification_v1.json')]
OM=R/'audit/Packet_01.5_Master_Applicability_Consolidation_v1.json'
OD=R/'audit/applicability/Packet_01.5_Master_Applicability_Decisions_v1.jsonl'
OQ=R/'audit/applicability/Packet_01.5_Master_Remaining_Evidence_Queue_v1.jsonl'
OO=R/'audit/routing-inventory/Packet_01.5_Applicability_Inventory_v10_Master_Consolidated.jsonl'
OL=R/'audit/Packet_01.5_Master_Applicability_Conflict_Ledger_v1.json'
OC=R/'audit/Packet_01.5_Master_Applicability_Coverage_v1.json'
OS=R/'audit/Packet_01.5_Master_Applicability_Status_v1.md'

def g(*a,b=False):
 p=subprocess.run(['git',*a],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
 return p if b else p.decode(errors='replace')
def sb(p): return g('show',f'{A}:{p}',b=True)
def st(p): return sb(p).decode()
def js(p): return json.loads(st(p))
def jl(p): return [json.loads(x) for x in st(p).splitlines() if x.strip()]
def sh(b): return hashlib.sha256(b).hexdigest()
def fh(p): return sh(sb(p))
def ch(x): return sh(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
def wj(p,x): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def wl(p,x): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(''.join(json.dumps(y,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n' for y in x))
def walk(x):
 if isinstance(x,dict):
  yield x
  for v in x.values(): yield from walk(v)
 elif isinstance(x,list):
  for v in x: yield from walk(v)
def claim(x):
 if isinstance(x.get('preserved_claim'),str): return x['preserved_claim'].strip()
 m=x.get('missing_proof'); z='Preserved claim: '
 if isinstance(m,str) and z in m:return m.split(z,1)[1].strip()
 for k in ('source_claim','claim_text','historical_claim','finding','statement','record_text','source_text','claim'):
  if isinstance(x.get(k),str) and x[k].strip(): return x[k].strip()
def passed(x):
 t=json.dumps(x).upper();return 'PASS' in t and 'FAIL' not in t
def findint(x,keys):
 for d in walk(x):
  for k in keys:
   if isinstance(d.get(k),int):return d[k]

def main():
 g('cat-file','-e',f'{A}^{{commit}}')
 ib,ob=sb(INV),sb(OLD); inv,old=jl(INV),jl(OLD); win,plan=js(WIN),js(PLAN); bd,bq=jl(BD),jl(BQ)
 assert len(inv)==len(old)==2750 and win['records']==122 and len(bd)==6 and len(bq)==116 and passed(js(BR))
 ids=[{'composite_address':x['composite_address'],'source_record_ordinal':x['source_record_ordinal'],'original_identifier':x['original_identifier'],'source_envelope_hash':x['envelope_hash'],'source_block_hash':x['source_block_hash']} for x in win['record_identities']]
 add=[x['composite_address'] for x in ids]; assert len(add)==len(set(add))==122
 ii={x['composite_address']:x for x in inv}; oi={x['composite_address']:x for x in old}; wi={x['composite_address']:x for x in ids}; bqi={x['composite_address']:x for x in bq}
 pi=defaultdict(list)
 for d in walk(plan):
  if isinstance(d.get('composite_address'),str):pi[d['composite_address']].append(d)
 claims={}
 for a in add:
  cand=(([bqi[a]] if a in bqi else [])+pi[a]+[ii[a]])
  c=next((claim(x) for x in cand if claim(x)),None)
  if not c: raise AssertionError(f'claim missing {a}: {sorted(ii[a])}')
  claims[a]=c
 exp=defaultdict(list)
 for x in bq:exp[x['evidence_domain']].append(x['composite_address'])
 assert set(exp)=={x[0] for x in F}
 fammeta=[]; fd=defaultdict(list); fq={}
 for name,dp,qp,cp,rp in F:
  ds,qs,cov,rec=jl(dp),jl(qp),js(cp),js(rp); da=[x['composite_address'] for x in ds];qa=[x['composite_address'] for x in qs]
  assert set(da).isdisjoint(qa) and set(da)|set(qa)==set(exp[name]) and passed(rec) and sh(ib) in json.dumps(rec)
  assert findint(cov,('family_records',))==len(exp[name]);assert findint(cov,('decided_records','decisions_created'))==len(ds);assert findint(cov,('remaining_queued_records','remaining_exact_queues'))==len(qs);assert findint(cov,('unknown_hold_created','unknown_hold_decisions'))==0
  fammeta.append({'family':name,'records':len(exp[name]),'decisions':len(ds),'queued':len(qs),'addresses':exp[name],'paths':{'decisions':dp,'queue':qp,'coverage':cp,'receipt':rp},'sha256':{'decisions':fh(dp),'queue':fh(qp),'coverage':fh(cp),'receipt':fh(rp)}})
  for x in ds:fd[x['composite_address']].append((name,dp,x))
  for x in qs:
   a=x['composite_address'];assert a not in fq;fq[a]=(name,qp,x)
 assert set(fd).isdisjoint(fq) and set(fd)|set(fq)==set(bqi)
 contradictions=[];dupes=[];sel={}
 for a,c in fd.items():
  states={x[2].get('applicability_state') for x in c}
  if len(states)>1: contradictions.append({'composite_address':a,'states':sorted(map(str,states)),'sources':[{'family':n,'path':p,'sha256':ch(r)} for n,p,r in c]})
  else:
   c.sort(key=lambda x:x[0]);sel[a]=c[0]
   if len(c)>1:dupes.append({'composite_address':a,'state':next(iter(states)),'families':[x[0] for x in c]})
 if contradictions: raise AssertionError(json.dumps(contradictions))
 md=[]
 for x in bd:
  a=x['composite_address'];y=copy.deepcopy(x);y['preserved_claim']=claims[a];y['master_consolidation']={'id':CID,'anchor':A,'layer':'BASELINE_DECISION','family':None,'path':BD,'artifact_sha256':fh(BD),'source_decision_sha256':ch(x),'prior_state':oi[a].get('applicability_state'),'prior_decision_hash':oi[a].get('applicability_decision_hash')};md.append(y)
 for a in sorted(sel,key=lambda q:wi[q]['source_record_ordinal']):
  n,p,x=sel[a];y=copy.deepcopy(x);y['preserved_claim']=claims[a];y['master_consolidation']={'id':CID,'anchor':A,'layer':'VERIFIED_FAMILY_DECISION','family':n,'path':p,'artifact_sha256':fh(p),'source_decision_sha256':ch(x),'prior_state':oi[a].get('applicability_state'),'prior_decision_hash':oi[a].get('applicability_decision_hash')};md.append(y)
 md.sort(key=lambda x:wi[x['composite_address']]['source_record_ordinal'])
 mq=[]
 for a in sorted(fq,key=lambda q:wi[q]['source_record_ordinal']):
  n,p,x=fq[a];o=oi[a];mq.append({**wi[a],'preserved_claim':claims[a],'evidence_domain':n,'master_queue_id':f'{CID}::{a}','result':'REMAIN_QUEUED','prior_applicability_state':o.get('applicability_state'),'prior_applicability_decision_hash':o.get('applicability_decision_hash'),'prior_applicability_batch_id':o.get('applicability_batch_id'),'state_preservation_rule':'PRIOR_STATE_PRESERVED_UNTIL_DIRECT_VERIFIED_EVIDENCE','family_queue_path':p,'family_queue_sha256':fh(p),'family_queue_record_sha256':ch(x),'family_queue_record':x,'reopening_rule':'Capture the exact required evidence, bind it to this permanent address, and independently verify it.'})
 ma={x['composite_address'] for x in md};qa={x['composite_address'] for x in mq};assert ma.isdisjoint(qa) and ma|qa==set(add)
 mdi={x['composite_address']:x for x in md};mqi={x['composite_address']:x for x in mq};overlay=[];sup=[]
 for o in old:
  a=o['composite_address']
  if a in mdi:
   y=copy.deepcopy(o);d=mdi[a]
   for k,v in d.items():
    if k not in ('master_consolidation','preserved_claim'):y[k]=copy.deepcopy(v)
   nh=ch({'id':CID,'address':a,'source':d['master_consolidation']['source_decision_sha256'],'state':y.get('applicability_state')});oldstate=o.get('applicability_state');oldhash=o.get('applicability_decision_hash');y['applicability_decision_hash']=nh;y['applicability_batch_id']=CID;y['master_consolidation']={**d['master_consolidation'],'result':'DECIDED','master_decision_hash':nh};overlay.append(y)
   if oldstate!=y.get('applicability_state') or oldhash!=nh:sup.append({'composite_address':a,'prior_state':oldstate,'new_state':y.get('applicability_state'),'prior_decision_hash':oldhash,'new_decision_hash':nh,'source_family':d['master_consolidation']['family'],'result':'NEWER_VERIFIED_DECISION_APPLIED'})
  elif a in mqi:
   y=copy.deepcopy(o);q=mqi[a];y['master_consolidation']={'id':CID,'anchor':A,'result':'REMAIN_QUEUED','family':q['evidence_domain'],'queue_path':q['family_queue_path'],'queue_record_sha256':q['family_queue_record_sha256'],'prior_state_preserved':True};overlay.append(y)
  else:overlay.append(copy.deepcopy(o))
 assert len(overlay)==2750
 states=Counter(x.get('applicability_state') for x in md);dc=Counter(x['master_consolidation']['family'] or 'BASELINE' for x in md);qc=Counter(x['evidence_domain'] for x in mq)
 ledger={'packet':'01.5','artifact':'master_applicability_conflict_ledger','version':1,'anchor':A,'real_contradiction_count':0,'real_contradictions':[],'same_state_duplicate_count':len(dupes),'same_state_duplicates':dupes,'supersession_count':len(sup),'supersessions':sup,'precedence_rules':['Immutable identity and claim come from the baseline window and source inventory.','Verified baseline decisions remain unless a later verified same-address decision exists.','The seven families partition the 116 baseline evidence-queue records.','Corrected current-runtime results supersede the earlier untrusted runtime partition.','Later merged independently verified family decisions supersede the prior overlay.','Queued records preserve prior applicability state and decision hash.','Equal-precedence different states are real contradictions and stop consolidation.']}
 manifest={'packet':'01.5','artifact':'master_applicability_consolidation','version':1,'id':CID,'anchor':A,'scope':{'first':win['first_address'],'last':win['last_address'],'records':122,'addresses':add},'immutable_source':{'path':INV,'sha256':sh(ib),'records':2750,'unchanged':True},'prior_overlay':{'path':OLD,'sha256':sh(ob),'records':2750},'baseline':{'decisions':len(bd),'queued':len(bq),'paths':{'window':WIN,'plan':PLAN,'decisions':BD,'queue':BQ,'coverage':BC,'receipt':BR},'sha256':{p:fh(p) for p in (WIN,PLAN,BD,BQ,BC,BR)}},'families':fammeta,'result':{'records':122,'decisions':len(md),'remaining_queue':len(mq),'unknown_hold_created':0,'decision_state_counts':dict(states),'decision_source_counts':dict(dc),'queue_family_counts':dict(qc),'real_contradictions':0,'supersessions':len(sup)},'prohibited_actions':{'routing_assignments':0,'destination_assignments':0,'grouping_assignments':0,'source_records_removed_or_closed':0,'implementation_actions':0,'packet_04_actions':0}}
 coverage={'packet':'01.5','id':CID,'anchor':A,'window_records':122,'decision_records':len(md),'remaining_queued_records':len(mq),'unknown_hold_created':0,'complete_nonduplicated_coverage':True,'permanent_addresses_preserved':True,'preserved_claims_unchanged':True,'source_inventory_count':2750,'source_inventory_sha256':sh(ib),'source_inventory_unchanged':True,'prior_overlay_count':2750,'new_overlay_count':2750,'new_versioned_overlay':str(OO.relative_to(R)),'real_contradiction_count':0,'routing_assignments':0,'destination_assignments':0,'grouping_assignments':0,'source_records_removed_or_closed':0,'implementation_actions':0,'packet_04_actions':0}
 status=f'''# Packet 01.5 Master Applicability Consolidation v1\n\nSTATUS: CONSOLIDATED — INDEPENDENT VERIFICATION REQUIRED\n\n- Anchor: `{A}`\n- Authorized window: `{win['first_address']}` through `{win['last_address']}`\n- Window records: 122\n- Master decisions: {len(md)}\n- Remaining evidence queue: {len(mq)}\n- Automatic `UNKNOWN — HOLD`: 0\n- Real contradictions: 0\n- Versioned overlay records: 2,750\n- Immutable source inventory: 2,750 records unchanged\n\nOnly merged verified baseline and seven-family artifacts were used. No evidence was reacquired and no preserved claim was changed.\n\nNo routing, destinations, grouping, source-record closure or removal, implementation, or Packet 04 work occurred.\n'''
 wj(OM,manifest);wl(OD,md);wl(OQ,mq);wl(OO,overlay);wj(OL,ledger);wj(OC,coverage);OS.write_text(status)
 print(json.dumps({'status':'BUILT','records':122,'decisions':len(md),'queue':len(mq),'states':dict(states),'supersessions':len(sup),'inventory':2750},indent=2))
if __name__=='__main__':main()
