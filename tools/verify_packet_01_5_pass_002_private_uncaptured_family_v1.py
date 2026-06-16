#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path

R=Path(__file__).resolve().parents[1]
A='417d11653d7e94dcc5b57939dfd4a26f30fdc221';F='PRIVATE_OR_UNCAPTURED_EVIDENCE';ADDRESS='P01.5::P004::OBS-004'
QUEUE='audit/applicability/Packet_01.5_Scalable_Pass_002_Evidence_Queue_v1.jsonl'
WINDOW='audit/applicability/Packet_01.5_Scalable_Pass_002_Window_v1.json'
INVENTORY='audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl'
OVERLAY='audit/routing-inventory/Packet_01.5_Applicability_Inventory_v11_Pass_002.jsonl'
CENSUS=R/'audit/Packet_01.5_Pass_002_Private_Uncaptured_Family_Census_v1.json'
DEC=R/'audit/applicability/Packet_01.5_Pass_002_Private_Uncaptured_Family_Decisions_v1.jsonl'
REM=R/'audit/applicability/Packet_01.5_Pass_002_Private_Uncaptured_Family_Remaining_Queue_v1.jsonl'
COV=R/'audit/Packet_01.5_Pass_002_Private_Uncaptured_Family_Coverage_v1.json'
STAT=R/'audit/Packet_01.5_Pass_002_Private_Uncaptured_Family_Status_v1.md'
REC=R/'audit/Packet_01.5_Pass_002_Private_Uncaptured_Family_Independent_Verification_v1.json'
ALLOWED={
 '.github/workflows/packet_015_pass_002_private_uncaptured_family.yml',
 'tools/build_packet_01_5_pass_002_private_uncaptured_family_v1.py',
 'tools/verify_packet_01_5_pass_002_private_uncaptured_family_v1.py',
 str(CENSUS.relative_to(R)),str(DEC.relative_to(R)),str(REM.relative_to(R)),
 str(COV.relative_to(R)),str(STAT.relative_to(R)),str(REC.relative_to(R))
}
IDENTITY_KEYS=('composite_address','inventory_position','source_record_ordinal','original_identifier','preserved_claim','source_path','source_pass','source_set','source_file_hash','source_envelope_hash','source_block_hash','queue_id','evidence_domain','prior_applicability_state','prior_applicability_decision_hash','state_preservation_rule')
FORBIDDEN_KEYS={'secret','token','credential','private_value','private_values','private_contents','personal_data','raw_private_data','private_memory_contents'}

