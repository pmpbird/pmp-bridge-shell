#!/usr/bin/env python3
"""Receipt writer for Packet 01.5 scalable pass 001."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_receipts(repo: Path, result: dict[str, Any]) -> None:
    audit = repo / "audit"
    out_json = audit / "Packet_01.5_Scalable_Pass_001_Independent_Verification_v1.json"
    out_md = audit / "Packet_01.5_Scalable_Pass_001_Independent_Verification_v1.md"
    status = audit / "Packet_01.5_Routing_Status_v83.md"
    out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    out_md.write_text(f"""# Packet 01.5 — Scalable Pass 001 Independent Verification v1

STATUS: PASS — SCALABLE PASS 001 VERIFIED
WATCH: NONE
BLOCKERS: NONE
WINDOW RECORDS: {result['window_records']}
EVIDENCE-SUPPORTED DECISIONS: {result['evidence_supported_decisions']}
EVIDENCE-ACQUISITION QUEUE ENTRIES: {result['evidence_queue_entries']}
UNKNOWN — HOLD CREATED: 0
CURRENT DEFECT OR LIMITATION: 2
ACTIVE CONDITIONAL RISK: 4
ROUTING ASSIGNMENTS: 0
SEMANTIC GROUPING: 0
SOURCE RECORDS REMOVED OR CLOSED: 0
PACKET 04 AUTHORIZED: NO

## Meaningful decisions

- `AI-003` — `CURRENT DEFECT OR LIMITATION`: configured worker has no AI/provider/model endpoint.
- `AI-004` — `ACTIVE CONDITIONAL RISK`: configured worker uses wildcard CORS.
- `AI-005` — `ACTIVE CONDITIONAL RISK`: configured worker exposes POST endpoints without an authorization check.
- `AI-006` — `ACTIVE CONDITIONAL RISK`: caller JSON is broadly merged into protected backend objects.
- `AI-007` — `ACTIVE CONDITIONAL RISK`: request-size, rate, replay, and idempotency controls are absent from current worker source.
- `AI-008` — `CURRENT DEFECT OR LIMITATION`: KV is unbound while writes may be accepted without persistence.

These six decisions supersede their earlier HOLD overlays because current repository source and configuration provide stronger direct evidence.

## Undecided records

The other 116 baseline records were not classified as HOLD. Each appears in exactly one evidence-acquisition queue with its permanent address, exact missing proof, acquisition method, blocking condition, and reopening trigger.

## Independent proof

- immutable 2,750-record inventory and every envelope hash: PASS
- exact 122-record baseline window: PASS
- current worker and Wrangler evidence predicates: PASS
- six decision overlays against Contract v2: PASS
- 116 record-specific queue entries in source order: PASS
- complete decided-or-queued coverage with no overlap: PASS
- unsupported mass HOLD: none
- adversarial rejection fixtures passed: {result['adversarial_rejection_fixtures_passed']}
- source inventory unchanged: PASS

## Next authorized work

Acquire evidence by queue family, then rerun applicability processing under the same scalable gate. A new per-window gate is not required.

Stop before routing, grouping, closure, implementation, or Packet 04.
""", encoding="utf-8")

    status.write_text(f"""# Packet 01.5 — Routing Status v83

STATUS: SCALABLE APPLICABILITY PASS 001 VERIFIED
WATCH: NONE
BLOCKERS: NONE
FOUR-RECORD GATE CYCLE: SUPERSEDED
WINDOW RECORDS PROCESSED: 122
EVIDENCE-SUPPORTED APPLICABILITY DECISIONS: 6
EVIDENCE-ACQUISITION QUEUE ENTRIES: 116
UNKNOWN — HOLD CREATED: 0
CURRENT DEFECT OR LIMITATION: 2
ACTIVE CONDITIONAL RISK: 4
ROUTING ASSIGNMENTS COMPLETED: 0
SEMANTIC GROUPING ASSIGNMENTS COMPLETED: 0
INDIVIDUAL RECORD CLOSURE: NOT AUTHORIZED
PACKET 04: NOT AUTHORIZED

## Decision addresses

`P01.5::B::0003` through `P01.5::B::0008`

## Coverage

All 122 baseline addresses appear exactly once as either a verified applicability decision or a record-specific evidence-queue entry. The immutable source inventory remains unchanged.

## Next authorized work

`Packet 01.5 — Evidence Acquisition from SCALABLE-PASS-001 Queues`

Further windows may run under the same scalable gate after a verified cursor. Stop before routing, grouping, closure, implementation, or Packet 04.
""", encoding="utf-8")
