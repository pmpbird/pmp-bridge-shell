# Packet 01.5 — Discovery Pass 03

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for reliability, crash-consistency, stale-client, backup, restore, provider-loss, platform-lifecycle, network, cache, quota, and recovery-chain failures.

## Provisional records

### REL-002 — Multi-record updates are not atomic

A change may update several keys, files, manifests, receipts, or indexes. Failure between writes can leave a mixed state that looks partly current and partly old.

HARM: corrupted identity, broken routes, wrong evidence, or unsafe recovery.

OVERLAP TO CHECK: DATA-004, DATA-009, RUN-008.

### REL-003 — Side effect succeeds but receipt creation fails

A write, promotion, deletion, Shortcut action, Notes save, backend action, or GitHub update may succeed while the acknowledgement or receipt fails.

HARM: retrying may duplicate the action, while not retrying may leave unrecorded state.

OVERLAP TO CHECK: OPS-010, RUN-014.

### REL-004 — Partial deployment creates a split route

Only some HTML, JSON, loader, service-worker, asset, or configuration files may update successfully.

HARM: different users or reloads may execute incompatible generations of the app.

OVERLAP TO CHECK: BUILD-004, PLAT-010, RUN-007.

### REL-005 — Stale client opens a newer data schema

An old Home Screen app, cached loader, tab, or service worker may read or write data created by a newer version.

HARM: silent downgrade, corruption, data loss, or invalid migration.

OVERLAP TO CHECK: DATA-005, PLAT-005, PLAT-010.

### REL-006 — Concurrent tabs or devices overwrite each other

Multiple tabs, browser sessions, devices, Shortcuts, or backend requests may modify the same logical record without locking, version checks, or conflict resolution.

HARM: last-write-wins data loss, duplicated work, or contradictory receipts.

OVERLAP TO CHECK: DATA-007, DATA-010.

### REL-007 — Time and clock identity are untrusted

Device clock changes, time-zone changes, offline time, provider time, or reused timestamps may alter ordering, expiry, ID generation, or evidence interpretation.

HARM: stale evidence appears new, IDs collide, or valid work appears expired.

OVERLAP TO CHECK: REL-001, GOV-009, PROOF-012.

### REL-008 — Retries repeat non-idempotent actions

A timeout or missing acknowledgement may cause a write, issue creation, email, Note append, deployment, payment-like operation, or promotion request to run more than once.

HARM: duplication, repeated external actions, or conflicting project state.

OVERLAP TO CHECK: OPS-010, OPS-012.

### REL-009 — Offline queue replays obsolete actions

Queued work may execute after the user changed their mind, a candidate was replaced, authority expired, or the project advanced.

HARM: stale actions modify the wrong version or violate current intent.

OVERLAP TO CHECK: OPS-011, RUN-013.

### REL-010 — Browser storage or cache is evicted without warning

Safari or iOS may clear localStorage, Cache API data, service-worker data, or temporary files because of pressure, policy, inactivity, reinstall, or browser reset.

HARM: missing state, broken offline operation, or unrecoverable local records.

OVERLAP TO CHECK: DATA-001, PLAT-004, PLAT-011.

### REL-011 — Storage quota exhaustion is not safely handled

Writes may fail because local, Notes, GitHub, backend, device, or archive storage is full.

HARM: partial saves, missing receipts, lost evidence, or failed backups.

OVERLAP TO CHECK: DATA-006, OPS-003.

### REL-012 — Service-worker or cache split-brain

A page, service worker, Cache API, and network may each serve different versions. Update activation may be delayed or inconsistent.

HARM: the app appears updated while critical code remains stale.

OVERLAP TO CHECK: PLAT-005, PLAT-010.

### BKP-001 — Backup completeness is not proven

A backup may omit hidden keys, external records, Notes, Shortcuts, credentials, indexes, manifests, binary files, or records added after the backup process was designed.

HARM: restore succeeds technically but loses essential project state.

OVERLAP TO CHECK: DATA-002, DATA-003, OPS-006.

### BKP-002 — Restore can overwrite newer valid state

A backup may be older than the current app or may contain only part of the record set.

HARM: recovery destroys newer evidence, decisions, user data, or limitation updates.

OVERLAP TO CHECK: DATA-009, OPS-006.

### BKP-003 — Backup encryption or recovery key can be lost

A protected backup may depend on a password, device keychain, provider account, recovery phrase, or encryption key with no tested recovery path.

HARM: the backup exists but can never be restored.

OVERLAP TO CHECK: DATA-008, OPS-008.

### REC-001 — Rollback depends on the same damaged system

Rollback code, manifests, credentials, routes, or backups may be stored or executed by the component that just failed or was compromised.

HARM: the advertised rollback path is unavailable during the incident it is meant to solve.

OVERLAP TO CHECK: RUN-011, OPS-007.

### REC-002 — Recovery instructions may be stale or inaccessible during outage

Instructions may exist only inside the broken app, unavailable chat, lost Note, inaccessible repository, or provider account.

HARM: the user cannot recover when normal tools are unavailable.

OVERLAP TO CHECK: OPS-005, OPS-015.

### REC-003 — Recovery is documented but not rehearsed end to end

Backup, restore, rollback, provider replacement, domain recovery, and device replacement may never be tested from failure through verified normal operation.

HARM: hidden missing steps appear only during a real incident.

OVERLAP TO CHECK: PROOF-006, OPS-007.

### PROV-001 — Provider semantics change without a version change

An AI, hosting, GitHub, Notes, Shortcut, CDN, or backend provider may change behavior, limits, output shape, policy, safety filtering, retention, or availability without preserving prior semantics.

HARM: previously valid assumptions and tests stop matching reality.

OVERLAP TO CHECK: PROOF-012, OPS-004, PLAT-014.

### PROV-002 — Provider account, rate, quota, or region failure

The project may lose access because of suspension, rate limiting, quota exhaustion, billing-policy change, region restriction, account recovery failure, or provider shutdown.

HARM: core workflows stop, evidence becomes unreachable, or the user is locked out.

OVERLAP TO CHECK: OPS-004, OPS-008.

### PLAT-003 — iOS, Safari, Notes, or Shortcuts lifecycle changes

Operating-system updates may change Home Screen behavior, storage persistence, background limits, clipboard access, Shortcut automation, Notes formatting, file handling, or service-worker behavior.

HARM: a proven workflow fails after an ordinary device update.

OVERLAP TO CHECK: PLAT-001, PLAT-002, PLAT-014.

### NET-001 — Timeout outcome is ambiguous

A client may time out without knowing whether the server, Shortcut, GitHub, Notes, or provider completed the requested action.

HARM: unsafe retry, duplicate work, or missing acknowledgement.

OVERLAP TO CHECK: REL-003, REL-008, OPS-010.

## Pass 03 result

New provisional records: 21
Routing decisions made: 0
Records closed: 0
Deduplication required later: Yes
Discovery saturation: NOT REACHED

Combined working total:
- Existing baseline: 122
- Pass 01 provisional: 10
- Pass 02 provisional: 20
- Pass 03 provisional: 21
- Current preserved plus provisional: 173

NEXT DISCOVERY PASS:
Performance, resource exhaustion, observability, measurement errors, accessibility, localization, user-intent ambiguity, and metric-gaming risks.

END PACKET 01.5 — DISCOVERY PASS 03
