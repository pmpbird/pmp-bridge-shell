#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import sys

UNIT = pathlib.Path(__file__).resolve().parents[1] / "p2c-post-failure-static-preflight-001"
sys.path.insert(0, str(UNIT))
from static_preflight_modes_001 import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
