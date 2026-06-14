# Packet 01.5 — Routing Preparation Gate v1

STATUS: GATE DESIGNED
ROUTING ASSIGNMENTS: BLOCKED UNTIL INDEPENDENT VERIFICATION PASSES
SEMANTIC DEDUPLICATION: NOT STARTED
INDIVIDUAL RECORD CLOSURE: NOT STARTED
DATE: 2026-06-14

This gate defines the only permitted path from saturated broad discovery into routing.

It prepares routing without assigning any owner, merging any candidate, deleting any source wording, or closing any record.

## 1. Protected source sets

### 1.1 Preserved baseline

- Required source identity: `pmp-current-permanent-limitation-register-v3-final.json`
- Certified preserved count: 122
- Requirement before routing: the exact source artifact must be available to the verifier and frozen by content hash.

### 1.2 Provisional discovery set

- Working-register source: `audit/Packet_01.5_Discovery_Working_Register_v1.md`
- Discovery-pass sources: `audit/Packet_01.5_Discovery_Pass_02_*.md` through `audit/Packet_01.5_Discovery_Pass_69_*.md`
- Mechanically audited source-file count: 69
- Mechanically audited provisional headings: 2628

### 1.3 Certified combined source count

- Baseline: 122
- Provisional: 2628
- Combined: 2750

No routing dataset is valid unless it contains exactly one preserved record envelope for every one of these 2750 source records.

## 2. Stable composite addressing

### 2.1 Baseline address

Each baseline record receives:

`P01.5::B::<source-order-ordinal>`

Rules:

- ordinal is zero-padded to four digits;
- order is the immutable order in the frozen baseline source artifact;
- original baseline identifier remains a separate preserved field;
- the address cannot be reused, renumbered, or changed after the baseline hash is frozen.

Example:

`P01.5::B::0047`

### 2.2 Provisional address

Each provisional record receives:

`P01.5::P<pass-number>::<record-identifier>`

Rules:

- pass number is zero-padded to three digits;
- record identifier is copied exactly from the source heading;
- repeated identifiers in different passes are allowed because the pass-qualified address remains unique;
- repeated identifiers inside the same pass fail the gate;
- a malformed or missing record identifier fails the gate.

Example:

`P01.5::P041::GUARD-001`

### 2.3 Source identity fields

Every routing envelope must preserve:

- composite address
- source set: `BASELINE` or `PROVISIONAL`
- source file path
- source-file cryptographic hash
- source-relative record ordinal
- original record identifier
- original heading
- exact original body
- exact source block hash

## 3. Lossless record envelope

Every normalized routing record must contain these fields before routing begins:

- `composite_address`
- `source_set`
- `source_path`
- `source_file_hash`
- `source_record_ordinal`
- `original_identifier`
- `original_heading`
- `original_body`
- `source_block_hash`
- `harm_text`
- `overlap_text`
- `legacy_exception_codes`
- `applicability_state`
- `applicability_evidence`
- `routing_state`
- `primary_destination`
- `secondary_destinations`
- `cross_cutting_laws`
- `watch_triggers`
- `semantic_cluster_ids`
- `normalization_version`

At gate entry:

- `routing_state` must equal `UNROUTED`;
- destination fields must remain empty;
- applicability state may remain `UNCLASSIFIED` until the classification stage begins;
- original wording fields are immutable.

## 4. Applicability classification

Applicability is independent of routing destination.

Every record must receive exactly one state:

1. `CURRENT_DEFECT`
2. `ACTIVE_CONDITIONAL_RISK`
3. `DORMANT_FUTURE_RISK`
4. `OUT_OF_SCOPE_CANDIDATE`

Activation rule:

A discovered candidate may become a current requirement only when evidence shows an actual or planned PMP Current/Resident contact path through capability, data, advice, decision, storage, coordination, routing, governance, or dependency.

Prohibited inference:

Discovery inside a real-world domain does not, by itself, prove a current app limitation.

## 5. Permitted destination classes

Routing may later use these nonexclusive destination types:

