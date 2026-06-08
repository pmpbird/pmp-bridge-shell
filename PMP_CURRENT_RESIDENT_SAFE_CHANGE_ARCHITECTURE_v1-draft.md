BEGIN PMP CURRENT — RESIDENT SAFE CHANGE ARCHITECTURE

CARD NAME:
PMP Current — Resident Safe Change Architecture

CARD VERSION:
v1-draft

DOCUMENT STATE:
architecture planning only
not implemented
not wired into current app
not promotion authority

ROLE:
This architecture defines how Resident will become an independent guarded development agent while preserving everything already built, protecting the frozen current baseline, and preventing Resident from becoming the only judge of its own changes.

This document must be grounded in the actual current Resident system.
It must not redesign Resident from an imaginary blank state.
It must not silently remove working capabilities.
It must not directly authorize writes to the frozen current app.

────────────────────────
PROTECTED SECTION 1
RESIDENT CURRENT CAPABILITY INVENTORY
────────────────────────

AUTHORITATIVE HUMAN-READABLE INVENTORY:
PMP_CURRENT_RESIDENT_CAPABILITY_INVENTORY_v1-current.md

AUTHORITATIVE MACHINE-READABLE INVENTORY:
pmp-resident-current-capability-inventory-v1.json

INVENTORY STATE:
current known capability inventory with watch

PROTECTED INVENTORY LAW:

1. Every existing Resident capability must be preserved, deliberately upgraded, safely replaced, deprecated with proof, or held as unknown.
2. No existing capability may be silently deleted, bypassed, renamed, or semantically weakened.
3. Unknown files and capabilities remain held until audited.
4. Storage-key renames require migration.
5. User-visible workflow changes require disclosure and testing.
6. Replacements require rollback and a replacement receipt.
7. The architecture must map every current capability to its future component before implementation.

CURRENT PROTECTED CAPABILITY FAMILIES:

1. Integrated Resident conversation drawer
2. Guide, Inspector, Diagnose, and Prepare modes
3. Active Work Thread
4. Whole-App Health Snapshot
5. App Truth Scanner
6. Storage scanner
7. Bug Memory
8. Repair request builder
9. Same-origin live PMP mirror
10. Hidden Resident X-Ray
11. Inventory Eyes and lossless command bridge
12. Private Bug Memory room
13. Bug Memory pack and Notes catalog builder
14. Notes backend bridge
15. Resident ZIP X-Ray
16. Bug Mixer Lab
17. Safe Writer protected transaction
18. Code Safety safe-point bank
19. Resident context inside Safe Writer and Code Safety
20. Privacy and trust-zone separation

CURRENT HIGH-RISK PROTECTED OBJECTS:

1. frozen baseline identity
2. current route identity
3. current-map authority
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

UNKNOWN — HOLD FILES:

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

HOLD RULE:
No deletion, merge, replacement, or authority transfer involving an UNKNOWN — HOLD file is allowed until that file is audited and classified.

────────────────────────
SECTION 2
PRIMARY RESIDENT SAFE CHANGE GOAL
────────────────────────

The user describes a desired app change in ordinary language.

Resident must then:

1. understand the request
2. produce a precise specification
3. read applicable body laws
4. read protected-object rules
5. build an impact map
6. identify missing coverage
7. create an isolated candidate
8. inspect the candidate statically
9. select required tests
10. run affected tests
11. run regression tests
12. run breaker attacks
13. observe candidate runtime behavior
14. compare candidate with frozen baseline
15. submit evidence to the trusted outer guardian
16. receive a promotion decision
17. request user approval when required
18. promote or roll back
19. write immutable-enough receipts
20. convert proven new bugs into regression tests

REQUIRED PIPELINE:

REQUEST
→ SPECIFICATION
→ BODY-LAW READ
→ PROTECTED-OBJECT READ
→ IMPACT MAP
→ COVERAGE CHECK
→ ISOLATED CANDIDATE
→ STATIC INSPECTION
→ AFFECTED TESTS
→ REGRESSION TESTS
→ BREAKER TESTS
→ RUNTIME PROOF
→ BASELINE COMPARISON
→ OUTER-GUARDIAN VERIFICATION
→ USER APPROVAL WHEN REQUIRED
→ PROMOTION OR ROLLBACK
→ RECEIPT
→ REGRESSION LEARNING

