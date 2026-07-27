# Maintenance and exact future-change rules

## Mandatory change sequence

1. Read the final pointer, locked packet, authority matrix, affected pass
   closure, and newest checkpoint.
2. Inspect GitHub main and the clean mirror. Preserve all unrelated changes.
3. State the smallest owner-scoped change and its claim ceiling.
4. Create a clean branch from verified main.
5. Add deterministic tests and fault cases before or with implementation.
6. Update the diagnostic matrix, evidence report, immutable receipt, and
   exact-next-move state.
7. Run the permanent no-blind-flying gate.
8. Push, open or update the PR, preserve complete CI artifacts, and repair
   ordinary failures without broadening scope.
9. Merge only the exact green head.
10. Verify final GitHub main, synchronize the clean laptop mirror, and build
    independently verified full and compact checkpoints.

## Forbidden shortcuts

- No silent authority gain.
- No direct edit on main.
- No destructive clean or reset of user work.
- No deletion disguised as cleanup or migration.
- No production or persisted-user-data mutation without exact authority.
- No retry of consumed observations or exactly-once formal proof.
- No completion claim based only on local tests.
- No package accepted without CRC, entry manifest, payload hashes, commit
  identity, size, and SHA-256 sidecar.
- No overwrite or deletion of an earlier checkpoint.

## Maintenance state after Pass 13

Pass 13 ends feature-roadmap execution. The next safe move is maintenance only:
observe a specific symptom or receive an explicit change request, bind it to
the relevant owner and authority, and follow the mandatory sequence above.
Do not infer a Pass 14.
