#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

R=Path(__file__).resolve().parents[1]
A='e4d9bf6f69c25622dad671db926233db51a576b7'
F='AUTHORITATIVE_PACKET_LAW'
ADDRESSES=['P01.5::P001::REG-001','P01.5::P001::REG-005','P01.5::P002::SEC-002','P01.5::P002::SEC-004','P01.5::P005::AUTH-003','P01.5::P005::EMERG-001']
QUEUE='audit/applicability/Packet_01.5_Scalable_Pass_002_Evidence_Queue_v1.jsonl'
WINDOW='audit/applicability/Packet_01.5_Scalable_Pass_002_Window_v1.json'
INVENTORY='audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl'
OVERLAY='audit/routing-inventory/Packet_01.5_Applicability_Inventory_v11_Pass_002.jsonl'
CURRENT_RECEIPT='audit/Packet_01.5_Pass_002_Current_Runtime_Family_Independent_Verification_v1.json'
PRIVATE_RECEIPT='audit/Packet_01.5_Pass_002_Private_Uncaptured_Family_Independent_Verification_v1.json'
DEPLOY_RECEIPT='audit/Packet_01.5_Pass_002_Deployment_Live_Family_Independent_Verification_v1.json'
DEPENDENCY_RECEIPT='audit/Packet_01.5_Pass_002_Dependency_Platform_Family_Independent_Verification_v1.json'
CROSS_RECEIPT='audit/Packet_01.5_Pass_002_Cross_Source_Conflict_Family_Independent_Verification_v1.json'
CENSUS=R/'audit/Packet_01.5_Pass_002_Authoritative_Packet_Law_Family_Census_v1.json'
DEC=R/'audit/applicability/Packet_01.5_Pass_002_Authoritative_Packet_Law_Family_Decisions_v1.jsonl'
REM=R/'audit/applicability/Packet_01.5_Pass_002_Authoritative_Packet_Law_Family_Remaining_Queue_v1.jsonl'
COV=R/'audit/Packet_01.5_Pass_002_Authoritative_Packet_Law_Family_Coverage_v1.json'
STAT=R/'audit/Packet_01.5_Pass_002_Authoritative_Packet_Law_Family_Status_v1.md'

