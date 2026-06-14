# Packet 01.5 — Discovery Pass 12

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for network trust, API semantics, authentication sessions, authorization enforcement, replay, rate limits, remote configuration, third-party web content, redirects, and cross-origin boundary failures.

## Provisional records

### NET-002 — TLS success is mistaken for endpoint identity

A valid encrypted connection may still terminate at the wrong host, compromised account, replaced origin, corporate proxy, or attacker-controlled endpoint with a valid certificate.

HARM: secrets and trusted actions reach the wrong system.

OVERLAP TO CHECK: SEC-009, AUTHN-001.

### NET-003 — Captive portal, proxy, VPN, or filtering layer alters traffic

Public Wi-Fi, enterprise proxies, VPNs, content filters, and carrier systems may block, redirect, inspect, modify, or delay requests.

HARM: login, update, proof, and provider behavior differs from the expected network path.

OVERLAP TO CHECK: NET-001, SEC-010.

### NET-004 — Redirect chain crosses an untrusted origin

Authentication, downloads, APIs, links, and recovery flows may follow redirects to a different host, scheme, port, or path without rechecking trust.

HARM: credentials, tokens, files, or approvals are disclosed to an unintended origin.

OVERLAP TO CHECK: SEC-010, CORS-003.

### NET-005 — DNS, connection, and cache state disagree

Different devices, caches, resolvers, providers, or service workers may resolve the same name to different origins or generations.

HARM: users receive inconsistent or attacker-controlled content under one familiar name.

OVERLAP TO CHECK: SEC-009, REL-012.

### NET-006 — Response truncation is parsed as a complete success

A connection may end after headers or partial JSON, HTML, file, log, or artifact transfer.

HARM: incomplete data is saved, verified, migrated, or executed as complete.

OVERLAP TO CHECK: TOOL-002, REL-002.

### NET-007 — Requests and responses are reordered

Retries, parallel connections, caches, queues, and asynchronous providers may deliver newer and older results out of order.

HARM: stale state overwrites current state or a later approval binds to an earlier request.

OVERLAP TO CHECK: SYNC-002, REL-006.

### NET-008 — Online/offline indicators are unreliable

The device may report connectivity while DNS, authentication, provider, or target routes remain unavailable, or report offline while queued paths still execute.

HARM: the app selects an unsafe retry, fallback, or queue state.

OVERLAP TO CHECK: QUAL-001, REL-009.

### API-001 — Undocumented API defaults change behavior

Omitted fields may trigger provider defaults for privacy, retention, model, permissions, pagination, overwrite, retries, or output format.

HARM: the same request silently acquires new meaning.

OVERLAP TO CHECK: PROV-001, SEM-001.

### API-002 — HTTP success code hides partial or logical failure

An API may return 200 or 202 while embedding errors, skipped items, rejected fields, delayed processing, or partial completion in the body.

HARM: the project records full success from transport-level success.

OVERLAP TO CHECK: TOOL-002, UI-004.

### API-003 — Pagination, filtering, or result limits omit records

Search, issue, email, file, log, and provider endpoints may return only the first page, a capped set, or filtered records.

HARM: audits, backups, deletions, and Packet 1.5 loads are incomplete.

OVERLAP TO CHECK: AIH-006, BKP-001.

### API-004 — API ordering is unstable or undefined

Records may be returned in changing order when no explicit stable sort and tie-breaker are requested.

HARM: pages skip, duplicate, or reorder records between calls.

OVERLAP TO CHECK: NET-007, BUILDINT-006.

### API-005 — Error schemas change or collapse distinct failures

Authentication, authorization, validation, quota, conflict, timeout, and provider failures may share one generic response or change shape.

HARM: the wrong retry, warning, or recovery action is chosen.

OVERLAP TO CHECK: UI-006, PROV-001.

### API-006 — Duplicate, unknown, or conflicting response fields are accepted

A parser may choose the first, last, coerced, or silently ignored value when fields repeat or conflict.

HARM: attacker-controlled or malformed responses gain ambiguous meaning.

OVERLAP TO CHECK: SCHEMA-003, SCHEMA-005.

### API-007 — Webhooks are delayed, duplicated, missing, or out of order

Remote event delivery may be retried or arrive after polling and manual changes.

HARM: actions repeat, stale state returns, or valid changes are reversed.

OVERLAP TO CHECK: REL-008, NET-007.

