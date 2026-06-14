# Packet 01.5 — Discovery Pass 08

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for data-meaning drift, schema evolution, migration failure, encryption and key handling, data minimization, identity linking, deletion semantics, synchronization, and privacy-inference risks.

## Provisional records

### SEM-001 — Field meaning changes while the field name stays the same

A stored field may keep the same key while its meaning, scope, source, confidence, or units change across versions.

HARM: old and new records appear compatible while representing different facts.

OVERLAP TO CHECK: DATA-005, GOV-009.

### SEM-002 — Missing, null, empty, false, zero, and unknown are conflated

Different states may be serialized or interpreted as equivalent.

HARM: absence of evidence becomes negative evidence, defaults overwrite unknowns, or required work appears complete.

OVERLAP TO CHECK: DATA-004, QUAL-002.

### SEM-003 — Units, precision, locale, and time zone are implicit

Numbers and dates may lack explicit units, precision, calendar, or time-zone identity.

HARM: thresholds, expiry, ordering, measurements, and migrations produce wrong results.

OVERLAP TO CHECK: LOC-001, REL-007.

### SEM-004 — Derived values lose source provenance

Summaries, scores, risk levels, owner lists, and status fields may be stored without the source records and transformation version that produced them.

HARM: derived truth cannot be reproduced or invalidated when inputs change.

OVERLAP TO CHECK: OBS-002, PROOF-002.

### SEM-005 — Cached derived data remains after source correction

A source record may be fixed or deleted while indexes, summaries, search results, counts, and packet-specific views remain stale.

HARM: corrected truth does not propagate to decisions.

OVERLAP TO CHECK: GOV-009, REG-006.

### SCHEMA-001 — No single authoritative schema exists

Code, documentation, examples, validators, exports, and stored records may each describe different structures.

HARM: producers and consumers silently disagree about valid data.

OVERLAP TO CHECK: DATA-004, MAINT-003.

### SCHEMA-002 — Schema version is not attached to each record

The system may infer record generation from app version, file location, or surrounding context.

HARM: mixed or copied records are parsed with the wrong rules.

OVERLAP TO CHECK: DATA-005, BUILD-011.

### SCHEMA-003 — Unknown fields are discarded during read and write

An older component may load a newer record, ignore fields it does not understand, and save the shortened record.

HARM: forward-compatible information is silently erased.

OVERLAP TO CHECK: REL-005, REG-010.

### SCHEMA-004 — Old clients continue writing obsolete shapes

Cached tabs, old Home Screen installs, scripts, Shortcuts, or providers may produce data after a new schema is active.

HARM: obsolete fields and assumptions re-enter current storage.

OVERLAP TO CHECK: REL-005, PLAT-003.

### SCHEMA-005 — Implicit type coercion accepts malformed data

Strings, numbers, booleans, arrays, objects, and dates may be converted automatically instead of rejected.

HARM: invalid records look valid and fail later in less visible ways.

OVERLAP TO CHECK: DATA-004, SEC-004.

### SCHEMA-006 — Multiple schema generations coexist without a compatibility matrix

Records, caches, backups, exports, and remote systems may simultaneously use several versions.

HARM: compatibility assumptions are guessed rather than proven.

OVERLAP TO CHECK: REL-004, REL-005.

### MIG-001 — Migration is not idempotent

Running a migration twice may duplicate, re-wrap, rename again, or transform already migrated values.

HARM: retries or recovery corrupt otherwise valid data.

OVERLAP TO CHECK: REL-008, DATA-005.

### MIG-002 — Partial migration has no safe resume point

A crash or interruption may leave some records migrated and others old without a durable progress marker.

HARM: rerun, rollback, and continuation each risk additional corruption.

OVERLAP TO CHECK: REL-002, REL-003.

### MIG-003 — Migration is structurally valid but semantically lossy

A new record may pass schema validation while dropping distinctions, evidence, order, history, links, or uncertainty.

HARM: data appears successfully migrated while meaning was lost.

OVERLAP TO CHECK: CTX-003, SCHEMA-003.

### MIG-004 — Rollback cannot safely handle writes made after migration

New-version records may be created before a rollback to the old schema.

HARM: rollback either loses new work or feeds unreadable data to the old app.

OVERLAP TO CHECK: DATA-009, SELF-005.

### MIG-005 — Migration order and cross-record dependencies are undefined

Indexes, parents, children, references, permissions, and derived records may require a specific sequence.

HARM: individually valid migrations create globally inconsistent state.

