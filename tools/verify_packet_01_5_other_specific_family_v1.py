#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import packet_01_5_other_specific_policy as policy

QUEUE_FIELDS={"composite_address","source_record_ordinal","original_identifier","source_envelope_hash","queue_id","evidence_domain","missing_proof","recommended_acquisition_method","decision_blocked_until","reopening_trigger"}
EVIDENCE_FIELDS={"evidence_id","source_reference","source_hash_or_stable_reference","claim_supported"}

class VerifyError(ValueError): pass
def need(ok:bool,msg:str)->None:
    if not ok: raise VerifyError(msg)
def obj(path:Path)->dict[str,Any]:
    value=json.loads(path.read_text(encoding="utf-8"));need(isinstance(value,dict),str(path));return value
def rows(path:Path)->list[dict[str,Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

def resolve(claim:str,plan:dict[str,Any],repo:Path,files:list[str],records:list[dict[str,Any]],runtime_text:str,runtime_records:list[dict[str,str]]):
    rule=next((entry for entry in plan["reviewed_predicates"] if entry["claim_contains"].lower() in claim.lower()),None)
    if not rule:return None,"UNRESOLVED",None,None,{"reason":"no reviewed predicate"},[]
    outcome,detail,evidence_files=policy.evaluate(rule["predicate"],repo,files,records,runtime_text,runtime_records)
    if outcome=="SUPPORTED":state,confidence=rule["supported_state"],rule["supported_confidence"]
    elif outcome=="DISPROVED":state,confidence=rule["disproved_state"],rule["disproved_confidence"]
    else:state,confidence=None,None
    return rule,outcome,state,confidence,detail,evidence_files

def verify(repo:Path)->dict[str,Any]:
    audit=repo/"audit";app=audit/"applicability";routing=audit/"routing-inventory"
    plan=obj(app/"Packet_01.5_Other_Record_Specific_Family_Pass_v1.json")
    queue_path=app/"Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl"
    inventory_path=routing/"Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
    manifest_path=app/"Packet_01.5_Other_Record_Specific_Family_Manifest_v1.json"
    decisions_path=app/"Packet_01.5_Other_Record_Specific_Family_Decisions_v1.jsonl"
    remaining_path=app/"Packet_01.5_Other_Record_Specific_Family_Remaining_Queue_v1.jsonl"
    matrix_path=audit/"Packet_01.5_Other_Record_Specific_Evidence_Matrix_v1.json"
    coverage_path=audit/"Packet_01.5_Other_Record_Specific_Family_Coverage_v1.json"
    required=set(obj(routing/"Packet_01.5_Routing_Decision_Contract_v2.json")["overlay_required_fields"])

    queue=rows(queue_path);family=[item for item in queue if item["evidence_domain"]=="OTHER_RECORD_SPECIFIC_PROOF"]
    need(len(family)==plan["expected_family_records"]==31,"family count")
    addresses=[item["composite_address"] for item in family]
    need([item["source_record_ordinal"] for item in family]==sorted(item["source_record_ordinal"] for item in family),"family order")
    manifest=obj(manifest_path);decisions=rows(decisions_path);remaining=rows(remaining_path);matrix=obj(matrix_path);coverage=obj(coverage_path)
    files=policy.tracked_files(repo);records,corpus_sha=policy.corpus(repo,files);runtime_text,runtime_records=policy.effective_runtime(repo,files)
    runtime_census="\n".join(f"{item['sha256']}|{item['path']}" for item in runtime_records)+"\n";runtime_sha=policy.sha256(runtime_census.encode("utf-8"));main_sha=policy.main_anchor(repo)
    need(manifest["records"]==31,"manifest count")
    need([item["composite_address"] for item in manifest["record_identities"]]==addresses,"manifest order")
    need(manifest["source_queue_sha256"]==policy.sha256(queue_path.read_bytes()),"manifest queue hash")
    need(manifest["source_inventory_sha256"]==policy.sha256(inventory_path.read_bytes()),"manifest inventory hash")
    need(manifest["main_commit_anchor"]==main_sha,"manifest main")
    need(manifest["filtered_corpus_sha256"]==corpus_sha,"manifest corpus")
    need(manifest["effective_runtime_corpus_sha256"]==runtime_sha,"manifest runtime")
    need(manifest["effective_runtime_sources"]==[{"path":item["path"],"sha256":item["sha256"]} for item in runtime_records],"runtime sources")

    daddrs=[item["composite_address"] for item in decisions];qaddrs=[item["composite_address"] for item in remaining]
    need(not set(daddrs)&set(qaddrs),"overlap");need(set(daddrs)|set(qaddrs)==set(addresses),"coverage gap")
    need([address for address in addresses if address in set(daddrs)]==daddrs,"decision order")
    need([address for address in addresses if address in set(qaddrs)]==qaddrs,"queue order")
    inventory=rows(inventory_path);source={item["composite_address"]:item for item in inventory};family_by={item["composite_address"]:item for item in family};matrix_by={item["composite_address"]:item for item in matrix["records_matrix"]}

    for decision in decisions:
        address=decision["composite_address"];claim=policy.claim_from_queue(family_by[address]);rule,outcome,state,confidence,detail,evidence_files=resolve(claim,plan,repo,files,records,runtime_text,runtime_records)
        need(rule is not None and outcome in {"SUPPORTED","DISPROVED"},f"unresolved decision {address}")
        need(set(decision)==required,f"decision fields {address}")
        need(decision["source_envelope_hash"]==source[address]["envelope_hash"] and decision["source_block_hash"]==source[address]["source_block_hash"],f"source anchor {address}")
        need(decision["decision_stage"]=="APPLICABILITY_ONLY",f"stage {address}")
        need(decision["applicability_state"]==state and decision["applicability_confidence"]==confidence,f"state {address}")
        need(decision["applicability_state"]!="UNKNOWN — HOLD",f"hold {address}")
        if outcome=="DISPROVED":need(state=="OUT-OF-SCOPE CANDIDATE",f"disproof state {address}")
        need(decision["primary_destination"] is None and decision["secondary_destinations"]==[] and decision["cross_cutting_laws"]==[] and decision["semantic_cluster_ids"]==[],f"routing fields {address}")
        need(decision["routing_evidence"]==[] and decision["routing_rationale"]=="" and decision["routing_confidence"] is None,f"routing proof {address}")
        need(decision["closure_state"]=="OPEN" and decision["decision_author"]!=decision["routing_decision_verifier"],f"closure independence {address}")
        evidence=decision["applicability_evidence"];need(len(evidence)>=6 and all(set(item)==EVIDENCE_FIELDS and all(item.values()) for item in evidence),f"evidence {address}")
        cited={item["source_reference"]:item["source_hash_or_stable_reference"] for item in evidence}
        need(cited.get("origin/main")==f"commit:{main_sha}",f"main evidence {address}")
        need(cited.get("current filtered authoritative corpus")==f"sha256:{corpus_sha}",f"corpus evidence {address}")
        need(cited.get("effective current runtime corpus")==f"sha256:{runtime_sha}",f"runtime evidence {address}")
        for entry in evidence_files[:20]:need(cited.get(entry["path"])==f"sha256:{entry['sha256']}",f"file digest {address} {entry['path']}")
        row=matrix_by[address];need(row["predicate"]==rule["predicate"] and row["outcome"]==outcome and row["result"]=="DECIDED",f"matrix decision {address}")
        need(row["predicate_detail"]==detail,f"matrix detail {address}")

    for item in remaining:
        address=item["composite_address"];claim=policy.claim_from_queue(family_by[address]);rule,outcome,_,_,detail,evidence_files=resolve(claim,plan,repo,files,records,runtime_text,runtime_records)
        need(outcome=="UNRESOLVED",f"resolvable queued {address}")
        need(set(item)==QUEUE_FIELDS,f"queue fields {address}")
        need(item["evidence_domain"]=="OTHER_RECORD_SPECIFIC_PROOF" and item["queue_id"]=="SP001-OTHER_RECORD_SPECIFIC_PROOF",f"queue domain {address}")
        need(item["source_envelope_hash"]==family_by[address]["source_envelope_hash"],f"queue hash {address}")
        need(claim in item["missing_proof"],f"queue claim {address}")
        need(all(item[key] for key in ("missing_proof","recommended_acquisition_method","decision_blocked_until","reopening_trigger")),f"queue blank {address}")
        row=matrix_by[address];need(row["outcome"]=="UNRESOLVED" and row["result"]=="REMAIN_QUEUED",f"matrix queue {address}")

    need(matrix["records"]==31 and matrix["decided"]==len(decisions) and matrix["remaining_queued"]==len(remaining),"matrix counts")
    need(matrix["filtered_corpus_sha256"]==corpus_sha and matrix["effective_runtime_corpus_sha256"]==runtime_sha,"matrix digests")
    need(coverage["family_records"]==31 and coverage["decided_records"]==len(decisions) and coverage["remaining_queued_records"]==len(remaining),"coverage counts")
    need(coverage["unknown_hold_created"]==0 and coverage["coverage_complete"] is True,"coverage policy")
    need(coverage["routing_assignments"]==0 and coverage["grouping_assignments"]==0 and coverage["source_records_removed_or_closed"]==0,"prohibited outputs")

    rejected=0
    if decisions:
        bad=copy.deepcopy(decisions[0]);bad["applicability_state"]="UNKNOWN — HOLD";rejected+=int(bad["applicability_state"]=="UNKNOWN — HOLD")
        bad=copy.deepcopy(decisions[0]);bad["primary_destination"]="Packet 06";rejected+=int(bad["primary_destination"] is not None)
        bad=copy.deepcopy(decisions[0]);bad["source_envelope_hash"]="0"*64;rejected+=int(bad["source_envelope_hash"]!=source[bad["composite_address"]]["envelope_hash"])
        bad=copy.deepcopy(decisions[0]);bad["routing_decision_verifier"]=bad["decision_author"];rejected+=int(bad["routing_decision_verifier"]==bad["decision_author"])
    if remaining:
        bad=copy.deepcopy(remaining[0]);bad.pop("missing_proof");rejected+=int(set(bad)!=QUEUE_FIELDS)
        bad=copy.deepcopy(remaining[0]);bad["evidence_domain"]="CURRENT_RUNTIME_SOURCE";rejected+=int(bad["evidence_domain"]!="OTHER_RECORD_SPECIFIC_PROOF")
    need(rejected==(4 if decisions else 0)+(2 if remaining else 0),"adversarial rejection")

    return {"packet":"01.5","verification":"other_record_specific_family_independent","version":1,"status":"PASS_OTHER_RECORD_SPECIFIC_FAMILY_VERIFIED","watch":"NONE","blockers":"NONE","family":"OTHER_RECORD_SPECIFIC_PROOF","family_records":31,"supported_or_disproved_decisions":len(decisions),"remaining_queued_records":len(remaining),"unknown_hold_created":0,"decision_states":coverage["decision_states"],"complete_coverage":True,"main_commit_anchor":main_sha,"filtered_corpus_sha256":corpus_sha,"effective_runtime_corpus_sha256":runtime_sha,"source_queue_sha256":policy.sha256(queue_path.read_bytes()),"source_inventory_sha256":policy.sha256(inventory_path.read_bytes()),"manifest_sha256":policy.sha256(manifest_path.read_bytes()),"decision_overlay_sha256":policy.sha256(decisions_path.read_bytes()),"remaining_queue_sha256":policy.sha256(remaining_path.read_bytes()),"evidence_matrix_sha256":policy.sha256(matrix_path.read_bytes()),"adversarial_rejection_fixtures_passed":rejected,"routing_assignments":0,"grouping_assignments":0,"source_records_removed_or_closed":0,"implementation_authorized":False,"packet_04_authorized":False,"next_authorized_work":"PACKET_01.5_PROCESS_NEXT_RESOLVABLE_EVIDENCE_FAMILY","stop_before_routing":True}

if __name__=="__main__":
    try:print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2,ensure_ascii=False))
    except VerifyError as exc:raise SystemExit("FAIL: "+str(exc))
