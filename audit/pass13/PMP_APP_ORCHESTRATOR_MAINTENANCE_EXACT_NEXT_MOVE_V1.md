# Exact next move

Commit the reviewed ownership-maintenance tree on
`agent/app-orchestrator-owner-conflict-repair-v1`, push it, open the pull
request, run and repair ordinary CI failures, and merge only the exact green
head.

After merge:

1. verify GitHub `main` equals the merge result;
2. synchronize the clean laptop mirror to that exact commit;
3. create new full and compact canonical checkpoints without overwriting any
   earlier package;
4. verify ZIP CRC, entry manifest, payload hashes, embedded commit identity,
   size, and SHA-256 sidecars.

Do not run a formal proof, activate production behavior, migrate or change
persisted user data, delete prior packages, or infer a Pass 14.
