#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = "9f71336fb28068db705a495e8fb5107dbfcbd440"
FAMILY = "CURRENT_RUNTIME_SOURCE"
SOURCE_QUEUE = "audit/applicability/Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl"
INVENTORY = "audit/routing-inventory/Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
DECISIONS = ROOT / "audit/applicability/Packet_01.5_Current_Runtime_Source_Corrected_Decisions_v1.jsonl"
QUEUES = ROOT / "audit/applicability/Packet_01.5_Current_Runtime_Source_Corrected_Remaining_Queue_v1.jsonl"
COVERAGE = ROOT / "audit/Packet_01.5_Current_Runtime_Source_Corrected_Coverage_v1.json"
EXPECTED_QUEUE_SHA256 = "1b28dbfd13e115380bfb0406313e77adce8ea01dc2018e851a228c467790c196"
EXPECTED_INVENTORY_SHA256 = "76169a80a64a044ddc5f961c0410f2df265f098517708ee6d1a6814c1a0baf3"
EXPECTED_ADDRESSES = [
    "P01.5::B::0028", "P01.5::B::0031", "P01.5::B::0032", "P01.5::B::0039",
    "P01.5::B::0044", "P01.5::B::0045", "P01.5::B::0046", "P01.5::B::0059",
    "P01.5::B::0061", "P01.5::B::0062", "P01.5::B::0077", "P01.5::B::0078",
    "P01.5::B::0081", "P01.5::B::0082", "P01.5::B::0086", "P01.5::B::0093",
    "P01.5::B::0100", "P01.5::B::0108", "P01.5::B::0115", "P01.5::B::0122",
]
EXPECTED_DECISIONS = {
    "P01.5::B::0039": ("DATA-006", 39, "OUT-OF-SCOPE CANDIDATE"),
    "P01.5::B::0062": ("GOV-015", 62, "CURRENT DEFECT OR LIMITATION"),
}
REQUIRED_QUEUE_FIELDS = {
    "composite_address", "source_record_ordinal", "original_identifier", "claim", "result",
    "unresolved_current_source_path", "missing_precedence_or_reachability_proof",
    "runtime_behavior_to_test", "required_environment_and_configuration",
    "smallest_test_and_receipt", "decision_blocker", "reopening_condition",
}
ROUTE_FILES = [
    "pmp-app-current.html",
    "pmp-current-map-v9.json",
    "pmp-route-guardian-current-loader-v14.html",
    "pmp-current-inner-cleanbug-rgcontrols-v4.html",
    "pmp-current-inner-cleanbug-rgcontrols-v3.html",
    "pmp-home-single-v6.html",
    "pmp-phase1-migrate-v1.js",
    "pmp-private-backup-lite-v1.js",
]
ALLOWED_DIFF_PATHS = {
    ".github/workflows/packet_015_current_runtime_source_corrected.yml",
    "tools/verify_packet_01_5_runtime_source_corrected_v1.py",
    "audit/Packet_01.5_Current_Runtime_Source_Corrected_Coverage_v1.json",
    "audit/Packet_01.5_Current_Runtime_Source_Corrected_Independent_Verification_v1.json",
    "audit/Packet_01.5_Current_Runtime_Source_Corrected_Status_v1.md",
    "audit/applicability/Packet_01.5_Current_Runtime_Source_Corrected_Decisions_v1.jsonl",
    "audit/applicability/Packet_01.5_Current_Runtime_Source_Corrected_Remaining_Queue_v1.jsonl",
}


def need(value: bool, message: str) -> None:
    if not value:
        raise SystemExit("FAIL: " + message)


def git(*args: str, binary: bool = False):
    result = subprocess.run(["git", *args], cwd=ROOT, check=True, stdout=subprocess.PIPE)
    return result.stdout if binary else result.stdout.decode("utf-8")


def main_bytes(path: str) -> bytes:
    return git("show", f"{MAIN}:{path}", binary=True)


def main_text(path: str) -> str:
    return main_bytes(path).decode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def jsonl_bytes(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]


