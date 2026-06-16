#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, subprocess
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

IDENTITY_KEYS=('composite_address','inventory_position','source_record_ordinal','original_identifier','preserved_claim','source_path','source_pass','source_set','source_file_hash','source_envelope_hash','source_block_hash','queue_id','evidence_domain','prior_applicability_state','prior_applicability_decision_hash','state_preservation_rule')

EXPECTED={
 'P01.5::P002::SEC-003':{
  'inventory_position':135,'source_record_ordinal':3,'original_identifier':'SEC-003',
  'preserved_claim':'host compromise, secret theft, network exfiltration, or modification outside the candidate.',
  'source_path':'audit/Packet_01.5_Discovery_Pass_02_Security_Privacy_and_Human_Risk_v1.md',
  'source_pass':2,'source_set':'PROVISIONAL',
  'source_file_hash':'8506f61d266208458cb79ca97cbce3f8b3baa715f992c40035ef72013727410b',
  'source_envelope_hash':'776de00b2f12ea082163da59f15cba949d6a810d7c89221a9074677b92dbbf7c',
  'source_block_hash':'b05b8be6e526e4f54ee0e04668656f3cbc2a90d10f7ffb8d4614ecd6ee9d1b3f',
  'queue_id':'SP002-DEPLOYMENT_AND_LIVE_BEHAVIOR','prior_applicability_state':'UNCLASSIFIED',
  'prior_applicability_decision_hash':None
 },
 'P01.5::P005::REPO-001':{
  'inventory_position':225,'source_record_ordinal':20,'original_identifier':'REPO-001',
  'preserved_claim':'source, history, issues, evidence, and deployment control may disappear together.',
  'source_path':'audit/Packet_01.5_Discovery_Pass_05_Governance_Audit_Retention_and_Succession_v1.md',
  'source_pass':5,'source_set':'PROVISIONAL',
  'source_file_hash':'fd14c3e585bc88006628b1310905f64c9f26814c402d8ea30926ae7d8b8acb0f',
  'source_envelope_hash':'f60f37b5a24795ba47085edd58e6ddec04cd7f9c152cee590e36594d2404fdb2',
  'source_block_hash':'8b55affd5c3a624fffb74f059a88557166d6b28b8cc3652c95cf68f6506ff7d5',
  'queue_id':'SP002-DEPLOYMENT_AND_LIVE_BEHAVIOR','prior_applicability_state':'UNCLASSIFIED',
  'prior_applicability_decision_hash':None
 }
}

PROOFS={
 'P01.5::P002::SEC-003':'Provide one current, independently verifiable deployment-and-live receipt bound to P01.5::P002::SEC-003 that identifies the immutable served revision, provider project and environment, effective route and security headers, effective secret-binding names with only redacted fingerprints, effective outbound-network policy, and bounded integrity and exfiltration probe verdicts; the receipt must prove or disprove the complete preserved claim without exposing secret values: host compromise, secret theft, network exfiltration, or modification outside the candidate.',
 'P01.5::P005::REPO-001':'Provide one current, independently verifiable continuity receipt bound to P01.5::P005::REPO-001 that identifies the immutable served revision and effective deployment controller, proves repository history, issues, evidence, and deployment control do not share one unmitigated failure domain, and includes a bounded export, restore, and control-recovery test with PASS/FAIL verdicts; the receipt must prove or disprove the complete preserved claim: source, history, issues, evidence, and deployment control may disappear together.'
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
 return f'''# Packet 01.5 Pass 002 — Deployment and Live-Behavior Family v1

STATUS: BUILT — PENDING INDEPENDENT VERIFICATION

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

No current claim-specific deployment-and-live receipt was available. Both prior `UNCLASSIFIED` states remain preserved, and both records remain queued for the smallest exact live proof required.

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
 assert len(rows(ib))==len(rows(ob))==2750
 assert sha(qb)=='0c4b9660151448fdb03b328e3fa41d0e98e679d0233759f651e90eae3a5a0e96'
 assert sha(wb)=='eb75fa865feab6e3017f6d93938fb71ff2740870b618d513cafa86f20382dc28'
 assert sha(ib)=='76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477'
 assert sha(ob)=='465ed8e338c7d32ce3c460960d8637855c65d7018d7f5c90db12c915a1c88654'
 assert git('rev-parse',f'{A}:{CURRENT_RECEIPT}')=='5942c78a331d078b11364f46313079df3d9e887f'
 assert git('rev-parse',f'{A}:{PRIVATE_RECEIPT}')=='92045d7fa63839582ec518066033d58fede2ed8c'
 census={'packet':'01.5','pass':'002','family':F,'authoritative_anchor':A,'family_records':2,'addresses_in_inventory_order':ADDRESSES,'records':[{k:q[k] for k in IDENTITY_KEYS} for q in selected]}
 remaining=[]
 for q in selected:
  remaining.append({**q,'family':F,'family_result':'REMAIN_QUEUED','family_inspection_status':'NO_CURRENT_CLAIM_SPECIFIC_DEPLOYMENT_AND_LIVE_RECEIPT','direct_decision_supported':False,'deployment_receipts_reviewed':0,'bounded_live_probes_completed':0,'immutable_deployed_revision_verified':False,'effective_live_configuration_verified':False,'effective_route_verified':False,'smallest_exact_remaining_proof':PROOFS[q['composite_address']],'prior_state_preserved':True})
 coverage={
  'packet':'01.5','pass':'002','family':F,'authoritative_anchor':A,
  'family_records':2,'decided_records':0,'remaining_queued_records':2,'unknown_hold_created':0,
  'complete_nonduplicated_coverage':True,'direct_decision_gate_matches':0,
  'deployment_receipts_reviewed':0,'bounded_live_probes_completed':0,
  'immutable_deployed_revision_verified':False,'effective_live_configuration_verified':False,'effective_route_verified':False,
  'pass_002_total_records':122,'previously_processed_records':27,'family_records_accounted':2,
  'processed_records_if_merged':29,'remaining_unprocessed_records':93,'pass_002_reconciliation_exact':True,
  'queue_sha256':sha(qb),'window_sha256':sha(wb),
  'source_inventory_sha256':sha(ib),'source_inventory_count':2750,'source_inventory_unchanged':True,
  'pass_002_overlay_sha256':sha(ob),'pass_002_overlay_count':2750,'pass_002_overlay_unchanged':True,
  'current_runtime_family_receipt_blob_sha':'5942c78a331d078b11364f46313079df3d9e887f',
  'private_uncaptured_family_receipt_blob_sha':'92045d7fa63839582ec518066033d58fede2ed8c',
  'previously_merged_family_artifacts_unchanged':True,'records_outside_family_unchanged':True,
  'evidence_reacquired':False,'other_evidence_families_processed':False,
  'application_behavior_modified':False,'configuration_modified':False,'dependencies_modified':False,
  'deployment_modified':False,'runtime_state_modified':False,'routing_assignments':0,'destination_assignments':0,
  'grouping_assignments':0,'source_records_removed_or_closed':0,'implementation_actions':0,'packet_04_actions':0
 }
 wj(CENSUS,census); wl(DEC,[]); wl(REM,remaining); wj(COV,coverage); STAT.write_text(status())
 print(json.dumps({'status':'BUILT','family_records':2,'decisions':0,'remaining_queue':2,'bounded_live_probes_completed':0},indent=2))

if __name__=='__main__': main()
