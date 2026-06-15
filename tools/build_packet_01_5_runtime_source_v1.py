#!/usr/bin/env python3
from __future__ import annotations
import json
from runtime_source_evaluate import compute
from runtime_source_git import FAMILY,INVENTORY_SHA,QUEUE_SHA,sha
from runtime_source_paths import *

def write_jsonl(path,items):path.write_text(''.join(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'))+'\n' for x in items),encoding='utf-8')

def main():
    data=compute();graph=data['graph'];family=data['family'];decisions=data['decisions'];remaining=data['remaining'];matrix=data['matrix'];tests=data['bounded_tests']
    PRECEDENCE.write_text(json.dumps(graph,indent=2)+'\n')
    TESTS.write_text(json.dumps({'packet':'01.5','family':FAMILY,'main_commit':graph['main_commit'],'graph_sha256':graph['graph_sha256'],'tests':tests,'status':'PASS'},indent=2)+'\n')
    MANIFEST.write_text(json.dumps({'packet':'01.5','family':FAMILY,'records':20,'main_commit_anchor':graph['main_commit'],'source_queue_sha256':QUEUE_SHA,'source_inventory_sha256':INVENTORY_SHA,'runtime_graph_sha256':graph['graph_sha256'],'identities':[{'composite_address':x['composite_address'],'source_record_ordinal':x['source_record_ordinal'],'original_identifier':x['original_identifier'],'source_envelope_hash':x['source_envelope_hash']} for x in family]},indent=2)+'\n')
    write_jsonl(DECISIONS,decisions);write_jsonl(REMAINING,remaining)
    MATRIX.write_text(json.dumps({'packet':'01.5','family':FAMILY,'records':20,'decided':len(decisions),'queued':len(remaining),'matrix':matrix},indent=2)+'\n')
    states={}
    for item in decisions:states[item['applicability_state']]=states.get(item['applicability_state'],0)+1
    COVERAGE.write_text(json.dumps({'packet':'01.5','family':FAMILY,'family_records':20,'decided_records':len(decisions),'remaining_queued_records':len(remaining),'unknown_hold_created':0,'coverage_complete':len(decisions)+len(remaining)==20,'decision_states':states,'routing_assignments':0,'grouping_assignments':0,'source_records_removed_or_closed':0},indent=2)+'\n')
    SUMMARY.write_text(f'# Packet 01.5 — Current Runtime Source Family v1\n\nSTATUS: BUILT — PENDING INDEPENDENT VERIFICATION\nFAMILY RECORDS: 20\nEVIDENCE-SUPPORTED DECISIONS: {len(decisions)}\nREMAINING QUEUED: {len(remaining)}\nUNKNOWN — HOLD CREATED: 0\nROUTING ASSIGNMENTS: 0\nGROUPING ASSIGNMENTS: 0\n\nEffective-source precedence is bound to authoritative main. Static source decisions are separated from browser, device, and non-runtime evidence queues.\n\nStop before routing, destinations, grouping, closure, implementation, or Packet 04.\n')
    if INVENTORY.read_bytes()!=data['inventory_bytes']:raise SystemExit('FAIL: inventory changed')
    print(f'PASS: built {len(decisions)} decisions and {len(remaining)} queues; graph nodes={len(graph["nodes"])}')
if __name__=='__main__':main()
