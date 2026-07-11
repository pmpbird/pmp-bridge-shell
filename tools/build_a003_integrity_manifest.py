#!/usr/bin/env python3
"""Build the A-003 runtime source-byte integrity manifest.

The generator intentionally excludes the bootstrap document because a document cannot
verify its own bytes before execution. All downstream runtime source files are hashed
with SHA-256 and Git blob SHA-1 identities. The script also inventories Current Map
routes, local literal references, the historical Home payload, and external scripts.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.request
from typing import Any, Iterable

MANIFEST_TYPE = "PMP_RUNTIME_INTEGRITY_MANIFEST_V1"
VERSION = "20260711A-A003-PROBE"
DEFAULT_OUTPUT = "a003-generated-integrity-manifest.json"
DEFAULT_REPORT = "a003-integrity-probe-report.json"
ROOT_TRUST_ANCHOR = "pmp-app-current.html"
MANIFEST_PATH = "pmp-runtime-integrity-manifest-v1.json"
MAP_PATH = "pmp-current-map-v12.json"
RESOLVER_PATH = "pmp-current-route-resolver-v1.js"
INTEGRITY_SW_PATH = "pmp-integrity-service-worker-v1.js"
HISTORICAL_HOME_COMMIT = "7ac7213aeeeb8bb55692a4985e0fa80a547cff4e"
HISTORICAL_HOME_PATH = "pmp-home-single-v6.html"
JSZIP_URL = "https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js"
RUNTIME_EXTENSIONS = {".html", ".htm", ".js", ".mjs", ".json", ".wasm", ".css"}
EXECUTABLE_EXTENSIONS = {".html", ".htm", ".js", ".mjs", ".json", ".wasm"}
EXCLUDED_DIRS = {".git", ".github", "audit", "tools", "node_modules", "__pycache__"}
EXCLUDED_FILES = {ROOT_TRUST_ANCHOR, MANIFEST_PATH}

LOCAL_REF_RE = re.compile(
    r"(?P<quote>['\"])(?P<path>(?![a-z]+:|//|/|#)[A-Za-z0-9._/-]+\.(?:html?|m?js|json|wasm|css))(?:\?[^'\"]*)?(?:#[^'\"]*)?(?P=quote)",
    re.IGNORECASE,
)
SCRIPT_SRC_RE = re.compile(
    r"<script\b[^>]*\bsrc\s*=\s*(['\"])(?P<src>.*?)\1",
    re.IGNORECASE | re.DOTALL,
)


def sha256_bytes(data: bytes) -> dict[str, str]:
    digest = hashlib.sha256(data).digest()
    return {
        "sha256_hex": digest.hex(),
        "sha256_base64": base64.b64encode(digest).decode("ascii"),
        "sri": "sha256-" + base64.b64encode(digest).decode("ascii"),
    }


def git_blob_sha(data: bytes) -> str:
    prefix = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(prefix + data).hexdigest()


def execution_class(path: str) -> str:
    suffix = Path(path).suffix.lower()
    return {
        ".html": "EXECUTABLE_DOCUMENT",
        ".htm": "EXECUTABLE_DOCUMENT",
        ".js": "EXECUTABLE_SCRIPT",
        ".mjs": "EXECUTABLE_MODULE",
        ".json": "RUNTIME_DATA",
        ".wasm": "EXECUTABLE_WASM",
        ".css": "STYLE_SOURCE",
    }.get(suffix, "RUNTIME_SOURCE")


def iter_runtime_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDED_DIRS)
        base = Path(dirpath)
        for filename in sorted(filenames):
            path = base / filename
            rel = path.relative_to(root).as_posix()
            if rel in EXCLUDED_FILES:
                continue
            if path.suffix.lower() not in RUNTIME_EXTENSIONS:
                continue
            yield path


def record_for_file(root: Path, path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    rel = path.relative_to(root).as_posix()
    hashes = sha256_bytes(data)
    return {
        "path": rel,
        "bytes": len(data),
        "git_blob_sha": git_blob_sha(data),
        **hashes,
        "mime_type": mimetypes.guess_type(rel)[0] or "application/octet-stream",
        "execution_class": execution_class(rel),
        "enforcement": "SERVICE_WORKER_PRE_RESPONSE_SHA256",
    }


def flatten_map_paths(value: Any, out: set[str]) -> None:
    if isinstance(value, dict):
        path = value.get("path")
        if isinstance(path, str):
            out.add(path.split("?", 1)[0].split("#", 1)[0])
        for child in value.values():
            flatten_map_paths(child, out)
    elif isinstance(value, list):
        for child in value:
            flatten_map_paths(child, out)


def discover_local_references(root: Path, records: list[dict[str, Any]]) -> dict[str, Any]:
    existing = {r["path"] for r in records} | {ROOT_TRUST_ANCHOR, MANIFEST_PATH}
    references: dict[str, set[str]] = {}
    missing: dict[str, set[str]] = {}
    for record in records:
        path = root / record["path"]
        if path.suffix.lower() not in {".html", ".htm", ".js", ".mjs", ".json", ".css"}:
            continue
        try:
            text = path.read_text("utf-8")
        except UnicodeDecodeError:
            continue
        found: set[str] = set()
        for match in LOCAL_REF_RE.finditer(text):
            candidate = match.group("path").lstrip("./")
            found.add(candidate)
        if found:
            references[record["path"]] = found
            absent = {p for p in found if p not in existing}
            if absent:
                missing[record["path"]] = absent
    return {
        "references": {k: sorted(v) for k, v in sorted(references.items())},
        "missing": {k: sorted(v) for k, v in sorted(missing.items())},
        "missing_count": sum(len(v) for v in missing.values()),
    }


def discover_external_scripts(root: Path, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    found: dict[str, set[str]] = {}
    for record in records:
        path = root / record["path"]
        if path.suffix.lower() not in {".html", ".htm"}:
            continue
        try:
            text = path.read_text("utf-8")
        except UnicodeDecodeError:
            continue
        for match in SCRIPT_SRC_RE.finditer(text):
            src = match.group("src").strip()
            if re.match(r"^https?://", src, re.IGNORECASE):
                found.setdefault(src, set()).add(record["path"])
    result = []
    for url, consumers in sorted(found.items()):
        result.append({"url": url, "consumers": sorted(consumers)})
    return result


def fetch_external(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "PMP-A003-Integrity-Builder/1"})
    with urllib.request.urlopen(req, timeout=30) as response:
        data = response.read()
    return {"url": url, "bytes": len(data), **sha256_bytes(data)}


def historical_home_record(root: Path) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", "show", f"{HISTORICAL_HOME_COMMIT}:{HISTORICAL_HOME_PATH}"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace"))
    data = proc.stdout
    return {
        "path": HISTORICAL_HOME_PATH,
        "repository_ref": HISTORICAL_HOME_COMMIT,
        "bytes": len(data),
        "git_blob_sha": git_blob_sha(data),
        **sha256_bytes(data),
        "execution_class": "HISTORICAL_EXECUTABLE_DOCUMENT",
        "enforcement": "HOME_RESTORE_PRE_DOCUMENT_WRITE_SHA256",
    }


def build(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    records = [record_for_file(root, p) for p in iter_runtime_files(root)]
    records.sort(key=lambda r: r["path"])
    index = {r["path"]: r for r in records}

    map_data = json.loads((root / MAP_PATH).read_text("utf-8"))
    declared_paths: set[str] = set()
    flatten_map_paths(map_data, declared_paths)
    declared_paths.discard(ROOT_TRUST_ANCHOR)
    declared_status = []
    for path in sorted(declared_paths):
        declared_status.append({
            "path": path,
            "covered": path in index,
            "sha256_hex": index.get(path, {}).get("sha256_hex"),
        })

    refs = discover_local_references(root, records)
    external_scripts = discover_external_scripts(root, records)

    external_records: list[dict[str, Any]] = []
    external_errors: list[dict[str, str]] = []
    for item in external_scripts:
        try:
            fetched = fetch_external(item["url"])
            fetched["consumers"] = item["consumers"]
            fetched["enforcement"] = "SRI_REQUIRED"
            external_records.append(fetched)
        except Exception as exc:  # noqa: BLE001
            external_errors.append({"url": item["url"], "error": str(exc), "consumers": item["consumers"]})

    historical = historical_home_record(root)
    current_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()

    manifest = {
        "type": MANIFEST_TYPE,
        "version": VERSION,
        "repository": "pmpbird/pmp-bridge-shell",
        "source_commit": current_head,
        "algorithm": "SHA-256",
        "root_trust_anchors": [
            {
                "path": ROOT_TRUST_ANCHOR,
                "classification": "BOOTSTRAP_ROOT_NOT_SELF_VERIFIABLE",
                "rule": "This is the only application bootstrap source excluded from downstream manifest self-enforcement."
            }
        ],
        "protected_bootstrap_sources": [MAP_PATH, RESOLVER_PATH, INTEGRITY_SW_PATH],
        "manifest_path": MANIFEST_PATH,
        "unlisted_executable_policy": "FAIL_CLOSED",
        "network_policy": "VERIFY_NETWORK_BYTES_BEFORE_RESPONSE; VERIFIED_HASH_MATCH_CACHE_ONLY_ON_NETWORK_FAILURE",
        "records": records,
        "historical_records": [historical],
        "external_records": external_records,
        "counts": {
            "runtime_records": len(records),
            "executable_records": sum(Path(r["path"]).suffix.lower() in EXECUTABLE_EXTENSIONS for r in records),
            "style_records": sum(Path(r["path"]).suffix.lower() == ".css" for r in records),
            "map_declared_paths": len(declared_status),
            "map_declared_covered": sum(item["covered"] for item in declared_status),
            "historical_records": 1,
            "external_records": len(external_records),
            "external_errors": len(external_errors),
        },
    }
    manifest_bytes = (json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    manifest["self_digest_for_generated_bytes"] = sha256_bytes(manifest_bytes)

    report = {
        "type": "PMP_A003_INTEGRITY_PROBE_REPORT_V1",
        "source_commit": current_head,
        "root_trust_anchor": ROOT_TRUST_ANCHOR,
        "manifest_path": MANIFEST_PATH,
        "map_declared_status": declared_status,
        "map_declared_uncovered": [item["path"] for item in declared_status if not item["covered"]],
        "local_reference_missing": refs["missing"],
        "local_reference_missing_count": refs["missing_count"],
        "external_scripts": external_scripts,
        "external_records": external_records,
        "external_errors": external_errors,
        "historical_home": historical,
        "counts": manifest["counts"],
        "decision": "PASS_PROBE" if all(item["covered"] for item in declared_status) and not external_errors else "PROBE_REQUIRES_RECONCILIATION",
    }
    return manifest, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    manifest, report = build(root)
    Path(args.output).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", "utf-8")
    Path(args.report).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", "utf-8")
    print(json.dumps({
        "manifest": args.output,
        "report": args.report,
        "source_commit": manifest["source_commit"],
        "counts": manifest["counts"],
        "decision": report["decision"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
