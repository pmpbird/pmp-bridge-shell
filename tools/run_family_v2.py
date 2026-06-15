#!/usr/bin/env python3
import runpy
import sys
from pathlib import Path
import route_scope_v1

root=Path(__file__).resolve().parent
mode=sys.argv[1] if len(sys.argv)>1 else ""
if mode=="build":
    runpy.run_path(str(root/"build_packet_01_5_deployment_live_family_v1.py"),run_name="__main__")
elif mode=="verify":
    runpy.run_path(str(root/"verify_packet_01_5_deployment_live_family_v1.py"),run_name="__main__")
else:
    raise SystemExit("usage: run_family_v2.py build|verify")
