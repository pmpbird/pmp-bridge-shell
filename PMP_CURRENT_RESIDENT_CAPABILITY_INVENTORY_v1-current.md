BEGIN PMP CURRENT — RESIDENT CURRENT CAPABILITY INVENTORY

CARD NAME:
PMP Current — Resident Current Capability Inventory

CARD VERSION:
v1-current

SAVE STATUS:
save as one complete planning/support note

ROLE:
This inventory records the Resident capabilities that already exist in PMP Current before the Resident Safe Change Architecture is designed or implemented.

Its purpose is to stop future work from accidentally rebuilding Resident from assumptions, duplicating working tools, breaking existing memory, or silently subtracting capabilities.

This inventory is grounded in direct repository review of the current known Resident surfaces, hidden support files, private Bug Memory tools, Safe Writer, Code Safety, Inventory Eyes, and X-Ray support.

This inventory is not proof that Resident can already code the app independently.
It is not the complete Resident architecture.
It is not permission to rewrite the frozen current app.
It is not proof that every historical Resident file has been fully audited.

CURRENT INVENTORY STATE:
current known capability inventory with watch

MACHINE-READABLE RECORD:
pmp-resident-current-capability-inventory-v1.json

────────────────────────
CORE PRESERVATION LAW
────────────────────────

No existing Resident capability may be silently removed, renamed, bypassed, replaced, or semantically weakened during the Resident Safe Change Architecture build.

Every existing capability must receive one controlled status:

1. PRESERVE
2. PRESERVE AND UPGRADE
3. REPLACE SAFELY
4. DEPRECATE WITH PROOF
5. UNKNOWN — HOLD

A replacement is allowed only when:

1. the old capability is identified,
2. the new capability is mapped,
3. stored data and keys are migrated safely,
4. behavioral equivalence or intentional improvement is tested,
5. rollback exists,
6. user-visible removal is disclosed,
7. a replacement receipt is written.

Unknown does not mean disposable.
Unknown means hold until audited.

────────────────────────
CURRENT RESIDENT SYSTEM SHAPE
────────────────────────

The known current system includes:

1. PMP Current outer layer
   pmp-home-single-v14.html

2. Integrated Resident user surface
   Resident drawer inside pmp-home-single-v6.html

3. Standalone Resident inspection surface
   resident.html

4. Hidden Resident X-Ray
   pmp-resident-xray-core.js
   pmp-resident-xray-finish.js
   pmp-inventory-eyes-xray-feed.js

5. Inventory Eyes and lossless awareness
   pmp-inventory-eyes-manifest-v1.0.0.json
   PMP Current Inventory Eyes functions

6. Private Bug Memory room
   private-bug-memory-hub-v9.html
   private-bug-memory-hub-v7.html

7. Bug Memory pack and Notes catalog
   resident-notes-catalog-v3.html

8. Private Notes backend bridge
   resident-notes-backend-v2.html

9. Private ZIP intake scanner
   resident-zip-xray-v2.html

10. Bug hypothesis and prediction lab
    private-bug-mixer-lab-v1.html

11. Protected edit tool
    safe-writer-v14.html
    safe-writer.html

12. Safe-point and recovery tool
    code-safety-v13.html
    code-safety.html

────────────────────────
CURRENT CAPABILITY RECORDS
────────────────────────

RC-001 — INTEGRATED RESIDENT CONVERSATION DRAWER

CURRENT STATUS:
PRESERVE AND UPGRADE

CURRENTLY PROVIDES:

1. normal-language request box
2. Run control
3. Chat view
4. Tools view
5. packet request
6. packet save
7. pipeline control
8. work display
9. copy work
10. help action
11. chat archive
12. chat reset
13. Resident reply area
14. warning area

FUTURE ROLE:
Primary user entry for Resident Safe Change requests.

DO NOT LOSE:
The user must still be able to tell Resident what to do in ordinary language.

────────────────────────

RC-002 — RESIDENT AUTHORITY MODES

CURRENT STATUS:
PRESERVE AND MAP

CURRENTLY PROVIDES:

