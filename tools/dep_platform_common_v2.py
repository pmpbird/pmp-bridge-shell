#!/usr/bin/env python3
from dep_platform_common import *
import dep_platform_common as base

_original_allowed = base.allowed

def allowed(name: str) -> bool:
    low = name.lower()
    if 'packet_01.5_' in low or 'packet_01_5_' in low:
        return False
    return _original_allowed(name)

base.allowed = allowed
