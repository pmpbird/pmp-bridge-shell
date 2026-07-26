#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "audit/pass9/pass9-bank-continuous-run-unit1-inventory-v1.json"
RECEIPT = ROOT / "audit/pass9/receipts/RECEIPT_P9_U1_BANK_CONTINUOUS_RUN_INVENTORY_20260726T192000Z_001.json"
RUNNER = ROOT / "tools/run_pass9_unit1_bank_continuous_run_inventory_v1.py"
INPUTS = {
    "pass8_closure_sha256": "audit/pass8/pass8-helper-unit6-closure-certification-v1.json",
    "current_map_sha256": "pmp-current-map-v12.json",
    "runtime_manifest_sha256": "pmp-runtime-integrity-manifest-v1.json",
    "safe_area_loader_sha256": "pmp-safe-area-surface-fill-v1.js",
    "inner_v30_sha256": "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html",
    "inner_v23_sha256": "pmp-current-inner-cleanbug-rgcontrols-v23.html",
    "inner_v4_sha256": "pmp-current-inner-cleanbug-rgcontrols-v4.html",
    "inner_v3_sha256": "pmp-current-inner-cleanbug-rgcontrols-v3.html",
    "historic_fix_001_sha256": "pmp-pass9-fix-001-bank-owner-slot-contract-20260710A.json",
    "historic_fix_002_sha256": "pmp-pass9-fix-002-fill-continuous-run-owner-slot-20260710A.json",
    "historic_working_point_sha256": "pmp-restore-checkpoint-pass9-bank-control-diagnostics-stable-20260710A.json",
    "runner_sha256": "tools/run_pass9_unit1_bank_continuous_run_inventory_v1.py",
    "test_sha256": "tools/test_pass9_unit1_bank_continuous_run_inventory_v1.py",
}
ASSERTIONS = 0


def equal(actual: Any, expected: Any, message: str) -> None:
    global ASSERTIONS
    ASSERTIONS += 1
    assert actual == expected, f"{message}: {actual!r} != {expected!r}"


def check(condition: Any, message: str) -> None:
    global ASSERTIONS
    ASSERTIONS += 1
    assert condition, message


def bytes_for(path: str) -> bytes:
    local = ROOT / path
    if local.is_file():
        return local.read_bytes()
    return subprocess.check_output(["git", "show", f"HEAD:{path}"], cwd=ROOT)


def sha(path: str) -> str:
    return hashlib.sha256(bytes_for(path)).hexdigest()


report = json.loads(REPORT.read_text())
receipt = json.loads(RECEIPT.read_text())
result = json.loads(
    subprocess.check_output([sys.executable, str(RUNNER)], cwd=ROOT, text=True)
)

equal(report["type"], "PMP_PASS9_BANK_CONTINUOUS_RUN_UNIT1_INVENTORY_V1", "type")
equal(report["version"], "1.0.0", "version")
equal(report["base_main_commit"], "92069614248bce9aea81822ad6df1cf1a030f6a8", "base")
equal(report["pass"], 9, "pass")
equal(report["unit_id"], "P9-U1", "unit")
equal(report["status"], "BANK_CONTINUOUS_RUN_INVENTORY_PROVEN", "status")
equal(receipt["status"], report["status"], "receipt status")
equal(receipt["evidence"], REPORT.relative_to(ROOT).as_posix(), "receipt evidence")
for key, path in INPUTS.items():
    equal(report["inputs"][key], sha(path), f"input hash {path}")

equal(result["type"], "PMP_PASS9_UNIT1_BANK_CONTINUOUS_RUN_INVENTORY_RESULT_V1", "runner type")
equal(result["repository_commit"], report["base_main_commit"], "runner commit")
equal(result["effects"], {
    "production_files_changed": False,
    "browser_launched": False,
    "network_requests": False,
    "storage_writes": False,
    "bank_mutations": False,
    "persisted_user_data_changed": False,
    "live_observation_performed": False,
    "formal_proof_performed": False,
}, "runner zero effects")