1. Guide Mode
2. Inspector Mode
3. Diagnose Mode
4. Prepare Mode

FUTURE ROLE:
Explicit authority levels separating explanation, observation, diagnosis, preparation, candidate writing, and promotion recommendation.

DO NOT DO:
Do not silently turn an explanation mode into write authority.

────────────────────────

RC-003 — ACTIVE WORK THREAD

CURRENT STATUS:
PRESERVE AND UPGRADE

CURRENTLY RECORDS:

1. active goal
2. phase
3. current tool
4. safety state
5. next safe step

FUTURE ROLE:
Persistent change-job state, restart context, and future-chat handoff.

────────────────────────

RC-004 — WHOLE-APP HEALTH SNAPSHOT

CURRENT STATUS:
UPGRADE

CURRENTLY READS:

1. safe-point bank state
2. Last Good pointer
3. pinned emergency pointer
4. safe-point count
5. quarantine count
6. App Truth health

FUTURE ROLE:
Change-aware health, regression state, guardian state, rollback state, and promotion readiness.

WATCH:
The current health view is not yet a complete whole-app code-change validator.

────────────────────────

RC-005 — APP TRUTH SCANNER

CURRENT STATUS:
PRESERVE AND EXPAND

CURRENTLY CHECKS THE BRIDGE CONTRACT FOR:

1. missing Bridge screen
2. extra direct cards
3. forbidden hidden elements
4. suspect elements
5. raw code or form areas
6. touch-triggered DOM changes
7. related storage-key evidence

CURRENT OUTPUTS:

1. pass/fail contract status
2. bug-open status
3. root-cause layer hint
4. repair-needed state
5. next safe step

FUTURE ROLE:
Whole-app contract registry and runtime regression scanner.

WATCH:
The current detailed scanner is primarily Bridge-focused.
It must not be falsely described as complete whole-app bug coverage.

────────────────────────

RC-006 — STORAGE SCANNER

CURRENT STATUS:
PRESERVE WITH PRIVACY BOUNDARY

CURRENTLY PROVIDES:

1. matching localStorage key names
2. value size metadata
3. evidence-only status
4. no automatic bug claim from key existence alone

FUTURE ROLE:
Storage identity, schema drift, migration impact, stale-key, and protected-key detection.

PRIVACY LAW:
Key-name visibility does not authorize private-value capture.

────────────────────────

RC-007 — BUG MEMORY

CURRENT STATUS:
PRESERVE AND UPGRADE

CURRENTLY PROVIDES:

1. bug identity
2. duplicate matching
3. status
4. severity
5. priority
6. confidence
7. times seen
8. latest evidence
9. history entries
10. screen and bug-family classification

FUTURE ROLE:
Permanent known-bug registry and regression-test source.

NEW-BUG LAW:
Every proven new bug should become a permanent regression test when technically possible.

────────────────────────

RC-008 — REPAIR REQUEST BUILDER

CURRENT STATUS:
UPGRADE

CURRENTLY PROVIDES:

1. target
2. proven problem
3. proof status
4. repair rule
5. Safe Writer steps
6. verification steps

FUTURE ROLE:
Formal candidate change specification containing intended behavior, affected area, acceptance tests, protected objects, rollback requirement, and claim ceiling.

────────────────────────

RC-009 — SAME-ORIGIN LIVE PMP MIRROR

CURRENT STATUS:
PRESERVE AND ISOLATE

CURRENTLY PROVIDES:

1. live same-origin PMP loading
2. DOM inspection
3. observation without directly changing the normal app surface

FUTURE ROLE:
Candidate preview and runtime sandbox.

BOUNDARY:
A mirror is not automatically a fully isolated candidate environment.
Candidate storage, routes, and code identity still need separate protection.

────────────────────────

RC-010 — HIDDEN RESIDENT X-RAY

CURRENT STATUS:
PRESERVE AND UPGRADE

CURRENTLY OBSERVES:

1. live DOM structure
2. screen inventory
3. buttons and interactive controls
4. forms
5. visibility and geometry
6. route links
7. manifest-known routes
8. possible missing local files
9. current app map
10. Inventory Eyes summary
11. vault current summary
12. localStorage key names only
13. periodic history

