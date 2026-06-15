#!/usr/bin/env python3
from __future__ import annotations

import verify_packet_01_5_runtime_source_corrected_v1 as verifier

verifier.EXPECTED_QUEUE_SHA256 = "1b28dbfd69e9af4b51ce5cf4eb4e43d4ed4aaea107129b2e11b7b41c9dfd861a"
verifier.EXPECTED_INVENTORY_SHA256 = "76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477"
verifier.ALLOWED_DIFF_PATHS.add("tools/run_packet_01_5_runtime_source_corrected_v2.py")

if __name__ == "__main__":
    verifier.main()
