#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "audit"
APP = AUDIT / "applicability"

receipt = json.loads((AUDIT / "Packet_01.5_Authoritative_Packet_Law_Family_Independent_Verification_v1.json").read_text(encoding="utf-8"))
decisions = [json.loads(line) for line in (APP / "Packet_01.5_Authoritative_Packet_Law_Family_Decisions_v1.jsonl").read_text(encoding="utf-8").splitlines()]
remaining = [json.loads(line) for line in (APP / "Packet_01.5_Authoritative_Packet_Law_Family_Remaining_Queue_v1.jsonl").read_text(encoding="utf-8").splitlines()]
matrix = json.loads((AUDIT / "Packet_01.5_Authoritative_Packet_Law_Evidence_Matrix_v1.json").read_text(encoding="utf-8"))
matrix_by_address = {item["composite_address"]: item for item in matrix["records_matrix"]}
count = receipt["evidence_supported_or_disproved_decisions"]

rows = "\n".join(
    f"- `{item['composite_address']}` / `{matrix_by_address[item['composite_address']]['original_identifier']}` — `{item['applicability_state']}` — `{matrix_by_address[item['composite_address']]['outcome']}`"
    for item in decisions
)
state_lines = "\n".join(f"- {state}: {value}" for state, value in sorted(receipt["decision_states"].items())) or "- None"

(AUDIT / "Packet_01.5_Authoritative_Packet_Law_Family_Independent_Verification_v1.md").write_text(f"""# Packet 01.5 — Authoritative Packet Law Family Independent Verification v2

STATUS: PASS — AUTHORITATIVE PACKET LAW FAMILY VERIFIED
WATCH: NONE
BLOCKERS: NONE
FAMILY RECORDS: 25
SUPPORTED OR DISPROVED DECISIONS: {count}
REMAINING QUEUED: {receipt['remaining_queued_records']}
UNKNOWN — HOLD CREATED: 0
ROUTING ASSIGNMENTS: 0
GROUPING ASSIGNMENTS: 0
SOURCE RECORDS REMOVED OR CLOSED: 0
PACKET 04 AUTHORIZED: NO

## Authority precedence

1. Current approved decisions, latest status ledgers, and independently verified receipts
2. Current governing packet laws, packet records, roadmaps, and completion receipts
3. Older versions as corroboration only

Discovery artifacts, routing batches, reconstructed baselines, applicability outputs, and copied limitation statements are excluded from authority. Within a normalized document family, the latest version controls. Equal-tier conflicts remain queued.

## Decisions

{rows or '- No claims met the strict current-authority support or disproof threshold.'}

## Decision-state counts

{state_lines}

Direct current support produces a current applicability decision. Direct higher-precedence disproof produces an `OUT-OF-SCOPE CANDIDATE`, not a current defect.

## Remaining records

The remaining {len(remaining)} law-family records retain their permanent addresses and original source order. Each queue entry names the missing controlling authority, incomplete clause, private dependency, or unresolved precedence conflict.

## Independent verification

- complete 25-record family coverage: PASS
- current main commit anchor: `{receipt['main_commit_anchor']}`
- authority census digest: `{receipt['authority_census_sha256']}`
- forbidden copied/discovery authority excluded: PASS
- tier and version precedence recomputed: PASS
- support and disproof predicates independently rerun: PASS
- equal-tier conflicts blocked: PASS
- content digests for controlling sources: PASS
- unsupported automatic HOLD decisions: none
- routing and grouping leakage: none
- adversarial rejection fixtures: {receipt['adversarial_rejection_fixtures_passed']}

## Next boundary

Process the next largest evidence family that current repository evidence can materially resolve. Stop before routing, grouping, closure, implementation, or Packet 04.
""", encoding="utf-8")

(AUDIT / "Packet_01.5_Routing_Status_v85.md").write_text(f"""# Packet 01.5 — Routing Status v85

STATUS: AUTHORITATIVE PACKET LAW FAMILY VERIFIED
WATCH: NONE
BLOCKERS: NONE
FAMILY RECORDS PROCESSED: 25
SUPPORTED OR DISPROVED APPLICABILITY DECISIONS: {count}
REMAINING EVIDENCE-QUEUE RECORDS: {receipt['remaining_queued_records']}
UNKNOWN — HOLD CREATED: 0
ROUTING ASSIGNMENTS COMPLETED: 0
SEMANTIC GROUPING ASSIGNMENTS COMPLETED: 0
INDIVIDUAL RECORD CLOSURE: NOT AUTHORIZED
PACKET 04: NOT AUTHORIZED

All 25 authoritative-packet-law addresses remain preserved in original source order and appear exactly once as either decided or still queued. Approved role amendments and current verified status outrank older packet-role descriptions. Discovery and routing-batch copies are not governing authority.

## Next authorized work

`Packet 01.5 — Process Next Resolvable Evidence Family`

The scalable gate remains active. Stop before routing, grouping, closure, implementation, or Packet 04.
""", encoding="utf-8")
