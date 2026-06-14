# Packet 01.5 — Discovery Pass 13

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for incident detection, severity and scope errors, containment failure, evidence preservation, communication failure, recovery verification, repeated incidents, false closure, and hidden compromise persistence.

## Provisional records

### INCDET-001 — Incident is mistaken for an ordinary bug

Data loss, account takeover, supply-chain compromise, privacy exposure, unauthorized deployment, or malicious behavior may first appear as a routine defect.

HARM: normal debugging continues while the incident spreads.

OVERLAP TO CHECK: OBS-001, UI-006.

### INCDET-002 — Ordinary bug is mistaken for an active attack

A platform change, cache fault, race condition, provider outage, or user error may be classified as compromise without enough evidence.

HARM: unnecessary shutdown, destructive recovery, credential rotation, or evidence contamination.

OVERLAP TO CHECK: AIH-003, INCSEV-001.

### INCDET-003 — Detection relies on the compromised component

The same app, provider, account, logger, repository, service worker, or device that may be compromised may also be the only source of health and incident evidence.

HARM: the attacker or failure can suppress the signal that would reveal it.

OVERLAP TO CHECK: AUD-001, REC-001.

### INCDET-004 — Low-volume or slow compromise stays below alert thresholds

Rare unauthorized reads, small data changes, gradual permission drift, intermittent redirects, or occasional malicious outputs may never trigger a threshold.

HARM: compromise persists for a long time while appearing normal.

OVERLAP TO CHECK: OBS-003, PRIV-002.

### INCDET-005 — Detection rules are stale after architecture changes

New providers, routes, schemas, accounts, flags, devices, and workflows may not be included in monitoring and incident checks.

HARM: newly introduced paths become invisible.

OVERLAP TO CHECK: MAINT-003, REMOTE-001.

### INCDET-006 — Monitoring outage is not itself detected

Logs, notifications, health checks, provider alerts, or audit collectors may stop without generating a separate failure signal.

HARM: absence of evidence is mistaken for absence of incidents.

OVERLAP TO CHECK: OBS-005, NOTIFY-001.

### INCDET-007 — Baseline behavior is undefined

The project may not know normal volumes, timing, providers, file changes, permission use, redirects, retries, or background activity.

HARM: abnormal behavior cannot be distinguished from ordinary variation.

OVERLAP TO CHECK: MEAS-001, OBS-006.

### INCSEV-001 — Severity is underestimated

A seemingly local failure may affect private data, authority, backups, recovery, deployment, or multiple providers.

HARM: containment and escalation are too slow or too narrow.

OVERLAP TO CHECK: AUTHZ-005, DIS-003.

### INCSEV-002 — Severity is overestimated

A contained, reversible, low-impact fault may trigger full shutdown, key rotation, account removal, or destructive restore.

HARM: response causes more damage than the incident.

OVERLAP TO CHECK: INCDET-002, DEST-003.

### INCSEV-003 — Scope is inferred from visible symptoms only

The affected file, account, provider, candidate, device, user, or time window may be broader than what first appears.

HARM: hidden affected objects remain active after partial containment.

OVERLAP TO CHECK: IDENT-001, AUTHZ-005.

### INCSEV-004 — Privacy, availability, integrity, and authority impacts are collapsed into one score

A single severity number may hide different types of harm requiring different actions.

HARM: the wrong containment and notification plan is selected.

OVERLAP TO CHECK: UI-003, MEAS-006.

### CONTAIN-001 — Containment action depends on compromised credentials

Revocation, deployment freeze, repository lock, provider disablement, or domain change may require the same account or device suspected of compromise.

HARM: containment cannot be trusted or performed.

OVERLAP TO CHECK: AUTH-002, REC-001.

### CONTAIN-002 — Containment is incomplete across connected systems

Disabling one account, token, provider, branch, deployment, or device may leave other sessions, caches, webhooks, automations, backups, and service accounts active.

HARM: compromise continues through forgotten paths.

OVERLAP TO CHECK: AUTHN-005, AUTHZ-005.

### CONTAIN-003 — Containment destroys volatile evidence

Restarting, clearing storage, deleting accounts, rotating keys, restoring backups, or removing files may erase logs, memory, sessions, timestamps, and attacker traces.

HARM: cause and scope can no longer be established.

OVERLAP TO CHECK: DEST-006, FORENSIC-001.

### CONTAIN-004 — Isolation also blocks recovery and communication

Disconnecting devices, disabling accounts, freezing repositories, or shutting providers may remove access to recovery instructions, backups, support, and trusted communication.

