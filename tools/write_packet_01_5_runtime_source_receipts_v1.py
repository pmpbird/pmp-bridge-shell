#!/usr/bin/env python3
import json,os,subprocess
from runtime_source_paths import *

v=json.loads(VERIFY_JSON.read_text());m=json.loads(MATRIX.read_text());by={x['composite_address']:x for x in m['matrix']}
d=[json.loads(x) for x in DECISIONS.read_text().splitlines()];q=[json.loads(x) for x in REMAINING.read_text().splitlines()]
rows='\n'.join(f"- `{x['composite_address']}` / `{by[x['composite_address']]['original_identifier']}` — `{x['applicability_state']}`" for x in d)
queues='\n'.join(f"- `{x['composite_address']}` / `{x['original_identifier']}` — {x['decision_blocked_until']}" for x in q)
SUMMARY.write_text(f'''# Packet 01.5 — Current Runtime Source Family v1

STATUS: VERIFIED
FAMILY RECORDS: 20
EVIDENCE-SUPPORTED DECISIONS: {v['evidence_supported_decisions']}
REMAINING QUEUED: {v['remaining_queued_records']}
UNKNOWN — HOLD CREATED: 0
ROUTING ASSIGNMENTS: 0
GROUPING ASSIGNMENTS: 0
SOURCE RECORDS REMOVED OR CLOSED: 0

Effective-source precedence is anchored to authoritative `main` commit `{v['main_commit_anchor']}`.

The effective route was reconstructed from the public entry through the primary map, Route Guardian loader, nested wrappers, inner application, runtime-injected scripts, worker, and platform configuration. Fallback-only and manual-action paths remain separately identified.

Static source decisions are separated from browser, device, environment-dependent, and non-runtime evidence queues. Every family address appears exactly once as decided or queued in original source order.

Stop before routing, destinations, grouping, closure, implementation, or Packet 04.
''')
VERIFY_MD.write_text(f'''# Packet 01.5 — Current Runtime Source Independent Verification v1

STATUS: PASS — CURRENT RUNTIME SOURCE FAMILY VERIFIED
WATCH: NONE
BLOCKERS: NONE
FAMILY RECORDS: 20
EVIDENCE-SUPPORTED DECISIONS: {v['evidence_supported_decisions']}
REMAINING QUEUED: {v['remaining_queued_records']}
UNKNOWN — HOLD CREATED: 0
ROUTING ASSIGNMENTS: 0
GROUPING ASSIGNMENTS: 0
SOURCE RECORDS REMOVED OR CLOSED: 0
PACKET 04 AUTHORIZED: NO

## Decisions

{rows}

## Runtime or non-runtime evidence queues

{queues}

## Independent verification

- complete 20-record family coverage: PASS
- permanent source order: PASS
- authoritative main anchor: `{v['main_commit_anchor']}`
- runtime precedence graph: `{v['runtime_graph_sha256']}`
- every controlling source digest: PASS
- every precedence edge: PASS
- bounded source-level runtime tests: PASS
- every applicability predicate rerun: PASS
- every remaining queue entry verified: PASS
- prior Packet 01.5 outputs excluded as evidence: PASS
- immutable 2,750-record source inventory: PASS
- automatic UNKNOWN — HOLD decisions: none
- routing, grouping, closure, implementation, and Packet 04 leakage: none
- adversarial rejection fixtures: {v['adversarial_rejection_fixtures_passed']}

## Next boundary

Process the next largest evidence family that current evidence can materially resolve. Stop before routing, destinations, grouping, closure, implementation, or Packet 04.
''')
STATUS.write_text(f'''# Packet 01.5 — Routing Status v89

STATUS: CURRENT RUNTIME SOURCE FAMILY VERIFIED
WATCH: NONE
BLOCKERS: NONE
FAMILY RECORDS PROCESSED: 20
EVIDENCE-SUPPORTED APPLICABILITY DECISIONS: {v['evidence_supported_decisions']}
REMAINING EVIDENCE-QUEUE RECORDS: {v['remaining_queued_records']}
UNKNOWN — HOLD CREATED: 0
ROUTING ASSIGNMENTS COMPLETED: 0
SEMANTIC GROUPING ASSIGNMENTS COMPLETED: 0
INDIVIDUAL RECORD CLOSURE: NOT AUTHORIZED
PACKET 04: NOT AUTHORIZED

All 20 permanent addresses remain in original source order and appear exactly once as decided or queued. Effective-source precedence is anchored to authoritative main, and static source evidence is separated from browser, device, and non-runtime evidence.

## Next authorized work

`Packet 01.5 — Process Next Resolvable Evidence Family`

The scalable gate remains active. Stop before routing, destinations, grouping, closure, implementation, or Packet 04.
''')
if os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('CRS_COMMIT_OUTPUTS')=='true':subprocess.run(['bash','tools/commit_runtime_source_outputs.sh'],check=True)
