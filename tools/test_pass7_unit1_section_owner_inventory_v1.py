#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "tools/run_pass7_unit1_section_owner_inventory_v1.py"
SPEC = importlib.util.spec_from_file_location("p7u1_inventory", RUNNER_PATH)
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)
ASSERTIONS = 0


def check(condition: Any, message: str) -> None:
    global ASSERTIONS
    ASSERTIONS += 1
    assert condition, message


def equal(actual: Any, expected: Any, message: str) -> None:
    global ASSERTIONS
    ASSERTIONS += 1
    assert actual == expected, f"{message}: {actual!r} != {expected!r}"


first = RUNNER.build_inventory()
second = RUNNER.build_inventory()
equal(first, second, "inventory is deterministic")
equal(first["type"], RUNNER.RESULT_TYPE, "result type")
equal(first["version"], "1.0.0", "result version")
equal(first["status"], "PASS", "result status")
check(RUNNER.verify_result_hash(first), "result hash")
equal(first["registry"]["path"], "pmp-section-owner-registry-v1.js", "registry path")
equal(first["registry"]["declared_owner_count"], 8, "eight owners declared")
equal(len(first["owners"]), 8, "eight owner rows")
equal(first["summary"]["owners_declared"], 8, "summary owners")
equal(first["summary"]["sections_inventory"], 8, "eight sections")
equal(first["summary"]["owners_with_source_candidates"], 6, "six source-bound owners")
equal(first["summary"]["owners_without_source_candidates"], 2, "two unresolved source owners")
equal(first["summary"]["observed_facts"], 6, "six observations")
equal(first["summary"]["inferred_conclusions"], 3, "three inferences")
equal(first["summary"]["unresolved_cases"], 4, "four unresolved cases")
check(first["summary"]["owner_named_root_sources"] >= 20, "owner-named sources inventoried")
check(
    first["summary"]["unregistered_owner_named_sources"] >= 10,
    "unregistered owner-named sources surfaced",
)
check(all(value is False for value in first["effects"].values()), "all effects false")
check("No owner is registered" in first["claim_ceiling"], "claim ceiling blocks registration")
check("granted authority" in first["claim_ceiling"], "claim ceiling blocks authority")

expected_ids = [
    "app_orchestrator_owner",
    "reload_current_owner",
    "mount_registry_owner",
    "bank_screen_owner",
    "continuous_run_level_owner",
    "resident_30b_owner",
    "source_gate_owner",
    "diagnostics_owner",
]
equal([row["id"] for row in first["owners"]], expected_ids, "owner declaration order")
equal(len({row["id"] for row in first["owners"]}), 8, "owner IDs unique")
equal(len({row["section"] for row in first["owners"]}), 8, "section IDs unique")

for row in first["owners"]:
    check(row["name"].endswith("Owner"), f"{row['id']}: owner name")
    check(isinstance(row["status"], str) and row["status"], f"{row['id']}: status")
    check(isinstance(row["scope"], str) and row["scope"], f"{row['id']}: scope")
    check(isinstance(row["section"], str) and row["section"], f"{row['id']}: section")
    check(isinstance(row["source_candidates"], list), f"{row['id']}: source candidates")
    equal(
        row["source_candidate_count"],
        len(row["source_candidates"]),
        f"{row['id']}: source count",
    )
    check(
        isinstance(row["lifecycle_dependencies"], list),
        f"{row['id']}: lifecycle dependencies",
    )
    check(isinstance(row["consumers"], list) and row["consumers"], f"{row['id']}: consumers")
    for source in row["source_candidates"]:
        check((ROOT / source).is_file() or RUNNER.read_tracked(source), f"{row['id']}: source exists")
    if row["source_candidates"]:
        equal(
            row["binding_status"],
            "DECLARED_WITH_SOURCE_CANDIDATE",
            f"{row['id']}: bound status",
        )
    else:
        equal(
            row["binding_status"],
            "DECLARED_WITHOUT_DEDICATED_SOURCE_CANDIDATE",
            f"{row['id']}: unresolved status",
        )