active = result["active_chain"]
equal(active["map"], "pmp-current-map-v12.json", "current map")
equal(active["frames"], report["inventory"]["active_chain_frames"], "active frames")
equal(len(active["frames"]), 4, "four active frames")
equal(active["direct_script_occurrences"], 120, "direct scripts")
equal(len(active["dynamic_safe_area_dependencies"]), 5, "dynamic dependencies")
equal(
    [row["path"] for row in active["dynamic_safe_area_dependencies"]],
    [
        "pmp-diagnostics-owner-v1.js",
        "pmp-diagnostics-bottom-tab-forcer-v1.js",
        "pmp-bank-load-guardian-v1.js",
        "pmp-bank-home-visibility-guard-v1.js",
        "pmp-bank-owner-dependency-bridge-v1.js",
    ],
    "dynamic dependency order",
)

inventory = result["inventory"]
equal(inventory["relevant_occurrences"], 37, "relevant occurrences")
equal(inventory["unique_relevant_sources"], 35, "unique relevant sources")
equal(inventory["role_counts"], report["inventory"]["role_counts"], "role counts")
equal(sum(inventory["role_counts"].values()), 35, "role total")
equal(inventory["duplicate_relevant_sources"], report["inventory"]["duplicate_relevant_sources"], "duplicates")
equal(len(inventory["duplicate_relevant_sources"]), 2, "duplicate source count")
equal(len(inventory["storage_writer_sources"]), 24, "storage writer count")
equal(len(inventory["interval_sources"]), 19, "interval source count")
equal(len(inventory["sources"]), 35, "source rows")
check(all(row["integrity_manifest_present"] for row in inventory["sources"]), "all manifest present")
check(all(row["integrity_manifest_sha256_matches"] for row in inventory["sources"]), "all hashes match")
equal(len({row["path"] for row in inventory["sources"]}), 35, "source paths unique")

sources = {row["path"]: row for row in inventory["sources"]}
for path, role in (
    ("pmp-master-bank-inventory-router-v1.js", "BANK_FACT_OR_PERSISTENCE"),
    ("pmp-master-bank-tab-v1.js", "BANK_FACT_OR_PERSISTENCE"),
    ("pmp-continuous-run-state-bank-v1.js", "CONTINUOUS_RUN_LIFECYCLE"),
    ("pmp-bank-screen-owner-v1.js", "MIXED_BANK_CONTINUOUS_RUN_BOUNDARY"),
    ("pmp-bank-owner-dependency-bridge-v1.js", "MIXED_BANK_CONTINUOUS_RUN_BOUNDARY"),
):
    check(path in sources, f"{path} inventoried")
    equal(sources[path]["role"], role, f"{path} role")

router = sources["pmp-master-bank-inventory-router-v1.js"]
equal(router["sha256"], report["critical_sources"]["bank_router"]["sha256"], "router hash")
check("PMPMasterBankInventoryRouterV1" in router["global_exports"], "router global")
equal(router["storage_set_calls"], 1, "router storage writes")

bank = sources["pmp-master-bank-tab-v1.js"]
equal(bank["sha256"], report["critical_sources"]["bank_shell_owner"]["sha256"], "Bank shell hash")
check("PMPMasterBankTabV1" in bank["global_exports"], "Bank shell global")
equal(bank["interval_calls"], 1, "Bank shell interval")

state = sources["pmp-continuous-run-state-bank-v1.js"]
equal(state["sha256"], report["critical_sources"]["continuous_run_state"]["sha256"], "state hash")
check("PMPContinuousRunStateBankV1" in state["global_exports"], "state global")
equal(state["storage_remove_calls"], 3, "state clear calls")
for key in report["critical_sources"]["continuous_run_state"]["persisted_keys"]:
    check(key in state["storage_keys"], f"state key {key}")

slot = sources["pmp-bank-screen-owner-v1.js"]
equal(slot["sha256"], report["critical_sources"]["continuous_run_slot_painter"]["sha256"], "slot painter hash")
check("PMPBankScreenOwnerV1" in slot["global_exports"], "slot painter global")
equal(slot["interval_calls"], 1, "slot painter interval")
check("pmp_bank_project_registry_v1" in slot["storage_keys"], "slot registry key")

