#!/usr/bin/env python3
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "2c960a8ea0ffef5e30790fb8b8c42a7c2b6b748b"
REPORT = ROOT / "audit/pass10/pass10-bank-unit7-level-owner-stability-repair-v1.json"
RECEIPT = ROOT / "audit/pass10/receipts/RECEIPT_P10_U7R_BANK_LEVEL_OWNER_STABILITY_REPAIR_20260727T022458Z_001.json"
WORKFLOW = ROOT / ".github/workflows/pass10-unit7-bank-level-owner-stability-repair-v1.yml"
TEST = ROOT / "tools/test_pass10_unit7_bank_level_owner_stability_repair_v1.js"
GENERATOR = ROOT / "tools/generate_pass10_unit7_bank_level_owner_integrity_updates_v1.py"
MANIFEST = ROOT / "pmp-runtime-integrity-manifest-v1.json"
SEAL = ROOT / "audit/a003-manifest-seal.json"
BOOTSTRAP = ROOT / "pmp-app-current.html"
INPUTS = {
    "bank_tab_sha256": ROOT / "pmp-master-bank-tab-v1.js",
    "level_owner_sha256": ROOT / "pmp-continuous-run-level-ui-scope-v1.js",
    "inner_runtime_sha256": ROOT / "pmp-current-inner-cleanbug-rgcontrols-v23.html",
    "runtime_manifest_sha256": MANIFEST,
    "a003_seal_sha256": SEAL,
    "root_anchor_sha256": BOOTSTRAP,
    "test_sha256": TEST,
    "fixture_sha256": ROOT / "tools/fixtures/pass10-unit7-bank-level-owner-stability-v1.html",
}
EXPECTED = {
    ".github/workflows/pass10-unit4-bank-owner-projection-refresh-v1.yml",
    ".github/workflows/pass10-unit7-bank-level-owner-stability-repair-v1.yml",
    "audit/a003-manifest-seal.json",
    "audit/pass10/pass10-bank-unit7-level-owner-stability-repair-v1.json",
    "audit/pass10/receipts/RECEIPT_P10_U7R_BANK_LEVEL_OWNER_STABILITY_REPAIR_20260727T022458Z_001.json",
    "pmp-app-current.html",
    "pmp-continuous-run-level-ui-scope-v1.js",
    "pmp-current-inner-cleanbug-rgcontrols-v23.html",
    "pmp-master-bank-tab-v1.js",
    "pmp-runtime-integrity-manifest-v1.json",
    "tools/fixtures/pass10-unit7-bank-level-owner-stability-v1.html",
    "tools/generate_pass10_unit7_bank_level_owner_integrity_updates_v1.py",
    "tools/test_pass10_unit7_bank_level_owner_stability_repair_v1.js",
    "tools/verify_pass10_unit7_bank_level_owner_stability_repair_v1.py",
}


def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed(base):
    rows = set()
    for command in (
        ("git", "diff", "--name-only", f"{base}...HEAD"),
        ("git", "diff", "--name-only", base),
        ("git", "ls-files", "--others", "--exclude-standard"),
    ):
        rows.update(filter(None, output(*command).splitlines()))
    return rows


