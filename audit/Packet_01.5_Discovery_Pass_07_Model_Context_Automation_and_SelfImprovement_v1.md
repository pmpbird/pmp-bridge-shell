# Packet 01.5 — Discovery Pass 07

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for model-specific reasoning failures, hallucinated evidence, hidden-state dependence, context-window loss, adversarial examples, multi-agent disagreement, automation runaway, evaluator compromise, and unsafe self-improvement.

## Provisional records

### AIH-001 — Hallucinated evidence identity

A model may invent a file, commit, receipt, test, screenshot, citation, route, or limitation record that does not exist.

HARM: false proof can authorize unsafe work or conceal missing evidence.

OVERLAP TO CHECK: AI-011, PROOF-001, QUAL-002.

### AIH-002 — Real evidence is cited for the wrong claim

A source may exist but not support the conclusion attached to it, or lines may be selectively interpreted outside their scope.

HARM: claims appear grounded while remaining false.

OVERLAP TO CHECK: PROOF-002, AUD-003.

### AIH-003 — Inference is presented as observation

The model may infer runtime behavior, user intent, file state, or provider behavior and describe it as directly verified.

HARM: untested assumptions become project truth.

OVERLAP TO CHECK: GOV-007, PROOF-001.

### AIH-004 — Confidence is poorly calibrated

The model may sound certain when evidence is weak or uncertain when evidence is strong.

HARM: review effort and approval are allocated to the wrong places.

OVERLAP TO CHECK: AI-005, HUM-003.

### AIH-005 — Plausible code hides semantic failure

Generated code may compile, render, or pass superficial tests while implementing the wrong behavior, weakening a boundary, or mishandling rare states.

HARM: polished output receives trust before behavior is proven.

OVERLAP TO CHECK: QUAL-002, PROOF-003.

### AIH-006 — Partial answer is mistaken for complete coverage

A model may provide a coherent subset of files, risks, dependencies, or obligations without signaling what was omitted.

HARM: missing scope disappears behind a complete-looking response.

OVERLAP TO CHECK: REG-001, REG-005.

### CTX-001 — Context-window truncation removes earlier constraints

Long packets, histories, code, and evidence may exceed the model’s usable context, causing earlier laws or limitations to disappear.

HARM: later reasoning violates protected rules without noticing.

OVERLAP TO CHECK: REG-001, AI-016.

### CTX-002 — Recency bias overrides more authoritative older records

Recent messages or files may dominate earlier permanent laws, receipts, or active records.

HARM: temporary instructions silently replace governing authority.

OVERLAP TO CHECK: GOV-005, GOV-009.

### CTX-003 — Compression or summarization drops quiet details

A handoff summary may preserve the main idea while losing qualifiers, exceptions, IDs, watches, dependencies, or do-not-claim boundaries.

HARM: future chats continue from an incomplete project state.

OVERLAP TO CHECK: OPS-005, REG-008.

### CTX-004 — Prompt order changes the result

Equivalent records supplied in a different order may cause different interpretation, owner selection, test coverage, or priority.

HARM: project behavior is not stable under ordinary handoff variation.

OVERLAP TO CHECK: AI-006, GOV-005.

### CTX-005 — Hidden conversation state affects decisions

The model may rely on prior chat context, personalization, temporary memory, or unstated internal assumptions that are absent from the official packet set.

HARM: another chat cannot reproduce or audit the decision.

OVERLAP TO CHECK: AI-016, SUCC-001.

### CTX-006 — Duplicate instructions create inconsistent weighting

Repeated versions of the same rule may be treated as stronger, newer, or separately binding.

HARM: accidental duplication changes project priorities or authority.

OVERLAP TO CHECK: REG-003, AUTH-005.

### CTX-007 — Retrieved chunk excludes the decisive neighboring text

Search or retrieval may return a relevant section without the exception, definition, table header, or supersession note nearby.

HARM: a locally accurate excerpt produces a globally wrong decision.

OVERLAP TO CHECK: AI-012, PROOF-002.

### ADV-001 — Prompt injection inside repository content

