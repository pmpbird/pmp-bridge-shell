# Packet 01.5 — Discovery Pass 15

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for architecture-boundary failure, core contamination, shell dependence, portability erosion, hidden state, configuration coupling, feature interaction, and monolithic failure.

## Provisional records

### ARCH-001 — Component boundaries are implied rather than enforced

Modules may be described as separate while sharing direct imports, mutable objects, storage, permissions, or authority.

HARM: one component can silently reshape another despite the documented architecture.

OVERLAP TO CHECK: AUTH-008, COV-003.

### ARCH-002 — Circular dependencies hide real ownership

Core, shell, data, routing, validation, and recovery components may depend on one another in cycles.

HARM: no component can be replaced, tested, initialized, or recovered independently.

OVERLAP TO CHECK: REG-007, MAINT-005.

### ARCH-003 — Shared mutable state crosses boundaries

Several components may read and write the same objects, caches, globals, records, or configuration without an explicit owner.

HARM: changes have invisible side effects and race conditions.

OVERLAP TO CHECK: REL-006, STATE-001.

### ARCH-004 — Direct imports bypass declared interfaces

A component may reach internal functions, storage keys, private fields, or provider clients instead of using the protected boundary.

HARM: safeguards and compatibility contracts are bypassed.

OVERLAP TO CHECK: AUTHZ-001, BUILDINT-001.

### ARCH-005 — Control plane, data plane, and evidence plane are mixed

The same records or functions may carry user data, authority decisions, runtime commands, and proof status.

HARM: ordinary data edits can alter control or evidence.

OVERLAP TO CHECK: AUD-001, SEM-004.

### ARCH-006 — Startup and shutdown order are hidden dependencies

Components may work only when initialized, restored, authenticated, or closed in a specific undocumented sequence.

HARM: recovery, migration, and replacement fail outside the normal path.

OVERLAP TO CHECK: MIG-005, FLOW-002.

### CORE-001 — Core logic imports shell or browser APIs

Core behavior may directly depend on DOM, service worker, localStorage, Notes, Shortcuts, GitHub, hosting, or iOS-specific interfaces.

HARM: the core cannot move without carrying the current shell’s structure and limits.

OVERLAP TO CHECK: LOCK-002, PLAT-003.

### CORE-002 — Core identity is stored in shell metadata

Routes, filenames, UI labels, hosting paths, browser keys, repository layout, or provider IDs may define what the core is.

HARM: replacing the shell changes or loses core identity.

OVERLAP TO CHECK: REL-001, PORT-003.

### CORE-003 — Core state depends on shell storage semantics

The core may assume localStorage ordering, browser persistence, Git history, Notes formatting, provider transactions, or one device’s behavior.

HARM: a new shell preserves data bytes but changes meaning or durability.

OVERLAP TO CHECK: REL-010, SCHEMA-001.

### CORE-004 — Core serialization uses builder-specific structure

Records may encode builder component names, generated IDs, route shapes, UI hierarchy, hidden defaults, or proprietary conventions.

HARM: the builder leaves an imprint inside the supposedly pure core.

OVERLAP TO CHECK: LOCK-001, SCHEMA-002.

### CORE-005 — Core protections exist only in the current shell

Validation, authorization, privacy, rollback, and invariants may be enforced by UI or hosting code rather than by the core contract.

HARM: moving the core removes its protection while preserving its appearance.

OVERLAP TO CHECK: AUTHZ-001, SHELL-005.

### CORE-006 — Core decisions depend on one provider’s model or tool behavior

Reasoning, parsing, confidence, tool selection, memory, or safety may assume undocumented behavior from the present AI or connector.

HARM: provider replacement changes core decisions and identity.

OVERLAP TO CHECK: LOCK-002, PROV-001.

### CORE-007 — Portability claim excludes required external conditions

The core may be called portable while requiring a specific origin, account, keychain, device, directory, provider, or remote service.

HARM: portability exists only inside the original environment.

OVERLAP TO CHECK: LOCK-004, PORT-006.

### CORE-008 — Core version is not independently identifiable

Shell version, repository commit, deployed build, prompt version, schema, and core logic may share one vague version label.

HARM: proof and migration cannot identify the exact core being carried.

OVERLAP TO CHECK: PROOFCHAIN-001, SELF-004.

