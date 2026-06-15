#!/usr/bin/env python3
import runpy
from pathlib import Path
import dep_platform_common_v2

root = Path(__file__).resolve().parent
runpy.run_path(str(root / 'build_packet_01_5_dependency_platform_v1.py'), run_name='__main__')
runpy.run_path(str(root / 'refine_dep_platform_queues.py'), run_name='__main__')
