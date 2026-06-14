# Packet 01.5 — Discovery Pass 11

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for interface-state ambiguity, destructive-action design, mobile interaction errors, interrupted workflows, notification failure, undo defects, stale screens, and human recovery mistakes.

## Provisional records

### UI-001 — Screen state is stale after underlying state changes

A page may continue showing old candidate, packet, permission, provider, storage, or deployment status after another tab, device, tool, or backend changes it.

HARM: the user acts on a state that is no longer true.

OVERLAP TO CHECK: SYNC-001, OBS-006.

### UI-002 — Action controls do not show the exact target identity

Buttons such as approve, promote, delete, restore, retry, replace, or close may omit the candidate ID, file, packet, environment, or version they affect.

HARM: the correct action is applied to the wrong object.

OVERLAP TO CHECK: TOOL-001, REL-001.

### UI-003 — One status word represents several different layers

PASS, SAVED, SYNCED, DEPLOYED, VERIFIED, SAFE, COMPLETE, or CURRENT may describe only one layer while appearing to describe the whole system.

HARM: partial success is mistaken for global success.

OVERLAP TO CHECK: HUM-003, OBS-006.

### UI-004 — Optimistic interface reports success before durable completion

The screen may update immediately even though storage, backend, GitHub, Notes, deployment, or receipt creation is still pending.

HARM: the user leaves or continues under a false success state.

OVERLAP TO CHECK: REL-003, NET-001.

### UI-005 — Progress indicator freezes or advances inaccurately

A spinner, percentage, step count, or queue position may stop updating, jump, reset, or continue after failure.

HARM: the user cannot tell whether work is active, blocked, duplicated, or abandoned.

OVERLAP TO CHECK: OBS-001, PERF-001.

### UI-006 — Error message hides the failed layer

A generic failure may not say whether the problem occurred in validation, storage, provider, permission, network, deployment, receipt, or recovery.

HARM: the user repeats the wrong action or chooses the wrong recovery path.

OVERLAP TO CHECK: OBS-001, NET-001.

### UI-007 — Warning severity is visually inconsistent

Critical, blocking, informational, stale, and recoverable conditions may use similar colors, icons, placement, or wording.

HARM: dangerous warnings are treated like ordinary notices.

OVERLAP TO CHECK: ACC-002, HUM-001.

### UI-008 — Confirmation dialog lacks concrete consequences

A dialog may ask “Are you sure?” without stating what will change, what cannot be undone, what remains, and which object is affected.

HARM: consent is recorded without informed understanding.

OVERLAP TO CHECK: HUM-002, UI-002.

### UI-009 — Default or emphasized action is unsafe

The visually dominant, preselected, keyboard-default, or first focus target may be promote, replace, delete, overwrite, or continue.

HARM: habit or accidental input chooses the most damaging option.

OVERLAP TO CHECK: HUM-001, ACC-001.

### UI-010 — Layout shift moves controls under the finger

Loading text, keyboard appearance, images, status updates, dynamic type, or orientation changes may move a button during a tap.

HARM: the user triggers a different action than intended.

OVERLAP TO CHECK: ACC-002, PERF-001.

### UI-011 — Overlapping or crowded tap targets cause wrong actions

Small screens may place approve, reject, delete, restore, close, and back controls too near each other.

HARM: high-impact actions occur from ordinary touch imprecision.

OVERLAP TO CHECK: ACC-002, MOB-001.

### UI-012 — Rapid taps or double taps create duplicate actions

The interface may leave controls active while a request is pending.

HARM: duplicate issues, writes, approvals, deployments, retries, or deletions occur.

OVERLAP TO CHECK: REL-008, AUTO-005.

### UI-013 — Modal or sheet remains open after its target changes

A candidate, packet, file, or recovery point may be replaced while an old confirmation surface remains visible.

HARM: confirmation applies to a stale target.

OVERLAP TO CHECK: UI-001, INTENT-002.

### UI-014 — Hidden scrolling conceals required warnings or actions

Long receipts, dialogs, sheets, and forms may place consequences, remaining watches, or cancel controls outside the visible mobile viewport.

HARM: the user approves without seeing all required information.

OVERLAP TO CHECK: HUM-002, ACC-002.

### UI-015 — Unsaved changes are not clearly distinguished from saved state