### SHELL-001 — Shell transforms inputs before the core sees them

UI controls, parsers, file loaders, provider adapters, or route handlers may normalize, omit, reorder, truncate, or reinterpret input.

HARM: core behavior depends on hidden shell preprocessing.

OVERLAP TO CHECK: CTX-007, SEM-002.

### SHELL-002 — Shell controls routing or decision meaning

Navigation, screen sequence, button availability, feature flags, or adapter logic may decide which core path is reachable.

HARM: the shell defines the environment instead of merely carrying it.

OVERLAP TO CHECK: UI-003, REMOTE-001.

### SHELL-003 — Shell caches a stale or partial core

Service workers, bundles, browser storage, app snapshots, or local files may load a different core generation than the visible shell.

HARM: interface and logic identities split.

OVERLAP TO CHECK: REL-012, REL-005.

### SHELL-004 — Shell fallback silently substitutes different behavior

Offline mode, provider fallback, cached output, local approximation, or reduced functionality may replace the core path without an explicit identity change.

HARM: the app appears to carry the same environment while running a different one.

OVERLAP TO CHECK: QUAL-001, API-009.

### SHELL-005 — Shell permissions become implicit core authority

The core may inherit broad browser, repository, provider, Shortcut, or account permissions because the shell possesses them.

HARM: the core’s true authority is larger than its contract states.

OVERLAP TO CHECK: AUTHZ-004, AUTHZ-005.

### SHELL-006 — Shell update silently reshapes the core contract

A UI, adapter, hosting, provider, or platform update may change field defaults, routes, timing, available tools, error behavior, or persistence.

HARM: the core’s effective behavior changes without a core revision.

OVERLAP TO CHECK: PROV-001, TOOL-003.

### SHELL-007 — Different shells interpret the same core differently

Two carriers may disagree about defaults, ordering, validation, missing fields, permissions, error recovery, or unsupported features.

HARM: one core package produces multiple incompatible environments.

OVERLAP TO CHECK: SCHEMA-006, PORT-004.

### PORT-003 — Export preserves records but not executable context

An export may omit adapters, permissions, prompts, schemas, indexes, routes, provider settings, or initialization order.

HARM: the core can be copied but not made operational.

OVERLAP TO CHECK: LOCK-005, BKP-001.

### PORT-004 — Unsupported capability is silently substituted

A new shell may replace unavailable storage, background, security, notification, or provider features with weaker alternatives.

HARM: portability introduces silent semantic downgrade.

OVERLAP TO CHECK: QUAL-001, SHELL-004.

### PORT-005 — Capability detection reports presence but not required behavior

An API or feature may exist while lacking persistence, limits, security, performance, or lifecycle behavior assumed by the core.

HARM: compatibility tests pass while real operation fails.

OVERLAP TO CHECK: TEST-003, PLAT-001.

### PORT-006 — Portable operation still depends on remote mutable assets

Fonts, scripts, models, schemas, prompts, libraries, endpoints, or configuration may be fetched from external locations.

HARM: the carried package is incomplete and can change after transfer.

OVERLAP TO CHECK: REPRO-002, WEB-001.

### PORT-007 — Export/import round trip is not lossless

Repeated export and import may alter order, unknown fields, timestamps, links, permissions, binary data, or provenance.

HARM: each move slowly corrupts the core.

OVERLAP TO CHECK: MIG-003, SCHEMA-003.

### STATE-001 — Hidden state exists outside the canonical store

Closures, memory, caches, DOM, service workers, provider sessions, queued tasks, feature flags, and temporary files may affect behavior.

HARM: backup, restore, proof, and migration omit part of the running environment.

OVERLAP TO CHECK: CTX-005, EVAL-003.

### STATE-002 — Several stores claim authority for the same state

Local storage, backend, Notes, GitHub, cache, memory, and current chat may each hold a writable copy.

HARM: state conflicts cannot be resolved by architecture alone.

OVERLAP TO CHECK: SYNC-001, AUTH-005.

### STATE-003 — Derived state is not rebuilt after source change

Indexes, summaries, counts, status, permissions, routes, and UI may remain from an earlier source generation.

HARM: the system acts on stale conclusions.

OVERLAP TO CHECK: SEM-005, UI-001.

