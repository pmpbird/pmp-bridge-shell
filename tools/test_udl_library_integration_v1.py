#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = "pmp-universal-discovery-library-v1.js"
HOST_PATH = "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html"
PRIVATE_URL = "https://phillips-macbook-air.tail64f36e.ts.net/library"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, evidence: object = None) -> None:
        checks.append({"name": name, "pass": bool(passed), "evidence": evidence})

    script = (ROOT / SCRIPT_PATH).read_text("utf-8")
    host = (ROOT / HOST_PATH).read_text("utf-8")
    manifest = json.loads(
        (ROOT / "pmp-runtime-integrity-manifest-v1.json").read_text("utf-8")
    )
    index = {row["path"]: row for row in manifest.get("records", [])}
    git_paths = set(
        subprocess.check_output(
            ["git", "ls-files"], cwd=ROOT, text=True
        ).splitlines()
    )

    check("Active v30 host loads the Library integration", SCRIPT_PATH in host)
    check("The integration uses the exact private Library URL", PRIVATE_URL in script)
    check(
        "The public integration stores no privileged credential",
        not re.search(
            r"bearer|authorization|api[_-]?key|password|fetch\s*\(|XMLHttpRequest",
            script,
            re.IGNORECASE,
        ),
    )
    check(
        "The integration cannot submit shell or model-API requests",
        "shell" not in script.casefold()
        and "/api/generate" not in script
        and "/api/chat" not in script,
    )
    check(
        "The private surface opens in an isolated tab",
        "'_blank','noopener,noreferrer'" in script,
    )
    check(
        "Nested frames and the Library owner are handled",
        "contentDocument" in script
        and "getElementById('library')" in script
        and "library_section_owner" in script,
    )
    check(
        "Boot retries are bounded and no interval is used",
        "[0,100,300,900,2000,5000,10000]" in script
        and "setInterval" not in script,
    )
    check(
        "The integration is closed by the runtime integrity manifest",
        SCRIPT_PATH in index
        and index.get(SCRIPT_PATH, {}).get("sha256_hex")
        == sha256(ROOT / SCRIPT_PATH)
        and index.get(HOST_PATH, {}).get("sha256_hex") == sha256(ROOT / HOST_PATH),
    )
    check(
        "The pre-existing case-distinct launchers remain preserved",
        {"Index.html", "index.html"}.issubset(git_paths),
    )

    failed = [item for item in checks if not item["pass"]]
    result = {
        "type": "PMP_UNIVERSAL_DISCOVERY_LIBRARY_INTEGRATION_TEST_V1",
        "status": "PASS" if not failed else "FAIL",
        "tests_total": len(checks),
        "tests_passed": len(checks) - len(failed),
        "tests_failed": len(failed),
        "private_url": PRIVATE_URL,
        "checks": checks,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
