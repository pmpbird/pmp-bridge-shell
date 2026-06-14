# Packet 01.5 — Discovery Working Register v1

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: INTENTIONALLY NOT STARTED
DATE OPENED: 2026-06-14

## Discovery law

- Preserve the existing 122-record baseline.
- Do not assign packet owners during this phase.
- Add new records only when they are meaningfully distinct.
- Mark overlaps for deduplication; do not erase source records.
- Do not claim saturation until multiple breaker passes stop finding new material.
- Do not begin Packet 04 while Packet 01.5 discovery remains open.

## Baseline

Existing preserved records: 122

Source baseline:
`pmp-current-permanent-limitation-register-v3-final.json`

## Discovery Pass 01 — Packet 01.5 self-failure risks

These are provisional permanent records. Ownership fields remain blank until the later routing phase.

### REG-001 — Register size and context truncation

The complete Packet 01.5 register may become too large for a chat, model context, mobile paste operation, or single document view. A new chat may receive only part of it without realizing records were omitted.

HARM:
Mandatory future work can disappear from the current packet load.

EVIDENCE NEEDED:
Measured size limits, full-load verification, truncation detection, and a safe segmented/indexed reading method.

### REG-002 — Partial copy or paste without detection

Manual copying from Apple Notes may omit a section, stop early, alter formatting, or paste only the visible selection.

HARM:
The receiving chat may falsely believe the full routing register was supplied.

EVIDENCE NEEDED:
Record count, section count, digest, opening marker, closing marker, and completeness receipt.

### REG-003 — Stale Packet 01.5 version

Several copies may exist in Apple Notes, Files, ZIPs, GitHub, or prior chats. A future chat may read an older register.

HARM:
New limitations, corrections, closures, or reopening triggers can be missed.

EVIDENCE NEEDED:
Active-version pointer, supersession rule, version identity, digest, and stale-copy warning.

### REG-004 — Packet identity and alias mismatch

The same packet may be written as 1.5, 01.5, Packet 1.5, Packet 01.5, 06.5, or by name only. Ownership searches can miss records when labels differ.

HARM:
Applicable obligations may not load into the current packet.

EVIDENCE NEEDED:
Canonical packet IDs, alias table, and exact-match plus normalized-match audit.

### REG-005 — Human-language search misses

A chat may search Packet 01.5 only for the current packet number and miss indirect dependencies, linked records, continuing watches, or records whose owner is expressed in prose.

HARM:
The current packet may pass with incomplete obligations.

EVIDENCE NEEDED:
Machine-readable owner fields, dependency links, reverse index, and packet-load report.

### REG-006 — No packet-specific obligation index

A large master register without a generated per-packet index requires each chat to rediscover its obligations manually.

HARM:
Different chats can load different work from the same register.

EVIDENCE NEEDED:
Deterministic per-packet obligation lists generated from the active register.

### REG-007 — Conflicting or circular ownership

Two records may assign incompatible owners, require each other first, or form a dependency cycle.

HARM:
Work can stall, loop, or be falsely carried forward forever.

EVIDENCE NEEDED:
Owner conflict audit, dependency-cycle detection, and explicit resolution state.

### REG-008 — Later discoveries fail to propagate

A new limitation discovered during a later packet may be recorded only in that chat, receipt, or local note and never added to the active Packet 01.5 register.

HARM:
The issue disappears when the project changes chats.

EVIDENCE NEEDED:
Mandatory discovery-to-register write-back, acknowledgement, and next-start verification.

### REG-009 — Packet closeout does not reconcile its loaded records

A packet may finish its main task but fail to state what happened to every Packet 01.5 record it loaded.

HARM:
Open limitations can silently disappear or be mistaken for closed.

EVIDENCE NEEDED:
Start-load inventory, end-of-packet reconciliation, and receipt-level disposition for every loaded ID.

### REG-010 — Register corruption or silent edit

A Packet 01.5 record may be accidentally edited, merged, reordered, shortened, or deleted without a visible change history.

HARM:
Requirements, evidence, owners, watches, or reopening triggers can be lost.

EVIDENCE NEEDED:
Append-preserving history, content digests, change receipts, merge receipts, and corruption detection.

## Pass 01 result

New provisional records: 10
Total preserved plus provisional: 132
Routing decisions made: 0
Records closed: 0
Discovery saturation: NOT REACHED

## Next discovery pass

Security, privacy, malicious-input, secret-leakage, imported-file, and supply-chain failure modes.

END PACKET 01.5 — DISCOVERY WORKING REGISTER v1