HARM: the project is contained but cannot recover safely.

OVERLAP TO CHECK: REC-002, AUTH-001.

### CONTAIN-005 — Containment expires or is reversed without verification

Temporary blocks, revoked tokens, disabled automations, or isolated environments may be restored because symptoms disappear rather than because the cause is removed.

HARM: the incident resumes.

OVERLAP TO CHECK: EMERG-002, REOPEN-001.

### CONTAIN-006 — Containment spreads damage through automation

A scripted response may bulk-revoke, delete, restore, rotate, or redeploy across many systems based on an incorrect incident classification.

HARM: response automation creates a larger outage or data loss event.

OVERLAP TO CHECK: INS-001, AUTO-004.

### FORENSIC-001 — Incident evidence is not captured before state changes

Logs, screenshots, memory, network details, process state, provider responses, timestamps, and affected identities may disappear during recovery.

HARM: the project cannot reconstruct what happened.

OVERLAP TO CHECK: CONTAIN-003, OBS-005.

### FORENSIC-002 — Evidence timestamps and clocks cannot be reconciled

Device, GitHub, provider, backend, browser, and user records may use different time zones, offsets, clock accuracy, and retention windows.

HARM: event ordering and causality are wrong.

OVERLAP TO CHECK: REL-007, SEM-003.

### FORENSIC-003 — Evidence collection changes or contaminates the evidence

Opening files, refreshing pages, logging in, exporting, copying, scanning, or running diagnostics may update timestamps, caches, sessions, and logs.

HARM: later analysis cannot distinguish incident activity from investigation activity.

OVERLAP TO CHECK: OBS-004, AUD-001.

### FORENSIC-004 — Chain of custody is absent

Collected logs, devices, screenshots, files, exports, and copies may not record who collected them, when, from where, with which method, and whether they changed.

HARM: evidence authenticity and interpretation remain uncertain.

OVERLAP TO CHECK: SEC-007, PROOFCHAIN-001.

### FORENSIC-005 — Sensitive evidence is overshared during response

Incident logs and exports may contain credentials, personal data, private source, user behavior, or exploit details.

HARM: investigation creates a second privacy or security incident.

OVERLAP TO CHECK: AUD-005, SOC-005.

### FORENSIC-006 — Absence of logs is treated as proof that no event occurred

Retention gaps, disabled monitoring, provider limitations, log tampering, or offline activity may leave no record.

HARM: unknown scope is falsely closed as unaffected.

OVERLAP TO CHECK: INCDET-006, PROOFCHAIN-009.

### COMMS-001 — Incident communication uses a compromised channel

Email, chat, repository, device, provider, or account used to coordinate response may be under attacker control.

HARM: false instructions, leaked recovery details, or blocked warnings.

OVERLAP TO CHECK: AUTH-005, SOC-002.

### COMMS-002 — No trusted out-of-band contact path exists

The project may have no separate way to reach the user, successor, provider, domain registrar, or support contact when primary channels fail.

HARM: containment and recovery stall.

OVERLAP TO CHECK: REC-002, DIS-002.

### COMMS-003 — Incident status is communicated without exact scope and uncertainty

Messages such as resolved, safe, contained, or no data lost may omit affected systems, evidence gaps, remaining watches, and confidence.

HARM: people resume normal operation too early.

OVERLAP TO CHECK: HUM-003, UI-003.

### COMMS-004 — Notification duties and affected parties are unknown

The project may not know whether users, providers, collaborators, legal authorities, or service operators must be told and within what time.

HARM: delayed disclosure, legal exposure, or affected people cannot protect themselves.

OVERLAP TO CHECK: VIAB-004, RET-004.

### COMMS-005 — Public disclosure creates new exploitability

Sharing incident details, source paths, affected versions, recovery steps, or weaknesses may help attackers before mitigation is complete.

HARM: a contained issue becomes broadly exploitable.

OVERLAP TO CHECK: SOC-005, FORENSIC-005.

### RECOVER-001 — Recovery restores availability without restoring trust

The app may run again while compromised credentials, dependencies, providers, caches, flags, accounts, or hidden persistence remain.

HARM: service resumes on an untrusted foundation.

OVERLAP TO CHECK: REC-003, PERSIST-001.

### RECOVER-002 — Recovery uses a backup created after compromise

A backup may already contain malicious code, poisoned memory, stolen sessions, altered configuration, or corrupted records.

HARM: restore faithfully reinstalls the incident.

