#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "pmp-runtime-integrity-manifest-v1.json"
SEAL = ROOT / "audit/a003-manifest-seal.json"
BOOTSTRAP = ROOT / "pmp-app-current.html"
NEW_RECORDS = (
    "pmp-migration-inactive-gate-v1.js",
    "pmp-migration-plan-v1.json",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob(data: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(data)).encode() + b"\0" + data
    ).hexdigest()


def record(path: str, existing: dict | None = None) -> dict:
    data = (ROOT / path).read_bytes()
    digest = hashlib.sha256(data).digest()
    result = dict(existing or {})
    result.update(
        {
            "path": path,
            "bytes": len(data),
            "git_blob_sha": blob(data),
            "sha256_hex": digest.hex(),
            "sha256_base64": base64.b64encode(digest).decode(),
            "sri": "sha256-" + base64.b64encode(digest).decode(),
            "mime_type": (
                "application/json"
                if path.endswith(".json")
                else "text/javascript"
            ),
            "execution_class": (
                "RUNTIME_DATA"
                if path.endswith(".json")
                else "EXECUTABLE_SCRIPT"
            ),
            "enforcement": "SERVICE_WORKER_PRE_RESPONSE_SHA256",
        }
    )
    return result


def main() -> None:
    manifest = json.loads(MANIFEST.read_text("utf-8"))
    index = {row["path"]: row for row in manifest["records"]}
    for runtime_path in NEW_RECORDS:
        index[runtime_path] = record(runtime_path, index.get(runtime_path))
    manifest["records"] = [index[item] for item in sorted(index)]
    manifest["counts"]["runtime_records"] = len(manifest["records"])
    manifest["counts"]["executable_records"] = sum(
        1
        for row in manifest["records"]
        if row["execution_class"] != "STYLE_SOURCE"
    )
    identity = {
        "records": [
            (row["path"], row["sha256_hex"])
            for row in manifest.get("records", [])
        ],
        "historical_records": [
            (row["path"], row.get("repository_ref"), row["sha256_hex"])
            for row in manifest.get("historical_records", [])
        ],
        "external_records": [
            (row["url"], row["sha256_hex"])
            for row in manifest.get("external_records", [])
        ],
        "root_trust_anchors": manifest.get("root_trust_anchors", []),
        "policy": {
            "algorithm": manifest.get("algorithm"),
            "unlisted_executable_policy": manifest.get(
                "unlisted_executable_policy"
            ),
            "network_policy": manifest.get("network_policy"),
        },
    }
    manifest["runtime_source_set_sha256"] = sha(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    )
    manifest_bytes = (
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False)
        + "\n"
    ).encode()
    MANIFEST.write_bytes(manifest_bytes)

    manifest_sha = sha(manifest_bytes)
    seal = json.loads(SEAL.read_text("utf-8"))
    seal.update(
        manifest_bytes=len(manifest_bytes),
        manifest_sha256=manifest_sha,
        runtime_source_set_sha256=manifest["runtime_source_set_sha256"],
        sealed_branch="agent/pass12-migration-plan-safe-closure-v1",
        pass12_context=(
            "Pass 12 adds a static plan and an unreferenced inactive helper "
            "to the complete A-003 source manifest. The current runtime does "
            "not load the helper. It contains no production storage or "
            "network API and denies every production migration request. "
            "No production storage or persisted user data was read or changed."
        ),
    )
    SEAL.write_text(
        json.dumps(seal, indent=2, sort_keys=True) + "\n", "utf-8"
    )

    bootstrap = BOOTSTRAP.read_text("utf-8")
    updated, count = re.subn(
        r"const MANIFEST_SHA256='[0-9a-f]{64}';",
        f"const MANIFEST_SHA256='{manifest_sha}';",
        bootstrap,
        count=1,
    )
    assert count == 1
    BOOTSTRAP.write_text(updated, "utf-8")
    print(
        "PASS: Pass 12 inactive migration plan exact source identities "
        "regenerated without loading or activating the helper"
    )


if __name__ == "__main__":
    main()
