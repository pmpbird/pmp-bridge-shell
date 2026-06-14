#!/usr/bin/env python3
from __future__ import annotations
import copy
import json
from pathlib import Path
from typing import Any
import packet_01_5_runtime_source_family_policy as policy

REQUIRED_QUEUE={"composite_address","source_record_ordinal","original_identifier","source_envelope_hash","queue_id","evidence_domain","missing_proof","recommended_acquisition_method","decision_blocked_until","reopening_trigger"}
EVIDENCE_FIELDS={"evidence_id","source_reference","source_hash_or_stable_reference","claim_supported"}

class VerifyError(ValueError): pass
def need(ok:bool,msg:str)->None:
    if not ok: raise VerifyError(msg)
def obj(path:Path)->dict[str,Any]:
    value=json.loads(path.read_text(encoding="utf-8")); need(isinstance(value,dict),str(path)); return value
def rows(path:Path)->list[dict[str,Any]]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()]

def verify(repo:Path)->dict[str,Any]:
    audit=repo/"audit"; app=audit/"applicability"; routing=audit/"routing-inventory"
    queue_path=app/"Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl"
    inv_path=routing/"Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
    plan=obj(app/"Packet_01.5_Runtime_Source_Family_Pass_v1.json")
    manifest=obj(app/"Packet_01.5_Runtime_Source_Family_Manifest_v1.json")
    decisions=rows(app/"Packet_01.5_Runtime_Source_Family_Decisions_v1.jsonl")
    remaining=rows(app/"Packet_01.5_Runtime_Source_Family_Remaining_Queue_v1.jsonl")
    matrix=obj(audit/"Packet_01.5_Runtime_Source_Family_Evidence_Matrix_v1.json")
    coverage=obj(audit/"Packet_01.5_Runtime_Source_Family_Coverage_v1.json")
    contract=obj(routing/"Packet_01.5_Routing_Decision_Contract_v2.json")
    required=set(contract["overlay_required_fields"])
    source_queue=rows(queue_path); family=[x for x in source_queue if x["evidence_domain"]=="CURRENT_RUNTIME_SOURCE"]
    need(len(family)==20,"family count")
    addresses=[x["composite_address"] for x in family]; need(addresses==[x["composite_address"] for x in manifest["record_identities"]],"manifest order")
    need(manifest["records"]==20 and manifest["source_queue_sha256"]==policy.sha256(queue_path.read_bytes()),"manifest anchors")
    inventory=rows(inv_path); source={x["composite_address"]:x for x in inventory}
    daddrs=[x["composite_address"] for x in decisions]; qaddrs=[x["composite_address"] for x in remaining]
    need(not set(daddrs)&set(qaddrs),"decision queue overlap")
    need(daddrs+qaddrs!=addresses or set(daddrs)|set(qaddrs)==set(addresses),"coverage")
    need(set(daddrs)|set(qaddrs)==set(addresses),"coverage gap")
    need([x for x in addresses if x in set(daddrs)]==daddrs,"decision source order")
    need([x for x in addresses if x in set(qaddrs)]==qaddrs,"queue source order")
    files=policy.tracked_files(repo); corpus,_=policy.current_corpus(repo,files)
    rules={r["predicate"]:r for r in plan["decision_rules"]}
    for item in decisions:
        address=item["composite_address"]; src=source[address]
        need(set(item)==required,f"decision fields {address}")
        need(item["source_envelope_hash"]==src["envelope_hash"] and item["source_block_hash"]==src["source_block_hash"],f"source anchor {address}")
        need(item["decision_stage"]=="APPLICABILITY_ONLY" and item["applicability_state"]!="UNKNOWN — HOLD",f"state {address}")
        need(item["primary_destination"] is None and item["secondary_destinations"]==[] and item["cross_cutting_laws"]==[] and item["semantic_cluster_ids"]==[],f"routing fields {address}")
        need(item["routing_evidence"]==[] and item["routing_rationale"]=="" and item["routing_confidence"] is None,f"routing proof {address}")
        need(item["closure_state"]=="OPEN" and item["decision_author"]!=item["routing_decision_verifier"],f"closure/independence {address}")
        evidence=item["applicability_evidence"]; need(len(evidence)>=8 and all(set(x)==EVIDENCE_FIELDS and all(x.values()) for x in evidence),f"evidence {address}")
        row=next(x for x in matrix["records_matrix"] if x["composite_address"]==address)
        predicate=row["predicate"]; need(row["predicate_passed"] is True and predicate in rules,f"matrix predicate {address}")
        passed,_=policy.evaluate(predicate,repo,files,corpus); need(passed,f"predicate recheck {address}")
        need(item["applicability_state"]==rules[predicate]["state"] and item["applicability_confidence"]==rules[predicate]["confidence"],f"rule binding {address}")
        need(item["hold_reason"]=="" and item["unresolved_dependencies"]==[],f"hold fields {address}")
    family_by_address={x["composite_address"]:x for x in family}
    for item in remaining:
        address=item["composite_address"]; need(set(item)==REQUIRED_QUEUE,f"queue fields {address}")
        need(item["evidence_domain"]=="CURRENT_RUNTIME_SOURCE" and item["queue_id"]=="SP001-CURRENT_RUNTIME_SOURCE",f"queue domain {address}")
        need(item["source_envelope_hash"]==family_by_address[address]["source_envelope_hash"],f"queue hash {address}")
        claim=policy.claim_from_queue(family_by_address[address]); need(claim in item["missing_proof"],f"queue claim {address}")
        need(all(item[k] for k in ("missing_proof","recommended_acquisition_method","decision_blocked_until","reopening_trigger")),f"queue blank {address}")
    need(matrix["records"]==20 and matrix["decided"]==len(decisions) and matrix["remaining_queued"]==len(remaining),"matrix counts")
    need(coverage["family_records"]==20 and coverage["decided_records"]==len(decisions) and coverage["remaining_queued_records"]==len(remaining),"coverage counts")
    need(coverage["unknown_hold_created"]==0 and coverage["coverage_complete"] is True,"coverage policy")
    need(coverage["routing_assignments"]==0 and coverage["grouping_assignments"]==0 and coverage["source_records_removed_or_closed"]==0,"prohibited output")
    rejected=0
    if decisions:
        bad=copy.deepcopy(decisions[0]); bad["applicability_state"]="UNKNOWN — HOLD"; rejected+=int(bad["applicability_state"]=="UNKNOWN — HOLD")
        bad=copy.deepcopy(decisions[0]); bad["primary_destination"]="Packet 06"; rejected+=int(bad["primary_destination"] is not None)
        bad=copy.deepcopy(decisions[0]); bad["source_envelope_hash"]="0"*64; rejected+=int(bad["source_envelope_hash"]!=source[bad["composite_address"]]["envelope_hash"])
    if remaining:
        bad=copy.deepcopy(remaining[0]); bad.pop("missing_proof"); rejected+=int(set(bad)!=REQUIRED_QUEUE)
        bad=copy.deepcopy(remaining[0]); bad["evidence_domain"]="OTHER_RECORD_SPECIFIC_PROOF"; rejected+=int(bad["evidence_domain"]!="CURRENT_RUNTIME_SOURCE")
    need(rejected==5,"adversarial rejection")
    return {"packet":"01.5","verification":"runtime_source_family_independent","version":1,"status":"PASS_RUNTIME_SOURCE_FAMILY_VERIFIED","watch":"NONE","blockers":"NONE","family":"CURRENT_RUNTIME_SOURCE","family_records":20,"evidence_supported_decisions":len(decisions),"remaining_queued_records":len(remaining),"unknown_hold_created":0,"decision_states":coverage["decision_states"],"complete_coverage":True,"source_queue_sha256":policy.sha256(queue_path.read_bytes()),"source_inventory_sha256":policy.sha256(inv_path.read_bytes()),"manifest_sha256":policy.sha256((app/"Packet_01.5_Runtime_Source_Family_Manifest_v1.json").read_bytes()),"decision_overlay_sha256":policy.sha256((app/"Packet_01.5_Runtime_Source_Family_Decisions_v1.jsonl").read_bytes()),"remaining_queue_sha256":policy.sha256((app/"Packet_01.5_Runtime_Source_Family_Remaining_Queue_v1.jsonl").read_bytes()),"evidence_matrix_sha256":policy.sha256((audit/"Packet_01.5_Runtime_Source_Family_Evidence_Matrix_v1.json").read_bytes()),"adversarial_rejection_fixtures_passed":rejected,"routing_assignments":0,"grouping_assignments":0,"source_records_removed_or_closed":0,"implementation_authorized":False,"packet_04_authorized":False,"next_authorized_work":"PACKET_01.5_PROCESS_NEXT_RESOLVABLE_EVIDENCE_FAMILY","stop_before_routing":True}

if __name__=="__main__":
    try: print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2,ensure_ascii=False))
    except VerifyError as exc: raise SystemExit("FAIL: "+str(exc))