────────────────────────
SECTION 3
TRUSTED OUTER GUARDIAN LAW
────────────────────────

Resident may propose, build, explain, diagnose, repair, and recommend.

Resident must not be the only judge of its own changes.

The following must remain outside the candidate code Resident is currently changing:

1. frozen baseline identity
2. final promotion authority
3. rollback authority
4. safety-critical validators
5. authorization rules
6. candidate identity verification
7. protected proof receipts
8. user-approval requirements

The outer guardian must independently verify:

1. candidate identity
2. baseline identity
3. changed-file set
4. protected-object changes
5. required-test execution
6. test-result ownership
7. tested-to-promoted identity equality
8. rollback availability
9. claim-ceiling preservation
10. route and storage identity
11. validator integrity
12. stale report and stale approval rejection

CORE LAW:
AI may propose and explain.
Deterministic protected validators control safety-critical promotion.

────────────────────────
SECTION 4
CURRENT-TO-FUTURE CAPABILITY MAPPING
────────────────────────

Before implementation, every RC-001 through RC-020 capability must receive:

1. current source file
2. current user-visible behavior
3. current storage keys
4. future component
5. preserved behavior
6. intended upgrade
7. tests required
8. migration needed
9. rollback method
10. final status

ALLOWED FINAL STATUSES:

PRESERVED
UPGRADED
REPLACED_WITH_PROOF
DEPRECATED_WITH_PROOF
HELD_UNTIL_AUDIT

No capability may enter implementation with an undefined future status.

────────────────────────
SECTION 5
CHANGE REQUEST AND SPECIFICATION CONTRACT
────────────────────────

TO BE COMPLETED.

Must define:

1. request schema
2. user intent record
3. explicit non-goals
4. acceptance conditions
5. protected areas
6. risk class
7. uncertainty state
8. required user confirmation
9. cancellation behavior
10. request receipt

────────────────────────
SECTION 6
BODY-LAW AND PROTECTED-OBJECT READER
────────────────────────

TO BE COMPLETED.

Must define:

1. how Resident reads BODY-000 through BODY-021
2. how add-ons and support records are read
3. how hooks become executable checks
4. how claim ceilings are loaded
5. how protected objects are indexed
6. how rule conflicts are handled
7. how unknown rules cause HOLD
8. how body-law versions are bound to a candidate

────────────────────────
SECTION 7
CHANGE-IMPACT MAP
────────────────────────

TO BE COMPLETED.

Must map a requested change to:

1. files
2. functions
3. routes
4. controls
5. screens
6. storage keys
7. reports
8. hooks
9. tests
10. validators
11. privacy zones
12. proof claims
13. rollback records
14. current capability records

────────────────────────
SECTION 8
CANDIDATE ISOLATION
────────────────────────

TO BE COMPLETED.

Must define:

1. candidate branch or workspace
2. candidate ID
3. baseline commit/hash
4. changed-file list
5. isolated storage namespace
6. preview URL or shell
7. candidate expiration
8. candidate ownership
9. candidate deletion
10. protection from writing current directly

────────────────────────
SECTION 9
TEST REGISTRY AND AUTOMATIC TEST SELECTION
────────────────────────

TO BE COMPLETED.

Must define:

1. test IDs
2. bug-family coverage
3. trigger rules
4. affected-area mapping
5. required versus optional tests
6. timeout behavior
7. test-data isolation
8. result schemas
9. missing-coverage HOLD
10. permanent regression-test creation

────────────────────────
SECTION 10
RUNTIME OBSERVATION AND APP TRUTH
────────────────────────

TO BE COMPLETED.

Must upgrade current App Truth and X-Ray capabilities into:

1. whole-app contract registry
2. candidate runtime observer
3. error listener
4. failed-action listener
5. DOM mutation observer
6. route observer
7. storage mutation observer
8. stale-report detector
9. user-visible regression detector
10. candidate versus baseline behavior comparison

────────────────────────
SECTION 11
PROMOTION, APPROVAL, AND ROLLBACK
────────────────────────

TO BE COMPLETED.

