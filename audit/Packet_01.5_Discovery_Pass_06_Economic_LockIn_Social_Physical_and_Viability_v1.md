# Packet 01.5 — Discovery Pass 06

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for economic sustainability, failure of free operation, vendor lock-in, social engineering, physical device loss, environmental disaster, maintenance burden, obsolete skills and tools, and long-term project viability risks.

## Provisional records

### ECO-001 — A free dependency becomes paid or restricted

A hosting service, AI provider, domain, CDN, repository feature, backend, storage service, or automation may remove its free tier or reduce it below the project’s needs.

HARM: essential operation stops or the project is forced into an unplanned paid dependency.

OVERLAP TO CHECK: OPS-004, PROV-002.

### ECO-002 — Usage cost grows unpredictably

AI calls, bandwidth, storage, logs, backups, builds, domains, or external actions may scale with usage in ways that are difficult to forecast.

HARM: cost spikes, forced shutdown, or pressure to weaken testing and proof.

OVERLAP TO CHECK: PERF-004, PROV-002.

### ECO-003 — Hidden ownership costs are omitted

A “free” system may still require a compatible iPhone, replacement hardware, domain renewal, backup storage, electricity, internet, recovery time, and skilled maintenance.

HARM: the project becomes unsustainable despite having no direct software fee.

OVERLAP TO CHECK: FREE-OPERATION LAW, MAINT-001.

### ECO-004 — Safety and proof are reduced to save money or time

Long tests, independent review, backups, multiple providers, and recovery rehearsals may be skipped because they consume resources.

HARM: budget pressure silently weakens the project’s protection standard.

OVERLAP TO CHECK: MEAS-004, PROOF-006.

### ECO-005 — No controlled degraded mode exists when funds disappear

The project may depend on paid or quota-limited services without defining which features stop, which remain safe, and how the user is warned.

HARM: abrupt failure or silent fallback to a weaker unsafe workflow.

OVERLAP TO CHECK: QUAL-001, PROV-002.

### LOCK-001 — Proprietary data format prevents complete export

A provider may store prompts, logs, notes, automation state, model settings, or project metadata in formats that cannot be fully exported.

HARM: history, evidence, or operating capability is trapped.

OVERLAP TO CHECK: DATA-002, OPS-004.

### LOCK-002 — Provider-specific behavior becomes part of Resident identity

Prompts, tool calls, response parsing, safety assumptions, or workflow logic may depend on one provider’s undocumented behavior.

HARM: replacing the provider changes Resident’s meaning or breaks the workflow.

OVERLAP TO CHECK: AI-007, PROV-001.

### LOCK-003 — Switching cost becomes practically impossible

Even when export exists, changing providers may require rewriting adapters, tests, documentation, permissions, data formats, and recovery procedures.

HARM: the project remains captive because migration is too risky or expensive.

OVERLAP TO CHECK: BUILD-008, OPS-004.

### LOCK-004 — Provider controls project identity or authentication

A provider account, Apple ID, domain registrar, GitHub organization, or external identity service may become the only way to prove ownership or access critical records.

HARM: losing one account can erase practical control of the project.

OVERLAP TO CHECK: AUTH-002, REPO-001.

### LOCK-005 — Exported data lacks enough context to remain usable

A provider may export raw records without relationships, timestamps, permissions, schemas, attachments, or executable automation.

HARM: the data technically leaves the provider but cannot restore the system.

OVERLAP TO CHECK: BKP-001, DATA-003.

### SOC-001 — Phishing targets project credentials or approval

Messages, links, QR codes, login pages, fake alerts, or copied support requests may imitate GitHub, Apple, hosting, AI, or domain providers.

HARM: credentials, recovery codes, or approvals are surrendered to an attacker.

OVERLAP TO CHECK: SEC-010, AUTH-006.

### SOC-002 — Fake support or recovery agent gains control

A person claiming to be provider support, a collaborator, or a recovery specialist may request codes, exports, screen sharing, or configuration changes.

HARM: trusted access is transferred outside the documented authority process.

OVERLAP TO CHECK: AUTH-002, SOC-001.

### SOC-003 — Urgency and fear bypass careful review

Warnings about imminent loss, suspension, security breach, data deletion, or deadline may pressure the user to approve unsafe steps.

HARM: emergency language becomes a social bypass around project safeguards.

OVERLAP TO CHECK: EMERG-001, HUM-001.

### SOC-004 — Familiar branding creates false trust

A known provider name, polished UI, AI confidence, official-looking icon, or cloned repository may be trusted without independent identity verification.

HARM: malicious or incorrect actions appear legitimate.

OVERLAP TO CHECK: SEC-010, HUM-003.

### SOC-005 — Sensitive project information is overshared during help-seeking

Source, screenshots, logs, prompts, credentials, private bugs, or recovery details may be shared publicly or with an untrusted helper.

HARM: privacy loss, exploit disclosure, or account compromise.

OVERLAP TO CHECK: SEC-006, AUD-005.

### PHY-001 — Primary device is lost or stolen

The iPhone may contain local storage, Apple Notes, Shortcuts, sessions, credentials, approvals, and private project records.

HARM: loss of availability and possible unauthorized access.

OVERLAP TO CHECK: SEC-008, SUCC-003.

### PHY-002 — Device is damaged or suddenly unusable

Water, impact, battery failure, hardware defect, update failure, or repair may make the primary device unavailable without warning.

HARM: current work, keys, Notes, and recovery paths may be inaccessible.

OVERLAP TO CHECK: BKP-003, REC-002.

### PHY-003 — Passcode, biometrics, or unlocked-session security fails

Shoulder surfing, coercion, biometric misuse, weak passcodes, or an unattended unlocked phone may expose project authority.

HARM: unauthorized approvals, exports, deletions, or credential changes.

