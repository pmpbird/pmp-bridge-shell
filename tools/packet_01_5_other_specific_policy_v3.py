#!/usr/bin/env python3
from packet_01_5_other_specific_policy_v2 import *
import packet_01_5_other_specific_policy as base

_original_included = base.included

def included(path: str) -> bool:
    low = path.lower()
    if "packet_01.5_other_record_specific" in low:
        return False
    return _original_included(path)

base.included = included
