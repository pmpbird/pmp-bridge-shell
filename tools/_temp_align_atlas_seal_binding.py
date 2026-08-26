#!/usr/bin/env python3
from pathlib import Path
import json

NEW_V='1.5.0-served-a003-reference-truth-20260826A'
NEW_R='1.1.0-served-a003-reference-truth-20260826A'
OLD_V='1.4.0-fresh-scan-classification-truth-20260825A'
OLD_R='1.0.0-current-map-http-truth-20260825A'

def replace(path, old, new, expected=None):
    p=Path(path); text=p.read_text('utf-8'); count=text.count(old)
    if expected is not None and count!=expected: raise SystemExit(f'{path}: expected {expected} matches for {old!r}, got {count}')
    if expected is None and count<1: raise SystemExit(f'{path}: missing {old!r}')
    p.write_text(text.replace(old,new),'utf-8')
    return count

# Runtime interface: exporter continues 2.7 ZIP handoff behavior but accepts the repaired canonical scanner identity.
replace('pmp-active-path-discovery-zip-export-v2.js', f"EXPECTED_MACHINE_VERSION='{OLD_V}'", f"EXPECTED_MACHINE_VERSION='{NEW_V}'", 1)
replace('pmp-active-path-discovery-zip-export-v2.js', f"EXPECTED_MACHINE_REVISION='{OLD_R}'", f"EXPECTED_MACHINE_REVISION='{NEW_R}'", 1)

# Current maintenance tests follow the new canonical Atlas identity; historical receipts/gates remain untouched.
replace('tools/test_app_orchestrator_ownership_maintenance_v1.py', OLD_V, NEW_V, 1)
replace('tools/test_active_path_fresh_scan_classification_truth_v1.py', OLD_V, NEW_V)
replace('tools/test_active_path_fresh_scan_classification_truth_v1.py', OLD_R, NEW_R)
replace('tools/test_active_path_fresh_scan_classification_truth_v1.py', "'no_forced_pass': 'freeze_gate:{pass:policy.map_fetch_ok&&hard.length===0' in machine,", "'no_forced_pass': 'freeze_gate:{pass:policy.map_fetch_ok&&integrity.fetch_ok&&!!integrity.manifest_sha256' in machine,", 1)
replace('audit/a002-active-path-fresh-scan-classification-v1.cjs', OLD_V, NEW_V)
replace('audit/a002-active-path-fresh-scan-classification-v1.cjs', OLD_R, NEW_R)
replace('tools/test_active_path_zip_output_handoff_v1.py', OLD_V, NEW_V)
replace('tools/test_active_path_zip_output_handoff_v1.py', OLD_R, NEW_R)
replace('audit/a002-active-path-zip-output-v1.cjs', OLD_V, NEW_V)
replace('audit/a002-active-path-zip-output-v1.cjs', OLD_R, NEW_R)

# Strengthen this repair's own deterministic contract to cover exporter/scanner compatibility.
p=Path('tools/test_active_path_seal_binding_reference_truth_v1.py')
text=p.read_text('utf-8')
old="s = Path(\"pmp-active-path-discovery-machine-v1.js\").read_text(\"utf-8\")\nchecks = {"
new="s = Path(\"pmp-active-path-discovery-machine-v1.js\").read_text(\"utf-8\")\nexporter = Path(\"pmp-active-path-discovery-zip-export-v2.js\").read_text(\"utf-8\")\nchecks = {"
if text.count(old)!=1: raise SystemExit('new deterministic exporter prelude mismatch')
text=text.replace(old,new,1)
old="    \"revision\": \"1.1.0-served-a003-reference-truth-20260826A\" in s,\n"
new=old+"    \"exporter_identity_aligned\": \"EXPECTED_MACHINE_VERSION='1.5.0-served-a003-reference-truth-20260826A'\" in exporter and \"EXPECTED_MACHINE_REVISION='1.1.0-served-a003-reference-truth-20260826A'\" in exporter,\n"
if text.count(old)!=1: raise SystemExit('new deterministic exporter check mismatch')
text=text.replace(old,new,1)
p.write_text(text,'utf-8')

changed_paths=[
  '.github/workflows/a002-active-path-seal-binding-reference-truth.yml',
  'audit/a002-active-path-fresh-scan-classification-v1.cjs',
  'audit/a002-active-path-seal-binding-reference-truth-v1.cjs',
  'audit/a002-active-path-zip-output-v1.cjs',
  'audit/a003-manifest-seal.json',
  'audit/pass13/active-path-seal-binding-reference-truth-gate-v1.json',
  'audit/pass13/receipts/RECEIPT_ACTIVE_PATH_SEAL_BINDING_REFERENCE_TRUTH_20260826A_001.json',
  'pmp-active-path-discovery-machine-v1.js',
  'pmp-active-path-discovery-zip-export-v2.js',
  'pmp-app-current.html',
  'pmp-runtime-integrity-manifest-v1.json',
  'tools/test_active_path_fresh_scan_classification_truth_v1.py',
  'tools/test_active_path_seal_binding_reference_truth_v1.py',
  'tools/test_active_path_zip_output_handoff_v1.py',
  'tools/test_app_orchestrator_ownership_maintenance_v1.py',
  'tools/verify_active_path_seal_binding_reference_truth_v1.py'
]
implementation=['pmp-active-path-discovery-machine-v1.js','pmp-active-path-discovery-zip-export-v2.js','pmp-app-current.html']

gate_path=Path('audit/pass13/active-path-seal-binding-reference-truth-gate-v1.json')
gate=json.loads(gate_path.read_text('utf-8'))
gate['scope']['changed_paths']=changed_paths
gate['scope']['implementation_paths']=implementation
gate['claim_ceiling']='Repairs only Active Path scan integrity identity, reference classification truth, and the exporter compatibility binding required to consume that repaired scanner. It does not change ZIP handoff behavior, owners, helpers, routes, Bank, Continuous Run, storage, or persisted user data.'
gate_path.write_text(json.dumps(gate,indent=2,sort_keys=False)+'\n','utf-8')

verify_path=Path('tools/verify_active_path_seal_binding_reference_truth_v1.py')
v=verify_path.read_text('utf-8')
old='assert gate["scope"]["implementation_paths"] == ["pmp-active-path-discovery-machine-v1.js", "pmp-app-current.html"]'
new='assert gate["scope"]["implementation_paths"] == ["pmp-active-path-discovery-machine-v1.js", "pmp-active-path-discovery-zip-export-v2.js", "pmp-app-current.html"]'
if v.count(old)!=1: raise SystemExit('verifier implementation scope mismatch')
verify_path.write_text(v.replace(old,new,1),'utf-8')

receipt_path=Path('audit/pass13/receipts/RECEIPT_ACTIVE_PATH_SEAL_BINDING_REFERENCE_TRUTH_20260826A_001.json')
receipt=json.loads(receipt_path.read_text('utf-8'))
receipt['repair']['exporter_compatibility_binding']='The existing 2.7 ZIP handoff behavior is unchanged; its exact expected scanner version/revision are aligned to 1.5.0 / 1.1.0 so fresh ZIP export consumes the repaired canonical scanner rather than rejecting it.'
receipt_path.write_text(json.dumps(receipt,indent=2,sort_keys=False)+'\n','utf-8')
print('ALIGN_OK')