### STATE-004 — Reset or logout leaves residual state

Caches, drafts, service workers, tokens, in-memory records, recent files, notifications, and provider sessions may survive a reset.

HARM: old identity and data leak into the next session or user.

OVERLAP TO CHECK: AUTHN-005, RET-002.

### STATE-005 — Snapshot excludes in-flight operations

A backup or state capture may omit pending requests, locks, queues, transactions, retries, and unsaved drafts.

HARM: restore repeats or loses actions without knowing which.

OVERLAP TO CHECK: FLOW-001, BKP-001.

### STATE-006 — State machine permits impossible transitions

A record may move from stale to approved, deleted to active, unverified to deployed, or closed to modified without required intermediate proof.

HARM: invalid states become representable and later trusted.

OVERLAP TO CHECK: GOV-006, UI-003.

### CONFIG-001 — Configuration precedence is unclear

Defaults, local files, environment variables, remote flags, user settings, provider settings, and cached values may conflict.

HARM: actual behavior cannot be predicted from any one record.

OVERLAP TO CHECK: BUILDINT-002, REMOTE-002.

### CONFIG-002 — Secrets and ordinary configuration are mixed

The same files, exports, interfaces, logs, or update paths may carry both public settings and credentials.

HARM: safe sharing or versioning of configuration exposes secrets.

OVERLAP TO CHECK: AUTHN-001, SEC-006.

### CONFIG-003 — Configuration update is partial across components

Some clients, providers, shells, workers, and caches may receive a new setting while others retain the old value.

HARM: one named environment runs conflicting rules.

OVERLAP TO CHECK: REMOTE-002, REL-004.

### CONFIG-004 — Configuration validation checks shape but not compatibility

A setting may be syntactically valid while incompatible with the current schema, provider, permission, shell, or core version.

HARM: accepted configuration breaks behavior later.

OVERLAP TO CHECK: SCHEMA-005, TEST-001.

### INTERACT-001 — Individually safe features become unsafe together

Caching, retries, offline queues, auto-save, restore, sync, remote flags, and notifications may interact in combinations not covered by their individual designs.

HARM: composition creates failures no feature owns.

OVERLAP TO CHECK: COV-003, AUTO-005.

### INTERACT-002 — Feature execution order changes meaning

Validation, migration, authorization, fallback, synchronization, logging, and deployment may produce different outcomes when reordered.

HARM: timing and implementation details redefine policy.

OVERLAP TO CHECK: ARCH-006, TEST-008.

### INTERACT-003 — One feature disables another feature’s protection

Performance mode, offline mode, emergency mode, debug mode, recovery mode, or compatibility mode may bypass validation, logging, privacy, or approval.

HARM: a useful feature becomes an authority escape.

OVERLAP TO CHECK: EMERG-001, QUAL-001.

### MONO-001 — One process or shell failure disables the entire environment

Rendering, storage, routing, validation, provider access, recovery, and evidence may all live in one runtime.

HARM: one crash or corruption removes every operating and recovery surface.

OVERLAP TO CHECK: AUTH-001, DIS-003.

### MONO-002 — Changes require full-system deployment and rollback

A small fix to one feature may require rebuilding, retesting, promoting, and reverting the whole environment.

HARM: unrelated stable behavior shares the same release risk.

OVERLAP TO CHECK: MAINT-005, DEPLOY-003.

### MONO-003 — Fault isolation and ownership are impossible

Logs, state, permissions, dependencies, and failures may be so intertwined that no component can be quarantined independently.

HARM: incidents require broad shutdown and destructive recovery.

OVERLAP TO CHECK: CONTAIN-002, INCSEV-003.

## Pass 15 result

New provisional records: 42
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
- Pass 09 provisional: 42
- Pass 10 provisional: 43
- Pass 11 provisional: 44
- Pass 12 provisional: 43
- Pass 13 provisional: 43
- Pass 14 provisional: 42
- Pass 15 provisional: 42
- Current preserved plus provisional: 653

NEXT DISCOVERY PASS:
Search and retrieval failure, indexing drift, ranking bias, missing context, duplicate suppression, stale embeddings, archive invisibility, and knowledge-base poisoning.

END PACKET 01.5 — DISCOVERY PASS 15
