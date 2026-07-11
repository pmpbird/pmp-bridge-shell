#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import io
import json
import shutil
import stat
import subprocess
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

SOURCE_COMMIT = "903cd10808f2d4639dff82aa4595cc7b74417e7a"
PACKAGE_NAME = "CURRENT_USE_THIS_PMP_APP_ORCHESTRATOR_PASS1_CANONICAL_V1.zip"
FIXED_TIME = (2026, 7, 11, 0, 0, 0)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def safe_extract_tar(data: bytes, destination: Path) -> None:
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as archive:
        for member in archive.getmembers():
            p = PurePosixPath(member.name)
            if p.is_absolute() or ".." in p.parts:
                raise RuntimeError(f"Unsafe git archive path: {member.name}")
        archive.extractall(destination)


def create_verifier(path: Path) -> None:
    text = r'''#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, sys, zipfile
from pathlib import PurePosixPath

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

package = sys.argv[1]
errors = []
with zipfile.ZipFile(package, "r") as zf:
    names = zf.namelist()
    if len(names) != len(set(names)):
        errors.append("duplicate member names")
    for name in names:
        p = PurePosixPath(name)
        if p.is_absolute() or ".." in p.parts:
            errors.append(f"unsafe member: {name}")
    manifest = json.loads(zf.read("PMP_APP_TRANSFER/PACKAGE_MANIFEST.json"))
    for record in manifest["files"]:
        name = record["path"]
        if name not in names:
            errors.append(f"missing: {name}")
        elif digest(zf.read(name)) != record["sha256"]:
            errors.append(f"hash mismatch: {name}")
    for line in zf.read("PMP_APP_TRANSFER/SHA256SUMS.txt").decode("utf-8").splitlines():
        expected, name = line.split("  ", 1)
        if name not in names or digest(zf.read(name)) != expected:
            errors.append(f"checksum mismatch: {name}")
    if any(n.lower().endswith(".zip") and "crosswalk" in n.lower() for n in names):
        errors.append("Crosswalk Router ZIP contamination detected")
result = {"status": "PASS" if not errors else "FAIL", "errors": errors, "checks_failed": len(errors)}
print(json.dumps(result, indent=2, sort_keys=True))
raise SystemExit(0 if not errors else 1)
'''
    path.write_text(text, encoding="utf-8")


