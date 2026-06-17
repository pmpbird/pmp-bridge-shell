#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

R=Path(__file__).resolve().parents[1]
A='2831e328b241693f1e669bb833753d03753ac838'
F='CROSS_SOURCE_CONFLICT'
ADDRESSES=['P01.5::P003::REL-006', 'P01.5::P003::REL-008', 'P01.5::P004::PERF-006', 'P01.5::P005::RET-004']
QUEUE='audit/applicability/Packet_01.5_Scalable_Pass_002_Evidence_Queue_v1.jsonl'
WINDOW='audit/applicability/Packet_01.5_Scalable_Pass_002_Window_v1.json'
INVENTORY='audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl'
OVERLAY='audit/routing-inventory/Packet_01.5_Applicability_Inventory_v11_Pass_002.jsonl'
CURRENT_RECEIPT='audit/Packet_01.5_Pass_002_Current_Runtime_Family_Independent_Verification_v1.json'
PRIVATE_RECEIPT='audit/Packet_01.5_Pass_002_Private_Uncaptured_Family_Independent_Verification_v1.json'
DEPLOY_RECEIPT='audit/Packet_01.5_Pass_002_Deployment_Live_Family_Independent_Verification_v1.json'
DEPENDENCY_RECEIPT='audit/Packet_01.5_Pass_002_Dependency_Platform_Family_Independent_Verification_v1.json'
CENSUS=R/'audit/Packet_01.5_Pass_002_Cross_Source_Conflict_Family_Census_v1.json'
DEC=R/'audit/applicability/Packet_01.5_Pass_002_Cross_Source_Conflict_Family_Decisions_v1.jsonl'
REM=R/'audit/applicability/Packet_01.5_Pass_002_Cross_Source_Conflict_Family_Remaining_Queue_v1.jsonl'
COV=R/'audit/Packet_01.5_Pass_002_Cross_Source_Conflict_Family_Coverage_v1.json'
STAT=R/'audit/Packet_01.5_Pass_002_Cross_Source_Conflict_Family_Status_v1.md'

