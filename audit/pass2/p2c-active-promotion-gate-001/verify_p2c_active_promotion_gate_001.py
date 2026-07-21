#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import pathlib
import subprocess
import tarfile


BASE_MAIN = "b302081e697a2ae46ba6820eea319d647c3c8dd7"
SOURCE_COMMIT = "98b2e293717b81289e3b372d1fff8f5832d29fd6"
CAPSULE_SHA256 = "a644ad9ea538117f8aa6b01ac6988ac8d938a64fb170fa2a8f071afebc77e500"
SAFE_WRITER_SHA256 = "685afcd60d5bb997af71f6317a090f4a9e4e53adca5aa103c6edaf8be85be8c3"
ROOT = pathlib.Path(__file__).resolve().parents[3]
AUDIT_ROOT = ROOT / "audit/pass2/p2c-isolated-proof-rerun-008"
DEPS_ROOT = ROOT / "audit/pass2/p2c-isolated-proof-rerun-006"
GATE_ROOT = ROOT / "audit/pass2/p2c-active-promotion-gate-001"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def reconstruct_capsule() -> bytes:
    bundle = DEPS_ROOT / "bundle"
    prefix_text = "".join((bundle / f"part0{i}.b64").read_text() for i in range(4))
    payload = bytearray(base64.b64decode("".join(prefix_text.split())))
    for name in (
        "part04_0.bin",
        "part04_1.bin",
        "part04_2.bin",
        "part05_0.bin",
        "part05_1.bin",
        "part06_0.bin",
        "part06_1.bin",
    ):
        payload.extend((bundle / name).read_bytes())
    tail_text = "".join((bundle / "part06_2.b64").read_text().split())
    payload.extend(base64.b64decode(tail_text))
    result = bytes(payload)
    assert len(result) == 61478
    assert sha256_bytes(result) == CAPSULE_SHA256
    return result


def capsule_json(capsule: bytes, member: str) -> dict:
    with tarfile.open(fileobj=io.BytesIO(capsule), mode="r:gz") as archive:
        extracted = archive.extractfile(member)
        assert extracted is not None, member
        return json.loads(extracted.read().decode("utf-8"))


