# A-002 Pre-Execution Control Sheet

Status: **plan and rollback ledger prepared; no route patch executed**

Baseline: `main` commit `5dd049de1500ea427fa2cf395687239a19706115`

## Why execution cannot start immediately

The A-002 authority inventory found 13 route-capable files that were not represented in the accepted A-001 identity shards. The original A-001 branch remains immutable.

Before any route behavior changes, A-002 must create and pass an additive source-identity supplement linked to A-001 receipt `PMP-A001-5dd049de-PASS-003`.

The supplement must contain these 13 exact baseline identities:

1. `pmp-reload-current-live-update-marker-v1.json`
2. `pmp-current-reload-owner-v29-cachelift-20260706b.html`
3. `pmp-current-inner-cleanbug-rgcontrols-v16.html`
4. `pmp-route-guardian-recovery-tools-v8.html`
5. `pmp-safe-writer-canonical-route-v1.js`
6. `safe-writer-v14.html`
7. `pmp-route-guardian-last-good-v18.html`
8. `pmp-move-ledger-candidate-follow-v1.html`
9. `pmp-route-guardian-current-loader-v14.html`
10. `pmp-current-inner-cleanbug-rgcontrols-v9.html`
11. `pmp-current-inner-cleanbug-rgcontrols-v13.html`
12. `pmp-route-guardian-last-good-v3-button-v1.js`
13. `pmp-route-guardian-last-good-v1.html`

If even one identity fails, A-002 stops before implementation.

## Planned routing architecture

Only `pmp-current-map-v12.json` may name application destinations.

Two fixed mechanism paths are permitted:

- `pmp-current-map-v12.json`
- `pmp-current-route-resolver-v1.js`

The resolver is not allowed to contain fallback destinations. Its job is only to read and validate Current Map, issue a route handoff, and fail closed when the map is unavailable or invalid.

The map will name:

- the stable entry and Route Guardian;
- the current Reload Owner;
- the full ordered runtime-wrapper chain;
- Home and tool routes;
- Last Good and recovery routes;
- the allowed screen hashes;
- the policy for historic files.

## Planned execution order

### P0 — Reconcile A-001 identities

Audit files only. Create the 13-entry supplement and linked receipt. No route code changes.

### P1 — Create the canonical contract

Add the strict resolver, expand Current Map v12, and make the stable entry and Route Guardian consume Current Map only.

Route Guardian v22 will no longer try v11, v10, or the hard-coded v29 fallback. Invalid Current Map means fail closed.

### P2 — Convert the current boot chain

Reload Owner v30, inner v30, v23, v4, v3, Home v6, and the live-update marker will consume map-issued roles instead of hard-coded next files.

The marker becomes revision-only. Runtime byte-hash enforcement remains A-003.

### P3 — Converge Reload Current

Current Screen Pointer, Reload World, Launcher Reload Bridge, and the v2 guard will all call one map-backed reload path while preserving the current screen.

Old v9, v27, Route Guardian v20, and Route Guardian v21 reload paths will be removed.

### P4 — Convert tool routes

Safe Writer, Code Safety, Route Guardian Action, and tool-return paths will read their destinations from Current Map.

This removes the stale v27 return and the missing `pmp-clean-v13.html` return.

### P5 — Restrict recovery authority

Last Good, Recovery Tools, and Candidate Follow will preserve saved evidence but cannot directly execute arbitrary saved HTML routes.

A saved route becomes a candidate and must be explicitly allowed by Current Map recovery policy.

### P6 — Quarantine historic authority

Old maps remain inspectable as evidence but lose current status. Old Guardians, Reload Owners, and wrappers become Current Map delegates or fail-closed historic notices.

History is retained; it is not deleted.

### P7 — Repeat the full authority audit

Repeat the 65-object census. A-002 passes only when no independent route selector remains and all tested app/tool/recovery flows preserve data.

## Rollback design

Each phase receives its own commit and rollback group.

Rollback restores exact baseline Git blobs. The new resolver is deleted when P1 is rolled back. Rollback proceeds in reverse order:

`P7 → P6 → P5 → P4 → P3 → P2 → P1 → P0`

Rollback is code-only. It may not clear:

- localStorage;
- IndexedDB;
- Cache Storage;
- Bank data;
- user content;
- saved spots;
- move ledger;
- staged Safe Writer or Code Safety content.

Failed test evidence is retained rather than deleted.

## Stop conditions

Stop immediately when any of these occurs:

- an identity does not match;
- the baseline moved without a new freeze;
- Current Map failure opens an alternate route;
- any old map or hard-coded current target is consulted;
- a screen cannot be restored;
- a tool cannot return safely;
- recovery evidence changes;
- a historic route launches as current;
- any Bank, user, storage, or IndexedDB data is lost;
- a certification claim exceeds the tested scope.

## Current decision

`A002_PREEXECUTION_PACKET_COMPLETE_PATCH_EXECUTION_NOT_AUTHORIZED`

No app, route, runtime, storage, cache, IndexedDB, Bank, DOM, or visual file has been changed by this preparation.
