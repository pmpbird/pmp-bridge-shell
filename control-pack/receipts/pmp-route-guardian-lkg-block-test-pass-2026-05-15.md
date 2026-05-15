# PMP Route Guardian — Last Known Good Block Test Pass

Date: 2026-05-15

## Verdict

PASS_LKG_BLOCKED_ROUTE_PROOF

## Purpose

Prove that Last Known Good appears when Route Guardian blocks a route, while Open World stays blocked and the recovery path remains advisory only.

## Test Surface

- Test page: `pmp-route-guardian-lkg-block-test.html`
- Current approved loader at test time: `pmp-route-guardian-current-loader-v7.html`
- Current certifier at test time: `pmp-path-certifier-v7.js`
- Current inner app: `pmp-current-inner-cleanbug-rgcontrols-v3.html`

## Required Result

The test page must intentionally fail current-loader agreement because it is not the approved map loader. Route Guardian must block Open World and include Last Known Good recovery information.

## Observed Block

- `open_world_allowed`: false
- `next_allowed_action`: `BLOCK_OPEN_WORLD`
- `route_confidence`: LOW
- `stale_shell_risk`: true
- `self_drift_ok`: false
- `loader_current_surface_agreement`: false
- `blocked_reasons` included:
  - stale shell risk
  - route proof not clean
  - self drift: current surface does not match map loader

## Static Chain Still Passed

- `verdict`: `PASS_ROUTE_CHAIN_STATIC_PROOF`
- Map/current-inner static proof remained intact.
- This is acceptable because the route chain can exist while the current surface is still blocked by the certifier.

## Last Known Good Proof

Last Known Good appeared only because the route was blocked:

- `last_known_good.needed`: true
- `last_known_good.included`: true
- `last_known_good.available`: true
- `last_known_good.current_route_passed`: false
- `last_known_good.fetch_ok`: true
- `last_known_good.parse_ok`: true

## Last Known Good Route Recorded

- Entry: `pmp-app-current.html`
- Map: `pmp-current-map.json`
- Loader: `pmp-route-guardian-current-loader-v7.html`
- Certifier: `pmp-path-certifier-v7.js`
- Current inner: `pmp-current-inner-cleanbug-rgcontrols-v3.html`
- Fallback inner: `pmp-current-inner-cleanbug-rgcontrols-v3.html`
- World hash: `#world`
- Bug Memory: `bug-memory-current-clean-v1.html`
- Resident: `pmp-resident-route-guardian-surface-v2.html`
- Repo Index: `pmp-route-guardian-repo-index-v1.html`

## Advisory-Only Rule

Last Known Good is advisory only.

It must not:

- auto-restore
- auto-promote
- delete
- archive
- write app state

## Permission Integrity

- `deletion_permission`: false
- `archive_permission`: false
- `route_guardian_writes_app_state`: false

## Result Summary

- Blocked-route test: PASS
- Open World stayed blocked: PASS
- Last Known Good appeared when blocked: PASS
- Recovery path remained advisory only: PASS
- No destructive permission granted: PASS

## Final Status

This receipt proves the Route Guardian Last Known Good recovery path works as intended for a blocked current surface.