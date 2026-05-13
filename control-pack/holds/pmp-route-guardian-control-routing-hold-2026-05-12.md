# PMP Route Guardian Control Routing Hold — 2026-05-12

Status: HOLD

## Current operating decision

Use the current installed Route Guardian first screen as-is for now.

Do not keep testing the Control Room button routing until the route map and Route Guardian expected path can be updated safely together.

## Working installed behavior

`pmp-app-current.html` currently has Route Guardian first-screen entry installed.

Working path:

```text
pmp-app-current.html
→ Route Guardian first screen
→ Check Route
→ Open World after pass
```

## Paused behavior

Pause testing and promotion of:

```text
Automatic App Update → Route Guardian first
Open Code Safety → Route Guardian first
```

Reason:

```text
The safer replacement inner-loader exists, but the current map still points to the old inner-loader. The map and Route Guardian expected current-inner path must be updated together before this is tested again.
```

## Created but not fully activated

Created support/action files:

```text
pmp-route-guardian-action-v1.html
pmp-current-inner-cleanbug-rgcontrols-v1.html
```

These should not be treated as active current route until the map and Route Guardian expected path are safely aligned.

## Do not do yet

Do not keep retesting Control Room button routing.
Do not claim Automatic App Update routing is fixed.
Do not claim Open Code Safety routing is fixed.
Do not change the current map unless Route Guardian expected path is also updated safely.
Do not delete or archive anything.

## Safe current use

Use the current installed first-screen Route Guardian only:

```text
https://pmpbird.github.io/pmp-bridge-shell/pmp-app-current.html?rginstall=1
```

## Next future repair condition

Only resume this track when both can be safely updated together:

1. `pmp-current-map.json` current/fallback path
2. `pmp-route-guardian-v1.js` expected currentInner

Target alignment later:

```text
pmp-current-inner-cleanbug-rgcontrols-v1.html
```

## Permissions

Deletion permission: false
Archive permission: false
Current map patch permission: false until a new explicit approval
Route Guardian expectation patch permission: false until a new explicit approval
