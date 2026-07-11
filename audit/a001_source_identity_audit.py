#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from collections import deque
from pathlib import PurePosixPath
from typing import Any

SOURCE_EXTENSIONS = {
    ".html", ".htm", ".js", ".mjs", ".json", ".css", ".wasm",
    ".webmanifest", ".svg", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".txt"
}
REFERENCE_RE = re.compile(
    r"""(?P<url>https://raw\.githubusercontent\.com/pmpbird/pmp-bridge-shell/(?P<commit>[0-9a-f]{40})/(?P<remote_path>[A-Za-z0-9._~!$&'()*+,;=:@%/-]+))
       |(?P<local>(?:\.\.?/|/)?[A-Za-z0-9._~!$&'()*+,;=:@%/-]+\.(?:html?|m?js|json|css|wasm|webmanifest|svg|png|jpe?g|gif|ico|txt)(?:\?[^\"'`\s<>)\]}]*)?(?:#[^\"'`\s<>)\]}]*)?)""",
    re.IGNORECASE | re.VERBOSE,
)

def run(*args: str, text: bool = True) -> str:
    proc = subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=text)
    return proc.stdout if text else proc.stdout  # type: ignore[return-value]

def git_bytes(ref: str, path: str) -> bytes:
    proc = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.stdout

def git_blob_sha(ref: str, path: str) -> str:
    return run("git", "rev-parse", f"{ref}:{path}").strip()

def list_tree(ref: str) -> dict[str, dict[str, str]]:
    out = run("git", "ls-tree", "-r", "--full-tree", ref)
    tree: dict[str, dict[str, str]] = {}
    for line in out.splitlines():
        meta, path = line.split("\t", 1)
        mode, kind, sha = meta.split()
        tree[path] = {"mode": mode, "kind": kind, "blob_sha": sha}
    return tree

def normalize_local_reference(parent: str, raw: str) -> str | None:
    raw = raw.split("?", 1)[0].split("#", 1)[0]
    if not raw or raw.startswith(("http://", "https://", "//", "data:", "blob:", "javascript:")):
        return None
    raw = raw.lstrip("/")
    base = PurePosixPath(parent).parent
    candidate = PurePosixPath(base, raw) if raw.startswith(("./", "../")) else PurePosixPath(raw)
    parts: list[str] = []
    for part in candidate.parts:
        if part in ("", "."):
            continue
        if part == "..":
            if parts:
                parts.pop()
            else:
                return None
        else:
            parts.append(part)
    if not parts:
        return None
    path = "/".join(parts)
    if PurePosixPath(path).suffix.lower() not in SOURCE_EXTENSIONS:
        return None
    return path