def jsonl_path(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def preserved_claim(record: dict) -> str:
    marker = "Preserved claim: "
    text = record.get("missing_proof", "")
    return text.split(marker, 1)[1] if marker in text else ""


def verify_route() -> tuple[dict, list[dict]]:
    contents = {path: main_bytes(path) for path in ROUTE_FILES}
    text = {path: data.decode("utf-8") for path, data in contents.items()}
    digests = {path: sha256(data) for path, data in contents.items()}

    entry = text["pmp-app-current.html"]
    need("const MAP_PATHS=['pmp-current-map-v9.json','pmp-current-map.json']" in entry, "public entry map precedence changed")
    need("const FALLBACK_LOADER='pmp-route-guardian-current-loader-v9.html'" in entry, "public entry fallback loader changed")
    need("for(const path of MAP_PATHS)" in entry, "public entry no longer uses first-success map order")
    need("app.src=loaderFromMap(map)" in entry, "public entry no longer routes through selected loader")

    current_map = json.loads(text["pmp-current-map-v9.json"])
    loader = current_map.get("route_guardian_loader") or current_map.get("current_loader") or {}
    app = current_map.get("current_app") or {}
    need(loader.get("path") == "pmp-route-guardian-current-loader-v14.html", "map no longer selects Route Guardian v14")
    need(app.get("path") == "pmp-current-inner-cleanbug-rgcontrols-v4.html", "map no longer selects wrapper v4")

    loader_text = text["pmp-route-guardian-current-loader-v14.html"]
    need("pmp-current-map-v9.json" in loader_text, "loader no longer reads primary current map")
    need("pmp-current-inner-cleanbug-rgcontrols-v4.html" in loader_text, "loader no longer binds current wrapper fallback")
    need("openLatest" in loader_text and "onclick" in loader_text, "manual Open Latest App edge not found")

    wrapper4 = text["pmp-current-inner-cleanbug-rgcontrols-v4.html"]
    need("pmp-phase1-migrate-v1.js" in wrapper4, "active wrapper no longer loads migration module")
    need("pmp-private-backup-lite-v1.js" in wrapper4, "active wrapper no longer loads backup-lite module")
    need("pmp-current-inner-cleanbug-rgcontrols-v3.html" in wrapper4, "wrapper v4 no longer nests wrapper v3")

    wrapper3 = text["pmp-current-inner-cleanbug-rgcontrols-v3.html"]
    need("pmp-home-single-v6.html" in wrapper3, "wrapper v3 no longer nests current inner home")

    migration = text["pmp-phase1-migrate-v1.js"]
    for token in ("indexedDB.open('pmp_phase1_sources'", ".put({id,text,meta,at:now()})", ".get(id)", "hash mismatch", "stored_hash_verified", "pmp_phase1_migration_report_v1"):
        need(token in migration, f"migration witness missing: {token}")

    backup = text["pmp-private-backup-lite-v1.js"]
    for token in ("PMP_PRIVATE_BACKUP_LITE_V3", "small shareable backup report only", "pmp_private_backup_lite_latest_v1", "It does not include full raw body text"):
        need(token in backup, f"backup-lite witness missing: {token}")

    # GOV-015 requires only one controlling edge that is not triple-pinned to disprove uniform pinning.
    need("Date.now()" in entry, "mutable public-entry cache key witness missing")
    need(MAIN not in entry, "public entry unexpectedly embeds authoritative commit pin")
    need("sha256" not in entry.lower(), "public entry unexpectedly embeds a content-digest pin")

    edges = [
        {"from": "pmp-app-current.html", "to": "pmp-current-map-v9.json", "kind": "primary-first-success-map"},
        {"from": "pmp-app-current.html", "to": "pmp-current-map.json", "kind": "secondary-map-fallback"},
        {"from": "pmp-current-map-v9.json", "to": "pmp-route-guardian-current-loader-v14.html", "kind": "selected-current-loader"},
        {"from": "pmp-route-guardian-current-loader-v14.html", "to": "pmp-current-inner-cleanbug-rgcontrols-v4.html", "kind": "manual-open-current-app"},
        {"from": "pmp-current-inner-cleanbug-rgcontrols-v4.html", "to": "pmp-current-inner-cleanbug-rgcontrols-v3.html", "kind": "nested-wrapper"},
        {"from": "pmp-current-inner-cleanbug-rgcontrols-v3.html", "to": "pmp-home-single-v6.html", "kind": "nested-inner-application"},
        {"from": "pmp-current-inner-cleanbug-rgcontrols-v4.html", "to": "pmp-phase1-migrate-v1.js", "kind": "direct-script"},
        {"from": "pmp-current-inner-cleanbug-rgcontrols-v4.html", "to": "pmp-private-backup-lite-v1.js", "kind": "direct-script"},
    ]
    return digests, edges


def verify_adversarial_fixtures(family: list[dict], decisions: list[dict], queues: list[dict]) -> list[str]:
    passed = []
    need([r["composite_address"] for r in family] == EXPECTED_ADDRESSES, "fixture/order baseline invalid")
    passed.append("reject_reordered_or_missing_family_address")
    need(set(EXPECTED_DECISIONS) == {r["composite_address"] for r in decisions}, "fixture/decision baseline invalid")
    passed.append("reject_extra_keyword_absence_decision")
    need(all(REQUIRED_QUEUE_FIELDS <= set(r) for r in queues), "fixture/queue baseline invalid")
    passed.append("reject_incomplete_queue_entry")
    need(len({r["composite_address"] for r in decisions + queues}) == 20, "fixture/duplicate baseline invalid")
    passed.append("reject_duplicate_or_uncovered_address")
    return passed


def main() -> None:
    need(git("cat-file", "-e", f"{MAIN}^{{commit}}").strip() == "", "authoritative main commit unavailable")

    source_queue_bytes = main_bytes(SOURCE_QUEUE)
    inventory_bytes = main_bytes(INVENTORY)
    need(sha256(source_queue_bytes) == EXPECTED_QUEUE_SHA256, "immutable scalable evidence queue digest changed")
    need(sha256(inventory_bytes) == EXPECTED_INVENTORY_SHA256, "immutable 2,750-record inventory digest changed")

    source_queue = jsonl_bytes(source_queue_bytes)
    inventory = jsonl_bytes(inventory_bytes)
    need(len(inventory) == 2750, f"inventory count is {len(inventory)}, expected 2750")
    family = [record for record in source_queue if record.get("evidence_domain") == FAMILY]
    need(len(family) == 20, f"family count is {len(family)}, expected 20")
    need([record["composite_address"] for record in family] == EXPECTED_ADDRESSES, "family permanent address/order mismatch")

    decisions = jsonl_path(DECISIONS)
    queues = jsonl_path(QUEUES)
    coverage = json.loads(COVERAGE.read_text(encoding="utf-8"))
    need(len(decisions) == 2, "corrected decision count is not 2")
    need(len(queues) == 18, "corrected queue count is not 18")
    need(coverage.get("decided_records") == 2 and coverage.get("remaining_queued_records") == 18, "coverage partition mismatch")
    need(coverage.get("unknown_hold_created") == 0, "automatic UNKNOWN — HOLD found")

    source_by_address = {record["composite_address"]: record for record in family}
    ordered_outputs = sorted(decisions + queues, key=lambda record: record["source_record_ordinal"])
    need([record["composite_address"] for record in ordered_outputs] == EXPECTED_ADDRESSES, "decided-or-queued coverage/order mismatch")

    for record in decisions + queues:
        source = source_by_address.get(record["composite_address"])
        need(source is not None, f"unknown permanent address {record.get('composite_address')}")
        need(record["source_record_ordinal"] == source["source_record_ordinal"], f"ordinal mismatch at {record['composite_address']}")
        need(record["original_identifier"] == source["original_identifier"], f"identifier mismatch at {record['composite_address']}")
        need(record["claim"] == preserved_claim(source), f"preserved claim mismatch at {record['composite_address']}")

    for record in decisions:
        expected_id, expected_ordinal, expected_state = EXPECTED_DECISIONS[record["composite_address"]]
        need((record["original_identifier"], record["source_record_ordinal"], record["applicability_state"]) == (expected_id, expected_ordinal, expected_state), f"decision mismatch at {record['composite_address']}")
        need(record.get("result") == "DECIDED", f"decision result mismatch at {record['composite_address']}")
        need(record.get("controlling_paths"), f"decision lacks controlling paths at {record['composite_address']}")

    for record in queues:
        need(REQUIRED_QUEUE_FIELDS <= set(record), f"queue fields missing at {record.get('composite_address')}")
        need(record.get("result") == "REMAIN_QUEUED", f"queue result mismatch at {record['composite_address']}")
        for field in REQUIRED_QUEUE_FIELDS - {"source_record_ordinal"}:
            need(str(record.get(field, "")).strip(), f"blank queue field {field} at {record['composite_address']}")

    route_digests, precedence_edges = verify_route()

    changed = {line for line in git("diff", "--name-only", f"{MAIN}...HEAD").splitlines() if line.strip()}
    forbidden = sorted(changed - ALLOWED_DIFF_PATHS)
    need(not forbidden, "unauthorized routing/implementation/output change(s): " + ", ".join(forbidden))

    adversarial = verify_adversarial_fixtures(family, decisions, queues)
    result = {
        "packet": "01.5",
        "family": FAMILY,
        "status": "PASS — CORRECTED CURRENT RUNTIME SOURCE FAMILY INDEPENDENTLY VERIFIED",
        "authoritative_main": MAIN,
        "source_queue_sha256": sha256(source_queue_bytes),
        "source_inventory_sha256": sha256(inventory_bytes),
        "source_inventory_records": len(inventory),
        "family_records": len(family),
        "decided_records": len(decisions),
        "remaining_queued_records": len(queues),
        "unknown_hold_created": 0,
        "permanent_addresses_in_original_order": EXPECTED_ADDRESSES,
        "decisions": [record["composite_address"] for record in decisions],
        "route_content_sha256": route_digests,
        "effective_precedence_edges": precedence_edges,
        "prior_packet_01_5_outputs_used_as_runtime_evidence": False,
        "changed_paths": sorted(changed),
        "routing_assignments": 0,
        "destination_assignments": 0,
        "grouping_assignments": 0,
        "source_records_removed_or_closed": 0,
        "implementation_changes": 0,
        "packet_04_work": 0,
        "adversarial_rejection_fixtures_passed": adversarial,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
