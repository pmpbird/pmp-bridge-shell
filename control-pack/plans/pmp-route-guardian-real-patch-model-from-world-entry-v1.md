# PMP Route Guardian Real Patch Model from World Entry Proof v1

Status: model/spec only. No real app files changed.

Created: 2026-05-12

Deletion permission: false. Archive permission: false. Real app patch permission: false.

## Purpose

Use the passed world-entry proof page as the model for any future real Route Guardian patch.

This file exists because the separate real-entry test page was blocked by Safari/GitHub Pages cache, while the already-served world-entry proof page passed cleanly on the user's device.

## Active proof source

Use this as the working proof/model source:

```text
pmp-route-guardian-test-v1.html?world=entry-v1
```

Pass receipt:

```text
control-pack/receipts/pmp-route-guardian-world-entry-test-pass-2026-05-12.json
```

Blocked real-entry receipt:

```text
control-pack/receipts/pmp-real-entry-test-blocked-by-cache-2026-05-12.json
```

## Why this model is valid

The user-provided report from the world-entry proof page showed:

```text
Route Guardian version: 1.0.2-standalone-support-test
approved_support_test_surface: true
stale_shell_risk.risk_count: 0
verdict: PASS_ROUTE_CHAIN_STATIC_PROOF
current_path: pmp-current-inner-cleanbug-v1.html
base app: pmp-home-single-v6.html
Bug Memory clean route: bug-memory-current-clean-v1.html
```

The user also confirmed:

```text
Everything looks good
```

## Do not use as proof yet

Do not use this cached page as final proof yet:

```text
pmp-app-current-route-guardian-real-entry-test.html
```

Reason:

```text
It kept loading an older cached Route Guardian script and produced a false stale-shell warning even though the route chain passed.
```

## Future real patch behavior

The future real patch should copy the behavior of the passed world-entry proof page, not the cached real-entry test page.

Required future behavior:

1. Route Guardian appears first.
2. Primary button starts as `Check Route`.
3. Copy Report remains visible before app/world opens.
4. Route Guardian checks `pmp-current-map.json`.
5. Route Guardian confirms current map points to `pmp-current-inner-cleanbug-v1.html`.
6. Route Guardian confirms current inner loads `pmp-home-single-v6.html`.
7. Route Guardian confirms clean Bug Memory route `bug-memory-current-clean-v1.html`.
8. If route proof passes, primary button changes to `Open World` or `Load World`.
9. If route proof fails, Route Guardian turns red and does not load World automatically.
10. After pass and user action, World opens through the current map target.
11. Visible World heading should say `World`, not `PMP World`.

## Real patch targets later

Only after a later explicit approval:

```text
pmp-app-current.html
pmp-home-single-v6.html
```

Potential real changes later:

```text
pmp-app-current.html:
- add Route Guardian first-screen gate before loading current inner app
- keep copy-report path available before opening World
- load World only after route proof passes and user taps Open/Load World

pmp-home-single-v6.html:
- visible World heading changes from PMP World to World
```

## Do not change yet

Do not change these during this model/spec stage:

```text
pmp-app-current.html
pmp-home-single-v6.html
pmp-current-map.json
pmp-current-inner-cleanbug-v1.html
bug-memory-current-clean-v1.html
safe-writer-v14.html
code-safety-v13.html
hard-fresh.html
```

## Control Room carryover

The future patch must preserve the user's locked Control Room requirements:

```text
Safe Writer / Safety Rider stays visible.
Deep Resident Intelligence stays visible.
Color Settings stays visible.
```

Route Guardian can replace current-version/update clutter, especially the Automatic App Update role, only after separate Control Room test proof.

## Promotion gates before real app patch

Before patching any real app file:

1. This model/spec exists.
2. Passed world-entry proof receipt exists.
3. Blocked cached real-entry receipt exists, so the cache issue is not confused with route failure.
4. Real patch proposal remains in DRAFT until user explicitly approves real app patch.
5. Backup branch remains available.
6. A rollback plan is written.
7. User approves touching `pmp-app-current.html` and/or `pmp-home-single-v6.html` by name.

## Current decision

Use the world-entry proof page as the model.
Stop retesting the cached real-entry page for now.
Do not patch real app files yet.

## Next action

Create a final pre-patch checklist before any real app patch is allowed.
Suggested file:

```text
control-pack/checklists/pmp-route-guardian-real-patch-precheck-v1.md
```