IDENTITY_KEYS=('composite_address','inventory_position','source_record_ordinal','original_identifier','preserved_claim','source_path','source_pass','source_set','source_file_hash','source_envelope_hash','source_block_hash','queue_id','evidence_domain','prior_applicability_state','prior_applicability_decision_hash','state_preservation_rule')
EXPECTED={'P01.5::P003::REL-006': {'inventory_position': 157, 'source_record_ordinal': 5, 'original_identifier': 'REL-006', 'preserved_claim': 'last-write-wins data loss, duplicated work, or contradictory receipts.', 'source_path': 'audit/Packet_01.5_Discovery_Pass_03_Reliability_Recovery_and_Platform_v1.md', 'source_pass': 3, 'source_set': 'PROVISIONAL', 'source_file_hash': '55c2ddb82b56bb6d2ad3a9f531aa5d4c06ba7d12587b63db6a33ab8a25914102', 'source_envelope_hash': 'a915c54a58268fd1d16e9c600ad3f105b2a02ab63b513f99192162c98333007f', 'source_block_hash': 'd11b4f188b660053fdd6b08d8e178628dac06c08c0765ca408e64b86a9fd211a', 'queue_id': 'SP002-CROSS_SOURCE_CONFLICT', 'prior_applicability_state': 'UNCLASSIFIED', 'prior_applicability_decision_hash': None}, 'P01.5::P003::REL-008': {'inventory_position': 159, 'source_record_ordinal': 7, 'original_identifier': 'REL-008', 'preserved_claim': 'duplication, repeated external actions, or conflicting project state.', 'source_path': 'audit/Packet_01.5_Discovery_Pass_03_Reliability_Recovery_and_Platform_v1.md', 'source_pass': 3, 'source_set': 'PROVISIONAL', 'source_file_hash': '55c2ddb82b56bb6d2ad3a9f531aa5d4c06ba7d12587b63db6a33ab8a25914102', 'source_envelope_hash': '7ba4132caba7cebea863072e34ea497389ee59a41043ffddd2b57ab11d1a0458', 'source_block_hash': 'd87813e65f1c0635a25509cafd6fbf5eafc8609a9303d85a5b0a8a2aee49665f', 'queue_id': 'SP002-CROSS_SOURCE_CONFLICT', 'prior_applicability_state': 'UNCLASSIFIED', 'prior_applicability_decision_hash': None}, 'P01.5::P004::PERF-006': {'inventory_position': 179, 'source_record_ordinal': 6, 'original_identifier': 'PERF-006', 'preserved_claim': 'unfinished work, missing acknowledgement, duplicated retries, or inconsistent state.', 'source_path': 'audit/Packet_01.5_Discovery_Pass_04_Performance_Observability_Accessibility_and_Metrics_v1.md', 'source_pass': 4, 'source_set': 'PROVISIONAL', 'source_file_hash': 'dea3d33cc02124c99bf95698010667c948cda094fabc3bba86e016232aa5d764', 'source_envelope_hash': 'a38ae6422a7317af5f4b2020f8541b39368eb477343b01057e214ab197ef1d32', 'source_block_hash': 'df351e0444a0f05a4c93cf49a8b1d880b65c0554e0c0abfcdf08b1bd59438d41', 'queue_id': 'SP002-CROSS_SOURCE_CONFLICT', 'prior_applicability_state': 'UNCLASSIFIED', 'prior_applicability_decision_hash': None}, 'P01.5::P005::RET-004': {'inventory_position': 233, 'source_record_ordinal': 28, 'original_identifier': 'RET-004', 'preserved_claim': 'inconsistent deletion, unnecessary exposure, or missing proof.', 'source_path': 'audit/Packet_01.5_Discovery_Pass_05_Governance_Audit_Retention_and_Succession_v1.md', 'source_pass': 5, 'source_set': 'PROVISIONAL', 'source_file_hash': 'fd14c3e585bc88006628b1310905f64c9f26814c402d8ea30926ae7d8b8acb0f', 'source_envelope_hash': '80b3fcef2ee81c34e7fd6e8535ca225ee11161d407e4743ef5190a0fd019bac8', 'source_block_hash': '1ee9ea192acb0507873d7fb885f3be878c872b1045ab74a59af6bbc8379ba91f', 'queue_id': 'SP002-CROSS_SOURCE_CONFLICT', 'prior_applicability_state': 'UNCLASSIFIED', 'prior_applicability_decision_hash': None}}
PROOFS={'P01.5::P003::REL-006': "Provide one current, independently verifiable cross-source adjudication receipt bound to P01.5::P003::REL-006 that enumerates every conflicting state or receipt source, records immutable content hashes and effective dates, documents each source's authority status and the governing precedence rule, and executes a bounded concurrent-write and reconciliation test with PASS/FAIL verdicts proving or disproving the complete preserved claim: last-write-wins data loss, duplicated work, or contradictory receipts.", 'P01.5::P003::REL-008': 'Provide one current, independently verifiable cross-source adjudication receipt bound to P01.5::P003::REL-008 that enumerates every source capable of initiating or recording the action and project state, records immutable hashes and effective dates, documents authority and precedence, and executes a bounded duplicate-action and state-reconciliation test with PASS/FAIL verdicts proving or disproving the complete preserved claim: duplication, repeated external actions, or conflicting project state.', 'P01.5::P004::PERF-006': 'Provide one current, independently verifiable cross-source adjudication receipt bound to P01.5::P004::PERF-006 that enumerates every progress, acknowledgement, retry, and completion-state source, records immutable hashes and effective dates, documents authority and precedence, and executes a bounded interruption, acknowledgement-loss, and retry-reconciliation test with PASS/FAIL verdicts proving or disproving the complete preserved claim: unfinished work, missing acknowledgement, duplicated retries, or inconsistent state.', 'P01.5::P005::RET-004': 'Provide one current, independently verifiable cross-source adjudication receipt bound to P01.5::P005::RET-004 that enumerates every deletion, retention, backup, audit, and policy source, records immutable hashes and effective dates, documents authority and precedence, and executes a bounded delete, retain, restore, and proof-availability test with PASS/FAIL verdicts proving or disproving the complete preserved claim: inconsistent deletion, unnecessary exposure, or missing proof.'}

