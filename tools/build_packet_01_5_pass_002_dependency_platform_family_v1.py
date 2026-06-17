#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

R=Path(__file__).resolve().parents[1]
A='2e2b1647636acf44849c4a0215a15d9c760fde2e'
F='DEPENDENCY_OR_PLATFORM_STATE'
ADDRESSES=['P01.5::P002::SEC-010', 'P01.5::P002::MEM-002', 'P01.5::P004::PERF-001', 'P01.5::P006::ECO-001']
QUEUE='audit/applicability/Packet_01.5_Scalable_Pass_002_Evidence_Queue_v1.jsonl'
WINDOW='audit/applicability/Packet_01.5_Scalable_Pass_002_Window_v1.json'
INVENTORY='audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl'
OVERLAY='audit/routing-inventory/Packet_01.5_Applicability_Inventory_v11_Pass_002.jsonl'
CURRENT_RECEIPT='audit/Packet_01.5_Pass_002_Current_Runtime_Family_Independent_Verification_v1.json'
PRIVATE_RECEIPT='audit/Packet_01.5_Pass_002_Private_Uncaptured_Family_Independent_Verification_v1.json'
DEPLOY_RECEIPT='audit/Packet_01.5_Pass_002_Deployment_Live_Family_Independent_Verification_v1.json'
CENSUS=R/'audit/Packet_01.5_Pass_002_Dependency_Platform_Family_Census_v1.json'
DEC=R/'audit/applicability/Packet_01.5_Pass_002_Dependency_Platform_Family_Decisions_v1.jsonl'
REM=R/'audit/applicability/Packet_01.5_Pass_002_Dependency_Platform_Family_Remaining_Queue_v1.jsonl'
COV=R/'audit/Packet_01.5_Pass_002_Dependency_Platform_Family_Coverage_v1.json'
STAT=R/'audit/Packet_01.5_Pass_002_Dependency_Platform_Family_Status_v1.md'

