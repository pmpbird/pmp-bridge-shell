#!/usr/bin/env python3
"""Verify Packet 01.5 Applicability Evidence Catalog v1.

This verifier checks repository evidence, runtime-resolution precedence, privacy
boundaries, source-inventory integrity, and catalog policy fixtures. It performs
no real applicability classification, routing, grouping, deletion, or closure.
"""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "audit"
CATALOG_PATH = AUDIT / "applicability" / "Packet_01.5_Applicability_Evidence_Catalog_v1.json"
INVENTORY_PATH = AUDIT / "routing-inventory" / "Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
ROUTING_VERIFIER = REPO / "tools" / "verify_packet_01_5_routing_start_gate_v2.py"
ROUTING_RECEIPT = AUDIT / "Packet_01.5_Routing_Start_Authorization_Independent_Verification_v2.json"

OUT_JSON = AUDIT / "Packet_01.5_Applicability_Evidence_Catalog_Independent_Verification_v1.json"
OUT_MD = AUDIT / "Packet_01.5_Applicability_Evidence_Catalog_Independent_Verification_v1.md"
STATUS_MD = AUDIT / "Packet_01.5_Routing_Status_v77.md"

EXPECTED_INVENTORY_SHA256 = "76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477"
EXPECTED_ADDRESS_SEQUENCE_SHA256 = "3d808e1ec3f163e4cb2ab7a15767563fe7c43b9920bcecde9abe711226220916"
EXPECTED_LINES = 2750
EXPECTED_FIRST = "P01.5::B::0001"
EXPECTED_LAST = "P01.5::P069::XRES-003"
EXPECTED_STATES = [
    "CURRENT DEFECT OR LIMITATION",
    "ACTIVE CONDITIONAL RISK",
    "DORMANT FUTURE RISK",
    "OUT-OF-SCOPE CANDIDATE",
    "UNKNOWN — HOLD",
]
EXPECTED_MAP_ORDER = ["pmp-current-map-v9.json", "pmp-current-map.json"]
EXPECTED_EVIDENCE_IDS = [f"AEC-{number:03d}" for number in range(1, 13)]


class CatalogError(ValueError):
    pass


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise CatalogError(f"missing JSON source: {path.relative_to(REPO)}")
    except json.JSONDecodeError as exc:
        raise CatalogError(f"invalid JSON source {path.relative_to(REPO)}: {exc}")
    if not isinstance(value, dict):
        raise CatalogError(f"JSON source is not an object: {path.relative_to(REPO)}")
    return value


def nested(value: dict[str, Any], dotted: str) -> Any:
    current: Any = value
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            raise CatalogError(f"missing JSON path: {dotted}")
        current = current[part]
    return current


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_source_entry(entry: dict[str, Any]) -> None:
    required = {"evidence_id", "path", "tier", "freshness", "supports", "does_not_support"}
    if not required.issubset(entry):
        raise CatalogError(f"evidence entry missing required fields: {entry.get('evidence_id')}")
    if not isinstance(entry["supports"], list) or not entry["supports"]:
        raise CatalogError(f"evidence supports list is blank: {entry['evidence_id']}")
    if not isinstance(entry["does_not_support"], list) or not entry["does_not_support"]:
        raise CatalogError(f"evidence limitation list is blank: {entry['evidence_id']}")

    path = REPO / entry["path"]
    if not path.is_file():
        raise CatalogError(f"evidence path does not exist: {entry['path']}")

    text = path.read_text(encoding="utf-8")
    for marker in entry.get("required_markers", []):
        if marker not in text:
            raise CatalogError(f"required marker missing in {entry['evidence_id']}: {marker}")

    if "required_json_values" in entry:
        source = load_json(path)
        for dotted, expected in entry["required_json_values"].items():
            actual = nested(source, dotted)
            if actual != expected:
                raise CatalogError(
                    f"JSON value mismatch in {entry['evidence_id']} at {dotted}: "
                    f"expected={expected!r}, actual={actual!r}"
                )

    forbidden_fields = {
        "classification_decision",
        "record_classification_decision",
        "primary_destination",
        "secondary_destinations",
        "routing_decision",
    }
    if forbidden_fields.intersection(entry):
        raise CatalogError(f"catalog evidence entry contains a decision or destination: {entry['evidence_id']}")


