#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
subprocess.run(['python3','tools/test_deterministic_diagnostics_startup_v1.py'],cwd=ROOT,check=True)
record=json.loads((ROOT/'audit/pass13/pass13-unit12-deterministic-diagnostics-startup-gate-v1.json').read_text())
assert record['status']=='PASS'
assert record['unit_id']=='P13-U12'
assert record['scope']['implementation_paths']==['pmp-app-orchestrator-v1.js']
print('PASS deterministic diagnostics startup verifier')