CURRENT REFRESH:

1. initial load
2. before Resident answer
3. background refresh
4. manual refresh

FUTURE ROLE:
Live dependency map and evidence source for change-impact prediction.

PRIVACY BOUNDARY:

1. app structure may be captured
2. localStorage key names may be captured
3. private values may not be captured
4. Apple Notes contents may not be captured
5. tokens, passwords, and secrets may not be captured

────────────────────────

RC-011 — INVENTORY EYES AND LOSSLESS COMMAND BRIDGE

CURRENT STATUS:
PRESERVE SEPARATION

CURRENTLY PROVIDES:

1. manifest-based app inventory
2. active/inactive file language
3. live-screen summary
4. privacy-sensitive surface list
5. theme-review targets
6. local report storage
7. vault write packet
8. Resident commands for lossless scans and copying reports

SEPARATION LAW:
Resident X-Ray may read Inventory Eyes summaries.
Resident X-Ray must not replace, overwrite, or silently redefine Inventory Eyes.

FUTURE ROLE:
Repository/app inventory authority and architecture map source.

────────────────────────

RC-012 — PRIVATE BUG MEMORY ROOM

CURRENT STATUS:
PRESERVE

CURRENTLY PROVIDES:

1. Save Bug Memory path
2. Load Memory from Notes
3. session-only memory load
4. copy-for-Resident packet
5. Bug Lab entry
6. prediction ledger guidance
7. controlled-test order

CONTROLLED TEST ORDER ALREADY PRESENT:

1. theory only
2. fake-state test
3. local sandbox copy
4. disposable test file
5. Safe Writer guarded test
6. current app only after everything else passes

FUTURE ROLE:
Private historical bug and regression evidence.

────────────────────────

RC-013 — BUG MEMORY PACK AND NOTES CATALOG BUILDER

CURRENT STATUS:
PRESERVE AND NORMALIZE

CURRENTLY PROVIDES:

1. bug normalization
2. bug IDs
3. severity and status
4. expected and actual behavior
5. likely cause
6. fix direction
7. acceptance tests
8. do-not-change fields
9. ZIP pack generation
10. manifest and instructions
11. validation, timeline, index, report, schema, test, playbook, and lossless bands
12. Notes save paths
13. fundamental bug ranking

FUTURE ROLE:
Portable bug/regression pack standard.

────────────────────────

RC-014 — NOTES BACKEND BRIDGE

CURRENT STATUS:
PRESERVE WITH MANUAL BOUNDARY

CURRENTLY PROVIDES:

1. local ZIP scan
2. unsafe-path detection
3. JSON parsing
4. required-field checks
5. duplicate bug-ID checks
6. chunk creation
7. payload and fragment hashes
8. clipboard transfer
9. Shortcuts handoff
10. Apple Notes append workflow

PRIVACY LAW:
Private Bug Memory stays out of public GitHub app state.
The web app cannot secretly read Apple Notes.

FUTURE ROLE:
Private evidence transfer outside the public repository.

────────────────────────

RC-015 — RESIDENT ZIP X-RAY

CURRENT STATUS:
PRESERVE AND CONNECT

CURRENTLY PROVIDES:

1. ZIP size gates
2. uncompressed-size watch
3. file-count watch
4. path safety classification
5. system-file rejection
6. file-band classification
7. JSON parsing
8. required bug-field checks
9. duplicate bug-ID checks
10. quarantine
11. private-only import
12. optional backend sync
13. merge-by-bug-ID behavior
14. report copying

FUTURE ROLE:
Bug-pack intake validator and quarantine gate for regression memory.

────────────────────────

RC-016 — BUG MIXER LAB

CURRENT STATUS:
PRESERVE AS HYPOTHESIS TOOL

CURRENTLY PROVIDES:

1. private catalog load
2. two-bug mixing
3. fundamental ranking
4. easy bug names
5. prediction generation
6. prediction copying
7. Notes save
8. temporary session ledger

