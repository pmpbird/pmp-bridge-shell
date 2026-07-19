#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import tempfile


def file_sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def syntax_check(path: pathlib.Path, kind: str, evidence_dir: pathlib.Path) -> None:
    if kind == "document-inline":
        text = path.read_text()
        pattern = re.compile(
            r'<script type="application/pmp-p2c-managed-document"[^>]*>([\s\S]*?)</script>'
        )
        matches = pattern.findall(text)
        if len(matches) != 1:
            raise SystemExit(
                f"REHEARSAL101_MANAGED_DOCUMENT_SCRIPT_COUNT_INVALID:{path}:{len(matches)}"
            )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".js", dir=evidence_dir, delete=False
        ) as handle:
            handle.write(matches[0])
            check_path = pathlib.Path(handle.name)
    else:
        check_path = path
    result = subprocess.run(
        ["node", "--check", str(check_path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if kind == "document-inline":
        check_path.unlink(missing_ok=True)
    if result.returncode:
        raise SystemExit(
            "REHEARSAL101_NODE_CHECK_FAILED:"
            + str(path)
            + ":"
            + result.stdout[-4000:]
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--normalized-root", type=pathlib.Path, required=True)
    parser.add_argument("--base-manifest", type=pathlib.Path, required=True)
    parser.add_argument("--output-manifest", type=pathlib.Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--evidence-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()

    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(args.base_manifest.read_text())
    if manifest.get("type") != "PMP_REPAIR009_NORMALIZED_SOURCE_MANIFEST_002":
        raise SystemExit("REHEARSAL101_BASE_MANIFEST_TYPE_INVALID")

    declaration = re.compile(
        r"\bvar __awaiter = \(this && this\.__awaiter\) \|\| function\b"
    )
    records = []
    for row in manifest.get("records", []):
        relative = row["path"]
        target = args.normalized_root / relative
        if not target.is_file():
            raise SystemExit("REHEARSAL101_NORMALIZED_SOURCE_MISSING:" + relative)

        before = target.read_text()
        before_sha = hashlib.sha256(before.encode()).hexdigest()
        if before_sha != row["transformed_sha256"]:
            raise SystemExit(
                "REHEARSAL101_BASE_TRANSFORMED_SHA_MISMATCH:"
                + relative
                + ":"
                + before_sha
                + ":"
                + row["transformed_sha256"]
            )

        helper = "__pmpAwaiter_" + hashlib.sha256(relative.encode()).hexdigest()[:16]
        declaration_count = len(declaration.findall(before))
        invocation_count = len(re.findall(r"\b__awaiter\s*\(", before))
        if declaration_count != 1:
            raise SystemExit(
                f"REHEARSAL101_AWAITER_DECLARATION_COUNT_INVALID:{relative}:{declaration_count}"
            )
        if invocation_count < 1:
            raise SystemExit(
                f"REHEARSAL101_AWAITER_INVOCATION_COUNT_INVALID:{relative}:{invocation_count}"
            )

        after = declaration.sub("var " + helper + " = function", before, count=1)
        after = re.sub(r"\b__awaiter\s*\(", helper + "(", after)
        if "__awaiter" in after:
            raise SystemExit("REHEARSAL101_RESIDUAL_SHARED_AWAITER:" + relative)
        if after.count(helper) != invocation_count + 1:
            raise SystemExit(
                f"REHEARSAL101_UNIQUE_HELPER_COUNT_INVALID:{relative}:{after.count(helper)}:{invocation_count + 1}"
            )

        target.write_text(after)
        syntax_check(target, row["kind"], args.evidence_dir)
        after_sha = file_sha256(target)
        after_bytes = target.stat().st_size
        row["transformed_sha256"] = after_sha
        row["transformed_bytes"] = after_bytes
        row["awaiter_helper"] = helper
        row["awaiter_helper_isolation"] = "PER_SOURCE_NO_GLOBAL_INHERITANCE"
        records.append(
            {
                "path": relative,
                "kind": row["kind"],
                "realm": row["realm"],
                "base_transformed_sha256": before_sha,
                "isolated_transformed_sha256": after_sha,
                "isolated_transformed_bytes": after_bytes,
                "awaiter_helper": helper,
                "awaiter_invocation_count": invocation_count,
                "residual_shared_awaiter_count": after.count("__awaiter"),
                "node_syntax_check": "PASS",
            }
        )

    manifest["source_repository_commit"] = args.source_commit
    manifest["awaiter_helper_model"] = "DETERMINISTIC_PER_SOURCE_HELPER"
    manifest["shared_global_awaiter_inheritance"] = False
    manifest["awaiter_isolated_record_count"] = len(records)
    manifest["base_manifest_sha256"] = file_sha256(args.base_manifest)
    args.output_manifest.parent.mkdir(parents=True, exist_ok=True)
    args.output_manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    evidence = {
        "type": "PMP_P2C_TYPESCRIPT_AWAITER_HELPER_ISOLATION_REHEARSAL_101",
        "status": "PASS",
        "source_commit": args.source_commit,
        "record_count": len(records),
        "expected_record_count": 19,
        "all_helpers_unique": len({row["awaiter_helper"] for row in records}) == len(records),
        "shared_global_awaiter_inheritance": False,
        "manifest_path": str(args.output_manifest),
        "manifest_sha256": file_sha256(args.output_manifest),
        "production_changed": False,
        "current_map_changed": False,
        "unknown_actor_policy_weakened": False,
        "records": records,
    }
    if evidence["record_count"] != 19 or evidence["all_helpers_unique"] is not True:
        raise SystemExit("REHEARSAL101_AWAITER_ISOLATION_COVERAGE_INVALID")
    (args.evidence_dir / "typescript-awaiter-helper-isolation-rehearsal-101.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
