#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

FULL_PREFIX = "APP_ORCHESTRATOR_REPOSITORY/"
COMPACT_PREFIX = "COMPACT_CONTINUATION/"
METADATA_PREFIX = "CHECKPOINT_METADATA/"
FULL_MANIFEST = "PACKAGE_METADATA/FULL_PAYLOAD_MANIFEST.json"
COMPACT_MANIFEST = "PACKAGE_METADATA/COMPACT_PAYLOAD_MANIFEST.json"
ESSENTIAL_EXACT = {
    ".github/workflows/pass13-final-certification-v1.yml",
    "audit/a003-manifest-seal.json",
    "pmp-app-current.html",
    "pmp-current-map-v12.json",
    "pmp-migration-inactive-gate-v1.js",
    "pmp-migration-plan-v1.json",
    "pmp-runtime-integrity-manifest-v1.json",
    "pmp-safety-no-deletion-guard-v1.js",
    "pmp-safety-no-deletion-policy-v1.json",
    "tools/build_pass13_release_packages_v1.py",
    "tools/run_pass13_end_to_end_regression_v1.py",
    "tools/verify_pass13_final_certification_v1.py",
}


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=repo)


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def blob_sha(payload: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(payload)).encode() + b"\0" + payload
    ).hexdigest()


def zip_info(name: str, mode: int = 0o100644) -> zipfile.ZipInfo:
    item = zipfile.ZipInfo(name)
    item.date_time = (2026, 7, 27, 7, 41, 0)
    item.create_system = 3
    item.external_attr = mode << 16
    item.compress_type = zipfile.ZIP_DEFLATED
    return item


def repo_rows(repo: Path, commit: str) -> list[dict]:
    rows = []
    raw = git(repo, "ls-tree", "-r", "-z", "--long", commit)
    for item in raw.split(b"\0"):
        if not item:
            continue
        meta, raw_path = item.split(b"\t", 1)
        mode, kind, object_id, size = meta.decode().split()
        if kind != "blob":
            continue
        payload = git(repo, "cat-file", "blob", object_id)
        assert len(payload) == int(size)
        assert blob_sha(payload) == object_id
        rows.append({
            "path": raw_path.decode(),
            "mode": mode,
            "git_blob_sha": object_id,
            "bytes": len(payload),
            "sha256": sha(payload),
            "_payload": payload,
        })
    return rows


def metadata_rows(metadata: Path) -> list[dict]:
    rows = []
    for item in sorted(metadata.rglob("*")):
        if not item.is_file():
            continue
        payload = item.read_bytes()
        rows.append({
            "path": item.relative_to(metadata).as_posix(),
            "mode": "100644",
            "bytes": len(payload),
            "sha256": sha(payload),
            "_payload": payload,
        })
    return rows


def public(row: dict) -> dict:
    return {key: value for key, value in row.items() if key != "_payload"}


def collision_list(rows: list[dict]) -> list[list[str]]:
    folded: dict[str, str] = {}
    collisions = []
    for row in rows:
        key = row["path"].casefold()
        if key in folded:
            collisions.append([folded[key], row["path"]])
        else:
            folded[key] = row["path"]
    return collisions


def manifest_payload(
    package_type: str,
    commit: str,
    tree: str,
    repository_rows: list[dict],
    metadata: list[dict],
) -> bytes:
    value = {
        "type": package_type,
        "version": "1.0.0",
        "repository": "pmpbird/pmp-bridge-shell",
        "commit": commit,
        "tree": tree,
        "repository_record_count": len(repository_rows),
        "metadata_record_count": len(metadata),
        "casefold_collisions": collision_list(repository_rows),
        "repository_records": [public(row) for row in repository_rows],
        "metadata_records": [public(row) for row in metadata],
    }
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def write_package(
    path: Path,
    sidecar: Path,
    prefix: str,
    manifest_name: str,
    package_type: str,
    commit: str,
    tree: str,
    repository_rows: list[dict],
    metadata: list[dict],
) -> str:
    assert not path.exists() and not sidecar.exists()
    manifest = manifest_payload(
        package_type, commit, tree, repository_rows, metadata
    )
    with zipfile.ZipFile(path, "w", allowZip64=True) as archive:
        for row in repository_rows:
            archive.writestr(
                zip_info(prefix + row["path"], int(row["mode"], 8)),
                row["_payload"],
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )
        for row in metadata:
            archive.writestr(
                zip_info(METADATA_PREFIX + row["path"]),
                row["_payload"],
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )
        archive.writestr(
            zip_info(manifest_name),
            manifest,
            compress_type=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        )
    package_sha = sha(path.read_bytes())
    sidecar.write_text(f"{package_sha}  {path.name}\n")
    return package_sha


