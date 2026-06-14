# Packet 01.5 — Discovery Pass 20

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for human cognition, fatigue, interruption, misunderstanding, overtrust, undertrust, training failure, decision framing, cognitive accessibility, and operator error under stress.

## Provisional records

### COG-001 — Working memory is overloaded

The operator may need to hold packet state, version identity, warnings, pending actions, dependencies, and exceptions in mind at once.

HARM: quiet constraints are dropped while the visible task still appears correct.

OVERLAP TO CHECK: HUM-002, CTX-003.

### COG-002 — First explanation anchors later reasoning

An early diagnosis, label, severity, or proposed fix may shape all later review even after contradictory evidence appears.

HARM: the project keeps refining the first story instead of reconsidering it.

OVERLAP TO CHECK: POST-001, AIH-003.

### COG-003 — Confirmation bias filters evidence

Reviewers may notice facts supporting the current design, PASS, owner, or preferred provider and discount disconfirming evidence.

HARM: false confidence survives repeated review.

OVERLAP TO CHECK: POST-004, MEAS-005.

### COG-004 — Available examples are mistaken for representative cases

Recent, vivid, easy-to-recall, or dramatic failures may dominate risk judgments.

HARM: common quiet failures and rare unseen failures are misprioritized.

OVERLAP TO CHECK: TRIAGE-001, OBS-003.

### COG-005 — Sunk-cost pressure preserves unsafe work

Time spent on code, packets, testing, migration, or provider setup may make rollback, replacement, or abandonment feel unacceptable.

HARM: prior investment outweighs current evidence.

OVERLAP TO CHECK: RBACK-001, POST-004.

### COG-006 — Too many choices prevent a safe decision

Large option sets for restore points, providers, routes, flags, fixes, or packet owners may overwhelm the operator.

HARM: action is delayed, guessed, or delegated without understanding.

OVERLAP TO CHECK: RECUI-004, MAINT-007.

### COG-007 — Abstraction level does not match the operator

Instructions may be too technical, too simplified, too compressed, or too detached from the actual screen and object.

HARM: the operator follows words without understanding the underlying effect.

OVERLAP TO CHECK: DOC-006, HUM-002.

### COG-008 — Local task focus hides system-wide consequences

The operator may optimize the current file, bug, screen, or packet without considering authority, data, recovery, provider, and downstream effects.

HARM: a correct local change creates a global failure.

OVERLAP TO CHECK: TRIAGE-004, CHANGE-005.

### FAT-001 — Fatigue increases approval and execution errors

Long work, late hours, stress, illness, or repetitive review may reduce attention and judgment.

HARM: wrong objects are approved, skipped, deleted, or promoted.

OVERLAP TO CHECK: INS-001, HUM-001.

### FAT-002 — Repetitive review becomes rubber-stamping

Repeated warnings, receipts, diffs, tests, and similar records may receive less scrutiny over time.

HARM: a dangerous change passes because it resembles routine work.

OVERLAP TO CHECK: INS-003, NOTIFY-004.

### FAT-003 — Long sessions reduce decision consistency

The same evidence may receive different treatment early and late in a work session.

HARM: thresholds and authority drift without a formal policy change.

OVERLAP TO CHECK: MEAS-006, AIH-004.

### FAT-004 — Human condition is not reflected in task risk

Sleep loss, pain, medication, distraction, emotional distress, or cognitive impairment may not change the permitted action set.

HARM: high-impact work proceeds when the operator is not fit to perform it safely.

OVERLAP TO CHECK: AUTH-001, STRESS-002.

### FAT-005 — Constant task switching destroys context

Moving among chats, Notes, GitHub, files, providers, code, and packets imposes repeated reconstruction cost.

HARM: assumptions and object identity bleed between tasks.

OVERLAP TO CHECK: INTERRUPT-004, TOOL-001.

### FAT-006 — Fatigue is hidden by fluent behavior

An operator or AI may continue producing polished, confident work after real comprehension and checking have declined.

HARM: visible fluency masks unsafe performance.

OVERLAP TO CHECK: AIH-004, HUM-003.

### INTERRUPT-001 — Interruption removes the active mental model

