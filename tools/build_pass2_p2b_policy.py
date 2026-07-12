#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ACTORS = [
    ("audit/pass2/fixtures/p2b-known-storage-actor.js", "fixture_storage", "fixture-owner", "fixture", ["storage_write"]),
    ("audit/pass2/fixtures/p2b-known-dom-actor.js", "fixture_dom", "fixture-owner", "fixture", ["dom_write"]),
    ("audit/pass2/fixtures/p2b-known-limited-actor.js", "fixture_limited", "fixture-owner", "fixture", []),
    ("audit/pass2/fixtures/p2b-known-async-actor.js", "fixture_async", "fixture-owner", "fixture", ["timer_schedule", "storage_write"]),
]
CANONICAL_SOURCE_MANIFEST = "pmp-actor-source-manifest-v1.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("utf-8") + data).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("pmp-actor-authority-policy-v1.json"))
    parser.add_argument("--manifest-output", type=Path, default=Path(CANONICAL_SOURCE_MANIFEST))
    args = parser.parse_args()

    actors = []
    records = []
    for path, role, owner, phase, capabilities in ACTORS:
        data = (args.root / path).read_bytes()
        digest = sha256(data)
        actors.append({
            "path": path,
            "sha256": digest,
            "role": role,
            "owner": owner,
            "phase": phase,
            "stop_condition": "bounded_fixture",
            "capabilities": capabilities,
        })
        records.append({
            "path": path,
            "bytes": len(data),
            "git_blob_sha": git_blob_sha(data),
            "sha256_hex": digest,
            "execution_class": "P2B_CERTIFICATION_FIXTURE_ACTOR",
            "enforcement": "PMP_ACTOR_AUTHORITY_GATE_PRE_EXECUTION_SHA256",
        })

    source_manifest = {
        "type": "PMP_ACTOR_SOURCE_MANIFEST_V1",
        "version": "1.0.0-pass2-p2b-fixtures",
        "algorithm": "SHA-256",
        "status": "P2B_CERTIFICATION_MANIFEST_NOT_ACTIVE_CHAIN",
        "records": records,
        "record_count": len(records),
        "unknown_source_policy": "BLOCK_BEFORE_ACTOR_TOKEN",
        "truth_boundary": "This manifest independently freezes the exact fixture actor source bytes used to certify the P2-B gate. Production active-chain actor identities remain P2-C.",
        "pass2_complete": False,
        "pass3_started": False,
    }
    policy = {
        "type": "PMP_ACTOR_AUTHORITY_POLICY_V1",
        "version": "1.0.0-pass2-p2b-fixture-policy",
        "algorithm": "SHA-256",
        "status": "P2B_CERTIFICATION_POLICY_NOT_ACTIVE_CHAIN",
        "source_manifest": CANONICAL_SOURCE_MANIFEST,
        "unknown_actor_policy": "BLOCK_BEFORE_SIDE_EFFECT",
        "unauthorized_capability_policy": "BLOCK_BEFORE_SIDE_EFFECT",
        "protected_capabilities": [
            "storage_write", "storage_delete", "storage_clear", "dom_write", "dom_delete",
            "script_injection", "resource_target_change", "document_write", "navigation",
            "network_fetch", "indexeddb_open", "indexeddb_delete", "cache_open", "cache_delete",
            "timer_schedule", "event_listener"
        ],
        "actors": actors,
        "truth_boundary": "This P2-B policy certifies the gate engine and adversarial fixtures. Active-chain actor policy and integration remain P2-C.",
        "pass2_complete": False,
        "pass3_started": False,
    }

    write_json(args.manifest_output, source_manifest)
    write_json(args.output, policy)
    print(json.dumps({
        "status": "PASS",
        "actors": len(actors),
        "policy": str(args.output),
        "source_manifest": str(args.manifest_output),
        "source_manifest_reference": CANONICAL_SOURCE_MANIFEST,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