IDENTITY_KEYS=('composite_address','inventory_position','source_record_ordinal','original_identifier','preserved_claim','source_path','source_pass','source_set','source_file_hash','source_envelope_hash','source_block_hash','queue_id','evidence_domain','prior_applicability_state','prior_applicability_decision_hash','state_preservation_rule')
EXPECTED={
 'P01.5::P002::SEC-010': {'inventory_position': 142, 'source_record_ordinal': 10, 'original_identifier': 'SEC-010', 'preserved_claim': 'user approves the wrong candidate, provider, or action.', 'source_path': 'audit/Packet_01.5_Discovery_Pass_02_Security_Privacy_and_Human_Risk_v1.md', 'source_pass': 2, 'source_set': 'PROVISIONAL', 'source_file_hash': '8506f61d266208458cb79ca97cbce3f8b3baa715f992c40035ef72013727410b', 'source_envelope_hash': '373442a2c054c38bb7f4cf96696da55f00495216f34334fc344f06d2eaa94d47', 'source_block_hash': 'd18e12c73f0d681d38bf06217c6aa3a9aa8c798452b19f227d73cd190def0591', 'queue_id': 'SP002-DEPENDENCY_OR_PLATFORM_STATE', 'prior_applicability_state': 'UNCLASSIFIED', 'prior_applicability_decision_hash': None},
 'P01.5::P002::MEM-002': {'inventory_position': 144, 'source_record_ordinal': 12, 'original_identifier': 'MEM-002', 'preserved_claim': 'Resident follows obsolete failure models.', 'source_path': 'audit/Packet_01.5_Discovery_Pass_02_Security_Privacy_and_Human_Risk_v1.md', 'source_pass': 2, 'source_set': 'PROVISIONAL', 'source_file_hash': '8506f61d266208458cb79ca97cbce3f8b3baa715f992c40035ef72013727410b', 'source_envelope_hash': '402a4758c587c97a12d17cb28e10ce066b0cfe75ef6060c852b6f9589636bb30', 'source_block_hash': '04b79116c11d5aeb8c3a02602987a9e647e2bbfe05f8c34a2154012404f36ea2', 'queue_id': 'SP002-DEPENDENCY_OR_PLATFORM_STATE', 'prior_applicability_state': 'UNCLASSIFIED', 'prior_applicability_decision_hash': None},
 'P01.5::P004::PERF-001': {'inventory_position': 174, 'source_record_ordinal': 1, 'original_identifier': 'PERF-001', 'preserved_claim': 'the app appears frozen, taps are lost, approval screens become unusable, and iOS may terminate the page.', 'source_path': 'audit/Packet_01.5_Discovery_Pass_04_Performance_Observability_Accessibility_and_Metrics_v1.md', 'source_pass': 4, 'source_set': 'PROVISIONAL', 'source_file_hash': 'dea3d33cc02124c99bf95698010667c948cda094fabc3bba86e016232aa5d764', 'source_envelope_hash': 'e4f6a5cb910b720256abf28fd4ed8237e52197447c0ff2881dca6c8f82fb362e', 'source_block_hash': '59e5ab9422f057f2c0f44beeeeff6bfe4f44f52a1fbbe65e51c984f5f3dac248', 'queue_id': 'SP002-DEPENDENCY_OR_PLATFORM_STATE', 'prior_applicability_state': 'UNCLASSIFIED', 'prior_applicability_decision_hash': None},
 'P01.5::P006::ECO-001': {'inventory_position': 239, 'source_record_ordinal': 1, 'original_identifier': 'ECO-001', 'preserved_claim': 'essential operation stops or the project is forced into an unplanned paid dependency.', 'source_path': 'audit/Packet_01.5_Discovery_Pass_06_Economic_LockIn_Social_Physical_and_Viability_v1.md', 'source_pass': 6, 'source_set': 'PROVISIONAL', 'source_file_hash': '9cc99251d797d8f481e977b2bd1bbc77c74919fda3c0e741a54a807b2babd094', 'source_envelope_hash': '0cf810c8c8c65d49c03dfabf6a8c32e65530450faf2409b17d41a617a3e1f82d', 'source_block_hash': '72e3d5d31fb7c8bbcf8badda79816a50ef1981d295ba90eb8e2cb01484a475e1', 'queue_id': 'SP002-DEPENDENCY_OR_PLATFORM_STATE', 'prior_applicability_state': 'UNCLASSIFIED', 'prior_applicability_decision_hash': None}
}
PROOFS={
 'P01.5::P002::SEC-010': 'Provide one current, independently verifiable dependency-and-platform receipt bound to P01.5::P002::SEC-010 that identifies the effective candidate, provider, provider version, action identity, approval surface, and selection/confirmation configuration, then executes a targeted approval test with known alternatives and a PASS/FAIL verdict proving or disproving the complete preserved claim: user approves the wrong candidate, provider, or action.',
 'P01.5::P002::MEM-002': 'Provide one current, independently verifiable dependency-and-platform receipt bound to P01.5::P002::MEM-002 that identifies the effective provider and platform versions, the active failure-model assumptions, and a dated capability/behavior matrix, then runs targeted compatibility and failure-injection tests with PASS/FAIL verdicts proving or disproving the complete preserved claim: Resident follows obsolete failure models.',
 'P01.5::P004::PERF-001': 'Provide one current, independently verifiable platform receipt bound to P01.5::P004::PERF-001 that identifies the tested iOS, Safari/WebKit, device class, memory conditions, effective app revision, and approval-screen route, then runs bounded responsiveness, tap-delivery, long-task, memory-pressure, and page-termination tests with PASS/FAIL verdicts proving or disproving the complete preserved claim: the app appears frozen, taps are lost, approval screens become unusable, and iOS may terminate the page.',
 'P01.5::P006::ECO-001': 'Provide one current, independently verifiable provider-and-economic-platform receipt bound to P01.5::P006::ECO-001 that identifies every essential external dependency, effective service tier, quota, billing state, availability status, portability or fallback path, and tested version, then runs bounded outage, quota-exhaustion, and fallback tests with PASS/FAIL verdicts proving or disproving the complete preserved claim: essential operation stops or the project is forced into an unplanned paid dependency.'
}

