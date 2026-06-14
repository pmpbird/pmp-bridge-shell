# Packet 01.5 — Discovery Pass 19

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for legal and licensing boundaries, ownership, attribution, privacy rights, consent, jurisdiction, accessibility duties, export restrictions, records obligations, and third-party terms.

## Provisional records

### LIC-001 — Dependency license is unknown or misidentified

Source, packages, fonts, models, images, datasets, examples, and generated code may enter the project without a verified license identity.

HARM: use, redistribution, modification, or deployment may exceed granted rights.

OVERLAP TO CHECK: LEGAL-001, DEP-011.

### LIC-002 — License obligations are lost during bundling

Notices, source offers, attribution, license text, modification marks, and redistribution conditions may be omitted from the final artifact.

HARM: compliant source becomes a noncompliant release.

OVERLAP TO CHECK: BUILDINT-003, ATTR-001.

### LIC-003 — Incompatible licenses are combined

Individually permitted components may impose conflicting redistribution, disclosure, branding, or use conditions when combined.

HARM: no lawful distribution path exists for the assembled artifact.

OVERLAP TO CHECK: DEP-001, ARCH-001.

### LIC-004 — Model or dataset terms differ from code licenses

Weights, hosted APIs, embeddings, datasets, generated output, and source code may each carry separate use and redistribution restrictions.

HARM: a code-compliant project still violates model or data terms.

OVERLAP TO CHECK: TERMS-001, LOCK-002.

### LIC-005 — License version or grant changes over time

A provider, package, model, font, or dataset may later use a different license or terms version.

HARM: updates silently change legal obligations.

OVERLAP TO CHECK: PROV-001, CHANGE-001.

### LIC-006 — “Free” is mistaken for unrestricted use

No-cost services and assets may still restrict commercial use, redistribution, automation, volume, geography, or prohibited activities.

HARM: the project relies on rights it never received.

OVERLAP TO CHECK: ECO-001, TERMS-001.

### LIC-007 — License proof is not preserved with the exact version

A current webpage or package metadata may be used to justify an older or different artifact.

HARM: later audit cannot prove which terms governed the shipped version.

OVERLAP TO CHECK: PROOFCHAIN-001, VER-008.

### LIC-008 — Generated output contains protected source material

AI-generated code, text, imagery, or examples may reproduce third-party material without reliable provenance.

HARM: the project distributes content it does not own or have permission to use.

OVERLAP TO CHECK: AIH-001, LEGAL-001.

### OWN-001 — Ownership of user-created and AI-assisted work is unclear

Prompts, designs, code, records, outputs, and refinements may involve user, model provider, contractor, collaborator, and source-material interests.

HARM: control and redistribution rights are disputed later.

OVERLAP TO CHECK: LIC-008, AUTH-007.

### OWN-002 — Repository control is mistaken for intellectual-property ownership

Possessing the account, branch, file, or deployment does not establish ownership of every included component.

HARM: technical control is treated as legal title.

OVERLAP TO CHECK: REPO-001, LIC-001.

### OWN-003 — Contributor rights are not documented

Code, documentation, data, design, testing, or support from another person may lack a clear grant or assignment.

HARM: future modification, publication, or transfer becomes contested.

OVERLAP TO CHECK: AUTH-007, HANDOFF-001.

### OWN-004 — Project transfer does not include all necessary rights

A successor may receive files and credentials but not licenses, contributor grants, domain rights, provider contracts, or data permissions.

HARM: operational succession occurs without lawful authority to continue.

OVERLAP TO CHECK: HANDOFF-001, LOCK-004.

### OWN-005 — Brand, name, icon, or domain conflicts with another party

Project naming and visual identity may overlap trademarks, product names, domains, or protected branding.

HARM: publication or growth requires disruptive renaming or creates legal exposure.

OVERLAP TO CHECK: CORE-002, REPO-003.

### ATTR-001 — Required attribution is missing or inaccessible

Notices may be absent from the app, repository, documentation, archive, or distribution package.

HARM: use violates attribution conditions even when the underlying asset is permitted.

OVERLAP TO CHECK: LIC-002, DOC-001.

### ATTR-002 — Attribution falsely implies endorsement