IDENTITY_KEYS=('composite_address','inventory_position','source_record_ordinal','original_identifier','preserved_claim','source_path','source_pass','source_set','source_file_hash','source_envelope_hash','source_block_hash','queue_id','evidence_domain','prior_applicability_state','prior_applicability_decision_hash','state_preservation_rule')
EXPECTED={
'P01.5::P001::REG-001':{'inventory_position':123,'source_record_ordinal':1,'original_identifier':'REG-001','preserved_claim':'Mandatory future work can disappear from the current packet load.','source_path':'audit/Packet_01.5_Discovery_Working_Register_v1.md','source_pass':1,'source_set':'PROVISIONAL','source_file_hash':'edcb6a56f0a87531f38cba214cb1c3db99d708d5d7741fb1dcf6d9c8c099276e','source_envelope_hash':'65a10d34749751cc7368f56dc48a371c1b10f6d0364495f7bf92c3f83a7193cc','source_block_hash':'dc3a7445a551a4126e9c978b6f81268853c40bedf8afebdfa062a579565a2cf5','queue_id':'SP002-AUTHORITATIVE_PACKET_LAW','prior_applicability_state':'UNCLASSIFIED','prior_applicability_decision_hash':None},
'P01.5::P001::REG-005':{'inventory_position':127,'source_record_ordinal':5,'original_identifier':'REG-005','preserved_claim':'The current packet may pass with incomplete obligations.','source_path':'audit/Packet_01.5_Discovery_Working_Register_v1.md','source_pass':1,'source_set':'PROVISIONAL','source_file_hash':'edcb6a56f0a87531f38cba214cb1c3db99d708d5d7741fb1dcf6d9c8c099276e','source_envelope_hash':'4517364ccf25aebb4e49bb24fe0614f1af3716437ec186ea06654348493c3aa4','source_block_hash':'2a4587df9b2689bf74b5618a375c83d7596852308776241a2b0499e3e8157d11','queue_id':'SP002-AUTHORITATIVE_PACKET_LAW','prior_applicability_state':'UNCLASSIFIED','prior_applicability_decision_hash':None},
'P01.5::P002::SEC-002':{'inventory_position':134,'source_record_ordinal':2,'original_identifier':'SEC-002','preserved_claim':'compromised CDN or injected content may execute with app authority.','source_path':'audit/Packet_01.5_Discovery_Pass_02_Security_Privacy_and_Human_Risk_v1.md','source_pass':2,'source_set':'PROVISIONAL','source_file_hash':'8506f61d266208458cb79ca97cbce3f8b3baa715f992c40035ef72013727410b','source_envelope_hash':'22e8f75ec486d7f1db0902da5ab84519bb8d97de81de3b15185415fdc9806a92','source_block_hash':'fb66cb5bfa721d4845cc5b181911de9052a5f6ce8abd4e61137902bf9052f57b','queue_id':'SP002-AUTHORITATIVE_PACKET_LAW','prior_applicability_state':'UNCLASSIFIED','prior_applicability_decision_hash':None},
'P01.5::P002::SEC-004':{'inventory_position':136,'source_record_ordinal':4,'original_identifier':'SEC-004','preserved_claim':'unintended commands, file overwrite, external requests, or authority escape.','source_path':'audit/Packet_01.5_Discovery_Pass_02_Security_Privacy_and_Human_Risk_v1.md','source_pass':2,'source_set':'PROVISIONAL','source_file_hash':'8506f61d266208458cb79ca97cbce3f8b3baa715f992c40035ef72013727410b','source_envelope_hash':'e5222ea92c07fa631a576b5431e1a6d3c2dbb92e1f904966ce1a2832df960b2b','source_block_hash':'14dd7e866d56b1d4e9c6fe0bd992cc3f478a567813d169a7343fd4c608b815ee','queue_id':'SP002-AUTHORITATIVE_PACKET_LAW','prior_applicability_state':'UNCLASSIFIED','prior_applicability_decision_hash':None},
'P01.5::P005::AUTH-003':{'inventory_position':208,'source_record_ordinal':3,'original_identifier':'AUTH-003','preserved_claim':'stale authority can later modify code, records, evidence, or deployment.','source_path':'audit/Packet_01.5_Discovery_Pass_05_Governance_Audit_Retention_and_Succession_v1.md','source_pass':5,'source_set':'PROVISIONAL','source_file_hash':'fd14c3e585bc88006628b1310905f64c9f26814c402d8ea30926ae7d8b8acb0f','source_envelope_hash':'86160d3d5f3bf695da2670afe565b1c97311ca69678de1e3a219497330151367','source_block_hash':'a2cb904947544a39cad0ba98a061bd1cdc350762e8b1fd32b20cf998ae86b0ef','queue_id':'SP002-AUTHORITATIVE_PACKET_LAW','prior_applicability_state':'UNCLASSIFIED','prior_applicability_decision_hash':None},
'P01.5::P005::EMERG-001':{'inventory_position':214,'source_record_ordinal':9,'original_identifier':'EMERG-001','preserved_claim':'an urgent fix becomes an unrestricted authority escape.','source_path':'audit/Packet_01.5_Discovery_Pass_05_Governance_Audit_Retention_and_Succession_v1.md','source_pass':5,'source_set':'PROVISIONAL','source_file_hash':'fd14c3e585bc88006628b1310905f64c9f26814c402d8ea30926ae7d8b8acb0f','source_envelope_hash':'2fefaf81c7240848d787570ccd530fc077b7241de41ea1eb17d19b8fe9be0430','source_block_hash':'8ae0f1bf2616e9ffb9d8ddfc145a10d46844d7bc0150c611773f4eb453503d21','queue_id':'SP002-AUTHORITATIVE_PACKET_LAW','prior_applicability_state':'UNCLASSIFIED','prior_applicability_decision_hash':None}}
PROOFS={
'P01.5::P001::REG-001':'Provide one current, independently verifiable authoritative packet-law receipt bound to P01.5::P001::REG-001 that identifies the governing law text, immutable law hash, effective version, authority status, applicability rule, and complete obligation-loading rule, then applies that law to the exact record with a PASS/FAIL verdict proving or disproving the complete preserved claim: Mandatory future work can disappear from the current packet load.',
'P01.5::P001::REG-005':'Provide one current, independently verifiable authoritative packet-law receipt bound to P01.5::P001::REG-005 that identifies the governing law text, immutable law hash, effective version, authority status, applicability rule, and complete packet-pass criteria, then applies that law to the exact record with a PASS/FAIL verdict proving or disproving the complete preserved claim: The current packet may pass with incomplete obligations.',
'P01.5::P002::SEC-002':'Provide one current, independently verifiable authoritative packet-law receipt bound to P01.5::P002::SEC-002 that identifies the governing law text, immutable law hash, effective version, authority status, applicability rule, and CDN or injected-content authority boundary, then applies that law to the exact record with a PASS/FAIL verdict proving or disproving the complete preserved claim: compromised CDN or injected content may execute with app authority.',
'P01.5::P002::SEC-004':'Provide one current, independently verifiable authoritative packet-law receipt bound to P01.5::P002::SEC-004 that identifies the governing law text, immutable law hash, effective version, authority status, applicability rule, and command, file, external-request, and authority-escape boundary, then applies that law to the exact record with a PASS/FAIL verdict proving or disproving the complete preserved claim: unintended commands, file overwrite, external requests, or authority escape.',
'P01.5::P005::AUTH-003':'Provide one current, independently verifiable authoritative packet-law receipt bound to P01.5::P005::AUTH-003 that identifies the governing law text, immutable law hash, effective version, authority status, applicability rule, and stale-authority revocation boundary, then applies that law to the exact record with a PASS/FAIL verdict proving or disproving the complete preserved claim: stale authority can later modify code, records, evidence, or deployment.',
'P01.5::P005::EMERG-001':'Provide one current, independently verifiable authoritative packet-law receipt bound to P01.5::P005::EMERG-001 that identifies the governing emergency-authority law text, immutable law hash, effective version, authority status, applicability rule, scope limit, expiration, and review rule, then applies that law to the exact record with a PASS/FAIL verdict proving or disproving the complete preserved claim: an urgent fix becomes an unrestricted authority escape.'}

