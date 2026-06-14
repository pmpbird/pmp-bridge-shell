# PMP Current — Continuation Protocol v1

STATUS: ACTIVE
DATE: 2026-06-14

## Purpose

Prevent loss when work moves to a new chat. No earlier packet needs to be rewritten.

## New-chat startup set

For a finished previous packet and a new current packet, provide:

1. Note 00 — Project Start Card
2. previous packet completion receipt
3. current packet note
4. `audit/PMP-Current-Active-Work-Card.md`

Then say:

`Work only the active packet. Verify prerequisites and the Active Work Card. Continue from NEXT ACTION. Do not restart completed work. Print a new checkpoint before chat transfer and a completion receipt only when the packet actually passes.`

## Active Work Card rule

The Active Work Card is the only live mid-packet continuation record. It must contain:

- active packet and status
- prerequisite receipts verified
- exact work already completed
- outputs and evidence created
- decisions made
- limitations currently owned by the packet
- unresolved questions, watches, and blockers
- exact next action
- repository paths and commit identities when applicable

Update it after every meaningful completed step and before leaving a chat.

## Completion transition

When the packet passes:

1. create final outputs and evidence
2. create the completion receipt
3. update the Master Status Ledger
4. replace the Active Work Card with the next authorized packet's NOT STARTED card
5. preserve the old card in the completed packet's evidence package when useful

## Limitation enforcement

A later packet cannot safely pass merely because it was worked on. Its receipt must account for every limitation assigned to that packet by stating one of these:

- implemented and proven
- safely carried forward under a named owner and proof path
- permanently limited under a continuing watch
- blocked

No limitation may disappear from the permanent register or Master Status Ledger without a valid closure receipt.

END PMP CURRENT — CONTINUATION PROTOCOL v1