OVERLAP TO CHECK: REL-002, REG-007.

### MIG-006 — One malformed record blocks or is silently skipped

A migration may stop entirely, omit bad records, or substitute defaults without a quarantine and repair record.

HARM: availability fails or data disappears unnoticed.

OVERLAP TO CHECK: OBS-001, QUAL-001.

### MIG-007 — Migration tests use only clean synthetic fixtures

Real records may contain old bugs, duplicates, partial data, unusual text, large fields, or unknown versions absent from test fixtures.

HARM: production migration fails despite passing tests.

OVERLAP TO CHECK: MEAS-002, PROOF-004.

### CRYPTO-001 — “Encrypted at rest” is assumed rather than bounded

Browser storage, Notes, files, provider databases, device backups, logs, and exports may have different encryption properties.

HARM: sensitive data is treated as protected in places where it is readable.

OVERLAP TO CHECK: DATA-008, SEC-006.

### CRYPTO-002 — Encryption keys are stored with encrypted data

Keys, recovery tokens, or decrypting sessions may live in the same device, account, backup, repository, or provider as the ciphertext.

HARM: one compromise exposes both data and its protection.

OVERLAP TO CHECK: BKP-003, AUTH-001.

### CRYPTO-003 — Key rotation is undefined or incomplete

Old ciphertext, backups, devices, sessions, service accounts, and shared copies may continue using retired keys.

HARM: compromised keys remain useful or valid data becomes unreadable.

OVERLAP TO CHECK: AUTH-003, RET-002.

### CRYPTO-004 — Key loss has no bounded recovery path

A device reset, account loss, forgotten password, damaged keychain, or unavailable recovery code may permanently remove decryption ability.

HARM: protected data becomes unrecoverable.

OVERLAP TO CHECK: BKP-003, SUCC-003.

### CRYPTO-005 — Randomness, nonce, or identifier generation is weak or reused

Client clocks, predictable IDs, repeated nonces, poor entropy, or copied state may undermine cryptographic and identity guarantees.

HARM: collisions, replay, decryption risk, or forged identity.

OVERLAP TO CHECK: REL-001, SEC-007.

### CRYPTO-006 — Encryption lacks integrity and authenticity

Ciphertext may be encrypted without proving it was not altered or substituted.

HARM: corrupted or attacker-modified data decrypts into trusted-looking content.

OVERLAP TO CHECK: SEC-007, AUD-001.

### CRYPTO-007 — Metadata remains exposed despite content encryption

Filenames, sizes, timing, frequency, relationships, routes, owners, and access patterns may remain visible.

HARM: sensitive facts can be inferred without reading content.

OVERLAP TO CHECK: PRIV-002, AUD-005.

### MIN-001 — The project collects more data than each function needs

Prompts, full source, logs, device details, account identifiers, history, and screenshots may be gathered by default.

HARM: unnecessary exposure, retention burden, and larger breach impact.

OVERLAP TO CHECK: DATA-013, DATA-014.

### MIN-002 — Temporary and diagnostic fields become permanent

Debug payloads, raw provider responses, trace IDs, screenshots, and intermediate reasoning may remain in normal records or backups.

HARM: private and low-value data accumulates indefinitely.

OVERLAP TO CHECK: OBS-004, RET-004.

### MIN-003 — Data collected for one purpose is reused for another

Testing, support, debugging, model improvement, benchmarking, or analytics may reuse project data without a new boundary decision.

HARM: consent and privacy assumptions silently expand.

OVERLAP TO CHECK: RET-001, VIAB-004.

### MIN-004 — Sensitive information hides inside free text

Credentials, names, private source, health, location, finances, or recovery details may appear inside prompts, comments, filenames, logs, and Bug Memory.

HARM: field-level controls and deletion rules miss the actual sensitive content.

OVERLAP TO CHECK: SEC-006, SOC-005.

### IDENT-001 — Separate records can be linked into a single identity

Device data, timestamps, writing style, repository activity, provider IDs, routes, and project history may connect records thought to be separate.

HARM: privacy boundaries collapse through correlation.

OVERLAP TO CHECK: CRYPTO-007, PRIV-001.

### IDENT-002 — Pseudonyms are reversible through context

Stable IDs, rare events, filenames, commits, locations, and timing may reveal the person or project behind a pseudonym.

HARM: de-identified exports remain personally identifying.

OVERLAP TO CHECK: IDENT-001, PRIV-004.