def git(*args):
 p=subprocess.run(['git',*args],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
 return p.decode(errors='replace').strip()
def show(path): return subprocess.run(['git','show',f'{A}:{path}'],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
def rows(data): return [json.loads(x) for x in data.decode().splitlines() if x.strip()]
def sha(data): return hashlib.sha256(data).hexdigest()
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def wj(path,value): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def wl(path,values): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(''.join(canonical(x)+'\n' for x in values))
def status():
 return f'''# Packet 01.5 Pass 002 — Authoritative Packet Law Family v1

STATUS: BUILT — PENDING INDEPENDENT VERIFICATION

- Authoritative anchor: `{A}`
- Permanent addresses: `{ADDRESSES[0]}`, `{ADDRESSES[1]}`, `{ADDRESSES[2]}`, `{ADDRESSES[3]}`, `{ADDRESSES[4]}`, `{ADDRESSES[5]}`
- Family records: 6
- Direct decisions: 0
- Exact remaining queues: 6
- Automatic `UNKNOWN — HOLD`: 0
- Authoritative packet-law receipts reviewed: 0
- Governing laws identified: 0
- Governing law hashes verified: no
- Effective law versions verified: no
- Authority statuses verified: no
- Applicability rules verified: no
- Immutable inventory: 2,750 records unchanged
- Pass 002 v11 overlay: 2,750 records unchanged
- Previously merged family artifacts: unchanged
- Pass 002 reconciliation if merged: 43 processed + 79 remaining = 122

No current claim-specific authoritative packet-law receipt was available. All six prior `UNCLASSIFIED` states remain preserved, and all six records remain queued for the smallest exact packet-law proof required.

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
 assert git('rev-parse',f'{A}:{DEPENDENCY_RECEIPT}')=='7ccb9a57451e80ced1a88de47406e92b7dc0b486'
 assert git('rev-parse',f'{A}:{CROSS_RECEIPT}')=='3e7df143344d51b4be07e3cd25cd6d3be78edee9'
 census={'packet':'01.5','pass':'002','family':F,'authoritative_anchor':A,'family_records':6,'addresses_in_inventory_order':ADDRESSES,'records':[{k:q[k] for k in IDENTITY_KEYS} for q in selected]}
 remaining=[]
 for q in selected:
  remaining.append({**q,'family':F,'family_result':'REMAIN_QUEUED','family_inspection_status':'NO_CURRENT_CLAIM_SPECIFIC_AUTHORITATIVE_PACKET_LAW_RECEIPT','direct_decision_supported':False,'authoritative_packet_law_receipts_reviewed':0,'governing_law_identified':False,'governing_law_hash_verified':False,'effective_law_version_verified':False,'authority_status_verified':False,'applicability_rule_verified':False,'smallest_exact_remaining_proof':PROOFS[q['composite_address']],'prior_state_preserved':True})
 coverage={'packet':'01.5','pass':'002','family':F,'authoritative_anchor':A,'family_records':6,'decided_records':0,'remaining_queued_records':6,'unknown_hold_created':0,'complete_nonduplicated_coverage':True,'direct_decision_gate_matches':0,'authoritative_packet_law_receipts_reviewed':0,'governing_laws_identified':0,'governing_law_hashes_verified':False,'effective_law_versions_verified':False,'authority_statuses_verified':False,'applicability_rules_verified':False,'pass_002_total_records':122,'previously_processed_records':37,'family_records_accounted':6,'processed_records_if_merged':43,'remaining_unprocessed_records':79,'pass_002_reconciliation_exact':True,'queue_sha256':sha(qb),'window_sha256':sha(wb),'source_inventory_sha256':sha(ib),'source_inventory_count':2750,'source_inventory_unchanged':True,'pass_002_overlay_sha256':sha(ob),'pass_002_overlay_count':2750,'pass_002_overlay_unchanged':True,'current_runtime_family_receipt_blob_sha':'5942c78a331d078b11364f46313079df3d9e887f','private_uncaptured_family_receipt_blob_sha':'92045d7fa63839582ec518066033d58fede2ed8c','deployment_live_family_receipt_blob_sha':'84d580215ee70c3c1e6b0b5a2d606c0c5d690eac','dependency_platform_family_receipt_blob_sha':'7ccb9a57451e80ced1a88de47406e92b7dc0b486','cross_source_conflict_family_receipt_blob_sha':'3e7df143344d51b4be07e3cd25cd6d3be78edee9','previously_merged_family_artifacts_unchanged':True,'records_outside_family_unchanged':True,'evidence_reacquired':False,'other_evidence_families_processed':False,'application_behavior_modified':False,'configuration_modified':False,'dependencies_modified':False,'deployment_modified':False,'runtime_state_modified':False,'routing_assignments':0,'destination_assignments':0,'grouping_assignments':0,'source_records_removed_or_closed':0,'implementation_actions':0,'packet_04_actions':0}
 wj(CENSUS,census); wl(DEC,[]); wl(REM,remaining); wj(COV,coverage); STAT.write_text(status())
 print(json.dumps({'status':'BUILT','family_records':6,'decisions':0,'remaining_queue':6,'authoritative_packet_law_receipts_reviewed':0},indent=2))

if __name__=='__main__': main()