- `PRIMARY_OWNER_PACKET`
- `SECONDARY_OWNER_PACKET`
- `CROSS_CUTTING_LAW`
- `CONTINUING_WATCH`
- `NO_CURRENT_PROJECT_CONTACT`
- `OUT_OF_SCOPE_HOLD`
- `DISCOVERY_REOPENING_TRIGGER`

Destination and applicability must remain separate fields.

A dormant or no-contact record may still have a future owner candidate, but it cannot be represented as an active obligation.

## 6. Non-destructive semantic comparison

Semantic comparison may identify:

- exact duplicates
- probable semantic duplicates
- parent/child relationships
- overlapping harms
- shared causes
- shared proof requirements
- cross-cutting laws
- sector-specific variants

Semantic comparison must not:

- delete a source record;
- overwrite original wording;
- collapse addresses;
- select a canonical survivor without an auditable decision;
- change applicability or routing automatically;
- treat similar wording as proof of identical obligations.

Every semantic group must preserve all member addresses and the reason for grouping.

## 7. Mechanical count and structural proof

The gate verifier must independently count source headings and ignore hand-maintained totals.

Required proof:

- baseline artifact exists and contains exactly 122 ordered records;
- provisional source set contains exactly 69 files;
- provisional source set contains exactly 2628 record headings;
- combined inventory contains exactly 2750 record envelopes;
- every source record produces exactly one envelope;
- no envelope lacks a source address;
- no composite address repeats;
- no source block is omitted;
- no source block maps to more than one envelope;
- no malformed provisional heading exists;
- every provisional record contains `HARM:`;
- every provisional record contains `OVERLAP TO CHECK:` or is listed in the frozen legacy exception ledger.

Frozen legacy structural exceptions:

- Pass 01 / REG-001 through REG-010 lack `OVERLAP TO CHECK:` and must be preserved with exception code `LEGACY-P01-NO-OVERLAP`.

Frozen declared-count corrections:

- Pass 04: actual 32, historical declaration 29
- Pass 06: actual 36, historical declaration 35
- Pass 09: actual 44, historical declaration 42
- Pass 13: actual 44, historical declaration 43
- Pass 34: actual 47, historical declaration 42

Mechanical source counts govern; historical declarations remain preserved as evidence.

## 8. Lossless normalization proof

Normalization passes only when all of the following are proven:

1. **Bijection:** each source record maps to one and only one normalized envelope.
2. **Reverse reconstruction:** each envelope can reproduce the exact original heading and body.
3. **Hash equality:** reconstructed source blocks match their frozen source-block hashes.
4. **Count equality:** `122 + 2628 = 2750` envelopes.
5. **Address uniqueness:** all 2750 composite addresses are unique.
6. **No destructive merge:** semantic groups contain references, never replacement records.
7. **Exception preservation:** all historical structural and count exceptions remain explicitly represented.
8. **Blank-routing proof:** no owner or destination assignment exists at the moment the preparation gate opens.

## 9. Independent verification requirements

A verifier independent from the gate-design step must review:

- the exact frozen source set;
- the mechanical integrity audit;
- the baseline artifact and hash;
- composite-address generation;
- exception ledger;
- envelope schema;
- applicability-state separation;
- destination taxonomy;
- bijection and reverse-reconstruction proof;
- routing fields remaining blank.

The verifier returns only:

- `PASS — ROUTING PREPARATION GATE OPEN`, or
- `FAIL — ROUTING REMAINS BLOCKED`, with exact blockers.

## 10. Gate opening effect

A passing gate authorizes preparation of the routing inventory and classification workflow.

It does not itself authorize:

- owner assignment;
- semantic merge;
- deletion;
- individual closure;
- Packet 04.

A separate routing-start authorization is required after the verified inventory exists.

## 11. Current gate state

- Gate design: COMPLETE
- Provisional mechanical proof: AVAILABLE
- Baseline source artifact proof: REQUIRED
- Independent verification: REQUIRED
- Routing assignments: BLOCKED

END PACKET 01.5 — ROUTING PREPARATION GATE v1
