# Packet 01.5 — Discovery Pass 16

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for search failure, retrieval incompleteness, indexing drift, ranking bias, missing neighboring context, duplicate suppression errors, stale embeddings, archive invisibility, and knowledge-base poisoning.

## Provisional records

### RETR-001 — Exact-name search misses aliases and renamed records

Search may require the current filename, packet number, prefix, spelling, or identifier even when the same object has older names and aliases.

HARM: authoritative records appear absent and are recreated or ignored.

OVERLAP TO CHECK: REG-004, REG-005.

### RETR-002 — Semantic search misses literal identifiers

Embedding or natural-language retrieval may overlook exact hashes, IDs, filenames, error codes, branch names, and short technical terms.

HARM: the decisive record is absent despite a seemingly relevant result set.

OVERLAP TO CHECK: REG-005, CTX-007.

### RETR-003 — Literal search misses paraphrases and indirect obligations

Keyword search may fail when a packet, limitation, or requirement is described without its exact vocabulary.

HARM: related obligations remain undiscovered.

OVERLAP TO CHECK: REG-005, HANDOFF-001.

### RETR-004 — Retrieval stops after the first plausible result

A system may accept one matching record without checking supersession, exceptions, conflicts, newer versions, or neighboring evidence.

HARM: a locally plausible source overrides the complete project state.

OVERLAP TO CHECK: AIH-002, CTX-007.

### RETR-005 — Result limits silently omit relevant records

Top-k retrieval, page limits, token budgets, connector caps, or timeouts may truncate the result set.

HARM: incomplete search is mistaken for complete coverage.

OVERLAP TO CHECK: API-003, AIH-006.

### RETR-006 — Query wording changes which truth is retrieved

Small changes in phrasing, language, tense, packet name, or risk framing may return different records.

HARM: project decisions depend on prompt wording rather than authority.

OVERLAP TO CHECK: CTX-004, ADV-005.

### RETR-007 — Search scope excludes a relevant source

The query may search GitHub but not Notes, Files, current chat, archives, provider records, or prior packets.

HARM: the source of truth remains outside the chosen search boundary.

OVERLAP TO CHECK: STATE-002, REG-003.

### RETR-008 — Neighboring context is not retrieved

A result chunk may omit table headers, definitions, supersession notes, exception clauses, source identity, or continuation lines.

HARM: accurate text is interpreted incorrectly.

OVERLAP TO CHECK: CTX-007, AIH-002.

### RETR-009 — Search result identity is detached from source identity

A snippet may not preserve exact file, version, line range, commit, packet state, or retrieval time.

HARM: evidence cannot be verified or may be applied to the wrong source.

OVERLAP TO CHECK: PROOFCHAIN-001, OBS-002.

### RETR-010 — Failed retrieval degrades into unsupported model memory

When search returns nothing or errors, the system may answer from prior context or general knowledge without clearly marking the change in evidence basis.

HARM: missing evidence becomes confident invention.

OVERLAP TO CHECK: AIH-001, CTX-005.

### INDEX-001 — Index update lags behind source changes

New, edited, moved, superseded, or deleted records may not appear promptly in search.

HARM: current truth remains invisible while stale truth remains discoverable.

OVERLAP TO CHECK: SEM-005, API-008.

### INDEX-002 — Deleted or superseded content remains searchable

Old chunks, embeddings, caches, and indexes may survive after the source is removed or marked historical.

HARM: obsolete authority continues influencing decisions.

OVERLAP TO CHECK: RET-002, UI-017.

### INDEX-003 — Current content disappears after reindexing

Parser changes, unsupported format, indexing errors, permissions, size limits, or malformed sections may drop valid records.

HARM: authoritative material vanishes without a source deletion.

OVERLAP TO CHECK: OBS-001, API-003.

### INDEX-004 — Chunk boundaries split one obligation into misleading fragments

A requirement, condition, harm, exception, and owner note may be indexed separately.

HARM: retrieval returns an incomplete or reversed meaning.

OVERLAP TO CHECK: CTX-003, RETR-008.

### INDEX-005 — Metadata and content indexes disagree

Filename, date, status, packet, owner, tags, and body text may be updated through different pipelines.

HARM: filtering hides the correct document or labels a stale document current.