A call, notification, app switch, sleep, crash, or conversation change may break understanding of the current object and step.

HARM: resumed work starts from an inaccurate reconstruction.

OVERLAP TO CHECK: FLOW-001, FAT-005.

### INTERRUPT-002 — Resume point is mentally mistaken

The interface may restore one step while the operator believes a different action already completed or still remains.

HARM: work is duplicated, skipped, or executed out of order.

OVERLAP TO CHECK: FLOW-002, UI-015.

### INTERRUPT-003 — Notifications interrupt critical confirmation

Alerts, messages, calls, banners, and system prompts may arrive while the operator is checking a destructive or authority-bearing action.

HARM: the action is confirmed without full attention or the wrong control is touched.

OVERLAP TO CHECK: UI-010, NOTIFY-004.

### INTERRUPT-004 — Parallel conversations contaminate one another

Several chats, issue threads, Notes, branches, or support conversations may discuss similar objects with different state.

HARM: instructions, code, evidence, or decisions are applied to the wrong project generation.

OVERLAP TO CHECK: REL-001, SUP-003.

### INTERRUPT-005 — Delayed continuation loses unstated assumptions

A task resumed days or weeks later may retain files and text but not the operator’s unstated reasoning, uncertainty, or intended next check.

HARM: continuation appears seamless while important context is gone.

OVERLAP TO CHECK: SUCC-001, CTX-003.

### TRUST-001 — Polished output receives excessive trust

Clear language, attractive formatting, citations, code quality, or confident tone may be mistaken for correctness.

HARM: presentation substitutes for verification.

OVERLAP TO CHECK: AIH-004, SOC-004.

### TRUST-002 — Low trust causes users to bypass the system

After false alarms, confusing refusals, or visible mistakes, users may ignore warnings and perform direct manual actions.

HARM: safeguards lose practical authority even when they are correct.

OVERLAP TO CHECK: MISUSE-002, NOTIFY-004.

### TRUST-003 — Past success is generalized beyond the tested domain

A model, workflow, provider, or operator that performed well on one class of task may be trusted on unrelated high-risk tasks.

HARM: competence is assumed where it was never proven.

OVERLAP TO CHECK: MISUSE-001, PERF-007.

### TRUST-004 — Trust is not scoped by action type

Read-only explanation, code generation, deployment, deletion, credential handling, legal interpretation, and recovery may receive the same trust level.

HARM: low-risk reliability grants high-risk authority.

OVERLAP TO CHECK: AUTH-008, MISUSE-001.

### TRUST-005 — Human review defers to apparent machine consensus

Several models, agents, tools, or automated checks may agree because they share assumptions or sources.

HARM: the human stops independent reasoning precisely when correlation is highest.

OVERLAP TO CHECK: AGENT-001, EVAL-002.

### TRUST-006 — One automation surprise destroys trust in unrelated protections

A single unexpected action may cause the operator to disable broader automation, warnings, or safeguards.

HARM: a local trust failure removes valid protections system-wide.

OVERLAP TO CHECK: FLAG-007, MISUSE-002.

### TRUST-007 — Authority cues are stronger than evidence cues

Official-looking labels, repository roles, provider branding, model names, badges, signatures, or “verified” language may dominate actual proof.

HARM: status symbols are trusted despite weak evidence.

OVERLAP TO CHECK: ATTR-002, HUM-003.

### TRAIN-001 — Reading instructions is mistaken for comprehension

Completion may be recorded when a user opened, scrolled, acknowledged, or received documentation.

HARM: formal training status exists without usable understanding.

OVERLAP TO CHECK: UPDATE-004, HUM-002.

### TRAIN-002 — Training covers only the happy path

Users may learn normal creation, save, and deployment but not conflict, denial, corruption, rollback, incident, or recovery paths.

HARM: competence disappears when conditions become dangerous.

OVERLAP TO CHECK: DOC-003, TEST-004.

### TRAIN-003 — Training becomes stale after system changes

Screens, providers, permissions, policies, schemas, and recovery procedures may change without retraining.

HARM: remembered instructions direct users into obsolete behavior.