def build(output_dir: Path) -> dict[str, object]:
    work = Path(".transfer-package-work")
    if work.exists():
        shutil.rmtree(work)
    staging = work / "staging"
    repo = staging / "APP_ORCHESTRATOR_REPOSITORY"
    transfer = staging / "PMP_APP_TRANSFER"
    repo.mkdir(parents=True)
    transfer.mkdir(parents=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(["git", "cat-file", "-e", f"{SOURCE_COMMIT}^{{commit}}"], check=True)
    archive = subprocess.run(
        ["git", "archive", "--format=tar", SOURCE_COMMIT],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    safe_extract_tar(archive, repo)

    receipt = repo / "audit/pr38-post-merge-stable-receipt.json"
    if not receipt.is_file():
        raise RuntimeError("Stable PR #38 receipt is missing from the frozen source commit.")
    shutil.copy2(receipt, transfer / "PR38_STABLE_POST_MERGE_RECEIPT.json")

    (transfer / "00_READ_FIRST.md").write_text(
        "# PMP App / App Orchestrator — Canonical Pass 1 Transfer Package\n\n"
        "This is the first canonical App Orchestrator transfer ZIP.\n\n"
        f"The source snapshot is an exact git archive of stable main commit `{SOURCE_COMMIT}`.\n\n"
        "The Crosswalk Router project is separate future-integration work. Its uploaded ZIP was not used, copied, or made a dependency.\n\n"
        "Current position: overall Pass 1 remains in progress; A-002, A-003, PR #38 delivery, and post-merge stabilization are complete.\n\n"
        "Every completed App Orchestrator move must update this canonical ZIP and rerun package integrity verification before the move is complete.\n",
        encoding="utf-8",
    )

    metadata = {
        "SOURCE_IDENTITY.json": {
            "type": "PMP_APP_ORCHESTRATOR_SOURCE_IDENTITY_V1",
            "repository": "pmpbird/pmp-bridge-shell",
            "branch": "main",
            "source_commit": SOURCE_COMMIT,
            "source_mode": "exact_git_archive",
            "source_receipt": "audit/pr38-post-merge-stable-receipt.json",
            "source_status": "FINAL_STABLE_POST_MERGE_EXERCISED_SCOPE_PASS",
        },
        "PASS_AND_PHASE_LEDGER.json": {
            "type": "PMP_APP_ORCHESTRATOR_PASS_AND_PHASE_LEDGER_V1",
            "overall_project": {
                "pass": "Pass 1",
                "phase": "App Orchestrator repair program and transfer continuity",
                "status": "IN_PROGRESS_NOT_DECLARED_COMPLETE",
            },
            "completed": [
                {"repair": "A-002", "phase": "P0-P7", "status": "COMPLETE_MERGED_FINAL_STABLE_VERIFIED"},
                {"repair": "A-003", "phase": "runtime source-byte enforcement and main reseal", "status": "COMPLETE_MERGED_FINAL_STABLE_VERIFIED"},
                {"delivery": "PR #38", "phase": "merge, verification, stability repair, final receipt", "status": "COMPLETE"},
                {"transfer": "A1", "phase": "first canonical App Orchestrator ZIP", "status": "COMPLETE"},
            ],
            "current": {"pass": "Pass 1", "phase": "A2 — final Pass 1 closure inventory", "status": "NEXT"},
        },
        "PROJECT_BOUNDARY.json": {
            "type": "PMP_APP_ORCHESTRATOR_PROJECT_BOUNDARY_V1",
            "included_project": "PMP App / App Orchestrator",
            "excluded_project": "Crosswalk Router",
            "crosswalk_router_zip_used": False,
            "crosswalk_router_dependency_created": False,
            "rule": "Crosswalk Router remains separate until a later explicitly authorized integration phase.",
        },
        "CANONICAL_PACKAGE_RULE.json": {
            "type": "PMP_APP_ORCHESTRATOR_CANONICAL_PACKAGE_RULE_V1",
            "rule": "Every completed App Orchestrator work move must be written into the current canonical ZIP and followed by ZIP integrity verification before the move is complete.",
            "canonical_filename": PACKAGE_NAME,
            "base_source_commit": SOURCE_COMMIT,
        },
        "PASS1_CLOSURE_STATUS.json": {
            "type": "PMP_APP_ORCHESTRATOR_PASS1_CLOSURE_STATUS_V1",
            "overall_pass": "Pass 1",
            "status": "IN_PROGRESS_NOT_DECLARED_COMPLETE",
            "completed_boundaries": ["A-002", "A-003", "PR38 delivery", "post-merge stability repair", "canonical transfer package creation"],
            "next_boundary": "Run final Pass 1 closure inventory against repair ledgers and receipts; execute any remaining repair before closure certification.",
            "pass2_started": False,
        },
    }
    for name, value in metadata.items():
        write_json(transfer / name, value)
    create_verifier(transfer / "verify_package.py")

    payload = []
    for file in sorted(p for p in staging.rglob("*") if p.is_file()):
        rel = file.relative_to(staging).as_posix()
        if rel in {"PMP_APP_TRANSFER/PACKAGE_MANIFEST.json", "PMP_APP_TRANSFER/SHA256SUMS.txt"}:
            continue
        data = file.read_bytes()
        payload.append({"path": rel, "bytes": len(data), "sha256": sha256(data)})
    write_json(
        transfer / "PACKAGE_MANIFEST.json",
        {
            "type": "PMP_APP_ORCHESTRATOR_CANONICAL_PACKAGE_MANIFEST_V1",
            "package": PACKAGE_NAME,
            "source_commit": SOURCE_COMMIT,
            "manifest_rule": "Manifest and checksum files exclude recursive self-reference.",
            "files": payload,
        },
    )

    checksum_lines = []
    for file in sorted(p for p in staging.rglob("*") if p.is_file() and p != transfer / "SHA256SUMS.txt"):
        checksum_lines.append(f"{sha256(file.read_bytes())}  {file.relative_to(staging).as_posix()}")
    (transfer / "SHA256SUMS.txt").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

    package = output_dir / PACKAGE_NAME
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for file in sorted(p for p in staging.rglob("*") if p.is_file()):
            rel = file.relative_to(staging).as_posix()
            info = zipfile.ZipInfo(rel, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            mode = 0o755 if file.name == "verify_package.py" else 0o644
            info.external_attr = (stat.S_IFREG | mode) << 16
            zf.writestr(info, file.read_bytes())

    verification = subprocess.run(
        ["python3", str(transfer / "verify_package.py"), str(package)],
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    (output_dir / "package-verification.json").write_text(verification, encoding="utf-8")

    package_digest = sha256(package.read_bytes())
    (output_dir / f"{PACKAGE_NAME}.sha256").write_text(
        f"{package_digest}  {PACKAGE_NAME}\n", encoding="utf-8"
    )
    with zipfile.ZipFile(package, "r") as zf:
        names = zf.namelist()
    report = {
        "type": "PMP_APP_ORCHESTRATOR_CANONICAL_PACKAGE_BUILD_REPORT_V1",
        "status": "PASS",
        "overall_project_pass": "Pass 1",
        "phase": "Transfer Package A1",
        "package": PACKAGE_NAME,
        "package_sha256": package_digest,
        "package_bytes": package.stat().st_size,
        "member_count": len(names),
        "unique_member_names": len(names) == len(set(names)),
        "source_commit": SOURCE_COMMIT,
        "crosswalk_router_archive_included": False,
        "next_phase": "A2 — final Pass 1 closure inventory",
    }
    write_json(output_dir / "package-build-report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    args = parser.parse_args()
    print(json.dumps(build(args.output_dir), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
