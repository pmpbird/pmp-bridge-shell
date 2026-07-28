# App Orchestrator operator guide

## Normal use

1. Open the deployed PMP app from the verified GitHub Pages release.
2. Let Route Guardian resolve the canonical current app.
3. Confirm the app reaches its normal ready state before using Bank or
   Continuous Run.
4. Use Bank records through their owning Bank interface. Continuous Run levels
   belong only in Continuous Run Bank.
5. Use **Archive Selected Packet** for Connections records. Archive is
   recoverable and does not delete the binary payload.

## Move safely to a new ChatGPT chat

1. Open **Diagnostics**.
2. Open **App Orchestrator Status**.
3. Tap **Copy New Chat Safe Handoff** once.
4. Paste the copied packet into the new chat. If the packet grows beyond the
   copy limit, the same button downloads one small self-verifying ZIP instead.

The packet includes the current ownership registry, authority and maintenance
state, Current Map, Active Path Discovery reports, diagnostics, required
checks, and exact safety boundaries. It intentionally excludes persisted user
data.

## Before trusting a changed release

- Confirm GitHub main, the Current Map, A-003 manifest, A-003 seal, bootstrap
  manifest anchor, and clean laptop mirror agree.
- Require the affected deterministic suite and permanent no-blind-flying gate
  to pass.
- Require the PR head used by CI to equal the head that is merged.
- Preserve the resulting checkpoint ZIP and SHA-256 sidecar.

## Stop conditions

Stop and preserve evidence if the app shows repeated route changes, duplicate
owners, helper ownership escalation, Continuous Run levels in ordinary Bank,
flickering or out-of-order levels, unexpected deletion, integrity mismatch,
partial migration, stale-version mutation, or an authority replay.

Do not improvise a retry for a consumed observation or formal-proof event.