TRUTH LAW:
Predictions are questions for controlled testing.
Predictions are not confirmed bugs.

FUTURE ROLE:
Generate breaker hypotheses and test ideas.

────────────────────────

RC-017 — SAFE WRITER PROTECTED TRANSACTION

CURRENT STATUS:
PRESERVE AND REFACTOR TOWARD CANDIDATE FLOW

CURRENTLY PROVIDES:

1. GitHub connection test
2. current-file fetch
3. exact text find
4. replacement preview
5. staged replacement
6. DOM guard
7. transaction preview
8. BEFORE safe point
9. protected commit
10. AFTER safe point
11. Last Good update
12. failed-transaction quarantine
13. local last-good copy and restore-to-box

CURRENT WRITE BOUNDARY:
A user-provided GitHub token is entered into Safe Writer for the transaction.

CURRENT TARGET BEHAVIOR:
Direct protected update transaction for the selected file.

FUTURE ROLE:
Candidate branch writer and promotion transaction executor.

REQUIRED UPGRADE:
Do not let Resident jump from request directly to the current branch.
Add candidate identity, isolated branch/workspace, test binding, outer-guardian verification, and protected promotion.

────────────────────────

RC-018 — CODE SAFETY SAFE-POINT BANK

CURRENT STATUS:
PRESERVE AND UPGRADE

CURRENTLY PROVIDES:

1. code hashing
2. safe-point creation
3. current pointer
4. Last Good pointer
5. pinned emergency pointer
6. bank health
7. clean/warning status
8. blockers and warnings
9. local code snapshots
10. audit log
11. quarantine
12. Auto-Catch
13. find version
14. compare versions
15. export/import bank
16. restore packet preview and copy

CURRENT LIMIT:
Restore write-back is described as not connected in the audited interface.

FUTURE ROLE:
Protected baseline, rollback bank, immutable-enough audit source, and recovery authority.

────────────────────────

RC-019 — RESIDENT INSIDE SAFE WRITER AND CODE SAFETY

CURRENT STATUS:
PRESERVE AND REPLACE HANDOFF DEPENDENCY

CURRENTLY PROVIDES:

1. local tool context
2. frame-text awareness
3. safety-bank status
4. selected packet context
5. Corpus status
6. automatic-update request awareness
7. next-step guidance
8. copyable handoff

CURRENT LIMIT:
These Resident wrappers guide and copy handoffs.
They do not independently control the underlying tools.

FUTURE ROLE:
Resident-native tool orchestration under protected permissions.

────────────────────────

RC-020 — PRIVACY AND TRUST-ZONE SEPARATION

CURRENT STATUS:
NON-NEGOTIABLE PRESERVE

CURRENTLY PRESENT BOUNDARIES:

1. X-Ray captures key names, not private values
2. Apple Notes contents are not silently read
3. private Bug Memory is not stored in public GitHub app state
4. tokens, passwords, and secrets are excluded from normal reports
5. Bug Memory can be loaded for a private session only
6. public-safe inventory and private memory remain distinct

FUTURE ROLE:
Permanent trust-zone and data-classification law for Resident and the outer guardian.

────────────────────────
CURRENT STORAGE AND CONTRACT KEYS
────────────────────────

Known keys that future architecture must preserve, migrate, or explicitly replace:

1. pmp_resident_thread_v1
2. pmp_resident_report_v1
3. pmp_bug_memory_v1
4. pmp_resident_xray_context_v1
5. pmp_resident_xray_history_v1
6. pmp_resident_xray_rule_v1
7. pmp_inventory_eyes_latest_v1
8. pmp_lossless_visible_compact_latest_v1
9. pmp_app_lossless_inventory_latest_v1
10. pmp_resident_auto_lossless_inventory_context_v1
11. pmp_lossless_improve_runs_inventory_rule_v1
12. pmp_code_safety_bank_v1
13. pmp_safe_writer_last_good_v3
14. pmp_clean_connection_packets_v5
15. pmp_corpus_inbox_v1
16. pmp_auto_update_request_v20
17. pmp_private_bug_memory_existing_v1
18. pmp_backend_config_v1

