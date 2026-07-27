#!/usr/bin/env python3
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "fe41bfd99a7380af018f4a8cdb2e68962e8a6f26"
REPORT = ROOT / "audit/pass10/pass10-bank-unit7-uniform-title-weight-v1.json"
RECEIPT = ROOT / "audit/pass10/receipts/RECEIPT_P10_U7U_UNIFORM_TITLE_WEIGHT_20260727T041526Z_001.json"
WORKFLOW = ROOT / ".github/workflows/pass10-unit7-uniform-title-weight-v1.yml"
HISTORICAL_WORKFLOW = ROOT / ".github/workflows/pass10-unit7-single-card-presentation-v1.yml"
TEST = ROOT / "tools/test_pass10_unit7_uniform_title_weight_v1.js"
FIXTURE = ROOT / "tools/fixtures/pass10-unit7-uniform-title-weight-v1.html"
GENERATOR = ROOT / "tools/generate_pass10_unit7_uniform_title_weight_integrity_updates_v1.py"
MANIFEST = ROOT / "pmp-runtime-integrity-manifest-v1.json"
SEAL = ROOT / "audit/a003-manifest-seal.json"
BOOTSTRAP = ROOT / "pmp-app-current.html"
INPUTS = {
    "bank_owner_sha256": ROOT / "pmp-bank-screen-owner-v1.js",
    "level_owner_sha256": ROOT / "pmp-continuous-run-level-ui-scope-v1.js",
    "inner_runtime_sha256": ROOT / "pmp-current-inner-cleanbug-rgcontrols-v23.html",
    "runtime_manifest_sha256": MANIFEST,
    "a003_seal_sha256": SEAL,
    "root_anchor_sha256": BOOTSTRAP,
    "test_sha256": TEST,
    "fixture_sha256": FIXTURE,
    "prior_presentation_test_sha256": ROOT / "tools/test_pass10_unit7_single_card_presentation_v1.js",
    "prior_alias_test_sha256": ROOT / "tools/test_pass10_unit7_legacy_level_alias_single_stack_repair_v1.js",
    "prior_owner_test_sha256": ROOT / "tools/test_pass10_unit7_bank_level_owner_stability_repair_v1.js",
}
EXPECTED = {
    ".github/workflows/pass10-unit7-single-card-presentation-v1.yml",
    ".github/workflows/pass10-unit7-uniform-title-weight-v1.yml",
    "audit/a003-manifest-seal.json",
    "audit/pass10/pass10-bank-unit7-uniform-title-weight-v1.json",
    "audit/pass10/receipts/RECEIPT_P10_U7U_UNIFORM_TITLE_WEIGHT_20260727T041526Z_001.json",
    "pmp-app-current.html",
    "pmp-bank-screen-owner-v1.js",
    "pmp-current-inner-cleanbug-rgcontrols-v23.html",
    "pmp-runtime-integrity-manifest-v1.json",
    "tools/fixtures/pass10-unit7-uniform-title-weight-v1.html",
    "tools/generate_pass10_unit7_uniform_title_weight_integrity_updates_v1.py",
    "tools/test_pass10_unit7_uniform_title_weight_v1.js",
    "tools/verify_pass10_unit7_uniform_title_weight_v1.py",
}


def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed(base):
    committed = set(
        filter(
            None,
            output("git", "diff", "--name-only", f"{base}...HEAD").splitlines(),
        )
    )
    staged = set(
        filter(None, output("git", "diff", "--cached", "--name-only").splitlines())
    )
    assert "Index.html" not in staged
    rows = set(committed)
    for command in (
        ("git", "diff", "--name-only", base),
        ("git", "ls-files", "--others", "--exclude-standard"),
    ):
        rows.update(filter(None, output(*command).splitlines()))
    if "Index.html" in rows and "Index.html" not in committed:
        rows.remove("Index.html")
    return rows


