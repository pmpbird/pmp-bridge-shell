#!/usr/bin/env python3
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "91072a4f8320c9f5764626c35dd8d5a897c128ba"
REPORT = ROOT / "audit/pass9/pass9-bank-continuous-run-unit6-bounded-observation-decision-v1.json"
RECEIPT = ROOT / "audit/pass9/receipts/RECEIPT_P9_U6_BOUNDED_OBSERVATION_NOT_REQUIRED_20260726T210000Z_001.json"
WORKFLOW = ROOT / ".github/workflows/pass9-unit6-bounded-observation-decision-v1.yml"
RUNNER = ROOT / "tools/run_pass9_unit6_bounded_observation_decision_v1.js"
TEST = ROOT / "tools/test_pass9_unit6_bounded_observation_decision_v1.js"
GATE = ROOT / "tools/run_pass6_unit7_no_blind_flying_gate_v1.py"
INPUTS = {
    "unit3_integration_sha256": ROOT / "audit/pass9/pass9-bank-continuous-run-unit3-owner-integration-v1.json",
    "unit4_proof_sha256": ROOT / "audit/pass9/pass9-bank-continuous-run-unit4-exhaustive-proof-v1.json",
    "unit5_certification_sha256": ROOT / "audit/pass9/pass9-bank-continuous-run-unit5-authority-persisted-data-certification-v1.json",
    "runner_sha256": RUNNER,
    "test_sha256": TEST,
}
EXPECTED = {
    ".github/workflows/pass9-unit6-bounded-observation-decision-v1.yml",
    "audit/pass9/pass9-bank-continuous-run-unit6-bounded-observation-decision-v1.json",
    "audit/pass9/receipts/RECEIPT_P9_U6_BOUNDED_OBSERVATION_NOT_REQUIRED_20260726T210000Z_001.json",
    "tools/run_pass9_unit6_bounded_observation_decision_v1.js",
    "tools/test_pass9_unit6_bounded_observation_decision_v1.js",
    "tools/verify_pass9_unit6_bounded_observation_decision_v1.py",
}

def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def changed(base):
    rows = set()
    for cmd in (("git","diff","--name-only",f"{base}...HEAD"),("git","diff","--name-only",base),("git","ls-files","--others","--exclude-standard")):
        rows.update(filter(None, output(*cmd).splitlines()))
    return rows
def workflow_paths(text):
    match = re.search(r"(?m)^    paths:\n(?P<rows>(?:      - [^\n]+\n)+)", text)
    assert match
    return {row.strip()[2:].strip().strip("'\"") for row in match.group("rows").splitlines()}

def main():
    base = sys.argv[1] if len(sys.argv) > 1 else BASE
    assert base == BASE
    assert changed(base) == EXPECTED
    report, receipt = json.loads(REPORT.read_text()), json.loads(RECEIPT.read_text())
    assert report["base_main_commit"] == BASE
    assert report["status"] == "BOUNDED_OBSERVATION_NOT_REQUIRED"
    assert set(report["scope"]["changed_paths"]) == EXPECTED
    assert report["scope"]["implementation_paths"] == []
    assert set(receipt["changed_paths"]) == EXPECTED
    for key, path in INPUTS.items():
        assert report["inputs"][key] == sha(path), key
    text = output("node", str(TEST.relative_to(ROOT)))
    match = re.search(r"decision \((\d+)/(\d+)\)", text)
    assert match and match.group(1) == match.group(2) == "59"
    assert "(143/143)" in output("node", "tools/test_pass9_unit5_authority_persisted_data_certification_v1.js")
    result = json.loads(output("node", str(RUNNER.relative_to(ROOT))))
    assert result["status"] == report["status"]
    assert result["decision"]["observation_required"] is False
    assert result["decision"]["observation_performed"] is False
    assert result["decision"]["observation_authority_consumed"] is False
    assert result["decision"]["retry_of_consumed_observation_authorized"] is False
    assert result["decision"]["next_step"] == "P9-U7"
    assert result["criteria"]["complete_evidence_units"] == 5
    assert result["criteria"]["cumulative_assertions"] == 979
    assert result["criteria"]["unresolved_verification_failures"] == 0
    assert result["criteria"]["production_repair_complete"] is True
    assert result["criteria"]["exhaustive_behavior_complete"] is True
    assert result["criteria"]["authority_data_certified"] is True
    assert result["criteria"]["new_visual_claim_required_for_pass9_exit"] is False
    assert all(value is False for value in result["effects"].values())
    binding = report["no_blind_flying_gate"]
    assert binding["fault_injection"]["status"] == "COVERED"
    assert len(binding["fault_injection"]["cases"]) == 16
    assert len(binding["required_artifact_roles"]) == 9
    gate = json.loads(output("python3", str(GATE.relative_to(ROOT)), "--base", BASE))
    assert gate["status"] == "PASS", gate
    assert gate["unit_id"] == "P9-U6"
    assert gate["summary"]["runtime_paths"] == 0
    workflow = WORKFLOW.read_text()
    assert workflow_paths(workflow) == EXPECTED
    for token in ("if: always()","actions/upload-artifact@v4","Upload complete P9-U6 evidence","Enforce preserved result after upload","artifact-manifest.json","authority-state.json","exit-status.json","scope.json","retention-days: 90"):
        assert token in workflow
    assert workflow.index("Upload complete P9-U6 evidence") < workflow.index("Enforce preserved result after upload")
    assert workflow.rstrip().endswith('run: test "${{ steps.evaluate.outputs.exit_code }}" = "0"')
    assert all(value is False for value in report["effects"].values())
    assert report["next_step"]["id"] == "P9-U7"
    assert receipt["next_safe_move"]["step_id"] == "P9-U7"
    print("PASS: exact six-file P9-U6 bounded observation decision verified (59/59, gate PASS)")

if __name__ == "__main__":
    main()