OVERLAP TO CHECK: SEC-008, AUTH-006.

### PHY-004 — Device replacement cannot recreate the working environment

A new phone may restore some data but not browser state, Home Screen installation, local storage, Shortcut permissions, Notes links, provider sessions, or hidden settings.

HARM: the project cannot resume even though backups exist.

OVERLAP TO CHECK: REC-003, BKP-001.

### PHY-005 — No tested spare-device or alternate-access path

The project may depend entirely on one phone with no verified secondary device or safe desktop path.

HARM: a single hardware event stops all work and recovery.

OVERLAP TO CHECK: AUTH-001, REC-002.

### DIS-001 — Regional disaster affects primary and backup together

Fire, flood, earthquake, evacuation, civil disruption, or local infrastructure failure may affect the user, device, power, network, and local backups at the same time.

HARM: correlated loss defeats ordinary backup assumptions.

OVERLAP TO CHECK: BKP-001, SUCC-001.

### DIS-002 — Extended power or telecommunications outage

The user may lose charging, internet, cellular service, DNS access, or provider connectivity for an extended period.

HARM: no access to cloud records, support, authentication, or live proof.

OVERLAP TO CHECK: NET-001, PROV-002.

### DIS-003 — Provider and backup share one failure domain

Source, deployment, evidence, backups, and identity may all depend on the same cloud provider, account, region, or email address.

HARM: one provider incident removes both production and recovery.

OVERLAP TO CHECK: REPO-001, AUTH-001.

### DIS-004 — Emergency relocation changes legal, network, or device conditions

Travel or displacement may change region availability, data rules, phone number, payment methods, device access, or provider authentication.

HARM: recovery and ordinary operation fail under already stressful conditions.

OVERLAP TO CHECK: PROV-002, AUTH-002.

### MAINT-001 — Maintenance burden exceeds one person’s capacity

The combined work of updates, testing, evidence, backups, monitoring, Packet 1.5, providers, domains, and recovery may become too large to sustain.

HARM: safeguards are gradually skipped and stale risk accumulates.

OVERLAP TO CHECK: ECO-003, SUCC-001.

### MAINT-002 — Dependency and platform updates accumulate faster than review

Libraries, browsers, iOS, provider APIs, actions, and build tools may change continuously.

HARM: the project runs on increasingly stale and vulnerable components.

OVERLAP TO CHECK: BUILD-008, PLAT-003.

### MAINT-003 — Documentation drifts from real operation

Instructions, diagrams, packet descriptions, recovery steps, and provider setup may remain unchanged while the implementation evolves.

HARM: future work and recovery follow obsolete procedures.

OVERLAP TO CHECK: GOV-009, REC-002.

### MAINT-004 — Skills required to operate the project disappear

Future maintainers may not understand old web APIs, Shortcuts, GitHub workflows, custom formats, security controls, or AI-provider behavior.

HARM: preserved artifacts become practically unmaintainable.

OVERLAP TO CHECK: SUCC-002, SUCC-004.

### MAINT-005 — Complexity growth makes every change high risk

Layers of wrappers, manifests, compatibility paths, evidence rules, providers, and legacy records may accumulate without simplification.

HARM: small changes require excessive work and are more likely to break hidden dependencies.

OVERLAP TO CHECK: PERF-005, REG-006.

### MAINT-006 — Temporary workaround becomes permanent architecture

A quick fix, fallback, manual step, duplicated record, or compatibility shim may remain because removing it feels risky.

HARM: technical debt becomes part of the project’s identity and increases future failure paths.

OVERLAP TO CHECK: QUAL-001, GOV-007.

### MAINT-007 — No maintenance priority or risk budget

The project may treat all warnings, upgrades, tests, and cleanup as equally urgent.

HARM: critical work is delayed by low-value activity or maintenance never finishes.

OVERLAP TO CHECK: HUM-001, OPS-003.

### VIAB-001 — Project scope expands beyond the original category

New features, providers, devices, users, and claims may accumulate until the project no longer has a testable narrow purpose.

HARM: proof becomes impossible and the system becomes unfocused.

OVERLAP TO CHECK: GOV-007, PROOF-015.

### VIAB-002 — No criteria exist for pausing, simplifying, or retiring the project

The project may continue consuming effort even when dependencies fail, goals change, or maintenance cost exceeds value.

HARM: unsafe or obsolete operation continues because stopping was never designed.

OVERLAP TO CHECK: SUCC-005, ECO-003.

### VIAB-003 — Data and evidence volume outgrow the architecture

Years of messages, bugs, receipts, screenshots, logs, versions, and Packet 1.5 records may exceed practical storage, search, review, and transfer limits.

HARM: the system cannot reliably load its own history or obligations.

OVERLAP TO CHECK: REG-001, PERF-002.

### VIAB-004 — External law, policy, or platform rules change

Privacy law, consumer rules, AI regulation, app-platform rules, export controls, accessibility requirements, or provider terms may change.

HARM: a previously acceptable workflow becomes restricted or unlawful.

OVERLAP TO CHECK: LEGAL-001, PROV-001.

### VIAB-005 — The project remains dependent on unavailable expert help

Critical security, legal, accessibility, infrastructure, or recovery decisions may require expertise the user cannot obtain or afford.

HARM: unresolved high-risk areas remain permanently open or are guessed at.

OVERLAP TO CHECK: MAINT-001, ECO-003.

## Pass 06 result

New provisional records: 35
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
- Current preserved plus provisional: 270

NEXT DISCOVERY PASS:
Model-specific reasoning failure, adversarial examples, hallucinated evidence, hidden-state dependence, context-window failure, multi-agent disagreement, automation runaway, and unsafe self-improvement.

END PACKET 01.5 — DISCOVERY PASS 06