def validate_catalog(catalog: dict[str, Any], verify_files: bool = True) -> None:
    if catalog.get("packet") != "01.5":
        raise CatalogError("packet identity mismatch")
    if catalog.get("artifact") != "applicability_evidence_catalog":
        raise CatalogError("catalog identity mismatch")
    if catalog.get("version") != 1:
        raise CatalogError("catalog version mismatch")
    if catalog.get("required_applicability_states") != EXPECTED_STATES:
        raise CatalogError("five-state applicability vocabulary mismatch")

    authorized = catalog.get("authorized_use", {})
    expected_false = (
        "actual_classification_performed_by_catalog",
        "routing_authorized_by_catalog",
        "semantic_grouping_authorized_by_catalog",
        "record_closure_authorized",
        "packet_04_authorized",
    )
    if authorized.get("applicability_only") is not True:
        raise CatalogError("catalog is not applicability-only")
    for field in expected_false:
        if authorized.get(field) is not False:
            raise CatalogError(f"catalog authorization boundary violated: {field}")
    for field in ("record_specific_evidence_still_required", "catalog_entry_alone_is_not_a_classification"):
        if authorized.get(field) is not True:
            raise CatalogError(f"catalog evidence boundary missing: {field}")

    rules = catalog.get("decision_rules", {})
    for field in (
        "missing_evidence",
        "conflicting_evidence",
        "stale_evidence_without_current_confirmation",
        "private_evidence_unavailable",
        "external_or_live_state_not_captured",
    ):
        if rules.get(field) != "UNKNOWN — HOLD":
            raise CatalogError(f"uncertainty does not force HOLD: {field}")
    for field in (
        "conditional_risk_may_not_be_silently_promoted",
        "discovery_heading_is_not_applicability_evidence",
        "severity_word_is_not_applicability_evidence",
        "provisional_owner_is_not_applicability_evidence",
        "destination_fields_must_remain_blank_during_applicability_only",
    ):
        if rules.get(field) is not True:
            raise CatalogError(f"decision rule missing: {field}")

    privacy = catalog.get("privacy_boundary", {})
    for field in (
        "public_safe_repository_structure_allowed",
        "public_safe_source_code_allowed",
        "local_storage_key_names_allowed",
    ):
        if privacy.get(field) is not True:
            raise CatalogError(f"public-safe evidence unexpectedly prohibited: {field}")
    for field in (
        "private_bug_memory_contents_allowed",
        "apple_notes_contents_allowed",
        "tokens_allowed",
        "passwords_allowed",
        "secrets_allowed",
        "private_local_storage_values_allowed",
        "private_values_allowed",
    ):
        if privacy.get(field) is not False:
            raise CatalogError(f"private boundary bypassed: {field}")

    tiers = catalog.get("authority_tiers")
    if not isinstance(tiers, list) or [item.get("tier") for item in tiers] != [
        "T1_GOVERNING",
        "T2_EFFECTIVE_RUNTIME_CONTROL",
        "T3_PUBLIC_SAFE_INVENTORY",
        "T4_RECORD_SPECIFIC_INSPECTION",
        "T5_UNCAPTURED_OR_PRIVATE",
    ]:
        raise CatalogError("authority tiers mismatch")

    runtime = catalog.get("runtime_resolution", {})
    if runtime.get("stable_door") != "pmp-app-current.html":
        raise CatalogError("stable door mismatch")
    if runtime.get("map_precedence") != EXPECTED_MAP_ORDER:
        raise CatalogError("map precedence mismatch")
    if runtime.get("effective_map_when_available") != EXPECTED_MAP_ORDER[0]:
        raise CatalogError("effective map mismatch")
    if runtime.get("fallback_map") != EXPECTED_MAP_ORDER[1]:
        raise CatalogError("fallback map mismatch")
    if runtime.get("effective_loader") != "pmp-route-guardian-current-loader-v14.html":
        raise CatalogError("effective loader mismatch")
    if runtime.get("effective_current_app") != "pmp-current-inner-cleanbug-rgcontrols-v4.html":
        raise CatalogError("effective current app mismatch")
    if runtime.get("effective_current_app_wraps") != "pmp-current-inner-cleanbug-rgcontrols-v3.html":
        raise CatalogError("current-app wrapper target mismatch")
    if runtime.get("manual_open_required") is not True:
        raise CatalogError("manual-open gate missing")

    sources = catalog.get("evidence_sources")
    if not isinstance(sources, list):
        raise CatalogError("evidence source list missing")
    ids = [entry.get("evidence_id") for entry in sources if isinstance(entry, dict)]
    if ids != EXPECTED_EVIDENCE_IDS or len(ids) != len(set(ids)):
        raise CatalogError("evidence IDs are missing, reordered, or duplicated")

    if verify_files:
        for entry in sources:
            if not isinstance(entry, dict):
                raise CatalogError("evidence entry is not an object")
            validate_source_entry(entry)

    source_by_id = {entry["evidence_id"]: entry for entry in sources}
    if source_by_id["AEC-007"]["freshness"] != "FALLBACK_MAP_ONLY_WHEN_HIGHER_PRECEDENCE_MAP_FAILS":
        raise CatalogError("fallback map was promoted")
    if source_by_id["AEC-010"]["freshness"] != "SUPPORTING_BASELINE_REVIEW_REQUIRED":
        raise CatalogError("manifest was promoted to current runtime authority")
    if source_by_id["AEC-011"]["freshness"] != "OLDER_NORMALIZED_SNAPSHOT_REVIEW_REQUIRED":
        raise CatalogError("older vault snapshot was promoted")
    if source_by_id["AEC-012"]["freshness"] != "HISTORICAL_UPDATE_STATUS":
        raise CatalogError("historical updater status was promoted")

    forbidden_top_level = {"record_decisions", "classification_records", "routing_records", "destinations"}
    if forbidden_top_level.intersection(catalog):
        raise CatalogError("catalog contains actual record decisions or destinations")

    authorization = catalog.get("authorization_on_independent_pass", {})
    if authorization.get("next_authorized_work") != "PACKET_01.5_PHASE_E_FIRST_CONTROLLED_APPLICABILITY_ONLY_BATCH":
        raise CatalogError("next authorized work mismatch")
    for field in ("actual_classification_performed", "actual_routing_performed", "packet_04_authorized"):
        if authorization.get(field) is not False:
            raise CatalogError(f"pass authorization exceeds boundary: {field}")
    if authorization.get("stop_before_first_record_decision") is not True:
        raise CatalogError("stop-before-first-decision boundary missing")


