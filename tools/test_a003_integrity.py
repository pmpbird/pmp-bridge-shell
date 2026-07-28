#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "pmp-runtime-integrity-manifest-v1.json"
SEAL = ROOT / "audit/a003-manifest-seal.json"
BOOTSTRAP = ROOT / "pmp-app-current.html"
MAP = ROOT / "pmp-current-map-v12.json"
ROOT_ANCHOR = "pmp-app-current.html"
MANIFEST_PATH = "pmp-runtime-integrity-manifest-v1.json"
RUNTIME_EXTENSIONS = {".html", ".htm", ".js", ".mjs", ".json", ".wasm", ".css"}
EXCLUDED_DIRS = {".git", ".github", "audit", "tools", "node_modules", "__pycache__"}
EXCLUDED_FILES = {ROOT_ANCHOR, MANIFEST_PATH}
REGISTER_RE = re.compile(r"(?:navigator\s*\.\s*)?serviceWorker\s*\.\s*register\s*\(", re.IGNORECASE)
SCRIPT_SRC_RE = re.compile(r"<script\b[^>]*\bsrc\s*=\s*(['\"])(?P<src>.*?)\1", re.IGNORECASE | re.DOTALL)
CASE_DISTINCT_GIT_PATHS = {"Index.html", "index.html"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def source_bytes(path: str) -> bytes:
    target = ROOT / path
    if target.is_file():
        return target.read_bytes()
    if path in CASE_DISTINCT_GIT_PATHS:
        return subprocess.check_output(["git", "show", f"HEAD:{path}"], cwd=ROOT)
    raise FileNotFoundError(path)


def source_text(path: str) -> str:
    return source_bytes(path).decode("utf-8")


def flatten_paths(value: Any, out: set[str]) -> None:
    if isinstance(value, dict):
        if isinstance(value.get("path"), str):
            out.add(value["path"].split("?", 1)[0].split("#", 1)[0])
        for child in value.values():
            flatten_paths(child, out)
    elif isinstance(value, list):
        for child in value:
            flatten_paths(child, out)


def runtime_paths() -> set[str]:
    result: set[str] = set()
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        base = Path(dirpath)
        for name in filenames:
            path = base / name
            rel = path.relative_to(ROOT).as_posix()
            if rel in EXCLUDED_FILES or path.suffix.lower() not in RUNTIME_EXTENSIONS:
                continue
            result.add(rel)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="a003-repository-test-result.json")
    args = parser.parse_args()

    tests: list[dict[str, Any]] = []
    findings: dict[str, Any] = {}

    def check(name: str, condition: bool, evidence: Any = None) -> None:
        tests.append({"name": name, "pass": bool(condition), "evidence": evidence})

    manifest_bytes = MANIFEST.read_bytes()
    manifest = json.loads(manifest_bytes)
    seal = json.loads(SEAL.read_text("utf-8"))
    bootstrap = BOOTSTRAP.read_text("utf-8")
    current_map = json.loads(MAP.read_text("utf-8"))
    records = manifest.get("records", [])
    index = {r["path"]: r for r in records}

    actual_manifest_sha = sha256(manifest_bytes)
    root_match = re.search(r"const MANIFEST_SHA256='([0-9a-f]{64})';", bootstrap)
    root_digest = root_match.group(1) if root_match else None
    check("Manifest type and final version", manifest.get("type") == "PMP_RUNTIME_INTEGRITY_MANIFEST_V1" and manifest.get("version") == "20260711A-A003-FINAL", {"type": manifest.get("type"), "version": manifest.get("version")})
    check("Manifest SHA matches seal", actual_manifest_sha == seal.get("manifest_sha256"), {"actual": actual_manifest_sha, "sealed": seal.get("manifest_sha256")})
    check("Manifest SHA matches root bootstrap", actual_manifest_sha == root_digest, {"actual": actual_manifest_sha, "root": root_digest})
    check("Root anchor is explicit and not self-listed", ROOT_ANCHOR not in index and any(r.get("path") == ROOT_ANCHOR and r.get("classification") == "BOOTSTRAP_ROOT_NOT_SELF_VERIFIABLE" for r in manifest.get("root_trust_anchors", [])))
    check("Manifest does not list itself", MANIFEST_PATH not in index)
    check("Manifest fail-closed policy", manifest.get("algorithm") == "SHA-256" and manifest.get("unlisted_executable_policy") == "FAIL_CLOSED")

    exact_failures: list[dict[str, Any]] = []
    for record in records:
        try:
            data = source_bytes(record["path"])
        except FileNotFoundError:
            exact_failures.append({"path": record["path"], "error": "missing"})
            continue
        actual_sha = sha256(data)
        actual_blob = blob_sha(data)
        if actual_sha != record.get("sha256_hex") or actual_blob != record.get("git_blob_sha") or len(data) != record.get("bytes"):
            exact_failures.append({"path": record["path"], "expected_sha256": record.get("sha256_hex"), "actual_sha256": actual_sha, "expected_blob": record.get("git_blob_sha"), "actual_blob": actual_blob, "expected_bytes": record.get("bytes"), "actual_bytes": len(data)})
    check("Every manifest record matches repository bytes", not exact_failures, exact_failures[:20])

    actual_runtime = runtime_paths()
    listed_runtime = set(index)
    actual_runtime.update(CASE_DISTINCT_GIT_PATHS & listed_runtime)
    check("Manifest covers complete generated runtime set", actual_runtime == listed_runtime, {"unlisted": sorted(actual_runtime - listed_runtime), "stale": sorted(listed_runtime - actual_runtime), "actual_count": len(actual_runtime), "listed_count": len(listed_runtime)})

    map_paths: set[str] = set()
    flatten_paths(current_map, map_paths)
    map_paths.discard(ROOT_ANCHOR)
    uncovered_map = sorted(path for path in map_paths if path not in index)
    check("Every Current Map path has an exact manifest record", not uncovered_map and len(map_paths) == 42, {"map_paths": len(map_paths), "uncovered": uncovered_map})
    check("Current Map requires A-003 integrity", current_map.get("route_contract", {}).get("runtime_integrity_required") is True and current_map.get("route_contract", {}).get("unlisted_executable_policy") == "fail_closed")

    historical = (manifest.get("historical_records") or [{}])[0]
    proc = subprocess.run(["git", "show", f"{historical.get('repository_ref')}:{historical.get('path')}"], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    historical_ok = proc.returncode == 0 and sha256(proc.stdout) == historical.get("sha256_hex") and blob_sha(proc.stdout) == historical.get("git_blob_sha")
    check("Historical Home exact bytes match manifest", historical_ok, {"sha256": historical.get("sha256_hex"), "blob": historical.get("git_blob_sha"), "git_error": proc.stderr.decode("utf-8", "replace") if proc.returncode else None})
    check("Current Map historical Home digest agrees", current_map.get("historical_payloads", {}).get("home_v6", {}).get("sha256") == historical.get("sha256_hex"))

    external_records = manifest.get("external_records", [])
    external_by_url = {r["url"]: r for r in external_records}
    external_missing: list[dict[str, str]] = []
    external_sri_invalid: list[str] = []
    for record in external_records:
        expected_sri = "sha256-" + base64.b64encode(bytes.fromhex(record["sha256_hex"])).decode("ascii")
        if record.get("sri") != expected_sri:
            external_sri_invalid.append(record["url"])
        for consumer in record.get("consumers", []):
            text = (ROOT / consumer).read_text("utf-8")
            urls = [m.group("src") for m in SCRIPT_SRC_RE.finditer(text)]
            if record["url"] not in urls:
                external_missing.append({"url": record["url"], "consumer": consumer})
    check("External scripts have exact SHA-256 SRI records", len(external_records) == 3 and not external_sri_invalid and not external_missing, {"records": len(external_records), "invalid_sri": external_sri_invalid, "missing_consumers": external_missing})

    unregistered_external: list[dict[str, str]] = []
    for record in records:
        if not record["path"].lower().endswith((".html", ".htm")):
            continue
        text = source_text(record["path"])
        for match in SCRIPT_SRC_RE.finditer(text):
            src = match.group("src")
            if re.match(r"^https?://", src, re.IGNORECASE) and src not in external_by_url:
                unregistered_external.append({"path": record["path"], "url": src})
    check("Every cross-origin script is declared in manifest", not unregistered_external, unregistered_external)

    registrations: list[dict[str, Any]] = []
    for record in records:
        if Path(record["path"]).suffix.lower() not in {".html", ".htm", ".js", ".mjs"}:
            continue
        try:
            text = source_text(record["path"])
        except UnicodeDecodeError:
            continue
        if REGISTER_RE.search(text):
            registrations.append({"path": record["path"], "matches": len(REGISTER_RE.findall(text))})
    check("No protected downstream source can replace the integrity Service Worker", not registrations, registrations)

    sw_text = (ROOT / "pmp-integrity-service-worker-v1.js").read_text("utf-8")
    resolver_text = (ROOT / "pmp-current-route-resolver-v1.js").read_text("utf-8")
    guardian_text = (ROOT / "pmp-route-guardian-current-loader-v22.html").read_text("utf-8")
    home_text = (ROOT / "pmp-home-single-v6.html").read_text("utf-8")
    check("Integrity worker blocks mismatches and unlisted executable sources", "SOURCE_DIGEST_MISMATCH" in sw_text and "UNLISTED_EXECUTABLE_SOURCE" in sw_text and "MATCHING_VERIFIED_CACHE_ONLY" in sw_text)
    check("Integrity worker enforces external SRI", "EXTERNAL_SRI_MISMATCH" in sw_text and "crossorigin=\"anonymous\"" in sw_text)
    check("Resolver requires manifest-backed role records", "ROLE_INTEGRITY_RECORD_MISSING" in resolver_text and "source_sha256" in resolver_text)
    check("Guardian does not register a replacement Service Worker", "serviceWorker.register" not in guardian_text and "PMP_RUNTIME_INTEGRITY_STATUS_REQUEST" in guardian_text)
    check("Home verifies historical bytes before document write", "historical_home_sha256_mismatch" in home_text and home_text.index("historical_home_sha256_mismatch") < home_text.index("document.write"))

    forbidden_patterns = {
        "localStorage.clear": re.compile(r"localStorage\s*\.\s*clear\s*\("),
        "indexedDB.deleteDatabase": re.compile(r"indexedDB\s*\.\s*deleteDatabase\s*\("),
        "caches wholesale delete loop": re.compile(r"caches\s*\.\s*keys\s*\(.*caches\s*\.\s*delete", re.DOTALL),
    }
    a003_runtime_files = ["pmp-app-current.html", "pmp-current-map-v12.json", "pmp-current-route-resolver-v1.js", "pmp-integrity-service-worker-v1.js", "pmp-route-guardian-current-loader-v22.html", "pmp-home-single-v6.html"]
    destructive: list[dict[str, str]] = []
    for path in a003_runtime_files:
        text = (ROOT / path).read_text("utf-8")
        for label, pattern in forbidden_patterns.items():
            if pattern.search(text):
                destructive.append({"path": path, "pattern": label})
    check("A-003 introduces no destructive data operation", not destructive, destructive)

    findings["manifest_sha256"] = actual_manifest_sha
    findings["manifest_record_count"] = len(records)
    findings["map_path_count"] = len(map_paths)
    findings["external_record_count"] = len(external_records)
    findings["downstream_service_worker_registrations"] = registrations
    findings["exact_byte_failures"] = exact_failures

    passed = sum(1 for item in tests if item["pass"])
    failed = len(tests) - passed
    output = {
        "type": "PMP_A003_REPOSITORY_TEST_RESULT_V1",
        "repair_id": "A-003",
        "status": "PASS" if failed == 0 else "FAIL",
        "tests_total": len(tests),
        "tests_passed": passed,
        "tests_failed": failed,
        "tests": tests,
        "findings": findings,
        "decision": "PASS_REPOSITORY_INTEGRITY_GATE" if failed == 0 else "STOP_A003_REPOSITORY_GATE_FAILED"
    }
    Path(args.output).write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", "utf-8")
    print(json.dumps({"status": output["status"], "tests_total": len(tests), "tests_passed": passed, "tests_failed": failed, "output": args.output}, sort_keys=True))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
