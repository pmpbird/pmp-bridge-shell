# Bug Bank Empty-State Audit — 2026-07-28

## Status

AUDIT COMPLETE — REPAIR NOT PERFORMED

## User-observed symptom

The Bug Bank previously showed bug entries. The current Bug Bank view is empty.

## Proven current route

`pmp-bug-memory-route-fix.js` redirects Bug Memory actions to `bm.html`.

`bm.html` is a private Bug Memory room. It provides:

- Save Bug Memory
- Load Memory from Notes
- Bug Lab
- session-only pasted memory

It does not render the live Bug Catalog and does not read a Bug Bank record list.

## Existing bug-catalog storage

`pmp-bug-catalog-engine-v1.js` defines these localStorage namespaces:

- `pmp_bug_cards_loaded_v1`
- `pmp_bug_catalog_live_v1`
- `pmp_bug_catalog_meta_v1`

The engine can parse, save, load, and clear a bug catalog. Repository search found no current renderer that reads `pmp_bug_catalog_live_v1` to populate the visible Bug Bank.

## Bank inventory finding

`pmp-bank-inventory-readonly-projection-v1.js` declares `bug_memory: 'Bug Bank'`, but its namespace rules contain no record whose `owning_bank` is `bug_memory`.

Therefore the projection creates the Bug Bank container but assigns it zero source namespaces. The visible inventory can truthfully return an empty Bug Bank even when older bug data may still exist elsewhere.

## Root cause

The current app has a disconnected data path:

1. A Bug Bank name/container exists.
2. Bug catalog storage keys exist.
3. The current Bug Memory route opens `bm.html`, which does not display the catalog.
4. The bank inventory does not register the bug catalog namespaces as Bug Bank sources.
5. No current renderer was found that reads the live catalog key into the Bug Bank view.

The empty list is therefore caused by missing source registration and missing render binding, not by proven deletion.

## What is not proven

This repository-only audit cannot inspect the user's live browser localStorage values. It does not prove whether old records are still present, empty, or were previously cleared.

No code path inspected here proves that the old records were intentionally deleted.

## Safe repair direction

The next repair should be non-destructive and read-only first:

1. Register the three existing bug-catalog namespaces with the Bug Bank inventory.
2. Add a Bug Bank renderer that reads through `PMPBugCatalogEngine.loadCatalog()` or the owner-approved equivalent.
3. Display an explicit distinction between:
   - catalog missing,
   - catalog present with zero cards,
   - catalog present with cards,
   - malformed/quarantined catalog.
4. Do not call `clearCatalog()`.
5. Do not migrate, rewrite, or delete stored bug records.
6. Add a live-browser test using seeded disposable storage, not the user's real records.

## Effects of this audit

- app behavior changed: false
- stored bug data changed: false
- routes changed: false
- storage migration performed: false
- deletion performed: false
