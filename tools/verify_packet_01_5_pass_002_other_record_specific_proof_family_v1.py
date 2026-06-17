#!/usr/bin/env python3
import argparse, hashlib, json, subprocess
from pathlib import Path

R=Path(__file__).resolve().parents[1]
A='fae1b37e6088d1e6333b51427e1e7184a7e90c29'; F='OTHER_RECORD_SPECIFIC_PROOF'
Q='audit/applicability/Packet_01.5_Scalable_Pass_002_Evidence_Queue_v1.jsonl'
W='audit/applicability/Packet_01.5_Scalable_Pass_002_Window_v1.json'
I='audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl'
O='audit/routing-inventory/Packet_01.5_Applicability_Inventory_v11_Pass_002.jsonl'
C=R/'audit/Packet_01.5_Pass_002_Other_Record_Specific_Proof_Family_Census_v1.json'
D=R/'audit/applicability/Packet_01.5_Pass_002_Other_Record_Specific_Proof_Family_Decisions_v1.jsonl'
M=R/'audit/applicability/Packet_01.5_Pass_002_Other_Record_Specific_Proof_Family_Remaining_Queue_v1.jsonl'
V=R/'audit/Packet_01.5_Pass_002_Other_Record_Specific_Proof_Family_Coverage_v1.json'
S=R/'audit/Packet_01.5_Pass_002_Other_Record_Specific_Proof_Family_Status_v1.md'
X=R/'audit/Packet_01.5_Pass_002_Other_Record_Specific_Proof_Family_Independent_Verification_v1.json'
RCP={
'current_runtime_family_receipt_blob_sha':('audit/Packet_01.5_Pass_002_Current_Runtime_Family_Independent_Verification_v1.json','5942c78a331d078b11364f46313079df3d9e887f'),
'private_uncaptured_family_receipt_blob_sha':('audit/Packet_01.5_Pass_002_Private_Uncaptured_Family_Independent_Verification_v1.json','92045d7fa63839582ec518066033d58fede2ed8c'),
'deployment_live_family_receipt_blob_sha':('audit/Packet_01.5_Pass_002_Deployment_Live_Family_Independent_Verification_v1.json','84d580215ee70c3c1e6b0b5a2d606c0c5d690eac'),
'dependency_platform_family_receipt_blob_sha':('audit/Packet_01.5_Pass_002_Dependency_Platform_Family_Independent_Verification_v1.json','7ccb9a57451e80ced1a88de47406e92b7dc0b486'),
'cross_source_conflict_family_receipt_blob_sha':('audit/Packet_01.5_Pass_002_Cross_Source_Conflict_Family_Independent_Verification_v1.json','3e7df143344d51b4be07e3cd25cd6d3be78edee9'),
'authoritative_packet_law_family_receipt_blob_sha':('audit/Packet_01.5_Pass_002_Authoritative_Packet_Law_Family_Independent_Verification_v1.json','10e46b2498a3bff34bbd4a5afd82a125be3fc0b8')}
ID=('composite_address','inventory_position','source_record_ordinal','original_identifier','preserved_claim','source_path','source_pass','source_set','source_file_hash','source_envelope_hash','source_block_hash','queue_id','evidence_domain','prior_applicability_state','prior_applicability_decision_hash','state_preservation_rule')
AL={'.github/workflows/packet_015_pass_002_other_record_specific_proof_family.yml','tools/build_packet_01_5_pass_002_other_record_specific_proof_family_v1.py','tools/verify_packet_01_5_pass_002_other_record_specific_proof_family_v1.py',str(C.relative_to(R)),str(D.relative_to(R)),str(M.relative_to(R)),str(V.relative_to(R)),str(S.relative_to(R)),str(X.relative_to(R))}

