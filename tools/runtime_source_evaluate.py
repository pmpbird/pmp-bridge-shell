#!/usr/bin/env python3
from __future__ import annotations
import json
from runtime_source_git import FAMILY,INVENTORY_SHA,QUEUE_SHA,claim,jsonl,sha,source_map
from runtime_source_graph import build_graph,graph_text
from runtime_source_paths import ROOT,QUEUE,INVENTORY,PASS,PRECEDENCE
from runtime_source_rules import DECISIONS,QUEUES,REASONS,evaluate

def need(value,message):
    if not value:raise ValueError(message)
def evidence(eid,ref,stable,claim_supported):return {'evidence_id':eid,'source_reference':ref,'source_hash_or_stable_reference':stable,'claim_supported':claim_supported}

def compute():
    queue_bytes=QUEUE.read_bytes();inventory_bytes=INVENTORY.read_bytes();need(sha(queue_bytes)==QUEUE_SHA,'queue sha');need(sha(inventory_bytes)==INVENTORY_SHA,'inventory sha')
    pass_data=json.loads(PASS.read_text());family=[x for x in jsonl(QUEUE) if x['evidence_domain']==FAMILY];need(len(family)==pass_data['expected_records']==20,'family count');need([x['source_record_ordinal'] for x in family]==sorted(x['source_record_ordinal'] for x in family),'source order');need({x['original_identifier'] for x in family}==set(DECISIONS)|set(QUEUES),'identifier coverage')
    inventory=source_map(INVENTORY);graph=build_graph(ROOT);need(graph['main_commit']==pass_data['main_anchor'],'main anchor');node_by={x['path']:x for x in graph['nodes']};core_text=graph_text(ROOT,graph,manual=True)
    bounded=[
      {'test':'primary_map_first_success','pass':graph['primary_map']==graph['map_precedence'][0],'detail':graph['map_precedence']},
      {'test':'loader_and_current_app_resolved','pass':bool(graph['current_loader'] and graph['current_app']),'detail':[graph['current_loader'],graph['current_app']]},
      {'test':'nested_chain_contains_v4_v3_home','pass':all(x in graph['primary_paths'] for x in ('pmp-current-inner-cleanbug-rgcontrols-v4.html','pmp-current-inner-cleanbug-rgcontrols-v3.html','pmp-home-single-v6.html')),'detail':graph['primary_paths']},
      {'test':'fallbacks_separated','pass':bool(graph['fallback_paths']) and not set(graph['fallback_paths']).issubset(set(graph['primary_paths'])),'detail':graph['fallback_paths']},
      {'test':'worker_and_config_bound','pass':all(x in graph['platform_paths'] for x in ('pmp-worker.js','wrangler.toml')),'detail':graph['platform_paths']},
      {'test':'packet_processing_outputs_excluded','pass':not any('Packet_01.5_' in x['path'] or 'packet_01_5_' in x['path'] for x in graph['nodes']),'detail':'runtime graph only'},
    ];need(all(x['pass'] for x in bounded),'bounded source tests')
    decisions=[];remaining=[];matrix=[]
    for item in family:
        address=item['composite_address'];identifier=item['original_identifier'];preserved=claim(item);source=inventory[address];need(source['envelope_hash']==item['source_envelope_hash'],'source envelope '+address)
        outcome,detail,used=evaluate(identifier,ROOT,graph,core_text);expected='DISPROVED' if identifier=='DATA-006' else 'SUPPORTED' if identifier in DECISIONS else 'RUNTIME_TEST_OR_NONRUNTIME_EVIDENCE_REQUIRED';decided=identifier in DECISIONS and outcome==expected
        matrix.append({'composite_address':address,'source_record_ordinal':item['source_record_ordinal'],'original_identifier':identifier,'claim':preserved,'predicate':DECISIONS.get(identifier,(None,))[0] if identifier in DECISIONS else 'RUNTIME_OR_NONRUNTIME_EVIDENCE_REQUIRED','outcome':outcome,'expected_outcome':expected,'detail':detail,'controlling_paths':used,'result':'DECIDED' if decided else 'REMAIN_QUEUED'})
        if not decided:
            if identifier in QUEUES:source_path,missing,behavior,environment,test,block,reopen=QUEUES[identifier]
            else:source_path=', '.join(used) or ', '.join(graph['primary_paths']);missing='The current predicate did not reach its required complete outcome.';behavior='Re-evaluate the complete preserved claim against the effective runtime.';environment='Authoritative main and deterministic local runtime source test.';test='Resolve the conflicting predicate evidence and rerun the independent verifier.';block=f'Expected {expected}, observed {outcome}.';reopen='Any controlling source, route, precedence rule, test, or digest changes.'
            remaining.append({'composite_address':address,'source_record_ordinal':item['source_record_ordinal'],'original_identifier':identifier,'source_envelope_hash':item['source_envelope_hash'],'queue_id':'CRS001-'+FAMILY,'evidence_domain':FAMILY,'preserved_claim':preserved,'runtime_source_path':source_path,'missing_precedence_or_reachability_proof':missing,'runtime_behavior_to_test':behavior,'required_environment_and_configuration':environment,'smallest_test_or_receipt':test,'decision_blocked_until':block,'reopening_trigger':reopen});continue
        predicate,state,confidence=DECISIONS[identifier];ev=[evidence('CRS-SOURCE-'+address,f'{INVENTORY.relative_to(ROOT)}#{address}',source['envelope_hash'],'Preserves the immutable source claim and permanent address.'),evidence('CRS-QUEUE-'+address,f'{QUEUE.relative_to(ROOT)}#{address}',f'sha256:{QUEUE_SHA}#{address}','Proves family membership and source order.'),evidence('CRS-PASS-'+address,f'{PASS.relative_to(ROOT)}#{predicate}','sha256:'+sha(PASS.read_bytes())+'#'+predicate,'Binds the reviewed runtime predicate.'),evidence('CRS-GRAPH-'+address,str(PRECEDENCE.relative_to(ROOT)),'sha256:'+graph['graph_sha256'],'Binds effective-source precedence and every reachable content digest.'),evidence('CRS-MAIN-'+address,'origin/main','commit:'+graph['main_commit'],'Anchors all source reads to authoritative main.')]
        for number,path in enumerate(used,1):
            if path in node_by:ev.append(evidence(f'CRS-FILE-{number:02d}-'+address,path,'sha256:'+node_by[path]['sha256'],'Direct controlling source for this predicate.'))
        decisions.append({'composite_address':address,'source_inventory_sha256':INVENTORY_SHA,'source_envelope_hash':source['envelope_hash'],'source_block_hash':source['source_block_hash'],'decision_stage':'APPLICABILITY_ONLY','applicability_state':state,'applicability_evidence':ev,'applicability_reasoning_summary':REASONS[identifier],'applicability_confidence':confidence,'primary_destination':None,'secondary_destinations':[],'cross_cutting_laws':[],'semantic_cluster_ids':[],'routing_evidence':[],'routing_rationale':'','routing_confidence':None,'expected_receiving_work':'','expected_completion_evidence':'','unresolved_dependencies':[],'hold_reason':'','reopening_conditions':['A controlling runtime source, route, precedence edge, platform binding, or verified receipt changes.','The main commit, source-envelope digest, or runtime graph digest changes.'],'decision_version':'Packet-01.5-Current-Runtime-Source-v1','decision_author':pass_data['decision_author'],'routing_decision_verifier':pass_data['decision_verifier'],'closure_state':'OPEN'})
    need(len(decisions)==11 and len(remaining)==9,'expected partition')
    return {'pass':pass_data,'family':family,'graph':graph,'bounded_tests':bounded,'decisions':decisions,'remaining':remaining,'matrix':matrix,'queue_bytes':queue_bytes,'inventory_bytes':inventory_bytes}
