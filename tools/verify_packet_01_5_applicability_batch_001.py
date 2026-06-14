#!/usr/bin/env python3
"""Verify Packet 01.5 Applicability Batch 001 without changing it."""
from __future__ import annotations

import gzip, hashlib, json
from collections import Counter
from datetime import date
from pathlib import Path

R = Path(__file__).resolve().parents[1]
A = R / "audit"
PARENT = A / "routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
CHILD = A / "routing-inventory/Packet_01.5_Applicability_Inventory_v2_Batch_001.jsonl"
CHILD_GZ = A / "routing-inventory/Packet_01.5_Applicability_Inventory_v2_Batch_001.jsonl.gz"
MANIFEST = A / "routing-inventory/Packet_01.5_Applicability_Inventory_v2_Batch_001.manifest.json"
PLAN = A / "routing-batches/Packet_01.5_Applicability_Batch_001_Plan_v1.json"
CATALOG = A / "routing-evidence/Packet_01.5_Project_Contact_Evidence_Catalog_v1.json"
OUTJ = A / "routing-batches/Packet_01.5_Applicability_Batch_001_Independent_Verification_v1.json"
OUTM = A / "routing-batches/Packet_01.5_Applicability_Batch_001_Independent_Verification_v1.md"
STATUS = A / "Packet_01.5_Applicability_Classification_Status_v77.md"
PARENT_SHA = "76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477"
IMMUTABLE = ["composite_address","source_set","source_path","source_pass","source_file_hash","source_record_ordinal","original_identifier","original_heading","original_body","source_block_hash","harm_text","overlap_text","legacy_exception_codes","normalization_version"]
EVIDENCE_FIELDS = {"evidence_id","evidence_type","source_reference","source_hash_or_stable_reference","contact_path_explanation","decision_rationale"}
EVIDENCE_TYPES = {"CURRENT_CONTACT","PLANNED_CONTACT","ABSENT_CONTACT","SCOPE_EXCLUSION"}


def die(message): raise SystemExit("FAIL: " + message)
def req(value, message):
    if not value: die(message)
def h(data): return hashlib.sha256(data).hexdigest()
def canonical(value): return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
def env_hash(value):
    copy=dict(value); copy.pop("envelope_hash",None); return h(canonical(copy))
def obj(path): return json.loads(path.read_text())
def jsonl(path):
    raw=path.read_bytes(); return [json.loads(line) for line in raw.splitlines()],raw