OVERLAP TO CHECK: BKP-002, PERSIST-002.

### RECOVER-003 — Recovery point is selected by date instead of verified cleanliness

The newest available backup or release may be assumed safe without evidence of when compromise began.

HARM: hidden contamination survives.

OVERLAP TO CHECK: RECUI-004, FORENSIC-002.

### RECOVER-004 — Recovery validation checks only visible symptoms

The project may confirm page loading, login, storage, or deployment while ignoring permissions, hidden sessions, webhooks, providers, logs, and privacy exposure.

HARM: incomplete recovery receives PASS.

OVERLAP TO CHECK: TEST-003, INCSEV-003.

### RECOVER-005 — Rotated secrets remain embedded in old artifacts and logs

Old builds, backups, Notes, screenshots, caches, commits, provider logs, and devices may still contain compromised credentials.

HARM: “rotation” does not remove attacker access or disclosure risk.

OVERLAP TO CHECK: RET-002, AUTHN-005.

### RECOVER-006 — Recovery creates a second identity or split system

Emergency rebuilds, new repositories, replacement domains, new accounts, and restored devices may coexist with the old system without a clean authority transition.

HARM: users and tools act on different “current” systems.

OVERLAP TO CHECK: REPO-003, SYNC-001.

### PERSIST-001 — Malicious persistence survives in remote configuration or automation

Feature flags, webhooks, Actions, service accounts, Shortcuts, providers, scheduled tasks, and caches may reintroduce harmful behavior after visible files are cleaned.

HARM: compromise returns without a new intrusion.

OVERLAP TO CHECK: REMOTE-001, AUTH-003.

### PERSIST-002 — Poisoned memory or training records survive recovery

Bug Memory, prompts, examples, embeddings, model settings, summaries, or saved diagnoses may continue carrying attacker instructions or false beliefs.

HARM: Resident remains behaviorally compromised after code restore.

OVERLAP TO CHECK: MEM-001, SELF-005.

### PERSIST-003 — Compromised dependency or builder recontaminates clean source

A restored repository may be rebuilt by the same malicious action, package, image, registry, or toolchain.

HARM: clean source produces a compromised artifact again.

OVERLAP TO CHECK: SUPPLY-001, PROOFCHAIN-006.

### POST-001 — Root cause is replaced by the first plausible explanation

Time pressure or incomplete evidence may produce a convenient cause without testing alternatives.

HARM: the real cause and recurrence path remain.

OVERLAP TO CHECK: AIH-003, TEST-001.

### POST-002 — Corrective actions address symptoms only

The project may patch the visible bug without changing authority, monitoring, recovery, provider, or process weaknesses that enabled it.

HARM: a similar incident recurs through the same class of failure.

OVERLAP TO CHECK: MAINT-006, INCDET-005.

### POST-003 — Incident lessons never enter Packet 1.5 and future packets

Findings may remain in chat, support messages, provider tickets, or a local note.

HARM: the project forgets the incident after handoff.

OVERLAP TO CHECK: REG-008, MEM-001.

### POST-004 — Incident review is biased toward protecting prior claims or decisions

Reviewers may minimize impact, avoid reopening completed packets, or preserve a PASS status.

HARM: truth is subordinated to project reputation or sunk work.

OVERLAP TO CHECK: MEAS-005, AUD-003.

### REOPEN-001 — Incident is closed because symptoms stop

A quiet period, successful restart, restored page, or passing test may be treated as full resolution.

HARM: hidden persistence, affected records, and missing evidence remain unresolved.

OVERLAP TO CHECK: CONTAIN-005, RECOVER-004.

### REOPEN-002 — No objective reopening trigger exists

The project may not define which new evidence, repeated symptom, provider notice, stale credential, or related failure must reopen the incident.

HARM: recurrence is treated as unrelated or ignored.

OVERLAP TO CHECK: PROOF-012, REG-008.

### REOPEN-003 — Repeated incidents are counted separately without detecting a pattern

Similar failures across providers, versions, devices, or time may not be linked.

HARM: systemic weakness appears as unrelated noise.

OVERLAP TO CHECK: SEM-004, OBS-003.

## Pass 13 result

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
- Pass 13 provisional: 43
- Current preserved plus provisional: 569

NEXT DISCOVERY PASS:
Support operations, maintenance handoff, user assistance, documentation quality, issue intake, triage, escalation, service continuity, update communication, and end-user misuse.

END PACKET 01.5 — DISCOVERY PASS 13
