#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import io
import json

import verify_packet_01_5_runtime_source_corrected_v1 as verifier

verifier.EXPECTED_QUEUE_SHA256 = "1b28dbfd69e9af4b51ce5cf4eb4e43d4ed4aaea107129b2e11b7b41c9dfd861a"
verifier.EXPECTED_INVENTORY_SHA256 = "76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477"
verifier.ALLOWED_DIFF_PATHS.add("tools/run_packet_01_5_runtime_source_corrected_v2.py")

if __name__ == "__main__":
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        verifier.main()
    result = json.loads(captured.getvalue())
    print(f"STATUS={result['status']}")
    print(f"MAIN={result['authoritative_main']}")
    print(f"SOURCE_QUEUE_SHA256={result['source_queue_sha256']}")
    print(f"SOURCE_INVENTORY_SHA256={result['source_inventory_sha256']} RECORDS={result['source_inventory_records']}")
    print(f"FAMILY={result['family_records']} DECIDED={result['decided_records']} QUEUED={result['remaining_queued_records']} UNKNOWN_HOLD={result['unknown_hold_created']}")
    print("DECISIONS=" + ",".join(result["decisions"]))
    for path, digest in sorted(result["route_content_sha256"].items()):
        print(f"ROUTE_SHA256 {path} {digest}")
    print("BOUNDARIES=" + json.dumps({
        "prior_outputs_as_evidence": result["prior_packet_01_5_outputs_used_as_runtime_evidence"],
        "routing": result["routing_assignments"],
        "destinations": result["destination_assignments"],
        "grouping": result["grouping_assignments"],
        "closed": result["source_records_removed_or_closed"],
        "implementation": result["implementation_changes"],
        "packet_04": result["packet_04_work"],
    }, sort_keys=True, separators=(",", ":")))
    print("ADVERSARIAL=" + ",".join(result["adversarial_rejection_fixtures_passed"]))
