#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys
from typing import Any, Iterable, Mapping, Sequence

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
HIST = REPO_ROOT / "audit/pass2/p2c-isolated-proof-rerun-008"
UNIT = pathlib.Path(__file__).resolve().parent
WORKFLOW = REPO_ROOT / ".github/workflows/pass2-p2c-receipt038-static-preflight.yml"
AUTH = HIST / "P2C_NODEPATH_ROLLBACK_SOURCE_REPAIR_AUTHORIZATION_RECEIPT_082.json"
DIRECTIVE = HIST / "P2C_RECEIPT082_EXACTLY_ONE_FORMAL_PROOF_EXECUTION_DIRECTIVE_083.json"
RESEAL = HIST / "P2C_RECEIPT082_MERGED_MAIN_STATIC_RESEAL_RECEIPT_115.json"
CURRENT = UNIT / "P2C_POST_FAILURE_STATIC_PREFLIGHT_CURRENT_AUTHORITY_RECEIPT_001.json"
CONTRACT = UNIT / "P2C_STATIC_PREFLIGHT_MODE_CONTRACT_001.json"
SCOPE = UNIT / "P2C_POST_FAILURE_STATIC_PREFLIGHT_SCOPE_LOCK_001.json"
MODE_MAINTENANCE = "maintenance_reseal"
MODE_EXACT_HEAD_SEAL = "exact_head_seal"
VALID_MODES = {MODE_MAINTENANCE, MODE_EXACT_HEAD_SEAL}


class StaticPreflightError(RuntimeError):
    def __init__(self, code: str, **details: Any) -> None:
        self.code, self.details = code, details
        super().__init__(json.dumps({"code": code, "details": details}, sort_keys=True))


def require(value: bool, code: str, **details: Any) -> None:
    if not value:
        raise StaticPreflightError(code, **details)


