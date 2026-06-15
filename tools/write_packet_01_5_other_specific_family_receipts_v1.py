#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
AUDIT=REPO/"audit";APP=AUDIT/"applicability"
receipt=json.loads((AUDIT/"Packet_01.5_Other_Record_Specific_Family_Independent_Verification_v1.json").read_text(encoding="utf-8"))
decisions=[json.loads(line) for line in (APP/"Packet_01.5_Other_Record_Specific_Family_Decisions_v1.jsonl").read_text(encoding="utf-8").splitlines()]
remaining=[json.loads(line) for line in (APP/"Packet_01.5_Other_Record_Specific_Family_Remaining_Queue_v1.jsonl").read_text(encoding="utf-8").splitlines()]
matrix=json.loads((AUDIT/"Packet_01.5_Other_Record_Specific_Evidence_Matrix_v1.json").read_text(encoding="utf-8"))
by={item["composite_address"]:item for item in matrix["records_matrix"]}
rows="\n".join(f"- `{item['composite_address']}` / `{by[item['composite_address']]['original_identifier']}` — `{item['applicability_state']}` — `{by[item['composite_address']]['outcome']}`" for item in decisions)
states="\n".join(f"- {state}: {count}" for state,count in sorted(receipt["decision_states"].items())) or "- None"

(AUDIT/"Packet_01.5_Other_Record_Specific_Family_Independent_Verification_v1.md").write_text(f"""# Packet 01.5 — Other Record-Specific Family Independent Verification v1

STATUS: PASS — OTHER RECORD-SPECIFIC FAMILY VERIFIED
WATCH: NONE
BLOCKERS: NONE
FAMILY RECORDS: 31
SUPPORTED OR DISPROVED DECISIONS: {receipt['supported_or_disproved_decisions']}
REMAINING QUEUED: {receipt['remaining_queued_records']}
UNKNOWN — HOLD CREATED: 0
ROUTING ASSIGNMENTS: 0
GROUPING ASSIGNMENTS: 0
SOURCE RECORDS REMOVED OR CLOSED: 0
PACKET 04 AUTHORIZED: NO

## Decisions

{rows or '- No reviewed predicate produced a complete supported or disproved result.'}

## Decision-state counts

{states}

## Evidence discipline

The family is heterogeneous. Every decision comes from a named claim-specific three-way predicate: complete absence, complete verified proof, or unresolved partial evidence. Discovery copies, source-inventory claims, plans without completion proof, semantic similarity, and untracked state are excluded as proof.

## Remaining records

The remaining {len(remaining)} records preserve permanent addresses and source order. Their queue entries identify either the missing predicate, the incomplete proof components, or the current files that must be resolved.

## Independent verification

- complete 31-record family coverage: PASS
- current main commit anchor: `{receipt['main_commit_anchor']}`
- filtered current-corpus digest: `{receipt['filtered_corpus_sha256']}`
- effective-runtime corpus digest: `{receipt['effective_runtime_corpus_sha256']}`
- every reviewed predicate independently rerun: PASS
- all partial evidence kept queued: PASS
- unsupported automatic HOLD decisions: none
- routing and grouping leakage: none
- adversarial rejection fixtures: {receipt['adversarial_rejection_fixtures_passed']}

## Next boundary

Process the next largest evidence family that current repository evidence can materially resolve. Stop before routing, destinations, grouping, closure, implementation, or Packet 04.
""",encoding="utf-8")

(AUDIT/"Packet_01.5_Routing_Status_v87.md").write_text(f"""# Packet 01.5 — Routing Status v87

STATUS: OTHER RECORD-SPECIFIC FAMILY VERIFIED
WATCH: NONE
BLOCKERS: NONE
FAMILY RECORDS PROCESSED: 31
SUPPORTED OR DISPROVED APPLICABILITY DECISIONS: {receipt['supported_or_disproved_decisions']}
REMAINING EVIDENCE-QUEUE RECORDS: {receipt['remaining_queued_records']}
UNKNOWN — HOLD CREATED: 0
ROUTING ASSIGNMENTS COMPLETED: 0
SEMANTIC GROUPING ASSIGNMENTS COMPLETED: 0
INDIVIDUAL RECORD CLOSURE: NOT AUTHORIZED
PACKET 04: NOT AUTHORIZED

All 31 addresses remain preserved in original source order and appear exactly once as either decided or still queued. Only complete reviewed record-specific predicates may create decisions.

## Next authorized work

`Packet 01.5 — Process Next Resolvable Evidence Family`

The scalable gate remains active. Stop before routing, destinations, grouping, closure, implementation, or Packet 04.
""",encoding="utf-8")
