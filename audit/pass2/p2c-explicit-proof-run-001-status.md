# Pass 2 / P2-C Explicit Production-Shaped Proof Run 001

This branch is an audit-only proof carrier based exactly on repository commit `c618596f2b5c99ca7f355153a5bd31268170df80`.

The user explicitly authorized one isolated production-shaped activation-and-rollback proof. That authorization does **not** authorize production activation or merge.

The workflow must:

1. verify the sealed proof payload SHA-256;
2. create a detached disposable worktree at the exact source commit;
3. activate the prospective enforcement patch only inside that worktree;
4. run the navigable-origin Chromium proof;
5. run A-003 repository 21/21, A-003 adversarial live 47/47, and A-002 live 41/41;
6. roll the worktree back byte-for-byte even after failure;
7. upload complete evidence;
8. leave production, Current Map, storage, IndexedDB, Cache Storage, Bank, user content, and Pass 3 untouched.

This branch must not be merged.
