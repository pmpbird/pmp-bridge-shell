# Packet 01.5 — Discovery Pass 10

STATUS: DISCOVERY IN PROGRESS
PHASE: PROBLEM FINDING ONLY
ROUTING: NOT STARTED
DATE: 2026-06-14

This pass looks for build integrity, dependency resolution, reproducibility, package-manager behavior, generated files, toolchain drift, signing, deployment provenance, and supply-chain compromise.

## Provisional records

### DEP-001 — Transitive dependencies are not fully known

A direct dependency may pull many nested packages, binaries, plugins, scripts, and registries that are not reviewed individually.

HARM: hidden code gains build or runtime authority.

OVERLAP TO CHECK: BUILD-008, SUPPLY-001.

### DEP-002 — Lockfile is missing, stale, or ignored

The declared dependency file and installed dependency tree may not match, or automation may regenerate the lockfile silently.

HARM: different environments build different software from the same source.

OVERLAP TO CHECK: BUILD-008, REPRO-001.

### DEP-003 — Version ranges admit unreviewed updates

Caret, tilde, wildcard, latest, branch, URL, or floating tag references may resolve to newer content without a source change.

HARM: behavior changes outside the reviewed commit.

OVERLAP TO CHECK: PROV-001, TOOLCHAIN-001.

### DEP-004 — Lockfile integrity metadata is not verified

Checksums, registry identity, tarball origin, or resolved URLs may be ignored or replaced.

HARM: a different package can be installed under the expected name and version.

OVERLAP TO CHECK: SEC-007, SIGN-003.

### DEP-005 — Package-manager version changes resolution

Different npm, pnpm, yarn, system, or plugin versions may choose different dependency trees and peer resolutions.

HARM: builds differ even with the same manifest and lockfile.

OVERLAP TO CHECK: TOOLCHAIN-001, REPRO-001.

### DEP-006 — Optional and peer dependencies create hidden branches

A dependency may activate different code depending on what is installed, omitted, or available in the environment.

HARM: local, CI, and production behavior diverge.

OVERLAP TO CHECK: ENV-001, DEP-011.

### DEP-007 — Duplicate dependency versions behave inconsistently

Several copies of the same library may carry different state, types, security fixes, or runtime assumptions.

HARM: behavior depends on which copy a module resolves.

OVERLAP TO CHECK: DEP-005, BUILDINT-006.

### DEP-008 — Abandoned package or maintainer takeover

A trusted package may become unmaintained, transferred, compromised, or republished by a different owner.

HARM: future updates inherit malicious or unsupported code.

OVERLAP TO CHECK: MAINT-002, SUPPLY-002.

### DEP-009 — Install and lifecycle scripts execute before review

Dependencies may run preinstall, postinstall, prepare, build, download, or native compilation scripts.

HARM: code executes on the host before the resulting tree is inspected.

OVERLAP TO CHECK: SEC-003, BUILD-009.

### DEP-010 — Prebuilt binaries lack source and provenance parity

A package may download platform-specific binaries that cannot be reproduced from the reviewed source.

HARM: hidden executable content enters the build.

OVERLAP TO CHECK: REPRO-004, SIGN-001.

### DEP-011 — Dependency vulnerability and license data are stale

Advisory databases, package metadata, license declarations, and support status may be incomplete or delayed.

HARM: known risk remains undetected or a legal boundary is misclassified.

OVERLAP TO CHECK: LEGAL-001, MAINT-002.

### BUILDINT-001 — Local and CI build paths differ

Developers, GitHub Actions, hosting, and release processes may use different commands, environments, flags, or dependency-install modes.

HARM: locally tested code is not the released code.

OVERLAP TO CHECK: ENV-001, REPO-004.

### BUILDINT-002 — Environment variables silently change the build

Secrets, feature flags, base URLs, modes, analytics, debug settings, and provider identifiers may alter output without appearing in source control.

HARM: artifact behavior cannot be inferred from the commit alone.

OVERLAP TO CHECK: AUTH-004, PROOFCHAIN-001.

### BUILDINT-003 — Generated files are stale

Compiled assets, manifests, indexes, schemas, route tables, service workers, or bundles may not be regenerated after source changes.

HARM: source and deployed behavior disagree.

OVERLAP TO CHECK: REPO-004, TEST-006.

### BUILDINT-004 — Generated files cannot be traced to their generators

