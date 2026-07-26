#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROTECTED_BLOBS = {
    "pmp-boot-status-strip-owner-v1.js": "7894bca06d1a850f4648159e8445d5e8b7e568ea",
    "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html": "f62cdb28d1507b1731e9ca1660b6289081433147",
    "pmp-current-map-v12.json": "709c4d953697ada70a6bc5f29eca44c68f4f6f7d",
    "pmp-current-route-resolver-v1.js": "3190d8ec65e4fbb653190cdab640de3d493df1c9",
    "pmp-route-guardian-current-loader-v22.html": "fd6ea047e87ea33ef093d78e224167a4bebc1d86",
    "pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html": "ffb45fd17cd407bf22ab2c3fb911bb3e9def0754",
    "pmp-app-orchestrator-v1.js": "6e0f9145dca873b73f6000444b8c498ff3741629",
    "pmp-app-current.html": "7742ed0c84051a66ad41b62f7ae5c165fe9a454f",
    "audit/a003-manifest-seal.json": "2d8cc9d3a7aaf29a7fe9114bf7fc6b45ad7b91a0",
}


def load(relative):
    return json.loads((ROOT / relative).read_text())


def run(*args):
    subprocess.check_call(args, cwd=ROOT)


def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def main():
    unit1 = load("audit/pass4/pass4-boot-status-strip-unit1-current-path-contract-boundary-v1.json")
    unit2 = load("audit/pass4/pass4-boot-status-strip-unit2-bounded-passive-integration-v1.json")
    unit3 = load("audit/pass4/pass4-boot-status-strip-unit3-isolated-state-fail-passive-proof-v1.json")
    unit4r = load("audit/pass4/pass4-boot-status-strip-unit4-route-guardian-interaction-repair-readiness-v1.json")
    unit4c = load("audit/pass4/pass4-boot-status-strip-unit4-hands-on-reconciliation-v1.json")
    unit5 = load("audit/pass4/pass4-boot-status-strip-unit5-closure-certification-v1.json")

    assert unit1["pass"] == 4 and unit1["unit"] == 1
    assert unit2["pass"] == 4 and unit2["unit"] == 2
    assert unit3["pass"] == 4 and unit3["unit"] == 3
    assert unit4r["status"] == "DETERMINISTIC_REPAIR_READY"
    assert unit4c["status"] == "HANDS_ON_SUCCESS_RECONCILED_PENDING_GREEN_MERGE"
    assert unit5["status"] == "CERTIFIED_PENDING_GREEN_MERGE"

    report = unit4c["user_report"]
    assert report["exact_quote"] == "it worked, what pass are we on?"
    assert report["independent_automated_observation"] is False
    assert all(report["reported_results"].values())

    preserved = unit4c["preserved_live_observation"]
    assert preserved["pull_request"] == 152
    assert preserved["workflow_run"] == 30190359765
    assert preserved["result"] == "FAIL_PRESERVED"
    assert preserved["observation_count"] == 1
    assert preserved["retried"] is False

    assert set(unit3["states_proven"]) == {
        "BOOTING",
        "BOOT_SLOW",
        "BOOT_FAILURE",
        "READY_ACKNOWLEDGED",
    }
    assert unit3["zero_effects"] == {
        "route_assignment": 0,
        "alternate_destination_consultation": 0,
        "localStorage_writes": 0,
        "sessionStorage_writes": 0,
        "indexedDB_writes": 0,
        "app_orchestrator_ownership_transfers": 0,
        "startup_repairs": 0,
        "startup_delays": 0,
        "bank_rebuilds": 0,
        "level_reorders": 0,
        "resident_changes": 0,
        "mount_registry_ownership_changes": 0,
    }

    for path, expected_blob in PROTECTED_BLOBS.items():
        assert output("git", "rev-parse", f"HEAD:{path}") == expected_blob, path
        assert unit4c["protected_main_blobs"][path] == expected_blob

    exit_criteria = unit5["exit_criteria"]
    for key in (
        "BOOTING_proven",
        "BOOT_SLOW_proven",
        "BOOT_FAILURE_proven",
        "READY_ACKNOWLEDGED_proven",
        "current_path_observed_without_observer_selected_routing",
        "unit4_and_unit5_receipts_in_branch",
    ):
        assert exit_criteria[key] is True, key
    for key in (
        "route_changes_attributable_to_strip",
        "ownership_transfers_attributable_to_strip",
        "startup_repairs_attributable_to_strip",
        "persisted_user_data_writes_attributable_to_strip",
    ):
        assert exit_criteria[key] == 0, key

    assert unit5["closure_branch_scope"] == {
        "evidence_and_verification_only": True,
        "production_runtime_changed": False,
        "runtime_integrity_changed": False,
        "persisted_user_data_changed": False,
        "pass5_implementation_started": False,
    }
    assert all(item["retry_authorized"] is False for item in unit5["preserved_failures"])
    assert unit5["formal_proof_quarantine"]["pull_request"] == 122
    assert unit5["formal_proof_quarantine"]["retry_authorized"] is False

    run("python3", "tools/test_pass4_unit1_current_path_contract_boundary_v1.py")
    run("node", "tools/test_pass4_unit2_passive_strip_integration_v1.js")
    run("node", "tools/test_pass4_unit3_isolated_state_fail_passive_proof_v1.js")
    run("node", "tools/test_pass4_unit4_route_guardian_interaction_repair_v1.js")
    print("PASS: Pass 4 Unit 4 hands-on reconciliation and Unit 5 closure certification")


if __name__ == "__main__":
    main()