def expect_invalid(name: str, candidate: dict[str, Any]) -> None:
    try:
        validate_catalog(candidate, verify_files=True)
    except CatalogError:
        return
    fail(f"adversarial catalog fixture unexpectedly passed: {name}")


def verify_repository_relationships() -> dict[str, Any]:
    door = (REPO / "pmp-app-current.html").read_text(encoding="utf-8")
    require(
        "const MAP_PATHS=['pmp-current-map-v9.json','pmp-current-map.json'];" in door,
        "stable-door map precedence changed",
    )

    effective = load_json(REPO / "pmp-current-map-v9.json")
    fallback = load_json(REPO / "pmp-current-map.json")
    require(effective["route_guardian_loader"]["path"] == "pmp-route-guardian-current-loader-v14.html", "effective loader changed")
    require(effective["current_app"]["path"] == "pmp-current-inner-cleanbug-rgcontrols-v4.html", "effective current app changed")
    require(fallback["route_guardian_loader"]["path"] == "pmp-route-guardian-current-loader-v10.html", "fallback loader changed")
    require(fallback["current_app"]["path"] == "pmp-current-inner-cleanbug-rgcontrols-v3.html", "fallback current app changed")
    require(effective != fallback, "effective and fallback maps collapsed")

    loader = (REPO / effective["route_guardian_loader"]["path"]).read_text(encoding="utf-8")
    wrapper = (REPO / effective["current_app"]["path"]).read_text(encoding="utf-8")
    require("Press Open Latest App." in loader, "manual-open requirement changed")
    require("pmp-current-map-v9.json" in loader, "loader target-map relationship changed")
    require("pmp-current-inner-cleanbug-rgcontrols-v3.html" in wrapper, "v4 wrapper target changed")

    manifest = load_json(REPO / "pmp-inventory-eyes-manifest-v1.0.0.json")
    vault = load_json(REPO / "pmp-lossless-inventory-vault/current.json")
    update_status = load_json(REPO / "pmp-current-update-status.json")
    require("private Bug Memory" in manifest["privacy_rule"], "manifest private boundary changed")
    require("private values" in vault["truth_boundary"].lower(), "vault private boundary changed")
    require(update_status["target_map"] == "pmp-current-map.json", "historical updater target changed")

    effective_time = parse_iso(effective["updated_at"])
    vault_time = parse_iso(vault["report_identity"]["report_built_at"])
    update_time = parse_iso(update_status["checked_at"])
    require(effective_time > vault_time, "vault snapshot is not older than effective map")
    require(effective_time > update_time, "updater status is not older than effective map")

    return {
        "stable_door": "pmp-app-current.html",
        "map_precedence": EXPECTED_MAP_ORDER,
        "effective_map": "pmp-current-map-v9.json",
        "effective_loader": effective["route_guardian_loader"]["path"],
        "effective_current_app": effective["current_app"]["path"],
        "fallback_map": "pmp-current-map.json",
        "fallback_loader": fallback["route_guardian_loader"]["path"],
        "fallback_current_app": fallback["current_app"]["path"],
        "older_inventory_freshness_control": "PASS",
        "privacy_boundary_control": "PASS",
    }


