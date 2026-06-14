# Packet 01.5 — Routing-Start Authorization Gate v1

STATUS: GATE DEFINED — PENDING INDEPENDENT VERIFICATION
WATCH: NONE
BLOCKERS: NONE KNOWN
ROUTING ASSIGNMENTS: NOT STARTED
APPLICABILITY CLASSIFICATION: NOT STARTED
SEMANTIC DEDUPLICATION: NOT STARTED
INDIVIDUAL RECORD CLOSURE: NOT STARTED
PACKET 04: NOT AUTHORIZED
DATE: 2026-06-14

## Purpose

This gate determines whether Packet 01.5 may move from a verified blank inventory into controlled applicability classification and owner-routing work.

Passing this gate does not itself classify or route any record.

## Required preconditions

All of the following must pass:

1. The blank routing inventory contains exactly 2750 envelopes.
2. The source split is exactly 122 baseline plus 2628 provisional.
3. All 2750 composite addresses are unique.
4. Source-to-envelope bijection is independently verified.
5. Exact original headings and bodies are independently verified.
6. Source-file, source-block, and envelope hashes are independently verified.
7. Every applicability state remains `UNCLASSIFIED` before routing starts.
8. Every routing state remains `UNROUTED` before routing starts.
9. All primary, secondary, cross-cutting-law, watch-trigger, and semantic-cluster fields remain blank.
10. Deleted records, merged source records, and closed records remain zero.

## Immutable fields after authorization

The following envelope fields are source evidence and may never be rewritten by classification or routing:

- `composite_address`
- `source_set`
- `source_path`
- `source_pass`
- `source_file_hash`
- `source_record_ordinal`
- `original_identifier`
- `original_heading`
- `original_body`
- `source_block_hash`
- `harm_text`
- `overlap_text`
- `legacy_exception_codes`
- `normalization_version`

Any authorized change must preserve the pre-change envelope and produce a new auditable envelope hash.

## Authorized sequence

Routing work must proceed in this order:

### Phase A — Applicability classification

Each envelope receives exactly one of:

- `CURRENT_DEFECT`
- `ACTIVE_CONDITIONAL_RISK`
- `DORMANT_FUTURE_RISK`
- `OUT_OF_SCOPE_CANDIDATE`

Every classification requires record-specific evidence. A discovered real-world risk is not a current PMP Current defect merely because it exists in the discovery library.

### Phase B — Destination preparation

Destination candidates may be prepared only after Phase A is complete for that envelope.

- `CURRENT_DEFECT` and `ACTIVE_CONDITIONAL_RISK` require an identified current or planned project contact path before owner routing.
- `DORMANT_FUTURE_RISK` may receive a dormant watch location and reopening trigger, but not an active owner assignment without a later contact-path event.
- `OUT_OF_SCOPE_CANDIDATE` remains preserved, unrouted to active owners, and reviewable; it may not be deleted.

### Phase C — Owner-routing verification

A destination is not authoritative until an independent verifier confirms:

- the applicability evidence supports the state;
- the destination exists in the governing packet map;
- the destination does not alter source wording;
- secondary and cross-cutting references are non-destructive;
- no source envelope was lost, replaced, merged, or closed.

## Evidence requirement

Every applicability decision must contain at least one evidence entry with:

- evidence identifier;
- evidence type: `CURRENT_CONTACT`, `PLANNED_CONTACT`, `ABSENT_CONTACT`, or `SCOPE_EXCLUSION`;
- source path or governing record;
- source hash or stable reference;
- concise contact-path explanation;
- decision rationale.

A state may not be inferred from the discovery domain name alone.

## Batch transaction law

- Maximum batch size: 100 envelopes.
- Every batch starts from a verified parent inventory hash.
- Every batch writes to a new versioned inventory; the parent remains preserved.
- Every batch must pass count equality, address equality, immutable-field equality, and hash-chain verification.
- A failed batch is rejected in full; partial acceptance is prohibited.
- The blank inventory remains the rollback point until all routing work is independently accepted.

## Semantic comparison law

Semantic clusters may be added only as references.

They may not:

- replace source envelopes;
- collapse counts;
- rewrite original wording;
- delete repeated identifiers;
- close records;
- become routing destinations by themselves.

## Authorization boundary

A passing result authorizes:

- Phase A applicability classification;
- preparation of evidence-backed destination candidates;
- non-destructive semantic-cluster references;
- batch-level independent verification.

A passing result does not authorize:

- destructive semantic deduplication;
- deletion;
- individual record closure;
- Packet 04;
- treating all 2750 records as present defects;
- routing an envelope without its required applicability evidence.

## Pass condition

The gate passes only when an independent mechanical verifier confirms all preconditions and all control laws above.

END PACKET 01.5 — ROUTING-START AUTHORIZATION GATE v1