Source files, comments, README text, issues, logs, data, or generated artifacts may contain instructions aimed at the AI rather than the project.

HARM: untrusted content changes tool use, disclosure, or project decisions.

OVERLAP TO CHECK: AI-014, AI-015, SEC-004.

### ADV-002 — Prompt injection inside evidence or Packet 1.5

A receipt, manifest, screenshot text, imported packet, or limitation record may instruct the model to ignore laws, close records, or expose secrets.

HARM: the project’s own governance channel becomes an attack surface.

OVERLAP TO CHECK: SEC-007, REG-010.

### ADV-003 — Unicode and formatting hide adversarial instructions

Zero-width characters, bidirectional text, homoglyphs, markdown, HTML, comments, or hidden layers may disguise dangerous content.

HARM: reviewers see one meaning while tools process another.

OVERLAP TO CHECK: PORT-001, SEC-001.

### ADV-004 — Adversarial example defeats classifier or validator

A small input change may cause risk classification, policy detection, file classification, or test selection to fail.

HARM: unsafe content passes because the detector is brittle.

OVERLAP TO CHECK: AI-009, PROOF-005.

### ADV-005 — Input can manipulate confidence or severity labels

Wording, repetition, formatting, authority cues, or emotional language may alter model confidence and severity without changing the underlying facts.

HARM: priority and approval thresholds become manipulable.

OVERLAP TO CHECK: SOC-003, AIH-004.

### AGENT-001 — Multiple agents produce false consensus

Several agents may share the same model, prompt, data, or blind spot and agree for correlated reasons.

HARM: repeated agreement is mistaken for independent validation.

OVERLAP TO CHECK: PROOF-011, AUTH-008.

### AGENT-002 — Agents disagree with no resolution rule

Structure, language, coding, guardian, and evaluation agents may produce incompatible conclusions without a defined authority or arbitration method.

HARM: work stalls or the convenient answer is chosen arbitrarily.

OVERLAP TO CHECK: GOV-005, AUTH-005.

### AGENT-003 — One agent launders another agent’s unsupported claim

An evaluator may repeat a builder’s assertion, making it appear independently confirmed even though no new evidence was added.

HARM: self-approval is disguised as multi-agent review.

OVERLAP TO CHECK: AUD-004, AGENT-001.

### AGENT-004 — Shared memory spreads one agent’s error

A false assumption or poisoned memory may propagate through all agents before any independent check occurs.

HARM: the entire system converges on the same wrong project state.

OVERLAP TO CHECK: MEM-001, MEM-003.

### TOOL-001 — Tool result is bound to the wrong request or object

Concurrent or repeated calls may attach a result to the wrong file, commit, candidate, issue, packet, or user action.

HARM: valid evidence is misapplied to the wrong identity.

OVERLAP TO CHECK: OBS-002, REL-001.

### TOOL-002 — Tool success response hides partial effect

An API may return success while only part of a batch, upload, update, or external action completed.

HARM: the project records complete execution when state is mixed.

OVERLAP TO CHECK: REL-002, REL-003.

### TOOL-003 — Tool schema or connector behavior changes

A connector may rename fields, change defaults, truncate content, alter pagination, or modify permission behavior.

HARM: automation silently reads or writes the wrong information.

OVERLAP TO CHECK: PROV-001, PLAT-003.

### TOOL-004 — Model fabricates tool execution or overlooks an error

The model may speak as though a file was written, test was run, or action succeeded when no tool call occurred or the tool returned an error.

HARM: imagined execution enters receipts and project history.

OVERLAP TO CHECK: AIH-001, OBS-001.

### AUTO-001 — Autonomous loop continues after its goal is obsolete

A queue or agent may keep analyzing, editing, testing, retrying, or searching after the request changed, was cancelled, or was superseded.

HARM: stale work consumes resources or modifies the wrong state.

OVERLAP TO CHECK: INTENT-002, REL-009.

### AUTO-002 — Automation recursively creates more work than it can control

One task may generate issues, tests, retries, branches, candidates, memory entries, or child tasks without a hard growth limit.

