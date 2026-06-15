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
    receipt = {
        "status": result["status"],
        "authoritative_main": result["authoritative_main"],
        "source_queue_sha256": result["source_queue_sha256"],
        "source_inventory_sha256": result["source_inventory_sha256"],
        "source_inventory_records": result["source_inventory_records"],
        "family_records": result["family_records"],
        "decided_records": result["decided_records"],
        "remaining_queued_records": result["remaining_queued_records"],
        "unknown_hold_created": result["unknown_hold_created"],
        "decisions": result["decisions"],
        "route_content_sha256": result["route_content_sha256"],
        "effective_precedence_edges": result["effective_precedence_edges"],
        "prior_packet_01_5_outputs_used_as_runtime_evidence": result["prior_packet_01_5_outputs_used_as_runtime_evidence"],
        "routing_assignments": result["routing_assignments"],
        "destination_assignments": result["destination_assignments"],
        "grouping_assignments": result["grouping_assignments"],
        "source_records_removed_or_closed": result["source_records_removed_or_closed"],
        "implementation_changes": result["implementation_changes"],
        "packet_04_work": result["packet_04_work"],
        "adversarial_rejection_fixtures_passed": result["adversarial_rejection_fixtures_passed"],
    }
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
