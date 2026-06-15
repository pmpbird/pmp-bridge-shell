#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json, subprocess
from pathlib import Path

R=Path(__file__).resolve().parents[1]
A='8cf485bba1f89684edcd3c8429cefdd4c1dc0e83'
F='PRIVATE_OR_UNCAPTURED_EVIDENCE'
QS='audit/applicability/Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl'
IV='audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl'
CV='audit/routing-inventory/Packet_01.5_Applicability_Inventory_v9_Batch_008.jsonl'
AM='audit/Packet_01_Additive_Amendment_Control_Spine_and_Existing_Packet_Roles_v1.md'
RA='audit/PMP-Current-Resident-Reasoning-Connection-Audit-v1.md'
M=R/'audit/Packet_01.5_Private_Evidence_Matrix_v1.json'
D=R/'audit/applicability/Packet_01.5_Private_Evidence_Family_Decisions_v1.jsonl'
Q=R/'audit/applicability/Packet_01.5_Private_Evidence_Family_Remaining_Queue_v1.jsonl'
C=R/'audit/Packet_01.5_Private_Evidence_Family_Coverage_v1.json'
S=R/'audit/Packet_01.5_Private_Evidence_Family_Status_v1.md'
P=R/'audit/Packet_01.5_Private_Evidence_Family_Independent_Verification_v1.json'
SHA={QS:'1b28dbfd69e9af4b51ce5cf4eb4e43d4ed4aaea107129b2e11b7b41c9dfd861a',IV:'76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477',CV:'628875ac288a85b95131588678d7ae9c692ab2c53654409f1cd6b2e85c116e87',AM:'3d5189ea1d64df792d921d176528928b343dd317986ff4223a28aca89a42210f',RA:'22cc351549548ec172a10cfcb2393c85ae5c4b63d58be4cfaad98e3debc3a396'}
ADDR=['P01.5::B::0013','P01.5::B::0041','P01.5::B::0042','P01.5::B::0051','P01.5::B::0053','P01.5::B::0056','P01.5::B::0089','P01.5::B::0110','P01.5::B::0119']
DEC=['P01.5::B::0042','P01.5::B::0056','P01.5::B::0110']
QUE=['P01.5::B::0013','P01.5::B::0041','P01.5::B::0051','P01.5::B::0053','P01.5::B::0089','P01.5::B::0119']
ST={'P01.5::B::0042':'CURRENT DEFECT OR LIMITATION','P01.5::B::0056':'OUT-OF-SCOPE CANDIDATE','P01.5::B::0110':'CURRENT DEFECT OR LIMITATION'}
ALLOW={'.github/workflows/packet_015_private_evidence_census.yml','tools/verify_packet_01_5_private_evidence_v1.py','audit/Packet_01.5_Private_Evidence_Matrix_v1.json','audit/applicability/Packet_01.5_Private_Evidence_Family_Decisions_v1.jsonl','audit/applicability/Packet_01.5_Private_Evidence_Family_Remaining_Queue_v1.jsonl','audit/Packet_01.5_Private_Evidence_Family_Coverage_v1.json','audit/Packet_01.5_Private_Evidence_Family_Status_v1.md','audit/Packet_01.5_Private_Evidence_Family_Independent_Verification_v1.json'}