Draft edits, pending uploads, local-only notes, and committed records may look identical.

HARM: the user assumes work is preserved when it is not.

OVERLAP TO CHECK: REPO-005, REL-003.

### UI-016 — Navigation loses or silently submits unfinished work

Back, reload, close, app switching, deep links, or route changes may discard drafts or submit partially completed forms.

HARM: intent and project state diverge without explicit choice.

OVERLAP TO CHECK: FLOW-001, INTENT-002.

### UI-017 — History and current state are visually mixed

Old receipts, superseded packets, archived candidates, and active records may appear together without clear state labels.

HARM: historical evidence is mistaken for current authority.

OVERLAP TO CHECK: REG-003, GOV-009.

### UI-018 — Sensitive information appears in previews and app-switcher snapshots

Prompt text, code, credentials, errors, recovery details, and private records may remain visible outside the app.

HARM: nearby people or other software can see protected content.

OVERLAP TO CHECK: SEC-006, PHY-003.

### DEST-001 — Irreversible action is available without a safer reversible stage

Delete, overwrite, revoke, rotate, promote, replace, or migrate may act directly instead of first creating a preview, quarantine, backup, or candidate.

HARM: one mistake produces permanent loss.

OVERLAP TO CHECK: RUN-006, REC-001.

### DEST-002 — Bulk-action scope is unclear

“Delete all,” “replace,” “restore,” “apply,” or “close selected” may not show the exact record count, categories, dependencies, and exclusions.

HARM: a larger set changes than the user intended.

OVERLAP TO CHECK: INS-001, UI-008.

### DEST-003 — Destructive preview differs from actual execution

The preview may omit hidden records, dependent objects, provider effects, or changes caused by current state at execution time.

HARM: informed approval is based on an incomplete simulation.

OVERLAP TO CHECK: TEST-017, SEM-004.

### DEST-004 — Offline destructive action executes later under changed conditions

A queued deletion, overwrite, revocation, restore, or promotion may run after the target, authority, or user intent changes.

HARM: stale intent causes current damage.

OVERLAP TO CHECK: REL-009, INTENT-002.

### DEST-005 — Delete, remove, archive, detach, revoke, reset, and erase are not distinguished

Different actions may use similar words while having very different persistence and recovery effects.

HARM: the user selects an action whose real meaning they did not intend.

OVERLAP TO CHECK: LOC-003, DEL-001.

### DEST-006 — Destructive action also removes its own recovery evidence

Deleting a candidate, provider, branch, key, account, or dataset may remove logs, receipts, mappings, or credentials needed to undo it.

HARM: the action destroys the route back.

OVERLAP TO CHECK: REC-001, AUD-001.

### DEST-007 — Confirmation can be reused after state changes

A confirmation token, open dialog, browser history entry, or cached approval may remain valid after the target mutates.

HARM: old consent authorizes a new action.

OVERLAP TO CHECK: AUTH-006, UI-013.

### DEST-008 — Cancellation is accepted visually but action still completes

The interface may show cancelled while an already-sent provider, deployment, deletion, or write continues.

HARM: the user believes damage was prevented when it was not.

OVERLAP TO CHECK: NET-001, REL-003.

### MOB-001 — System gestures conflict with app gestures

Edge swipes, pull-to-refresh, text selection, long press, pinch, and browser navigation may overlap custom controls.

HARM: accidental navigation, refresh, selection, or action occurs.

OVERLAP TO CHECK: ACC-002, UI-011.

### MOB-002 — Keyboard and viewport hide the active control or warning

The on-screen keyboard may cover submit, cancel, consequence text, errors, or the current field.

HARM: incomplete or wrong data is submitted, or the user cannot safely cancel.

OVERLAP TO CHECK: ACC-002, UI-014.

### MOB-003 — Orientation and safe-area changes break layout

Rotation, display zoom, notches, browser bars, and standalone mode may clip or reposition critical controls.

HARM: actions become unreachable or misleading.

OVERLAP TO CHECK: PLAT-013, LOC-002.

### MOB-004 — App switching returns to an obsolete or sensitive screen

After authentication, provider changes, timeout, or project-state changes, iOS may restore an old visual snapshot.

HARM: stale approval or private information is exposed.

OVERLAP TO CHECK: UI-001, UI-018.

### MOB-005 — Share sheet sends the wrong file or stale version

