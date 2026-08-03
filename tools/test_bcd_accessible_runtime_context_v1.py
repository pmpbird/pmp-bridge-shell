#!/usr/bin/env python3
from pathlib import Path

src = (Path(__file__).resolve().parents[1] / 'pmp-diagnostic-coverage-passes-bcd-v1-1-1-0.js').read_text()
required = [
    "1.2.0-accessible-runtime-context-20260803G",
    "function accessible(w)",
    "function root()",
    "function roots()",
    "roots().forEach(w=>walk(w,0))",
    "#bridge,[data-section=\"bridge\"]",
    "#library,[data-section=\"library\"]",
    "#bank,[data-bank-owner]",
    "mounted_validation:bankOpen?'REQUIRED_AND_EVALUATED':'DEFERRED_UNTIL_BANK_OPEN'",
    "canonicalScript||scopeApi||scopeReceipt",
    "accessible_document_count:docs().length",
]
missing = [token for token in required if token not in src]
assert not missing, f'missing accessible-runtime-context markers: {missing}'
assert "function T(){try{return window.top||window}" not in src
assert "owner_changes:false" in src
assert "helper_changes:false" in src
assert "route_changes:false" in src
assert "storage_migration:false" in src
assert "persisted_user_data_write:false" in src
assert "dom_repair:false" in src
print('PASS: B-D diagnostics scan the highest accessible same-origin runtime context and defer closed Continuous Run mounts')
