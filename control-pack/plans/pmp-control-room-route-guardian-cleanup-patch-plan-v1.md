# PMP Control Room Route Guardian Cleanup Patch Plan v1

Status: patch plan only. No Control Room buttons hidden yet.

Created: 2026-05-13

Deletion permission: false. Archive permission: false.

## Purpose

Clean the normal Control Room view now that Route Guardian successfully owns the safer paths for Code Safety and Automatic App Update.

## Current confirmed state

Confirmed by user:

```text
Code Safety opens compact inside Route Guardian and still has all options available.
```

Confirmed route shape:

```text
Open Code Safety
→ Route Guardian action
→ Check Route
→ Open Code Safety
→ compact Code Safety panel inside Route Guardian
```

Confirmed current check shape:

```text
Automatic App Update
→ Route Guardian action
→ Check Route
→ Open World / current path
```

## Cleanup goal

Remove clutter from the normal Control Room view without deleting any underlying tool.

## Keep visible in Control Room

These must remain visible:

```text
Safe Writer / Safety Rider
Deep Resident Intelligence
Color Settings
```

Optional visible item if needed:

```text
Route Guardian / Current Check
```

## Hide from normal Control Room

These may be hidden from the normal Control Room view because their safe path now lives through Route Guardian:

```text
Open Code Safety
Automatic App Update
```

## Do not delete

Do not delete or archive:

```text
code-safety-v13.html
code-safety.html
pmp-route-guardian-action-v2.html
pmp-route-guardian-v1.js
pmp-current-inner-cleanbug-rgcontrols-v2.html
pmp-current-map.json
safe-writer-v14.html
hard-fresh.html
```

## Implementation direction

Because `pmp-home-single-v6.html` is large and direct patching can be risky, the first cleanup should be done from the active current shell/inner route instead of directly rewriting the large base app.

Preferred safe patch location:

```text
pmp-current-inner-cleanbug-rgcontrols-v2.html
```

Patch behavior:

1. Detect Control Room buttons after the app loads.
2. Find button text containing `Open Code Safety`.
3. Hide that button from the normal Control Room view.
4. Find button text containing `Automatic App Update`.
5. Hide that button from the normal Control Room view.
6. Leave Safe Writer / Safety Rider visible.
7. Leave Deep Resident Intelligence visible.
8. Leave Color Settings visible.
9. Leave Code Safety accessible through Route Guardian action path, not deleted.
10. Leave Automatic App Update/current check logic accessible through Route Guardian/Open World path, not deleted.

## Test after patch

Test link:

```text
https://pmpbird.github.io/pmp-bridge-shell/pmp-app-current.html?controlcleanup=1
```

Test battery:

1. Open app.
2. Pass Route Guardian.
3. Tap Open World.
4. Open Control Room.
5. Confirm `Open Code Safety` button is not visible.
6. Confirm `Automatic App Update` button is not visible.
7. Confirm Safe Writer / Safety Rider is visible.
8. Confirm Deep Resident Intelligence is visible.
9. Confirm Color Settings is visible.
10. Confirm Route Guardian first-screen still appears on fresh app open.
11. Confirm Code Safety still works through Route Guardian action if reached from the existing safe path.
12. Confirm no file is deleted or archived.

## Rollback

If cleanup hides the wrong thing:

1. Restore previous `pmp-current-inner-cleanbug-rgcontrols-v2.html` SHA.
2. Keep `pmp-current-map.json` pointed at the current v2 route unless the v2 route itself fails.
3. Do not touch `pmp-home-single-v6.html`.
4. Do not delete any safety file.

## Approval needed before patch

Before patching the active inner file, user should approve:

```text
Approve patching pmp-current-inner-cleanbug-rgcontrols-v2.html to hide Open Code Safety and Automatic App Update from the normal Control Room view.
```

## Current result

Plan created.

No Control Room button cleanup installed yet.
No deletion.
No archive.