def workflow_paths(text):
    match = re.search(r"(?m)^    paths:\n(?P<rows>(?:      - [^\n]+\n)+)", text)
    assert match
    return {
        row.strip()[2:].strip().strip("'\"")
        for row in match.group("rows").splitlines()
    }


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else BASE
    assert base == BASE
    assert changed(base) == EXPECTED, (sorted(changed(base)), sorted(EXPECTED))
    report = json.loads(REPORT.read_text())
    receipt = json.loads(RECEIPT.read_text())
    assert report["base_main_commit"] == BASE
    assert report["substep"] == "P10-U7R"
    assert report["unit_id"] == "P10-U7"
    assert report["status"] == "DETERMINISTIC_REPAIR_GREEN_HANDS_ON_RECHECK_REQUIRED"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == [
        "pmp-app-current.html",
        "pmp-continuous-run-level-ui-scope-v1.js",
        "pmp-current-inner-cleanbug-rgcontrols-v23.html",
        "pmp-master-bank-tab-v1.js",
    ]
    assert report["trigger"]["prior_check_passed"] is False
    assert len(report["trigger"]["observed_failures"]) == 3
    assert report["root_cause"]["classification"] == (
        "SINGLE_OWNER_DOM_ORDER_VIOLATION_AND_SELF_TRIGGERING_REPARENT_LOOP"
    )
    assert report["repair"]["bank_home_level_count_required"] == 0
    assert report["repair"]["recurring_reparent_timer_active"] is False
    assert report["repair"]["noop_reconcile_preserves_dom_identity"] is True
    assert report["repair"]["canonical_order"][:3] == ["1", "2", "3"]
    assert report["repair"]["canonical_order"][-2:] == ["30", "30B"]
    for key, path in INPUTS.items():
        assert report["inputs"][key] == sha(path), key

    test = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"repair \((\d+)/(\d+)\)", test)
    assert match and match.group(1) == match.group(2) == "106"
    for prior, count in (
        ("tools/test_pass9_unit3_bank_continuous_run_owner_integration_v1.js", 234),
        ("tools/test_pass10_unit3_bank_readonly_projection_v1.js", 125),
        ("tools/test_pass10_unit4_bank_owner_projection_refresh_v1.js", 121),
        ("tools/test_pass10_unit7_bank_hands_on_readiness_v1.js", 75),
    ):
        assert f"({count}/{count})" in output("node", prior)
    output("node", "--check", "pmp-master-bank-tab-v1.js")
    output("node", "--check", "pmp-continuous-run-level-ui-scope-v1.js")

    manifest = json.loads(MANIFEST.read_text())
    rows = {row["path"]: row for row in manifest["records"]}
    for path in (
        "pmp-master-bank-tab-v1.js",
        "pmp-continuous-run-level-ui-scope-v1.js",
        "pmp-current-inner-cleanbug-rgcontrols-v23.html",
    ):
        assert rows[path]["sha256_hex"] == sha(ROOT / path)
    seal = json.loads(SEAL.read_text())
    assert seal["manifest_sha256"] == sha(MANIFEST)
    assert seal["runtime_source_set_sha256"] == manifest["runtime_source_set_sha256"]
    assert seal["sealed_branch"] == report["branch"]
    bootstrap = BOOTSTRAP.read_text()
    assert f"const MANIFEST_SHA256='{sha(MANIFEST)}';" in bootstrap

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    assert "actions/upload-artifact@v4" in workflow
    assert "Enforce preserved result after upload" in workflow
    assert workflow.index("Upload complete P10-U7R evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    assert receipt["status"] == report["status"]
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["decisions"]["pass10_complete"] is False
    assert receipt["next_safe_move"]["requires_user_app_check"] is True
    assert report["next_step"]["requires_user_app_check"] is True
    assert report["effects"]["persisted_user_data_changed"] is False
    assert report["effects"]["storage_migration_performed"] is False
    assert report["effects"]["live_app_observation_performed"] is False
    assert report["effects"]["formal_proof_performed"] is False
    assert report["authority"]["formal_proof_authorization_consumed"] is False
    binding = report["no_blind_flying_gate"]
    assert binding["type"] == "PMP_PASS6_PERMANENT_NO_BLIND_FLYING_GATE_BINDING_V1"
    assert binding["ci_lane"] == "static_contract"
    assert binding["diagnostic_matrix_update"]["status"] == "UPDATED"
    assert binding["automatic_retry"] is False
    assert binding["special_authority"]["consumed"] is False
    assert GENERATOR.is_file()
    print(
        "PASS: exact 14-file P10-U7R Bank level-owner stability repair verified "
        "(106/106 + 555/555 prior assertions)"
    )


if __name__ == "__main__":
    main()