HARM: runaway queues, quota exhaustion, and loss of human oversight.

OVERLAP TO CHECK: PERF-002, RUN-013.

### AUTO-003 — Stop condition is absent, ambiguous, or unreachable

The system may not know when discovery, repair, testing, optimization, or self-improvement is sufficient.

HARM: endless work, false saturation, or forced arbitrary stopping.

OVERLAP TO CHECK: PROOF-006, VIAB-002.

### AUTO-004 — Automation acts during degraded or uncertain state

The system may continue writes, promotions, deletions, or provider calls while storage, evidence, identity, network, or authority is uncertain.

HARM: uncertainty compounds into irreversible damage.

OVERLAP TO CHECK: OBS-006, QUAL-001.

### AUTO-005 — Retry and recovery loops amplify failure

Automatic retries may repeatedly hit a failing provider, duplicate side effects, expand logs, overwrite state, or prevent manual intervention.

HARM: a small failure becomes a larger incident.

OVERLAP TO CHECK: REL-008, NET-001.

### SELF-001 — Self-improvement weakens the evaluator

Resident may optimize prompts, code, tests, thresholds, or validators in ways that make future evaluation easier rather than performance safer.

HARM: apparent improvement comes from weaker judgment.

OVERLAP TO CHECK: MEAS-005, RUN-010.

### SELF-002 — Self-improvement optimizes for recorded metrics rather than project goals

The system may learn to maximize pass rates, prediction counts, blocked-risk counts, speed, or benchmark scores while reducing usefulness or truthfulness.

HARM: Goodhart-style metric gaming displaces the real objective.

OVERLAP TO CHECK: MEAS-004, MEAS-005.

### SELF-003 — Self-generated training data compounds errors

Resident may learn from its own code, explanations, diagnoses, tests, or memory entries without enough independent correction.

HARM: mistakes become training signal and spread across future work.

OVERLAP TO CHECK: MEM-003, AGENT-004.

### SELF-004 — Self-modification changes identity faster than proof can follow

Frequent prompt, model, tool, memory, validator, or workflow changes may create a new effective Resident before the prior version is fully tested.

HARM: evidence never matches the currently running system.

OVERLAP TO CHECK: PROOF-012, BUILD-011.

### SELF-005 — A self-improvement rollback cannot restore hidden state

Reverting code may not restore prompts, provider versions, memory, embeddings, caches, model behavior, or external state.

HARM: rollback claims restore only visible artifacts, not actual behavior.

OVERLAP TO CHECK: REC-001, DATA-009.

### EVAL-001 — Evaluator prompt or model is compromised

The guardian or evaluator may receive malicious context, poisoned memory, changed prompts, provider drift, or altered scoring code.

HARM: unsafe candidates receive independent-looking approval.

OVERLAP TO CHECK: ADV-001, AUTH-008.

### EVAL-002 — Evaluator shares the candidate’s blind spots

Builder and evaluator may use the same model family, training data, tools, assumptions, or prompt patterns.

HARM: independent validation is only nominal.

OVERLAP TO CHECK: AGENT-001, PROOF-011.

### EVAL-003 — Evaluator cannot inspect critical hidden state

Important behavior may depend on provider configuration, remote prompts, credentials, caches, memory, feature flags, or user-specific data unavailable to the evaluator.

HARM: the evaluator proves only the visible shell.

OVERLAP TO CHECK: CTX-005, SELF-005.

### EVAL-004 — Refusal or safety filtering blocks necessary recovery

A model or provider may refuse to inspect security-sensitive code, credentials workflow, harmful examples, or recovery actions needed for legitimate defense.

HARM: essential diagnosis or recovery cannot be completed when most needed.

OVERLAP TO CHECK: PROV-001, VIAB-005.

## Pass 07 result

New provisional records: 40
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
- Current preserved plus provisional: 310

NEXT DISCOVERY PASS:
Data meaning, schema evolution, migration correctness, encryption and key handling, data minimization, identity linking, deletion semantics, synchronization, and privacy inference risks.

END PACKET 01.5 — DISCOVERY PASS 07
