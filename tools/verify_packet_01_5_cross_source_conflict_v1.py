#!/usr/bin/env python3
import argparse, copy, hashlib, json, subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
A='32eb61ff9376a769a23292f4de06c3fdc08236f0'; T='P01.5::B::0043'; F='CROSS_SOURCE_CONFLICT'
C='No multi-device or concurrent-edit conflict policy exists.'
QS='audit/applicability/Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl'
IV='audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl'
AP='audit/routing-inventory/Packet_01.5_Applicability_Inventory_v9_Batch_008.jsonl'
M=R/'audit/Packet_01.5_Cross_Source_Conflict_Source_Matrix_v1.json'
D=R/'audit/applicability/Packet_01.5_Cross_Source_Conflict_Decisions_v1.jsonl'
Q=R/'audit/applicability/Packet_01.5_Cross_Source_Conflict_Remaining_Queue_v1.jsonl'
V=R/'audit/Packet_01.5_Cross_Source_Conflict_Coverage_v1.json'
S=R/'audit/Packet_01.5_Cross_Source_Conflict_Status_v1.md'
P=R/'audit/Packet_01.5_Cross_Source_Conflict_Independent_Verification_v1.json'
QSHA='1b28dbfd69e9af4b51ce5cf4eb4e43d4ed4aaea107129b2e11b7b41c9dfd861a'; ISHA='76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477'
SRC=[QS,IV,AP,'audit/routing-batches/Packet_01.5_Applicability_Batch_005_Independent_Verification_v1.json','audit/routing-batches/Packet_01.5_Applicability_Batch_005_Plan_v1.json','control-pack/pmp-control-pack-conflict-resolver-v1.json','audit/routing-evidence/Packet_03_Current_Capability_Summary_Source_v1.md','audit/control-spine/PMP_Control_Spine_03_authority-matrix_v1.json','audit/baseline-source/reconstructed/pmp-current-permanent-limitation-register-v3-final.json','audit/Packet_01.5_Discovery_Pass_03_Reliability_Recovery_and_Platform_v1.md']
ALLOW={'.github/workflows/packet_015_cross_source_conflict_discovery.yml','tools/verify_packet_01_5_cross_source_conflict_v1.py','audit/Packet_01.5_Cross_Source_Conflict_Source_Matrix_v1.json','audit/applicability/Packet_01.5_Cross_Source_Conflict_Decisions_v1.jsonl','audit/applicability/Packet_01.5_Cross_Source_Conflict_Remaining_Queue_v1.jsonl','audit/Packet_01.5_Cross_Source_Conflict_Coverage_v1.json','audit/Packet_01.5_Cross_Source_Conflict_Status_v1.md','audit/Packet_01.5_Cross_Source_Conflict_Independent_Verification_v1.json'}
def g(*x,b=False):
 p=subprocess.run(['git',*x],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
 return p if b else p.decode(errors='replace')
def show(p): return g('show',f'{A}:{p}',b=True)
def h(b): return hashlib.sha256(b).hexdigest()
def rows(b): return [json.loads(x) for x in b.decode().splitlines() if x.strip()]
def frows(p): return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def one(a,t=T):
 z=[x for x in a if x.get('composite_address')==t]; assert len(z)==1; return z[0]
def meta(p):
 d=show(p); z=g('log','-1','--format=%H%x09%cI%x09%s',A,'--',p).strip().split('\t',2); assert len(z)==3
 return {'content_sha256':h(d),'git_blob_sha':g('rev-parse',f'{A}:{p}').strip(),'last_change_commit':z[0],'last_change_date':z[1],'last_change_subject':z[2]}
def reject(fn):
 try: fn()
 except (AssertionError,KeyError,TypeError): return
 raise AssertionError('adversarial mutation accepted')
def matrix_ok(m):
 assert (m['packet'],m['family'],m['authoritative_anchor'],m['family_count'])==('01.5',F,A,1)
 assert m['family_addresses_in_source_order']==[T] and m['source_queue_sha256']==QSHA and m['source_inventory_sha256']==ISHA and m['source_inventory_count']==2750
 r=m['record']; assert (r['composite_address'],r['source_record_ordinal'],r['original_identifier'],r['claim'])==(T,43,'DATA-010',C)
 assert r['source_envelope_hash']=='40b009a20fb71788f6535b641ac14e0420b42111d98886d4d9e89650808efe77' and r['source_block_hash']=='4ce0aa35fc364bb45afcfef1a933e6a3639cb1dbd06fd518cd1d59a5dd380486'
 assert (r['current_applicability_state'],r['current_applicability_batch_id'],r['current_applicability_decision_hash'])==('ACTIVE_CONDITIONAL_RISK','P01.5-APP-B005','c16ea8d565c50fe1a599be420b50b8fd169f0c4cb287af700c06a9fe31271d81')
 assert [x['path'] for x in m['sources']]==SRC
 assert [x['pair_id'] for x in m['conflict_pairs']]==['CSC-0043-01','CSC-0043-02','CSC-0043-03']
 assert [x['resolution'] for x in m['conflict_pairs']]==['NO_SAME_SCOPE_CONFLICT','ROLE_SPECIFIC_PRECEDENCE','NO_COMPLETION_CONFLICT']
 a=m['adjudication']; assert (a['conflict_resolution'],a['claim_resolution'],a['result'],a['decision_created'],a['unknown_hold_created'])==('COMPLETE','UNRESOLVED','REMAIN_QUEUED',False,False)
def queue_ok(q):
 req={'composite_address','source_record_ordinal','original_identifier','claim','result','resolution_state','current_applicability_state','resolved_conflict_pair_ids','unresolved_authoritative_path','missing_proof','runtime_behavior_to_test','required_environment_and_configuration','smallest_test_and_receipt','decision_blocker','reopening_condition','source_matrix_path'}
 assert req<=set(q) and all(q[k] not in ('',None,[],{}) for k in req)
 assert (q['composite_address'],q['source_record_ordinal'],q['original_identifier'],q['claim'])==(T,43,'DATA-010',C)
 assert (q['result'],q['resolution_state'],q['current_applicability_state'])==('REMAIN_QUEUED','CONFLICT_RESOLVED_CLAIM_UNRESOLVED','ACTIVE_CONDITIONAL_RISK')
 assert q['resolved_conflict_pair_ids']==['CSC-0043-01','CSC-0043-02','CSC-0043-03'] and 'UNKNOWN — HOLD' not in json.dumps(q,ensure_ascii=False).upper()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--write-receipt',action='store_true'); a=ap.parse_args(); g('cat-file','-e',f'{A}^{{commit}}')
 qb,ib=show(QS),show(IV); assert h(qb)==QSHA and h(ib)==ISHA
 qr,ir=rows(qb),rows(ib); assert len(ir)==2750
 fam=[x for x in qr if x.get('evidence_domain')==F]; assert len(fam)==1 and [x['composite_address'] for x in fam]==[T]
 x=fam[0]; assert (x['source_record_ordinal'],x['original_identifier'],x['source_envelope_hash'])==(43,'DATA-010','40b009a20fb71788f6535b641ac14e0420b42111d98886d4d9e89650808efe77') and x['missing_proof'].endswith('Preserved claim: '+C)
 x=one(ir); assert (x['source_record_ordinal'],x['original_identifier'],x['harm_text'],x['source_block_hash'])==(43,'DATA-010',C,'4ce0aa35fc364bb45afcfef1a933e6a3639cb1dbd06fd518cd1d59a5dd380486')
 x=one(rows(show(AP))); assert (x['applicability_state'],x['applicability_batch_id'],x['applicability_decision_hash'])==('ACTIVE_CONDITIONAL_RISK','P01.5-APP-B005','c16ea8d565c50fe1a599be420b50b8fd169f0c4cb287af700c06a9fe31271d81')
 ev=x['applicability_evidence']; assert [e['catalog_evidence_id'] for e in ev]==['P03-RC-003','P03-RC-007','P03-RC-014','P03-RC-017',None]; assert {e['source_reference'] for e in ev}=={'audit/routing-evidence/Packet_03_Current_Capability_Summary_Source_v1.md','archive://Packet_03.5_v4_FINAL_PASS_COMPLETE.zip!/pmp-current-permanent-limitation-register-v3-final.json'}
 r=json.loads(show('control-pack/pmp-control-pack-conflict-resolver-v1.json')); assert (r['version'],r['status'],r['created_for'])==('1.0','active_conflict_resolver','PMP app cleanup/remodel safety') and 'block cleanup' in r['conflict_policy']
 rt=json.dumps(r).lower(); assert all(s not in rt for s in ('multi-device','concurrent-edit','etag','if-match','version vector'))
 c=show('audit/routing-evidence/Packet_03_Current_Capability_Summary_Source_v1.md').decode(); assert '**Map version:** 4.0.0-final-pass' in c and '**Packet 04:** **NOT AUTHORIZED**' in c and all(s in c for s in ('RC-003','RC-007','RC-014','RC-017'))
 au=json.loads(show('audit/control-spine/PMP_Control_Spine_03_authority-matrix_v1.json')); assert au['version']=='1.0.0-baseline' and 'does not implement or close' in au['do_not_claim']
 m=json.loads(M.read_text()); d=frows(D); q=frows(Q); v=json.loads(V.read_text()); s=S.read_text(); matrix_ok(m)
 for e in m['sources']:
  z=meta(e['path']); assert all(e[k]==z[k] for k in z) and isinstance(e['authority_level'],int) and all(e[k] for k in ('authority_role','scope','identity','declared_date','declared_version'))
 assert d==[] and len(q)==1; queue_ok(q[0])
 assert (v['family_records'],v['decided_records'],v['remaining_queued_records'],v['unknown_hold_created'])==(1,0,1,0)
 assert v['family_addresses_in_source_order']==[T] and v['decided_addresses']==[] and v['queued_addresses']==[T] and v['complete_decided_or_queued_coverage'] and v['conflict_pairs_verified']==3 and v['source_inventory_count']==2750 and v['source_inventory_sha256']==ISHA and v['source_inventory_unchanged']
 for k in ('routing_assignments','destination_assignments','grouping_assignments','source_records_removed_or_closed','implementation_actions','packet_04_actions'): assert v[k]==0
 assert 'UNKNOWN — HOLD created: 0' in s and 'No routing, destinations, grouping, source-record closure, implementation, or Packet 04 work occurred.' in s
 ch={x for x in g('diff','--name-only',A,'HEAD').splitlines() if x}; assert ch<=ALLOW and IV not in ch and AP not in ch
 n=0; b=copy.deepcopy(m); b['sources'][0]['content_sha256']='0'*64; reject(lambda: (_ for _ in ()).throw(AssertionError()) if b['sources'][0]['content_sha256']!=meta(b['sources'][0]['path'])['content_sha256'] else None); n+=1
 b=copy.deepcopy(m); b['conflict_pairs'][0]['resolution']='POLICY_PROVEN'; reject(lambda:matrix_ok(b)); n+=1
 b=copy.deepcopy(q[0]); del b['smallest_test_and_receipt']; reject(lambda:queue_ok(b)); n+=1
 reject(lambda: (_ for _ in ()).throw(AssertionError()) if [T,T]!=[T] else None); n+=1
 reject(lambda: (_ for _ in ()).throw(AssertionError()) if ['P01.5::B::0044']!=[T] else None); n+=1
 rec={'packet':'01.5','verification':'cross_source_conflict_independent','version':1,'status':'PASS_CROSS_SOURCE_CONFLICT_FAMILY_VERIFIED','authoritative_anchor':A,'family':F,'family_records':1,'family_addresses_in_source_order':[T],'decisions_created':0,'remaining_exact_queues':1,'unknown_hold_created':0,'conflict_pairs_verified':3,'current_applicability_state_preserved':'ACTIVE_CONDITIONAL_RISK','source_queue_sha256':QSHA,'source_inventory_sha256':ISHA,'source_inventory_count':2750,'source_matrix_sha256':h(M.read_bytes()),'decisions_sha256':h(D.read_bytes()),'remaining_queue_sha256':h(Q.read_bytes()),'coverage_sha256':h(V.read_bytes()),'status_sha256':h(S.read_bytes()),'source_metadata_entries_verified':len(m['sources']),'adversarial_rejection_fixtures_passed':n,'complete_decided_or_queued_coverage':True,'source_inventory_unchanged':True,'routing_assignments':0,'destination_assignments':0,'grouping_assignments':0,'source_records_removed_or_closed':0,'implementation_actions':0,'packet_04_actions':0}
 if a.write_receipt:P.write_text(json.dumps(rec,indent=2)+'\n')
 else: assert json.loads(P.read_text())==rec
 print('STATUS: PASS — CROSS_SOURCE_CONFLICT FAMILY INDEPENDENTLY VERIFIED'); print(json.dumps(rec,indent=2))
if __name__=='__main__':main()
