# Pass 2 / P2-C Explicit Production-Shaped Proof 001

This branch is audit-only and must close without merge.

The user explicitly authorized an isolated production-shaped activation-and-rollback proof. The proof runner creates a detached Git worktree at commit `c618596f2b5c99ca7f355153a5bd31268170df80`, applies the enforcement candidate only inside that disposable copy, runs the browser proof plus A-002 and A-003, performs inverse rollback, and reruns the regressions on the restored copy.

The branch itself changes no production runtime source, Current Map destination, storage, IndexedDB, cache, Bank, or user content. Production application and merge remain unauthorized.
