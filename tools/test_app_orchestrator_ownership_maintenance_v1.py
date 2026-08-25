#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "pmp-app-orchestrator-ownership-registry-v1.json"

checks = 0


def check(value: object, label: str) -> None:
    global checks
    checks += 1
    assert value, label


def text(path: str) -> str:
    return (ROOT / path).read_text("utf-8")


def validate_registry(data: dict) -> list[str]:
    errors: list[str] = []
    rows = data.get("resources", [])
    ids = [row.get("id") for row in rows]
    if len(ids) != len(set(ids)):
        errors.append("duplicate_resource_id")
    identifiers: dict[str, list[str]] = {}
    for row in rows:
        if not row.get("owner") or not row.get("writer"):
            errors.append("missing_owner_or_writer")
        for identifier in row.get("identifiers", []):
            identifiers.setdefault(identifier, []).append(row["id"])
    for identifier, owners in identifiers.items():
        if len(owners) > 1:
            errors.append("identifier_multi_resource:" + identifier)
    return errors


def main() -> None:
    registry = json.loads(REGISTRY.read_text("utf-8"))
    check(registry["type"] == "PMP_APP_ORCHESTRATOR_OWNERSHIP_REGISTRY_V1", "registry type")
    check(registry["rules"]["one_canonical_writer_per_resource"] is True, "one writer rule")
    check(registry["rules"]["helpers_may_request_but_may_not_commit_owner_state"] is True, "helper request rule")
    check(registry["rules"]["persisted_user_data"] == "preserve_exact_bytes_no_migration", "user data rule")
    check(not validate_registry(registry), "registry validates")
    rows = {row["id"]: row for row in registry["resources"]}
    for resource in (
        "active_path_discovery_canonical_report",
        "active_path_discovery_bounded_support_report",
        "mount_registry",
        "transfer_store_manifest",
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
    check("indexedDB.open" not in legacy, "legacy store no DB open")
    check("localStorage.setItem" not in legacy, "legacy store no canonical write")

    for path, actor, field in (
        ("pmp-source-zip-reader-level2-v1.js", "pmp-source-zip-reader-level2-v1.js", "source_zip_reader_level2"),
        ("pmp-source-zip-extractor-level2b-v1.js", "pmp-source-zip-extractor-level2b-v1.js", "source_zip_extractor_level2b"),
        ("pmp-source-pdf-text-level2c-v1.js", "pmp-source-pdf-text-level2c-v1.js", "source_pdf_text_level2c"),
        ("pmp-source-reference-gate-level4-v1.js", "pmp-source-reference-gate-level4-v1.js", "source_reference_gate_level4"),
    ):
        source = text(path)
        check("commitSourceStage" in source, path + " delegates")
        check(actor in source and field in source, path + " exact binding")

    router = text("pmp-resident-cr-status-router-v1.js")
    check("read_only_delegate" in router, "resident router delegate")
    check("residentRun=" not in router, "resident router no wrapper")
    check("localStorage.setItem" not in router, "resident router no status write")
    check("setInterval(" not in router, "resident router no timer")

    resident = text("pmp-resident-continuous-run-status-reader-v1.js")
    check("setInterval(" not in resident, "resident status owner event driven")
    check("pmpResidentStatusOwnerBound" in resident, "resident status owner binds once")

    source_text = text("pmp-source-text-reader-level3-v1.js")
    check("setInterval(" not in source_text, "source text reader event driven")
    check("pmp:bank-owner-slot-ready" in source_text, "source text reader owner event")

    foundation = text("pmp-owner-diagnostics-foundation-v1.js")
    check("read_only_legacy_summary" in foundation, "foundation read only")
    check("removeItem" not in foundation, "foundation no storage deletion")
    check("querySelector" not in foundation, "foundation no DOM mutation")
    check("pmp_section_owner_registry_snapshot_v1" in foundation, "foundation reads owner snapshot")
    check("pmp_helper_registry_snapshot_v1" in foundation, "foundation reads helper snapshot")
    check("setInterval(" not in foundation, "foundation no timer")

    loader = text("pmp-continuous-run-bank-order-frame-loader-v1.js")
    check("EVENT_DRIVEN_NEW_DOCUMENT_ONCE_SINGLE_OWNER_FRAME" in loader, "single frame mode")
    check("child_frames_injected:0" in loader, "no child stateful injection")
    check("setInterval(" not in loader, "loader no timer")
    check("querySelectorAll('iframe" not in loader, "loader does not traverse frames")
    check(".remove()" not in loader, "loader does not replace scripts")

    for path in (
        "pmp-layout-guard-v1.js",
        "pmp-continuous-run-bank-stable-status-owner-v1.js",
        "pmp-bank-zero-loading-flash-guard-v1.js",
    ):
        source = text(path)
        check("setInterval(" not in source, path + " no recurring repaint")
        check("MutationObserver" not in source, path + " no observer repaint")
        check(".remove()" not in source, path + " no DOM removal")
    safe = text("pmp-safe-area-surface-fill-v1.js")
    check("setInterval(" not in safe, "safe area no timer")
    check("createElement('script')" not in safe, "safe area no loader")
    check("localStorage" not in safe, "safe area no shared receipt collision")
    check("querySelectorAll('iframe" not in safe, "safe area local document only")

    top_loader = text("pmp-top-lossless-loader.js")
    top_injector = text("pmp-top-lossless-injector.js")
    check("setInterval(" not in top_loader, "top lossless loader no poll")
    check("setInterval(" not in top_injector, "top lossless injector no poll")
    check(".remove()" not in top_loader, "top lossless loader never replaces")
    check(".remove()" not in top_injector, "top lossless injector never replaces")
    check("?fresh=" not in top_loader and "?fresh=" not in top_injector, "top lossless stable sources")

    helper_bank = text("pmp-helper-bank-live-inspector-v2.js")
    master_bank = text("pmp-master-bank-tab-v1.js")
    check("setInterval(" not in helper_bank, "helper bank presenter no recurring repaint")
    check("renderInto" in helper_bank, "helper bank explicit owner API")
    check("helper.renderInto(d)" in master_bank, "Bank owner requests helper presentation")

    problem_seeds = text("pmp-helper-problem-type-seeds-v1.js")
    problem_only = text("pmp-helper-problem-type-only-v1.js")
    cleaner = text("pmp-hidden-safe-writer-surface-cleaner-v1.js")
    for path, source in (
        ("pmp-helper-problem-type-seeds-v1.js", problem_seeds),
        ("pmp-helper-problem-type-only-v1.js", problem_only),
        ("pmp-hidden-safe-writer-surface-cleaner-v1.js", cleaner),
    ):
        check("setInterval(" not in source, path + " no recurring action")
        check("localStorage.setItem" not in source, path + " no persisted write")
        check(".remove()" not in source, path + " no DOM removal")
    check("localStorage.setItem=function" not in problem_only, "no Storage monkeypatch")

    source_loader = text("pmp-private-source-loader-v1.js")
    check("setInterval(" not in source_loader, "private source loader event driven")
    check("explicit_private_source_intake" in source_loader, "private source declared role")

    helper_rules = text("pmp-pass8-helper-rules-v1.js")
    check("machine_readable_registry_plus_static_CI_plus_owner_broker" in helper_rules, "helper enforcement named")
    for path in (
        "pmp-top-lossless-injector.js",
        "pmp-helper-bank-live-inspector-v2.js",
        "pmp-helper-problem-type-seeds-v1.js",
        "pmp-hidden-safe-writer-surface-cleaner-v1.js",
        "pmp-private-source-loader-v1.js",
        "pmp-resident-continuous-run-status-reader-v1.js",
        "pmp-source-text-reader-level3-v1.js",
    ):
        check(path in helper_rules, "helper declared " + path)

    page = text("pmp-current-page-code-scope-v1.js")
    adapter = text("pmp-route-code-map-adapter-v1.js")
    check("write(RELOAD" not in page, "page scope no reload write")
    check("wr(RECEIPT" not in adapter, "adapter no reload write")
    check("never extends or rewrites the canonical Reload Current receipt" in page, "page scope rule")
    check("never extends or rewrites the canonical Reload Current receipt" in adapter, "adapter rule")

    diagnostics = text("pmp-diagnostics-owner-v1.js")
    for token in (
        "PMP_DIAGNOSTICS_PANEL_ORDER_REPORT_V2",
        "PMP_DIAGNOSTICS_DUPLICATE_PANEL_REPORT_V2",
        "PMP_DIAGNOSTICS_FLICKER_REPAINT_REPORT_V2",
        "PMP_DIAGNOSTICS_ERROR_BUG_WATCH_REPORT_V2",
        "Copy New Chat Safe Handoff",
        "ensureStyle",
        "pmpDiagQuick",
        "App Health Summary",
        "App Orchestrator Status",
        "Bank / Continuous Run Visual State",
        "result.mode==='clipboard'||result.mode==='copy'",
    ):
        check(token in diagnostics, "diagnostics implements " + token)
    check(
        "pmpDiagSafeHandoffHome" not in diagnostics,
        "Diagnostics home omits the duplicate safe handoff shortcut",
    )
    check(
        diagnostics.count("Copy New Chat Safe Handoff") == 1,
        "one safe handoff action remains inside App Orchestrator Status",
    )
    check(
        "if(id==='app_orchestrator')controls=action('pmpDiagSafeHandoff'" in diagnostics,
        "App Orchestrator Status owns the safe handoff action",
    )
    for removed in (
        "['active_path','Active Path Discovery'",
        "pmpDiagOpenActivePathHome",
        "pmpDiagRunActivePath",
        "pmpDiagCopyActivePath",
        "if(id==='active_path')",
    ):
        check(removed not in diagnostics, "Diagnostics omits duplicate Active Path UI: " + removed)
    check(
        "pmp_active_path_discovery_report_v1" in diagnostics
        and "pmp_active_path_discovery_bounded_report_v2" in diagnostics,
        "Diagnostics report may still read Active Path evidence without presenting a duplicate tool",
    )
    check(
        "position:fixed!important;inset:0!important;z-index:9!important" in diagnostics,
        "Diagnostics is anchored to the visible viewport above app content and below navigation",
    )
    check("el.scrollTop=0" in diagnostics, "Diagnostics opens at its first action")
    check("placeholder" not in diagnostics.lower(), "no diagnostic placeholders")
    orchestrator = text("pmp-app-orchestrator-v1.js")
    check("pmp-diagnostics-bottom-tab-forcer-v1.js" in orchestrator, "orchestrator loads Diagnostics entry")
    check("PMPDiagnosticsBottomTabForcerV1" in orchestrator, "orchestrator binds Diagnostics owner")

    handoff = text("pmp-new-chat-safe-handoff-v1.js")
    check("MAX_COPY_BYTES" in handoff, "handoff bounded copy")
    check("storedZip" in handoff and "crc32" in handoff, "handoff ZIP implementation")
    check("NEW_CHAT_SAFE_HANDOFF.json.sha256" in handoff, "handoff sidecar")
    check("PMP_NEW_CHAT_SAFE_HANDOFF_PACKAGE_MANIFEST_V2" in handoff, "handoff package manifest V2")
    check("persisted user data" in handoff, "handoff excludes data")
    check(
        "app-orchestrator-diagnostics-handoff-active-path-restoration-v1.json"
        in handoff,
        "handoff includes Diagnostics restoration evidence",
    )

    inner30 = text("pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html")
    check(inner30.count("pmp-app-orchestrator-ownership-runtime-v1.js") == 1, "ownership runtime loaded once")
    check(inner30.count("pmp-new-chat-safe-handoff-v1.js") == 1, "handoff loaded once")
    check(inner30.index("pmp-app-orchestrator-ownership-runtime-v1.js") < inner30.index("pmp-app-orchestrator-v1.js"), "ownership runtime precedes orchestrator")
    check(inner30.index("pmp-new-chat-safe-handoff-v1.js") < inner30.index("pmp-app-orchestrator-v1.js"), "handoff precedes orchestrator")

    bad = json.loads(json.dumps(registry))
    bad["resources"].append(dict(bad["resources"][0]))
    check("duplicate_resource_id" in validate_registry(bad), "duplicate resource fault rejected")
    bad = json.loads(json.dumps(registry))
    bad["resources"][1]["identifiers"].append(bad["resources"][0]["identifiers"][0])
    check(any(x.startswith("identifier_multi_resource:") for x in validate_registry(bad)), "identifier collision fault rejected")
    bad = json.loads(json.dumps(registry))
    bad["resources"][0]["writer"] = ""
    check("missing_owner_or_writer" in validate_registry(bad), "missing writer fault rejected")

    print(json.dumps({"status": "PASS", "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