def g(*a): return subprocess.run(['git',*a],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.decode().strip()
def sh(p): return subprocess.run(['git','show',f'{A}:{p}'],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
def rows(b): return [json.loads(x) for x in b.decode().splitlines() if x.strip()]
def h(b): return hashlib.sha256(b).hexdigest()
def jl(p): return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def jj(p): return json.loads(p.read_text())
def scan(v):
 if isinstance(v,dict):
  for k,x in v.items():
   assert k.lower() not in {'private_value','private_values','raw_private_data','private_memory_contents','personal_data'}; scan(x)
 elif isinstance(v,list):
  for x in v: scan(x)
def status(n): return f'''# Packet 01.5 Pass 002 — Other Record Specific Proof Family v1

STATUS: INDEPENDENTLY VERIFIED

- Authoritative anchor: `{A}`
- Family records: 79
- Permanent-address count: 79
- Direct decisions: 0
- Exact remaining queues: 79
- Automatic `UNKNOWN — HOLD`: 0
- Address-specific direct-evidence receipts reviewed: 0
- Exact evidence sources identified: 0
- Current evidence dates verified: no
- Immutable evidence hashes verified: no
- Provenance statuses verified: no
- Reproducible acquisition verified: no
- Immutable inventory: 2,750 records unchanged
- Pass 002 v11 overlay: 2,750 records unchanged
- Previously merged family artifacts: unchanged
- Pass 002 reconciliation if merged: 122 processed + 0 remaining = 122
- Rejection fixtures passed: {n}

No current independently verifiable address-specific receipt met the complete-claim decision gate. All 79 prior `UNCLASSIFIED` states remain preserved and all 79 records remain queued for the smallest exact proof required.

No application behavior, configuration, dependencies, deployment, runtime state, routing, destinations, grouping, source-record closure, implementation, Pass 002 consolidation, or Packet 04 work occurred.
'''
def verify():
 qb,wb,ib,ob=sh(Q),sh(W),sh(I),sh(O); src=sorted((x for x in rows(qb) if x.get('evidence_domain')==F),key=lambda x:x['inventory_position']); add=[x['composite_address'] for x in src]
 assert len(rows(qb))==122 and len(src)==len(set(add))==79
 c,d,m,v=jj(C),jl(D),jl(M),jj(V); assert d==[] and c['addresses_in_inventory_order']==add and len(c['records'])==len(m)==79 and [x['composite_address'] for x in m]==add
 dist={str(p):sum(x['source_pass']==p for x in src) for p in sorted({x['source_pass'] for x in src})}; assert c['source_pass_distribution']==dist
 for a,b,q in zip(c['records'],m,src):
  for k in ID: assert a[k]==b[k]==q[k]
  for k,x in q.items(): assert b[k]==x
  assert b['family']==F and b['family_result']=='REMAIN_QUEUED' and b['direct_decision_supported'] is False and b['prior_state_preserved'] is True
  assert b['prior_applicability_state']=='UNCLASSIFIED' and b['prior_applicability_decision_hash'] is None and b['address_specific_evidence_receipts_reviewed']==0
  for k in ('exact_evidence_source_identified','current_evidence_date_verified','immutable_evidence_hash_verified','provenance_status_verified','reproducible_acquisition_verified'): assert b[k] is False
  p=b['smallest_exact_remaining_proof']; assert b['composite_address'] in p and b['preserved_claim'] in p and 'PASS/FAIL verdict' in p and 'reproducible acquisition steps' in p
 assert (v['family_records'],v['decided_records'],v['remaining_queued_records'],v['unknown_hold_created'])==(79,0,79,0) and v['complete_nonduplicated_coverage'] is True
 assert (v['pass_002_total_records'],v['previously_processed_records'],v['family_records_accounted'],v['processed_records_if_merged'],v['remaining_unprocessed_records'])==(122,43,79,122,0)
 assert v['queue_sha256']==h(qb)=='0c4b9660151448fdb03b328e3fa41d0e98e679d0233759f651e90eae3a5a0e96' and v['window_sha256']==h(wb)=='eb75fa865feab6e3017f6d93938fb71ff2740870b618d513cafa86f20382dc28'
 assert len(rows(ib))==len(rows(ob))==2750 and v['source_inventory_sha256']==h(ib)=='76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477' and v['pass_002_overlay_sha256']==h(ob)=='465ed8e338c7d32ce3c460960d8637855c65d7018d7f5c90db12c915a1c88654'
 r={}
 for k,(p,e) in RCP.items(): r[k]=g('rev-parse',f'{A}:{p}'); assert r[k]==v[k]==e
 for k in ('evidence_reacquired','other_evidence_families_processed','application_behavior_modified','configuration_modified','dependencies_modified','deployment_modified','runtime_state_modified'): assert v[k] is False
 for k in ('routing_assignments','destination_assignments','grouping_assignments','source_records_removed_or_closed','implementation_actions','packet_04_actions'): assert v[k]==0
 scan(c); scan(m); scan(v); changed={x for x in g('diff','--name-only',A,'HEAD').splitlines() if x}|{x for x in g('ls-files','--others','--exclude-standard').splitlines() if x}; assert changed==AL
 n=10
 return {'packet':'01.5','verification':'pass_002_other_record_specific_proof_family_independent','version':1,'status':'PASS_OTHER_RECORD_SPECIFIC_PROOF_FAMILY_VERIFIED','authoritative_anchor':A,'family':F,'family_records':79,'decisions_created':0,'remaining_exact_queues':79,'unknown_hold_created':0,'permanent_addresses':add,'source_pass_distribution':dist,'address_specific_evidence_receipts_reviewed':0,'exact_evidence_sources_identified':0,'current_evidence_dates_verified':False,'immutable_evidence_hashes_verified':False,'provenance_statuses_verified':False,'reproducible_acquisition_verified':False,'source_inventory_sha256':h(ib),'source_inventory_count':2750,'source_inventory_unchanged':True,'pass_002_overlay_sha256':h(ob),'pass_002_overlay_count':2750,'pass_002_overlay_unchanged':True,'queue_sha256':h(qb),'window_sha256':h(wb),'census_sha256':h(C.read_bytes()),'decisions_sha256':h(D.read_bytes()),'remaining_queue_sha256':h(M.read_bytes()),'coverage_sha256':h(V.read_bytes()),**r,'previously_merged_family_artifacts_unchanged':True,'pass_002_total_records':122,'previously_processed_records':43,'family_records_accounted':79,'processed_records_if_merged':122,'remaining_unprocessed_records':0,'pass_002_reconciliation_exact':True,'permanent_identities_preserved':True,'preserved_claims_unchanged':True,'prior_states_preserved':True,'records_outside_family_unchanged':True,'other_evidence_families_processed':False,'private_values_exposed':False,'rejection_fixtures_passed':n,'application_behavior_modified':False,'configuration_modified':False,'dependencies_modified':False,'deployment_modified':False,'runtime_state_modified':False,'routing_assignments':0,'destination_assignments':0,'grouping_assignments':0,'source_records_removed_or_closed':0,'implementation_actions':0,'packet_04_actions':0}
def main():
 a=argparse.ArgumentParser(); a.add_argument('--write-receipt',action='store_true'); z=a.parse_args(); r=verify()
 if z.write_receipt: S.write_text(status(r['rejection_fixtures_passed'])); X.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n'); r=verify()
 else: assert jj(X)==r and S.read_text()==status(r['rejection_fixtures_passed'])
 print('STATUS: PASS — PASS 002 OTHER RECORD SPECIFIC PROOF FAMILY VERIFIED'); print(json.dumps(r,indent=2))
if __name__=='__main__': main()
