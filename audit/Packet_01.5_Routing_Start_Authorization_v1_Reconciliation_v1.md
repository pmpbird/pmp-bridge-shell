# Packet 01.5 — Routing-Start Authorization v1 Reconciliation

STATUS: V1 PASS WITHDRAWN — SUPERSEDED BY REQUIRED V2 GATE  
ROUTING PERFORMED: NONE  
APPLICABILITY CLASSIFICATION PERFORMED: NONE  
PACKET 04 AUTHORIZED: NO

## Reason for reconciliation

The v1 gate and its verifier reached a mechanical PASS, but the PASS did not cover every mandatory protection in the authoritative Packet 01.5 work packet and new-chat handoff.

The uncovered requirements are:

1. the fifth applicability state, `UNKNOWN — HOLD`
2. mandatory HOLD behavior instead of guessed assignment
3. explicit routing confidence
4. explicit applicability confidence
5. explicit coexistence of primary and secondary destinations
6. an immutable decision-overlay architecture separate from the source inventory
7. exact permanent-address sequence verification
8. independent recomputation of every envelope hash during the gate proof
9. explicit routing-decision evidence, verifier identity, and reopening conditions
10. adversarial rejection tests for prohibited decisions
11. proof that semantic grouping is reversibly address-based and cannot replace a source envelope
12. inclusion of `envelope_hash` among protected source identities

Because those protections were required before routing could begin, the v1 authorization result is not sufficient authority for routing.

## Preservation decision

The v1 files remain preserved as historical evidence. They are not deleted or rewritten.

The authoritative corrective action is a separate v2 gate and separate v2 independent verification.

Until v2 passes with WATCH: NONE and BLOCKERS: NONE:

- routing start is not authorized
- applicability classification is not authorized
- semantic grouping is not authorized
- Packet 04 is not authorized

## Safe claim

The verified blank 2,750-envelope inventory remains unchanged and no routing or applicability classification was performed by the v1 gate.

END PACKET 01.5 — ROUTING-START AUTHORIZATION v1 RECONCILIATION
