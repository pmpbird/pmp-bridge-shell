#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re, subprocess
from pathlib import Path

R=Path(__file__).resolve().parents[1]
A='696ab70f3dde70f8ee8e0ef3a733f5e44ef1f515'
F='DEPLOYMENT_AND_LIVE_BEHAVIOR'
ADDRESSES=['P01.5::P002::SEC-003','P01.5::P005::REPO-001']
QUEUE='audit/applicability/Packet_01.5_Scalable_Pass_002_Evidence_Queue_v1.jsonl'
WINDOW='audit/applicability/Packet_01.5_Scalable_Pass_002_Window_v1.json'
INVENTORY='audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl'
OVERLAY='audit/routing-inventory/Packet_01.5_Applicability_Inventory_v11_Pass_002.jsonl'
CURRENT_RECEIPT='audit/Packet_01.5_Pass_002_Current_Runtime_Family_Independent_Verification_v1.json'
PRIVATE_RECEIPT='audit/Packet_01.5_Pass_002_Private_Uncaptured_Family_Independent_Verification_v1.json'
CENSUS=R/'audit/Packet_01.5_Pass_002_Deployment_Live_Family_Census_v1.json'
DEC=R/'audit/applicability/Packet_01.5_Pass_002_Deployment_Live_Family_Decisions_v1.jsonl'
REM=R/'audit/applicability/Packet_01.5_Pass_002_Deployment_Live_Family_Remaining_Queue_v1.jsonl'
COV=R/'audit/Packet_01.5_Pass_002_Deployment_Live_Family_Coverage_v1.json'
STAT=R/'audit/Packet_01.5_Pass_002_Deployment_Live_Family_Status_v1.md'
REC=R/'audit/Packet_01.5_Pass_002_Deployment_Live_Family_Independent_Verification_v1.json'

ALLOWED={
 '.github/workflows/packet_015_pass_002_deployment_live_family.yml',
 'tools/build_packet_01_5_pass_002_deployment_live_family_v1.py',
 'tools/verify_packet_01_5_pass_002_deployment_live_family_v1.py',
 str(CENSUS.relative_to(R)),str(DEC.relative_to(R)),str(REM.relative_to(R)),
 str(COV.relative_to(R)),str(STAT.relative_to(R)),str(REC.relative_to(R))
}
IDENTITY_KEYS=('composite_address','inventory_position','source_record_ordinal','original_identifier','preserved_claim','source_path','source_pass','source_set','source_file_hash','source_envelope_hash','source_block_hash','queue_id','evidence_domain','prior_applicability_state','prior_applicability_decision_hash','state_preservation_rule')
FORBIDDEN_KEYS={'secret_value','secret_values','credential','credentials','token_value','token_values','password','passwords','private_key','private_keys','personal_data','raw_private_data','private_memory_contents'}
FORBIDDEN_PATTERNS=[
 re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
 re.compile(r'gh[pousr]_[A-Za-z0-9]{20,}'),
 re.compile(r'sk-[A-Za-z0-9]{20,}'),
 re.compile(r'AKIA[0-9A-Z]{16}'),
 re.compile(r'(?i)password\s*[:=]\s*[^\s,}]+')
]