def g(*x,b=False):
 p=subprocess.run(['git',*x],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
 return p if b else p.decode(errors='replace')
def show(p): return g('show',f'{A}:{p}',b=True)
def h(b): return hashlib.sha256(b).hexdigest()
def rows(b): return [json.loads(x) for x in b.decode().splitlines() if x.strip()]
def frows(p): return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def reject(fn):
 try: fn()
 except (AssertionError,KeyError,TypeError,ValueError): return
 raise AssertionError('mutation accepted')

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--write-receipt',action='store_true'); a=ap.parse_args()
 g('cat-file','-e',f'{A}^{{commit}}')
 src={p:show(p) for p in SHA}
 for p,v in SHA.items(): assert h(src[p])==v
 qr,iv,cv=rows(src[QS]),rows(src[IV]),rows(src[CV]); assert len(iv)==2750
 fam=sorted([x for x in qr if x.get('evidence_domain')==F],key=lambda x:x['source_record_ordinal'])
 assert [x['composite_address'] for x in fam]==ADDR
 m=json.loads(M.read_text()); d=frows(D); q=frows(Q); c=json.loads(C.read_text()); s=S.read_text()
 assert (m['packet'],m['family'],m['authoritative_anchor'],m['family_count'])==('01.5',F,A,9)
 assert m['family_addresses_in_source_order']==ADDR
 assert m['source_queue']['sha256']==SHA[QS] and m['source_inventory']=={'path':IV,'sha256':SHA[IV],'count':2750}
 assert m['current_applicability']['sha256']==SHA[CV]
 assert m['privacy_boundary']['raw_private_values_read'] is False and m['privacy_boundary']['raw_private_values_written'] is False
 assert m['decision_rule']['automatic_unknown_hold'] is False
 assert [x['composite_address'] for x in m['records']]==ADDR
 inv={x['composite_address']:x for x in iv}; fq={x['composite_address']:x for x in fam}; mm={x['composite_address']:x for x in m['records']}
 for k in ADDR:
  x,y,z=mm[k],inv[k],fq[k]
  assert x['source_record_ordinal']==y['source_record_ordinal']==z['source_record_ordinal']
  assert x['original_identifier']==y['original_identifier']==z['original_identifier']
  assert x['source_envelope_hash']==y['envelope_hash']==z['source_envelope_hash'] and x['source_block_hash']==y['source_block_hash']
  assert z['missing_proof'].endswith('Preserved claim: '+x['preserved_claim'])
  if k in DEC: assert x['family_outcome']=='DECIDED' and x['decision_state']==ST[k] and x['direct_evidence']
  else: assert x['family_outcome']=='REMAIN_QUEUED' and x['decision_state'] is None and x['required_privacy_safe_receipt']
 assert [x['composite_address'] for x in d]==DEC
 for x in d:
  assert x['applicability_state']==ST[x['composite_address']] and x['decision_stage']=='APPLICABILITY_ONLY' and x['closure_state']=='OPEN'
  assert x['primary_destination'] is None and x['secondary_destinations']==[] and x['semantic_cluster_ids']==[] and x['routing_evidence']==[] and x['routing_confidence'] is None
 assert [x['composite_address'] for x in q]==QUE
 req={'composite_address','source_record_ordinal','original_identifier','source_envelope_hash','source_block_hash','preserved_claim','result','reason','privacy_safe_receipt_type','required_receipt_fields','privacy_boundary_ref','receipt_disclosure_rule','smallest_test_and_receipt','decision_blocker','reopening_condition'}
 for x in q:
  assert req<=set(x) and x['result']=='REMAIN_QUEUED' and x['required_receipt_fields'] and x['smallest_test_and_receipt']
 assert len({x['composite_address'] for x in d+q})==9 and {x['composite_address'] for x in d+q}==set(ADDR)
 assert 'UNKNOWN — HOLD' not in (M.read_text()+D.read_text()+Q.read_text())
 assert (c['family_records'],c['decided_records'],c['remaining_queued_records'],c['unknown_hold_created'])==(9,3,6,0)
 assert c['family_addresses_in_source_order']==ADDR and c['decided_addresses']==DEC and c['queued_addresses']==QUE and c['complete_decided_or_queued_coverage']
 assert c['privacy_safe_receipts_only'] and c['raw_private_values_read'] is False and c['raw_private_values_written'] is False
 assert c['source_inventory_count']==2750 and c['source_inventory_sha256']==SHA[IV] and c['source_inventory_unchanged']
 for k in ('routing_assignments','destination_assignments','grouping_assignments','source_records_removed_or_closed','implementation_actions','packet_04_actions'): assert c[k]==0
 assert 'Supported decisions: 3' in s and 'Exact remaining queues: 6' in s and 'No routing, destinations, grouping, source-record closure, implementation, or Packet 04 work occurred.' in s
 am=src[AM].decode(); ra=src[RA].decode()
 for t in ('STATUS: APPROVED','Authority is record-class-specific, not medium-specific.','Each active record must be named by an ACTIVE pointer','Executed evidence outranks plans and templates.'): assert t in am
 for t in ('Current model-oriented behavior is manual handoff.','recent/session conversation — partial','Active Work Thread/local Resident records — partial','source/body text — manual local loading only','body laws — not automatically read by normal Run','private Bug Memory — manual/private tools only','Storage is browser-local unless the user explicitly copies or invokes an external transfer path.','Notes contents cannot be secretly read by the web app'): assert t in ra
 changed={x for x in g('diff','--name-only',A,'HEAD').splitlines() if x}; assert changed<=ALLOW and IV not in changed and CV not in changed
 n=0
 b=copy.deepcopy(m); b['family_count']=8; reject(lambda: (_ for _ in ()).throw(AssertionError()) if b['family_count']!=9 else None); n+=1
 b=copy.deepcopy(d); b[0]['applicability_state']='OTHER'; reject(lambda: (_ for _ in ()).throw(AssertionError()) if b[0]['applicability_state']!=ST[b[0]['composite_address']] else None); n+=1
 b=copy.deepcopy(q); b[0].pop('smallest_test_and_receipt'); reject(lambda: (_ for _ in ()).throw(AssertionError()) if not req<=set(b[0]) else None); n+=1
 reject(lambda: (_ for _ in ()).throw(AssertionError()) if DEC+QUE==ADDR else None); n+=1
 reject(lambda: (_ for _ in ()).throw(AssertionError()) if len(DEC)+len(QUE)!=9 else None); n+=1
 rec={'packet':'01.5','verification':'private_or_uncaptured_evidence_family_independent','version':1,'status':'PASS_PRIVATE_EVIDENCE_FAMILY_VERIFIED','authoritative_anchor':A,'family':F,'family_records':9,'family_addresses_in_source_order':ADDR,'decisions_created':3,'remaining_exact_queues':6,'unknown_hold_created':0,'source_queue_sha256':SHA[QS],'source_inventory_sha256':SHA[IV],'source_inventory_count':2750,'current_applicability_sha256':SHA[CV],'matrix_sha256':h(M.read_bytes()),'decisions_sha256':h(D.read_bytes()),'remaining_queue_sha256':h(Q.read_bytes()),'coverage_sha256':h(C.read_bytes()),'status_sha256':h(S.read_bytes()),'adversarial_rejection_fixtures_passed':n,'complete_decided_or_queued_coverage':True,'privacy_safe_receipts_only':True,'raw_private_values_read':False,'raw_private_values_written':False,'source_inventory_unchanged':True,'routing_assignments':0,'destination_assignments':0,'grouping_assignments':0,'source_records_removed_or_closed':0,'implementation_actions':0,'packet_04_actions':0}
 if a.write_receipt:P.write_text(json.dumps(rec,indent=2)+'\n')
 else: assert json.loads(P.read_text())==rec
 print('STATUS: PASS — PRIVATE_OR_UNCAPTURED_EVIDENCE FAMILY VERIFIED'); print(json.dumps(rec,indent=2))
if __name__=='__main__': main()
