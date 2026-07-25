#!/usr/bin/env python3
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "pmp-route-guardian-current-loader-v22.html"
MANIFEST = ROOT / "pmp-runtime-integrity-manifest-v1.json"
BOOTSTRAP = ROOT / "pmp-app-current.html"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def main():
    runtime = RUNTIME.read_bytes()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    record = next(item for item in manifest["records"] if item["path"] == RUNTIME.name)
    record["bytes"] = len(runtime)
    record["sha256_hex"] = sha256(runtime)
    record["git_blob_sha"] = git_blob(runtime)
    manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode()
    MANIFEST.write_bytes(manifest_bytes)

    bootstrap = BOOTSTRAP.read_text(encoding="utf-8")
    replacement = "const MANIFEST_SHA256='" + sha256(manifest_bytes) + "';"
    updated, count = re.subn(r"const MANIFEST_SHA256='[0-9a-f]{64}';", replacement, bootstrap, count=1)
    assert count == 1, "bootstrap manifest seal not found exactly once"
    BOOTSTRAP.write_text(updated, encoding="utf-8")
    print("PASS: Unit 2 runtime integrity record and root manifest seal regenerated")


if __name__ == "__main__":
    main()
