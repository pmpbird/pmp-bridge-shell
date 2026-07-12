# App Orchestrator Pass 2 — P2-B Hardening V2

## Current position

- Overall project pass: **Pass 2**
- Existing P2-B V1: merged and certified at its exercised 34-check scope
- Current move: **P2-B hardening V2**
- Active-chain integration: not started
- Pass 2 complete: no
- Pass 3 started: no

## Why hardening is required

The merged P2-B V1 gate correctly blocked unknown actors and unauthorized capabilities in its original fixtures. A later proof review found two weaknesses in the certification design:

1. The fixture manifest was reconstructed directly from the policy instead of being generated as an independent exact-source record.
2. The matrix did not separately prove unknown-source non-execution or no-effect outcomes for storage deletion, DOM deletion, and resource-target mutation.

These are proof gaps, not evidence that the gate engine failed.

## Hardening work

P2-B hardening V2 adds:

- `pmp-actor-source-manifest-v1.json`, generated directly from the exact fixture bytes;
- deterministic policy and manifest generation from the same bounded source set, with independent output comparison;
- policy-to-manifest path and SHA-256 agreement checks;
- a **42-check** adversarial browser matrix;
- separate denial and no-effect checks across all sixteen protected capability families;
- deterministic A-003 resealing for the new protected actor-source manifest;
- complete A-002 and A-003 regressions.

The first hardening browser execution passed all **42/42** checks. The initial workflow failure was only a stale expected total of 41; no gate failure occurred.

The gate engine is not changed unless the new matrix finds a real enforcement defect.

## Stop line

Hardening is complete only after:

- 42/42 adversarial checks pass;
- exact policy/source-manifest regeneration has no diff;
- A-003 is resealed and passes 21/21 plus 47/47;
- A-002 remains 41/41;
- a supplemental hardening receipt is independently verified and merged;
- the full-repository canonical ZIP is updated and reverified.

The next phase remains **P2-C — active runtime integration and complete production actor policy**.