Similar filenames, generated copies, cached previews, and recent-item ordering may cause the wrong packet, ZIP, screenshot, or source file to be shared.

HARM: private or obsolete artifacts leave the device.

OVERLAP TO CHECK: REPO-003, SEC-006.

### MOB-006 — Clipboard content persists or is replaced unexpectedly

Copied credentials, packets, commands, links, and code may remain available to other apps or be overwritten before paste.

HARM: secrets leak or the wrong content is submitted.

OVERLAP TO CHECK: SEC-006, REG-002.

### FLOW-001 — Interruption occurs before a durable checkpoint

Suspension, crash, call, low battery, reload, network loss, or device lock may interrupt a multi-step action before its state is safely recorded.

HARM: the system cannot tell what completed or where to resume.

OVERLAP TO CHECK: PERF-006, REL-002.

### FLOW-002 — Resume enters the wrong stage

A recovered workflow may restart from the beginning, skip validation, repeat a side effect, or resume after the target changed.

HARM: duplicate or out-of-order work corrupts state.

OVERLAP TO CHECK: REL-003, REL-008.

### FLOW-003 — Multi-step workflow has no visible transaction boundary

The user may not know which steps are provisional, committed, externally executed, or still reversible.

HARM: they exit, retry, or recover at an unsafe point.

OVERLAP TO CHECK: UI-004, REL-002.

### FLOW-004 — Recovery flow assumes the user remembers unavailable facts

Recovery may ask for the former version, affected packet, account, key, last successful step, or exact error when those details are inaccessible.

HARM: the correct recovery path cannot be selected.

OVERLAP TO CHECK: REC-002, SUCC-001.

### NOTIFY-001 — Required notification is suppressed, delayed, or grouped

OS settings, focus mode, network delay, browser restrictions, provider batching, or notification permissions may prevent timely delivery.

HARM: failures, approvals, expiry, provider loss, and recovery needs go unnoticed.

OVERLAP TO CHECK: PLAT-003, OBS-005.

### NOTIFY-002 — Notification lacks exact object and state identity

A message such as “build complete,” “action needed,” or “failed” may omit the candidate, packet, provider, environment, and timestamp.

HARM: the user opens or acts on the wrong item.

OVERLAP TO CHECK: UI-002, OBS-002.

### NOTIFY-003 — Notification action becomes stale

Approve, retry, restore, or open actions may remain available after the object changes, expires, closes, or is replaced.

HARM: old notifications trigger current side effects.

OVERLAP TO CHECK: DEST-007, INTENT-002.

### NOTIFY-004 — Repeated low-value notifications create alert blindness

Frequent progress, warning, retry, and success messages may reduce attention to critical events.

HARM: the important notification is ignored.

OVERLAP TO CHECK: HUM-001, INS-003.

### RECUI-001 — Undo is offered when full reversal is impossible

The interface may present Undo even though external messages, provider writes, key exposure, deletion propagation, or deployment effects cannot be reversed.

HARM: the user receives false recovery confidence.

OVERLAP TO CHECK: DEST-008, REC-001.

### RECUI-002 — Undo window is too short, hidden, or dependent on screen state

A toast or temporary control may disappear before the user understands the error or after the app is interrupted.

HARM: a theoretically reversible action becomes practically permanent.

OVERLAP TO CHECK: ACC-003, FLOW-001.

### RECUI-003 — Undo reverses visible state but not external side effects

The screen may restore a record while GitHub, Notes, provider, cache, notifications, or deployment remains changed.

HARM: apparent recovery leaves the system split.

OVERLAP TO CHECK: REL-004, SYNC-001.

### RECUI-004 — User selects the wrong restore point

Recovery options may show similar dates, names, versions, candidates, or incomplete descriptions.

HARM: valid newer work is overwritten or an unsafe version returns.

OVERLAP TO CHECK: BKP-002, UI-002.

## Pass 11 result

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
- Pass 09 provisional: 42
- Pass 10 provisional: 43
- Pass 11 provisional: 44
- Current preserved plus provisional: 483

NEXT DISCOVERY PASS:
Network trust, API semantics, authentication sessions, authorization enforcement, replay, rate limits, remote configuration, third-party web content, and cross-origin boundaries.

END PACKET 01.5 — DISCOVERY PASS 11
