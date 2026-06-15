#!/usr/bin/env python3
from packet_01_5_authoritative_law_policy import *
import packet_01_5_authoritative_law_policy as base

_original_candidate_tier = base.candidate_tier

def candidate_tier(path: str):
    low = path.lower()
    if "authoritative_packet_law" in low or "authoritative-packet-law" in low:
        return None
    return _original_candidate_tier(path)

base.candidate_tier = candidate_tier

def authority_sources(repo, files):
    return base.authority_sources(repo, files)
