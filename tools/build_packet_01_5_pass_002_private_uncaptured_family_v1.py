#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

R=Path(__file__).resolve().parents[1]
A='417d11653d7e94dcc5b57939dfd4a26f30fdc221'
F='PRIVATE_OR_UNCAPTURED_EVIDENCE'
ADDRESS='P01.5::P004::OBS-004'
QUEUE='audit/applicability/Packet_01.5_Scalable_Pass_002_Evidence_Queue_v1.jsonl'
WINDOW='audit/applicability/Packet_01.5_Scalable_Pass_002_Window_v1.json'
INVENTORY='audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl'
OVERLAY='audit/routing-inventory/Packet_01.5_Applicability_Inventory_v11_Pass_002.jsonl'
CENSUS=R/'audit/Packet_01.5_Pass_002_Private_Uncaptured_Family_Census_v1.json'
DEC=R/'audit/applicability/Packet_01.5_Pass_002_Private_Uncaptured_Family_Decisions_v1.jsonl'
REM=R/'audit/applicability/Packet_01.5_Pass_002_Private_Uncaptured_Family_Remaining_Queue_v1.jsonl'
COV=R/'audit/Packet_01.5_Pass_002_Private_Uncaptured_Family_Coverage_v1.json'
STAT=R/'audit/Packet_01.5_Pass_002_Private_Uncaptured_Family_Status_v1.md'

IDENTITY_KEYS=('composite_address','inventory_position','source_record_ordinal','original_identifier','preserved_claim','source_path','source_pass','source_set','source_file_hash','source_envelope_hash','source_block_hash','queue_id','evidence_domain','prior_applicability_state','prior_applicability_decision_hash','state_preservation_rule')

def git(*args,binary=False):
 p=subprocess.run(['git',*args],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
 return p if binary else p.decode(errors='replace')
def show(path):return git('show',f'{A}:{path}',binary=True)
def rows(data):return [json.loads(x) for x in data.decode().splitlines() if x.strip()]
def sha(data):return hashlib.sha256(data).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def wj(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def wl(path,values):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(''.join(canonical(x)+'\n' for x in values))
def status():
 return f'''# Packet 01.5 Pass 002 — Private or Uncaptured Evidence Family v1

STATUS: BUILT — PENDING INDEPENDENT VERIFICATION

- Authoritative anchor: `{A}`
- Permanent address: `{ADDRESS}`
- Family records: 1
- Direct decisions: 0
- Exact remaining queues: 1
- Automatic `UNKNOWN — HOLD`: 0
- Privacy-safe receipts reviewed: 0
- Private values exposed: no
- Immutable inventory: 2,750 records unchanged
- Pass 002 v11 overlay: 2,750 records unchanged

No approved claim-specific privacy-safe receipt is present. The prior state remains preserved, and the record remains queued for one bounded, independently verifiable receipt that exposes no private values.

No application behavior, configuration, dependencies, deployment, runtime state, routing, destinations, grouping, source-record closure, implementation, or Packet 04 work occurred.
'''

def main():
 git('cat-file','-e',f'{A}^{{commit}}')
 qb,wb,ib,ob=show(QUEUE),show(WINDOW),show(INVENTORY),show(OVERLAY)
 queue=rows(qb);selected=[x for x in queue if x.get('evidence_domain')==F]
 assert len(selected)==1 and selected[0]['composite_address']==ADDRESS
 q=selected[0]
 expected={
  'inventory_position':184,'source_record_ordinal':11,'original_identifier':'OBS-004',
  'preserved_claim':'observed behavior differs from normal behavior and private data leaks.',
  'source_path':'audit/Packet_01.5_Discovery_Pass_04_Performance_Observability_Accessibility_and_Metrics_v1.md',
  'source_pass':4,'source_set':'PROVISIONAL',
  'source_file_hash':'dea3d33cc02124c99bf95698010667c948cda094fabc3bba86e016232aa5d764',
  'source_envelope_hash':'86169e8a89bb971ace18343077a868911c2107941e04916dbebc2f0d290e49b4',
  'source_block_hash':'abb1938a4528f05013354a2bc6d047e092a5ab8008f33664245d572013beedb3',
  'queue_id':'SP002-PRIVATE_OR_UNCAPTURED_EVIDENCE','prior_applicability_state':'UNCLASSIFIED',
  'prior_applicability_decision_hash':None
 }
 for k,v in expected.items():assert q[k]==v
 assert len(rows(ib))==len(rows(ob))==2750
 assert sha(qb)=='0c4b9660151448fdb03b328e3fa41d0e98e679d0233759f651e90eae3a5a0e96'
 assert sha(wb)=='eb75fa865feab6e3017f6d93938fb71ff2740870b618d513cafa86f20382dc28'
 assert sha(ib)=='76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477'
 assert sha(ob)=='465ed8e338c7d32ce3c460960d8637855c65d7018d7f5c90db12c915a1c88654'
 identity={k:q[k] for k in IDENTITY_KEYS}
 census={'packet':'01.5','pass':'002','family':F,'authoritative_anchor':A,'family_records':1,'addresses_in_inventory_order':[ADDRESS],'records':[identity]}
 smallest=f"Provide one approved privacy-safe, claim-specific receipt for {ADDRESS} that compares the observed behavior with a defined normal-behavior baseline and returns only a redacted digest, bounded count, or boolean leak verdict; bind the receipt to the tested commit and effective configuration, include the comparison method and PASS/FAIL verdict, and make it independently verifiable without exposing private values, for: {q['preserved_claim']}"
 remaining={**q,'family':F,'family_result':'REMAIN_QUEUED','family_inspection_status':'NO_APPROVED_PRIVACY_SAFE_CLAIM_SPECIFIC_RECEIPT','direct_decision_supported':False,'privacy_safe_receipts_reviewed':0,'private_values_exposed':False,'smallest_exact_remaining_proof':smallest,'prior_state_preserved':True}
 coverage={
  'packet':'01.5','pass':'002','family':F,'authoritative_anchor':A,
  'family_records':1,'decided_records':0,'remaining_queued_records':1,'unknown_hold_created':0,
  'complete_nonduplicated_coverage':True,'direct_decision_gate_matches':0,
  'privacy_safe_receipts_reviewed':0,'private_values_exposed':False,
  'queue_sha256':sha(qb),'window_sha256':sha(wb),
  'source_inventory_sha256':sha(ib),'source_inventory_count':2750,'source_inventory_unchanged':True,
  'pass_002_overlay_sha256':sha(ob),'pass_002_overlay_count':2750,'pass_002_overlay_unchanged':True,
  'records_outside_family_unchanged':True,'evidence_reacquired':False,'other_evidence_families_processed':False,
  'application_behavior_modified':False,'configuration_modified':False,'dependencies_modified':False,
  'deployment_modified':False,'runtime_state_modified':False,'routing_assignments':0,'destination_assignments':0,
  'grouping_assignments':0,'source_records_removed_or_closed':0,'implementation_actions':0,'packet_04_actions':0
 }
 wj(CENSUS,census);wl(DEC,[]);wl(REM,[remaining]);wj(COV,coverage);STAT.write_text(status())
 print(json.dumps({'status':'BUILT','family_records':1,'decisions':0,'remaining_queue':1,'private_values_exposed':False},indent=2))

if __name__=='__main__':main()