OVERLAP TO CHECK: SEM-005, STATE-003.

### INDEX-006 — Binary, image, table, code, or attachment content is under-indexed

Important information may exist in screenshots, diagrams, ZIPs, manifests, tables, or structured files that text indexing only partially reads.

HARM: search reports no evidence even though the artifact contains it.

OVERLAP TO CHECK: BKP-001, API-003.

### INDEX-007 — Access-control filtering leaks or hides records incorrectly

An index may expose snippets from unauthorized sources or suppress sources the user is allowed to access.

HARM: privacy is breached or legitimate evidence is unavailable.

OVERLAP TO CHECK: AUTHZ-002, CORS-001.

### INDEX-008 — Reindexing changes stable result identity

Chunk IDs, document IDs, ranking keys, or citations may be regenerated after parsing or embedding updates.

HARM: old receipts and references no longer point to the same evidence.

OVERLAP TO CHECK: REL-001, PROOFCHAIN-003.

### RANK-001 — Recency outranks authority

A newer comment, draft, duplicate, support note, or experimental file may rank above a permanent law or verified receipt.

HARM: current-looking content overrides governing truth.

OVERLAP TO CHECK: CTX-002, GOV-005.

### RANK-002 — Popularity and repetition outrank correctness

Frequently copied, linked, quoted, or repeated text may rank higher than a quiet correction or exception.

HARM: duplication manufactures authority.

OVERLAP TO CHECK: CTX-006, KB-004.

### RANK-003 — Query-language match outranks semantic authority

A record that uses the same words as the query may outrank a more authoritative record using different terminology.

HARM: wording similarity replaces source quality.

OVERLAP TO CHECK: RETR-003, RETR-006.

### RANK-004 — Long or richly formatted documents dominate retrieval

Documents with repeated headings, metadata, summaries, and examples may crowd out shorter decisive records.

HARM: verbosity changes apparent importance.

OVERLAP TO CHECK: REG-001, MEAS-001.

### RANK-005 — Ranking hides disagreement

The system may show only the top answer and omit credible conflicting records, unresolved disputes, or competing versions.

HARM: uncertainty is converted into false consensus.

OVERLAP TO CHECK: AGENT-001, AUTH-005.

### RANK-006 — Personalized or contextual ranking is unreproducible

Prior searches, current chat, user profile, location, or hidden personalization may alter results.

HARM: another reviewer cannot reproduce the evidence set.

OVERLAP TO CHECK: CTX-005, PROOFCHAIN-008.

### RANK-007 — Search confidence is inferred from rank position

The first result may be treated as highly certain even when all scores are weak or nearly tied.

HARM: low-confidence retrieval becomes confident project truth.

OVERLAP TO CHECK: AIH-004, MEAS-006.

### EMBED-001 — Embedding model changes alter semantic neighborhoods

Re-embedding with a new model or version may change which records are considered similar.

HARM: search behavior changes without source changes.

OVERLAP TO CHECK: PROV-001, SELF-004.

### EMBED-002 — Stale embeddings survive edited content

The source may be corrected while the vector representation still reflects the old meaning.

HARM: retrieval continues surfacing superseded concepts.

OVERLAP TO CHECK: INDEX-001, SEM-005.

### EMBED-003 — One embedding compresses several conflicting sections

A whole document or large chunk may contain current, historical, rejected, and hypothetical content in one vector.

HARM: search cannot distinguish authority or state.

OVERLAP TO CHECK: UI-017, INDEX-004.

### EMBED-004 — Multilingual and specialized vocabulary retrieval is uneven

Technical names, abbreviations, faith framing, project-specific terms, and non-English text may embed poorly or inconsistently.

HARM: some concepts become systematically harder to retrieve.

OVERLAP TO CHECK: LOC-003, RETR-002.

### EMBED-005 — Adversarial text manipulates semantic similarity

Repeated keywords, hidden text, irrelevant definitions, or crafted phrasing may pull malicious content toward trusted queries.

HARM: poisoned records rank as highly relevant.

OVERLAP TO CHECK: ADV-003, KB-001.

### EMBED-006 — Embedding and reranking expose private content to external providers

Source text, queries, retrieved chunks, and metadata may be sent to third-party models or services.

HARM: private project data leaves the intended environment.

