# Pass 2 / P2-C Explicit Production-Shaped Proof Run 001

This branch is audit-only and must not be merged.

The user explicitly authorized exactly one isolated activation-and-rollback proof. The proof regenerates the enforcement candidate directly from sealed commit `c618596f2b5c99ca7f355153a5bd31268170df80`, activates it only in a disposable worktree, runs the production-shaped browser chain plus A-002 and A-003 regressions, then restores that worktree byte-for-byte.

Production application, production activation, Current Map changes, production storage changes, and merging are not authorized.
