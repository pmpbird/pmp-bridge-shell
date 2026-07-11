# A-002 Route Authority Inventory

Baseline: `main` at `5dd049de1500ea427fa2cf395687239a19706115`

Status: **inventory complete; repair code not started**

## What counts as route authority

An object is included when it can do at least one of these jobs:

- declare an application path;
- choose among route files;
- navigate the top window;
- set an iframe or frame source;
- replace the live document;
- intercept Reload Current, Last Good, Safe Writer, Code Safety, or recovery controls;
- select a saved or candidate route;
- alter which route bytes are served through a service worker.

Objects that only observe, report, test, or route data inside Bank/Resident are listed separately as non-authorities.

## Inventory result

The recursive inventory contains **65 distinct objects**:

| Class | Count |
|---|---:|
| Declared current chain | 11 |
| Active competing route mutators | 5 |
| Conditional recovery/tool claims | 15 |
| Historic or fallback claims | 19 |
| Influence-only, observer, disabled, test, or non-app router | 13 |
| Broken absent claims | 2 |
| Unclassified | 0 |

The full record, exact blob identities, targets, classifications, and evidence are in `audit/a002-route-authority-inventory.json`.

## Declared current chain

The declared chain is:

`pmp-app-current.html`
→ `pmp-route-guardian-current-loader-v22.html`
→ `pmp-current-map-v12.json`
→ `pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html`
→ `pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html`
→ `pmp-current-inner-cleanbug-rgcontrols-v23.html`
→ `pmp-current-inner-cleanbug-rgcontrols-v4.html`
→ `pmp-current-inner-cleanbug-rgcontrols-v3.html`
→ `pmp-home-single-v6.html`
→ historical Home v6 bytes at commit `7ac7213aeeeb8bb55692a4985e0fa80a547cff4e`.

Current Map v12 declares Route Guardian v22, Reload Owner v30, and inner v23 fallback. However, nearly every layer after the map independently hard-codes the next layer. Therefore the map is not presently the sole authority.

## Five active competing mutators

1. `pmp-current-screen-pointer-v1.js`
   - Reloads through **Current Map v9**.
   - Falls back to **Reload Owner v27**.
   - Uses `location.replace`.

2. `pmp-reload-world-from-map-v1.js`
   - Does not read Current Map.
   - Sends Reload Current directly to **Route Guardian v21**.

3. `pmp-launcher-reload-current-bridge-v1.js`
   - Is loaded by the current v4 wrapper.
   - Sends legacy reload controls directly to **Route Guardian v20**.

4. `pmp-route-guardian-last-good-clean-v1.js`
   - Is loaded by current inner v23.
   - Hard-codes inner v16 as current-before-last-good.
   - Can navigate to validated saved or move-ledger HTML routes.

5. `pmp-safe-writer-current-return-fix-v1.js`
   - Is loaded by current inner v30.
   - Opens Safe Writer v14 at the top window.
   - Carries a stale `return=current-v27` contract.

These five must be treated as direct A-002 blockers.

## Current Guardian conflict

Route Guardian v22 does not obey one map only. It tries:

1. Current Map v12;
2. Current Map v11;
3. Current Map v10;
4. hard-coded Reload Owner v29 permanent gate.

That means Route Guardian v22 is a route selector with its own fallback policy, rather than a pure executor of Current Map v12.

## Other current-chain claims

- Reload Owner v30 hard-codes inner v30.
- The live-update marker declares a target, but Reload Owner reads only its revision.
- Inner v30 hard-codes inner v23.
- Inner v23 hard-codes inner v4.
- Inner v4 hard-codes inner v3.
- Inner v3 hard-codes Home v6 and separate tool pages.
- Home v6 fetches a historical file and replaces the live document.
- The service-worker cache governor can influence which exact bytes are served, but it does not choose the destination path.
- The Pass 7.5 Reload Runtime Gate controls timing only and is not itself a path selector.

## Historic claims that remain reachable

Older route objects are not merely stored history. Current or conditional actors still call them:

- Maps v11, v10, v9, and unversioned `pmp-current-map.json`;
- Route Guardians v14, v15, v17, v18, v19, v20, and v21;
- Reload Owners v27, v28, v29, v29 cache-lift, and v29 permanent gate;
- inner wrappers v2, v9, v13, v16, v24, v26, and v29;
- Last Good v1/v18, Recovery Tools v8, and Move Ledger Candidate Follow.

They must be given explicit inactive, forwarder-only, recovery-only, or quarantined status. Filename age alone is not proof of inactivity.

## Broken route claims

- `code-safety-v13.html` sends Back to Control to missing `pmp-clean-v13.html`.
- The recovery package named missing `pmp-current-reload-current-live-update-marker-v1.json`; the actual live marker is `pmp-reload-current-live-update-marker-v1.json`.

## A-001 dependency discrepancy

A-002 discovered route-capable baseline files that were not present in the five A-001 identity shards. Examples include:

- the actual live-update marker;
- Reload Owner v29 cache-lift;
- inner v9, v13, and v16;
- Route Guardian v14;
- Last Good v1/v18 and its button owner;
- Recovery Tools v8;
- Move Ledger Candidate Follow;
- Safe Writer v14 and its canonical route owner.

The completed A-001 branch was not changed. This discrepancy is now an explicit A-002 blocker: A-002 may be designed, but it cannot be certified until inherited source-identity evidence is reconciled.

## Current decision

`A002_AUTHORITY_INVENTORY_COMPLETE_NO_CODE_MODIFIED_REPAIR_NOT_STARTED`

No route code, app file, storage, cache, IndexedDB, Bank, DOM, or runtime behavior was changed during this inventory.