by_id = {row["id"]: row for row in first["owners"]}
equal(by_id["bank_screen_owner"]["section"], "bank", "bank section")
equal(
    by_id["continuous_run_level_owner"]["section"],
    "continuous_run",
    "continuous run section",
)
check(
    "continuous_run_level_owner"
    in by_id["bank_screen_owner"]["lifecycle_dependencies"],
    "bank depends on continuous run",
)
check(
    "bank_screen_owner"
    in by_id["continuous_run_level_owner"]["lifecycle_dependencies"],
    "continuous run depends on bank",
)
equal(by_id["resident_30b_owner"]["source_candidates"], [], "resident source unresolved")
equal(by_id["source_gate_owner"]["source_candidates"], [], "source gate source unresolved")
check(
    "pmp-diagnostics-owner-v1.js" in by_id["diagnostics_owner"]["source_candidates"],
    "diagnostics source mapped",
)
check(
    "pmp-mount-lifecycle-runtime-v1.js"
    in by_id["mount_registry_owner"]["source_candidates"],
    "mount lifecycle source mapped",
)

equal(len(first["observed_facts"]), 6, "observation rows")
equal(len({row["id"] for row in first["observed_facts"]}), 6, "observation IDs unique")
for observation in first["observed_facts"]:
    equal(observation["claim_type"], "OBSERVED", f"{observation['id']}: observed type")
    check(observation["fact"], f"{observation['id']}: fact text")
    check(observation["evidence_path"], f"{observation['id']}: evidence path")
    check(
        len(observation["evidence_sha256"]) == 64,
        f"{observation['id']}: evidence digest",
    )
    equal(
        observation["evidence_sha256"],
        RUNNER.sha_text(RUNNER.read_tracked(observation["evidence_path"])),
        f"{observation['id']}: evidence hash",
    )

observation_ids = {row["id"] for row in first["observed_facts"]}
equal(len(first["inferred_conclusions"]), 3, "inference rows")
for inference in first["inferred_conclusions"]:
    equal(inference["claim_type"], "INFERRED", f"{inference['id']}: inferred type")
    check(inference["conclusion"], f"{inference['id']}: conclusion")
    check(inference["basis_observation_ids"], f"{inference['id']}: basis")
    check(
        set(inference["basis_observation_ids"]) <= observation_ids,
        f"{inference['id']}: valid basis",
    )

equal(
    [row["kind"] for row in first["unresolved_cases"]],
    [
        "CONTRADICTORY_PRESENCE_MODELS",
        "NO_DEDICATED_SOURCE_CANDIDATE",
        "UNREGISTERED_OWNER_NAMED_SOURCES",
        "BANK_CONTINUOUS_RUN_OVERLAP",
    ],
    "exact unresolved categories",
)
equal(
    first["unresolved_cases"][1]["owners"],
    ["resident_30b_owner", "source_gate_owner"],
    "source-unresolved owners",
)
equal(
    first["unresolved_cases"][3]["owners"],
    ["bank_screen_owner", "continuous_run_level_owner"],
    "bank overlap owners",
)
check(
    all(row["blocking_effect"].startswith("Do not") or row["blocking_effect"].startswith("Defer")
        for row in first["unresolved_cases"]),
    "all unresolved cases are fail-passive",
)

check(
    "pmp-bank-continuous-run-owner-split-diagnostic-v1.js"
    in first["owner_named_sources"],
    "bank split diagnostic inventoried",
)
check(
    "pmp-boot-status-strip-owner-v1.js" in first["unregistered_owner_named_sources"],
    "boot status owner remains unregistered",
)
check(
    "pmp-bug-bank-owner-v1.js" in first["unregistered_owner_named_sources"],
    "bug bank owner remains unregistered",
)
check(
    "pmp-bank-screen-owner-v1.js" not in first["unregistered_owner_named_sources"],
    "bank screen source mapped",
)

tampered = copy.deepcopy(first)
tampered["owners"][0]["scope"] = "expanded"
equal(RUNNER.verify_result_hash(tampered), False, "tampered inventory rejected")
tampered = copy.deepcopy(first)
tampered["unresolved_cases"].pop()
equal(RUNNER.verify_result_hash(tampered), False, "missing unresolved case rejected")

print(f"PASS: P7-U1 section-owner inventory ({ASSERTIONS}/{ASSERTIONS})")