Committed output may lack the exact source, generator version, options, and command that produced it.

HARM: reviewers cannot determine whether generated content is legitimate.

OVERLAP TO CHECK: SEM-004, REPRO-004.

### BUILDINT-005 — Generated output contains machine-specific state

Absolute paths, usernames, locale, timestamps, random IDs, hostnames, or local ordering may enter bundles and manifests.

HARM: builds are non-reproducible and may leak private information.

OVERLAP TO CHECK: REPRO-003, SEC-006.

### BUILDINT-006 — File discovery and ordering are nondeterministic

Filesystem order, glob behavior, locale sorting, parallelism, or plugin timing may change bundle contents or precedence.

HARM: identical inputs produce different artifacts.

OVERLAP TO CHECK: PORT-001, REPRO-003.

### BUILDINT-007 — Build cache contains stale or foreign artifacts

Shared, remote, or local caches may restore output from another branch, configuration, dependency tree, or secret context.

HARM: the build includes content not produced from its current inputs.

OVERLAP TO CHECK: TEST-019, PROOFCHAIN-006.

### BUILDINT-008 — Ignored and untracked files affect the build

Local configuration, generated files, downloaded assets, credentials, patches, and ignored directories may influence output while remaining absent from the commit.

HARM: another environment cannot reproduce the release.

OVERLAP TO CHECK: REPO-005, REPRO-001.

### BUILDINT-009 — Submodules, Git LFS, symlinks, or nested repositories are incomplete

Referenced content may be missing, moved, replaced, or fetched from the wrong identity.

HARM: source checkout appears complete while build inputs differ.

OVERLAP TO CHECK: REPO-003, PROOFCHAIN-004.

### BUILDINT-010 — Development-only tooling leaks into production

Debug code, source maps, test fixtures, mock endpoints, dev servers, logs, and broad permissions may remain in the release.

HARM: private data, attack surface, or false behavior reaches users.

OVERLAP TO CHECK: OBS-004, DEPLOY-002.

### TOOLCHAIN-001 — Compiler, bundler, minifier, or runtime version drifts

A toolchain update may alter syntax, optimization, module resolution, polyfills, or browser compatibility.

HARM: the same source produces new behavior without an intentional design change.

OVERLAP TO CHECK: PROV-001, MAINT-002.

### TOOLCHAIN-002 — Plugin order changes semantics

Transform, lint, bundling, CSS, route, or optimization plugins may interact differently when reordered or duplicated.

HARM: configuration edits cause hidden behavioral changes.

OVERLAP TO CHECK: BUILDINT-006, SCHEMA-001.

### TOOLCHAIN-003 — Tool defaults change between versions

Strictness, target browser, source-map mode, tree shaking, hashing, minification, and error handling may change silently.

HARM: old configuration no longer means the same thing.

OVERLAP TO CHECK: SEM-001, TOOLCHAIN-001.

### TOOLCHAIN-004 — Unsupported or obsolete toolchain becomes unsafe

Old runtimes and build tools may stop receiving security fixes or fail on new operating systems and registries.

HARM: the project is trapped between known vulnerabilities and risky upgrades.

OVERLAP TO CHECK: MAINT-002, LOCK-003.

### REPRO-001 — Build is not hermetic

The build may depend on network access, global tools, host files, shell state, locale, user configuration, or undeclared packages.

HARM: no one can prove which inputs produced the artifact.

OVERLAP TO CHECK: BUILDINT-008, DEP-002.

### REPRO-002 — Remote resources are fetched during build

Scripts, fonts, models, packages, schemas, or data may be downloaded from mutable URLs.

HARM: a later build receives different content under the same source identity.

OVERLAP TO CHECK: SEC-002, SUPPLY-003.

### REPRO-003 — Time, randomness, concurrency, or unstable metadata affect output

Timestamps, random seeds, parallel scheduling, archive metadata, and generated identifiers may change artifact bytes.

HARM: byte-for-byte verification and provenance comparison fail.

OVERLAP TO CHECK: REL-007, BUILDINT-006.

### REPRO-004 — No independent rebuild comparison exists

The project may never rebuild the same commit in a separate clean environment and compare outputs.

HARM: hidden machine state and compromised builders remain undetected.

OVERLAP TO CHECK: PROOFCHAIN-007, AUTH-008.