Must define:

1. deterministic promotion blockers
2. watch conditions
3. user approval classes
4. automatic promotion prohibition or narrow allowance
5. promotion receipt
6. rollback pointer
7. rollback execution
8. post-promotion smoke test
9. failed-promotion quarantine
10. freeze re-establishment

────────────────────────
SECTION 12
SELF-MODIFICATION AND GUARDIAN-UPGRADE PROCESS
────────────────────────

TO BE COMPLETED.

Any change to Resident, tests, validators, body-law readers, promotion rules, rollback rules, or outer guardian must use a separately protected high-risk process.

Resident must never approve:

1. its own validator weakening
2. its own authority expansion
3. rollback removal
4. baseline replacement
5. claim-ceiling weakening
6. guardian bypass
7. stale approval reuse

────────────────────────
SECTION 13
PRIVACY, PERMISSIONS, AND CREDENTIALS
────────────────────────

TO BE COMPLETED.

Must preserve current privacy boundaries and define:

1. public repository data
2. private browser data
3. Apple Notes data
4. Bug Memory data
5. credentials
6. GitHub authorization
7. model-provider data
8. logs and receipts
9. data retention
10. data deletion

A powerful GitHub token must not be embedded openly in the app.

────────────────────────
SECTION 14
REASONING ENGINE BOUNDARY
────────────────────────

TO BE COMPLETED AFTER CURRENT REASONING CONNECTION AUDIT.

Must define:

1. current Resident reasoning source
2. future replaceable model interface
3. offline/unavailable behavior
4. confidence and uncertainty
5. tool permissions
6. prompt/rule version binding
7. deterministic override
8. model replacement portability

CURRENT STATUS:
UNKNOWN — HOLD

────────────────────────
SECTION 15
RECEIPTS AND INDEPENDENT REPEATABILITY
────────────────────────

TO BE COMPLETED.

Must produce:

1. request receipt
2. specification receipt
3. impact-map receipt
4. candidate receipt
5. test-selection receipt
6. test-results receipt
7. breaker receipt
8. runtime receipt
9. guardian decision receipt
10. user approval receipt
11. promotion receipt
12. rollback receipt
13. regression-learning receipt

A future Resident instance, assistant, or person must be able to understand the decision without hidden chat context.

────────────────────────
SECTION 16
IMPLEMENTATION GATES
────────────────────────

GATE 1:
Current capability inventory complete enough for architecture.

CURRENT STATE:
PASSED WITH WATCH for known current files.
UNKNOWN — HOLD audit remains.

GATE 2:
All unknown Resident files audited.

CURRENT STATE:
NOT STARTED.

GATE 3:
Current-to-future capability map complete.

CURRENT STATE:
NOT STARTED.

GATE 4:
Outer guardian architecture complete.

CURRENT STATE:
NOT STARTED.

GATE 5:
Candidate isolation proven.

CURRENT STATE:
NOT STARTED.

GATE 6:
Automatic affected-test selection proven.

CURRENT STATE:
NOT STARTED.

GATE 7:
Promotion and rollback proven.

CURRENT STATE:
NOT STARTED.

GATE 8:
Resident makes a harmless real change without ChatGPT operating the tools.

CURRENT STATE:
NOT STARTED.

────────────────────────
SAFE CLAIM
────────────────────────

The Resident Safe Change Architecture has been started from a direct current-capability inventory, and subtraction protection is now defined at the planning level.

────────────────────────
DO-NOT-CLAIM
────────────────────────

Do not claim:

1. Resident Safe Change is implemented
2. Resident can independently code now
3. the outer guardian exists now
4. candidate isolation exists now
5. all Resident files are audited
6. every existing capability is fully understood
7. automatic test selection works now
8. rollback write-back is complete
9. the architecture changes the frozen app
10. this draft is promotion authority

────────────────────────
NEXT BEST MOVE
────────────────────────

Complete Gate 2:
Audit every UNKNOWN — HOLD file and classify it as current, support, archive, replacement candidate, or safe deprecation candidate.

Then complete the current-to-future capability map before writing Resident Safe Change implementation code.

END PMP CURRENT — RESIDENT SAFE CHANGE ARCHITECTURE v1-draft
