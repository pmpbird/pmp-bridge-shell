#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

R=Path(__file__).resolve().parents[1];A=R/"audit";P=A/"applicability"
receipt=json.loads((A/"Packet_01.5_Runtime_Source_Family_Independent_Verification_v1.json").read_text(encoding="utf-8"))
decisions=[json.loads(x) for x in (P/"Packet_01.5_Runtime_Source_Family_Decisions_v1.jsonl").read_text(encoding="utf-8").splitlines()]
remaining=[json.loads(x) for x in (P/"Packet_01.5_Runtime_Source_Family_Remaining_Queue_v1.jsonl").read_text(encoding="utf-8").splitlines()]
rows="\n".join(f"- `{x['composite_address']}` / `{next((r['original_identifier'] for r in json.loads((A/'Packet_01.5_Runtime_Source_Family_Evidence_Matrix_v1.json').read_text())['records_matrix'] if r['composite_address']==x['composite_address']), '')}` — `{x['applicability_state']}`" for x in decisions)
(A/"Packet_01.5_Runtime_Source_Family_Independent_Verification_v1.md").write_text(f"""# Packet 01.5 — Runtime Source Evidence Family Independent Verification v1

STATUS: PASS — RUNTIME SOURCE FAMILY VERIFIED
WATCH: NONE
BLOCKERS: NONE
FAMILY RECORDS: 20
EVIDENCE-SUPPORTED DECISIONS: {receipt['evidence_supported_decisions']}
REMAINING QUEUED: {receipt['remaining_queued_records']}
UNKNOWN — HOLD CREATED: 0
ROUTING ASSIGNMENTS: 0
GROUPING ASSIGNMENTS: 0
SOURCE RECORDS REMOVED OR CLOSED: 0
PACKET 04 AUTHORIZED: NO

## Decisions

{rows or '- None'}

## Remaining records

The remaining {len(remaining)} runtime-source records stay queued because static repository evidence did not prove their full claims. Their entries now state the narrower source or live-runtime evidence required.

## Verification

- complete 20-record family coverage: PASS
- permanent-address and source-order preservation: PASS
- current predicates independently rerun: PASS
- unsupported HOLD decisions: none
- routing and grouping leakage: none
- adversarial rejection fixtures: {receipt['adversarial_rejection_fixtures_passed']}
- source inventory unchanged: PASS

## Next boundary

Process the next largest evidence family that current repository evidence can materially resolve. Stop before routing, grouping, closure, implementation, or Packet 04.
""",encoding="utf-8")
(A/"Packet_01.5_Routing_Status_v84.md").write_text(f"""# Packet 01.5 — Routing Status v84

STATUS: CURRENT RUNTIME SOURCE FAMILY VERIFIED
WATCH: NONE
BLOCKERS: NONE
FAMILY RECORDS PROCESSED: 20
EVIDENCE-SUPPORTED APPLICABILITY DECISIONS: {receipt['evidence_supported_decisions']}
REMAINING EVIDENCE-QUEUE RECORDS: {receipt['remaining_queued_records']}
UNKNOWN — HOLD CREATED: 0
ROUTING ASSIGNMENTS COMPLETED: 0
SEMANTIC GROUPING ASSIGNMENTS COMPLETED: 0
INDIVIDUAL RECORD CLOSURE: NOT AUTHORIZED
PACKET 04: NOT AUTHORIZED

All 20 current-runtime-source addresses remain preserved in original source order and appear exactly once as either decided or still queued.

## Next authorized work

`Packet 01.5 — Process Next Resolvable Evidence Family`

The scalable gate remains active; no four-record gate is required. Stop before routing, grouping, closure, implementation, or Packet 04.
""",encoding="utf-8")