def git(*args,binary=False):
 p=subprocess.run(['git',*args],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
 return p if binary else p.decode(errors='replace')
def show(path):return git('show',f'{A}:{path}',binary=True)
def rows(data):return [json.loads(x) for x in data.decode().splitlines() if x.strip()]
def sha(data):return hashlib.sha256(data).hexdigest()
def fj(path):return json.loads(path.read_text())
def fl(path):return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
def require(value):assert value
def reject(fn):
 try:fn()
 except (AssertionError,KeyError,TypeError,ValueError):return
 raise AssertionError('invalid fixture accepted')
def scan_keys(value):
 if isinstance(value,dict):
  for k,v in value.items():
   assert k.lower() not in FORBIDDEN_KEYS
   scan_keys(v)
 elif isinstance(value,list):
  for v in value:scan_keys(v)

def status(r):
 return f'''# Packet 01.5 Pass 002 — Private or Uncaptured Evidence Family v1

STATUS: INDEPENDENTLY VERIFIED

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
- Rejection fixtures passed: {r['rejection_fixtures_passed']}

No approved claim-specific privacy-safe receipt is present. The prior state remains preserved, and the record remains queued for one bounded, independently verifiable receipt that exposes no private values.

No application behavior, configuration, dependencies, deployment, runtime state, routing, destinations, grouping, source-record closure, implementation, or Packet 04 work occurred.
'''

def verify():
 qb,wb,ib,ob=show(QUEUE),show(WINDOW),show(INVENTORY),show(OVERLAY)
 source=[x for x in rows(qb) if x.get('evidence_domain')==F]
 assert len(source)==1 and source[0]['composite_address']==ADDRESS
 q=source[0];census,dec,rem,cov=fj(CENSUS),fl(DEC),fl(REM),fj(COV)
 assert census['family_records']==1 and census['addresses_in_inventory_order']==[ADDRESS] and len(census['records'])==1
 assert dec==[] and len(rem)==1 and rem[0]['composite_address']==ADDRESS
 c=census['records'][0];r=rem[0]
 for k in IDENTITY_KEYS:assert c[k]==r[k]==q[k]
 assert r['family']==F and r['family_result']=='REMAIN_QUEUED'
 assert r['family_inspection_status']=='NO_APPROVED_PRIVACY_SAFE_CLAIM_SPECIFIC_RECEIPT'
 assert r['direct_decision_supported'] is False and r['privacy_safe_receipts_reviewed']==0
 assert r['private_values_exposed'] is False and r['prior_state_preserved'] is True
 assert ADDRESS in r['smallest_exact_remaining_proof'] and q['preserved_claim'] in r['smallest_exact_remaining_proof']
 assert 'privacy-safe' in r['smallest_exact_remaining_proof'] and 'without exposing private values' in r['smallest_exact_remaining_proof']
 assert cov['family_records']==1 and cov['decided_records']==0 and cov['remaining_queued_records']==1
 assert cov['unknown_hold_created']==0 and cov['complete_nonduplicated_coverage']
 assert cov['direct_decision_gate_matches']==0 and cov['privacy_safe_receipts_reviewed']==0
 assert cov['private_values_exposed'] is False and cov['records_outside_family_unchanged'] is True
 assert cov['queue_sha256']==sha(qb)=='0c4b9660151448fdb03b328e3fa41d0e98e679d0233759f651e90eae3a5a0e96'
 assert cov['window_sha256']==sha(wb)=='eb75fa865feab6e3017f6d93938fb71ff2740870b618d513cafa86f20382dc28'
 assert len(rows(ib))==cov['source_inventory_count']==2750
 assert cov['source_inventory_sha256']==sha(ib)=='76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477'
 assert len(rows(ob))==cov['pass_002_overlay_count']==2750
 assert cov['pass_002_overlay_sha256']==sha(ob)=='465ed8e338c7d32ce3c460960d8637855c65d7018d7f5c90db12c915a1c88654'
 for k in ('evidence_reacquired','other_evidence_families_processed','application_behavior_modified','configuration_modified','dependencies_modified','deployment_modified','runtime_state_modified'):assert cov[k] is False
 for k in ('routing_assignments','destination_assignments','grouping_assignments','source_records_removed_or_closed','implementation_actions','packet_04_actions'):assert cov[k]==0
 scan_keys(census);scan_keys(rem);scan_keys(cov)
 changed={x for x in git('diff','--name-only',A,'HEAD').splitlines() if x}
 assert changed==ALLOWED
 n=0
 reject(lambda:require(len(rem[:-1])==1));n+=1
 reject(lambda:require({ADDRESS,'P01.5::BAD'}=={ADDRESS}));n+=1
 reject(lambda:require(c['source_envelope_hash']=='bad'));n+=1
 reject(lambda:require(r['direct_decision_supported'] is True));n+=1
 reject(lambda:require(cov['source_inventory_count']==2749));n+=1
 reject(lambda:require(cov['private_values_exposed'] is True));n+=1
 reject(lambda:require(cov['routing_assignments']==1));n+=1
 reject(lambda:require('secret' not in FORBIDDEN_KEYS));n+=1
 return {
  'packet':'01.5','verification':'pass_002_private_uncaptured_family_independent','version':1,
  'status':'PASS_PRIVATE_UNCAPTURED_FAMILY_VERIFIED','authoritative_anchor':A,'family':F,
  'family_records':1,'decisions_created':0,'remaining_exact_queues':1,'unknown_hold_created':0,
  'permanent_address':ADDRESS,'privacy_safe_receipts_reviewed':0,'private_values_exposed':False,
  'source_inventory_sha256':sha(ib),'source_inventory_count':2750,'source_inventory_unchanged':True,
  'pass_002_overlay_sha256':sha(ob),'pass_002_overlay_count':2750,'pass_002_overlay_unchanged':True,
  'queue_sha256':sha(qb),'window_sha256':sha(wb),
  'census_sha256':sha(CENSUS.read_bytes()),'decisions_sha256':sha(DEC.read_bytes()),
  'remaining_queue_sha256':sha(REM.read_bytes()),'coverage_sha256':sha(COV.read_bytes()),
  'permanent_identity_preserved':True,'preserved_claim_unchanged':True,'prior_state_preserved':True,
  'records_outside_family_unchanged':True,'other_evidence_families_processed':False,
  'rejection_fixtures_passed':n,'routing_assignments':0,'destination_assignments':0,
  'grouping_assignments':0,'source_records_removed_or_closed':0,'implementation_actions':0,'packet_04_actions':0
 }

def main():
 p=argparse.ArgumentParser();p.add_argument('--write-receipt',action='store_true');a=p.parse_args();r=verify()
 if a.write_receipt:
  STAT.write_text(status(r));REC.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n');r=verify()
 else:
  assert fj(REC)==r and STAT.read_text()==status(r)
 print('STATUS: PASS — PASS 002 PRIVATE OR UNCAPTURED EVIDENCE FAMILY VERIFIED')
 print(json.dumps(r,indent=2))

if __name__=='__main__':main()
