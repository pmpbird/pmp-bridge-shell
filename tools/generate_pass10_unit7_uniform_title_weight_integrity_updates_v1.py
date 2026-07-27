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
RUNTIME_PATHS = (
    "pmp-bank-screen-owner-v1.js",
    "pmp-current-inner-cleanbug-rgcontrols-v23.html",
)
OLD_FRESH = (
    "pmp-bank-screen-owner-v1.js?"
    "fresh=pass9-unit3-continuous-run-owner-20260726A"
)
NEW_FRESH = (
    "pmp-bank-screen-owner-v1.js?"
    "fresh=pass10-unit7-uniform-title-weight-20260727A"
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
            "mime_type": "text/html" if path.endswith(".html") else "text/javascript",
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
    inner_path = ROOT / RUNTIME_PATHS[1]
    inner = inner_path.read_text("utf-8")
    if NEW_FRESH not in inner:
        assert inner.count(OLD_FRESH) == 1
        inner = inner.replace(OLD_FRESH, NEW_FRESH, 1)
        inner_path.write_text(inner, "utf-8")
    assert inner.count(NEW_FRESH) == 1

    manifest = json.loads(MANIFEST.read_text("utf-8"))
    index = {row["path"]: row for row in manifest["records"]}
    for path in RUNTIME_PATHS:
        index[path] = record(path, index.get(path))
    manifest["records"] = [index[path] for path in sorted(index)]
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
        sealed_branch="agent/pass10-unit7-uniform-title-weight-v1",
        pass10_context=(
            "P10-U7U applies the exact Level 3+ font weight 950 to the six "
            "Continuous Run owner titles before Level 3: Run State Summary, "
            "Lossless Slots ZIP Import, Staging Transfer Store, Bank Project "
            "Registry, Level 1, and Level 2. It changes only title typography "
            "and preserves every card, heading node, control, handler, "
            "readiness gate, Level 3+ single-card presentation, and canonical "
            "order. It does not read, write, delete, migrate, or activate "
            "persisted data."
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
    print("PASS: P10-U7U uniform title weight runtime integrity identities regenerated")


if __name__ == "__main__":
    main()
