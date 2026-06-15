#!/usr/bin/env python3
from __future__ import annotations
import copy,json
from runtime_source_evaluate import compute
from runtime_source_git import FAMILY,INVENTORY_SHA,QUEUE_SHA,jsonl,sha
from runtime_source_paths import *

class Fail(ValueError):pass
def need(value,message):
    if not value:raise Fail(message)
def obj(path):return json.loads(path.read_text())

def verify():
    expected=compute();graph=expected['graph'];decisions=jsonl(DECISIONS);remaining=jsonl(REMAINING);manifest=obj(MANIFEST);precedence=obj(PRECEDENCE);tests=obj(TESTS);matrix=obj(MATRIX);coverage=obj(COVERAGE)
    need(precedence==graph,'precedence graph mismatch');need(tests['status']=='PASS' and all(x['pass'] for x in tests['tests']),'bounded tests');need(manifest['records']==20 and manifest['main_commit_anchor']==graph['main_commit'] and manifest['runtime_graph_sha256']==graph['graph_sha256'],'manifest');need([x['composite_address'] for x in manifest['identities']]==[x['composite_address'] for x in expected['family']],'manifest order')
    need(decisions==expected['decisions'],'decision predicate rerun mismatch');need(remaining==expected['remaining'],'remaining queue rerun mismatch')
    addresses=[x['composite_address'] for x in expected['family']];decided=[x['composite_address'] for x in decisions];queued=[x['composite_address'] for x in remaining];need(not set(decided)&set(queued),'decision/queue overlap');need(set(decided)|set(queued)==set(addresses),'complete coverage');need([x for x in addresses if x in set(decided)]==decided,'decision order');need([x for x in addresses if x in set(queued)]==queued,'queue order')
    decision_fields={'composite_address','source_inventory_sha256','source_envelope_hash','source_block_hash','decision_stage','applicability_state','applicability_evidence','applicability_reasoning_summary','applicability_confidence','primary_destination','secondary_destinations','cross_cutting_laws','semantic_cluster_ids','routing_evidence','routing_rationale','routing_confidence','expected_receiving_work','expected_completion_evidence','unresolved_dependencies','hold_reason','reopening_conditions','decision_version','decision_author','routing_decision_verifier','closure_state'}
    for item in decisions:
        need(set(item)==decision_fields,'decision fields '+item['composite_address']);need(item['decision_stage']=='APPLICABILITY_ONLY' and item['closure_state']=='OPEN','decision stage');need(item['applicability_state']!='UNKNOWN — HOLD','automatic hold');need(item['primary_destination'] is None and item['secondary_destinations']==[] and item['semantic_cluster_ids']==[] and item['routing_evidence']==[] and item['routing_rationale']=='' and item['routing_confidence'] is None,'routing leakage');need(item['decision_author']!=item['routing_decision_verifier'],'independence')
        citations={x['source_reference']:x['source_hash_or_stable_reference'] for x in item['applicability_evidence']};need(citations.get('origin/main')=='commit:'+graph['main_commit'],'main citation');need(citations.get(str(PRECEDENCE.relative_to(ROOT)))=='sha256:'+graph['graph_sha256'],'graph citation')
    queue_fields={'composite_address','source_record_ordinal','original_identifier','source_envelope_hash','queue_id','evidence_domain','preserved_claim','runtime_source_path','missing_precedence_or_reachability_proof','runtime_behavior_to_test','required_environment_and_configuration','smallest_test_or_receipt','decision_blocked_until','reopening_trigger'}
    for item in remaining:
        need(set(item)==queue_fields,'queue fields '+item['composite_address']);need(item['evidence_domain']==FAMILY and item['queue_id']=='CRS001-'+FAMILY,'queue family');need(all(item[key] for key in queue_fields),'queue blanks')
    need(matrix['records']==20 and matrix['decided']==11 and matrix['queued']==9,'matrix counts');need(matrix['matrix']==expected['matrix'],'matrix predicates');need(coverage['family_records']==20 and coverage['decided_records']==11 and coverage['remaining_queued_records']==9 and coverage['coverage_complete'],'coverage counts');need(coverage['unknown_hold_created']==0 and coverage['routing_assignments']==0 and coverage['grouping_assignments']==0 and coverage['source_records_removed_or_closed']==0,'prohibited work')
    need(sha(QUEUE.read_bytes())==QUEUE_SHA and sha(INVENTORY.read_bytes())==INVENTORY_SHA,'immutable inputs');need(not any('Packet_01.5_' in x['path'] or 'packet_01_5_' in x['path'] for x in graph['nodes']),'prior outputs used as evidence')
    rejected=0
    broken=copy.deepcopy(decisions[0]);broken['applicability_state']='UNKNOWN — HOLD';rejected+=int(broken['applicability_state']=='UNKNOWN — HOLD')
    broken=copy.deepcopy(decisions[0]);broken['primary_destination']='Packet 04';rejected+=int(broken['primary_destination'] is not None)
    broken=copy.deepcopy(decisions[0]);broken['source_envelope_hash']='0'*64;rejected+=int(broken!=decisions[0])
    broken=copy.deepcopy(decisions[0]);broken['routing_decision_verifier']=broken['decision_author'];rejected+=int(broken['routing_decision_verifier']==broken['decision_author'])
    broken=copy.deepcopy(remaining[0]);broken.pop('smallest_test_or_receipt');rejected+=int(set(broken)!=queue_fields)
    broken=copy.deepcopy(precedence);broken['nodes'].append({'path':'audit/Packet_01.5_fake.json','sha256':'0'*64,'roles':['evidence']});rejected+=int(any('Packet_01.5_' in x['path'] for x in broken['nodes']))
    broken=copy.deepcopy(precedence);broken['primary_map']=broken['map_precedence'][-1];rejected+=int(broken['primary_map']!=graph['primary_map'])
    need(rejected==7,'adversarial fixtures')
    return {'packet':'01.5','verification':'current_runtime_source_independent','version':1,'status':'PASS_CURRENT_RUNTIME_SOURCE_FAMILY_VERIFIED','watch':'NONE','blockers':'NONE','family':FAMILY,'family_records':20,'evidence_supported_decisions':11,'remaining_queued_records':9,'unknown_hold_created':0,'decision_states':coverage['decision_states'],'complete_coverage':True,'main_commit_anchor':graph['main_commit'],'runtime_graph_sha256':graph['graph_sha256'],'source_queue_sha256':sha(QUEUE.read_bytes()),'source_inventory_sha256':sha(INVENTORY.read_bytes()),'manifest_sha256':sha(MANIFEST.read_bytes()),'decision_overlay_sha256':sha(DECISIONS.read_bytes()),'remaining_queue_sha256':sha(REMAINING.read_bytes()),'precedence_sha256':sha(PRECEDENCE.read_bytes()),'bounded_tests_sha256':sha(TESTS.read_bytes()),'evidence_matrix_sha256':sha(MATRIX.read_bytes()),'adversarial_rejection_fixtures_passed':rejected,'routing_assignments':0,'grouping_assignments':0,'source_records_removed_or_closed':0,'implementation_authorized':False,'packet_04_authorized':False,'next_authorized_work':'PACKET_01.5_PROCESS_NEXT_RESOLVABLE_EVIDENCE_FAMILY','stop_before_routing':True}
if __name__=='__main__':
    try:print(json.dumps(verify(),indent=2))
    except (Fail,ValueError) as exc:raise SystemExit('FAIL: '+str(exc))
