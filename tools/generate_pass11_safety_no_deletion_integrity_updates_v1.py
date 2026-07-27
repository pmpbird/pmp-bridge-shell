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
INNER = ROOT / "pmp-current-inner-cleanbug-rgcontrols-v23.html"
RUNTIME_PATHS = (
    "pmp-safety-no-deletion-guard-v1.js",
    "pmp-master-bank-inventory-router-v1.js",
    "pmp-connections-bank-packet-delete-v1.js",
    "pmp-current-inner-cleanbug-rgcontrols-v23.html",
)
BOUNDARY_TAG = (
    '<script src="pmp-bank-continuous-run-owner-boundary-v1.js?'
    'fresh=pass9-unit3-owner-boundary-20260726A"></script>'
)
GUARD_TAG = (
    '<script src="pmp-safety-no-deletion-guard-v1.js?'
    'fresh=pass11-safety-no-deletion-20260727A"></script>'
)
OLD_ROUTER = (
    "pmp-master-bank-inventory-router-v1.js?"
    "fresh=pass9-unit3-owner-boundary-20260726A"
)
NEW_ROUTER = (
    "pmp-master-bank-inventory-router-v1.js?"
    "fresh=pass11-safety-no-deletion-20260727A"
)
OLD_CONNECTIONS = (
    "pmp-connections-bank-packet-delete-v1.js?"
    "fresh=connections-bank-delete-selected-v1-20260624T1238Z"
)
NEW_CONNECTIONS = (
    "pmp-connections-bank-packet-delete-v1.js?"
    "fresh=pass11-recoverable-archive-20260727A"
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
                "text/html" if path.endswith(".html") else "text/javascript"
            ),
            "execution_class": (
                "EXECUTABLE_DOCUMENT"
                if path.endswith(".html")
                else "EXECUTABLE_SCRIPT"
            ),
            "enforcement": "SERVICE_WORKER_PRE_RESPONSE_SHA256",
        }
    )
    return result


def main() -> None:
    inner = INNER.read_text("utf-8")
    if GUARD_TAG not in inner:
        assert inner.count(BOUNDARY_TAG) == 1
        inner = inner.replace(BOUNDARY_TAG, BOUNDARY_TAG + GUARD_TAG, 1)
    assert inner.count(GUARD_TAG) == 1
    if NEW_ROUTER not in inner:
        assert inner.count(OLD_ROUTER) == 1
        inner = inner.replace(OLD_ROUTER, NEW_ROUTER, 1)
    if NEW_CONNECTIONS not in inner:
        assert inner.count(OLD_CONNECTIONS) == 1
        inner = inner.replace(OLD_CONNECTIONS, NEW_CONNECTIONS, 1)
    assert inner.count(NEW_ROUTER) == 1
    assert inner.count(NEW_CONNECTIONS) == 1
    INNER.write_text(inner, "utf-8")

    manifest = json.loads(MANIFEST.read_text("utf-8"))
    index = {row["path"]: row for row in manifest["records"]}
    for runtime_path in RUNTIME_PATHS:
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
        json.dumps(
            identity, sort_keys=True, separators=(",", ":")
        ).encode()
    )
    manifest_bytes = (
        json.dumps(
            manifest, indent=2, sort_keys=True, ensure_ascii=False
        )
        + "\n"
    ).encode()
    MANIFEST.write_bytes(manifest_bytes)

    manifest_sha = sha(manifest_bytes)
    seal = json.loads(SEAL.read_text("utf-8"))
    seal.update(
        manifest_bytes=len(manifest_bytes),
        manifest_sha256=manifest_sha,
        runtime_source_set_sha256=manifest["runtime_source_set_sha256"],
        sealed_branch="agent/pass11-safety-no-deletion-complete-v1",
        pass11_context=(
            "Pass 11 installs one load-inert safety and no-deletion guard, "
            "keeps active deletion denied by default, changes the Connections "
            "Bank action to recoverable archive, retains exact packet metadata "
            "and IndexedDB binary payloads, and requires exact backup, "
            "rollback, owner scope, expected version, append-only receipts, "
            "and single-use exceptional delete authority. No live user data "
            "is read or changed by the implementation or proof."
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
        "PASS: Pass 11 safety and no-deletion runtime integrity "
        "identities regenerated"
    )


if __name__ == "__main__":
    main()
