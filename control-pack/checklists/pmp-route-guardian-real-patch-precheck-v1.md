# PMP Route Guardian Real Patch Precheck v1

Status: required gate before any real app patch.

Created: 2026-05-12

Deletion permission: false. Archive permission: false. Real app patch permission: false.

## Purpose

This checklist must pass before any real app file is touched for Route Guardian first-screen entry or the World title rename.

Real app files protected by this checklist:

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

## Patch goal

Future desired behavior:

1. Route Guardian appears first.
2. Route Guardian checks the current route before World loads.
3. Copy Report remains available before opening World.
4. If route proof passes, the main button changes to `Open World` or `Load World`.
5. If route proof fails, Route Guardian turns red and does not load World automatically.
6. World opens through the current map target.
7. Visible World heading says `World`, not `PMP World`.

## Required source proof

These must exist before any real patch:

- [ ] `control-pack/receipts/pmp-route-guardian-one-button-json-pass-2026-05-12.json`
- [ ] `control-pack/receipts/pmp-route-guardian-world-entry-test-pass-2026-05-12.json`
- [ ] `control-pack/receipts/pmp-real-entry-test-blocked-by-cache-2026-05-12.json`
- [ ] `control-pack/plans/pmp-route-guardian-real-patch-model-from-world-entry-v1.md`
- [ ] `control-pack/proposals/pmp-route-guardian-real-app-entry-world-title-proposal-v1.json`

## Required proof values

From the working proof receipt/report:

- [ ] Route Guardian version is `1.0.2-standalone-support-test` or newer.
- [ ] `approved_support_test_surface` is `true`.
- [ ] `stale_shell_risk.risk_count` is `0`.
- [ ] `verdict` is `PASS_ROUTE_CHAIN_STATIC_PROOF`.
- [ ] Current map path is `pmp-current-inner-cleanbug-v1.html`.
- [ ] Current inner loads `pmp-home-single-v6.html`.
- [ ] Clean Bug Memory route is `bug-memory-current-clean-v1.html`.
- [ ] Support file count present is `8` or otherwise explicitly explained.

## Cache warning gate

The separate real-entry test page is not trusted as proof yet.

Blocked page:

```text
pmp-app-current-route-guardian-real-entry-test.html
```

Reason:

```text
It repeatedly loaded old cached Route Guardian code and produced a false stale-shell warning.
```

Before using that page as proof, it must show:

- [ ] Route Guardian version `1.0.3-standalone-support-test` or newer.
- [ ] `approved_support_test_surface: true`.
- [ ] `stale_shell_risk.risk_count: 0`.

Until then, use this as model/proof:

```text
pmp-route-guardian-test-v1.html?world=entry-v1
```

## Required user approval before real patch

Before touching real app files, user must explicitly approve by file name.

Required explicit approval language:

```text
Approve patching pmp-app-current.html for Route Guardian first-screen entry.
Approve patching pmp-home-single-v6.html to rename PMP World to World.
```

Without this, real patch permission remains false.

## Backup and rollback gate

Before real patch:

- [ ] Backup branch exists: `backup-before-pmp-cleanup-2026-05-12`.
- [ ] Restore drill remains valid.
- [ ] Previous file SHA is recorded for `pmp-app-current.html`.
- [ ] Previous file SHA is recorded for `pmp-home-single-v6.html`.
- [ ] Rollback instruction is written before patching.

Rollback instruction:

```text
If real patch fails, restore pmp-app-current.html and/or pmp-home-single-v6.html from backup branch or previous commit.
Keep pmp-current-map.json unchanged unless a separate map proposal is approved.
Use pmp-route-guardian-test-v1.html?world=entry-v1 as external proof while repairing.
```

## Route Guardian first-screen entry patch checks

Before patching `pmp-app-current.html`:

- [ ] Patch plan describes exactly where Route Guardian gate enters.
- [ ] Patch keeps `pmp-current-map.json` as the source of current truth.
- [ ] Patch does not hard-code a stale app version.
- [ ] Patch does not delete fallback behavior.
- [ ] Patch does not remove Copy Report.
- [ ] Patch does not auto-load World after failure.
- [ ] Patch keeps red/problem state visible when route proof fails.
- [ ] Patch does not expose private localStorage values.
- [ ] Patch does not write to app files.
- [ ] Patch does not change `pmp-current-map.json`.

## World title rename patch checks

Before patching `pmp-home-single-v6.html`:

- [ ] Only the visible World heading is renamed.
- [ ] Change is from `PMP World` to `World`.
- [ ] Tab label `World` stays correct.
- [ ] Screen id `world` stays unchanged.
- [ ] Functions and route hash `#world` stay unchanged.
- [ ] No Control Room tools are removed by this title rename.
- [ ] No Library, Bridge, Workshop, Resident, or Launcher behavior is changed by this title rename.

## Control Room protection gate

Any real patch must preserve these Control Room items:

- [ ] Safe Writer / Safety Rider remains visible.
- [ ] Deep Resident Intelligence remains visible.
- [ ] Color Settings remains visible.
- [ ] Code Safety remains protected.
- [ ] Hard Fresh remains protected.

Route Guardian may later replace the Automatic App Update role only after a separate Control Room patch pass.

## Post-patch test battery

After any real patch, these must pass on iPhone:

- [ ] Open `pmp-app-current.html`.
- [ ] Route Guardian appears first.
- [ ] Tap `Check Route`.
- [ ] Route Guardian turns green/pass.
- [ ] Copy Report works before opening World.
- [ ] Main button changes to `Open World` or `Load World`.
- [ ] Tap the main button.
- [ ] World opens.
- [ ] Visible heading says `World`.
- [ ] Tabs still work.
- [ ] Bridge opens.
- [ ] Library opens.
- [ ] Workshop opens.
- [ ] Control Room opens.
- [ ] Safe Writer / Safety Rider remains visible.
- [ ] Deep Resident Intelligence remains visible.
- [ ] Color Settings remains visible.
- [ ] Bug Memory clean route still opens.
- [ ] No Route Guardian overlay blocks app tabs after World opens.
- [ ] No old app route appears.
- [ ] No stale-shell warning appears after a clean pass.

## Receipt required after real patch

After patching and testing, create a receipt:

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

## Hard stop conditions

Do not patch real app files if any of these are true:

- [ ] User has not approved patching the real file by name.
- [ ] Backup branch is missing.
- [ ] Restore path is unclear.
- [ ] Current map proof fails.
- [ ] Route Guardian proof report has stale-shell risk greater than 0.
- [ ] Copy Report is broken.
- [ ] Test copy or proof source is still serving old cached code and no working proof alternative is named.
- [ ] The change would hide Safe Writer / Safety Rider.
- [ ] The change would hide Deep Resident Intelligence.
- [ ] The change would hide Color Settings.
- [ ] The change would delete or archive any file.

## Current result

Precheck file created.

Real patch permission remains false.

Next action:

```text
Review this checklist, then decide whether to approve building the real patch plan or to do another test-copy pass first.
```
