# App Orchestrator Pass 2 — P2-B Status

## Current position

- Overall project pass: **Pass 2**
- Phase: **P2-B — exact-source actor authorization gate and adversarial forbidden-action fixtures**
- P2-A: complete and merged
- P2-B: in progress
- Pass 2 complete: no
- Pass 3 started: no

## What P2-B builds

P2-B creates one fail-closed gate with these properties:

1. Every actor must match an exact SHA-256 identity in both the authority policy and the source manifest.
2. Unknown actor paths are denied before an actor token is created.
3. Changed bytes for a known actor are denied before an actor token is created.
4. Protected side-effect APIs require a valid actor token and an explicitly declared capability.
5. Unknown actors and undeclared capabilities are denied before the native side-effect method is called.
6. Actor identity is carried into registered timer, event, Promise, and microtask callbacks.
7. Denials are preserved in an in-memory audit report without writing app storage.

## Exercised protected capabilities

The adversarial fixture covers storage writes/deletes/clear, DOM mutation/deletion, script injection, resource target changes, document.write, navigation, network fetch, IndexedDB open/delete, Cache Storage open/delete, timer scheduling, and event-listener registration.

For each blocked case, the fixture verifies that the exercised side effect did not occur.

## Safety boundary

P2-B certifies the gate engine and fixtures. It does not silently activate the gate across the live app yet. Active-chain integration and the exact production actor policy remain P2-C.

No Current Map destination, storage schema, IndexedDB database, cache, Bank, user content, vault record, visual surface, Pass 3 work, or Crosswalk Router integration belongs in P2-B.

## Stop line

P2-B may be declared complete only after:

- adversarial browser fixtures pass;
- deterministic policy rebuild passes with no diff;
- the new gate and policy are included in the sealed A-003 manifest;
- A-002 and A-003 regressions remain green;
- an independently verified P2-B receipt is merged;
- the full-repository canonical ZIP is updated and reverified.

The next phase after P2-B is **P2-C — active runtime integration and exact active actor policy**.
