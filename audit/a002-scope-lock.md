# A-002 and A-003 Final Scope Lock

A-002 P0 through P7 and A-003 P0 through P6 are complete and passed at their full exercised scopes.

Final receipts:

- `audit/a002-final-receipt.json`
- `audit/a003-final-receipt.json`

Locked facts:

- sole route destination truth: `pmp-current-map-v12.json`
- A-002 authority census: 65 objects, 0 independent authorities, 0 unresolved
- A-002 live runtime: 37 passed, 0 failed
- A-003 deterministic runtime source-set SHA-256: `2efc5aa5f3ece5b1da94e162baf7f981a636ef5f23d9c6b3f2d8a348688172e2`
- A-003 sealed manifest SHA-256: `570c6db93da497758c6b18f53fa1e3c2b08cb1fdff761c9e54d97b87914e54d0`
- A-003 repository gate: 21 passed, 0 failed
- A-003 adversarial Chromium gate: 47 passed, 0 failed
- rollback required: no
- merge authorized: no

Forbidden without a separate explicit instruction:

- merge PR #38 into main;
- enable auto-merge;
- mark the PR ready for review if that is meant to authorize merge;
- claim the overall project’s Pass 1 is complete;
- clear storage, caches, IndexedDB, Bank data, or user content;
- claim that the bootstrap root self-verifies;
- claim complete protection against a compromised origin or the Service Worker registration TOCTOU interval.

Current boundary: `STOP_BEFORE_MERGE`.
