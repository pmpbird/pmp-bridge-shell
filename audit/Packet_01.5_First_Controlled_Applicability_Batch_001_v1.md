# Packet 01.5 — First Controlled Applicability Batch 001 v1

STATUS: BUILT — PENDING INDEPENDENT VERIFICATION
BATCH: `PACKET-01.5-APPLICABILITY-BATCH-001`
SOURCE ADDRESSES: `P01.5::B::0001` through `P01.5::B::0004`
APPLICABILITY DECISIONS BUILT: 4
CURRENT DEFECT OR LIMITATION: 0
ACTIVE CONDITIONAL RISK: 0
DORMANT FUTURE RISK: 0
OUT-OF-SCOPE CANDIDATE: 0
UNKNOWN — HOLD: 4
ROUTING ASSIGNMENTS: 0
SEMANTIC GROUPING ASSIGNMENTS: 0
SOURCE RECORDS REMOVED OR CLOSED: 0
PACKET 04 AUTHORIZED: NO

## Why all four records are HOLD

The four permanent records preserve historical claims and labels. The verified evidence catalog does not yet contain the current T4 source, packet-law, deployed-worker, endpoint, CORS, or runtime receipts required to affirm those claims today. Packet 01.5 law requires uncertainty to become `UNKNOWN — HOLD`, not a guessed current defect.

## Decisions

| Permanent address | Original ID | Applicability | Confidence | HOLD reason |
|---|---|---|---:|---|
| `P01.5::B::0001` | `AI-001` | `UNKNOWN — HOLD` | 98 | Current T4 source and runtime evidence is insufficient to establish whether the provider adapter, model call, and response parser are absent or present across the effective v4/v3 app chain and injected support scripts. |
| `P01.5::B::0002` | `AI-002` | `UNKNOWN — HOLD` | 97 | The current authoritative packet-scope evidence needed to prove the exact implementation boundary is not yet captured inside the independently verifiable repository evidence layer. |
| `P01.5::B::0003` | `AI-003` | `UNKNOWN — HOLD` | 98 | The current serving worker artifact and a current endpoint-enumeration proof are not captured in the verified evidence catalog. |
| `P01.5::B::0004` | `AI-004` | `UNKNOWN — HOLD` | 98 | The current serving worker identity and its effective CORS behavior are not independently captured or proven. |

## Preserved boundary

- The immutable 2,750-record source inventory was not changed.
- All destinations and routing-proof fields remain blank.
- No secondary destination, cross-cutting law, or semantic cluster was assigned.
- All four records remain `OPEN` and carry explicit dependencies and reopening conditions.
- This batch does not authorize implementation, routing, closure, Packet 04, or Batch 002.

## Required independent proof

The verifier must independently rerun the routing-start and evidence-catalog proofs, recompute inventory and decision hashes, validate the exact four-address selection, enforce the full decision contract, reject adversarial mutations, and prove the source inventory remains unchanged.

Stop after Batch 001 verification.

END PACKET 01.5 — FIRST CONTROLLED APPLICABILITY BATCH 001 v1
