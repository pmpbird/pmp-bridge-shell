# Packet 01.5 — Routing-Start Authorization Gate v2

STATUS: DEFINED — PENDING INDEPENDENT VERIFICATION  
WATCH: NONE KNOWN  
BLOCKERS: NONE KNOWN  
ROUTING ASSIGNMENTS COMPLETED: 0  
APPLICABILITY CLASSIFICATIONS COMPLETED: 0  
PACKET 04 AUTHORIZED: NO

## Authority and supersession

This v2 gate is the corrective authority required by:

- `audit/Packet_01.5_Problems_Limitations_and_Routing_Register_v1.md`
- `audit/Packet_01.5_New_Chat_Handoff_v1.md`
- `audit/Packet_01.5_Routing_Start_Authorization_v1_Reconciliation_v1.md`

The v1 gate and v1 PASS remain preserved as history but are not sufficient authority for routing.

This v2 gate becomes effective only if:

`audit/Packet_01.5_Routing_Start_Authorization_Independent_Verification_v2.md`

reports all three:

- STATUS: PASS — ROUTING START AUTHORIZED
- WATCH: NONE
- BLOCKERS: NONE

## Protected source anchor

The source inventory is immutable:

- path: `audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl`
- envelopes: 2,750
- baseline: 122
- provisional: 2,628
- bytes: 3,898,954
- SHA-256: `76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477`
- address-sequence SHA-256: `3d808e1ec3f163e4cb2ab7a15767563fe7c43b9920bcecde9abe711226220916`
- first address: `P01.5::B::0001`
- last address: `P01.5::P069::XRES-003`

All 2,750 source envelopes must remain present exactly once. Their permanent addresses, source wording, source hashes, and envelope hashes must remain unchanged.

## Separate decision-overlay law

Classification, routing, cross-cutting assignment, and semantic grouping must be written only to a separate decision overlay keyed by:

1. permanent address
2. source inventory hash
3. source envelope hash
4. source block hash

The blank source inventory must not be rewritten into a routed copy and must remain the rollback and reconstruction source.

The machine contract is:

`audit/routing-inventory/Packet_01.5_Routing_Decision_Contract_v2.json`

## Required applicability states

Every later applicability decision must use exactly one:

1. `CURRENT DEFECT OR LIMITATION`
2. `ACTIVE CONDITIONAL RISK`
3. `DORMANT FUTURE RISK`
4. `OUT-OF-SCOPE CANDIDATE`
5. `UNKNOWN — HOLD`

No state is inferred from a discovery domain, heading, severity word, or prior provisional owner suggestion.

A conditional or dormant risk may become a current defect only through explicit evidence, reasoning, confidence, and an independently verifiable decision record.

## Separation of applicability and destination

The permitted decision stages are:

- `APPLICABILITY_ONLY`
- `ROUTED`
- `HOLD`

At `APPLICABILITY_ONLY`, all destination and routing-proof fields remain blank.

At `ROUTED`, one primary destination is required. Secondary destinations and cross-cutting laws may coexist without copying, deleting, replacing, or closing the source envelope.

At `HOLD`, all destination fields remain blank, a HOLD reason is required, and at least one unresolved dependency or uncertainty is required.

`UNKNOWN — HOLD` must always use stage `HOLD`.

## Evidence and confidence law

Every applicability decision requires:

1. record-specific evidence
2. reasoning summary
3. applicability confidence from 0 through 100
4. reopening conditions
5. decision author
6. a distinct decision verifier

Every routed decision additionally requires:

1. routing evidence
2. routing rationale
3. routing confidence from 0 through 100
4. expected receiving work
5. expected completion evidence
6. explicit unresolved-dependency list
7. one primary destination
8. zero or more distinct secondary destinations
9. zero or more cross-cutting laws

Blank evidence, guessed destinations, duplicated destinations, or the same author and verifier must fail.

## Semantic-grouping law

Semantic grouping is reference-only and reversible by permanent address.

A cluster may never:

1. replace a source envelope
2. reduce the source-envelope count
3. erase record-level applicability or routing
4. change source wording or hashes
5. become the only surviving record
6. become a routing destination by itself
7. close a record because it appears duplicative

## Closure and authority law

Every routing-stage decision must retain closure state `OPEN`.

Routing:

- does not prove resolution
- does not prove implementation
- does not authorize promotion
- does not authorize record closure
- does not authorize Packet 04
- does not expand Resident authority

## Independent verification requirements

The verifier must:

1. rerun the existing source-to-envelope independent verifier
2. recompute the exact inventory byte hash
3. recompute the exact permanent-address sequence hash
4. parse all 2,750 envelopes
5. prove all permanent addresses are unique and within the verified sequence
6. recompute every envelope hash
7. confirm all inventory applicability and routing fields remain blank
8. verify the complete v2 decision contract
9. pass positive fixtures for all five applicability states
10. pass a routed fixture carrying primary, secondary, and cross-cutting assignments together
11. pass a HOLD fixture
12. reject adversarial fixtures for guessed HOLD, missing confidence, destination-before-applicability, source-hash mismatch, duplicate destinations, source closure, and author/verifier identity conflict
13. prove the inventory bytes are unchanged after all tests
14. confirm routing and classification counts remain zero
15. confirm Packet 04 remains unauthorized

## Pass decision

Only a complete independent PASS with no watch and no blocker authorizes the next work:

`Packet 01.5 Phase E — Applicability Classification`

The gate does not perform that work.

Stop after verification. Do not classify or route any source envelope as part of this gate.

END PACKET 01.5 — ROUTING-START AUTHORIZATION GATE v2