### API-008 — Eventual consistency is treated as immediate truth

A successful write may not appear in later reads, indexes, caches, or secondary regions for some time.

HARM: the system retries, overwrites, or falsely declares failure.

OVERLAP TO CHECK: UI-004, SYNC-001.

### API-009 — Deprecation or version negotiation is silent

Providers may route old endpoints to compatibility behavior, fallback models, reduced fields, or sunset paths without a hard failure.

HARM: degraded semantics continue under a familiar interface.

OVERLAP TO CHECK: QUAL-003, PROV-001.

### AUTHN-001 — Tokens are stored or transmitted in exposed locations

Access tokens, refresh tokens, session IDs, API keys, and recovery codes may appear in URLs, local storage, logs, clipboard, Notes, screenshots, or repository files.

HARM: possession of leaked data grants account or project access.

OVERLAP TO CHECK: SEC-006, CRYPTO-002.

### AUTHN-002 — Refresh-token race creates conflicting sessions

Several tabs, devices, retries, or queued requests may refresh or rotate credentials at the same time.

HARM: valid sessions are revoked unpredictably or stale credentials remain active.

OVERLAP TO CHECK: REL-006, AUTHN-005.

### AUTHN-003 — Session fixation or reuse binds activity to the wrong identity

A session identifier may exist before login, survive account change, or be reused across users, devices, or environments.

HARM: actions and evidence attach to the wrong authenticated identity.

OVERLAP TO CHECK: IDENT-003, REL-001.

### AUTHN-004 — Device-bound or passkey authentication blocks recovery and migration

Credentials may depend on a specific device, biometric state, platform account, secure enclave, or synchronized keychain.

HARM: device loss or provider migration removes legitimate access.

OVERLAP TO CHECK: PHY-004, SUCC-003.

### AUTHN-005 — Logout, revocation, or password change leaves active sessions

Cached tokens, service workers, app sessions, provider grants, devices, and API clients may remain authorized.

HARM: believed-revoked access continues to operate.

OVERLAP TO CHECK: AUTH-003, RET-002.

### AUTHN-006 — MFA and recovery paths are weaker than normal login

SMS, email recovery, backup codes, support processes, trusted devices, and reset links may bypass stronger authentication.

HARM: attackers target recovery rather than primary login.

OVERLAP TO CHECK: AUTH-002, SOC-002.

### AUTHZ-001 — Authorization is enforced only in the client interface

Buttons and routes may be hidden while direct API, URL, script, or tool calls remain unrestricted.

HARM: bypassing the interface grants forbidden actions.

OVERLAP TO CHECK: RUN-015, AUTH-004.

### AUTHZ-002 — Object identifiers allow access to another record

Changing a file ID, candidate ID, user ID, packet ID, branch, path, or resource name may reveal or modify another object without a separate ownership check.

HARM: private data and project authority cross boundaries.

OVERLAP TO CHECK: IDENT-003, SEC-004.

### AUTHZ-003 — Cached roles and permissions remain stale

The app, API gateway, provider, browser, or backend may continue using permissions after they are changed or revoked.

HARM: old authority survives longer than the governance record.

OVERLAP TO CHECK: AUTH-003, UI-001.

### AUTHZ-004 — Confused-deputy behavior uses stronger service authority

A low-authority user or component may ask a trusted backend, Shortcut, bot, or automation to perform an action using its broader credentials.

HARM: indirect requests bypass the requester’s limits.

OVERLAP TO CHECK: AUTH-008, TOOL-001.

### AUTHZ-005 — Combined permissions exceed every intended role

Several individually limited tokens, providers, automations, or roles may compose into full project control.

HARM: separation of duties exists on paper but not in combination.

OVERLAP TO CHECK: AUTH-001, AUTH-008.

### AUTHZ-006 — Authorization failure falls back to permissive behavior

Timeout, missing policy, unavailable identity provider, parse error, or unknown role may default to allow, owner, local mode, or cached permission.

HARM: uncertainty grants access instead of holding safely.

OVERLAP TO CHECK: AUTO-004, QUAL-001.

### REPLAY-001 — Captured request can be executed again

An approval, write, deployment, deletion, webhook, or recovery request may lack a nonce, sequence, expiry, or used-once record.

HARM: previously valid authority is reused for a new side effect.

OVERLAP TO CHECK: DEST-007, CRYPTO-005.

