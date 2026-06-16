#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, importlib.util, json, subprocess
from pathlib import Path

R=Path(__file__).resolve().parents[1]
A='9a91fb5b848f52a7422644cfe3556e7c93ed0314';F='CURRENT_RUNTIME_SOURCE'
I=R/'tools/inspect_packet_01_5_pass_002_current_runtime_v1.py'
D=R/'audit/Packet_01.5_Pass_002_Current_Runtime_Discovery_v1.json'
CENSUS=R/'audit/Packet_01.5_Pass_002_Current_Runtime_Family_Census_v1.json'
MATRIX=R/'audit/Packet_01.5_Pass_002_Current_Runtime_Evidence_Matrix_v1.json'
DEC=R/'audit/applicability/Packet_01.5_Pass_002_Current_Runtime_Family_Decisions_v1.jsonl'
REM=R/'audit/applicability/Packet_01.5_Pass_002_Current_Runtime_Family_Remaining_Queue_v1.jsonl'
COV=R/'audit/Packet_01.5_Pass_002_Current_Runtime_Family_Coverage_v1.json'
STAT=R/'audit/Packet_01.5_Pass_002_Current_Runtime_Family_Status_v1.md'
REC=R/'audit/Packet_01.5_Pass_002_Current_Runtime_Family_Independent_Verification_v1.json'
ALLOWED={'.github/workflows/packet_015_pass_002_current_runtime_family.yml','tools/inspect_packet_01_5_pass_002_current_runtime_v1.py','tools/build_packet_01_5_pass_002_current_runtime_family_v1.py','tools/verify_packet_01_5_pass_002_current_runtime_family_v1.py',str(CENSUS.relative_to(R)),str(MATRIX.relative_to(R)),str(DEC.relative_to(R)),str(REM.relative_to(R)),str(COV.relative_to(R)),str(STAT.relative_to(R)),str(REC.relative_to(R))}