def assert_git_blob(path: pathlib.Path, expected: str) -> None:
    actual = git("hash-object", path.relative_to(ROOT).as_posix())
    assert actual == expected, (path, actual, expected)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()

    scope = load_json(GATE_ROOT / "P2C_ACTIVE_PROMOTION_SCOPE_LOCK_001.json")
    assert scope["base_main_commit"] == BASE_MAIN
    assert scope["truth_boundary"] == {
        "production_runtime_files_changed": False,
        "active_chain_integrated": False,
        "formal_proof_executed": False,
        "authorization_consumed": False,
        "pass2_complete": False,
        "pass3_started": False,
    }

    changed = set(git("diff", "--name-only", BASE_MAIN, "HEAD").splitlines())
    allowed = set(scope["allowed_changes_in_this_gate_move"])
    assert changed <= allowed, sorted(changed - allowed)

    capsule = reconstruct_capsule()
    policy = capsule_json(capsule, "policy-template.json")
    actors = policy["actors"]
    actor_by_path = {row["path"]: row for row in actors}
    assert len(actors) == len(actor_by_path) == 86
    assert len(policy["quarantine_paths"]) == 25
    assert set(policy["quarantine_paths"]) <= set(actor_by_path)

    broker_paths = sorted(path for path in actor_by_path if path.startswith("pmp-p2c-production-") and "broker" in path)
    assert len(broker_paths) == 8
    missing = []
    matches = []
    mismatches = []
    for row in actors:
        path = ROOT / row["path"]
        if not path.is_file():
            missing.append(row["path"])
            continue
        actual = sha256_file(path)
        if actual == row["sha256"]:
            matches.append(row["path"])
        else:
            mismatches.append({"path": row["path"], "frozen": row["sha256"], "current": actual})
    assert sorted(missing) == broker_paths
    assert len(matches) == 73
    expected_mismatches = {
        "pmp-current-inner-cleanbug-rgcontrols-v23.html",
        "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html",
        "pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html",
        "pmp-pass75-reload-runtime-platform-gate-v1.js",
        "pmp-route-guardian-current-loader-v22.html",
    }
    assert {row["path"] for row in mismatches} == expected_mismatches

    normalized = load_json(DEPS_ROOT / "repair009-normalized-source-manifest-002.json")
    assert normalized["type"] == "PMP_REPAIR009_NORMALIZED_SOURCE_MANIFEST_002"
    assert len(normalized["records"]) == 19
    external_original_matches = []
    document_promotion_inputs = []
    for row in normalized["records"]:
        current = sha256_file(ROOT / row["path"])
        if row["kind"] == "external":
            assert current == row["original_sha256"], row["path"]
            external_original_matches.append(row["path"])
        else:
            assert row["kind"] == "document-inline"
            document_promotion_inputs.append(row["path"])
    assert len(external_original_matches) == 15
    assert len(document_promotion_inputs) == 4

    safe_writer = ROOT / "pmp-safe-writer-current-return-fix-v1.js"
    assert sha256_file(safe_writer) == SAFE_WRITER_SHA256
    assert actor_by_path[safe_writer.name]["sha256"] == SAFE_WRITER_SHA256

    bug_watch_text = (ROOT / "pmp-bug-watch-passive-capture-v1.js").read_text(encoding="utf-8")
    assert "No fixing, deleting, moving, rerouting, rebuilding, storage clearing, or IndexedDB write." in bug_watch_text
    assert "setInterval(scan,2500)" in bug_watch_text
    assert "clearInterval(" not in bug_watch_text
    assert "save(RECEIPT" in bug_watch_text

    auth_path = AUDIT_ROOT / "P2C_NODEPATH_ROLLBACK_SOURCE_REPAIR_AUTHORIZATION_RECEIPT_082.json"
    directive_path = AUDIT_ROOT / "P2C_RECEIPT082_EXACTLY_ONE_FORMAL_PROOF_EXECUTION_DIRECTIVE_083.json"
    reseal_path = AUDIT_ROOT / "P2C_RECEIPT082_MERGED_MAIN_STATIC_RESEAL_RECEIPT_115.json"
    auth = load_json(auth_path)
    directive = load_json(directive_path)
    reseal = load_json(reseal_path)
    assert auth["status"] == "AUTHORIZED_UNCONSUMED_STATIC_ONLY"
    assert directive["status"] == "AUTHORIZED_UNCONSUMED_EXACTLY_ONE_RUN"
    assert reseal["status"] == "SEALED_STATIC_PREFLIGHT_ONLY"
    assert auth["authorization_consumed"] is directive["authorization_consumed"] is reseal["authorization_consumed"] is False
    assert auth["proof_execution_started"] is directive["proof_execution_started"] is reseal["proof_execution_started"] is False
    assert auth["proof_run_count_authorized"] == directive["proof_run_count_authorized"] == 1
    assert auth["proof_run_count_executed_under_this_receipt"] == directive["proof_run_count_executed"] == reseal["proof_run_count_executed"] == 0
    assert auth["source_repository_commit"] == directive["source_repository_commit"] == reseal["source_repository_commit"] == SOURCE_COMMIT
    assert directive["authorization_receipt_sha256"] == sha256_file(auth_path)
    assert_git_blob(auth_path, directive["authorization_receipt_git_blob_sha"])
    binding_rows = [
        (pathlib.Path(auth["formal_workflow_path"]), auth["formal_workflow_git_blob_sha"]),
        (pathlib.Path(directive["execution_wrapper_path"]), directive["execution_wrapper_git_blob_sha"]),
        (pathlib.Path(auth["formal_wrapper_path"]), auth["formal_wrapper_git_blob_sha"]),
        (pathlib.Path(auth["runtime_binding_patcher_path"]), auth["runtime_binding_patcher_git_blob_sha"]),
        (pathlib.Path(auth["formal_finalizer_path"]), auth["formal_finalizer_git_blob_sha"]),
    ]
    for relative, expected in binding_rows:
        assert_git_blob(ROOT / relative, expected)
    for key in (
        "production_application_authorized",
        "production_activation_authorized",
        "current_map_change_authorized",
        "persisted_data_change_authorized",
        "second_proof_run_authorized",
    ):
        assert auth[key] is False and directive[key] is False, key

    output = {
        "type": "PMP_APP_ORCHESTRATOR_PASS2_P2C_ACTIVE_PROMOTION_GATE_VERIFICATION_001",
        "status": "PASS_READY_FOR_EXACTLY_ONE_FORMAL_PROOF_HEAD_SEAL",
        "base_main_commit": BASE_MAIN,
        "head_commit": git("rev-parse", "HEAD"),
        "changed_paths": sorted(changed),
        "frozen_capsule": {"bytes": len(capsule), "sha256": CAPSULE_SHA256},
        "recovered_contract": {
            "governed_actor_count": len(actors),
            "exact_current_actor_matches": len(matches),
            "expected_promotion_mismatches": mismatches,
            "missing_broker_sources_to_promote": broker_paths,
            "quarantine_count": len(policy["quarantine_paths"]),
            "normalized_async_actor_count": len(normalized["records"]),
            "external_original_source_matches": len(external_original_matches),
            "document_promotion_input_count": len(document_promotion_inputs),
            "realm_count": 5,
        },
        "safe_writer_sha256": SAFE_WRITER_SHA256,
        "bug_watch_current_gap": "PASSIVE_NO_AUTOFIX_BUT_MUTABLE_RECEIPT_AND_UNBOUNDED_INTERVAL",
        "formal_proof_authorization_consumed": False,
        "formal_proof_runs_executed": 0,
        "production_runtime_changed": False,
        "active_chain_integrated": False,
        "pass2_complete": False,
        "pass3_started": False,
        "exact_next_move": "ONE_FRESH_RECEIPT082_EXACT_HEAD_SEAL_PULL_REQUEST_AND_EXACTLY_ONE_FORMAL_PROOF",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
