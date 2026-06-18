# Automated Plan Controller Status v1

Status: **HARDENED AND TESTED — EXECUTION LOCKED — PASS 003 NOT STARTED**

Continuity remains unchanged:

- authoritative build base: `dc1c2dcbe35374532f581c62c3996648ad34e088`
- last completed and verified unit: `pass_002`
- next declared unit: `pass_003`
- Pass 003 remains uncompiled, disabled, and not started
- the first real Pass 003 run still requires explicit supervision

Hardening added:

- Hosted GitHub Models inference is blocked until repository variables freshly attest that paid usage is disabled for the personal account billing scope.
- The interface no longer claims `$0` while that account-level setting is unverified.
- Model proposals execute only inside Docker with no network, a read-only root filesystem, dropped capabilities, no-new-privileges, process/memory/CPU limits, and one designated writable workspace.
- Verification receipts no longer contain or authorize a `runtime_candidate`.
- The persistence job independently reconstructs the permitted transition from the current checkpoint, reviewed unit, decision, transport, proposal hashes, and verification receipt.
- Exact field sets, request identity, checkpoint sequence, next-unit progression, proposal hashes, and runtime-only write paths are revalidated before persistence.
- Adversarial coverage includes paid-usage configuration, stale attestation, artifact tampering, unexpected runtime state, checkpoint jumps, writes outside the workspace, network access, and surviving background processes.
- Ten legacy Pass 002 workflows are restricted to their own family files so unrelated controller changes do not invoke historical receipt regeneration.
- A complete status-only prepare → verify → persist workflow test proves that no model is called and the Pass 002/Pass 003 boundary remains unchanged.

Current zero-cost assurance:

- account-level GitHub Models paid-usage setting: **UNVERIFIED**
- Hosted Free execution: **BLOCKED UNTIL VERIFIED**
- paid API keys and paid fallback: forbidden
- automatic cost escalation: forbidden

Authority remains separated:

- inference: model read only, proposal only, no repository write
- verification: read only, isolated container execution only
- persistence: runtime branch only, no model access, no main write, no merge

This draft does not activate execution, compile Pass 003, start Pass 003, or authorize merging.