KEY LAW:
A future rename is a migration, not a deletion.
No protected key may silently disappear.

────────────────────────
CURRENT VERIFIED LIMITS
────────────────────────

1. Resident does not currently perform independent repository commits from its normal conversation surface.

2. Resident does not currently perform independent restore/write-back from its normal conversation surface.

3. The standalone App Truth scanner is primarily a Bridge-screen contract scanner, not a complete whole-app change validator.

4. Safe Writer can commit with a manually entered GitHub token, but it is not yet a complete candidate-branch and independently verified promotion system.

5. Code Safety restore write-back is not connected in the audited interface.

6. Resident inside Safe Writer and Code Safety currently guides and copies handoffs rather than independently controlling the full workflow.

7. Bug Mixer predictions are hypotheses, not confirmed bugs.

8. Automatic affected-test selection is not yet proven.

9. Candidate identity binding is not yet proven.

10. Independent outer-guardian approval is not yet implemented or proven.

11. Tested-candidate to promoted-candidate identity equality is not yet proven.

12. The exact reasoning/model connection used by the integrated Resident has not yet been fully audited and remains UNKNOWN — HOLD.

────────────────────────
KNOWN FILES STILL REQUIRING FULL AUDIT
────────────────────────

The Inventory Eyes manifest names additional Resident-related or supporting files that have not yet received a complete capability classification in this inventory:

1. resident-v1.html
2. resident-brain-core-v1.html
3. resident-intelligence-v1.html
4. resident-conversation-layer.html
5. resident-chat-menu.html
6. local-storage-manager.html
7. bridge-contextual-menu.html
8. corpus-workbench.html
9. project-connection-workbench.html
10. lossless-certification-system.html
11. proof-ledger-system.html
12. bm.html
13. pmp-inventory-eyes-detail-map-v1.0.0.json

STATUS FOR ALL ABOVE:
UNKNOWN — HOLD

RULE:
Do not delete, absorb, or replace them merely because they are not yet understood.

────────────────────────
HIGH-RISK PROTECTED OBJECTS
────────────────────────

The Resident Safe Change Architecture must protect:

1. frozen baseline identity
2. current route identity
3. protected current-map authority
4. Code Safety bank
5. Last Good pointer
6. pinned emergency pointer
7. rollback records
8. Resident X-Ray privacy boundary
9. Inventory Eyes separation
10. Bug Memory privacy boundary
11. body-law authority
12. claim ceilings
13. promotion rules
14. outer-guardian rules
15. authorization controls

────────────────────────
ARCHITECTURE ENTRY RULE
────────────────────────

The Resident Safe Change Architecture must begin with this inventory as Protected Section 1.

The architecture may add capabilities.
The architecture may strengthen capabilities.
The architecture may safely replace a capability after proof.

The architecture may not silently subtract an existing capability.

Before implementation begins, the architecture must map every protected capability to:

1. current source
2. future component
3. preserved data
4. preserved user behavior
5. new tests
6. rollback path
7. replacement or migration receipt

────────────────────────
SAFE CLAIM
────────────────────────

The known current Resident capability set has been inventoried from direct repository evidence with watch and is ready to become the protected starting point for the Resident Safe Change Architecture.

────────────────────────
DO-NOT-CLAIM
────────────────────────

Do not claim:

1. every historical Resident file has been fully audited
2. every repository file has been classified
3. Resident already codes independently
4. Resident already predicts every bug
5. automatic affected-test selection is complete
6. the outer guardian is already implemented
7. restore write-back is complete
8. the Resident Safe Change Architecture is implemented
9. this inventory by itself makes Resident safe to self-modify

────────────────────────
NEXT BEST MOVE
────────────────────────

Use this inventory as Protected Section 1 of:

PMP Current — Resident Safe Change Architecture

Then complete the audit of the UNKNOWN — HOLD files before allowing any architecture decision that deletes, merges, or replaces them.

END PMP CURRENT — RESIDENT CURRENT CAPABILITY INVENTORY v1-current