def workflow_paths(text):
    match = re.search(
        r"(?m)^    paths:\n(?P<rows>(?:      - [^\n]+\n)+)", text
    )
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
    assert report["substep"] == "P10-U7U"
    assert report["unit_id"] == "P10-U7"
    assert report["status"] == (
        "DETERMINISTIC_UNIFORM_TITLE_WEIGHT_GREEN_HANDS_ON_TYPOGRAPHY_RECHECK_REQUIRED"
    )
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == [
        "pmp-app-current.html",
        "pmp-bank-screen-owner-v1.js",
        "pmp-current-inner-cleanbug-rgcontrols-v23.html",
    ]
    assert report["trigger"]["user_confirmed_prior_single_card_repair_worked"] is True
    assert report["trigger"]["user_confirmed_prior_result_liked"] is True
    assert report["trigger"][
        "user_requested_pre_level3_titles_match_level3plus_bold_weight"
    ] is True
    assert report["root_cause"]["classification"] == (
        "INHERITED_PRE_LEVEL3_TITLE_WEIGHT_DIFFERS_FROM_EXPLICIT_LEVEL3PLUS_WEIGHT"
    )
    repair = report["repair"]
    for key in (
        "presentation_only",
        "exact_weight_match",
        "card_nodes_preserved",
        "heading_nodes_preserved",
        "functional_controls_preserved",
        "button_handlers_preserved",
        "level3plus_single_card_presentation_preserved",
        "canonical_order_preserved",
        "locked_waiting_readiness_preserved",
    ):
        assert repair[key] is True, key
    for key in (
        "title_font_size_changed",
        "title_line_height_changed",
        "title_text_changed",
        "card_structure_changed",
        "recurring_owner_timer_active",
    ):
        assert repair[key] is False, key
    assert repair["pre_level3_title_count"] == 6
    assert repair["pre_level3_title_weight_after"] == 950
    assert repair["level3plus_reference_weight"] == 950
    assert repair["canonical_order"] == [
        "1", "2", "3", "4", "4B", "5", "6", "7", "8", "9", "10",
        "11", "12", "13", "14", "15", "16", "17", "18", "19",
        "20", "21", "22", "23", "24", "25", "26", "27", "28",
        "29", "30", "30B",
    ]
    for key, path in INPUTS.items():
        assert report["inputs"][key] == sha(path), key

    test = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"uniform title weight \((\d+)/(\d+)\)", test)
    assert match and match.group(1) == match.group(2) == "86"
    prior_total = 0
    for prior, count in (
        ("tools/test_pass10_unit7_single_card_presentation_v1.js", 478),
        ("tools/test_pass10_unit7_legacy_level_alias_single_stack_repair_v1.js", 151),
        ("tools/test_pass10_unit7_bank_level_owner_stability_repair_v1.js", 106),
        ("tools/test_pass9_unit3_bank_continuous_run_owner_integration_v1.js", 234),
        ("tools/test_pass10_unit3_bank_readonly_projection_v1.js", 125),
        ("tools/test_pass10_unit4_bank_owner_projection_refresh_v1.js", 121),
        ("tools/test_pass10_unit7_bank_hands_on_readiness_v1.js", 75),
    ):
        assert f"({count}/{count})" in output("node", prior)
        prior_total += count
    assert prior_total == 1290
    verification = report["verification"]
    assert verification["assertions_passed"] == 86
    assert verification["browser_fixture_assertions_passed"] == 28
    assert verification["prior_regression_assertions_total"] == 1290
    assert verification["permanent_no_blind_flying_assertions"] == 166
    assert verification["permanent_no_blind_flying_result_sha256"] == (
        "340aa6c3b588fc0eef9e66191b5bb5f12f633d0c0b2af099a20eae597b2943b2"
    )
    assert "PMP_PASS10_UNIT7U_UNIFORM_TITLE_WEIGHT_FIXTURE_V1" in FIXTURE.read_text()
    output("node", "--check", "pmp-bank-screen-owner-v1.js")

    manifest = json.loads(MANIFEST.read_text())
    rows = {row["path"]: row for row in manifest["records"]}
    for path in (
        "pmp-bank-screen-owner-v1.js",
        "pmp-current-inner-cleanbug-rgcontrols-v23.html",
    ):
        assert rows[path]["sha256_hex"] == sha(ROOT / path)
    seal = json.loads(SEAL.read_text())
    assert seal["manifest_sha256"] == sha(MANIFEST)
    assert seal["runtime_source_set_sha256"] == manifest["runtime_source_set_sha256"]
    assert seal["sealed_branch"] == report["branch"]
    assert "P10-U7U applies the exact Level 3+ font weight 950" in seal["pass10_context"]
    bootstrap = BOOTSTRAP.read_text()
    assert f"const MANIFEST_SHA256='{sha(MANIFEST)}';" in bootstrap

    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    assert "actions/upload-artifact@v4" in workflow
    assert "Upload complete P10-U7U evidence" in workflow
    assert "Enforce preserved result after upload" in workflow
    assert workflow.index("Upload complete P10-U7U evidence") < workflow.index(
        "Enforce preserved result after upload"
    )
    historical = HISTORICAL_WORKFLOW.read_text()
    assert "P10-U7T historical exact-scope verifier not applicable" in historical
    assert "478-assertion runtime regression executed" in historical

    assert receipt["status"] == report["status"]
    assert set(receipt["changed_paths"]) == EXPECTED
    assert receipt["assertions"]["uniform_title_weight"] == 86
    assert receipt["assertions"]["browser_fixture"] == 28
    assert receipt["assertions"]["prior_regressions"] == 1290
    assert receipt["assertions"]["permanent_no_blind_flying"] == 166
    assert receipt["decisions"]["pre_level3_title_count"] == 6
    assert receipt["decisions"]["pre_level3_title_weight"] == (
        "EXACT_950_MATCH_TO_LEVEL3PLUS"
    )
    assert receipt["decisions"]["card_and_heading_nodes"] == "PRESERVED"
    assert receipt["decisions"]["pass10_complete"] is False
    assert receipt["next_safe_move"]["step_id"] == (
        "P10-U7B-FINAL-UNIFORM-TITLE-WEIGHT-RECHECK"
    )
    assert receipt["next_safe_move"]["requires_user_app_check"] is True
    assert report["next_step"]["id"] == (
        "P10-U7B-FINAL-UNIFORM-TITLE-WEIGHT-RECHECK"
    )
    assert report["effects"]["functional_runtime_behavior_changed"] is False
    assert report["effects"]["functional_nodes_removed"] is False
    assert report["effects"]["functional_controls_hidden"] is False
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
        "PASS: exact 13-file P10-U7U uniform title weight verified "
        "(86/86 + 28/28 fixture + 1290/1290 prior assertions + "
        "166/166 permanent gate)"
    )


if __name__ == "__main__":
    main()
