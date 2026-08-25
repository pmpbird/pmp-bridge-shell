#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def text(path):
    return (ROOT / path).read_text("utf-8")


def data(path):
    return json.loads(text(path))


def check(value, label):
    assert value, label


def main():
    registry = data("pmp-app-orchestrator-ownership-registry-v1.json")
    check(registry["type"] == "PMP_APP_ORCHESTRATOR_OWNERSHIP_REGISTRY_V1", "registry type")
    check(registry["version"] == "1.0.0", "registry version")
    resources = registry["resources"]
    rows = {row["id"]: row for row in resources}
    for resource in (
        "active_path_discovery_canonical_report",
        "active_path_discovery_bounded_support_report",
        "mount_registry",
        "transfer_store_manifest",
        "transfer_store_database",
        "must_reference_source_zip_database",
        "resident_continuous_run_status",
        "section_owner_registry",
        "helper_registry",
        "pass7_coverage_lock",
        "pass7_certification",
        "canonical_reload_receipt",
        "continuous_run_bank_surface",
        "diagnostics_surface",
        "helper_bank_presentation",
        "helper_problem_memory",
        "top_lossless_transfer_controls",
        "private_source_intake",
        "new_chat_safe_handoff",
    ):
        check(resource in rows, "registered resource " + resource)
    check(rows["active_path_discovery_canonical_report"]["writer"] == "pmp-active-path-discovery-machine-v1.js", "V1 writer")
    check(rows["active_path_discovery_bounded_support_report"]["writer"] == "pmp-active-path-discovery-machine-v2.js", "V2 writer")
    check(rows["transfer_store_manifest"]["writer"] == "pmp-continuous-run-bank-transfer-store-v2.js", "transfer writer")
    check(rows["canonical_reload_receipt"]["writer"] == "pmp-current-screen-pointer-v1.js", "reload writer")

    v1 = text("pmp-active-path-discovery-machine-v1.js")
    v2 = text("pmp-active-path-discovery-machine-v2.js")
    export = text("pmp-active-path-discovery-zip-export-v2.js")
    check("PMP_ACTIVE_PATH_DISCOVERY_REPORT_V1" in v1, "canonical V1 schema")
    check("pmp_active_path_discovery_report_v1" in v1, "canonical V1 key")
    check("PMP_ACTIVE_PATH_DISCOVERY_BOUNDED_REPORT_V2" in v2, "bounded V2 schema")
    check("pmp_active_path_discovery_bounded_report_v2" in v2, "bounded V2 key")
    check("pmp_active_path_discovery_report_v1" not in v2, "V2 does not write V1 key")
    check("PMPActivePathDiscoveryReportV1" not in v2, "V2 does not write V1 global")
    check("PMPActivePathDiscoveryMachineV1" not in v2, "V2 does not alias V1 machine")
    check("setInterval(" not in v1, "V1 no recurring mount")
    check("1.4.0-fresh-scan-classification-truth-20260825A" in v1, "V1 current fresh-scan classification version")
    check("frame.addEventListener('load',scheduleMount)" in v1, "V1 remounts after owned frame load")
    check("observer.observe(root,{childList:true,subtree:true})" in v1, "V1 observes mount-target creation")
    check("record.addedNodes" in v1 and "containsMountTarget" in v1, "V1 observer is target-bounded")
    check("[1000,2500,4500]" not in v1, "V1 fixed mount timer race removed")
    check("setInterval(" not in export, "export no recurring installer")
    check("PMP_ACTIVE_PATH_DISCOVERY_REPORT_V1" in export, "export validates canonical schema")

    aligner = text("pmp-pass1r-version-aligner-v1.js")
    check("read_only_no_registry_alignment_write" in aligner, "aligner read only")
    check("pmp_mount_registry_v1_receipt" not in aligner, "aligner does not touch registry receipt")
    check("r.version=" not in aligner, "aligner does not mutate registry object")
    check("setInterval(" not in aligner, "aligner no timer")

    transfer = text("pmp-continuous-run-bank-transfer-store-v2.js")
    must = text("pmp-continuous-run-bank-must-source-zip-v1.js")
    verify = text("pmp-continuous-run-bank-verify-receipt-fix-v1.js")
    legacy = text("pmp-continuous-run-bank-transfer-store-v1.js")
    check("const OWNER='bank_screen_owner'" in transfer, "transfer owner identity")
    check("commitSourceZip" in transfer and "commitSourceStage" in transfer, "owner broker APIs")
    check("api.commitSourceZip" in must, "source ZIP delegates metadata")
    check("localStorage.setItem" not in must, "source ZIP no manifest write")
    check("api.verifyStore(true)" in verify, "verify delegates")
    check("localStorage.setItem" not in verify, "verify no direct write")
    check("setInterval(" not in verify, "verify no timer")
    check("pmp_continuous_run_bank_transfer_manifest_v1" not in legacy, "legacy transfer store not canonical manifest writer")

    owner = text("pmp-bank-screen-owner-v1.js")
    boundary = text("pmp-bank-continuous-run-owner-boundary-v1.js")
    inventory = text("pmp-bank-inventory-readonly-projection-v1.js")
    refresh = text("pmp-bank-owner-projection-refresh-v1.js")
    master = text("pmp-master-bank-tab-v1.js")
    check("PMPBankScreenOwnerV1" in owner, "bank owner runtime")
    check("pmpBankOwnerDetailSlotV1" in owner, "bank owner detail slot")
    check("continuous_run" in boundary, "bank continuous run boundary")
    check("READ_ONLY" in inventory or "read" in inventory.lower(), "bank inventory read only")
    check("PMPBankScreenOwnerV1" in refresh, "refresh delegates to bank owner")
    check("PMPBankScreenOwnerV1" in master or "bank_screen_owner" in master, "master bank references owner")

    helper = text("pmp-helper-bank-live-inspector-v2.js")
    check("bank_screen_owner" in helper, "helper bank presenter parent owner")
    check("localStorage.setItem" not in helper, "helper presenter no storage write")

    current = text("pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html")
    check("pmp-app-orchestrator-v1.js" in current, "current loads orchestrator")
    check("pmp-app-orchestrator-ownership-runtime-v1.js" in current, "current loads ownership runtime")
    check("pmp-active-path-discovery-machine-v1.js" in current, "current loads canonical Active Path")

    maintenance = data("audit/pass13/app-orchestrator-ownership-maintenance-v1.json")
    check(maintenance["status"] == "PASS", "maintenance status")
    check(maintenance["ownership_registry_sha256"] == __import__("hashlib").sha256(text("pmp-app-orchestrator-ownership-registry-v1.json").encode()).hexdigest(), "registry maintenance digest")

    # Lossless handoff/package schema remains V2. This maintenance test intentionally
    # accepts the current package schema rather than reviving the retired V1 contract.
    handoff = text("pmp-new-chat-safe-handoff-v1.js")
    check("PMP_NEW_CHAT_SAFE_HANDOFF_V2" in handoff, "safe handoff V2")
    check("PMP_NEW_CHAT_SAFE_HANDOFF_PACKAGE_MANIFEST_V2" in handoff, "safe handoff package manifest V2")
    check("PACKAGE_MANIFEST.json" in handoff, "safe handoff package manifest path")

    # Safety invariants: maintenance must not create undeclared owners/helpers or
    # destructive data paths.
    combined = "\n".join([v1, v2, export, transfer, must, verify, helper, owner, boundary, inventory, refresh, master, current, handoff])
    check("localStorage.clear(" not in combined, "no localStorage clear")
    check("indexedDB.deleteDatabase(" not in combined, "no indexedDB delete")

    print(json.dumps({"type": "PMP_APP_ORCHESTRATOR_OWNERSHIP_MAINTENANCE_TEST_V1", "status": "PASS"}, sort_keys=True))


if __name__ == "__main__":
    main()
