# Pass 2 / P2-C Explicit Production-Shaped Proof Run 001

This branch is an audit-only, unmergeable proof carrier rooted at exact commit `c618596f2b5c99ca7f355153a5bd31268170df80`.

The user explicitly authorized an isolated disposable-copy activation-and-rollback proof. That authorization does not authorize production activation or merge.

The workflow must:

1. reconstruct the exact proof payload;
2. create a detached disposable worktree at the source commit;
3. activate the enforcement candidate only inside that worktree;
4. run the production-shaped browser proof;
5. run A-003 repository 21/21, A-003 adversarial live 47/47, and A-002 live 41/41;
6. roll the disposable worktree back to the original 1,481 files byte-for-byte;
7. upload evidence and close without merge.

Production runtime files, Current Map, storage, IndexedDB, Cache Storage, Bank data, user content, Pass 3 state, and Crosswalk Router remain untouched.
