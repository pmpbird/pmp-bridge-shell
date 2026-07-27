# App Orchestrator recovery guide

## First response

1. Stop the affected action; do not delete, clean, reset, or migrate data.
2. Record the visible symptom, route, owner, level or record identity, time,
   deployed commit, and relevant diagnostic receipt.
3. Preserve the newest verified checkpoint and current local worktree.
4. Compare GitHub main, the clean mirror, Current Map, A-003 manifest, seal,
   and bootstrap anchor.

## Source recovery

- Recover source from the exact Git commit recorded by the newest canonical
  checkpoint.
- Preserve both `Index.html` and `index.html` as distinct Git objects.
- Never rebuild a release from a case-insensitive Finder copy when exact Git
  object bytes are available.
- Use a new clean worktree for repair; never reset or clean a user-owned dirty
  worktree.

## Data recovery

- Archive and quarantine preserve exact payload bytes and references.
- A partial transactional write must restore the exact backup and leave an
  append-only failure receipt.
- A partial migration must discard staged target records and retain the exact
  source snapshot.
- Never delete the old app or source data before a separately authorized
  production migration has passed acceptance.

## Authority recovery

- Failed or consumed exactly-once authority cannot be retried.
- PR #122 and consumed observation PRs 149, 150, and 152 remain quarantined.
- If a new destructive, production, user-data, credential, privacy, financial,
  or formal-proof action is required, stop at that exact gate and request
  narrowly bound explicit authority.