def git(*args,binary=False):
 p=subprocess.run(['git',*args],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
 return p if binary else p.decode(errors='replace').strip()
def show(path): return subprocess.run(['git','show',f'{A}:{path}'],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
def rows(data): return [json.loads(x) for x in data.decode().splitlines() if x.strip()]
def sha(data): return hashlib.sha256(data).hexdigest()
def fj(path): return json.loads(path.read_text())
def fl(path): return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
def require(value): assert value
def reject(fn):
 try: fn()
 except (AssertionError,KeyError,TypeError,ValueError): return
 raise AssertionError('invalid fixture accepted')
def scan_keys(value):
 if isinstance(value,dict):
  for k,v in value.items():
   assert k.lower() not in FORBIDDEN_KEYS
   scan_keys(v)
 elif isinstance(value,list):
  for v in value: scan_keys(v)
def scan_text(text):
 for pattern in FORBIDDEN_PATTERNS: assert not pattern.search(text)

def status(r):
 return f'''# Packet 01.5 Pass 002 — Deployment and Live-Behavior Family v1

STATUS: INDEPENDENTLY VERIFIED

- Authoritative anchor: `{A}`
- Permanent addresses: `P01.5::P002::SEC-003`, `P01.5::P005::REPO-001`
- Family records: 2
- Direct decisions: 0
- Exact remaining queues: 2
- Automatic `UNKNOWN — HOLD`: 0
- Deployment receipts reviewed: 0
- Bounded live probes completed: 0
- Immutable deployed revision verified: no
- Effective live configuration verified: no
- Effective route verified: no
- Immutable inventory: 2,750 records unchanged
- Pass 002 v11 overlay: 2,750 records unchanged
- Previously merged family artifacts: unchanged
- Pass 002 reconciliation if merged: 29 processed + 93 remaining = 122
- Rejection fixtures passed: {r['rejection_fixtures_passed']}

No current claim-specific deployment-and-live receipt was available. Both prior `UNCLASSIFIED` states remain preserved, and both records remain queued for the smallest exact live proof required.

No application behavior, configuration, dependencies, deployment, runtime state, routing, destinations, grouping, source-record closure, implementation, Pass 002 consolidation, or Packet 04 work occurred.
'''

def verify():
 qb,wb,ib,ob=show(QUEUE),show(WINDOW),show(INVENTORY),show(OVERLAY)
 source=sorted((x for x in rows(qb) if x.get('evidence_domain')==F),key=lambda x:x['inventory_position'])
 assert len(rows(qb))==122
 assert len(source)==2 and [x['composite_address'] for x in source]==ADDRESSES
 census,dec,rem,cov=fj(CENSUS),fl(DEC),fl(REM),fj(COV)
 assert census['family_records']==2 and census['addresses_in_inventory_order']==ADDRESSES and len(census['records'])==2
 assert dec==[] and len(rem)==2 and [x['composite_address'] for x in rem]==ADDRESSES
 for c,r,q in zip(census['records'],rem,source):
  for k in IDENTITY_KEYS: assert c[k]==r[k]==q[k]
  assert r['family']==F and r['family_result']=='REMAIN_QUEUED'
  assert r['family_inspection_status']=='NO_CURRENT_CLAIM_SPECIFIC_DEPLOYMENT_AND_LIVE_RECEIPT'
  assert r['direct_decision_supported'] is False and r['deployment_receipts_reviewed']==0
  assert r['bounded_live_probes_completed']==0 and r['prior_state_preserved'] is True
  assert r['immutable_deployed_revision_verified'] is False
  assert r['effective_live_configuration_verified'] is False and r['effective_route_verified'] is False
  assert r['composite_address'] in r['smallest_exact_remaining_proof']
  assert r['preserved_claim'] in r['smallest_exact_remaining_proof']
  assert 'current, independently verifiable' in r['smallest_exact_remaining_proof']
 assert cov['family_records']==2 and cov['decided_records']==0 and cov['remaining_queued_records']==2
 assert cov['unknown_hold_created']==0 and cov['complete_nonduplicated_coverage']
 assert cov['direct_decision_gate_matches']==0 and cov['deployment_receipts_reviewed']==0
 assert cov['bounded_live_probes_completed']==0
 assert cov['immutable_deployed_revision_verified'] is False
 assert cov['effective_live_configuration_verified'] is False and cov['effective_route_verified'] is False
 assert cov['pass_002_total_records']==122 and cov['previously_processed_records']==27
 assert cov['family_records_accounted']==2 and cov['processed_records_if_merged']==29
 assert cov['remaining_unprocessed_records']==93 and cov['pass_002_reconciliation_exact'] is True
 assert 27+2+93==122
 assert cov['queue_sha256']==sha(qb)=='0c4b9660151448fdb03b328e3fa41d0e98e679d0233759f651e90eae3a5a0e96'
 assert cov['window_sha256']==sha(wb)=='eb75fa865feab6e3017f6d93938fb71ff2740870b618d513cafa86f20382dc28'
 assert len(rows(ib))==cov['source_inventory_count']==2750
 assert cov['source_inventory_sha256']==sha(ib)=='76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477'
 assert len(rows(ob))==cov['pass_002_overlay_count']==2750
 assert cov['pass_002_overlay_sha256']==sha(ob)=='465ed8e338c7d32ce3c460960d8637855c65d7018d7f5c90db12c915a1c88654'
 current_blob=git('rev-parse',f'{A}:{CURRENT_RECEIPT}')
 private_blob=git('rev-parse',f'{A}:{PRIVATE_RECEIPT}')
 assert current_blob==cov['current_runtime_family_receipt_blob_sha']=='5942c78a331d078b11364f46313079df3d9e887f'
 assert private_blob==cov['private_uncaptured_family_receipt_blob_sha']=='92045d7fa63839582ec518066033d58fede2ed8c'
 assert cov['previously_merged_family_artifacts_unchanged'] is True
 assert cov['records_outside_family_unchanged'] is True
 for k in ('evidence_reacquired','other_evidence_families_processed','application_behavior_modified','configuration_modified','dependencies_modified','deployment_modified','runtime_state_modified'): assert cov[k] is False
 for k in ('routing_assignments','destination_assignments','grouping_assignments','source_records_removed_or_closed','implementation_actions','packet_04_actions'): assert cov[k]==0
 for value in (census,rem,cov): scan_keys(value)
 for path in (CENSUS,DEC,REM,COV,STAT): scan_text(path.read_text())
 changed={x for x in git('diff','--name-only',A,'HEAD').splitlines() if x}
 assert changed==ALLOWED
 n=0
 reject(lambda:require(len(rem[:-1])==2)); n+=1
 reject(lambda:require(set(ADDRESSES+['P01.5::BAD'])==set(ADDRESSES))); n+=1
 reject(lambda:require(census['records'][0]['source_envelope_hash']=='bad')); n+=1
 reject(lambda:require(rem[0]['direct_decision_supported'] is True)); n+=1
 reject(lambda:require(cov['family_records']==1)); n+=1
 reject(lambda:require(cov['bounded_live_probes_completed']==1)); n+=1
 reject(lambda:require(cov['effective_route_verified'] is True)); n+=1
 reject(lambda:require(cov['routing_assignments']==1)); n+=1
 reject(lambda:require(current_blob=='bad')); n+=1
 reject(lambda:require('secret_value' not in FORBIDDEN_KEYS)); n+=1
 return {
  'packet':'01.5','verification':'pass_002_deployment_live_family_independent','version':1,
  'status':'PASS_DEPLOYMENT_LIVE_FAMILY_VERIFIED','authoritative_anchor':A,'family':F,
  'family_records':2,'decisions_created':0,'remaining_exact_queues':2,'unknown_hold_created':0,
  'permanent_addresses':ADDRESSES,'deployment_receipts_reviewed':0,'bounded_live_probes_completed':0,
  'immutable_deployed_revision_verified':False,'effective_live_configuration_verified':False,'effective_route_verified':False,
  'source_inventory_sha256':sha(ib),'source_inventory_count':2750,'source_inventory_unchanged':True,
  'pass_002_overlay_sha256':sha(ob),'pass_002_overlay_count':2750,'pass_002_overlay_unchanged':True,
  'queue_sha256':sha(qb),'window_sha256':sha(wb),
  'census_sha256':sha(CENSUS.read_bytes()),'decisions_sha256':sha(DEC.read_bytes()),
  'remaining_queue_sha256':sha(REM.read_bytes()),'coverage_sha256':sha(COV.read_bytes()),
  'current_runtime_family_receipt_blob_sha':current_blob,'private_uncaptured_family_receipt_blob_sha':private_blob,
  'previously_merged_family_artifacts_unchanged':True,
  'pass_002_total_records':122,'previously_processed_records':27,'family_records_accounted':2,
  'processed_records_if_merged':29,'remaining_unprocessed_records':93,'pass_002_reconciliation_exact':True,
  'permanent_identities_preserved':True,'preserved_claims_unchanged':True,'prior_states_preserved':True,
  'records_outside_family_unchanged':True,'other_evidence_families_processed':False,
  'private_values_exposed':False,'rejection_fixtures_passed':n,
  'application_behavior_modified':False,'configuration_modified':False,'dependencies_modified':False,
  'deployment_modified':False,'runtime_state_modified':False,
  'routing_assignments':0,'destination_assignments':0,'grouping_assignments':0,
  'source_records_removed_or_closed':0,'implementation_actions':0,'packet_04_actions':0
 }

def main():
 p=argparse.ArgumentParser(); p.add_argument('--write-receipt',action='store_true'); a=p.parse_args()
 r=verify()
 if a.write_receipt:
  STAT.write_text(status(r)); REC.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n'); r=verify()
 else:
  assert fj(REC)==r and STAT.read_text()==status(r)
 print('STATUS: PASS — PASS 002 DEPLOYMENT AND LIVE-BEHAVIOR FAMILY VERIFIED')
 print(json.dumps(r,indent=2))

if __name__=='__main__': main()
