#!/usr/bin/env python3
from packet_01_5_authoritative_law_policy_v2 import *
import packet_01_5_authoritative_law_policy as base

_original_reviewed = base.reviewed_predicate
_AMENDMENT = "Packet_03.5_Approved_Existing_Packet_Role_Amendment_v1.json"

def _without_amendment(items):
    return [item for item in items if _AMENDMENT.lower() not in item["path"].lower()]

def reviewed_predicate(predicate, claim, sources, files):
    if predicate in {
        "PACKET_06_5_ONLY_IMPLEMENTATION_CLAIM",
        "PACKET_23_IMPLEMENTATION_ROLE_CLAIM",
        "PACKET_24_EXECUTION_ROLE_CLAIM",
    }:
        support, disproof = base.direct_matches(claim, sources)
        support = _without_amendment(support)
        if predicate == "PACKET_06_5_ONLY_IMPLEMENTATION_CLAIM":
            disproof += base.source_match(sources, _AMENDMENT, ("status\": \"approved", "\"23\"", "actual resident safe change implementation execution"))
        elif predicate == "PACKET_23_IMPLEMENTATION_ROLE_CLAIM":
            disproof += base.source_match(sources, _AMENDMENT, ("\"23\"", "actual resident safe change implementation execution", "assembly plan"))
        else:
            disproof += base.source_match(sources, _AMENDMENT, ("\"24\"", "execution of integration", "acceptance", "runbook"))
        unique = {(item["path"], item["sha256"]): item for item in disproof}
        return base.resolve_lists(support, list(unique.values()), {"explicit_approved_role_clause": _AMENDMENT})
    return _original_reviewed(predicate, claim, sources, files)

base.reviewed_predicate = reviewed_predicate
