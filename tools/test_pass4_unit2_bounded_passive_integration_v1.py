#!/usr/bin/env python3
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INNER = ROOT / "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html"
MANIFEST = ROOT / "pmp-runtime-integrity-manifest-v1.json"
BOOTSTRAP = ROOT / "pmp-app-current.html"
AUDIT = ROOT / "audit/pass4/pass4-boot-status-strip-unit2-bounded-passive-integration-v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def extract_function(source: str, name: str) -> str:
    start = source.index("function " + name + "(")
    brace = source.index("{", start)
    depth = 0
    for index in range(brace, len(source)):
        depth += (source[index] == "{") - (source[index] == "}")
        if depth == 0:
            return source[start:index + 1]
    raise AssertionError(name)


def main() -> None:
    source = INNER.read_text(encoding="utf-8")
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert audit["unit"] == 2
    assert audit["preservation"]["unit3_started"] is False
    assert 'id="pmpBootStatusStripV1"' in source
    assert "PASS4_UNIT2_BOOT_STATUS_STRIP_BEGIN" in source

    block = source[source.index("/* PASS4_UNIT2_BOOT_STATUS_STRIP_BEGIN */"):source.index("/* PASS4_UNIT2_BOOT_STATUS_STRIP_END */")]
    for forbidden in ["localStorage", "sessionStorage", "indexedDB", "location.href", "location.assign", "location.replace", "frame.src", "setTimeout"]:
        assert forbidden not in block, forbidden

    function_source = extract_function(source, "deriveBootStatusStripState")
    node = (
        'const vm=require("vm");const c={};vm.createContext(c);vm.runInContext('
        + json.dumps(function_source)
        + ',c);const cases=[[{elapsed_ms:0},"BOOTING"],[{elapsed_ms:3000},"BOOT_SLOW"],'
          '[{failure:true},"BOOT_FAILURE"],[{malformed:true},"BOOT_FAILURE"],'
          '[{acknowledged:true},"READY_ACKNOWLEDGED"]];'
          'for(const [x,w] of cases){const g=c.deriveBootStatusStripState(x);'
          'if(g.state!==w)throw new Error(w+" got "+g.state)};'
          'console.log("PASS: five passive state cases");'
    )
    with tempfile.NamedTemporaryFile("w", suffix=".cjs", delete=False) as handle:
        handle.write(node)
        node_path = handle.name
    subprocess.check_call(["node", node_path])

    record = next(item for item in manifest["records"] if item["path"] == INNER.name)
    assert record["bytes"] == INNER.stat().st_size
    assert record["sha256_hex"] == sha256(INNER)
    assert record["git_blob_sha"] == blob_sha(INNER)
    sealed = re.search(r"const MANIFEST_SHA256='([0-9a-f]{64})';", BOOTSTRAP.read_text(encoding="utf-8")).group(1)
    assert sealed == sha256(MANIFEST)
    assert audit["zero_side_effects"] == {
        "route_assignments_by_strip": 0,
        "persisted_user_data_writes_by_strip": 0,
        "app_orchestrator_ownership_transfers": 0,
        "startup_repairs_or_delays": 0,
    }
    print("PASS: bounded passive strip integration and integrity chain verified")


if __name__ == "__main__":
    main()
