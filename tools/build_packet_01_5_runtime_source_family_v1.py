#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import packet_01_5_runtime_source_family_policy as policy

REPO=Path(__file__).resolve().parents[1]
AUDIT=REPO/"audit"; APP=AUDIT/"applicability"; ROUTING=AUDIT/"routing-inventory"
PLAN=APP/"Packet_01.5_Runtime_Source_Family_Pass_v1.json"
QUEUE=APP/"Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl"
INVENTORY=ROUTING/"Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
CONTRACT=ROUTING/"Packet_01.5_Routing_Decision_Contract_v2.json"
MANIFEST=APP/"Packet_01.5_Runtime_Source_Family_Manifest_v1.json"
DECISIONS=APP/"Packet_01.5_Runtime_Source_Family_Decisions_v1.jsonl"
REMAINING=APP/"Packet_01.5_Runtime_Source_Family_Remaining_Queue_v1.jsonl"
MATRIX=AUDIT/"Packet_01.5_Runtime_Source_Family_Evidence_Matrix_v1.json"
COVERAGE=AUDIT/"Packet_01.5_Runtime_Source_Family_Coverage_v1.json"
SUMMARY=AUDIT/"Packet_01.5_Runtime_Source_Family_v1.md"

INV_SHA="76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477"
QUEUE_SHA="1b28dbfd69e9af4b51ce5cf4eb4e43d4ed4aaea107129b2e11b7b41c9dfd861a"


def need(ok:bool,msg:str)->None:
    if not ok: raise SystemExit("FAIL: "+msg)
def obj(path:Path)->dict[str,Any]:
    value=json.loads(path.read_text(encoding="utf-8")); need(isinstance(value,dict),str(path)); return value
def rows(path:Path)->list[dict[str,Any]]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()]
def evidence(eid,ref,stable,claim):
    return {"evidence_id":eid,"source_reference":ref,"source_hash_or_stable_reference":stable,"claim_supported":claim}
def unresolved_entry(item:dict[str,Any],claim:str,detail:dict[str,Any]|None=None)->dict[str,Any]:
    if "Installed iPhone Home Screen" in claim:
        proof="Run cold-start, warm-start, offline, cache-update, and storage-clear tests on an installed iPhone Home Screen instance; record iOS/Safari versions and frame targets."
    elif "live outermost Resident wrapper order" in claim:
        proof="Instrument a live installed session and capture the complete outer-to-inner frame chain after Open Latest App, including injected support scripts and timestamps."
    else:
        proof="Static repository evidence did not prove the full claim. Capture a bounded current-runtime test or a more specific source predicate tied to this permanent address."
    if detail and detail.get("error"): proof+=" Predicate error: "+str(detail["error"])
    result=dict(item)
    result["missing_proof"]=f"{proof} Preserved claim: {claim}"
    result["recommended_acquisition_method"]="Use the effective current map and source hashes, then execute the smallest runtime test that can prove or disprove the full claim."
    result["decision_blocked_until"]="The required source or runtime evidence is captured, hashed, and independently verified."
    return result