Displaying a provider, contributor, organization, or project name may suggest sponsorship or approval not actually granted.

HARM: users misunderstand authority and affiliation.

OVERLAP TO CHECK: SOC-004, AUTH-006.

### ATTR-003 — Attribution source is lost after transformation

Compression, bundling, generation, migration, or copying may detach an asset from its creator, license, and modification history.

HARM: later compliance and provenance cannot be reconstructed.

OVERLAP TO CHECK: SEM-004, PORT-007.

### CONSENT-001 — Consent is bundled across unrelated purposes

Storage, provider processing, debugging, analytics, model improvement, support, and public sharing may be covered by one broad approval.

HARM: the user cannot meaningfully choose among distinct data uses.

OVERLAP TO CHECK: MIN-003, HUM-002.

### CONSENT-002 — Consent language does not match actual data flow

The interface may describe local or limited use while data also reaches providers, logs, backups, support, or embeddings.

HARM: processing exceeds the user’s informed expectation.

OVERLAP TO CHECK: PRIV-003, EMBED-006.

### CONSENT-003 — Consent is not versioned with changed behavior

A prior approval may remain active after new providers, purposes, data categories, retention, or sharing paths are added.

HARM: old consent is reused for materially different processing.

OVERLAP TO CHECK: CHANGE-008, EXP-001.

### CONSENT-004 — Withdrawal does not stop all processing

Revoking approval may not halt queued work, backups, provider retention, model training, analytics, or shared copies.

HARM: the project claims withdrawal while data use continues.

OVERLAP TO CHECK: AUTHN-005, DEL-002.

### CONSENT-005 — Consent is inferred from use, silence, or dismissed notice

Opening the app, continuing a workflow, or closing a banner may be treated as affirmative agreement.

HARM: approval exists in records without clear user intent.

OVERLAP TO CHECK: UPDATE-004, HUM-002.

### CONSENT-006 — Consent capacity and authority are not checked

A person may approve processing for data, accounts, devices, or other people they do not control or may not be authorized to consent for.

HARM: the project relies on invalid permission.

OVERLAP TO CHECK: AUTH-006, IDENT-003.

### PRIVRIGHT-001 — Access request cannot produce a complete record set

Data may be spread across local storage, providers, logs, backups, GitHub, Notes, embeddings, support, and archives.

HARM: the project cannot show what information it holds.

OVERLAP TO CHECK: STATE-002, API-003.

### PRIVRIGHT-002 — Correction request does not propagate to derived records

Fixing source data may not update summaries, embeddings, Bug Memory, scores, logs, backups, and external providers.

HARM: corrected information continues producing old conclusions.

OVERLAP TO CHECK: KB-003, SEM-005.

### PRIVRIGHT-003 — Deletion request conflicts with evidence and retention duties

Removing personal data may damage receipts, incident evidence, security logs, ownership records, or required history.

HARM: privacy and accountability obligations cannot both be met by simple deletion.

OVERLAP TO CHECK: RET-001, DEL-003.

### PRIVRIGHT-004 — Data portability export is incomplete or unusable

An export may omit context, relationships, machine-readable structure, attachments, or provider-held data.

HARM: nominal portability does not let the user move or understand their information.

OVERLAP TO CHECK: LOCK-005, PORT-003.

### PRIVRIGHT-005 — Automated decisions cannot be explained or challenged

Risk scores, routing, refusals, prioritization, and classifications may depend on opaque models, prompts, or hidden state.

HARM: affected users cannot understand or contest important outcomes.

OVERLAP TO CHECK: EVAL-003, AIH-004.

### JUR-001 — Applicable jurisdiction is unclear

User location, operator location, provider region, data storage, domain, and affected parties may point to different legal regimes.

HARM: the project applies the wrong duties or restrictions.

OVERLAP TO CHECK: DIS-004, VIAB-004.

### JUR-002 — Cross-border data transfer is not mapped

Providers, backups, support, embeddings, analytics, and repositories may process data in other regions.

HARM: data moves outside expected legal and privacy boundaries.

OVERLAP TO CHECK: PROV-002, EMBED-006.

### JUR-003 — Travel or relocation changes permitted operation

A user or device may enter a region with different privacy, encryption, content, AI, export, or access rules.

