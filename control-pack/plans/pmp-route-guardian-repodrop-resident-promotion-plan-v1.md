# PMP Route Guardian Repo Dropdown + Resident Promotion Plan v1

Built: 2026-05-14
Status: PLAN ONLY — no real app patch applied by this plan.

## Goal

Promote the tested Route Guardian improvements into the real installed app path only after proof is clean.

The real installed path remains:

- `pmp-app-current.html`

The working test path that passed the Resident shape problem is:

- `pmp-app-current-repodrop-test-v6.html`

The Resident-only support surface that avoids World flash is:

- `pmp-resident-route-guardian-surface-v2.html`

## User-approved behavior target

1. Route Guardian remains the first screen.
2. `Open World` is the only path that opens World.
3. Resident may open anytime from Route Guardian.
4. Resident must not load World behind it.
5. Resident must not flash World before opening.
6. Resident must keep all normal Resident options and abilities.
7. Resident Close hides Resident and returns to Route Guardian when opened from Route Guardian.
8. Normal app Resident behavior must not be hijacked.
9. Repo Index opens as a dropdown, not as a full-screen panel.
10. Show / Hide Report opens as a dropdown, not as a full-screen trap.

## Non-permissions

These remain false:

- deletion_permission: false
- archive_permission: false
- auto_promotion_permission: false
- route_guardian_writes_app_state: false

No old files should be deleted. No files should be archived. No newest file should be automatically promoted just because it is newest.

## Current clean test evidence

The user confirmed:

- Resident now looks right.
- Resident no longer loads World behind it.
- Resident-only surface keeps the needed normal Resident options.

The clean implementation path uses:

- `pmp-app-current-repodrop-test-v6.html` as the shell behavior proof.
- `pmp-resident-route-guardian-surface-v2.html` as the Resident-only surface proof.

## Files involved in real promotion

### Real app shell

Patch target:

- `pmp-app-current.html`

Promotion work:

- Remove or bypass the old full-screen Repo Index panel behavior.
- Add Repo Index dropdown behavior from the tested v6 shell.
- Add Resident pill behavior from the tested v6 shell.
- Point Resident pill to `pmp-resident-route-guardian-surface-v2.html`.
- Keep Route Guardian first-screen behavior intact.
- Keep Open World as the only World-opening path.

### Resident surface

Add or keep:

- `pmp-resident-route-guardian-surface-v2.html`

Promotion work:

- Keep as standalone Resident-only support surface.
- Do not load `pmp-home-single-v6.html` as hidden source.
- Do not show or flash World.
- Keep Resident options:
  - Chat
  - Tools
  - Ask box
  - Run
  - Close
  - Paste packet box
  - Packet Request
  - Save Packet
  - Pipeline
  - Show Work
  - Copy Work
  - Help Me
  - Archive Chat
  - Reset Chat
  - Resident reply
  - Resident warning
  - Resident work

### Route Guardian script

Patch target only if required:

- `pmp-route-guardian-v1.js`

Promotion work:

- Keep expected current inner aligned to the current map.
- Do not change current route truth unless the map changes.
- Do not add delete/archive/promote powers.

### Repo Index proof

Existing support:

- `pmp-route-guardian-repo-index-v1.html`

Promotion work:

- Keep Repo Index as routing truth only.
- Keep rule: newest does not mean correct.
- Keep active-file/proof-receipt checks.
- Present as dropdown from Route Guardian, not as a full-screen iframe panel.

## Required pre-patch checks

Before patching real files, verify:

1. `pmp-app-current-repodrop-test-v6.html` opens.
2. Route Guardian opens first.
3. Resident opens before Check Route.
4. Resident does not show World behind it.
5. Resident does not flash World.
6. Resident has normal options.
7. Resident Close returns to Route Guardian.
8. Check Route passes.
9. Open World opens World.
10. Normal app Resident still behaves normally from inside World.
11. Repo Index opens as dropdown.
12. Repo Index scan passes.
13. Report opens as dropdown.
14. No 404 on `pmp-resident-route-guardian-surface-v2.html`.
15. No stale-shell risk on the real installed app path.

## Real patch sequence

Do not patch all files blindly.

1. Fetch current `pmp-app-current.html`.
2. Create safe point / receipt before patch.
3. Patch only the necessary shell behavior:
   - Resident pill opens `pmp-resident-route-guardian-surface-v2.html` in the tested dropdown/floating drawer route.
   - Resident Close returns to Route Guardian only for that surface.
   - Repo Index opens as dropdown.
   - Report opens as dropdown.
   - Existing Route Guardian first-screen logic remains.
4. Do not patch `pmp-current-map.json` unless the current inner route changes.
5. Do not patch `pmp-route-guardian-v1.js` unless its expected path becomes stale.
6. Commit the real patch.
7. Run smoke test from browser path.
8. Run smoke test from Home Screen path.
9. Record receipt only after the real installed path passes.

## Blockers

Block promotion if any of these occur:

- Resident opens World first.
- World flashes behind Resident.
- Resident loses any normal option.
- Resident Close hijacks normal app Resident behavior.
- Repo Index opens a full-screen panel.
- Report creates a full-screen trap.
- Route Guardian is no longer first screen.
- Open World is not the only World path.
- Current map and Route Guardian expected path disagree.
- Any deletion/archive/autopromotion permission becomes true.

## Final approval wording needed before real patch

Use this exact approval before touching the real installed app shell:

> Approve patching `pmp-app-current.html` to promote tested Route Guardian Repo Index dropdown and Resident-only surface v2 behavior from `pmp-app-current-repodrop-test-v6.html`, while keeping Open World as the only World path and without changing deletion/archive/autopromotion permissions.

## Current decision

Plan is ready.

Next clean move is to review this plan, then either:

- approve real shell patching, or
- run one more v6 smoke test from the test link before real promotion.
