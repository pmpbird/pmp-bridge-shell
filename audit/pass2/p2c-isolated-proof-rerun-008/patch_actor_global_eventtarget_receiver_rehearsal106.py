#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess


TARGETS = {
    "pmp-current-screen-pointer-v1.js": {
        "before_bytes": 11609,
        "before_sha256": "c6473b7c6237d25c64a91559a28c3539d8f0d7113dcbaff443191c359f05ae5a",
        "old": "    addEventListener('load', () => [100, 500, 1200, 2500].forEach(t => setTimeout(() => { scan(); restore(0); }, t)));",
        "new": "    globalThis.addEventListener('load', () => [100, 500, 1200, 2500].forEach(t => setTimeout(() => { scan(); restore(0); }, t)));",
    },
    "pmp-reload-world-from-map-v1.js": {
        "before_bytes": 5923,
        "before_sha256": "e612c618c3cf98ebfde5974e197bdc6e6a973ccfe60e6e36b1ce0c00ed99e235",
        "old": "    addEventListener('load', scan);",
        "new": "    globalThis.addEventListener('load', scan);",
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-root", type=pathlib.Path, required=True)
    parser.add_argument("--evidence-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()

    source_root = args.bundle_root / "repair009-normalized-sources-002"
    manifest_path = args.bundle_root / "repair009-normalized-source-manifest-002.json"
    policy_path = args.bundle_root / "policy-template.json"
    for required in (source_root, manifest_path, policy_path):
        if not required.exists():
            raise SystemExit(f"REHEARSAL106_REQUIRED_INPUT_MISSING:{required}")

    manifest_before = manifest_path.read_bytes()
    policy_before = policy_path.read_bytes()
    manifest = json.loads(manifest_before)
    policy = json.loads(policy_before)
    if manifest.get("type") != "PMP_REPAIR009_NORMALIZED_SOURCE_MANIFEST_002":
        raise SystemExit("REHEARSAL106_NORMALIZED_MANIFEST_TYPE_INVALID")
    if policy.get("type") != "PMP_P2C_PRODUCTION_ENFORCEMENT_POLICY_CANDIDATE_002":
        raise SystemExit("REHEARSAL106_POLICY_TYPE_INVALID")

    bare_pattern = re.compile(r"(?<![\w.$])addEventListener\(")
    bare_before = []
    for candidate in sorted(source_root.rglob("*")):
        if not candidate.is_file():
            continue
        text = candidate.read_text()
        for match in bare_pattern.finditer(text):
            bare_before.append({"path": candidate.relative_to(source_root).as_posix(), "offset": match.start()})
    if [row["path"] for row in bare_before] != sorted(TARGETS):
        raise SystemExit("REHEARSAL106_BARE_EVENTTARGET_SET_INVALID:" + json.dumps(bare_before, sort_keys=True))

    manifest_by_path = {row["path"]: row for row in manifest.get("records", [])}
    policy_by_path = {row["path"]: row for row in policy.get("actors", [])}
    records = []
    for relative, expected in TARGETS.items():
        target = source_root / relative
        data_before = target.read_bytes()
        digest_before = sha256(data_before)
        if len(data_before) != expected["before_bytes"] or digest_before != expected["before_sha256"]:
            raise SystemExit(f"REHEARSAL106_SOURCE_IDENTITY_INVALID:{relative}:{len(data_before)}:{digest_before}")
        text = data_before.decode("utf-8")
        if text.count(expected["old"]) != 1 or expected["new"] in text:
            raise SystemExit(f"REHEARSAL106_SOURCE_ANCHOR_INVALID:{relative}")

        manifest_row = manifest_by_path.get(relative)
        policy_actor = policy_by_path.get(relative)
        if not manifest_row or manifest_row.get("transformed_sha256") != digest_before:
            raise SystemExit(f"REHEARSAL106_MANIFEST_IDENTITY_INVALID:{relative}")
        if not policy_actor or policy_actor.get("sha256") != digest_before:
            raise SystemExit(f"REHEARSAL106_POLICY_IDENTITY_INVALID:{relative}")

        target.write_text(text.replace(expected["old"], expected["new"], 1))
        syntax = subprocess.run(
            ["node", "--check", str(target)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        if syntax.returncode != 0:
            raise SystemExit(f"REHEARSAL106_NODE_CHECK_FAILED:{relative}:{syntax.stdout[-4000:]}")
        data_after = target.read_bytes()
        digest_after = sha256(data_after)
        manifest_row["transformed_sha256"] = digest_after
        manifest_row["transformed_bytes"] = len(data_after)
        policy_actor["sha256"] = digest_after
        records.append({
            "path": relative,
            "before_bytes": len(data_before),
            "before_sha256": digest_before,
            "after_bytes": len(data_after),
            "after_sha256": digest_after,
            "change": "BARE_GLOBAL_ADDEVENTLISTENER_TO_EXPLICIT_GLOBALTHIS_RECEIVER",
            "node_syntax_check": "PASS",
        })

    bare_after = []
    for candidate in sorted(source_root.rglob("*")):
        if not candidate.is_file():
            continue
        for match in bare_pattern.finditer(candidate.read_text()):
            bare_after.append({"path": candidate.relative_to(source_root).as_posix(), "offset": match.start()})
    if bare_after:
        raise SystemExit("REHEARSAL106_RESIDUAL_BARE_EVENTTARGET_CALLS:" + json.dumps(bare_after, sort_keys=True))

    manifest["global_eventtarget_receiver_repair"] = "EXPLICIT_GLOBALTHIS_RECEIVER"
    manifest["global_eventtarget_receiver_repair_record_count"] = len(records)
    policy["global_eventtarget_receiver_repair"] = "EXPLICIT_GLOBALTHIS_RECEIVER"
    policy["global_eventtarget_receiver_repair_record_count"] = len(records)
    manifest_path.write_bytes(json_bytes(manifest))
    policy_path.write_bytes(json_bytes(policy))

    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence = {
        "type": "PMP_P2C_ACTOR_GLOBAL_EVENTTARGET_RECEIVER_REPAIR_106",
        "status": "PASS",
        "scope": "DISPOSABLE_NORMALIZED_ACTOR_PAYLOAD_ONLY",
        "cause": "STRICT_BARE_GLOBAL_EVENTTARGET_CALL_LOST_RECEIVER_BEFORE_ACTOR_EXPORT_BINDING",
        "repair": "EXPLICIT_GLOBALTHIS_EVENTTARGET_RECEIVER",
        "record_count": len(records),
        "records": records,
        "bare_global_add_event_listener_calls_before": len(bare_before),
        "bare_global_add_event_listener_calls_after": len(bare_after),
        "manifest_sha256_before": sha256(manifest_before),
        "manifest_sha256_after": sha256(manifest_path.read_bytes()),
        "policy_sha256_before": sha256(policy_before),
        "policy_sha256_after": sha256(policy_path.read_bytes()),
        "authority_gate_changed": False,
        "actor_capabilities_changed": False,
        "unknown_actor_policy_weakened": False,
        "unauthorized_capability_policy_weakened": False,
        "current_map_changed": False,
        "persisted_data_changed": False,
        "production_changed": False,
        "production_activation_authorized": False,
        "formal_proof_executed": False,
    }
    if len(records) != 2:
        raise SystemExit("REHEARSAL106_REPAIR_COVERAGE_INVALID")
    evidence_path = args.evidence_dir / "actor-global-eventtarget-receiver-repair-106.json"
    evidence_path.write_bytes(json_bytes(evidence))
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
