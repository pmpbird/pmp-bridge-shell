# App Orchestrator Pass 2 — P2-B Status

## Current position

- Overall project pass: **Pass 2**
- Phase: **P2-B — exact-source actor authorization gate and forbidden-action fixtures**
- P2-A: complete and merged
- Pass 2 complete: **no**
- Pass 3 started: **no**

## P2-B job

P2-B replaces the old passive authority description at the active inner boundary with a fail-closed runtime gate.

The gate must:

1. accept only registered actor paths whose bytes match both the Pass 2 registry and the sealed A-003 source identity;
2. execute registered scripts only inside their actor identity;
3. carry actor identity through timers, promises, events, and child-window installation;
4. intercept protected side-effect APIs before native execution;
5. deny unknown actors, wrong bytes, unregistered scripts, and undeclared capabilities;
6. keep destructive capabilities globally forbidden;
7. append quarantine evidence with `side_effect_executed: false`.

## Protected capability surfaces

- local and session storage writes, removals, and clears;
- one-shot and recurring timers;
- event listener registration and handler properties;
- DOM mutation and dynamic script insertion;
- network fetch, XHR, and WebSocket creation;
- IndexedDB open and database deletion;
- Cache API open, write, and delete;
- iframe and window navigation through authorized loaders;
- Service Worker registration;
- `eval` and dynamic `Function` construction.

## Pass boundary

P2-B does not finish Pass 2. The following remain for P2-C:

- Bug Watch append-only immutable receipt history;
- recurring actor owner, stop, expiry, and handoff enforcement;
- whole-active-set lifecycle certification.

No Pass 3 owner action gateway is created by this phase.