OVERLAP TO CHECK: MIN-003, PRIV-003.

### ARCHIVE-001 — Archived material is excluded without checking active obligations

Moving a packet, issue, branch, or Note to history may hide unresolved limitations and watches contained inside it.

HARM: archival state erases future work.

OVERLAP TO CHECK: HANDOFF-001, UI-017.

### ARCHIVE-002 — Archive search differs from active search

Historical repositories, ZIPs, branches, old Notes, and exports may require separate tools or exact filenames.

HARM: prior evidence cannot be found during audit or recovery.

OVERLAP TO CHECK: RETR-007, REG-004.

### ARCHIVE-003 — Compressed or encrypted archives are invisible to indexing

ZIPs, encrypted backups, binary bundles, and offline copies may exist but remain unsearchable until manually opened.

HARM: preserved information is practically undiscoverable.

OVERLAP TO CHECK: INDEX-006, CRYPTO-004.

### ARCHIVE-004 — Archive restoration reintroduces stale index entries

Importing an old backup or bundle may recreate obsolete documents, embeddings, aliases, and status records.

HARM: historical content returns as current search truth.

OVERLAP TO CHECK: RET-003, SYNC-004.

### ARCHIVE-005 — Archive retention preserves data but loses navigation

Files may survive while manifests, indexes, folder structure, aliases, and cross-links disappear.

HARM: the archive is intact but unusable.

OVERLAP TO CHECK: LOCK-005, PORT-003.

### KB-001 — Malicious or false content is admitted into the knowledge base

Imported files, issue text, support notes, model output, Bug Memory, or generated summaries may enter retrieval without trust classification.

HARM: future reasoning repeatedly retrieves poisoned material.

OVERLAP TO CHECK: MEM-001, ADV-001.

### KB-002 — Speculation and verified fact share the same retrieval status

Hypotheses, examples, rejected ideas, predictions, and confirmed observations may be indexed identically.

HARM: tentative content becomes operational truth.

OVERLAP TO CHECK: AIH-003, DOC-001.

### KB-003 — Correction does not invalidate dependent summaries and answers

A false source may be fixed while derived notes, embeddings, caches, tests, routes, and Bug Memory remain unchanged.

HARM: the knowledge base continues reproducing the corrected error.

OVERLAP TO CHECK: SEM-005, MEM-002.

### KB-004 — Repetition amplifies one source into apparent consensus

Copied text across receipts, packets, summaries, issues, and notes may be counted as many independent confirmations.

HARM: one unsupported claim acquires false weight.

OVERLAP TO CHECK: AGENT-003, RANK-002.

### KB-005 — Source trust is inherited through quotation

A trusted packet or summary may quote untrusted content without preserving the original source and confidence.

HARM: laundering through a trusted document raises poisoned content’s authority.

OVERLAP TO CHECK: AGENT-003, AIH-002.

### KB-006 — Knowledge-base health is not audited independently

The project may not test retrieval completeness, stale content, poisoned records, archive coverage, contradictory sources, and citation validity over time.

HARM: silent knowledge corruption becomes a permanent reasoning layer.

OVERLAP TO CHECK: INCDET-005, PROOFCHAIN-006.

## Pass 16 result

New provisional records: 42
Routing decisions made: 0
Records closed: 0
Deduplication required later: Yes
Discovery saturation: NOT REACHED

Combined working total:
- Existing baseline: 122
- Pass 01 provisional: 10
- Pass 02 provisional: 20
- Pass 03 provisional: 21
- Pass 04 provisional: 29
- Pass 05 provisional: 33
- Pass 06 provisional: 35
- Pass 07 provisional: 40
- Pass 08 provisional: 44
- Pass 09 provisional: 42
- Pass 10 provisional: 43
- Pass 11 provisional: 44
- Pass 12 provisional: 43
- Pass 13 provisional: 43
- Pass 14 provisional: 42
- Pass 15 provisional: 42
- Pass 16 provisional: 42
- Current preserved plus provisional: 695

NEXT DISCOVERY PASS:
Scheduling, deadlines, clocks, recurring work, dependency timing, queue starvation, priority inversion, abandoned tasks, and time-based authority expiry.

END PACKET 01.5 — DISCOVERY PASS 16
