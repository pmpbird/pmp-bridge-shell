#!/usr/bin/env python3
from packet_01_5_other_specific_policy_v4 import *
import packet_01_5_other_specific_policy as base

_original_evaluate = base.evaluate


def schema_records(records, runtime_records):
    runtime_paths = {item["path"] for item in runtime_records}
    selected = []
    for item in records:
        low = item["path"].lower()
        name = low.rsplit("/", 1)[-1]
        if item["path"] in runtime_paths:
            selected.append(item)
        elif any(term in name for term in ("current", "approved", "status", "receipt", "capability-inventory")):
            selected.append(item)
        elif low.startswith("audit/") and "routing-evidence/" not in low and any(term in name for term in ("current", "completion", "verification", "audit")):
            selected.append(item)
    return selected


def evaluate(predicate, repo, files, records, runtime_text, runtime_records):
    if predicate == "ACTIVE_WORK_THREAD_SCHEMA_MIGRATION_UNRESOLVED":
        return schema_outcome(schema_records(records, runtime_records), ("active work thread",), ("schema", "migration", "version"))
    if predicate == "POINTER_AND_FREEZE_SCHEMAS_UNRESOLVED":
        return schema_outcome(schema_records(records, runtime_records), ("safe-point", "safe point", "last good", "emergency pointer", "freeze record"), ("safe-point", "last good", "emergency pointer", "freeze record", "schema", "owner"))
    return _original_evaluate(predicate, repo, files, records, runtime_text, runtime_records)


base.evaluate = evaluate