def load(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blob_bytes(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def blob_file(path: pathlib.Path) -> str:
    return blob_bytes(path.read_bytes())


def select_mode(changed: Sequence[str], trigger: str) -> str:
    return MODE_EXACT_HEAD_SEAL if trigger in changed else MODE_MAINTENANCE


def validate_mode_shape(mode: str, changed: Sequence[str], trigger: str) -> None:
    require(mode in VALID_MODES, "UNEXPECTED_STATIC_PREFLIGHT_MODE", mode=mode)
    require(bool(changed), "EMPTY_PULL_REQUEST_DIFF")
    require(not any(p.endswith(".pyc") or "/__pycache__/" in p for p in changed), "PYTHON_CACHE_PATH_IN_DIFF")
    if mode == MODE_MAINTENANCE:
        require(trigger not in changed, "MAINTENANCE_MODE_TRIGGER_PATH_PRESENT", changed=list(changed))
    else:
        require(list(changed) == [trigger], "EXACT_HEAD_SEAL_DIFF_NOT_EXACTLY_ONE_ALLOWED_PATH", actual=list(changed))


def validate_current_authority_state(state: Mapping[str, Any]) -> None:
    expected = {
        "status": "CONSUMED_PROOF_FAILED_STATIC_REPAIR_UNIT_1_ONLY",
        "canonical_checkpoint": "V27",
        "canonical_checkpoint_sha256": "dc7b9f18da096b7351bdbf103e680ff4905697decae83f451ccc2d7c6c387797",
        "repository": "pmpbird/pmp-bridge-shell",
        "live_main_anchor": "9c2a9959131e2367477d84404ce94f63694edc76",
        "formal_proof_pr": 122,
        "formal_proof_pr_state": "OPEN_UNMERGED",
        "formal_proof_pr_head": "ea337f534e89c04b842e3d88513be6d052b9e410",
        "formal_proof_run_id": 29835177022,
        "formal_proof_result": "FAIL",
        "authorization_consumed": True,
        "proof_execution_started": True,
        "proof_run_count_executed": 1,
        "receipt082_is_historical_record_only": True,
        "directive083_is_historical_record_only": True,
        "historical_unconsumed_fields_are_not_current_authority": True,
        "rerun_authorized": False,
        "second_proof_run_authorized": False,
        "merge_authorized": False,
        "production_application_authorized": False,
        "production_activation_authorized": False,
        "current_map_change_authorized": False,
        "persisted_data_change_authorized": False,
        "candidate_runtime_repair_authorized": False,
        "pass3_authorized": False,
        "static_preflight_repair_authorized": True,
        "formal_proof_execution_authorized": False,
    }
    for key, value in expected.items():
        require(state.get(key) == value, "CURRENT_POST_FAILURE_AUTHORITY_STATE_INVALID", key=key, expected=value, actual=state.get(key))


def validate_seal_document(
    seal: Mapping[str, Any], descriptor: Mapping[str, Any], *, base_sha: str, head_parent: str,
    actual_sha256: str, actual_git_blob_sha: str, actual_directive_sha256: str,
    actual_directive_git_blob_sha: str, actual_authorization_sha256: str,
) -> None:
    require(head_parent == base_sha, "EXACT_HEAD_SEAL_PARENT_NOT_PULL_REQUEST_BASE")
    require(seal.get("status") == "SEALED_EXACT_FINAL_PR_HEAD", "INCORRECT_HEAD_SEAL_STATUS")
    require(seal.get("sealed_parent_commit") == base_sha, "INCORRECT_HEAD_SEAL_PARENT")
    require(descriptor.get("sealed_parent_commit") == base_sha, "ALLOWED_SEAL_DESCRIPTOR_PARENT_MISMATCH")
    require(actual_sha256 == descriptor.get("sha256"), "INCORRECT_HEAD_SEAL_SHA256")
    require(actual_git_blob_sha == descriptor.get("git_blob_sha"), "INCORRECT_HEAD_SEAL_GIT_BLOB")
    require(seal.get("directive_path") == descriptor.get("directive_path"), "INCORRECT_HEAD_SEAL_DIRECTIVE_PATH")
    require(seal.get("directive_sha256") == actual_directive_sha256 == descriptor.get("directive_sha256"), "STALE_DIRECTIVE_SHA256_BINDING")
    require(seal.get("directive_git_blob_sha") == actual_directive_git_blob_sha == descriptor.get("directive_git_blob_sha"), "STALE_DIRECTIVE_GIT_BLOB_BINDING")
    require(seal.get("authorization_receipt_sha256") == actual_authorization_sha256 == descriptor.get("authorization_receipt_sha256"), "STALE_AUTHORIZATION_RECEIPT_SHA256_BINDING")
    require(seal.get("proof_run_count_authorized") == 1, "INCORRECT_HEAD_SEAL_AUTHORIZED_RUN_COUNT")
    require(seal.get("proof_run_count_executed") == 0, "HISTORICAL_HEAD_SEAL_EXECUTED_COUNT_CHANGED")
    for key in ("rerun_authorized", "second_proof_run_authorized", "merge_authorized", "production_activation_authorized"):
        require(seal.get(key) is False, "HEAD_SEAL_SAFETY_FLAG_INVALID", key=key)
    require(descriptor.get("validation_only") is True and descriptor.get("formal_execution_authorized") is False, "EXACT_HEAD_SEAL_DESCRIPTOR_NOT_STATIC_ONLY")


def validate_static_workflow_text(text: str, forbidden: Iterable[str]) -> None:
    for token in forbidden:
        require(token not in text, "FORBIDDEN_FORMAL_EXECUTION_TOKEN_IN_STATIC_WORKFLOW", token=token)
    commands = [line.strip().partition(":")[2].strip() for line in text.splitlines() if line.strip().startswith("run:")]
    require(len(commands) >= 3, "STATIC_WORKFLOW_MISSING_REQUIRED_PYTHON_STEPS")
    for command in commands:
        require(command.startswith("python3 "), "NON_PYTHON_COMMAND_IN_STATIC_WORKFLOW", command=command)


class GitReader:
    def __init__(self, root: pathlib.Path, allowed: Iterable[str]) -> None:
        self.root, self.allowed = root, set(allowed)

    def run_command(self, argv: Sequence[str]) -> str:
        require(bool(argv), "EMPTY_STATIC_COMMAND")
        require(argv[0] == "git", "NON_GIT_STATIC_COMMAND_REJECTED", argv=list(argv))
        require(len(argv) > 1 and argv[1] in self.allowed, "UNAUTHORIZED_GIT_SUBCOMMAND_REJECTED", argv=list(argv))
        return subprocess.run(list(argv), cwd=self.root, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False).stdout.strip()

    def git(self, *args: str) -> str:
        return self.run_command(("git", *args))

    def changed(self, base: str, head: str) -> list[str]:
        text = self.git("diff", "--name-only", base, head)
        return text.splitlines() if text else []

    def tree_blob(self, commit: str, path: str) -> str:
        return self.git("rev-parse", f"{commit}:{path}")

    def working_blob(self, path: str) -> str:
        return self.git("hash-object", path)

    def parent(self, commit: str) -> str:
        return self.git("rev-parse", f"{commit}^")

    def ancestor(self, older: str, newer: str, code: str) -> None:
        try:
            self.git("merge-base", "--is-ancestor", older, newer)
        except subprocess.CalledProcessError as exc:
            raise StaticPreflightError(code, ancestor=older, descendant=newer) from exc


def verify_bindings(git: GitReader, base: str, head: str, mode: str, contract: Mapping[str, Any], auth: Mapping[str, Any], directive: Mapping[str, Any], reseal: Mapping[str, Any]) -> dict[str, str]:
    bound, trigger = dict(contract["historical_bound_git_blobs_at_live_main"]), str(contract["formal_proof_trigger_path"])
    git.ancestor(str(contract["historical_authorization_anchor"]), base, "HISTORICAL_AUTHORIZATION_ANCHOR_NOT_ANCESTOR_OF_BASE")
    git.ancestor(str(contract["historical_source_repository_commit"]), base, "SOURCE_REPOSITORY_COMMIT_NOT_ANCESTOR_OF_BASE")
    git.ancestor(str(contract["post_failure_live_main_anchor"]), base, "POST_FAILURE_MAIN_ANCHOR_NOT_ANCESTOR_OF_BASE")
    for path, expected in bound.items():
        require(git.tree_blob(base, path) == expected, "BASE_TREE_HISTORICAL_BLOB_MISMATCH", path=path)
        if mode != MODE_EXACT_HEAD_SEAL or path != trigger:
            require(git.tree_blob(head, path) == expected, "HISTORICAL_PROOF_FILE_CHANGED", path=path)
            require(git.working_blob(path) == expected, "WORKING_TREE_NOT_PR_HEAD", path=path)
    auth_sha, directive_sha = sha256(AUTH), sha256(DIRECTIVE)
    auth_blob, directive_blob, reseal_blob = blob_file(AUTH), blob_file(DIRECTIVE), blob_file(RESEAL)
    require(auth_blob == bound[AUTH.relative_to(REPO_ROOT).as_posix()], "STALE_AUTHORIZATION_RECEIPT_GIT_BLOB")
    require(directive_blob == bound[DIRECTIVE.relative_to(REPO_ROOT).as_posix()], "STALE_DIRECTIVE_GIT_BLOB")
    require(reseal_blob == bound[RESEAL.relative_to(REPO_ROOT).as_posix()], "STALE_RESEAL_GIT_BLOB")
    require(directive.get("authorization_receipt_sha256") == auth_sha and directive.get("authorization_receipt_git_blob_sha") == auth_blob, "STALE_AUTHORIZATION_RECEIPT_BINDING")
    require(reseal.get("authorization_receipt_sha256") == auth_sha and reseal.get("authorization_receipt_git_blob_sha") == auth_blob, "STALE_RESEAL_AUTHORIZATION_BINDING")
    require(reseal.get("execution_directive_sha256") == directive_sha and reseal.get("execution_directive_git_blob_sha") == directive_blob, "STALE_RESEAL_DIRECTIVE_BINDING")
    require(auth.get("formal_proof_trigger_path") == directive.get("formal_proof_trigger_path") == reseal.get("formal_proof_trigger_path") == trigger, "HISTORICAL_TRIGGER_PATH_MISMATCH")
    source = str(contract["historical_source_repository_commit"])
    require(auth.get("source_repository_commit") == directive.get("source_repository_commit") == reseal.get("source_repository_commit") == source, "HISTORICAL_SOURCE_COMMIT_MISMATCH")
    formal_text = (REPO_ROOT / str(auth["formal_workflow_path"])).read_text(encoding="utf-8")
    require(formal_text.count("    paths:\n      - " + trigger + "\n") == 1, "FORMAL_WORKFLOW_TRIGGER_BINDING_INVALID")
    require("workflow_dispatch" not in formal_text, "FORMAL_WORKFLOW_HAS_MANUAL_DISPATCH")
    require(formal_text.count("      SOURCE_COMMIT: " + source + "\n") == 1, "FORMAL_WORKFLOW_SOURCE_BINDING_INVALID")
    for key in ("production_application_authorized", "production_activation_authorized", "current_map_change_authorized", "persisted_data_change_authorized", "merge_authorized", "second_proof_run_authorized"):
        require(auth.get(key) is False and directive.get(key) is False and reseal.get(key) is False, "HISTORICAL_SAFETY_FLAG_INVALID", key=key)
    return {"authorization_receipt_sha256": auth_sha, "authorization_receipt_git_blob_sha": auth_blob, "execution_directive_sha256": directive_sha, "execution_directive_git_blob_sha": directive_blob}


def run_preflight(mode: str, base: str, head: str) -> dict[str, Any]:
    auth, directive, reseal = load(AUTH), load(DIRECTIVE), load(RESEAL)
    current, contract, scope = load(CURRENT), load(CONTRACT), load(SCOPE)
    validate_current_authority_state(current)
    require(scope.get("proof_execution_authorized") is False and scope.get("second_proof_run_authorized") is False and scope.get("merge_authorized") is False, "UNIT_SCOPE_SAFETY_FLAG_INVALID")
    git = GitReader(REPO_ROOT, contract["static_command_policy"]["allowed_git_subcommands"])
    changed, trigger = git.changed(base, head), str(contract["formal_proof_trigger_path"])
    validate_mode_shape(mode, changed, trigger)
    validate_static_workflow_text(WORKFLOW.read_text(encoding="utf-8"), contract["forbidden_workflow_tokens"])
    summary = verify_bindings(git, base, head, mode, contract, auth, directive, reseal)
    exact = False
    if mode == MODE_EXACT_HEAD_SEAL:
        rows = [r for r in contract["allowed_exact_head_seals"] if r.get("path") == trigger]
        require(len(rows) == 1, "ALLOWED_EXACT_HEAD_SEAL_DESCRIPTOR_COUNT_INVALID")
        seal_path, descriptor = REPO_ROOT / trigger, rows[0]
        require(git.working_blob(trigger) == git.tree_blob(head, trigger), "HEAD_SEAL_WORKING_TREE_NOT_PR_HEAD")
        validate_seal_document(load(seal_path), descriptor, base_sha=base, head_parent=git.parent(head), actual_sha256=sha256(seal_path), actual_git_blob_sha=blob_file(seal_path), actual_directive_sha256=summary["execution_directive_sha256"], actual_directive_git_blob_sha=summary["execution_directive_git_blob_sha"], actual_authorization_sha256=summary["authorization_receipt_sha256"])
        exact = True
    return {
        "type": "PMP_APP_ORCHESTRATOR_P2C_POST_FAILURE_STATIC_PREFLIGHT_RESULT_001",
        "status": "PASS_MAINTENANCE_RESEAL_STATIC_ONLY" if mode == MODE_MAINTENANCE else "PASS_EXACT_HEAD_SEAL_STATIC_VALIDATION_ONLY",
        "mode": mode, "base_sha": base, "head_sha": head, "changed_files": changed,
        "formal_proof_trigger_path": trigger, "formal_proof_trigger_path_changed": trigger in changed,
        "exact_head_seal_validated": exact, "current_authorization_consumed": True,
        "current_proof_run_count_executed": 1, "current_formal_proof_result": "FAIL",
        "historical_receipt082_status_at_seal_time": auth.get("status"),
        "historical_directive083_status_at_seal_time": directive.get("status"),
        "historical_unconsumed_fields_are_current_authority": False,
        "formal_proof_execution_authorized": False, "rerun_authorized": False,
        "second_proof_run_authorized": False, "merge_authorized": False,
        "production_application_authorized": False, "production_activation_authorized": False,
        "current_map_change_authorized": False, "persisted_data_change_authorized": False,
        "static_git_subcommands_only": sorted(contract["static_command_policy"]["allowed_git_subcommands"]),
        "controller_or_proof_invoked": False, **summary,
    }


def need(value: str | None, env: str) -> str:
    result = value or os.environ.get(env)
    require(bool(result), "REQUIRED_ARGUMENT_OR_ENVIRONMENT_MISSING", name=env)
    return str(result)


def write_failure(directory: pathlib.Path, error: BaseException, mode: str | None, base: str | None, head: str | None) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    code = error.code if isinstance(error, StaticPreflightError) else type(error).__name__
    details = error.details if isinstance(error, StaticPreflightError) else {"message": str(error)}
    payload = {"type": "PMP_APP_ORCHESTRATOR_P2C_POST_FAILURE_STATIC_PREFLIGHT_FAILURE_001", "status": "FAIL_CLOSED_STATIC_ONLY", "mode": mode, "base_sha": base, "head_sha": head, "error_code": code, "details": details, "current_authorization_consumed": True, "current_proof_run_count_executed": 1, "formal_proof_execution_authorized": False, "controller_or_proof_invoked": False}
    (directory / "static-preflight-failure-post-failure-001.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode"); parser.add_argument("--select-mode", action="store_true")
    parser.add_argument("--base-sha"); parser.add_argument("--head-sha")
    parser.add_argument("--evidence-dir", type=pathlib.Path); parser.add_argument("--github-output", type=pathlib.Path)
    args = parser.parse_args(argv)
    evidence = args.evidence_dir or pathlib.Path(os.environ.get("EVIDENCE_DIR", "/tmp/p2c-receipt038-static-preflight"))
    mode, base, head = args.mode or os.environ.get("P2C_STATIC_PREFLIGHT_MODE"), None, None
    try:
        base, head = need(args.base_sha, "BASE_SHA"), need(args.head_sha, "PR_HEAD_SHA")
        contract = load(CONTRACT); git = GitReader(REPO_ROOT, contract["static_command_policy"]["allowed_git_subcommands"])
        changed = git.changed(base, head); selected = select_mode(changed, str(contract["formal_proof_trigger_path"]))
        if args.select_mode:
            require(args.github_output is not None, "GITHUB_OUTPUT_PATH_REQUIRED_FOR_MODE_SELECTION")
            args.github_output.parent.mkdir(parents=True, exist_ok=True)
            with args.github_output.open("a", encoding="utf-8") as handle: handle.write(f"mode={selected}\n")
            print(json.dumps({"selected_mode": selected, "changed_files": changed}, indent=2, sort_keys=True)); return 0
        require(mode is not None, "STATIC_PREFLIGHT_MODE_REQUIRED")
        require(mode == selected, "EXPLICIT_MODE_DOES_NOT_MATCH_DIFF", explicit_mode=mode, selected_mode=selected)
        result = run_preflight(mode, base, head); evidence.mkdir(parents=True, exist_ok=True)
        (evidence / "static-preflight-result-post-failure-001.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True)); return 0
    except BaseException as exc:
        write_failure(evidence, exc, mode, base, head)
        if isinstance(exc, StaticPreflightError): print(str(exc), file=sys.stderr); return 1
        raise
