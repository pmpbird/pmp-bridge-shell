#!/usr/bin/env python3
import runpy
import sys
from pathlib import Path
import packet_01_5_authoritative_law_policy_v3

root = Path(__file__).resolve().parent
mode = sys.argv[1] if len(sys.argv) > 1 else ""
if mode == "build":
    runpy.run_path(str(root / "build_packet_01_5_authoritative_law_family_v1.py"), run_name="__main__")
elif mode == "verify":
    runpy.run_path(str(root / "verify_packet_01_5_authoritative_law_family_v2.py"), run_name="__main__")
else:
    raise SystemExit("usage: run_packet_01_5_authoritative_law_family_v3.py build|verify")