HARM: ordinary operation becomes restricted or exposes the user to unexpected obligations.

OVERLAP TO CHECK: DIS-004, EXPORT-001.

### JUR-004 — Choice-of-law and dispute terms conflict across providers

Hosting, AI, repository, domain, payment, and device providers may each impose different governing law and venue.

HARM: one project inherits incompatible dispute and compliance frameworks.

OVERLAP TO CHECK: TERMS-001, LOCK-003.

### ACCESSLAW-001 — Accessibility obligations are treated as optional quality work

Required access for visual, motor, hearing, cognitive, or assistive-technology users may be postponed as enhancement work.

HARM: users are excluded and the project may fail applicable duties.

OVERLAP TO CHECK: ACC-001, QUEUE-001.

### ACCESSLAW-002 — Accessibility claim exceeds tested coverage

A label such as accessible or compliant may be based on limited automated checks or one device.

HARM: users rely on a claim not supported by real behavior.

OVERLAP TO CHECK: PERF-007, PROOFCHAIN-005.

### ACCESSLAW-003 — Provider or third-party content breaks accessibility

Embedded widgets, authentication, payment, support, documents, and AI output may be outside direct control but remain part of the user journey.

HARM: the full service is inaccessible despite an accessible core screen.

OVERLAP TO CHECK: WEB-001, COV-003.

### ACCESSLAW-004 — Emergency and recovery paths are less accessible than normal use

Critical warnings, backup restore, account recovery, consent, and incident communication may rely on time-limited, visual, or complex interfaces.

HARM: users lose access precisely when risk is highest.

OVERLAP TO CHECK: ACC-003, RECUI-002.

### EXPORT-001 — Encryption, AI, code, or technical data crosses restricted boundaries

Sharing, hosting, travel, provider use, publication, or support may move controlled technology or information across jurisdictions.

HARM: ordinary project operations may trigger export or sanctions restrictions.

OVERLAP TO CHECK: JUR-003, SOC-005.

### EXPORT-002 — Restricted person or region screening is absent

Automated access, collaboration, distribution, provider accounts, or support may reach parties subject to legal restrictions.

HARM: the project provides services or technology where it is not permitted.

OVERLAP TO CHECK: AUTHN-003, JUR-001.

### EXPORT-003 — Geoblocking or provider restrictions are mistaken for technical failure

Regional denials, sanctions controls, export restrictions, and legal removals may appear as ordinary outages or authentication errors.

HARM: the system retries, bypasses, or misdiagnoses a legal restriction.

OVERLAP TO CHECK: INCDET-001, API-005.

### RECORDLAW-001 — Required records are not retained in an admissible form

Approvals, licenses, consent, incidents, changes, notices, and receipts may lack durable identity, timestamps, integrity, or retrieval.

HARM: the project cannot demonstrate what occurred or under which authority.

OVERLAP TO CHECK: AUD-004, PROOFCHAIN-001.

### RECORDLAW-002 — Records are retained longer than justified

Logs, support data, consent history, screenshots, backups, and user content may remain indefinitely because deletion is difficult.

HARM: privacy exposure and legal burden grow without operational value.

OVERLAP TO CHECK: RET-004, MIN-002.

### TERMS-001 — Provider terms change without operational review

AI, hosting, repository, domain, device, analytics, and support providers may change acceptable use, data use, limits, ownership, or termination terms.

HARM: continued operation silently violates or accepts new conditions.

OVERLAP TO CHECK: PROV-001, LIC-005.

### TERMS-002 — Provider suspension or termination rights are not included in recovery planning

A service may remove access, data, accounts, domains, models, repositories, or support with limited notice or appeal.

HARM: project continuity depends on rights the provider can withdraw.

OVERLAP TO CHECK: PROV-002, LOCK-004.

## Pass 19 result

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
- Pass 16 provisional: 42
- Pass 17 provisional: 42
- Pass 18 provisional: 42
- Pass 19 provisional: 42
- Current preserved plus provisional: 821

NEXT DISCOVERY PASS:
Human cognition, fatigue, interruption, misunderstanding, overtrust, undertrust, training failure, decision framing, cognitive accessibility, and operator error under stress.

END PACKET 01.5 — DISCOVERY PASS 19
