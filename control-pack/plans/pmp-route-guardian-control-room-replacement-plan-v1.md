# PMP Route Guardian Control Room Replacement Plan v1

Status: planning only. No current app files changed.

Created: 2026-05-12

Deletion permission: false. Archive permission: false.

## Purpose

Use Route Guardian to simplify the Control Room without removing the tools that still belong there.

Route Guardian should own the current-version doorway check and stale-route repair path. It should not absorb the whole Control Room and should not delete safety tools.

## User correction locked

These must stay in the Control Room:

1. Safe Writer / Safety Rider
2. Deep Resident Intelligence
3. Color Settings

These are not replacement targets.

## Replacement target

Route Guardian may replace or hide ordinary Control Room buttons whose main purpose is current-version routing or emergency route repair.

Primary replacement candidate:

- Automatic App Update

Possible conditional replacement candidate:

- Open Code Safety as a normal always-visible button

Important: Code Safety itself must remain protected. The question is only whether the normal Control Room button should remain visible. Code Safety should still be reachable from Route Guardian when Route Guardian detects a route/current-version problem.

## Clean future Control Room shape

Keep visible in Control Room:

- Safe Writer / Safety Rider
- Deep Resident Intelligence
- Color Settings
- Route Guardian / Check Current PMP

Move to Route Guardian problem state:

- Open Code Safety
- Hard Fresh
- Copy Route Report
- route/current-version repair guidance

Remove or hide after proof:

- Automatic App Update button, if Route Guardian fully owns current-version checking and loading

## Route Guardian responsibility

Route Guardian may read/check/link to:

- pmp-app-current.html
- pmp-current-map.json
- pmp-current-inner-cleanbug-v1.html
- pmp-home-single-v6.html
- bug-memory-current-clean-v1.html
- required current support scripts
- safe-writer-v14.html as a protected tool link
- code-safety-v13.html as a protected problem-state tool link
- hard-fresh.html as a protected problem-state tool link

Route Guardian must not absorb or rewrite the full behavior of those tools.

## Green state

When Route Guardian passes:

- Show current route is clean.
- Primary button changes from Check Route to Open / Load PMP Current.
- Copy Report remains available.
- Do not show emergency tools as the main path.
- Do not delete or change app files.

## Red state

When Route Guardian finds a problem:

- Turn red.
- Do not load PMP Current automatically.
- Show the route report.
- Keep Copy Report available.
- Show protected repair links:
  - Open Code Safety
  - Open Safe Writer / Safety Rider
  - Open Hard Fresh
- Explain the route/current-version problem in plain language.

## What Route Guardian replaces

Route Guardian can eventually replace the Control Room's current-version checking role.

That means it may replace Automatic App Update if all of these pass:

1. Route Guardian proves current map and current inner path.
2. Route Guardian can load PMP Current from the map after pass.
3. Route Guardian can detect stale route problems.
4. Route Guardian can expose repair tools only when needed.
5. User confirms the flow on iPhone.
6. Control Room still keeps Safe Writer / Safety Rider, Deep Resident Intelligence, and Color Settings.
7. A rollback path exists.

## What Route Guardian does not replace

Route Guardian does not replace:

- Safe Writer / Safety Rider
- Deep Resident Intelligence
- Color Settings
- Resident X-Ray
- Inventory Eyes
- Lossless Vault
- Bug Memory contents
- Big Memory Reader
- full app UI logic

## Required proof before changing Control Room

Before any real Control Room button is hidden or changed:

1. Route Guardian one-button proof page has a JSON-backed pass receipt.
2. Route Guardian candidate shell either passes fresh-code test or a safer candidate is built.
3. A Control Room patch proposal is created.
4. The patch proposal names every button affected.
5. A test copy of pmp-home-single-v6.html is created first.
6. User tests the test copy on iPhone.
7. Only then can the real pmp-home-single-v6.html be patched.

## Proposed future button change

Current Control Room visible buttons include:

- Open Safe Writer
- Open Code Safety
- Automatic App Update
- Color Settings
- Deep Resident Intelligence

Future Control Room after proof:

- Open Safe Writer / Safety Rider
- Route Guardian / Check Current PMP
- Color Settings
- Deep Resident Intelligence

Code Safety stays protected but moves into Route Guardian red/problem state unless the user later chooses to keep it visible too.

Automatic App Update is the main removal candidate.

## Non-deletion rule

This plan does not delete code-safety-v13.html, safe-writer-v14.html, hard-fresh.html, or any safety file.

It only plans a safer route for when those tools appear.

## Next action

Create a Control Room button replacement proposal before touching app code.

Suggested next file:

control-pack/proposals/pmp-control-room-route-guardian-button-proposal-v1.json
