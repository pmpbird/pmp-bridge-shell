# PMP Route Guardian Real Entry Pass — 2026-05-12

Result: PASS

Tested URL:
https://pmpbird.github.io/pmp-bridge-shell/pmp-app-current.html?rginstall=1

Report built at:
2026-05-13T06:10:50.196Z

Route Guardian version:
1.0.3-standalone-support-test

Surface:
pmp-app-current.html

Important note:
approved_support_test_surface is false because this is the real expected entry file, not a support test surface.

Pass facts:
- stale_shell_risk.risk_count = 0
- likely_stale_shell = false
- verdict = PASS_ROUTE_CHAIN_STATIC_PROOF
- current map fetch ok = true
- current map parse ok = true
- current path = pmp-current-inner-cleanbug-v1.html
- current path matches expected = true
- fallback path matches expected = true
- home screen rule matches expected = true
- current inner fetch ok = true
- current inner loads base app = true
- clean Bug Memory route present = true
- support file count present = 8
- old Bug Memory route blocked = true

Installed behavior confirmed by report:
- Route Guardian loaded inside pmp-app-current.html.
- Route Guardian checked the current route before World entry.
- Route proof passed cleanly.

Files changed in install step:
- pmp-app-current.html

Files not changed directly in install step:
- pmp-home-single-v6.html
- pmp-current-map.json
- pmp-current-inner-cleanbug-v1.html
- bug-memory-current-clean-v1.html

Next user-device checks:
- Tap Open World.
- Confirm visible heading says World.
- Confirm tabs work.
- Confirm Control Room still shows Safe Writer / Safety Rider, Deep Resident Intelligence, and Color Settings.
