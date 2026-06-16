#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json, subprocess
from collections import Counter
from pathlib import Path

R=Path(__file__).resolve().parents[1]
A='15f99fab2fea10f2cb62c1885eb403030060a7b7'
INV='audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl'
START='audit/routing-inventory/Packet_01.5_Applicability_Inventory_v10_Master_Consolidated.jsonl'
FIRST=123; LAST=244
PASS_ID='SCALABLE-PASS-002'
WINDOW=R/'audit/applicability/Packet_01.5_Scalable_Pass_002_Window_v1.json'
PLAN=R/'audit/applicability/Packet_01.5_Scalable_Pass_002_Plan_v1.json'
DECISIONS=R/'audit/applicability/Packet_01.5_Scalable_Pass_002_Decisions_v1.jsonl'
QUEUE=R/'audit/applicability/Packet_01.5_Scalable_Pass_002_Evidence_Queue_v1.jsonl'
OVERLAY=R/'audit/routing-inventory/Packet_01.5_Applicability_Inventory_v11_Pass_002.jsonl'
COVERAGE=R/'audit/Packet_01.5_Scalable_Pass_002_Coverage_v1.json'
STATUS=R/'audit/Packet_01.5_Scalable_Pass_002_v1.md'

DOMAINS={
'AUTHORITATIVE_PACKET_LAW':('Capture the currently authoritative packet-law text that directly proves or disproves the preserved claim.','Extract digest-bound governing clauses and independently compare them with this permanent address.'),
'DEPLOYMENT_AND_LIVE_BEHAVIOR':('Capture the current serving artifact, route, headers, and safe live behavior needed to decide the preserved claim.','Identify the deployed revision and run bounded source-plus-live probes with receipts.'),
'DEPENDENCY_OR_PLATFORM_STATE':('Capture the current provider, dependency, binding, or platform state tied to the preserved claim.','Record versions/configuration and run a targeted compatibility or availability test.'),
'PRIVATE_OR_UNCAPTURED_EVIDENCE':('Capture a privacy-safe receipt proving or disproving the claim without exposing private values.','Produce a redacted digest, count, or boolean proof through the approved private-evidence boundary.'),
'CROSS_SOURCE_CONFLICT':('Resolve the conflicting sources and establish which one is current and authoritative.','Create a precedence comparison with dates, hashes, and an independent adjudication receipt.'),
'CURRENT_RUNTIME_SOURCE':('Trace the exact current runtime source path and test the behavior named in the preserved claim.','Capture source hashes, effective-map precedence, and a bounded runtime proof.'),
'OTHER_RECORD_SPECIFIC_PROOF':('Gather direct current evidence that specifically proves or disproves the preserved claim.','Define and execute a record-specific source, document, or runtime test with a stable receipt.'),
}

