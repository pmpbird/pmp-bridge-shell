#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = "66ea4021630371fe43010431556f8d56dccdd077"
RECORD = ROOT / "audit/pass13/udl-private-library-integration-gate-v1.json"
INTEGRATION = ROOT / "audit/udl-private-library-integration-20260729.json"
MANIFEST = ROOT / "pmp-runtime-integrity-manifest-v1.json"
SEAL = ROOT / "audit/a003-manifest-seal.json"
BOOTSTRAP = ROOT / "pmp-app-current.html"
LIBRARY = ROOT / "pmp-universal-discovery-library-v1.js"
HOST = ROOT / (
    "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html"
)
ASSERTIONS = 0


def check(value: bool, label: str) -> None:
    global ASSERTIONS
    ASSERTIONS += 1
    assert value, label


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed_paths() -> list[str]:
    committed = subprocess.check_output(
        ["git", "diff", "--name-only", f"{BASE}...HEAD"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    working = subprocess.check_output(
        ["git", "diff", "--name-only", BASE],
        cwd=ROOT,
        text=True,
    ).splitlines()
    untracked = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    return sorted(set(filter(None, committed + working + untracked)))


def main() -> None:
    record = json.loads(RECORD.read_text("utf-8"))
    integration = json.loads(INTEGRATION.read_text("utf-8"))
    manifest = json.loads(MANIFEST.read_text("utf-8"))
    seal = json.loads(SEAL.read_text("utf-8"))
    library = LIBRARY.read_text("utf-8")
    host = HOST.read_text("utf-8")
    bootstrap = BOOTSTRAP.read_text("utf-8")

    actual = changed_paths()
    check(record["unit_id"] == "P13-U10", "bounded unit identity")
    check(record["scope"]["changed_paths"] == actual, "exact changed scope")
    check(
        record["scope"]["implementation_paths"]
        == [
            "pmp-app-current.html",
            "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html",
            "pmp-universal-discovery-library-v1.js",
        ],
        "exact implementation scope",
    )
    gate = record["no_blind_flying_gate"]
    check(gate["automatic_retry"] is False, "no automatic retry")
    check(gate["special_authority"]["consumed"] is False, "no authority consumed")
    check(
        gate["diagnostic_matrix_update"]["status"] == "ADDED",
        "diagnostic matrix bound",
    )

    check(integration["integration"]["placement"] == "LIBRARY", "Library placement")
    check(
        integration["integration"]["private_control_surface_owner"]
        == "LOCAL_MAC_RUNTIME",
        "local Mac owns privileged surface",
    )
    check(
        integration["integration"]["public_backend_privileged"] is False,
        "public backend has no privilege",
    )
    check(
        integration["integration"]["tailscale_funnel_permitted"] is False,
        "Funnel forbidden",
    )
    check("TAILSCALE_SERVE_ONLY" in library, "Serve-only transport")
    check("window.open(PRIVATE_LIBRARY_URL" in library, "private surface opens")
    check("fetch(" not in library, "public entry performs no API mutation")
    check("localStorage" not in library, "public entry stores no durable credential")
    check("Bearer " not in library, "public entry contains no bearer secret")
    check("/api/chat" not in library, "model chat API not exposed")
    check("/api/generate" not in library, "model generation API not exposed")
    check(
        host.count("pmp-universal-discovery-library-v1.js?fresh=") == 1,
        "one private Library entry",
    )

    index = {row["path"]: row for row in manifest["records"]}
    for path in (
        "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html",
        "pmp-universal-discovery-library-v1.js",
    ):
        check(path in index, "protected runtime record " + path)
        check(index[path]["sha256_hex"] == sha(ROOT / path), "runtime hash " + path)
    check(seal["manifest_sha256"] == sha(MANIFEST), "manifest seal")
    match = re.search(r"const MANIFEST_SHA256='([0-9a-f]{64})';", bootstrap)
    check(bool(match), "bootstrap manifest identity")
    check(match.group(1) == seal["manifest_sha256"], "bootstrap seal agreement")
    check(
        seal["runtime_source_set_sha256"]
        == manifest["runtime_source_set_sha256"],
        "runtime source-set identity",
    )
    print(json.dumps({"status": "PASS", "assertions": ASSERTIONS}, sort_keys=True))


if __name__ == "__main__":
    main()