### REPRO-005 — Reproducible bytes do not prove safe behavior

Two builders may deterministically reproduce the same malicious, misconfigured, or semantically wrong artifact.

HARM: reproducibility is mistaken for correctness or trustworthiness.

OVERLAP TO CHECK: QUAL-002, TEST-001.

### SIGN-001 — Release artifact is unsigned or signature is not preserved

Users and validators may have no cryptographic link between the approved artifact and the deployed file.

HARM: substitution cannot be detected reliably.

OVERLAP TO CHECK: PROOFCHAIN-001, SEC-007.

### SIGN-002 — Signing key is compromised, copied, or overexposed

A key may exist in CI secrets, local devices, backups, logs, shared accounts, or provider systems with excessive access.

HARM: malicious artifacts can appear officially approved.

OVERLAP TO CHECK: CRYPTO-002, AUTH-001.

### SIGN-003 — Signature verification is optional or performed by the same builder

A pipeline may sign and “verify” its own output without a separately trusted verifier.

HARM: compromised build infrastructure certifies itself.

OVERLAP TO CHECK: AUTH-008, AUD-004.

### SIGN-004 — Key rotation breaks old verification or trust continuity

Retired and replacement keys may lack a signed transition record, revocation, expiry, and historical verification plan.

HARM: old releases become unverifiable or compromised keys remain trusted.

OVERLAP TO CHECK: CRYPTO-003, SUCC-003.

### DEPLOY-001 — Artifact can be replaced between build and deployment

Uploads, release assets, hosting caches, deployment directories, and automation handoffs may substitute or mutate files.

HARM: deployed bytes differ from tested and approved bytes.

OVERLAP TO CHECK: PROOFCHAIN-001, REPO-004.

### DEPLOY-002 — Source maps, debug assets, or internal metadata are publicly exposed

Production deployment may include source, comments, paths, environment details, test data, or credentials.

HARM: private implementation and attack-relevant information leak.

OVERLAP TO CHECK: BUILDINT-010, SEC-006.

### DEPLOY-003 — Rollback artifact is missing, mutable, or unverified

The previous release may not be preserved, may depend on deleted resources, or may lack a valid signature and restore test.

HARM: rollback selects an unknown or unusable state.

OVERLAP TO CHECK: REC-001, PROOFCHAIN-004.

### DEPLOY-004 — Deployment targets the wrong environment, origin, or project

Similar names, credentials, branches, hosting sites, regions, or configuration may direct a release elsewhere.

HARM: private code leaks or the live app remains unchanged while records claim success.

OVERLAP TO CHECK: REPO-003, TOOL-001.

### DEPLOY-005 — Automation bypasses branch protection or approval gates

Bots, tokens, hosting hooks, direct API writes, or emergency workflows may deploy without the same controls applied to humans.

HARM: the actual release path escapes the documented guardian.

OVERLAP TO CHECK: AUTH-004, EMERG-001.

### SUPPLY-001 — Mutable GitHub Action, image, or tool reference changes

Workflows may reference a branch, floating tag, mutable container tag, or externally controlled action.

HARM: CI executes new third-party code without a repository change.

OVERLAP TO CHECK: DEP-003, PROOFCHAIN-006.

### SUPPLY-002 — Trusted publisher or maintainer account is compromised

A valid upstream account may release malicious code under the expected package, action, image, or extension identity.

HARM: ordinary update mechanisms deliver the attack.

OVERLAP TO CHECK: DEP-008, INS-002.

### SUPPLY-003 — CDN, registry, mirror, or download endpoint serves altered content

Network or provider compromise may replace scripts, packages, binaries, fonts, models, and schemas.

HARM: external content enters the build or runtime outside review.

OVERLAP TO CHECK: SEC-002, REPRO-002.

### SUPPLY-004 — Compromised update reaches every environment at once

Shared auto-update, cache, dependency, action, model, or hosting mechanisms may distribute one bad version broadly.

HARM: production, validation, recovery, and backup paths fail together.

OVERLAP TO CHECK: DIS-003, PROV-001.

## Pass 10 result

New provisional records: 43
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
- Current preserved plus provisional: 439

NEXT DISCOVERY PASS:
User-interface state, destructive-action design, mobile interaction, interrupted workflows, notification failure, status ambiguity, undo behavior, and human recovery errors.

END PACKET 01.5 — DISCOVERY PASS 10