def main()->None:
    plan=obj(PLAN); need(plan["family"]=="CURRENT_RUNTIME_SOURCE","wrong family")
    need(plan["decision_author"]!=plan["decision_verifier"],"author equals verifier")
    inv_raw=INVENTORY.read_bytes(); need(policy.sha256(inv_raw)==INV_SHA,"inventory hash changed")
    q_raw=QUEUE.read_bytes(); need(policy.sha256(q_raw)==QUEUE_SHA,"source queue hash changed")
    inventory=rows(INVENTORY); source={x["composite_address"]:x for x in inventory}
    family=[x for x in rows(QUEUE) if x["evidence_domain"]=="CURRENT_RUNTIME_SOURCE"]
    need(len(family)==plan["expected_family_records"]==20,"runtime family count changed")
    need([x["source_record_ordinal"] for x in family]==sorted(x["source_record_ordinal"] for x in family),"family order changed")
    files=policy.tracked_files(REPO); corpus,runtime_files=policy.current_corpus(REPO,files)
    census_text="\n".join(files)+"\n"; census_sha=policy.sha256(census_text.encode())
    plan_sha=policy.sha256(PLAN.read_bytes()); queue_sha=policy.sha256(q_raw)
    evidence_paths=["pmp-current-map-v9.json","pmp-app-current.html","pmp-route-guardian-current-loader-v14.html","pmp-current-inner-cleanbug-rgcontrols-v4.html"]
    evidence_hashes={name:policy.sha256((REPO/name).read_bytes()) for name in evidence_paths}
    rules=plan["decision_rules"]
    decisions=[]; remaining=[]; matrix=[]
    for item in family:
        address=item["composite_address"]; claim=policy.claim_from_queue(item); src=source[address]
        need(src["source_envelope_hash"] if "source_envelope_hash" in src else True,"source")
        rule=next((r for r in rules if r["claim_contains"] in claim),None)
        passed=False; detail={"reason":"no matching reviewed rule"}; predicate=None
        if rule:
            predicate=rule["predicate"]; passed,detail=policy.evaluate(predicate,REPO,files,corpus)
        matrix.append({"composite_address":address,"original_identifier":item["original_identifier"],"claim":claim,"predicate":predicate,"predicate_passed":passed,"predicate_detail":detail,"result":"DECIDED" if passed else "REMAIN_QUEUED"})
        if not passed:
            remaining.append(unresolved_entry(item,claim,detail)); continue
        entries=[
            evidence(f"RSF-SOURCE-{address}",f"{INVENTORY.relative_to(REPO)}#{address}",src["envelope_hash"],"Preserves the immutable source claim and permanent address."),
            evidence(f"RSF-QUEUE-{address}",f"{QUEUE.relative_to(REPO)}#{address}",f"sha256:{queue_sha}#{address}","Proves the record belonged to the current-runtime-source evidence family."),
            evidence(f"RSF-PLAN-{address}",f"{PLAN.relative_to(REPO)}#{predicate}",f"sha256:{plan_sha}#{predicate}","Binds the record to the reviewed source predicate and applicability state."),
            evidence(f"RSF-CENSUS-{address}","git ls-files",f"sha256:{census_sha}","Provides the complete tracked-file census used by absence and configuration predicates."),
        ]
        for name in evidence_paths:
            entries.append(evidence(f"RSF-{Path(name).stem}-{address}",name,f"sha256:{evidence_hashes[name]}","Current runtime source used by the reviewed predicate."))
        decision={
          "composite_address":address,"source_inventory_sha256":INV_SHA,"source_envelope_hash":src["envelope_hash"],"source_block_hash":src["source_block_hash"],
          "decision_stage":"APPLICABILITY_ONLY","applicability_state":rule["state"],"applicability_evidence":entries,
          "applicability_reasoning_summary":policy.REASONS[predicate],"applicability_confidence":rule["confidence"],
          "primary_destination":None,"secondary_destinations":[],"cross_cutting_laws":[],"semantic_cluster_ids":[],
          "routing_evidence":[],"routing_rationale":"","routing_confidence":None,"expected_receiving_work":"","expected_completion_evidence":"",
          "unresolved_dependencies":[],"hold_reason":"","reopening_conditions":policy.REOPEN[predicate],
          "decision_version":"Packet-01.5-Runtime-Source-Family-v1","decision_author":plan["decision_author"],
          "routing_decision_verifier":plan["decision_verifier"],"closure_state":"OPEN"
        }
        decisions.append(decision)
    manifest={"packet":"01.5","family":"CURRENT_RUNTIME_SOURCE","records":20,"source_queue_sha256":queue_sha,"source_inventory_sha256":INV_SHA,"repository_census_sha256":census_sha,"runtime_source_files":runtime_files,"record_identities":[{"composite_address":x["composite_address"],"source_record_ordinal":x["source_record_ordinal"],"original_identifier":x["original_identifier"],"source_envelope_hash":x["source_envelope_hash"]} for x in family]}
    MANIFEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    DECISIONS.write_text("".join(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(",",":"))+"\n" for x in decisions),encoding="utf-8")
    REMAINING.write_text("".join(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(",",":"))+"\n" for x in remaining),encoding="utf-8")
    MATRIX.write_text(json.dumps({"packet":"01.5","family":"CURRENT_RUNTIME_SOURCE","records":20,"decided":len(decisions),"remaining_queued":len(remaining),"repository_census_sha256":census_sha,"source_hashes":evidence_hashes,"records_matrix":matrix},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    states={};
    for x in decisions: states[x["applicability_state"]]=states.get(x["applicability_state"],0)+1
    coverage={"packet":"01.5","family":"CURRENT_RUNTIME_SOURCE","family_records":20,"decided_records":len(decisions),"remaining_queued_records":len(remaining),"unknown_hold_created":0,"coverage_complete":len(decisions)+len(remaining)==20,"decision_states":states,"routing_assignments":0,"grouping_assignments":0,"source_records_removed_or_closed":0}
    COVERAGE.write_text(json.dumps(coverage,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    SUMMARY.write_text(f"""# Packet 01.5 — Runtime Source Evidence Family v1

STATUS: BUILT — PENDING INDEPENDENT VERIFICATION
FAMILY RECORDS: 20
EVIDENCE-SUPPORTED DECISIONS: {len(decisions)}
REMAINING QUEUED: {len(remaining)}
UNKNOWN — HOLD CREATED: 0
ROUTING ASSIGNMENTS: 0
GROUPING ASSIGNMENTS: 0

The full current-runtime-source family was processed in permanent source order. Reviewed static predicates produced {len(decisions)} applicability decisions. Claims requiring live observation or stronger proof remain queued with more specific acquisition instructions.

Stop before routing, grouping, closure, implementation, or Packet 04.
""",encoding="utf-8")
    need(INVENTORY.read_bytes()==inv_raw,"inventory changed")
    print(f"PASS: runtime-source family built with {len(decisions)} decisions and {len(remaining)} queued")

if __name__=="__main__": main()
