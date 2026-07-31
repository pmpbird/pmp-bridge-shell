import json
import subprocess
import sys
from pathlib import Path

result = subprocess.run(
    [sys.executable, 'tools/test_diagnostics_active_view_preservation_v1.py'],
    text=True,
    capture_output=True,
)
receipt = {
    'type': 'PMP_DIAGNOSTICS_ACTIVE_VIEW_PRESERVATION_VERIFICATION_V1',
    'version': '1.0.0',
    'status': 'PASS' if result.returncode == 0 else 'FAIL',
    'command': 'python tools/test_diagnostics_active_view_preservation_v1.py',
    'stdout': result.stdout,
    'stderr': result.stderr,
    'exit_status': result.returncode,
    'scope': ['pmp-diagnostics-consolidated-view-v1.js'],
}
print(json.dumps(receipt, indent=2))
raise SystemExit(result.returncode)