def verify_inventory() -> dict[str, Any]:
    raw = INVENTORY_PATH.read_bytes()
    require(sha256(raw) == EXPECTED_INVENTORY_SHA256, "inventory SHA-256 changed")
    lines = raw.splitlines()
    require(len(lines) == EXPECTED_LINES, "inventory line count changed")

    addresses: list[str] = []
    baseline = 0
    provisional = 0
    for number, line in enumerate(lines, 1):
        try:
            envelope = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid inventory JSON at line {number}: {exc}")
        require(isinstance(envelope, dict), f"inventory line {number} is not an object")
        address = envelope.get("composite_address")
        require(isinstance(address, str) and address, f"inventory address missing at line {number}")
        addresses.append(address)
        if envelope.get("source_set") == "BASELINE":
            baseline += 1
        elif envelope.get("source_set") == "PROVISIONAL":
            provisional += 1
        else:
            fail(f"unknown source set at {address}")

        require(envelope.get("applicability_state") == "UNCLASSIFIED", f"source was classified at {address}")
        require(envelope.get("routing_state") == "UNROUTED", f"source was routed at {address}")
        require(envelope.get("primary_destination") is None, f"source destination populated at {address}")
        for field in (
            "applicability_evidence",
            "secondary_destinations",
            "cross_cutting_laws",
            "watch_triggers",
            "semantic_cluster_ids",
        ):
            require(envelope.get(field) == [], f"source field populated ({field}) at {address}")

    require(addresses[0] == EXPECTED_FIRST, "first address changed")
    require(addresses[-1] == EXPECTED_LAST, "last address changed")
    require(len(set(addresses)) == EXPECTED_LINES, "addresses are not unique")
    address_hash = sha256(("\n".join(addresses) + "\n").encode("utf-8"))
    require(address_hash == EXPECTED_ADDRESS_SEQUENCE_SHA256, "address sequence changed")
    require(baseline == 122 and provisional == 2628, "source-set counts changed")

    return {
        "combined_envelopes": len(lines),
        "baseline_envelopes": baseline,
        "provisional_envelopes": provisional,
        "unique_addresses": len(set(addresses)),
        "inventory_sha256": sha256(raw),
        "address_sequence_sha256": address_hash,
        "applicability_classifications_completed": 0,
        "routing_assignments_completed": 0,
        "semantic_grouping_assignments_completed": 0,
        "source_records_removed": 0,
        "source_records_closed": 0,
    }


