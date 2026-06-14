# Packet 01.5 — Routing Preparation Gate Baseline Source Addendum v1

STATUS: PASS
WATCH: NONE
BLOCKERS: NONE
ROUTING: NOT STARTED
DATE: 2026-06-14

This additive record satisfies the baseline-source requirement in Routing Preparation Gate v1 without rewriting that gate.

## Exact source preservation

The exact archive member:

`pmp-current-permanent-limitation-register-v3-final.json`

was recovered from:

`Packet_03.5_v4_FINAL_PASS_COMPLETE.zip`

and preserved in the repository as seven ordered deterministic gzip/base64 transport parts under:

`audit/baseline-source/`

The transport is exact because reconstruction proves:

- raw source bytes: 349103
- raw source SHA-256: `ac36b36a38d2ad9ab9f73d69679e0ecc0dae4c2f3340fe505f6ed773c56ba5f4`
- deterministic gzip bytes: 31622
- gzip SHA-256: `dd9e5fcb38f8bb3babb846ab057fa5544ed7ee433ae2a8f9cb49249d14d5f34f`
- combined base64 characters: 42164
- combined base64 SHA-256: `ef577586fda95b9be8c22a170fa5a90eb0577bcfc621fe41b40890a029cadc93`
- transport parts: 7 of 7 verified
- reconstructed JSON records: 122
- unique original identifiers: 122
- reverse reconstruction: PASS

The compressed transport is not a rewritten substitute. It deterministically reconstructs the original raw JSON byte for byte and is governed by the raw source SHA-256.

## Stable baseline addressing

The baseline address manifest contains exactly:

`P01.5::B::0001` through `P01.5::B::0122`

Each entry preserves:

- immutable source ordinal
- original identifier
- canonical record SHA-256

Addresses are unique. Original identifiers are unique. Routing state is `UNROUTED`. All destination fields are blank.

## Governing artifacts

- `audit/baseline-source/pmp-current-permanent-limitation-register-v3-final.transport-manifest.json`
- `audit/baseline-source/pmp-current-permanent-limitation-register-v3-final.part-001.b64`
- `audit/baseline-source/pmp-current-permanent-limitation-register-v3-final.part-002.b64`
- `audit/baseline-source/pmp-current-permanent-limitation-register-v3-final.part-003.b64`
- `audit/baseline-source/pmp-current-permanent-limitation-register-v3-final.part-004.b64`
- `audit/baseline-source/pmp-current-permanent-limitation-register-v3-final.part-005.b64`
- `audit/baseline-source/pmp-current-permanent-limitation-register-v3-final.part-006.b64`
- `audit/baseline-source/pmp-current-permanent-limitation-register-v3-final.part-007.b64`
- `audit/Packet_01.5_Baseline_Address_Manifest_v1.json`
- `tools/verify_packet_01_5_baseline_source.py`
- `audit/Packet_01.5_Baseline_Source_Verification_v1.md`
- `audit/Packet_01.5_Baseline_Source_Verification_v1.json`

## Gate effect

The baseline-source blocker recorded by Independent Verification v1 is resolved.

No routing, applicability classification, semantic merge, deletion, or record closure occurred.

END PACKET 01.5 — ROUTING PREPARATION GATE BASELINE SOURCE ADDENDUM v1
