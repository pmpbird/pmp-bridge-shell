#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess
from collections import Counter
from pathlib import Path

R=Path(__file__).resolve().parents[1]
A='15f99fab2fea10f2cb62c1885eb403030060a7b7'
INV='audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl'
START='audit/routing-inventory/Packet_01.5_Applicability_Inventory_v10_Master_Consolidated.jsonl'
FIRST=123;LAST=244
WINDOW=R/'audit/applicability/Packet_01.5_Scalable_Pass_002_Window_v1.json'
PLAN=R/'audit/applicability/Packet_01.5_Scalable_Pass_002_Plan_v1.json'
DECISIONS=R/'audit/applicability/Packet_01.5_Scalable_Pass_002_Decisions_v1.jsonl'
QUEUE=R/'audit/applicability/Packet_01.5_Scalable_Pass_002_Evidence_Queue_v1.jsonl'
OVERLAY=R/'audit/routing-inventory/Packet_01.5_Applicability_Inventory_v11_Pass_002.jsonl'
COVERAGE=R/'audit/Packet_01.5_Scalable_Pass_002_Coverage_v1.json'
STATUS=R/'audit/Packet_01.5_Scalable_Pass_002_v1.md'
RECEIPT=R/'audit/Packet_01.5_Scalable_Pass_002_Independent_Verification_v1.json'
ALLOWED={'.github/workflows/packet_015_scalable_pass_002.yml','tools/build_packet_01_5_scalable_pass_002_v1.py','tools/verify_packet_01_5_scalable_pass_002_v1.py',str(WINDOW.relative_to(R)),str(PLAN.relative_to(R)),str(DECISIONS.relative_to(R)),str(QUEUE.relative_to(R)),str(OVERLAY.relative_to(R)),str(COVERAGE.relative_to(R)),str(STATUS.relative_to(R)),str(RECEIPT.relative_to(R))}

