import subprocess, sys
r = subprocess.run([sys.executable, 'tools/test_diagnostics_owner_refresh_no_navigation_v1.py'], capture_output=True, text=True)
print(r.stdout, end='')
if r.stderr: print(r.stderr, end='')
raise SystemExit(r.returncode)