### REPLAY-002 — Retry key is absent, unstable, or scoped too broadly

Idempotency identifiers may change between retries, collide across actions, or be reused for different targets.

HARM: actions duplicate or unrelated requests are incorrectly suppressed.

OVERLAP TO CHECK: REL-008, REL-001.

### REPLAY-003 — Delayed signed request remains valid after state changes

A request may be authentic but arrive after its target, authority, candidate, policy, or user intent has changed.

HARM: valid old instructions cause invalid current effects.

OVERLAP TO CHECK: REL-009, INTENT-002.

### RATE-001 — Rate limiting is treated as ordinary failure

429 responses, provider throttling, concurrency caps, and abuse controls may trigger immediate retries or fallback without respecting reset information.

HARM: the project amplifies throttling, consumes quota, or creates duplicate work.

OVERLAP TO CHECK: AUTO-005, PROV-002.

### RATE-002 — No backpressure protects downstream systems

Fast producers may overwhelm storage, providers, queues, renderers, validators, notifications, or human review.

HARM: memory growth, dropped work, stale approvals, and cascading failure.

OVERLAP TO CHECK: PERF-002, AUTO-002.

### RATE-003 — Per-user and global limits are confused

One device, account, project, provider, or shared service may consume a quota assumed to belong to another scope.

HARM: unrelated work is blocked or one actor exhausts the project’s capacity.

OVERLAP TO CHECK: ECO-002, AUTHZ-005.

### REMOTE-001 — Remote configuration changes behavior without a release

Feature flags, prompts, model choices, endpoints, limits, policy, routing, and safety thresholds may change outside the repository.

HARM: the running system changes without normal review or proof.

OVERLAP TO CHECK: BUILDINT-002, SELF-004.

### REMOTE-002 — Remote configuration is stale, partially loaded, or split across clients

Caches, regions, tabs, devices, and offline states may hold different configurations.

HARM: users and validators execute different policies under the same version.

OVERLAP TO CHECK: REL-004, UI-001.

### REMOTE-003 — Remote kill switch or flag has excessive authority

A provider or compromised account may disable protection, enable experimental behavior, redirect endpoints, or expose data through one configuration change.

HARM: a low-friction control bypasses the permanent project laws.

OVERLAP TO CHECK: AUTH-004, EMERG-001.

### WEB-001 — Third-party script or embedded content executes with page trust

Analytics, fonts, widgets, libraries, iframes, previews, and externally hosted assets may run or communicate inside the application context.

HARM: external code observes or alters private project behavior.

OVERLAP TO CHECK: SEC-002, SUPPLY-003.

### WEB-002 — External links leak sensitive referrer, query, or fragment data

Navigating away may disclose current routes, object IDs, search text, tokens, packet names, or user state.

HARM: third parties receive private project metadata.

OVERLAP TO CHECK: PRIV-002, AUTHN-001.

### WEB-003 — Window, iframe, opener, or message channel trusts the wrong sender

Cross-window messages and embedded content may not verify exact origin, source window, message type, and object identity.

HARM: another page can request actions, inject data, or read responses.

OVERLAP TO CHECK: SEC-010, CORS-001.

### CORS-001 — Cross-origin policy is overly broad or reflected from input

Wildcard origins, credentialed requests, origin reflection, broad methods, or broad headers may expose APIs to unintended websites.

HARM: a malicious site acts through the user’s authenticated session.

OVERLAP TO CHECK: AUTHN-003, WEB-003.

### CORS-002 — Preflight and actual authorization rules differ

A server may approve an OPTIONS request but enforce different methods, headers, credentials, or object checks on the real request.

HARM: clients misinterpret capability or unexpected requests succeed.

OVERLAP TO CHECK: AUTHZ-001, API-005.

### CORS-003 — Redirect, alternate origin, or subdomain escapes the intended boundary

Requests may move between www, API, CDN, preview, staging, custom domain, blob, or provider origins with different cookies and policies.

HARM: trust follows a familiar project name across technically different security boundaries.

OVERLAP TO CHECK: NET-004, SEC-009.

## Pass 12 result

New provisional records: 43
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
- Current preserved plus provisional: 526

NEXT DISCOVERY PASS:
Incident detection, containment, evidence preservation, severity errors, communication failure, recovery verification, post-incident learning, repeated incidents, and hidden compromise persistence.

END PACKET 01.5 — DISCOVERY PASS 12
