#!/usr/bin/env python3
import runpy
from pathlib import Path

import runtime_source_rules_v2

runpy.run_path(
    str(Path(__file__).resolve().parent / "verify_packet_01_5_runtime_source_v1.py"),
    run_name="__main__",
)
