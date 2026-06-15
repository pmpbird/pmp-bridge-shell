#!/usr/bin/env python3
from dep_platform_common import *
import dep_platform_common as base

_original_allowed = base.allowed
_original_census = base.census

def is_processing_output(name: str) -> bool:
    low = name.lower()
    return 'packet_01.5_' in low or 'packet_01_5_' in low

def allowed(name: str) -> bool:
    if is_processing_output(name):
        return False
    return _original_allowed(name)

def census(repo, names):
    filtered = [name for name in names if not is_processing_output(name)]
    return _original_census(repo, filtered)

base.allowed = allowed
base.census = census
