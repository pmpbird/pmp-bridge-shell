#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import pathlib
from typing import Any, Sequence

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
UNIT_ROOT = pathlib.Path(__file__).resolve().parent
SCOPE_LOCK_PATH = UNIT_ROOT / "P2C_POST_FAILURE_STATIC_PREFLIGHT_SCOPE_LOCK_001.json"
CURRENT_AUTHORITY_PATH = UNIT_ROOT / "P2C_POST_FAILURE_STATIC_PREFLIGHT_CURRENT_AUTHORITY_RECEIPT_001.json"
MODE_CONTRACT_PATH = UNIT_ROOT / "P2C_STATIC_PREFLIGHT_MODE_CONTRACT_001.json"
ACTIVATION_PATH = SCOPE_LOCK_PATH.relative_to(REPO_ROOT).as_posix()


import static_preflight_modes_001 as checker


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify bounded static-preflight repair Unit 1")
    parser.add_argument("--base-sha")
    parser.add_argument("--head-sha")
    parser.add_argument("--evidence-dir", type=pathlib.Path)
    return parser.parse_args(argv)


def required(value: str | None, env_name: str) -> str:
    result = value or os.environ.get(env_name)
    checker.require(bool(result), "UNIT1_REQUIRED_ARGUMENT_MISSING", name=env_name)
    return str(result)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    base_sha = required(args.base_sha, "BASE_SHA")
    head_sha = required(args.head_sha, "PR_HEAD_SHA")
    evidence_dir = args.evidence_dir or pathlib.Path(os.environ.get("EVIDENCE_DIR", "/tmp/p2c-receipt038-static-preflight"))
    evidence_dir.mkdir(parents=True, exist_ok=True)

    scope = json.loads(SCOPE_LOCK_PATH.read_text(encoding="utf-8"))
    current = json.loads(CURRENT_AUTHORITY_PATH.read_text(encoding="utf-8"))
    contract = json.loads(MODE_CONTRACT_PATH.read_text(encoding="utf-8"))
    checker.validate_current_authority_state(current)
    git = checker.GitReader(REPO_ROOT, contract["static_command_policy"]["allowed_git_subcommands"])
    changed = git.changed(base_sha, head_sha)

    if ACTIVATION_PATH not in changed:
        out: dict[str, Any] = {
            "type": "PMP_APP_ORCHESTRATOR_P2C_STATIC_PREFLIGHT_MODE_SEPARATION_UNIT1_VERIFICATION_001",
            "status": "SKIP_UNIT1_SCOPE_LOCK_NOT_CHANGED",
            "base_sha": base_sha,
            "head_sha": head_sha,
            "changed_files": changed,
            "formal_proof_executed": False,
            "authorization_consumed": True,
            "proof_run_count_executed": 1,
        }
        (evidence_dir / "static-preflight-unit1-scope-verification-001.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0

    exact_allowed = set(scope["allowed_exact_paths"])
    prefix = str(scope["allowed_new_prefix"])
    disallowed = sorted(path for path in changed if path not in exact_allowed and not path.startswith(prefix))
    checker.require(not disallowed, "UNIT1_DIFF_OUTSIDE_AUTHORIZED_SCOPE", disallowed=disallowed)

    required_changed = {
        ".github/workflows/pass2-p2c-receipt038-static-preflight.yml",
        "audit/pass2/p2c-isolated-proof-rerun-008/static_preflight_receipt038.py",
        ACTIVATION_PATH,
        (UNIT_ROOT / "P2C_POST_FAILURE_STATIC_PREFLIGHT_CURRENT_AUTHORITY_RECEIPT_001.json").relative_to(REPO_ROOT).as_posix(),
        (UNIT_ROOT / "P2C_STATIC_PREFLIGHT_MODE_CONTRACT_001.json").relative_to(REPO_ROOT).as_posix(),
        (UNIT_ROOT / "test_static_preflight_modes_001.py").relative_to(REPO_ROOT).as_posix(),
        (UNIT_ROOT / "static_preflight_modes_001.py").relative_to(REPO_ROOT).as_posix(),
        pathlib.Path(__file__).relative_to(REPO_ROOT).as_posix(),
        (UNIT_ROOT / "P2C_STATIC_PREFLIGHT_MODE_SEPARATION_CURRENT_STATE_001.md").relative_to(REPO_ROOT).as_posix(),
        (UNIT_ROOT / "P2C_STATIC_PREFLIGHT_MODE_SEPARATION_LOCAL_TEST_EVIDENCE_001.json").relative_to(REPO_ROOT).as_posix(),
        (UNIT_ROOT / "P2C_STATIC_PREFLIGHT_MODE_SEPARATION_REPAIR_RECEIPT_001.json").relative_to(REPO_ROOT).as_posix(),
    }
    missing_required = sorted(required_changed - set(changed))
    checker.require(not missing_required, "UNIT1_REQUIRED_CHANGE_MISSING", missing=missing_required)

    trigger_path = str(contract["formal_proof_trigger_path"])
    checker.require(trigger_path not in changed, "UNIT1_FORMAL_TRIGGER_PATH_CHANGED", trigger_path=trigger_path)

    formal_paths = set(contract["historical_bound_git_blobs_at_live_main"])
    prohibited_changed = sorted(formal_paths & set(changed))
    checker.require(not prohibited_changed, "UNIT1_HISTORICAL_PROOF_FILE_CHANGED", paths=prohibited_changed)

    for path, expected_blob in contract["historical_bound_git_blobs_at_live_main"].items():
        base_blob = git.tree_blob(base_sha, path)
        head_blob = git.tree_blob(head_sha, path)
        checker.require(base_blob == expected_blob, "UNIT1_BASE_HISTORICAL_BLOB_MISMATCH", path=path, expected=expected_blob, actual=base_blob)
        checker.require(head_blob == expected_blob, "UNIT1_HEAD_HISTORICAL_BLOB_MISMATCH", path=path, expected=expected_blob, actual=head_blob)

    checker.require(scope["proof_execution_authorized"] is False, "UNIT1_SCOPE_EXECUTION_NOT_FALSE")
    checker.require(scope["second_proof_run_authorized"] is False, "UNIT1_SCOPE_SECOND_PROOF_NOT_FALSE")
    checker.require(scope["merge_authorized"] is False, "UNIT1_SCOPE_MERGE_NOT_FALSE")

    out = {
        "type": "PMP_APP_ORCHESTRATOR_P2C_STATIC_PREFLIGHT_MODE_SEPARATION_UNIT1_VERIFICATION_001",
        "status": "PASS_STATIC_ONLY_UNIT1_SCOPE",
        "base_sha": base_sha,
        "head_sha": head_sha,
        "changed_files": changed,
        "changed_file_count": len(changed),
        "formal_trigger_path_changed": False,
        "historical_proof_files_changed": False,
        "formal_proof_executed": False,
        "controller_invoked": False,
        "authorization_consumed": True,
        "proof_run_count_executed": 1,
        "rerun_authorized": False,
        "second_proof_run_authorized": False,
        "merge_authorized": False,
        "production_change": False,
        "current_map_change": False,
        "persisted_data_change": False,
    }
    (evidence_dir / "static-preflight-unit1-scope-verification-001.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