OVERLAP TO CHECK: DOC-004, CHANGE-008.

### TRAIN-004 — Training is not practiced under realistic conditions

A user may never rehearse recovery, handoff, provider outage, device loss, corrupted data, or compromised credentials.

HARM: knowledge fails under time pressure and uncertainty.

OVERLAP TO CHECK: REC-003, HANDOFF-005.

### TRAIN-005 — Skill does not transfer across environments

Competence on desktop, test data, one provider, or one device may not carry to iPhone, production, offline, or restored state.

HARM: training appears complete while the target environment remains unfamiliar.

OVERLAP TO CHECK: ENV-004, PERF-007.

### TRAIN-006 — Operator does not know when to stop and escalate

Training may teach procedures without defining uncertainty, danger, authority limits, and escalation triggers.

HARM: the user improvises past the safe boundary.

OVERLAP TO CHECK: ESC-001, SUP-004.

### FRAME-001 — Default framing hides alternative interpretations

Presenting a problem as bug, security issue, provider outage, user error, or migration failure may narrow the solution space before evidence is gathered.

HARM: the selected frame determines the conclusion.

OVERLAP TO CHECK: INCDET-001, POST-001.

### FRAME-002 — Loss framing pushes riskier choices

Warnings about losing work, access, time, money, or progress may cause users to accept unsafe restore, migration, payment, or credential actions.

HARM: fear of loss overrides protection rules.

OVERLAP TO CHECK: SOC-003, COG-005.

### FRAME-003 — Metric framing changes perceived success

The same outcome may appear good or bad depending on whether it is shown as pass rate, failure count, coverage, users retained, or incidents avoided.

HARM: presentation selects the preferred decision.

OVERLAP TO CHECK: MEAS-001, MEAS-004.

### FRAME-004 — Option order and defaults steer the decision

First-listed, highlighted, recommended, or preselected actions may be chosen without independent comparison.

HARM: interface framing becomes hidden governance.

OVERLAP TO CHECK: UI-009, COG-006.

### FRAME-005 — Language complexity blocks cognitive access

Dense terminology, long sentences, nested conditions, unexplained abbreviations, and large record sets may prevent real understanding.

HARM: users appear informed while essential meaning remains inaccessible.

OVERLAP TO CHECK: ACCESSLAW-001, DOC-005.

### STRESS-001 — Urgency narrows attention to visible symptoms

During outage, data loss, account compromise, or deadline pressure, the operator may ignore evidence preservation, scope, privacy, and downstream effects.

HARM: immediate repair worsens the larger incident.

OVERLAP TO CHECK: CONTAIN-003, SOC-003.

### STRESS-002 — Emergency conditions increase destructive-action error

Stress may cause rapid deletion, reset, revocation, restore, rollback, or provider changes without full review.

HARM: response actions create irreversible collateral damage.

OVERLAP TO CHECK: DEST-001, CONTAIN-006.

### STRESS-003 — Stress impairs identity and authority verification

Under pressure, the operator may trust familiar names, accept support messages, reuse credentials, or skip exact target checks.

HARM: social engineering and wrong-object actions become more likely.

OVERLAP TO CHECK: SOC-001, UI-002.

### STRESS-004 — Shame or fear suppresses timely reporting

Users may hide mistakes, credential exposure, accidental deletion, unsafe bypasses, or misunderstood instructions.

HARM: incidents remain active longer and evidence disappears.

OVERLAP TO CHECK: INCDET-004, INTAKE-001.

### STRESS-005 — No safe plan exists when the operator is impaired or unavailable

The project may assume the sole operator can always reason, authenticate, communicate, and recover correctly.

HARM: illness, panic, injury, or crisis removes both operation and governance.

OVERLAP TO CHECK: AUTH-001, CONT-002.

## Pass 20 result

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
- Pass 20 provisional: 42
- Current preserved plus provisional: 863

NEXT DISCOVERY PASS:
Physical-world sensing, device sensors, environmental input, permissions, calibration, false readings, spoofing, unavailable sensors, and mismatch between digital state and reality.

END PACKET 01.5 — DISCOVERY PASS 20
