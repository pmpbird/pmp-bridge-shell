# PMP Route Guardian Map + Expected Path Alignment Plan v1

Status: planning only. No current route files changed.

Created: 2026-05-12

Deletion permission: false. Archive permission: false.

## Purpose

Prepare the safe repair path for the paused Control Room routing track.

The problem is not Route Guardian first-screen entry. That part is installed and working.

The paused problem is this:

```text
Automatic App Update and Open Code Safety cannot reliably route through Route Guardian until the active current inner-loader and Route Guardian's expected current-inner path are aligned.
```

## Current working state

Working now:

```text
pmp-app-current.html
→ Route Guardian first screen
→ Check Route
→ Open World after pass
```

Working proof receipt:

```text
control-pack/receipts/pmp-route-guardian-real-entry-pass-2026-05-12.md
```

Current hold:

```text
control-pack/holds/pmp-route-guardian-control-routing-hold-2026-05-12.md
```

## Paused track

Paused until alignment:

```text
Automatic App Update → Route Guardian first
Open Code Safety → Route Guardian first
```

## Existing new support files

These files already exist but are not fully active as the current route:

```text
pmp-route-guardian-action-v1.html
pmp-current-inner-cleanbug-rgcontrols-v1.html
```

## Required alignment later

These two files must be updated together in one controlled move:

```text
pmp-current-map.json
pmp-route-guardian-v1.js
```

Target active current inner path:

```text
pmp-current-inner-cleanbug-rgcontrols-v1.html
```

## Required future map change

Future map target should become:

```json
"current_app": {
  "path": "pmp-current-inner-cleanbug-rgcontrols-v1.html",
  "label": "PMP Current Clean Bug Memory + Route Guardian Controls",
  "cache_key": "pmp-current-cleanbug-rgcontrols-v1",
  "status": "current"
}
```

Fallback should also point to the same known-good current inner after the new route passes:

```json
"fallback_app": {
  "path": "pmp-current-inner-cleanbug-rgcontrols-v1.html",
  "cache_key": "fallback-cleanbug-rgcontrols-v1"
}
```

## Required future Route Guardian expectation change

Future Route Guardian expected current inner should become:

```text
currentInner: pmp-current-inner-cleanbug-rgcontrols-v1.html
```

Route Guardian version should advance from:

```text
1.0.3-standalone-support-test
```

to:

```text
1.0.4-standalone-support-test
```

## Why both must change together

If only the map changes:

```text
Route Guardian may fail because expected currentInner is still old.
```

If only Route Guardian changes:

```text
Route Guardian may fail because the current map still points to the old inner-loader.
```

Clean rule:

```text
Map current path and Route Guardian expected path must agree before testing Control Room routing again.
```

## Required explicit approval before patching

Before changing these files, user must explicitly approve by file name:

```text
Approve patching pmp-current-map.json to point to pmp-current-inner-cleanbug-rgcontrols-v1.html.
Approve patching pmp-route-guardian-v1.js to expect pmp-current-inner-cleanbug-rgcontrols-v1.html.
```

Without this, patch permission remains false.

## Patch order later

If explicitly approved later, use this order:

1. Fetch current `pmp-current-map.json` and record SHA.
2. Fetch current `pmp-route-guardian-v1.js` and record SHA.
3. Patch `pmp-route-guardian-v1.js` expectation to the new inner path and version 1.0.4.
4. Patch `pmp-current-map.json` current/fallback path to the new inner path.
5. Test `pmp-app-current.html` with a fresh query.
6. Copy Route Guardian report.
7. Confirm `stale_shell_risk.risk_count = 0`.
8. Confirm `current_path = pmp-current-inner-cleanbug-rgcontrols-v1.html`.
9. Only then resume Control Room button routing tests.

## Test after alignment

Test link later:

```text
https://pmpbird.github.io/pmp-bridge-shell/pmp-app-current.html?rgalign=1
```

Expected report later:

```text
version: 1.0.4-standalone-support-test
current_path: pmp-current-inner-cleanbug-rgcontrols-v1.html
current_path_matches_expected: true
fallback_path_matches_expected: true
stale_shell_risk.risk_count: 0
verdict: PASS_ROUTE_CHAIN_STATIC_PROOF
```

Then test:

1. Open World after Route Guardian pass.
2. Go to Control Room.
3. Tap Automatic App Update.
4. Confirm Route Guardian action page opens and stays.
5. Tap Check Route.
6. Confirm pass.
7. Confirm action continues to current check.
8. Go back to Control Room.
9. Tap Open Code Safety.
10. Confirm Route Guardian action page opens and stays.
11. Confirm Code Safety opens after pass.

## Rollback later

If alignment fails:

1. Restore `pmp-current-map.json` to old path:
   `pmp-current-inner-cleanbug-v1.html`
2. Restore `pmp-route-guardian-v1.js` expected currentInner to:
   `pmp-current-inner-cleanbug-v1.html`
3. Keep `pmp-app-current.html` Route Guardian first screen installed unless it is directly failing.
4. Keep using the current installed first-screen path only.

## Current result

This plan is created.

No map patch done.
No Route Guardian expectation patch done.
No delete/archive/cleanup done.

## Next best move

Ask for explicit file-name approval if the user wants to activate the alignment.
