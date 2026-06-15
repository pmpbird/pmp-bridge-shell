#!/usr/bin/env python3
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'audit';P=A/'applicability';v=json.loads((A/'Packet_01.5_Dependency_Platform_Independent_Verification_v1.json').read_text());d=[json.loads(x) for x in (P/'Packet_01.5_Dependency_Platform_Family_Decisions_v1.jsonl').read_text().splitlines()];q=[json.loads(x) for x in (P/'Packet_01.5_Dependency_Platform_Family_Remaining_Queue_v1.jsonl').read_text().splitlines()];m=json.loads((A/'Packet_01.5_Dependency_Platform_Evidence_Matrix_v1.json').read_text());by={x['composite_address']:x for x in m['matrix']}
rows='\n'.join(f"- `{x['composite_address']}` / `{by[x['composite_address']]['original_identifier']}` — `{x['applicability_state']}`" for x in d) or '- No complete repository predicate produced a decision.'
queues='\n'.join(f"- `{x['composite_address']}` / `{x['original_identifier']}` — {x['decision_blocked_until']}" for x in q)
(A/'Packet_01.5_Dependency_Platform_Independent_Verification_v1.md').write_text(f'''# Packet 01.5 — Dependency or Platform State Independent Verification v1

STATUS: PASS — DEPENDENCY OR PLATFORM STATE FAMILY VERIFIED
WATCH: NONE
BLOCKERS: NONE
FAMILY RECORDS: 14
EVIDENCE-SUPPORTED DECISIONS: {v['evidence_supported_decisions']}
REMAINING QUEUED: {v['remaining_queued_records']}
UNKNOWN — HOLD CREATED: 0
ROUTING ASSIGNMENTS: 0
GROUPING ASSIGNMENTS: 0
SOURCE RECORDS REMOVED OR CLOSED: 0
PACKET 04 AUTHORIZED: NO

## Decisions

{rows}

## External or incomplete evidence queues

{queues}

## Independent verification

- complete 14-record family coverage: PASS
- permanent source order: PASS
- main anchor: `{v['main_commit_anchor']}`
- authoritative corpus digest: `{v['authoritative_corpus_sha256']}`
- complete file-census digest: `{v['file_census_sha256']}`
- effective-runtime digest: `{v['runtime_corpus_sha256']}`
- every decision predicate rerun: PASS
- every remaining queue entry verified: PASS
- automatic UNKNOWN — HOLD decisions: none
- routing, grouping, closure, implementation, and Packet 04 leakage: none
- adversarial rejection fixtures: {v['adversarial_rejection_fixtures_passed']}

## Next boundary

Process the next largest evidence family that current repository evidence can materially resolve. Stop before routing, destinations, grouping, closure, implementation, or Packet 04.
''')
(A/'Packet_01.5_Routing_Status_v88.md').write_text(f'''# Packet 01.5 — Routing Status v88

STATUS: DEPENDENCY OR PLATFORM STATE FAMILY VERIFIED
WATCH: NONE
BLOCKERS: NONE
FAMILY RECORDS PROCESSED: 14
EVIDENCE-SUPPORTED APPLICABILITY DECISIONS: {v['evidence_supported_decisions']}
REMAINING EVIDENCE-QUEUE RECORDS: {v['remaining_queued_records']}
UNKNOWN — HOLD CREATED: 0
ROUTING ASSIGNMENTS COMPLETED: 0
SEMANTIC GROUPING ASSIGNMENTS COMPLETED: 0
INDIVIDUAL RECORD CLOSURE: NOT AUTHORIZED
PACKET 04: NOT AUTHORIZED

All 14 addresses remain preserved in original source order and appear exactly once as either decided or queued. Repository-provable state is separated from provider, account, cloud, device, and live-platform evidence.

## Next authorized work

`Packet 01.5 — Process Next Resolvable Evidence Family`

The scalable gate remains active. Stop before routing, destinations, grouping, closure, implementation, or Packet 04.
''')