bridge = sources["pmp-bank-owner-dependency-bridge-v1.js"]
equal(bridge["sha256"], report["critical_sources"]["cross_frame_dependency_bridge"]["sha256"], "bridge hash")
check("PMPBankOwnerDependencyBridgeV1" in bridge["global_exports"], "bridge global")

historic = inventory["historic_working_points"]
equal(len(historic), 3, "historic working points")
equal([row["status"] for row in historic], [
    "IMPLEMENTED_NEEDS_VISUAL_TEST",
    "IMPLEMENTED_NEEDS_VISUAL_TEST",
    "PASS9_WORKING_POINT_NOT_CERTIFIED",
], "historic statuses")
equal([row["certification_status"] for row in historic[:2]], ["not_certified", "not_certified"], "uncertified fixes")
equal(historic[2]["user_verified"], True, "working point user verified")
equal(
    [row["path"] for row in historic],
    [row["path"] for row in report["inventory"]["historic_working_points"]],
    "historic paths",
)

runner_conflicts = result["conflicts"]
report_conflicts = report["conflicts"]
equal(len(runner_conflicts), 9, "runner conflicts")
equal(len(report_conflicts), 9, "report conflicts")
equal([row["id"] for row in runner_conflicts], [row["id"] for row in report_conflicts], "conflict IDs")
for row in runner_conflicts:
    check(row["paths"], f"{row['id']} paths")
    check(row["fact"], f"{row['id']} fact")
    check(row["required_resolution"].startswith(("P9-U2", "P9-U3", "Continuous", "Treat")), f"{row['id']} resolution")
equal(result["boundaries"]["bank_owner"], "bank_screen_owner", "Bank owner")
equal(result["boundaries"]["continuous_run_owner"], "continuous_run_level_owner", "Continuous Run owner")
equal(result["boundaries"]["cross_delegation"], "FORBIDDEN", "cross delegation")
equal(result["boundaries"]["persisted_data_mutation_in_p9_u1"], "FORBIDDEN", "no data mutation")
equal(result["boundaries"]["actual_repair_target"], "P9-U3", "repair target")

contract = report["p9_u2_requirements"]
equal(contract["canonical_bank_owner"], "bank_screen_owner", "contract Bank owner")
equal(contract["canonical_continuous_run_owner"], "continuous_run_level_owner", "contract run owner")
equal(contract["separate_sections"], True, "separate sections")
equal(contract["cross_delegation"], "FORBIDDEN", "contract no cross delegation")
equal(len(contract["required_cross_owner_request_fields"]), 13, "request fields")
check("delete and clear denied by default" in contract["required_behaviors"], "delete clear deny")
check("no persisted-data migration in P9-U2 or P9-U3" in contract["required_behaviors"], "no migration")

gate = report["no_blind_flying_gate"]
equal(gate["ci_lane"], "static_contract", "gate lane")
equal(gate["diagnostic_matrix_update"]["status"], "CONFIRMED_UNCHANGED", "matrix unchanged")
equal(len(gate["diagnostic_evidence_routes"]), 1, "one evidence route")
equal(gate["fault_injection"]["status"], "NOT_APPLICABLE", "no fault injection")
equal(gate["fault_injection"]["cases"], [], "fault cases empty")
equal(len(gate["required_artifact_roles"]), 9, "artifact roles")
equal(gate["upload_before_enforcement"], True, "upload first")
equal(gate["automatic_retry"], False, "no retry")
equal(gate["special_authority"]["consumed"], False, "no special authority")

check(all(value is False for value in report["effects"].values()), "report zero effects")
check(all(value is False for value in receipt["effects"].values()), "receipt zero effects")
equal(report["authority"]["special_authority_type"], "NONE", "authority type")
equal(report["authority"]["special_authority_consumed"], False, "authority unconsumed")
equal(report["next_step"]["id"], "P9-U2", "next step")
equal(report["next_step"]["requires_user_app_check"], False, "no app check")
equal(report["next_step"]["requires_new_explicit_authority"], False, "no new authority")
equal(report["next_step"]["stop_after"], False, "continue")
equal(receipt["next_safe_move"]["step_id"], "P9-U2", "receipt next")

print(f"PASS: P9-U1 Bank and Continuous Run active-chain inventory ({ASSERTIONS}/{ASSERTIONS})")