def policy_fixtures(catalog: dict[str, Any]) -> tuple[int, int]:
    rules = catalog["decision_rules"]
    positive = 0
    for field in (
        "missing_evidence",
        "conflicting_evidence",
        "stale_evidence_without_current_confirmation",
        "private_evidence_unavailable",
        "external_or_live_state_not_captured",
    ):
        require(rules[field] == "UNKNOWN — HOLD", f"positive HOLD policy failed: {field}")
        positive += 1
    require(catalog["runtime_resolution"]["map_precedence"] == EXPECTED_MAP_ORDER, "positive map policy failed")
    positive += 1
    require(catalog["privacy_boundary"]["private_values_allowed"] is False, "positive privacy policy failed")
    positive += 1
    require(catalog["authorized_use"]["routing_authorized_by_catalog"] is False, "positive no-routing policy failed")
    positive += 1

    mutations: list[tuple[str, dict[str, Any]]] = []

    def mutated(name: str) -> dict[str, Any]:
        value = copy.deepcopy(catalog)
        mutations.append((name, value))
        return value

    value = mutated("duplicate evidence ID")
    value["evidence_sources"][1]["evidence_id"] = "AEC-001"

    value = mutated("classification performed")
    value["authorized_use"]["actual_classification_performed_by_catalog"] = True

    value = mutated("routing authorized")
    value["authorized_use"]["routing_authorized_by_catalog"] = True

    value = mutated("Packet 04 authorized")
    value["authorized_use"]["packet_04_authorized"] = True

    value = mutated("UNKNOWN HOLD removed")
    value["required_applicability_states"][-1] = "UNKNOWN"

    value = mutated("map order reversed")
    value["runtime_resolution"]["map_precedence"] = list(reversed(EXPECTED_MAP_ORDER))

    value = mutated("effective map changed")
    value["runtime_resolution"]["effective_map_when_available"] = "pmp-current-map.json"

    value = mutated("private content allowed")
    value["privacy_boundary"]["private_bug_memory_contents_allowed"] = True

    value = mutated("missing evidence promoted")
    value["decision_rules"]["missing_evidence"] = "CURRENT DEFECT OR LIMITATION"

    value = mutated("actual records inserted")
    value["record_decisions"] = [{"composite_address": EXPECTED_FIRST}]

    value = mutated("evidence path missing")
    value["evidence_sources"][0]["path"] = "audit/does-not-exist.md"

    value = mutated("fallback map promoted")
    value["evidence_sources"][6]["freshness"] = "CURRENT_EFFECTIVE_RUNTIME"

    value = mutated("vault snapshot promoted")
    value["evidence_sources"][10]["freshness"] = "CURRENT_EFFECTIVE_RUNTIME"

    value = mutated("destination separation disabled")
    value["decision_rules"]["destination_fields_must_remain_blank_during_applicability_only"] = False

    value = mutated("first record decision allowed")
    value["authorization_on_independent_pass"]["stop_before_first_record_decision"] = False

    for name, candidate in mutations:
        expect_invalid(name, candidate)

    return positive, len(mutations)


