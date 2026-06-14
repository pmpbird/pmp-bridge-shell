# Packet 01.5 — Discovery Pass 04

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for performance, resource-exhaustion, observability, measurement, accessibility, localization, user-intent, benchmark-gaming, and silent-quality-degradation risks.

## Provisional records

### PERF-001 — Main-thread blocking and interface freezing

Large scans, parsing, rendering, compression, hashing, comparison, or AI-response handling may block the browser main thread.

HARM: the app appears frozen, taps are lost, approval screens become unusable, and iOS may terminate the page.

OVERLAP TO CHECK: PLAT-003, RUN-002.

### PERF-002 — Unbounded growth of logs, DOM, memory, queues, or history

Long sessions may continually append messages, diagnostics, evidence, task state, or hidden elements without cleanup.

HARM: progressive slowdown, crashes, quota exhaustion, and corrupted saves.

OVERLAP TO CHECK: DATA-006, OPS-003, RUN-013.

### PERF-003 — Pathological input causes extreme work

A huge file, deeply nested JSON, repetitive text, enormous archive, adversarial regex input, or large dependency graph may trigger superlinear work.

HARM: denial of service, battery drain, browser termination, or impossible completion.

OVERLAP TO CHECK: SEC-005, OPS-009.

### PERF-004 — Battery, thermal, network, and mobile-data exhaustion

Continuous polling, repeated hashing, background retries, large uploads, model calls, or long validation runs may consume excessive battery, heat, or cellular data.

HARM: device throttling, interrupted work, unexpected cost, or user abandonment.

OVERLAP TO CHECK: OPS-003, PLAT-002.

### PERF-005 — Startup depends on too many sequential resources

A long loader chain, multiple manifests, remote libraries, providers, fonts, models, or configuration fetches may all be required before the app becomes usable.

HARM: slow startup, fragile offline behavior, and larger failure surface.

OVERLAP TO CHECK: BUILD-004, PLAT-007, RUN-007.

### PERF-006 — Background suspension interrupts long work

Safari or iOS may suspend, discard, or throttle the Home Screen app during analysis, upload, validation, waiting, or queue processing.

HARM: unfinished work, missing acknowledgement, duplicated retries, or inconsistent state.

OVERLAP TO CHECK: PLAT-002, REL-003, REL-009.

### PERF-007 — Performance proof on one device does not generalize

A workflow may pass on a fast device, warm cache, strong network, or small dataset but fail on an older phone, cold start, weak connection, or realistic history size.

HARM: false performance confidence and field-only failures.

OVERLAP TO CHECK: PROOF-004, PLAT-001.

### OBS-001 — Errors are swallowed or converted into normal-looking output

Exceptions, rejected promises, provider errors, storage failures, parsing failures, and test failures may be caught without preserving the true failure state.

HARM: broken work appears successful.

OVERLAP TO CHECK: RUN-014, PROOF-001.

### OBS-002 — Events cannot be correlated across systems

The app, Shortcut, Notes, backend, GitHub, provider, candidate, test run, and receipt may use unrelated identifiers.

HARM: evidence cannot prove which action produced which result.

OVERLAP TO CHECK: DATA-011, REL-001.

### OBS-003 — Rare failures disappear through sampling or short tests

Monitoring or validation may inspect only selected events, recent runs, or common paths.

HARM: intermittent data loss, race conditions, and long-run failures remain invisible.

OVERLAP TO CHECK: PROOF-006, PROOF-013.

### OBS-004 — Instrumentation changes behavior or leaks information

Debug logging, tracing, timing, screenshots, and diagnostic hooks may alter timing, expose secrets, consume storage, or make a race condition disappear.

HARM: observed behavior differs from normal behavior and private data leaks.

OVERLAP TO CHECK: SEC-006, PROOF-002.

### OBS-005 — Evidence and logs expire before they are needed

Browser logs, provider logs, temporary files, CI artifacts, screenshots, and diagnostic records may be overwritten or deleted.

HARM: later failures cannot be reconstructed or audited.

OVERLAP TO CHECK: DATA-014, GOV-009, PROOF-012.

### OBS-006 — Health indicator disagrees with actual component health

A single green status may remain visible even when storage, backend, Shortcut, Notes, route, cache, provider, or guardian is degraded.

HARM: the user continues unsafe work under false normal status.

OVERLAP TO CHECK: HUM-003, RUN-014.

### MEAS-001 — Wrong denominator or excluded failures distort success rates

Metrics may count only completed runs, omit blocked attempts, ignore timeouts, exclude crashes, or merge retries.

HARM: performance and safety appear better than reality.

OVERLAP TO CHECK: PROOF-003, PROOF-014.

### MEAS-002 — Warm-cache and laboratory bias

Tests may run with preloaded data, cached assets, stable networks, known repositories, or prepared devices.

HARM: measured speed and reliability do not match ordinary use.

OVERLAP TO CHECK: PERF-007, PROOF-004.

### MEAS-003 — Benchmark leakage and overfitting

Resident or its developers may learn hidden tasks, labels, scoring rules, fixtures, or competitor weaknesses.

HARM: benchmark scores rise without general capability improving.

