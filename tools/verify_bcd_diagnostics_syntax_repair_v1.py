#!/usr/bin/env python3
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
result=subprocess.run(['python3',str(ROOT/'tools/test_bcd_diagnostics_syntax_repair_v1.py')],cwd=ROOT,text=True,capture_output=True)
print(result.stdout,end='')
if result.stderr: print(result.stderr,end='')
raise SystemExit(result.returncode)