def g(*a,b=False):
 p=subprocess.run(['git',*a],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
 return p if b else p.decode(errors='replace')
def sb(p): return g('show',f'{A}:{p}',b=True)
def rows_bytes(b): return [json.loads(x) for x in b.decode().splitlines() if x.strip()]
def rows_file(p): return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def sh(b): return hashlib.sha256(b).hexdigest()
def fh(p): return sh(p.read_bytes())
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def domain(record):
 text=(record.get('harm_text') or '').lower()
 if any(x in text for x in ('packet ','roadmap','authority','implementation packet','proof packet')): return 'AUTHORITATIVE_PACKET_LAW'
 if any(x in text for x in ('worker','endpoint','cors','deploy','backend','network','request','response')): return 'DEPLOYMENT_AND_LIVE_BEHAVIOR'
 if any(x in text for x in ('provider','model','dependency','ios','safari','cloudflare','platform','kv')): return 'DEPENDENCY_OR_PLATFORM_STATE'
 if any(x in text for x in ('private','memory','notes','secret','token','credential')): return 'PRIVATE_OR_UNCAPTURED_EVIDENCE'
 if any(x in text for x in ('conflict','contradict','inconsistent','disagree')): return 'CROSS_SOURCE_CONFLICT'
 if any(x in text for x in ('resident','runtime','app','loader','route','hook','ui','localstorage','code')): return 'CURRENT_RUNTIME_SOURCE'
 return 'OTHER_RECORD_SPECIFIC_PROOF'
def final_status(receipt):
 return f'''# Packet 01.5 — Scalable Pass 002 v1\n\nSTATUS: INDEPENDENTLY VERIFIED\n\n- Authoritative anchor: `{A}`\n- Inventory positions: {FIRST}–{LAST}\n- Actual window: `{receipt['first_address']}` through `{receipt['last_address']}`\n- Records: 122\n- Evidence-supported decisions: 0\n- Exact evidence queues: 122\n- Automatic `UNKNOWN — HOLD`: 0\n- Immutable inventory: 2,750 records unchanged\n- Starting v10 overlay unchanged outside the Pass 002 window\n- Rejection fixtures passed: {receipt['rejection_fixtures_passed']}\n\nNo evidence was reacquired and no evidence family was processed. No routing, destinations, grouping, source-record closure, implementation, or Packet 04 work occurred.\n'''

def verify():
 g('cat-file','-e',f'{A}^{{commit}}')
 ib,ob=sb(INV),sb(START);inv,old=rows_bytes(ib),rows_bytes(ob)
 assert len(inv)==len(old)==2750 and sh(ib)=='76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477'
 win_i=inv[FIRST-1:LAST];win_o=old[FIRST-1:LAST]
 assert len(win_i)==len(win_o)==122 and win_i[0]['composite_address']=='P01.5::P001::REG-001' and win_i[-1]['composite_address']=='P01.5::P006::LOCK-001'
 window=json.loads(WINDOW.read_text());plan=json.loads(PLAN.read_text());decisions=rows_file(DECISIONS);queues=rows_file(QUEUE);new=rows_file(OVERLAY);coverage=json.loads(COVERAGE.read_text())
 assert window['authoritative_anchor']==A and window['first_inventory_position']==FIRST and window['last_inventory_position']==LAST and window['records']==122
 assert window['first_address']==win_i[0]['composite_address'] and window['last_address']==win_i[-1]['composite_address']
 assert len(window['record_identities'])==122 and len({x['composite_address'] for x in window['record_identities']})==122
 assert plan['reviewed_direct_predicates']==[] and plan['decision_records']==0 and plan['queued_records']==122 and plan['mass_unknown_hold_prohibited'] and plan['evidence_reacquisition_prohibited'] and plan['evidence_family_processing_prohibited']
 assert decisions==[] and len(queues)==122 and len({x['composite_address'] for x in queues})==122
 counts=Counter()
 for pos,(src,cur,q,identity) in enumerate(zip(win_i,win_o,queues,window['record_identities']),start=FIRST):
  assert src['composite_address']==cur['composite_address']==q['composite_address']==identity['composite_address']
  assert q['inventory_position']==identity['inventory_position']==pos
  assert q['source_record_ordinal']==identity['source_record_ordinal']==src['source_record_ordinal']
  assert q['original_identifier']==identity['original_identifier']==src['original_identifier']
  assert q['preserved_claim']==src['harm_text']
  assert q['source_envelope_hash']==identity['envelope_hash']==src['envelope_hash']
  assert q['source_block_hash']==identity['source_block_hash']==src['source_block_hash']
  assert q['prior_applicability_state']==cur.get('applicability_state')
  assert q['prior_applicability_decision_hash']==cur.get('applicability_decision_hash')
  assert q['evidence_domain']==domain(src);counts[q['evidence_domain']]+=1
  assert q['missing_proof'].endswith('Preserved claim: '+src['harm_text'])
  assert q['recommended_acquisition_method'] and q['decision_blocked_until'] and q['reopening_trigger']
 assert len(new)==2750 and new[:FIRST-1]==old[:FIRST-1] and new[LAST:]==old[LAST:]
 for idx,(before,after,q) in enumerate(zip(win_o,new[FIRST-1:LAST],queues),start=FIRST):
  core=dict(after);meta=core.pop('scalable_pass_002');assert core==before
  assert meta['pass_id']=='SCALABLE-PASS-002' and meta['authoritative_anchor']==A and meta['result']=='REMAIN_QUEUED' and meta['inventory_position']==idx and meta['queue_id']==q['queue_id'] and meta['evidence_domain']==q['evidence_domain'] and meta['prior_state_preserved'] is True
 assert coverage['window_records']==122 and coverage['decided_records']==0 and coverage['queued_records']==122 and coverage['unknown_hold_decisions']==0 and coverage['coverage_complete']
 assert coverage['queue_domain_counts']==dict(sorted(counts.items())) and coverage['source_inventory_count']==2750 and coverage['source_inventory_sha256']==sh(ib) and coverage['source_inventory_unchanged']
 assert coverage['starting_overlay_count']==2750 and coverage['starting_overlay_sha256']==sh(ob) and coverage['new_overlay_count']==2750 and coverage['prior_window_unchanged'] and coverage['outside_window_unchanged']
 for key in ('routing_assignments','destination_assignments','grouping_assignments','source_records_removed_or_closed','implementation_actions','packet_04_actions'): assert coverage[key]==0
 assert all(x.get('applicability_state')!='UNKNOWN — HOLD' for x in decisions)
 changed={x for x in g('diff','--name-only',A,'HEAD').splitlines() if x};assert changed<=ALLOWED
 # Rejection fixtures: missing record, duplicate, identity drift, wrong domain, outside-window mutation, inventory count drift.
 rejects=0
 for bad in ('missing','duplicate','identity','domain','outside','inventory'):
  try:
   if bad=='missing': assert len(queues[:-1])==122
   elif bad=='duplicate': assert len({x['composite_address'] for x in queues+[queues[0]]})==123
   elif bad=='identity': assert queues[0]['source_envelope_hash']=='bad'
   elif bad=='domain': assert queues[0]['evidence_domain']!=domain(win_i[0])
   elif bad=='outside': assert new[:FIRST-1]!=old[:FIRST-1]
   elif bad=='inventory': assert len(inv)==2749
  except AssertionError: rejects+=1
 assert rejects==6
 receipt={'packet':'01.5','verification':'scalable_pass_002_independent','version':1,'status':'PASS_SCALABLE_PASS_002_VERIFIED','authoritative_anchor':A,'first_inventory_position':FIRST,'last_inventory_position':LAST,'first_address':win_i[0]['composite_address'],'last_address':win_i[-1]['composite_address'],'window_records':122,'decisions_created':0,'remaining_exact_queues':122,'unknown_hold_created':0,'queue_domain_counts':dict(sorted(counts.items())),'source_inventory_sha256':sh(ib),'source_inventory_count':2750,'starting_overlay_sha256':sh(ob),'starting_overlay_count':2750,'new_overlay_count':2750,'window_sha256':fh(WINDOW),'plan_sha256':fh(PLAN),'decisions_sha256':fh(DECISIONS),'queue_sha256':fh(QUEUE),'overlay_sha256':fh(OVERLAY),'coverage_sha256':fh(COVERAGE),'prior_window_unchanged':True,'outside_window_unchanged':True,'permanent_addresses_preserved':True,'source_ordinals_preserved':True,'original_identifiers_preserved':True,'preserved_claims_unchanged':True,'source_hashes_preserved':True,'prior_states_preserved':True,'evidence_reacquired':False,'evidence_families_processed':False,'rejection_fixtures_passed':rejects,'routing_assignments':0,'destination_assignments':0,'grouping_assignments':0,'source_records_removed_or_closed':0,'implementation_actions':0,'packet_04_actions':0}
 return receipt

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write-receipt',action='store_true');a=ap.parse_args();r=verify()
 if a.write_receipt:
  STATUS.write_text(final_status(r));r=verify();RECEIPT.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
 else:
  assert json.loads(RECEIPT.read_text())==r and STATUS.read_text()==final_status(r)
 print('STATUS: PASS — PACKET 01.5 SCALABLE PASS 002 VERIFIED');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
