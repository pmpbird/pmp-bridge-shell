# PMP Route Guardian Repo Index v1 Plan

Status: standalone support/test plan. Not wired into the main app yet.

Created: 2026-05-13

Deletion permission: false. Archive permission: false. Auto-promotion permission: false.

## Purpose

Give Route Guardian a repo-awareness layer so it can compare the current app route against recent repo activity.

This is a second proof channel, not a replacement for `pmp-current-map.json`.

## Core rule

Newest file does not automatically mean correct file.

Correct file means:

```text
newest approved stable route + map agreement + Route Guardian expected-path agreement + user/test receipt support
```

## v1 behavior

Route Guardian Repo Index v1 should:

1. Read the public GitHub repo metadata.
2. Read recent commits from `main`.
3. Build a newest-touched file list from recent commit details.
4. Sort touched files newest to oldest.
5. Read `pmp-current-map.json`.
6. Read `pmp-route-guardian-v1.js`.
7. Extract Route Guardian version and expected `currentInner` path.
8. Compare the current map path to Route Guardian expected path.
9. Classify files into practical groups.
10. Produce a copyable report.

## Classifications

Initial v1 groups:

```text
current-stable
route-guardian
current-inner
base-app
code-safety
bug-memory
support-script
control-pack-plan
control-pack-receipt
control-pack-decision
control-pack-hold
candidate-or-test
old-or-stale-candidate
unknown
```

## Safety rules

Repo Index v1 must not:

```text
delete files
archive files
edit files
auto-promote newest files
rewrite pmp-current-map.json
change Route Guardian expected path
claim newest means correct
```

## Good warnings

Repo Index v1 should warn if:

```text
pmp-current-map.json and Route Guardian expected path disagree
current map points to an old/stale-looking file
newer candidate files exist but no approval receipt is found
Route Guardian file is older than the current map change
control-pack receipts are missing for a promoted route
```

## v1 limitation

GitHub Pages can read public GitHub API data without secrets, but unauthenticated API rate limits apply. Therefore v1 should inspect a limited recent commit window rather than scanning the entire repo history.

Suggested v1 commit window:

```text
12 recent commits
```

## Standalone file

Build:

```text
pmp-route-guardian-repo-index-v1.html
```

Do not wire it into `pmp-app-current.html` until it passes as a support/test page.

## Future promotion path

Only after test proof:

```text
Route Guardian first screen
→ optional Repo Index button/panel
→ read-only repo awareness
→ current map remains the source of active route truth
```

## Current result

Plan created.

No active route changed.
No deletion.
No archive.