def write_outputs(
    repository: dict[str, Any],
    inventory: dict[str, Any],
    evidence_count: int,
    positive: int,
    adversarial: int,
) -> None:
    result = {
        "packet": "01.5",
        "verification": "applicability_evidence_catalog_independent",
        "version": 1,
        "status": "PASS_APPLICABILITY_EVIDENCE_CATALOG_VERIFIED",
        "watch": "NONE",
        "blockers": "NONE",
        "catalog_path": str(CATALOG_PATH.relative_to(REPO)),
        "evidence_sources_verified": evidence_count,
        "authority_tiers_verified": 5,
        "five_state_applicability_vocabulary": "PASS",
        "uncertainty_to_hold_control": "PASS",
        "applicability_destination_separation": "PASS",
        "privacy_boundary_control": "PASS",
        "runtime_map_precedence_control": "PASS",
        "effective_fallback_map_separation": "PASS",
        "older_inventory_freshness_control": "PASS",
        "record_specific_evidence_requirement": "PASS",
        "catalog_contains_no_record_decisions": "PASS",
        "positive_policy_fixtures_passed": positive,
        "adversarial_rejection_fixtures_passed": adversarial,
        **repository,
        **inventory,
        "next_authorized_work": "PACKET_01.5_PHASE_E_FIRST_CONTROLLED_APPLICABILITY_ONLY_BATCH",
        "actual_classification_performed": False,
        "actual_routing_performed": False,
        "packet_04_authorized": False,
        "stop_before_first_record_decision": True,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    md = f"""# Packet 01.5 — Applicability Evidence Catalog Independent Verification v1

STATUS: PASS — APPLICABILITY EVIDENCE CATALOG VERIFIED
WATCH: NONE
BLOCKERS: NONE
APPLICABILITY CLASSIFICATIONS COMPLETED: 0
ROUTING ASSIGNMENTS COMPLETED: 0
SEMANTIC GROUPING ASSIGNMENTS COMPLETED: 0

## Source-integrity proof

- Combined envelopes: {inventory['combined_envelopes']}
- Baseline envelopes: {inventory['baseline_envelopes']}
- Provisional envelopes: {inventory['provisional_envelopes']}
- Unique permanent addresses: {inventory['unique_addresses']}
- Inventory SHA-256: `{inventory['inventory_sha256']}`
- Address-sequence SHA-256: `{inventory['address_sequence_sha256']}`
- Blank applicability state: PASS
- Blank routing state: PASS
- Source records removed: 0
- Source records closed: 0

## Catalog proof

- Evidence sources verified: {evidence_count}
- Authority tiers verified: 5
- Five-state applicability vocabulary: PASS
- Missing/conflicting/stale/private/uncaptured evidence produces `UNKNOWN — HOLD`: PASS
- Applicability and destination remain separate: PASS
- Private-content boundary: PASS
- Record-specific evidence remains mandatory: PASS
- Catalog contains no envelope classifications or destinations: PASS

## Runtime-resolution proof

- Stable door: `pmp-app-current.html`
- Map precedence: `pmp-current-map-v9.json` then `pmp-current-map.json`
- Effective map while available: `pmp-current-map-v9.json`
- Effective loader: `{repository['effective_loader']}`
- Effective current app: `{repository['effective_current_app']}`
- Fallback loader: `{repository['fallback_loader']}`
- Fallback current app: `{repository['fallback_current_app']}`
- Effective/fallback separation: PASS
- Older manifest/vault/updater evidence cannot override newer runtime control: PASS

## Executed policy tests

- Positive fixtures passed: {positive}
- Adversarial rejection fixtures passed: {adversarial}

## Authorization result

Authorized next:

- Packet 01.5 Phase E — First Controlled Applicability-Only Batch

Not performed:

- any record applicability decision
- owner routing
- secondary-destination routing
- cross-cutting-law assignment
- semantic grouping
- record deletion or closure
- Packet 04 work

FINAL RESULT: `PASS — APPLICABILITY EVIDENCE CATALOG VERIFIED`

WATCH: NONE

BLOCKERS: NONE

END PACKET 01.5 — APPLICABILITY EVIDENCE CATALOG INDEPENDENT VERIFICATION v1
"""
    OUT_MD.write_text(md, encoding="utf-8")

    status = f"""# Packet 01.5 — Routing Status v77

STATUS: APPLICABILITY EVIDENCE CATALOG VERIFIED
WATCH: NONE
BLOCKERS: NONE
ROUTING START AUTHORIZATION: PASS UNDER CORRECTED V2 GATE
APPLICABILITY EVIDENCE CATALOG: PASS
FIRST AUTHORIZED NEXT WORK: FIRST CONTROLLED APPLICABILITY-ONLY BATCH
ROUTING ASSIGNMENTS COMPLETED: 0
APPLICABILITY CLASSIFICATIONS COMPLETED: 0
SEMANTIC GROUPING ASSIGNMENTS COMPLETED: 0
INDIVIDUAL RECORD CLOSURE: NOT AUTHORIZED
PACKET 04: NOT AUTHORIZED

## Preserved inventory

- Baseline envelopes: {inventory['baseline_envelopes']}
- Provisional envelopes: {inventory['provisional_envelopes']}
- Total envelopes: {inventory['combined_envelopes']}
- Unique addresses: {inventory['unique_addresses']}
- Inventory SHA-256: `{inventory['inventory_sha256']}`
- Address-sequence SHA-256: `{inventory['address_sequence_sha256']}`
- Blank inventory remains immutable and is the rollback source

## Verified applicability evidence boundary

- Twelve canonical repository evidence sources are registered and verified.
- Runtime resolution follows the stable door's actual map precedence.
- The v9 map is effective while available; the unversioned map is fallback evidence.
- Older Inventory Eyes, vault, and updater records are supporting evidence and require freshness review.
- Private Bug Memory contents, Apple Notes contents, secrets, and private values remain outside the public-safe catalog.
- Missing, conflicting, stale, private, or uncaptured evidence requires `UNKNOWN — HOLD`.
- Every later decision still requires record-specific evidence and independent verification.

## Stop boundary

No source envelope was classified, routed, grouped, deleted, or closed. Stop before the first record decision.

END PACKET 01.5 — ROUTING STATUS v77
"""
    STATUS_MD.write_text(status, encoding="utf-8")


def main() -> None:
    subprocess.run([sys.executable, str(ROUTING_VERIFIER)], cwd=REPO, check=True)

    routing_receipt = load_json(ROUTING_RECEIPT)
    require(routing_receipt.get("status") == "PASS_ROUTING_START_AUTHORIZED", "routing-start gate is not PASS")
    require(routing_receipt.get("watch") == "NONE", "routing-start watch exists")
    require(routing_receipt.get("blockers") == "NONE", "routing-start blocker exists")
    require(routing_receipt.get("applicability_classifications_completed") == 0, "classification already performed")
    require(routing_receipt.get("routing_assignments_completed") == 0, "routing already performed")
    require(routing_receipt.get("packet_04_authorized") is False, "Packet 04 is authorized")

    catalog = load_json(CATALOG_PATH)
    try:
        validate_catalog(catalog, verify_files=True)
    except CatalogError as exc:
        fail(str(exc))

    repository = verify_repository_relationships()
    inventory = verify_inventory()
    positive, adversarial = policy_fixtures(catalog)

    write_outputs(repository, inventory, len(catalog["evidence_sources"]), positive, adversarial)
    print("PASS: Packet 01.5 Applicability Evidence Catalog v1 independently verified.")
    print(f"Evidence sources: {len(catalog['evidence_sources'])}")
    print(f"Positive fixtures: {positive}")
    print(f"Adversarial fixtures: {adversarial}")
    print("Actual applicability classifications: 0")
    print("Actual routing assignments: 0")


if __name__ == "__main__":
    main()