OVERLAP TO CHECK: PROOF-007, PROOF-010.

### MEAS-004 — Safety metrics can be gamed by refusing or blocking everything

A system may avoid unsafe promotions by refusing useful work, producing excessive HOLD decisions, or narrowing the evaluated task set.

HARM: high safety score with unusable behavior.

OVERLAP TO CHECK: PROOF-014, RUN-015.

### MEAS-005 — Thresholds drift after seeing results

Pass levels, severity labels, weighting, confidence thresholds, or comparison rules may be changed after weak results are observed.

HARM: retrospective rule changes manufacture a PASS.

OVERLAP TO CHECK: GOV-006, PROOF-010.

### MEAS-006 — Human scoring is inconsistent or biased

Reviewers may interpret correctness, severity, usefulness, naturalness, or safety differently across runs or competitors.

HARM: claims depend on subjective and unstable judgments.

OVERLAP TO CHECK: PROOF-010, PROOF-011.

### ACC-001 — Screen-reader and semantic structure are unproven

Buttons, headings, status, dialogs, errors, progress, and approval controls may lack correct names, roles, ordering, and announcements.

HARM: blind or low-vision users cannot safely understand or control the workflow.

OVERLAP TO CHECK: PLAT-013.

### ACC-002 — Visual, touch, and text-scaling access can fail

Low contrast, small touch targets, gesture-only actions, clipped Dynamic Type, zoom breakage, or color-only meaning may hide critical controls.

HARM: accidental approval, inability to recover, or inaccessible evidence.

OVERLAP TO CHECK: PLAT-013, HUM-002.

### ACC-003 — Timeouts, animation, and motion can block use

Timed confirmations, disappearing messages, auto-advance, flashing, or motion-heavy transitions may prevent careful review.

HARM: missed warnings, physical discomfort, or involuntary decisions.

OVERLAP TO CHECK: HUM-001, PLAT-013.

### LOC-001 — Locale-sensitive parsing changes meaning

Dates, times, decimal separators, thousands separators, sorting, calendars, and text comparison may behave differently by locale.

HARM: wrong ordering, wrong thresholds, malformed migrations, or incorrect evidence expiry.

OVERLAP TO CHECK: REL-007, PORT-001.

### LOC-002 — Text expansion and right-to-left layout break controls

Translated labels may be longer, use different scripts, or reverse layout direction.

HARM: clipped instructions, hidden buttons, or misleading approval surfaces.

OVERLAP TO CHECK: ACC-002, PLAT-013.

### LOC-003 — Translation changes legal, safety, or technical meaning

Terms such as delete, restore, promote, rollback, private, permanent, safe, and complete may be translated inconsistently.

HARM: users consent to a different action than intended.

OVERLAP TO CHECK: HUM-002, GOV-010.

### INTENT-001 — Ambiguous request is converted into a precise but wrong specification

Normal-language requests may support several reasonable meanings, while Resident selects one without enough clarification.

HARM: the system safely implements the wrong goal.

OVERLAP TO CHECK: AI-002, AI-003, RUN-003.

### INTENT-002 — User intent changes after specification lock

The user may refine, reverse, or partially withdraw the request while analysis, coding, testing, or queued actions continue under the old intent.

HARM: obsolete work is implemented or promoted.

OVERLAP TO CHECK: REL-009, RUN-013.

### INTENT-003 — Unspoken constraints are omitted

The user may assume preservation of appearance, cost, privacy, speed, offline behavior, compatibility, or existing habits without explicitly stating them.

HARM: a technically correct change violates the real need.

OVERLAP TO CHECK: GOV-007, OPS-014.

### INTENT-004 — Conflicting goals or authorities are unresolved

Speed, privacy, cost, completeness, portability, safety, and convenience may conflict, or two instructions may have different authority.

HARM: hidden tradeoffs are chosen without valid approval.

OVERLAP TO CHECK: GOV-005, GOV-008, AI-004.

### QUAL-001 — Graceful fallback hides missing capability

The app may silently substitute a weaker local mode, stale cache, placeholder result, or reduced provider behavior while appearing normal.

HARM: quality or protection disappears without an explicit HOLD or warning.

OVERLAP TO CHECK: OBS-006, RUN-014.

### QUAL-002 — Absence of visible errors is mistaken for correctness

A workflow may complete without exceptions while producing incomplete, stale, irrelevant, or semantically wrong output.

HARM: false PASS based only on technical completion.

OVERLAP TO CHECK: PROOF-001, PROOF-003.

### QUAL-003 — Model or provider quality drifts without interface failure

The same API and response schema may continue working while reasoning quality, factuality, coding quality, safety behavior, or latency degrades.

HARM: old proof remains technically compatible but no longer representative.

OVERLAP TO CHECK: PROV-001, PROOF-012.

## Pass 04 result

New provisional records: 29
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
- Current preserved plus provisional: 202

NEXT DISCOVERY PASS:
Governance capture, malicious authority changes, insider error, branch and repository loss, audit tampering, emergency powers, deletion and retention conflicts, and project-abandonment risks.

END PACKET 01.5 — DISCOVERY PASS 04
