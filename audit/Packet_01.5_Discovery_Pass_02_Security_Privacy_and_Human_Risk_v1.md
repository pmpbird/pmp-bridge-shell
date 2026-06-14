# Packet 01.5 — Discovery Pass 02

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for distinct security, privacy, malicious-input, memory-poisoning, human-decision, portability, legal, and identity risks not clearly isolated in the 122-record baseline.

## Provisional records

### SEC-001 — Untrusted text reaches executable or privileged browser contexts

Repository content, filenames, AI output, Bug Memory, receipts, manifests, or imported reports may be inserted into HTML, attributes, URLs, scripts, or event handlers without context-sensitive escaping.

HARM: script execution, false controls, data theft, or altered approval surfaces.

OVERLAP TO CHECK: AI-015, BUILD-009.

### SEC-002 — No complete browser content-security boundary

No proven Content Security Policy, Trusted Types policy, Subresource Integrity rule, local-vendoring rule, or inline-script restriction protects the live app.

HARM: compromised CDN or injected content may execute with app authority.

OVERLAP TO CHECK: PLAT-007, BUILD-008.

### SEC-003 — Repository scripts and build hooks may execute untrusted code

Package install scripts, test commands, build tools, Git hooks, task runners, or repository-defined commands may run before their effects are understood.

HARM: host compromise, secret theft, network exfiltration, or modification outside the candidate.

OVERLAP TO CHECK: BUILD-009.

### SEC-004 — Command, argument, URL, and path injection

Model output, filenames, branch names, issue text, repository content, or user text may be used to construct commands, tool arguments, URLs, or paths without strict typed validation.

HARM: unintended commands, file overwrite, external requests, or authority escape.

OVERLAP TO CHECK: AI-014, AI-015, BUILD-009.

### SEC-005 — Hostile archive and import handling

ZIPs and imported packages may contain zip bombs, path traversal, absolute paths, symlinks, nested archives, duplicate names, spoofed extensions, or extreme decompression ratios.

HARM: resource exhaustion, file confusion, overwrite, or hidden payloads.

OVERLAP TO CHECK: OPS-009, PLAT-012.

### SEC-006 — Secrets and private data leak through secondary artifacts

Credentials, private source, Bug Memory, user data, or provider responses may leak through prompts, logs, receipts, screenshots, clipboard, Apple Notes, ZIPs, Git history, crash reports, or diagnostic exports.

HARM: permanent disclosure even after the primary record is deleted.

OVERLAP TO CHECK: AI-010, DATA-013, DATA-014, OPS-013.

### SEC-007 — Imported evidence and packets lack proven authenticity

A file may have a digest yet still come from the wrong person, repository, branch, device, or process. Imported receipts, manifests, evidence, and routing registers have no complete signer or provenance trust rule.

HARM: forged or substituted evidence may authorize unsafe work.

OVERLAP TO CHECK: DATA-012, GOV-015.

### SEC-008 — Shared-device and shared-browser separation is undefined

Local storage, caches, clipboard, Notes, approvals, and private records may remain visible to another person using the same device, browser profile, or unlocked session.

HARM: privacy breach or unauthorized approval.

OVERLAP TO CHECK: DATA-008, DATA-013.

### SEC-009 — Domain, origin, DNS, and TLS continuity is ungoverned

Domain expiration, DNS takeover, origin change, certificate failure, hosting-account loss, or route migration may redirect users or orphan same-origin storage.

HARM: impersonation, lost data, broken routes, or loading an attacker-controlled app.

OVERLAP TO CHECK: OPS-008, PLAT-014.

### SEC-010 — Navigation and approval-surface deception

External links, popups, downloads, embedded pages, opener access, redirects, or look-alike pages may confuse which origin and version is requesting approval.

HARM: user approves the wrong candidate, provider, or action.

OVERLAP TO CHECK: OPS-014, RUN-015.

### MEM-001 — Bug Memory poisoning

False, malicious, speculative, or weakly proven entries may enter Bug Memory and later be treated as established truth.

HARM: repeated wrong fixes, unnecessary blockers, or unsafe code changes.

OVERLAP TO CHECK: PROOF-009, DATA-012.

### MEM-002 — Contradictory and stale memory has no enforced precedence

Two Bug Memory entries may conflict, or an older entry may silently override newer evidence without confidence, supersession, or expiry handling.

HARM: Resident follows obsolete failure models.

OVERLAP TO CHECK: GOV-009, PROOF-012.

### MEM-003 — Self-reinforcing learning loop

Resident may generate a diagnosis, store it as memory, then use that same memory as evidence that the diagnosis was correct.

HARM: false beliefs become increasingly difficult to detect.

OVERLAP TO CHECK: RUN-012, PROOF-013.

### HUM-001 — Approval fatigue

Frequent warnings, holds, confirmations, and technical receipts may train the user to approve without reading.

HARM: high-risk changes receive accidental approval.

OVERLAP TO CHECK: PROOF-014, RUN-015.

### HUM-002 — User comprehension is not proven for high-impact actions

Showing an explanation does not prove the user understood the affected data, authority, rollback limits, or residual risk—especially on a small iPhone screen.

HARM: consent is technically recorded but not meaningfully informed.

OVERLAP TO CHECK: OPS-014, PLAT-013.

### HUM-003 — Safety labels can create false confidence

Words such as PASS, SAFE, VERIFIED, PROTECTED, or COMPLETE may be shown without the exact scope, expiry, exclusions, and remaining watches at the moment of decision.

HARM: the user assumes broader safety than was proven.

OVERLAP TO CHECK: GOV-010, PROOF-015.

### PORT-001 — Filename and path identity differs across environments

Case sensitivity, Unicode normalization, confusable characters, reserved names, path separators, dotfiles, and maximum path lengths may cause the same file to be identified differently.

HARM: wrong-file edits, duplicate identities, failed migration, or incomplete proof.

OVERLAP TO CHECK: OPS-009, BUILD-011.

### PORT-002 — Encoding and binary handling can corrupt or omit content

UTF variants, byte-order marks, line endings, invalid bytes, binary files, large files, generated files, and mixed encodings may be silently changed or skipped.

HARM: source corruption, invalid diffs, or incomplete review.

OVERLAP TO CHECK: OPS-009.

### LEGAL-001 — Code and artifact provenance is incomplete

Generated, copied, transformed, or dependency-derived code may have unknown copyright, license, attribution, patent, trademark, or redistribution conditions.

HARM: the project may become unusable, non-portable, or legally restricted.

OVERLAP TO CHECK: BUILD-008, OPS-004.

### REL-001 — Identity collision or reuse

Candidate IDs, receipt IDs, limitation IDs, evidence IDs, task IDs, timestamps, or branch names may collide, be reused, or be generated from an untrusted clock.

HARM: evidence attaches to the wrong object or an old approval is mistaken for a new one.

OVERLAP TO CHECK: DATA-011, BUILD-011.

## Pass 02 result

New provisional records: 20
Routing decisions made: 0
Records closed: 0
Deduplication required later: Yes
Discovery saturation: NOT REACHED

Combined working total:
- Existing baseline: 122
- Pass 01 provisional: 10
- Pass 02 provisional: 20
- Current preserved plus provisional: 152

NEXT DISCOVERY PASS:
Reliability, crash consistency, stale clients, backup restoration, provider loss, platform lifecycle, and recovery-chain failure.

END PACKET 01.5 — DISCOVERY PASS 02
