# PMP Route Guardian Repo Index v1.0.3 Pass — 2026-05-13

Status: PASS

## User-provided report

The user provided a Repo Index report from version:

```text
1.0.3-routing-truth-only
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

## Safety state

```text
deletion_permission: false
archive_permission: false
auto_promotion_permission: false
```

## Confirmed classifier improvement

The following specific classes are now working:

```text
repo-index-page
repo-index-receipt
repo-index-decision
repo-index-plan
installed-stable-receipt
control-room-cleanup-receipt
current-map
route-guardian
```

## Next upgrade

Add a compact classification summary to the report:

```text
class_counts
unknown_paths
unknown_count
```

This makes it easier to see whether Repo Index understands the recent file set without reading every item manually.