def git(*args):
 p=subprocess.run(['git',*args],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
 return p.decode(errors='replace').strip()
def show(path):
 return subprocess.run(['git','show',f'{A}:{path}'],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
def rows(data): return [json.loads(x) for x in data.decode().splitlines() if x.strip()]
def sha(data): return hashlib.sha256(data).hexdigest()
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def wj(path,value): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def wl(path,values): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(''.join(canonical(x)+'\n' for x in values))
def status():
 return f"""# Packet 01.5 Pass 002 — Cross-Source Conflict Family v1

STATUS: BUILT — PENDING INDEPENDENT VERIFICATION

- Authoritative anchor: `{A}`
- Permanent addresses: `{ADDRESSES[0]}`, `{ADDRESSES[1]}`, `{ADDRESSES[2]}`, `{ADDRESSES[3]}`
- Family records: 4
- Direct decisions: 0
- Exact remaining queues: 4
- Automatic `UNKNOWN — HOLD`: 0
- Conflict-adjudication receipts reviewed: 0
- Conflicting source sets identified: 0
- Authority statuses verified: no
- Precedence rules verified: no
- Current authoritative source established: no
- Immutable inventory: 2,750 records unchanged
- Pass 002 v11 overlay: 2,750 records unchanged
- Previously merged family artifacts: unchanged
- Pass 002 reconciliation if merged: 37 processed + 85 remaining = 122

No current claim-specific conflict-adjudication receipt was available. All four prior `UNCLASSIFIED` states remain preserved, and all four records remain queued for the smallest exact adjudication proof required.

No application behavior, configuration, dependencies, deployment, runtime state, routing, destinations, grouping, source-record closure, implementation, Pass 002 consolidation, or Packet 04 work occurred.
"""

def main():
 git('cat-file','-e',f'{A}^{{commit}}')
 qb,wb,ib,ob=show(QUEUE),show(WINDOW),show(INVENTORY),show(OVERLAY)
 queue=rows(qb)
 selected=sorted((x for x in queue if x.get('evidence_domain')==F),key=lambda x:x['inventory_position'])
 assert len(queue)==122
 assert [x['composite_address'] for x in selected]==ADDRESSES
 for q in selected:
  for k,v in EXPECTED[q['composite_address']].items(): assert q[k]==v
  assert q['evidence_domain']==F
  assert q['state_preservation_rule']=='PRESERVE_CURRENT_STATE_UNTIL_DIRECT_MERGED_EVIDENCE_SUPPORTS_A_DECISION'
 assert len(rows(ib))==len(rows(ob))==2750
 assert sha(qb)=='0c4b9660151448fdb03b328e3fa41d0e98e679d0233759f651e90eae3a5a0e96'
 assert sha(wb)=='eb75fa865feab6e3017f6d93938fb71ff2740870b618d513cafa86f20382dc28'
 assert sha(ib)=='76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477'
 assert sha(ob)=='465ed8e338c7d32ce3c460960d8637855c65d7018d7f5c90db12c915a1c88654'
 assert git('rev-parse',f'{A}:{CURRENT_RECEIPT}')=='5942c78a331d078b11364f46313079df3d9e887f'
 assert git('rev-parse',f'{A}:{PRIVATE_RECEIPT}')=='92045d7fa63839582ec518066033d58fede2ed8c'
 assert git('rev-parse',f'{A}:{DEPLOY_RECEIPT}')=='84d580215ee70c3c1e6b0b5a2d606c0c5d690eac'
 assert git('rev-parse',f'{A}:{DEPENDENCY_RECEIPT}')=='7ccb9a57451e80ced1a88de47406e92b7dc0b486'
 census={'packet':'01.5','pass':'002','family':F,'authoritative_anchor':A,'family_records':4,'addresses_in_inventory_order':ADDRESSES,'records':[{k:q[k] for k in IDENTITY_KEYS} for q in selected]}
 remaining=[]
 for q in selected:
  remaining.append({**q,'family':F,'family_result':'REMAIN_QUEUED','family_inspection_status':'NO_CURRENT_CLAIM_SPECIFIC_CONFLICT_ADJUDICATION_RECEIPT','direct_decision_supported':False,'conflict_adjudication_receipts_reviewed':0,'conflicting_sources_identified':0,'authority_statuses_verified':False,'precedence_rules_verified':False,'current_authoritative_source_established':False,'smallest_exact_remaining_proof':PROOFS[q['composite_address']],'prior_state_preserved':True})
 coverage={
  'packet':'01.5','pass':'002','family':F,'authoritative_anchor':A,
  'family_records':4,'decided_records':0,'remaining_queued_records':4,'unknown_hold_created':0,
  'complete_nonduplicated_coverage':True,'direct_decision_gate_matches':0,
  'conflict_adjudication_receipts_reviewed':0,'conflicting_sources_identified':0,
  'authority_statuses_verified':False,'precedence_rules_verified':False,'current_authoritative_source_established':False,
  'pass_002_total_records':122,'previously_processed_records':33,'family_records_accounted':4,
  'processed_records_if_merged':37,'remaining_unprocessed_records':85,'pass_002_reconciliation_exact':True,
  'queue_sha256':sha(qb),'window_sha256':sha(wb),
  'source_inventory_sha256':sha(ib),'source_inventory_count':2750,'source_inventory_unchanged':True,
  'pass_002_overlay_sha256':sha(ob),'pass_002_overlay_count':2750,'pass_002_overlay_unchanged':True,
  'current_runtime_family_receipt_blob_sha':'5942c78a331d078b11364f46313079df3d9e887f',
  'private_uncaptured_family_receipt_blob_sha':'92045d7fa63839582ec518066033d58fede2ed8c',
  'deployment_live_family_receipt_blob_sha':'84d580215ee70c3c1e6b0b5a2d606c0c5d690eac',
  'dependency_platform_family_receipt_blob_sha':'7ccb9a57451e80ced1a88de47406e92b7dc0b486',
  'previously_merged_family_artifacts_unchanged':True,'records_outside_family_unchanged':True,
  'evidence_reacquired':False,'other_evidence_families_processed':False,
  'application_behavior_modified':False,'configuration_modified':False,'dependencies_modified':False,
  'deployment_modified':False,'runtime_state_modified':False,'routing_assignments':0,'destination_assignments':0,
  'grouping_assignments':0,'source_records_removed_or_closed':0,'implementation_actions':0,'packet_04_actions':0
 }
 wj(CENSUS,census); wl(DEC,[]); wl(REM,remaining); wj(COV,coverage); STAT.write_text(status())
 print(json.dumps({'status':'BUILT','family_records':4,'decisions':0,'remaining_queue':4,'conflict_adjudication_receipts_reviewed':0},indent=2))

if __name__=='__main__': main()