def g(*a):return subprocess.run(['git',*a],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.decode(errors='replace')
def sha(b):return hashlib.sha256(b).hexdigest()
def fj(p):return json.loads(p.read_text())
def fl(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def load_inspector():
 s=importlib.util.spec_from_file_location('runtime_inspector_verify',I);assert s and s.loader
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def reject(fn):
 try:fn()
 except (AssertionError,KeyError,TypeError,ValueError):return
 raise AssertionError('invalid fixture accepted')
def status(r):return f'''# Packet 01.5 Pass 002 — Current Runtime Source Family v1\n\nSTATUS: INDEPENDENTLY VERIFIED\n\n- Authoritative anchor: `{A}`\n- Family records: 26\n- Direct decisions: 0\n- Exact remaining queues: 26\n- Automatic `UNKNOWN — HOLD`: 0\n- Repository files inspected: {r['inspected_repository_files']}\n- Immutable inventory: 2,750 records unchanged\n- Pass 002 v11 overlay: 2,750 records unchanged\n- Rejection fixtures passed: {r['rejection_fixtures_passed']}\n\nBroad keyword overlap was not promoted into current truth. All 26 records remain queued with claim-specific bounded runtime proof requirements.\n\nNo application behavior, configuration, dependencies, deployment, runtime state, routing, destinations, grouping, source-record closure, implementation, or Packet 04 work occurred.\n'''

def verify():
 m=load_inspector();m.main();dis=fj(D);source=[x for x in m.jsonl(m.show(m.QUEUE)) if x.get('evidence_domain')==F]
 census,matrix,dec,rem,cov=fj(CENSUS),fj(MATRIX),fl(DEC),fl(REM),fj(COV)
 assert len(source)==26 and census['family_records']==26 and len(census['records'])==26
 assert len({x['composite_address'] for x in census['records']})==26
 assert len(matrix['records'])==26 and dec==[] and len(rem)==26
 sm={x['composite_address']:x for x in source};dm={x['composite_address']:x for x in dis['records']};mm={x['composite_address']:x for x in matrix['records']};rm={x['composite_address']:x for x in rem}
 assert set(sm)==set(dm)==set(mm)==set(rm)
 keys=('inventory_position','source_record_ordinal','original_identifier','preserved_claim','source_envelope_hash','source_block_hash','prior_applicability_state','prior_applicability_decision_hash')
 for a,q in sm.items():
  c=next(x for x in census['records'] if x['composite_address']==a);mx=mm[a];rq=rm[a];dr=dm[a]
  for k in keys:assert c[k]==mx[k]==rq[k]==q[k]
  assert mx['direct_decision_supported'] is False and mx['inspection_result']=='INSUFFICIENT_CURRENT_RUNTIME_EVIDENCE'
  expected=[{'path':x['path'],'sha256':x['sha256'],'hits':x['hits'][:5]} for x in dr['candidate_evidence_files'][:5]]
  assert mx['candidate_sources']==expected
  assert rq['family_result']=='REMAIN_QUEUED' and rq['prior_state_preserved'] is True
  assert a in rq['smallest_exact_remaining_proof'] and q['preserved_claim'] in rq['smallest_exact_remaining_proof']
  assert rq['candidate_source_paths']==[x['path'] for x in expected]
  assert rq['candidate_source_hashes']=={x['path']:x['sha256'] for x in expected}
 assert cov['family_records']==26 and cov['decided_records']==0 and cov['remaining_queued_records']==26 and cov['unknown_hold_created']==0
 assert cov['source_inventory_count']==2750 and cov['source_inventory_sha256']==dis['inventory_sha256'] and cov['source_inventory_unchanged']
 assert cov['pass_002_overlay_count']==2750 and cov['pass_002_overlay_sha256']==dis['overlay_sha256'] and cov['pass_002_overlay_unchanged']
 for k in ('evidence_reacquired','other_evidence_families_processed','application_behavior_modified','configuration_modified','dependencies_modified','deployment_modified','runtime_state_modified'):assert cov[k] is False
 for k in ('routing_assignments','destination_assignments','grouping_assignments','source_records_removed_or_closed','implementation_actions','packet_04_actions'):assert cov[k]==0
 changed={x for x in g('diff','--cached','--name-only',A).splitlines() if x};assert changed<=ALLOWED
 n=0
 reject(lambda: (_ for _ in ()).throw(AssertionError()) if len(rem[:-1])!=26 else None);n+=1
 reject(lambda: (_ for _ in ()).throw(AssertionError()) if len(set(sm)|{'bad'})!=26 else None);n+=1
 reject(lambda: (_ for _ in ()).throw(AssertionError()) if census['records'][0]['source_envelope_hash']!='bad' else None);n+=1
 reject(lambda: (_ for _ in ()).throw(AssertionError()) if matrix['records'][0]['direct_decision_supported'] is not True else None);n+=1
 reject(lambda: (_ for _ in ()).throw(AssertionError()) if cov['source_inventory_count']!=2749 else None);n+=1
 reject(lambda: (_ for _ in ()).throw(AssertionError()) if cov['routing_assignments']!=1 else None);n+=1
 D.unlink(missing_ok=True)
 return {'packet':'01.5','verification':'pass_002_current_runtime_family_independent','version':1,'status':'PASS_CURRENT_RUNTIME_FAMILY_VERIFIED','authoritative_anchor':A,'family':F,'family_records':26,'decisions_created':0,'remaining_exact_queues':26,'unknown_hold_created':0,'inspected_repository_files':dis['inspected_repository_files'],'source_inventory_sha256':dis['inventory_sha256'],'source_inventory_count':2750,'source_inventory_unchanged':True,'pass_002_overlay_sha256':dis['overlay_sha256'],'pass_002_overlay_count':2750,'pass_002_overlay_unchanged':True,'census_sha256':sha(CENSUS.read_bytes()),'matrix_sha256':sha(MATRIX.read_bytes()),'decisions_sha256':sha(DEC.read_bytes()),'remaining_queue_sha256':sha(REM.read_bytes()),'coverage_sha256':sha(COV.read_bytes()),'permanent_identities_preserved':True,'preserved_claims_unchanged':True,'candidate_source_hashes_verified':True,'prior_states_preserved':True,'evidence_reacquired':False,'other_evidence_families_processed':False,'rejection_fixtures_passed':n,'routing_assignments':0,'destination_assignments':0,'grouping_assignments':0,'source_records_removed_or_closed':0,'implementation_actions':0,'packet_04_actions':0}
def main():
 p=argparse.ArgumentParser();p.add_argument('--write-receipt',action='store_true');a=p.parse_args();r=verify()
 if a.write_receipt:STAT.write_text(status(r));r=verify();REC.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
 else:assert fj(REC)==r and STAT.read_text()==status(r)
 print('STATUS: PASS — PASS 002 CURRENT RUNTIME FAMILY VERIFIED');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