def git(*args,binary=False):
 p=subprocess.run(['git',*args],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
 return p if binary else p.decode(errors='replace').strip()
def show(path): return subprocess.run(['git','show',f'{A}:{path}'],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
def rows(data): return [json.loads(x) for x in data.decode().splitlines() if x.strip()]
def sha(data): return hashlib.sha256(data).hexdigest()
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def wj(path,value): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def wl(path,values): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(''.join(canonical(x)+'\n' for x in values))
def status():
 return f'''# Packet 01.5 Pass 002 — Dependency or Platform State Family v1

STATUS: BUILT — PENDING INDEPENDENT VERIFICATION

- Authoritative anchor: `{A}`
- Permanent addresses: `{ADDRESSES[0]}`, `{ADDRESSES[1]}`, `{ADDRESSES[2]}`, `{ADDRESSES[3]}`
- Family records: 4
- Direct decisions: 0
- Exact remaining queues: 4
- Automatic `UNKNOWN — HOLD`: 0
- Dependency/platform receipts reviewed: 0
- Targeted compatibility tests completed: 0
- Effective dependency versions verified: no
- Effective platform state verified: no
- Effective provider state verified: no
- Immutable inventory: 2,750 records unchanged
- Pass 002 v11 overlay: 2,750 records unchanged
- Previously merged family artifacts: unchanged
- Pass 002 reconciliation if merged: 33 processed + 89 remaining = 122

No current claim-specific dependency-or-platform receipt was available. All four prior `UNCLASSIFIED` states remain preserved, and all four records remain queued for the smallest exact proof required.

No application behavior, configuration, dependencies, deployment, runtime state, routing, destinations, grouping, source-record closure, implementation, Pass 002 consolidation, or Packet 04 work occurred.
'''

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
 census={'packet':'01.5','pass':'002','family':F,'authoritative_anchor':A,'family_records':4,'addresses_in_inventory_order':ADDRESSES,'records':[{k:q[k] for k in IDENTITY_KEYS} for q in selected]}
 remaining=[]
 for q in selected:
  remaining.append({**q,'family':F,'family_result':'REMAIN_QUEUED','family_inspection_status':'NO_CURRENT_CLAIM_SPECIFIC_DEPENDENCY_OR_PLATFORM_RECEIPT','direct_decision_supported':False,'dependency_platform_receipts_reviewed':0,'targeted_compatibility_tests_completed':0,'effective_dependency_versions_verified':False,'effective_platform_state_verified':False,'effective_provider_state_verified':False,'smallest_exact_remaining_proof':PROOFS[q['composite_address']],'prior_state_preserved':True})
 coverage={
  'packet':'01.5','pass':'002','family':F,'authoritative_anchor':A,
  'family_records':4,'decided_records':0,'remaining_queued_records':4,'unknown_hold_created':0,
  'complete_nonduplicated_coverage':True,'direct_decision_gate_matches':0,
  'dependency_platform_receipts_reviewed':0,'targeted_compatibility_tests_completed':0,
  'effective_dependency_versions_verified':False,'effective_platform_state_verified':False,'effective_provider_state_verified':False,
  'pass_002_total_records':122,'previously_processed_records':29,'family_records_accounted':4,
  'processed_records_if_merged':33,'remaining_unprocessed_records':89,'pass_002_reconciliation_exact':True,
  'queue_sha256':sha(qb),'window_sha256':sha(wb),
  'source_inventory_sha256':sha(ib),'source_inventory_count':2750,'source_inventory_unchanged':True,
  'pass_002_overlay_sha256':sha(ob),'pass_002_overlay_count':2750,'pass_002_overlay_unchanged':True,
  'current_runtime_family_receipt_blob_sha':'5942c78a331d078b11364f46313079df3d9e887f',
  'private_uncaptured_family_receipt_blob_sha':'92045d7fa63839582ec518066033d58fede2ed8c',
  'deployment_live_family_receipt_blob_sha':'84d580215ee70c3c1e6b0b5a2d606c0c5d690eac',
  'previously_merged_family_artifacts_unchanged':True,'records_outside_family_unchanged':True,
  'evidence_reacquired':False,'other_evidence_families_processed':False,
  'application_behavior_modified':False,'configuration_modified':False,'dependencies_modified':False,
  'deployment_modified':False,'runtime_state_modified':False,'routing_assignments':0,'destination_assignments':0,
  'grouping_assignments':0,'source_records_removed_or_closed':0,'implementation_actions':0,'packet_04_actions':0
 }
 wj(CENSUS,census); wl(DEC,[]); wl(REM,remaining); wj(COV,coverage); STAT.write_text(status())
 print(json.dumps({'status':'BUILT','family_records':4,'decisions':0,'remaining_queue':4,'targeted_compatibility_tests_completed':0},indent=2))

if __name__=='__main__': main()
