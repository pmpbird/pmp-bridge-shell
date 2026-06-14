# Packet 01.5 — Applicability Evidence Catalog v1

STATUS: DEFINED — PENDING INDEPENDENT VERIFICATION  
WATCH: NONE KNOWN  
BLOCKERS: NONE KNOWN  
APPLICABILITY CLASSIFICATIONS COMPLETED: 0  
ROUTING ASSIGNMENTS COMPLETED: 0  
SEMANTIC GROUPING ASSIGNMENTS COMPLETED: 0  
PACKET 04 AUTHORIZED: NO

## Purpose

This catalog establishes the canonical evidence boundary for Packet 01.5 Phase E applicability decisions.

It does **not** classify any of the 2,750 source envelopes. It does not assign an owner, destination, secondary destination, cross-cutting law, semantic cluster, closure state, or Packet 04 authority.

The machine-readable catalog is:

`audit/applicability/Packet_01.5_Applicability_Evidence_Catalog_v1.json`

## Governing rules

Every later record decision must remain record-specific and evidence-bound.

The only permitted applicability states remain:

1. `CURRENT DEFECT OR LIMITATION`
2. `ACTIVE CONDITIONAL RISK`
3. `DORMANT FUTURE RISK`
4. `OUT-OF-SCOPE CANDIDATE`
5. `UNKNOWN — HOLD`

The following always produce `UNKNOWN — HOLD` until resolved:

- missing evidence
- conflicting evidence
- stale evidence without current confirmation
- unavailable private evidence
- uncaptured external or live state

A heading, severity word, discovery domain, or provisional owner suggestion is not applicability evidence.

## Authority tiers

### T1 — Governing

Packet law, the corrected v2 routing-start gate, its independent verification receipt, the decision-overlay contract, and the verified routing status.

### T2 — Effective runtime control

The stable door, its actual map precedence, the effective map, the loader selected by that map, and the current-app wrapper selected by that map.

### T3 — Public-safe inventory

The Inventory Eyes manifest, normalized vault snapshot, and updater status. These are supporting sources and require freshness review before they can support a current-behavior claim.

### T4 — Record-specific inspection

Direct source, runtime, test, or proof evidence captured for the individual envelope being classified.

### T5 — Uncaptured or private

Unavailable, private, external, or live evidence. This tier cannot support a non-HOLD decision until the evidence is safely captured.

## Effective runtime resolution

The stable Home Screen door is `pmp-app-current.html`.

Its map order is authoritative for resolution:

1. `pmp-current-map-v9.json`
2. `pmp-current-map.json`

Therefore, while the first map loads successfully:

- effective loader: `pmp-route-guardian-current-loader-v14.html`
- effective current app: `pmp-current-inner-cleanbug-rgcontrols-v4.html`
- v4 wrapper target: `pmp-current-inner-cleanbug-rgcontrols-v3.html`

`pmp-current-map.json` remains fallback evidence only. It must not override the higher-precedence map merely because its filename is unversioned.

The loader requires a manual **Open Latest App** action. Its own source limits its safe claim: opening and support injection do not prove source acceptance, hook validation, complete app proof, full transfer, current-clean, frozen, or best-in-world status.

## Public-safe inventory boundary

The public-safe inventory may identify:

- public repository paths
- active/support/archive/future labels
- source structure
- localStorage key names
- public-safe runtime controls

It may not contain or infer from:

- private Bug Memory contents
- Apple Notes contents
- tokens
- passwords
- secrets
- private localStorage values
- other private values

The manifest and vault snapshot are supporting evidence. Their labels do not override newer effective-map or direct-source evidence.

## Record-decision use

A later applicability decision may cite catalog evidence entries, but must also supply:

1. evidence tied to the individual permanent address
2. a reasoning summary
3. applicability confidence from 0 through 100
4. reopening conditions
5. a decision author
6. a distinct decision verifier

During `APPLICABILITY_ONLY`, every destination and routing-proof field remains blank.

## Independent verification requirement

The independent verifier must prove:

1. all catalog source paths exist
2. every required marker and JSON value matches repository truth
3. source inventory hash and address-sequence hash remain unchanged
4. all 2,750 source records remain blank for applicability and routing
5. actual stable-door map precedence is preserved
6. effective and fallback maps remain distinct
7. v14 and v4 source relationships match the catalog
8. public-safe privacy exclusions remain mandatory
9. older inventory cannot override newer runtime-control evidence
10. the catalog contains no record classifications or destinations
11. positive policy fixtures pass
12. adversarial catalog mutations are rejected
13. no classification, routing, grouping, deletion, or closure occurs

## Pass boundary

Only an independent PASS with:

- WATCH: NONE
- BLOCKERS: NONE

may authorize the next work:

`Packet 01.5 Phase E — First Controlled Applicability-Only Batch`

Stop after verification. Do not make the first record decision as part of this catalog task.

END PACKET 01.5 — APPLICABILITY EVIDENCE CATALOG v1