def verify_package(
    path: Path,
    sidecar: Path,
    prefix: str,
    manifest_name: str,
    package_type: str,
    commit: str,
    tree: str,
) -> dict:
    package_sha = sha(path.read_bytes())
    assert sidecar.read_text().split()[0] == package_sha
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        assert len(names) == len(set(names))
        manifest = json.loads(archive.read(manifest_name))
        assert manifest["type"] == package_type
        assert manifest["commit"] == commit
        assert manifest["tree"] == tree
        for row in manifest["repository_records"]:
            payload = archive.read(prefix + row["path"])
            assert len(payload) == row["bytes"]
            assert sha(payload) == row["sha256"]
            assert blob_sha(payload) == row["git_blob_sha"]
        for row in manifest["metadata_records"]:
            payload = archive.read(METADATA_PREFIX + row["path"])
            assert len(payload) == row["bytes"]
            assert sha(payload) == row["sha256"]
        assert len(names) == (
            manifest["repository_record_count"]
            + manifest["metadata_record_count"]
            + 1
        )
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": package_sha,
        "entries": len(names),
        "repository_records": manifest["repository_record_count"],
        "metadata_records": manifest["metadata_record_count"],
        "crc": "PASS",
        "payload_hashes": "PASS",
        "sidecar": "PASS",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--metadata-dir", required=True)
    parser.add_argument("--full", required=True)
    parser.add_argument("--full-sidecar", required=True)
    parser.add_argument("--compact", required=True)
    parser.add_argument("--compact-sidecar", required=True)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    metadata_dir = Path(args.metadata_dir).resolve()
    full_path = Path(args.full).resolve()
    full_sidecar = Path(args.full_sidecar).resolve()
    compact_path = Path(args.compact).resolve()
    compact_sidecar = Path(args.compact_sidecar).resolve()
    commit = git(repo, "rev-parse", args.commit).decode().strip()
    tree = git(repo, "rev-parse", f"{commit}^{{tree}}").decode().strip()
    rows = repo_rows(repo, commit)
    metadata = metadata_rows(metadata_dir)
    names = {row["path"] for row in rows}
    essential = [
        row
        for row in rows
        if row["path"].startswith("audit/pass13/")
        or row["path"] in ESSENTIAL_EXACT
    ]
    required_available = {
        path for path in ESSENTIAL_EXACT if path in names
    }
    assert required_available.issubset({row["path"] for row in essential})
    assert len(essential) == len({row["path"] for row in essential})
    assert collision_list(rows) == [["Index.html", "index.html"]]
    assert collision_list(essential) == []

    write_package(
        full_path,
        full_sidecar,
        FULL_PREFIX,
        FULL_MANIFEST,
        "PMP_APP_ORCHESTRATOR_FULL_ARCHIVAL_PACKAGE_MANIFEST_V1",
        commit,
        tree,
        rows,
        metadata,
    )
    write_package(
        compact_path,
        compact_sidecar,
        COMPACT_PREFIX,
        COMPACT_MANIFEST,
        "PMP_APP_ORCHESTRATOR_COMPACT_CONTINUATION_PACKAGE_MANIFEST_V1",
        commit,
        tree,
        essential,
        metadata,
    )
    full_result = verify_package(
        full_path,
        full_sidecar,
        FULL_PREFIX,
        FULL_MANIFEST,
        "PMP_APP_ORCHESTRATOR_FULL_ARCHIVAL_PACKAGE_MANIFEST_V1",
        commit,
        tree,
    )
    compact_result = verify_package(
        compact_path,
        compact_sidecar,
        COMPACT_PREFIX,
        COMPACT_MANIFEST,
        "PMP_APP_ORCHESTRATOR_COMPACT_CONTINUATION_PACKAGE_MANIFEST_V1",
        commit,
        tree,
    )
    result = {
        "type": "PMP_PASS13_RELEASE_PACKAGE_BUILD_RESULT_V1",
        "status": "PASS",
        "commit": commit,
        "tree": tree,
        "full": full_result,
        "compact": compact_result,
        "casefold_collision_preserved_in_full": True,
        "earlier_packages_modified": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
