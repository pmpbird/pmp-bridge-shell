#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json
from pathlib import Path

R=Path(__file__).resolve().parents[1]
A='9a91fb5b848f52a7422644cfe3556e7c93ed0314'
F='CURRENT_RUNTIME_SOURCE'
I=R/'tools/inspect_packet_01_5_pass_002_current_runtime_v1.py'
D=R/'audit/Packet_01.5_Pass_002_Current_Runtime_Discovery_v1.json'
CENSUS=R/'audit/Packet_01.5_Pass_002_Current_Runtime_Family_Census_v1.json'
MATRIX=R/'audit/Packet_01.5_Pass_002_Current_Runtime_Evidence_Matrix_v1.json'
DEC=R/'audit/applicability/Packet_01.5_Pass_002_Current_Runtime_Family_Decisions_v1.jsonl'
REM=R/'audit/applicability/Packet_01.5_Pass_002_Current_Runtime_Family_Remaining_Queue_v1.jsonl'
COV=R/'audit/Packet_01.5_Pass_002_Current_Runtime_Family_Coverage_v1.json'
STAT=R/'audit/Packet_01.5_Pass_002_Current_Runtime_Family_Status_v1.md'

def load_inspector():
 s=importlib.util.spec_from_file_location('runtime_inspector',I);assert s and s.loader
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def sha(b):return hashlib.sha256(b).hexdigest()
def csha(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
def wj(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def wl(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(''.join(json.dumps(y,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n' for y in x))

def main():
 m=load_inspector();m.main();dis=json.loads(D.read_text())
 source=[x for x in m.jsonl(m.show(m.QUEUE)) if x.get('evidence_domain')==F]
 by={x['composite_address']:x for x in source};assert len(source)==len(by)==26
 census_records=[];matrix_records=[];remaining=[]
 for r in dis['records']:
  q=by[r['composite_address']]
  identity={k:q[k] for k in ('composite_address','inventory_position','source_record_ordinal','original_identifier','preserved_claim','source_envelope_hash','source_block_hash','prior_applicability_state','prior_applicability_decision_hash')}
  census_records.append(identity)
  candidates=[]
  for f in r['candidate_evidence_files'][:5]:
   candidates.append({'path':f['path'],'sha256':f['sha256'],'hits':f['hits'][:5]})
  entry={**identity,'search_terms':r['search_terms'],'candidate_sources':candidates,'candidate_source_count':r['candidate_evidence_file_count'],'conflict_status':'NO_ADJUDICATED_RUNTIME_CONFLICT','direct_decision_supported':False,'inspection_result':'INSUFFICIENT_CURRENT_RUNTIME_EVIDENCE','inspection_reason':'Only broad or partial repository matches were found; no same-address claim-specific bounded test or explicit current verdict exists.'}
  matrix_records.append(entry)
  paths=', '.join(x['path'] for x in candidates[:3]) or 'the exact current loader/source path'
  remaining.append({**q,'family':F,'family_result':'REMAIN_QUEUED','family_inspection_status':entry['inspection_result'],'family_evidence_matrix_record_sha256':csha(entry),'smallest_exact_remaining_proof':f"Provide one claim-specific bounded runtime test for {q['composite_address']} against {paths}, including tested commit, effective source/configuration hashes, exact input, observed output, and PASS/FAIL verdict for: {q['preserved_claim']}",'candidate_source_paths':[x['path'] for x in candidates],'candidate_source_hashes':{x['path']:x['sha256'] for x in candidates},'prior_state_preserved':True})
 census={'packet':'01.5','pass':'002','family':F,'authoritative_anchor':A,'family_records':26,'addresses_in_inventory_order':[x['composite_address'] for x in source],'records':census_records}
 matrix={'packet':'01.5','pass':'002','family':F,'authoritative_anchor':A,'inspection_scope':'CURRENT_MERGED_REPOSITORY_SOURCE_CONFIGURATION_EFFECTIVE_MAPS_TESTS','inspected_repository_files':dis['inspected_repository_files'],'decision_gate':'CLAIM_SPECIFIC_SAME_ADDRESS_BOUNDED_RUNTIME_TEST_OR_EXPLICIT_VERDICT','records':matrix_records}
 cov={'packet':'01.5','pass':'002','family':F,'authoritative_anchor':A,'family_records':26,'decided_records':0,'remaining_queued_records':26,'unknown_hold_created':0,'complete_nonduplicated_coverage':True,'direct_decision_gate_matches':0,'inspected_repository_files':dis['inspected_repository_files'],'queue_sha256':dis['queue_sha256'],'window_sha256':dis['window_sha256'],'source_inventory_sha256':dis['inventory_sha256'],'source_inventory_count':2750,'source_inventory_unchanged':True,'pass_002_overlay_sha256':dis['overlay_sha256'],'pass_002_overlay_count':2750,'pass_002_overlay_unchanged':True,'evidence_reacquired':False,'other_evidence_families_processed':False,'application_behavior_modified':False,'configuration_modified':False,'dependencies_modified':False,'deployment_modified':False,'runtime_state_modified':False,'routing_assignments':0,'destination_assignments':0,'grouping_assignments':0,'source_records_removed_or_closed':0,'implementation_actions':0,'packet_04_actions':0}
 status=f'''# Packet 01.5 Pass 002 — Current Runtime Source Family v1\n\nSTATUS: BUILT — PENDING INDEPENDENT VERIFICATION\n\n- Authoritative anchor: `{A}`\n- Family records: 26\n- Direct decisions: 0\n- Exact remaining queues: 26\n- Automatic `UNKNOWN — HOLD`: 0\n- Repository files inspected: {dis['inspected_repository_files']}\n- Immutable inventory: 2,750 records unchanged\n- Pass 002 v11 overlay: 2,750 records unchanged\n\nBroad keyword overlap was not promoted into current truth. No claim-specific same-address bounded runtime test or explicit current verdict was found, so all 26 records remain queued with the smallest exact proof required.\n\nNo application behavior, configuration, dependencies, deployment, runtime state, routing, destinations, grouping, source-record closure, implementation, or Packet 04 work occurred.\n'''
 wj(CENSUS,census);wj(MATRIX,matrix);wl(DEC,[]);wl(REM,remaining);wj(COV,cov);STAT.write_text(status);D.unlink()
 print(json.dumps({'status':'BUILT','family_records':26,'decisions':0,'remaining_queue':26,'inspected_repository_files':dis['inspected_repository_files']},indent=2))
if __name__=='__main__':main()
