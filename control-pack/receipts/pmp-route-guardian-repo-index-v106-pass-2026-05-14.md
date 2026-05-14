# PMP Route Guardian Repo Index v1.0.6 Pass — 2026-05-14

Status: PASS

## User-provided report

The user provided a Repo Index report from version:

```text
1.0.6-routing-truth-only
```

## Route truth

```text
agreement: true
warnings: []
map_current_path: pmp-current-inner-cleanbug-rgcontrols-v3.html
map_fallback_path: pmp-current-inner-cleanbug-rgcontrols-v3.html
route_guardian_version: 1.0.6-standalone-support-test
route_guardian_expected_currentInner: pmp-current-inner-cleanbug-rgcontrols-v3.html
```

## Active file summary

```text
required_count: 8
ok_count: 8
missing_count: 0
missing_paths: []
```

Active files confirmed readable:

```text
pmp-app-current.html
pmp-current-map.json
pmp-route-guardian-v1.js
pmp-current-inner-cleanbug-rgcontrols-v3.html
pmp-home-single-v6.html
bug-memory-current-clean-v1.html
pmp-route-guardian-action-v2.html
pmp-control-room-cleanup-v1.js
```

## Class summary proof

```text
unknown_count: 0
unknown_paths: []
```

## Proof receipt summary

```text
required_count: 4
ok_count: 4
missing_count: 0
missing_paths: []
```

## Safety state

```text
deletion_permission: false
archive_permission: false
auto_promotion_permission: false
```

## Result

Repo Index v1.0.6 proves:

```text
current route agreement + active file readability + proof receipt presence + no unknown recent classifications
```

## Next upgrade

Add a compact overall verdict field such as:

```text
repo_index_verdict: PASS_REPO_INDEX_ROUTING_TRUTH
```

This will let the user judge the whole report quickly without reading every section.