def main():
    parent,parent_raw=jsonl(PARENT); child,child_raw=jsonl(CHILD)
    manifest,plan,catalog=obj(MANIFEST),obj(PLAN),obj(CATALOG)
    req(h(parent_raw)==PARENT_SHA,"parent hash")
    req(len(parent)==len(child)==2750,"count")
    req(manifest["child"]["sha256"]==h(child_raw),"child hash")
    req(gzip.decompress(CHILD_GZ.read_bytes())==child_raw,"gzip reconstruction")
    req([x["composite_address"] for x in parent]==[x["composite_address"] for x in child],"address order")
    req(len({x["composite_address"] for x in child})==2750,"address uniqueness")

    expected=[f"P01.5::B::{n:04d}" for n in range(1,11)]
    decisions={x["address"]:x for x in plan["decisions"]}
    req(plan["selection"]["addresses"]==expected and set(decisions)==set(expected),"plan selection")
    catalog_ids={x["evidence_id"] for x in catalog["current_capabilities"]+catalog["boundary_evidence"]}
    req(len(catalog_ids)==26,"catalog IDs")

    changed=[]
    for before,after in zip(parent,child):
        address=before["composite_address"]
        req(after["envelope_hash"]==env_hash(after),f"envelope hash {address}")
        for field in IMMUTABLE: req(after.get(field)==before.get(field),f"immutable {field} {address}")
        req(after.get("routing_state")=="UNROUTED" and after.get("primary_destination") is None,f"routing {address}")
        for field in ["secondary_destinations","cross_cutting_laws","watch_triggers","semantic_cluster_ids"]: req(after.get(field)==[],f"blank {field} {address}")
        if before!=after:
            changed.append(address); decision=decisions.get(address); req(decision is not None,f"unplanned {address}")
            req(after["original_identifier"]==decision["original_identifier"],f"identifier {address}")
            req(after["applicability_state"]=="ACTIVE_CONDITIONAL_RISK",f"state {address}")
            req(after["applicability_batch_id"]=="P01.5-APP-B001",f"batch {address}")
            req(after["applicability_parent_envelope_hash"]==before["envelope_hash"],f"parent envelope {address}")
            evidence=after["applicability_evidence"]; req(isinstance(evidence,list) and len(evidence)>=2,f"evidence {address}")
            refs=set(); source_entries=0; ids=[]
            for item in evidence:
                req(EVIDENCE_FIELDS<=set(item),f"evidence schema {address}")
                req(item["evidence_type"] in EVIDENCE_TYPES,f"evidence type {address}")
                req(all(item[k] for k in EVIDENCE_FIELDS),f"empty evidence {address}")
                ids.append(item["evidence_id"])
                ref=item.get("catalog_evidence_id")
                if ref is None: source_entries+=1
                else: req(ref in catalog_ids,f"catalog reference {address}"); refs.add(ref)
            req(len(ids)==len(set(ids)),f"evidence ID uniqueness {address}")
            req(source_entries==1 and refs==set(decision["catalog_evidence_ids"]),f"evidence set {address}")
        else: req(address not in decisions,f"planned unchanged {address}")

    req(changed==expected,"changed sequence")
    states=Counter(x["applicability_state"] for x in child)
    req(states==Counter({"UNCLASSIFIED":2740,"ACTIVE_CONDITIONAL_RISK":10}),"state totals")
    req(manifest["changed_envelopes"]==10 and manifest["routing_assignments"]==0,"manifest totals")
    child_sha=h(child_raw)
    result={"packet":"01.5","verification":"applicability_batch_001_independent","version":1,"verification_date":date.today().isoformat(),"status":"PASS_ACCEPTED","watch":"NONE","blockers":"NONE","batch":"P01.5-APP-B001","parent_inventory_sha256":PARENT_SHA,"child_inventory_sha256":child_sha,"combined_envelopes":2750,"unique_addresses":2750,"classified_envelopes":10,"active_conditional_risk":10,"unclassified":2740,"immutable_field_match":"PASS","address_sequence_match":"PASS","evidence_schema_match":"PASS","catalog_reference_match":"PASS","routing_fields_blank":"PASS","gzip_reverse_reconstruction":"PASS","routing_assignments":0,"source_count_delta":0,"record_completion_count":0,"next_batch_ready":True}
    OUTJ.write_text(json.dumps(result,indent=2)+"\n")
    OUTM.write_text(f"""# Packet 01.5 — Applicability Batch 001 Independent Verification v1

STATUS: PASS — BATCH ACCEPTED
WATCH: NONE
BLOCKERS: NONE
ROUTING ASSIGNMENTS: 0

- Parent envelopes: 2750
- Child envelopes: 2750
- Unique addresses: 2750
- Changed envelopes: 10
- ACTIVE_CONDITIONAL_RISK: 10
- UNCLASSIFIED: 2740
- Parent SHA-256: `{PARENT_SHA}`
- Child SHA-256: `{child_sha}`
- Immutable source-field equality: PASS
- Address-sequence equality: PASS
- Evidence schema and catalog references: PASS
- Destination fields remain blank: PASS
- Deterministic gzip reconstruction: PASS
- Source count delta: 0
- Record completion count: 0

`P01.5::B::0001` through `P01.5::B::0010` are accepted as `ACTIVE_CONDITIONAL_RISK` because each depends on a planned or optional AI/provider/backend contact path rather than the presently verified local/manual Resident reasoning path.

FINAL RESULT: `PASS — APPLICABILITY BATCH 001 ACCEPTED`

WATCH: NONE

BLOCKERS: NONE
""")
    STATUS.write_text("""# Packet 01.5 — Applicability Classification Status v77

STATUS: BATCH 001 ACCEPTED
WATCH: NONE
BLOCKERS: NONE
ROUTING START: AUTHORIZED
APPLICABILITY CLASSIFICATIONS COMPLETED: 10 OF 2750
ROUTING ASSIGNMENTS COMPLETED: 0
SEMANTIC COMBINATION: NOT AUTHORIZED
INDIVIDUAL RECORD CLOSURE: NOT AUTHORIZED
PACKET 04: NOT AUTHORIZED

## Accepted state counts

- CURRENT_DEFECT: 0
- ACTIVE_CONDITIONAL_RISK: 10
- DORMANT_FUTURE_RISK: 0
- OUT_OF_SCOPE_CANDIDATE: 0
- UNCLASSIFIED: 2740

## Preservation

- Total envelopes: 2750
- Unique addresses: 2750
- Source wording and hashes preserved: PASS
- Destination fields populated: 0
- Source count delta: 0
- Record completion count: 0

## Next required action

Prepare and independently verify Applicability Batch 002 for `P01.5::B::0011` through `P01.5::B::0020`, using the accepted Batch 001 child inventory as the parent and keeping destination fields blank.
""")
    print("PASS — Applicability Batch 001 independently accepted")

if __name__=="__main__": main()
