import subprocess, sys

result = subprocess.run([sys.executable, 'tools/test_diagnostics_writer_trace_v1.py'], capture_output=True, text=True)
print(result.stdout, end='')
if result.stderr:
    print(result.stderr, end='')
raise SystemExit(result.returncode)
