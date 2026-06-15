#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from dep_platform_common import *
from dep_platform_rules import RULES,REASONS,EXTERNAL,evaluate

R=Path(__file__).resolve().parents[1];A=R/'audit';P=A/'applicability';Q=P/'Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl';I=A/'routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl';PLAN=P/'Packet_01.5_Dependency_Platform_Family_Pass_v1.json'
MAN=P/'Packet_01.5_Dependency_Platform_Family_Manifest_v1.json';DEC=P/'Packet_01.5_Dependency_Platform_Family_Decisions_v1.jsonl';REM=P/'Packet_01.5_Dependency_Platform_Family_Remaining_Queue_v1.jsonl';MAT=A/'Packet_01.5_Dependency_Platform_Evidence_Matrix_v1.json';COV=A/'Packet_01.5_Dependency_Platform_Family_Coverage_v1.json';SUM=A/'Packet_01.5_Dependency_Platform_Family_v1.md'
def need(x,m):
    if not x:raise SystemExit('FAIL: '+m)
def evidence(eid,ref,stable,claim):return {'evidence_id':eid,'source_reference':ref,'source_hash_or_stable_reference':stable,'claim_supported':claim}
def dump_lines(path,data):path.write_text(''.join(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'))+'\n' for x in data),encoding='utf-8')

def main():
    rawq=Q.read_bytes();rawi=I.read_bytes();need(sha(rawq)==QUEUE_SHA,'queue hash');need(sha(rawi)==INVENTORY_SHA,'inventory hash')
    plan=json.loads(PLAN.read_text());family=[x for x in rows(Q) if x['evidence_domain']==FAMILY];need(len(family)==plan['expected_family_records']==14,'family count');need([x['source_record_ordinal'] for x in family]==sorted(x['source_record_ordinal'] for x in family),'source order')
    inv={x['composite_address']:x for x in rows(I)};names=files(R);records,corp=corpus(R,names);file_rows,fcensus=census(R,names);run_rows,runsha=runtime(R,names);mainsha=anchor(R);plansha=sha(PLAN.read_bytes())
    decisions=[];remaining=[];matrix=[]
    for item in family:
        addr=item['composite_address'];ident=item['original_identifier'];text=claim(item);src=inv[addr];need(src['envelope_hash']==item['source_envelope_hash'],'source '+addr)
        outcome,detail,used=evaluate(ident,records,file_rows);rule=RULES.get(ident);state=confidence=None
        if outcome=='SUPPORTED':state,confidence=rule[1],rule[2]
        elif outcome=='DISPROVED':state,confidence='OUT-OF-SCOPE CANDIDATE',98
        matrix.append({'composite_address':addr,'original_identifier':ident,'claim':text,'predicate':rule[0] if rule else 'EXTERNAL_EVIDENCE_REQUIRED','outcome':outcome,'detail':detail,'result':'DECIDED' if state else 'REMAIN_QUEUED'})
        if not state:
            q=dict(item)
            if outcome=='EXTERNAL_REQUIRED':missing,method,block,reopen=EXTERNAL[ident]
            else:
                paths=', '.join(sorted({x['path'] for x in used})) or 'none'
                missing=f'The complete repository predicate is not satisfied. Current partial evidence paths: {paths}. Predicate detail: {json.dumps(detail,sort_keys=True)}.';method='Gather or approve the missing predicate components, bind versions and digests, then independently rerun this same rule.';block='Current repository evidence is partial rather than complete proof or complete disproof.';reopen='A relevant manifest, lock, policy, matrix, receipt, version, digest, or configuration changes.'
            q['missing_proof']=f'{missing} Preserved claim: {text}';q['recommended_acquisition_method']=method;q['decision_blocked_until']=block;q['reopening_trigger']=reopen;remaining.append(q);continue
        ev=[evidence('DP-SOURCE-'+addr,f'{I.relative_to(R)}#{addr}',src['envelope_hash'],'Preserves the immutable source claim and address.'),evidence('DP-QUEUE-'+addr,f'{Q.relative_to(R)}#{addr}',f'sha256:{QUEUE_SHA}#{addr}','Proves complete-family membership.'),evidence('DP-PLAN-'+addr,f'{PLAN.relative_to(R)}#{rule[0]}',f'sha256:{plansha}#{rule[0]}','Binds the reviewed predicate.'),evidence('DP-CORPUS-'+addr,'current authoritative dependency-platform corpus','sha256:'+corp,'Commits current governing and configuration evidence.'),evidence('DP-CENSUS-'+addr,'complete tracked-file census','sha256:'+fcensus,'Commits the complete repository file census.'),evidence('DP-RUNTIME-'+addr,'effective current runtime corpus','sha256:'+runsha,'Commits the effective route and configuration.'),evidence('DP-MAIN-'+addr,'origin/main','commit:'+mainsha,'Anchors evaluation to current main.')]
        for n,x in enumerate(used[:20],1):ev.append(evidence(f'DP-FILE-{n:02d}-'+addr,x['path'],'sha256:'+x['sha256'],'Current file used by the predicate.'))
        reason=REASONS[ident] if outcome=='SUPPORTED' else 'Complete current verified evidence disproves the preserved limitation claim.'
        decisions.append({'composite_address':addr,'source_inventory_sha256':INVENTORY_SHA,'source_envelope_hash':src['envelope_hash'],'source_block_hash':src['source_block_hash'],'decision_stage':'APPLICABILITY_ONLY','applicability_state':state,'applicability_evidence':ev,'applicability_reasoning_summary':reason,'applicability_confidence':confidence,'primary_destination':None,'secondary_destinations':[],'cross_cutting_laws':[],'semantic_cluster_ids':[],'routing_evidence':[],'routing_rationale':'','routing_confidence':None,'expected_receiving_work':'','expected_completion_evidence':'','unresolved_dependencies':[],'hold_reason':'','reopening_conditions':['A predicate component, current version, configuration, governing record, or receipt changes.','The main anchor or source-envelope digest changes.'],'decision_version':'Packet-01.5-Dependency-Platform-Family-v1','decision_author':plan['decision_author'],'routing_decision_verifier':plan['decision_verifier'],'closure_state':'OPEN'})
    manifest={'packet':'01.5','family':FAMILY,'records':14,'source_queue_sha256':QUEUE_SHA,'source_inventory_sha256':INVENTORY_SHA,'main_commit_anchor':mainsha,'authoritative_corpus_sha256':corp,'file_census_sha256':fcensus,'runtime_corpus_sha256':runsha,'identities':[{'composite_address':x['composite_address'],'source_record_ordinal':x['source_record_ordinal'],'original_identifier':x['original_identifier'],'source_envelope_hash':x['source_envelope_hash']} for x in family]}
    MAN.write_text(json.dumps(manifest,indent=2)+'\n');dump_lines(DEC,decisions);dump_lines(REM,remaining);MAT.write_text(json.dumps({'packet':'01.5','family':FAMILY,'records':14,'decided':len(decisions),'queued':len(remaining),'matrix':matrix},indent=2)+'\n');states={}
    for d in decisions:states[d['applicability_state']]=states.get(d['applicability_state'],0)+1
    COV.write_text(json.dumps({'packet':'01.5','family':FAMILY,'family_records':14,'decided_records':len(decisions),'remaining_queued_records':len(remaining),'unknown_hold_created':0,'coverage_complete':len(decisions)+len(remaining)==14,'decision_states':states,'routing_assignments':0,'grouping_assignments':0,'source_records_removed_or_closed':0},indent=2)+'\n')
    SUM.write_text(f'# Packet 01.5 — Dependency or Platform State Family v1\n\nSTATUS: BUILT — PENDING INDEPENDENT VERIFICATION\nFAMILY RECORDS: 14\nEVIDENCE-SUPPORTED DECISIONS: {len(decisions)}\nREMAINING QUEUED: {len(remaining)}\nUNKNOWN — HOLD CREATED: 0\nROUTING ASSIGNMENTS: 0\nGROUPING ASSIGNMENTS: 0\n\nRepository-provable state is separated from external provider, account, device, cloud, and platform state.\n\nStop before routing, destinations, grouping, closure, implementation, or Packet 04.\n')
    need(I.read_bytes()==rawi,'inventory changed');print(f'PASS: built {len(decisions)} decisions and {len(remaining)} queues')
if __name__=='__main__':main()
