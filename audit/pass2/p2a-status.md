# App Orchestrator Pass 2 — P2-A Status

## Current position

- Overall project pass: **Pass 2**
- Phase: **P2-A — exact-main scope lock, active actor census, and blocker freeze**
- Pass 1: formally closed at exercised scope
- Pass 2 runtime enforcement: **not implemented yet**
- Pass 3 and later passes: not started

## Why Pass 2 had to be reopened

The historical Pass 2 freeze proved that one then-current active path appeared to work. It did not prove whole-runtime authority enforcement.

The current audit found:

1. `pmp-authority-rules-v1.js` is explicitly a passive authority map.
2. The old freeze receipt is explicitly `active_path_only`.
3. The old route names obsolete Current Map v10 support.
4. Bug Watch writes one mutable receipt key rather than an append-only history.
5. Bug Watch runs recurring scans without a formal stop, expiry, or handoff.
6. No unknown-actor pre-side-effect block/quarantine gate is proven.

## P2-A job

P2-A does not alter runtime behavior. It establishes the exact current source and actor truth needed before enforcement can safely be added.

The census is generated from the sealed A-003 runtime manifest and records:

- every protected executable document and script;
- exact path, Git blob, SHA-256, and byte size;
- current-map roles;
- owner and version signals;
- static actor classes;
- DOM, storage, cache, IDB, navigation, worker, timer, observer, frame, migration, rescue, diagnostics, and bug-capture capabilities;
- recurring actor stop-condition evidence;
- reconciliation against the 208 A-001 plus A-002 supplement identities.

## Stop line

P2-A may pass only as an inventory and scope-lock move. It must not be misreported as Pass 2 completion.

After P2-A passes, the next phase is:

**P2-B — build the actor authorization gate and forbidden-action fixtures.**