def g(*a,b=False):
 p=subprocess.run(['git',*a],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
 return p if b else p.decode(errors='replace')
def sb(p): return g('show',f'{A}:{p}',b=True)
def rows(b): return [json.loads(x) for x in b.decode().splitlines() if x.strip()]
def sh(b): return hashlib.sha256(b).hexdigest()
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def write_json(p,x): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def write_jsonl(p,x): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(''.join(canonical(y)+'\n' for y in x))
def domain(record):
 text=(record.get('harm_text') or '').lower()
 if any(x in text for x in ('packet ','roadmap','authority','implementation packet','proof packet')): return 'AUTHORITATIVE_PACKET_LAW'
 if any(x in text for x in ('worker','endpoint','cors','deploy','backend','network','request','response')): return 'DEPLOYMENT_AND_LIVE_BEHAVIOR'
 if any(x in text for x in ('provider','model','dependency','ios','safari','cloudflare','platform','kv')): return 'DEPENDENCY_OR_PLATFORM_STATE'
 if any(x in text for x in ('private','memory','notes','secret','token','credential')): return 'PRIVATE_OR_UNCAPTURED_EVIDENCE'
 if any(x in text for x in ('conflict','contradict','inconsistent','disagree')): return 'CROSS_SOURCE_CONFLICT'
 if any(x in text for x in ('resident','runtime','app','loader','route','hook','ui','localstorage','code')): return 'CURRENT_RUNTIME_SOURCE'
 return 'OTHER_RECORD_SPECIFIC_PROOF'

def main():
 g('cat-file','-e',f'{A}^{{commit}}')
 ib,ob=sb(INV),sb(START); inv,old=rows(ib),rows(ob)
 assert len(inv)==len(old)==2750
 assert sh(ib)=='76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477'
 win_i=inv[FIRST-1:LAST];win_o=old[FIRST-1:LAST]
 assert len(win_i)==len(win_o)==122
 assert win_i[0]['composite_address']=='P01.5::P001::REG-001'
 assert win_i[-1]['composite_address']=='P01.5::P006::LOCK-001'
 for src,cur in zip(win_i,win_o):
  assert src['composite_address']==cur['composite_address']
  assert src['envelope_hash']==cur['envelope_hash'] and src['source_block_hash']==cur['source_block_hash']

 # No same-address reviewed direct predicates exist in the merged start state for this window.
 decisions=[]
 queues=[]; counts=Counter()
 for pos,(src,cur) in enumerate(zip(win_i,win_o),start=FIRST):
  d=domain(src);missing,method=DOMAINS[d];counts[d]+=1
  queues.append({
   'composite_address':src['composite_address'],
   'inventory_position':pos,
   'source_record_ordinal':src['source_record_ordinal'],
   'original_identifier':src['original_identifier'],
   'preserved_claim':src['harm_text'],
   'source_envelope_hash':src['envelope_hash'],
   'source_block_hash':src['source_block_hash'],
   'source_file_hash':src.get('source_file_hash'),
   'source_path':src.get('source_path'),
   'source_pass':src.get('source_pass'),
   'source_set':src.get('source_set'),
   'queue_id':f'SP002-{d}',
   'evidence_domain':d,
   'prior_applicability_state':cur.get('applicability_state'),
   'prior_applicability_decision_hash':cur.get('applicability_decision_hash'),
   'state_preservation_rule':'PRESERVE_CURRENT_STATE_UNTIL_DIRECT_MERGED_EVIDENCE_SUPPORTS_A_DECISION',
   'missing_proof':f'{missing} Preserved claim: {src["harm_text"]}',
   'recommended_acquisition_method':method,
   'decision_blocked_until':'The exact missing proof is captured, hashed, bound to this permanent address, and independently verified.',
   'reopening_trigger':'New merged authoritative evidence, a source/configuration change, a conflict, or a stale prior receipt.',
  })

 window={'packet':'01.5','pass_id':PASS_ID,'authoritative_anchor':A,'source_inventory_sha256':sh(ib),'starting_overlay_sha256':sh(ob),'first_inventory_position':FIRST,'last_inventory_position':LAST,'first_address':win_i[0]['composite_address'],'last_address':win_i[-1]['composite_address'],'records':122,'record_identities':[{'inventory_position':p,'composite_address':x['composite_address'],'source_record_ordinal':x['source_record_ordinal'],'original_identifier':x['original_identifier'],'envelope_hash':x['envelope_hash'],'source_block_hash':x['source_block_hash']} for p,x in enumerate(win_i,start=FIRST)]}
 plan={'packet':'01.5','pass_id':PASS_ID,'authoritative_anchor':A,'decision_rule':'Apply a decision only when an already-merged, claim-specific, same-address authoritative predicate directly proves or disproves the preserved claim.','reviewed_direct_predicates':[],'decision_records':0,'queued_records':122,'mass_unknown_hold_prohibited':True,'evidence_reacquisition_prohibited':True,'evidence_family_processing_prohibited':True,'established_evidence_domains':list(DOMAINS),'decision_author':'Structure AI','decision_verifier':'Independent Verification AI'}
 new=[]
 for idx,row in enumerate(old,start=1):
  if FIRST<=idx<=LAST:
   q=queues[idx-FIRST];y=copy.deepcopy(row);y['scalable_pass_002']={'pass_id':PASS_ID,'authoritative_anchor':A,'result':'REMAIN_QUEUED','inventory_position':idx,'queue_id':q['queue_id'],'evidence_domain':q['evidence_domain'],'queue_record_sha256':sh((canonical(q)+'\n').encode()),'prior_state_preserved':True};new.append(y)
  else:new.append(copy.deepcopy(row))
 assert len(new)==2750 and new[:FIRST-1]==old[:FIRST-1] and new[LAST:]==old[LAST:]
 coverage={'packet':'01.5','pass_id':PASS_ID,'authoritative_anchor':A,'window_records':122,'decided_records':0,'queued_records':122,'unknown_hold_decisions':0,'coverage_complete':True,'decision_addresses':[],'queue_domain_counts':dict(sorted(counts.items())),'first_address':win_i[0]['composite_address'],'last_address':win_i[-1]['composite_address'],'source_inventory_count':2750,'source_inventory_sha256':sh(ib),'source_inventory_unchanged':True,'starting_overlay_count':2750,'starting_overlay_sha256':sh(ob),'new_overlay_count':2750,'prior_window_unchanged':True,'outside_window_unchanged':True,'routing_assignments':0,'destination_assignments':0,'grouping_assignments':0,'source_records_removed_or_closed':0,'implementation_actions':0,'packet_04_actions':0}
 status=f'''# Packet 01.5 — Scalable Pass 002 v1\n\nSTATUS: BUILT — PENDING INDEPENDENT VERIFICATION\n\n- Authoritative anchor: `{A}`\n- Inventory positions: {FIRST}–{LAST}\n- Actual window: `{win_i[0]['composite_address']}` through `{win_i[-1]['composite_address']}`\n- Records: 122\n- Evidence-supported decisions: 0\n- Exact evidence queues: 122\n- Automatic `UNKNOWN — HOLD`: 0\n- Immutable inventory: 2,750 records unchanged\n- Starting v10 overlay preserved outside this window\n\nNo evidence was reacquired and no evidence family was processed. No routing, destinations, grouping, source-record closure, implementation, or Packet 04 work occurred.\n'''
 write_json(WINDOW,window);write_json(PLAN,plan);write_jsonl(DECISIONS,decisions);write_jsonl(QUEUE,queues);write_jsonl(OVERLAY,new);write_json(COVERAGE,coverage);STATUS.write_text(status)
 assert sb(INV)==ib and sb(START)==ob
 print(json.dumps({'status':'PASS_002_BUILT','first':window['first_address'],'last':window['last_address'],'records':122,'decisions':0,'queues':122,'queue_domain_counts':dict(counts),'inventory':2750},indent=2))
if __name__=='__main__':main()