### IDENT-003 — Records from different people or projects are merged incorrectly

Similar names, shared devices, reused accounts, copied packets, or imported archives may cause identity collision.

HARM: private data, evidence, authority, and obligations attach to the wrong owner.

OVERLAP TO CHECK: REL-001, REPO-003.

### IDENT-004 — Account, device, and project identity change over time

Email, phone number, Apple ID, domain, repository owner, device, or organization may change while records keep old identifiers.

HARM: legitimate continuity is mistaken for attack, or an attacker inherits trusted identity.

OVERLAP TO CHECK: AUTH-007, SUCC-003.

### DEL-001 — Soft deletion is presented as permanent deletion

A record may be hidden or marked deleted while content remains in storage, history, backups, indexes, logs, or providers.

HARM: user expectations and legal duties are not met.

OVERLAP TO CHECK: RET-002, DATA-014.

### DEL-002 — Deletion races with synchronization, retry, or restore

A deleted record may be recreated by an offline client, stale queue, retry, backup, or remote replica.

HARM: deletion does not remain deleted.

OVERLAP TO CHECK: RET-003, REL-009.

### DEL-003 — Deletion breaks relationships and evidence integrity

Removing one record may leave dangling references, invalid counts, broken receipts, orphaned children, or unverifiable decisions.

HARM: privacy repair damages project truth or runtime behavior.

OVERLAP TO CHECK: RET-001, MIG-005.

### SYNC-001 — Authoritative source is unclear during conflict

Apple Notes, GitHub, local storage, Files, backend, provider, and current chat may each contain a different version.

HARM: conflict resolution selects convenience rather than authority.

OVERLAP TO CHECK: AUTH-005, REG-003.

### SYNC-002 — Last-write-wins destroys semantically newer work

A later clock time may represent an older device, stale tab, partial record, or lower-authority source.

HARM: correct information is overwritten by a technically newer write.

OVERLAP TO CHECK: REL-006, REL-007.

### SYNC-003 — Offline branches diverge beyond automatic merge

Several devices or workflows may edit the same records independently for long periods.

HARM: automatic merging loses intent, while manual merging becomes error-prone.

OVERLAP TO CHECK: REL-006, OPS-011.

### SYNC-004 — Duplicate replay creates sync loops or repeated records

A merged, retried, or restored change may be treated as new and propagated repeatedly between systems.

HARM: duplication, endless synchronization, and quota exhaustion.

OVERLAP TO CHECK: REL-008, AUTO-005.

### PRIV-001 — Combined harmless fields reveal sensitive facts

Individually ordinary records may reveal routines, relationships, health, location, finances, beliefs, or security posture when combined.

HARM: privacy risk exceeds the sensitivity assigned to each field.

OVERLAP TO CHECK: IDENT-001, MIN-001.

### PRIV-002 — Timing and access patterns reveal behavior

Request times, failure times, commit patterns, provider calls, device activity, and recovery events may expose habits or absence.

HARM: metadata supports tracking, profiling, or targeted attack.

OVERLAP TO CHECK: CRYPTO-007, OBS-002.

### PRIV-003 — A model or provider can infer more than the explicit prompt contains

Source structure, writing style, bug history, filenames, and combined context may reveal identity, intent, skill level, private plans, or vulnerabilities.

HARM: sending “non-sensitive” context still exposes sensitive conclusions.

OVERLAP TO CHECK: AI-010, MIN-003.

### PRIV-004 — Small or unique datasets are easily re-identified

Rare project structure, unique bugs, exact timestamps, distinctive language, or singular device conditions may identify the project even after names are removed.

HARM: anonymization claims fail.

OVERLAP TO CHECK: IDENT-002, PROOF-015.

## Pass 08 result

New provisional records: 44
Routing decisions made: 0
Records closed: 0
Deduplication required later: Yes
Discovery saturation: NOT REACHED

Combined working total:
- Existing baseline: 122
- Pass 01 provisional: 10
- Pass 02 provisional: 20
- Pass 03 provisional: 21
- Pass 04 provisional: 29
- Pass 05 provisional: 33
- Pass 06 provisional: 35
- Pass 07 provisional: 40
- Pass 08 provisional: 44
- Current preserved plus provisional: 354

NEXT DISCOVERY PASS:
Testing blind spots, oracle failure, flaky tests, coverage illusion, test-data contamination, nondeterminism, mutation gaps, integration mismatch, and proof-chain failure.

END PACKET 01.5 — DISCOVERY PASS 08
