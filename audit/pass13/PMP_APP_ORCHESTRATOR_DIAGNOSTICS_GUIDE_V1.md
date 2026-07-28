# App Orchestrator diagnostics guide

## Evidence order

1. Read the final completion pointer and pass-closure ledger.
2. Verify GitHub main and clean mirror commit identity.
3. Verify Current Map and A-003 manifest/seal/bootstrap identities.
4. Identify the single owner of the failing route, section, helper, Bank, or
   Continuous Run surface.
5. Read the affected pass report, receipt, deterministic test, and workflow
   artifact before changing source.

## Required distinctions

- **Observed:** directly produced by a deterministic test, bounded observation,
  GitHub workflow, user confirmation, or exact byte/hash check.
- **Inferred:** conclusion derived from named observed evidence.
- **Blocked:** action intentionally unavailable because exact authority is
  absent.
- **Failed:** attempted action did not satisfy its gate and remains evidence.
- **Superseded:** later repair replaces the operative state but never erases
  the historical result.

## Core fault routes

- Route or startup: Passes 3–6.
- Owner or helper conflict: Passes 7–8.
- Bank/Continuous Run ordering, duplication, flicker, or leakage: Passes 9–10.
- Delete, archive, transaction, rollback, or preservation: Pass 11.
- Migration inventory, dry run, shadow compare, rollback, or authority gate:
  Pass 12.
- Cross-pass evidence, release identity, packages, or maintenance: Pass 13.

Every repair must add or update the diagnostic matrix, deterministic evidence,
receipt, workflow preservation path, and exact next-move record.
# New-chat safety handoff

Open **Diagnostics → App Orchestrator Status**, then use
**Copy New Chat Safe Handoff**. The button copies one bounded complete packet
or downloads one verified ZIP when the packet is too large.

Treat `pmp-app-orchestrator-ownership-registry-v1.json` as the current
ownership authority. Preserved Pass 7/8 helper and owner snapshots are
historical evidence and must not override this registry.
