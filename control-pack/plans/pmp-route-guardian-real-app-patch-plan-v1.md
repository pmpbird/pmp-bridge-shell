# PMP Route Guardian Real App Patch Plan v1

Status: patch plan only. No real app files changed.

Created: 2026-05-12

Deletion permission: false. Archive permission: false. Real app patch permission: false.

## Purpose

Define the exact future real-app patch for:

1. `pmp-app-current.html` — Route Guardian first-screen entry.
2. `pmp-home-single-v6.html` — visible World heading rename from `PMP World` to `World`.

This plan does not approve or perform the patch.

## Required precheck source

This plan follows:

```text
control-pack/checklists/pmp-route-guardian-real-patch-precheck-v1.md
```

Working model/proof source:

```text
pmp-route-guardian-test-v1.html?world=entry-v1
```

Pass receipt:

```text
control-pack/receipts/pmp-route-guardian-world-entry-test-pass-2026-05-12.json
```

Blocked cache receipt:

```text
control-pack/receipts/pmp-real-entry-test-blocked-by-cache-2026-05-12.json
```

## Hard boundary

Do not patch real app files unless the user explicitly says both of these by file name:

```text
Approve patching pmp-app-current.html for Route Guardian first-screen entry.
Approve patching pmp-home-single-v6.html to rename PMP World to World.
```

Until then:

```text
real_app_patch_permission: false
```

## Current protected files

Do not delete, archive, or rewrite these as part of this patch:

```text
pmp-current-map.json
pmp-current-inner-cleanbug-v1.html
bug-memory-current-clean-v1.html
safe-writer-v14.html
code-safety-v13.html
hard-fresh.html
```

## Patch 1: pmp-app-current.html

### Goal

Route Guardian becomes the first visible screen before World loads.

### Future behavior

1. User opens `pmp-app-current.html`.
2. Route Guardian appears first.
3. Main button starts as `Check Route`.
4. Copy Report stays visible before World opens.
5. Route Guardian checks `pmp-current-map.json`.
6. Route Guardian confirms the current map points to `pmp-current-inner-cleanbug-v1.html`.
7. Route Guardian confirms the current inner file loads `pmp-home-single-v6.html`.
8. Route Guardian confirms clean Bug Memory route `bug-memory-current-clean-v1.html` is present.
9. If clean, Route Guardian turns green/pass.
10. Main button changes to `Open World` or `Load World`.
11. User taps the main button.
12. Current app loads through the current map target.
13. Route Guardian overlay disappears and does not block app tabs.
14. If not clean, Route Guardian turns red and does not load World automatically.

### Implementation direction

`pmp-app-current.html` should keep `pmp-current-map.json` as the source of truth.

The patch should not hard-code the base app directly as the only path. It may use the expected route values for proof, but current loading should still come from the map.

Expected loading chain remains:

```text
pmp-app-current.html
→ Route Guardian gate
→ pmp-current-map.json
→ pmp-current-inner-cleanbug-v1.html
→ pmp-home-single-v6.html
→ #world
```

### Required Route Guardian UI inside real entry

The first screen should include:

```text
Route Guardian
Check Route button
Copy Report button
Show / Hide Report button or equivalent report visibility path
```

After pass:

```text
Check Route button changes to Open World / Load World
Copy Report remains available
```

On failure:

```text
red problem state
Copy Report available
World does not load automatically
plain-language problem note
```

### Not allowed in pmp-app-current.html patch

Do not:

- change `pmp-current-map.json`
- remove fallback awareness
- remove Copy Report
- auto-load World after a failed check
- expose private localStorage values
- write to app files
- delete any route or safety file
- hide Safe Writer, Deep Resident Intelligence, or Color Settings

## Patch 2: pmp-home-single-v6.html

### Goal

Change the visible World screen heading from:

```text
PMP World
```

to:

```text
World
```

### Scope

This is a display/title cleanup only.

Allowed change:

```html
<h1>PMP World</h1>
```

becomes:

```html
<h1>World</h1>
```

### Must remain unchanged

- screen id remains `world`
- route hash remains `#world`
- tab label remains `World`
- functions remain unchanged
- Bridge remains unchanged
- Library remains unchanged
- Workshop remains unchanged
- Control Room remains unchanged
- Resident remains unchanged
- Launcher remains unchanged

## Control Room protection

The real patch must preserve:

```text
Safe Writer / Safety Rider visible
Deep Resident Intelligence visible
Color Settings visible
Code Safety protected
Hard Fresh protected
```

This plan does not remove Control Room buttons.

The Automatic App Update replacement is a separate later Control Room patch track and should not be bundled into this real-entry/title patch.

## Patch order if later approved

If the user later approves real file patching by name, use this order:

1. Fetch current `pmp-app-current.html` and record SHA.
2. Fetch current `pmp-home-single-v6.html` and record SHA.
3. Patch `pmp-home-single-v6.html` title first because it is a small display-only change.
4. Patch `pmp-app-current.html` Route Guardian entry second.
5. Test `pmp-app-current.html` on iPhone.
6. Copy Route Guardian report.
7. Create pass/fail receipt.

## Rollback plan

If the title patch fails:

```text
Restore pmp-home-single-v6.html from previous SHA or backup branch.
```

If the Route Guardian entry patch fails:

```text
Restore pmp-app-current.html from previous SHA or backup branch.
Keep pmp-current-map.json unchanged.
Use pmp-route-guardian-test-v1.html?world=entry-v1 as external proof while repairing.
```

Backup branch:

```text
backup-before-pmp-cleanup-2026-05-12
```

## Post-patch test battery

After any later real patch, test on iPhone:

1. Open `pmp-app-current.html`.
2. Confirm Route Guardian appears first.
3. Tap `Check Route`.
4. Confirm green/pass state.
5. Confirm Copy Report works.
6. Confirm main button changes to `Open World` or `Load World`.
7. Tap main button.
8. Confirm World opens.
9. Confirm heading says `World`.
10. Confirm tabs are usable.
11. Confirm Bridge opens.
12. Confirm Library opens.
13. Confirm Workshop opens.
14. Confirm Control opens.
15. Confirm Safe Writer / Safety Rider remains visible.
16. Confirm Deep Resident Intelligence remains visible.
17. Confirm Color Settings remains visible.
18. Confirm Bug Memory clean route still opens.
19. Confirm no Route Guardian overlay blocks app tabs after World opens.
20. Confirm no old app route appears.
21. Confirm no stale-shell warning appears after a clean pass.

## Required receipt after later patch

Create:

```text
control-pack/receipts/pmp-route-guardian-real-app-patch-pass-YYYY-MM-DD.json
```

Receipt must include:

- patched file names
- previous SHAs
- new SHAs
- user report
- route report JSON summary
- pass/fail result
- rollback status
- deletion permission remains false
- archive permission remains false

## Current result

This patch plan is ready.

Real app patch is still blocked.

Next action:

```text
User must explicitly approve real file patching by name, or ask for another test-only pass.
```
