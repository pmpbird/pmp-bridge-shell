import subprocess, sys
r = subprocess.run([sys.executable, 'tools/test_whole_health_single_render_v1.py'], capture_output=True, text=True)
print(r.stdout, end='')
if r.stderr: print(r.stderr, end='')
raise SystemExit(r.returncode)
