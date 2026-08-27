# Pass 2 / P2-C Isolated Proof Rerun 002 — Closed Fail-Closed

This branch is audit-only, its pull request is closed without merge, and it must not be reopened or executed without a new explicit one-run isolated-proof authorization.

The user authorized exactly one isolated production-shaped proof rerun. That authorization was consumed by workflow run `29213836737`.

## Rerun 002 result

**FAIL CLOSED.** Production was never activated or changed.

Passed boundaries and lanes:

- authorization and audit-only scope verification;
- checksum-bound runner reconstruction;
- isolated Chromium installation;
- exact detached baseline and active worktrees;
- disposable active-copy preparation;
- active A-003 repository regression 21/21;
- byte-for-byte rollback at 1,481/1,481 files;
- restored A-003 repository regression 21/21;
- restored A-003 live adversarial regression 47/47;
- complete evidence upload.

Failed proof-harness lanes:

- production-shaped active browser: 13/34 because child-realm managed-script scanning ran before document parsing completed;
- active A-002 and active A-003 live diagnostics: external page-owned timers were correctly rejected by the active actor gate as `UNKNOWN_ACTOR`;
- restored A-002: the active chain reached v30, v23, v4, and v3 but exceeded the external 30-second Home observation window.

## Repair 006

Repair 006 is fully wired and **READY — NOT EXECUTED**. It:

- waits for `DOMContentLoaded` before child-realm managed-script scanning;
- removes only the unowned timers from external proof diagnostics;
- extends only the external A-002 Home observation window from 30 to 60 seconds;
- reapplies diagnostic-harness normalization after rollback before restored-copy regressions.

Repair 006 changes no production runtime source, Current Map destination, storage, IndexedDB, Cache Storage, Bank, user content, or Crosswalk Router content.

## Authorization and pass state

- another isolated proof rerun authorized: **no**;
- production activation authorized: **no**;
- production application authorized: **no**;
- merge authorized: **no**;
- Pass 2 complete: **no**;
- Pass 3 started: **no**;
- major moves remaining inside Pass 2: **1**;
- full passes remaining after Pass 2: **6**;
- unfinished passes including current Pass 2: **7**.

The exact next authorization, when intentionally granted, is one new isolated proof rerun using Repair 006. Production activation will still require a separate explicit authorization after a complete successful proof.
