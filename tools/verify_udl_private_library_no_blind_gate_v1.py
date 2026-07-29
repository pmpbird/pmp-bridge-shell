#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    result = subprocess.check_output(
        [sys.executable, "tools/test_udl_private_library_no_blind_gate_v1.py"],
        cwd=ROOT,
        text=True,
    )
    value = json.loads(result)
    assert value["status"] == "PASS"
    assert value["assertions"] >= 20
    audit = json.loads(
        (ROOT / "audit/udl-private-library-integration-20260729.json").read_text(
            "utf-8"
        )
    )
    assert audit["status"] == "READY_FOR_DRAFT_REVIEW"
    assert audit["unknown_promoted_to_pass"] is False
    assert (
        audit["validation"]["tailscale_serve_account_enablement"]
        == "BLOCKED_USER_ACTION"
    )
    print("PASS: private Library integration gate verified")


if __name__ == "__main__":
    main()