def decode_for_scan(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")

def extract_references(parent: str, data: bytes) -> tuple[set[str], list[dict[str, str]]]:
    text = decode_for_scan(data)
    local: set[str] = set()
    remote: list[dict[str, str]] = []
    for match in REFERENCE_RE.finditer(text):
        if match.group("url"):
            commit = match.group("commit")
            path = match.group("remote_path").split("?", 1)[0].split("#", 1)[0]
            remote.append({"commit": commit, "path": path, "url": match.group("url")})
            continue
        raw = match.group("local")
        if raw:
            norm = normalize_local_reference(parent, raw)
            if norm:
                local.add(norm)
    return local, remote

def infer_version(path: str, text: str) -> str:
    patterns = [
        r"\b(?:VERSION|RESTORE_VERSION|KEY)\s*=\s*['\"]([^'\"]+)['\"]",
        r'"version"\s*:\s*"([^"]+)"',
        r"'version'\s*:\s*'([^']+)'",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return m.group(1)
    m = re.search(r"(?:^|[-_.])v(\d+(?:\.\d+)*)", PurePosixPath(path).name, re.IGNORECASE)
    if m:
        return f"filename-v{m.group(1)}"
    return "content-addressed-no-declared-version"

def infer_role(path: str) -> str:
    n = path.lower()
    if n.endswith(".json") and "map" in n:
        return "route_map"
    if "service-worker" in n:
        return "service_worker"
    if "route-guardian" in n:
        return "route_guardian_or_route_tool"
    if "reload-owner" in n:
        return "reload_owner_wrapper"
    if "orchestrator" in n:
        return "app_orchestrator"
    if "registry" in n or "inventory" in n:
        return "registry_or_inventory"
    if "diagnostic" in n or "proof" in n or "receipt" in n or "certification" in n or "/audit/" in n:
        return "evidence_diagnostics_or_certification"
    if "loader" in n or "inject" in n or "frame" in n:
        return "loader_or_injection_actor"
    if "migration" in n or "cleaner" in n or "delete" in n or "repair" in n:
        return "migration_cleanup_or_destructive_actor"
    if n.endswith((".html", ".htm")):
        return "runtime_page_or_wrapper"
    if n.endswith((".js", ".mjs")):
        return "runtime_script"
    return "runtime_asset"

def infer_authority(path: str, text: str) -> str:
    n = path.lower()
    hay = (n + "\n" + text[:20000]).lower()
    if any(x in hay for x in ("document.open", "document.write", "indexeddb.delete", "caches.delete", "localstorage.clear", "removeitem(", ".remove()", "deleteobjectstore")):
        return "destructive_or_document_replacement_authority_candidate"
    if any(x in n for x in ("route", "reload", "navigation", "screen-pointer")):
        return "route_or_navigation_authority_candidate"
    if any(x in n for x in ("service-worker", "cache", "indexeddb", "storage", "migration")):
        return "storage_cache_or_persistence_authority_candidate"
    if any(x in n for x in ("owner", "registry", "authority", "orchestrator", "mount")):
        return "owner_or_governance_authority_candidate"
    if any(x in n for x in ("diagnostic", "proof", "receipt", "certification", "audit")):
        return "evidence_or_diagnostics_authority_candidate"
    if any(x in n for x in ("loader", "inject", "frame")):
        return "loading_or_injection_authority_candidate"
    return "support_or_runtime_authority_candidate"

def infer_expiry(reachable: bool, exists: bool, text: str) -> str:
    if not reachable and not exists:
        return "INACTIVE_AT_BASELINE_ABSENT_AND_UNREACHABLE"
    if not reachable:
        return "INACTIVE_AT_BASELINE_NOT_REACHABLE_FROM_ACTIVE_SEEDS"
    if not exists:
        return "REACHABLE_BUT_ABSENT_BLOCKER"
    low = text.lower()
    recurring = "setinterval" in low or "mutationobserver" in low or "requestanimationframe" in low
    stop = "clearinterval" in low or ".disconnect()" in low or "cancelanimationframe" in low
    if recurring and stop:
        return "ACTIVE_REACHABLE_RECURRING_WITH_INTERNAL_STOP_LOGIC"
    if recurring:
        return "ACTIVE_REACHABLE_RECURRING_NO_EXPLICIT_EXPIRY_FOUND"
    return "ACTIVE_REACHABLE_NO_EXPLICIT_EXPIRY_DECLARED"

def shortest_chain(parent: dict[str, str | None], path: str) -> list[str]:
    chain: list[str] = []
    cur: str | None = path
    seen: set[str] = set()
    while cur is not None and cur not in seen:
        seen.add(cur)
        chain.append(cur)
        cur = parent.get(cur)
    chain.reverse()
    return chain

def load_planning_candidates(path: str) -> set[str]:
    with open(path, "r", encoding="utf-8") as f:
        doc = json.load(f)
    candidates: set[str] = set(doc.get("unresolved_paths", []))
    for row in doc.get("resolved", []):
        if isinstance(row, list) and row:
            candidates.add(str(row[0]))
        elif isinstance(row, dict) and row.get("path"):
            candidates.add(str(row["path"]))
    missing = doc.get("missing_named_source")
    if missing:
        candidates.add(str(missing))
    return candidates

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--planning-manifest", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--seed", action="append", default=[])
    args = ap.parse_args()

    baseline = args.baseline
    tree = list_tree(baseline)
    planning_candidates = load_planning_candidates(args.planning_manifest)
    seeds = list(dict.fromkeys(args.seed or [
        "pmp-current-map-v12.json",
        "pmp-route-guardian-current-loader-v22.html",
    ]))

    references: dict[str, set[str]] = {}
    remote_references: list[dict[str, Any]] = []
    parent: dict[str, str | None] = {seed: None for seed in seeds}
    reachable: set[str] = set()
    queue: deque[str] = deque(seeds)
    missing_reachable: set[str] = set()

    while queue:
        path = queue.popleft()
        if path in reachable:
            continue
        reachable.add(path)
        if path not in tree:
            missing_reachable.add(path)
            references[path] = set()
            continue
        data = git_bytes(baseline, path)
        locals_found, remotes_found = extract_references(path, data)
        references[path] = locals_found
        for remote in remotes_found:
            remote["discovered_from"] = path
            remote_references.append(remote)
        for child in sorted(locals_found):
            if child not in parent:
                parent[child] = path
            if child not in reachable:
                queue.append(child)

    all_candidates = sorted(planning_candidates | reachable)
    inbound: dict[str, list[str]] = {p: [] for p in all_candidates}
    for src, children in references.items():
        for child in children:
            inbound.setdefault(child, []).append(src)

    entries: list[dict[str, Any]] = []
    for path in all_candidates:
        exists = path in tree
        is_reachable = path in reachable
        data = git_bytes(baseline, path) if exists else b""
        text = decode_for_scan(data)
        entry: dict[str, Any] = {
            "path": path,
            "baseline_commit": baseline,
            "tree_state": "PRESENT" if exists else "ABSENT",
            "git_blob_sha": tree[path]["blob_sha"] if exists else None,
            "sha256": hashlib.sha256(data).hexdigest() if exists else None,
            "byte_length": len(data) if exists else 0,
            "expected_version": infer_version(path, text) if exists else "ABSENT_AT_BASELINE",
            "runtime_role": infer_role(path),
            "authority_class": infer_authority(path, text),
            "reachability": "ACTIVE_OR_REACHABLE" if is_reachable else "INACTIVE_AT_BASELINE",
            "expiry_state": infer_expiry(is_reachable, exists, text),
            "inbound_references": sorted(inbound.get(path, [])),
            "shortest_active_chain": shortest_chain(parent, path) if is_reachable else [],
            "evidence": [],
        }
        if is_reachable:
            entry["evidence"].append("reachable_from_active_seed_by_static_repository_reference_closure")
        else:
            entry["evidence"].append("not_reachable_from_any_active_seed_in_static_repository_reference_closure")
        if exists:
            entry["evidence"].append("exact_identity_from_git_ls_tree_and_sha256_of_git_show_bytes")
        else:
            entry["evidence"].append("absent_from_pinned_baseline_git_tree")
        if not is_reachable:
            entry["inactive_proof"] = {
                "baseline_commit": baseline,
                "active_seeds": seeds,
                "zero_reachable_inbound_references": len(inbound.get(path, [])) == 0,
                "tree_state": entry["tree_state"],
            }
        entries.append(entry)

    historical: list[dict[str, Any]] = []
    seen_remote: set[tuple[str, str]] = set()
    for remote in sorted(remote_references, key=lambda r: (r["commit"], r["path"], r["discovered_from"])):
        key = (remote["commit"], remote["path"])
        if key in seen_remote:
            continue
        seen_remote.add(key)
        commit, path = key
        try:
            data = git_bytes(commit, path)
            blob = git_blob_sha(commit, path)
            historical.append({
                "path": path,
                "repository_ref": commit,
                "git_blob_sha": blob,
                "sha256": hashlib.sha256(data).hexdigest(),
                "byte_length": len(data),
                "expected_version": infer_version(path, decode_for_scan(data)),
                "runtime_role": "historical_remote_runtime_payload",
                "authority_class": "remote_runtime_or_document_replacement_payload",
                "expiry_state": "ACTIVE_WHEN_REFERENCING_SOURCE_FETCH_PATH_EXECUTES",
                "discovered_from": sorted({r["discovered_from"] for r in remote_references if (r["commit"], r["path"]) == key}),
                "identity_state": "EXACT_COMMIT_BLOB_AND_SHA256_RESOLVED",
            })
        except subprocess.CalledProcessError as exc:
            historical.append({
                "path": path,
                "repository_ref": commit,
                "git_blob_sha": None,
                "sha256": None,
                "byte_length": None,
                "runtime_role": "historical_remote_runtime_payload",
                "authority_class": "remote_runtime_or_document_replacement_payload",
                "expiry_state": "REACHABLE_BUT_UNRESOLVED_REMOTE_BLOCKER",
                "discovered_from": sorted({r["discovered_from"] for r in remote_references if (r["commit"], r["path"]) == key}),
                "identity_state": "UNRESOLVED",
                "error": exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else str(exc.stderr),
            })

    reachable_entries = [e for e in entries if e["reachability"] == "ACTIVE_OR_REACHABLE"]
    inactive_entries = [e for e in entries if e["reachability"] == "INACTIVE_AT_BASELINE"]
    unresolved_reachable = [e for e in reachable_entries if e["git_blob_sha"] is None]
    inactive_without_proof = [
        e for e in inactive_entries
        if not e.get("inactive_proof")
        or e["inactive_proof"]["zero_reachable_inbound_references"] is not True
    ]
    unresolved_historical = [e for e in historical if e["identity_state"] != "EXACT_COMMIT_BLOB_AND_SHA256_RESOLVED"]

    tests = [
        {
            "name": "Every active or reachable repository source has exact commit, Git blob SHA, and SHA-256",
            "pass": len(unresolved_reachable) == 0,
            "failures": [e["path"] for e in unresolved_reachable],
        },
        {
            "name": "Every planning candidate is either exactly identified or proven inactive",
            "pass": len(inactive_without_proof) == 0,
            "failures": [e["path"] for e in inactive_without_proof],
        },
        {
            "name": "Every historical remote runtime payload has exact commit, Git blob SHA, and SHA-256",
            "pass": len(unresolved_historical) == 0,
            "failures": [f'{e["repository_ref"]}:{e["path"]}' for e in unresolved_historical],
        },
        {
            "name": "Manifest includes every source discovered by recursive reference closure",
            "pass": set(reachable).issubset({e["path"] for e in entries}),
            "failures": sorted(set(reachable) - {e["path"] for e in entries}),
        },
    ]
    passed = all(t["pass"] for t in tests)

    manifest: dict[str, Any] = {
        "type": "PMP_ACTIVE_SOURCE_IDENTITY_MANIFEST_V2",
        "repair": "A-001",
        "baseline": {"branch": "main", "commit": baseline},
        "generation": {
            "method": "git_ls_tree_plus_recursive_static_reference_closure",
            "active_seeds": seeds,
            "deterministic_sorting": True,
            "runtime_execution": False,
            "storage_access": False,
        },
        "status": "PASS" if passed else "FAIL",
        "decision": "A-001_PASSED_A002_MAY_REMAIN_BLOCKED_UNTIL_USER_AUTHORIZES" if passed else "A-001_NOT_PASSED_DO_NOT_BEGIN_A002",
        "counts": {
            "baseline_tree_files": len(tree),
            "planning_candidates": len(planning_candidates),
            "repository_active_or_reachable_sources": len(reachable_entries),
            "historical_remote_runtime_sources": len(historical),
            "inactive_candidates_with_evidence": len(inactive_entries),
            "unresolved_reachable_sources": len(unresolved_reachable),
            "inactive_candidates_without_proof": len(inactive_without_proof),
            "unresolved_historical_sources": len(unresolved_historical),
            "manifest_entries": len(entries) + len(historical),
        },
        "tests": tests,
        "entries": entries,
        "historical_remote_entries": historical,
        "missing_reachable_sources": sorted(missing_reachable),
        "scope_guard": {
            "allowed": ["read Git tree", "read source bytes", "calculate hashes", "write audit outputs"],
            "forbidden_and_not_attempted": [
                "route changes", "storage clearing", "IndexedDB access", "cache clearing",
                "Bank rebuild", "DOM mutation", "runtime execution", "app feature changes"
            ],
        },
    }
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    manifest["manifest_sha256"] = hashlib.sha256(canonical).hexdigest()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
        f.write("\n")

    summary = {
        "status": manifest["status"],
        "decision": manifest["decision"],
        "counts": manifest["counts"],
        "failed_tests": [t for t in tests if not t["pass"]],
        "manifest_sha256": manifest["manifest_sha256"],
    }
    with open(args.summary, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if passed else 2

if __name__ == "__main__":
    raise SystemExit(main())
