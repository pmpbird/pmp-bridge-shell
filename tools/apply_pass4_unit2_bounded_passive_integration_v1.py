#!/usr/bin/env python3
import base64
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INNER = ROOT / "pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html"
MANIFEST = ROOT / "pmp-runtime-integrity-manifest-v1.json"
SEAL = ROOT / "audit/a003-manifest-seal.json"
BOOTSTRAP = ROOT / "pmp-app-current.html"
BRANCH = "agent/pass4-unit2-bounded-passive-strip-integration-v1"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def patch_inner() -> None:
    source = INNER.read_text(encoding="utf-8")
    if "PASS4_UNIT2_BOOT_STATUS_STRIP_BEGIN" not in source:
        badge = '.bootBadge{display:inline-flex;align-items:center;justify-content:center;width:max-content;max-width:100%;background:#acd1fb;border:2px solid #07101c;border-radius:999px;padding:7px 10px;font-size:12px;font-weight:950}'
        css = badge + '#pmpBootStatusStripV1{display:grid;grid-template-columns:auto 1fr;gap:9px;align-items:center;border:2px solid #07101c;border-radius:14px;background:#fff3de;padding:9px 10px;font-size:12px;font-weight:950;pointer-events:none}#pmpBootStatusStripV1 .pmpBootState{border:2px solid #07101c;border-radius:999px;background:#acd1fb;padding:4px 8px;white-space:nowrap}#pmpBootStatusStripV1[data-state="READY_ACKNOWLEDGED"] .pmpBootState{background:#7ee09b}#pmpBootStatusStripV1[data-state="BOOT_SLOW"] .pmpBootState{background:#ffe08a}#pmpBootStatusStripV1[data-state="BOOT_FAILURE"] .pmpBootState{background:#ffb2b2}#pmpBootStatusStripV1 .pmpBootStep{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}'
        assert source.count(badge) == 1
        source = source.replace(badge, css)

        old_markup = '<div class="bootBadge">App Orchestrator</div><h1 class="bootTitle">'
        new_markup = '<div class="bootBadge">App Orchestrator</div><div id="pmpBootStatusStripV1" data-state="BOOTING" role="status" aria-live="polite"><span class="pmpBootState">Booting</span><span class="pmpBootStep">Observing current startup</span></div><h1 class="bootTitle">'
        assert source.count(old_markup) == 1
        source = source.replace(old_markup, new_markup)

        note = "function setNote(s){try{document.getElementById('bootNote').textContent=s}catch(e){}}\n"
        functions = """function setNote(s){try{document.getElementById('bootNote').textContent=s}catch(e){}}
/* PASS4_UNIT2_BOOT_STATUS_STRIP_BEGIN */
function deriveBootStatusStripState(input){input=input&&typeof input==='object'?input:{};if(input.failure===true||input.malformed===true)return{state:'BOOT_FAILURE',label:'Boot failure',step:String(input.detail||'Startup status unavailable')};if(input.acknowledged===true)return{state:'READY_ACKNOWLEDGED',label:'Ready',step:String(input.detail||'App Orchestrator acknowledged')};if(Number(input.elapsed_ms||0)>=3000)return{state:'BOOT_SLOW',label:'Boot slow',step:String(input.detail||'Startup is still working')};return{state:'BOOTING',label:'Booting',step:String(input.detail||'Observing current startup')};}
function renderBootStatusStrip(input){let state=deriveBootStatusStripState(input),strip=document.getElementById('pmpBootStatusStripV1');if(!strip)return state;try{strip.setAttribute('data-state',state.state);let label=strip.querySelector('.pmpBootState'),step=strip.querySelector('.pmpBootStep');if(label)label.textContent=state.label;if(step)step.textContent=state.step}catch(e){}return state}
/* PASS4_UNIT2_BOOT_STATUS_STRIP_END */
"""
        assert source.count(note) == 1
        source = source.replace(note, functions)

        old_failure = "function failClosed(error){routeFailed=true;"
        new_failure = "function failClosed(error){routeFailed=true;renderBootStatusStrip({failure:true,detail:'Current Map chain validation failed'});"
        assert source.count(old_failure) == 1
        source = source.replace(old_failure, new_failure)

        old_ready = "currentLiveReport('boot_start_live_api');setReady('bootRuntime','ready');"
        new_ready = "currentLiveReport('boot_start_live_api');renderBootStatusStrip({acknowledged:true,detail:'App Orchestrator acknowledged current startup'});setReady('bootRuntime','ready');"
        assert source.count(old_ready) == 1
        source = source.replace(old_ready, new_ready)

        old_start = "publishApi();\nasync function initializeChain()"
        new_start = "publishApi();\nrenderBootStatusStrip({elapsed_ms:0,detail:'Observing current v22/v30 startup'});\nsetTimeout(()=>{if(!routeFailed&&!lastOrchestratorReport)renderBootStatusStrip({elapsed_ms:3000,detail:'Startup is still working'})},3000);\nasync function initializeChain()"
        assert source.count(old_start) == 1
        source = source.replace(old_start, new_start)
        INNER.write_text(source, encoding="utf-8")


def update_integrity() -> None:
    runtime = INNER.read_bytes()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    record = next(item for item in manifest["records"] if item["path"] == INNER.name)
    digest = hashlib.sha256(runtime).digest()
    b64 = base64.b64encode(digest).decode("ascii")
    record.update(
        bytes=len(runtime),
        git_blob_sha=blob_sha(runtime),
        sha256_hex=digest.hex(),
        sha256_base64=b64,
        sri="sha256-" + b64,
    )
    manifest_bytes = (json.dumps(manifest, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")
    MANIFEST.write_bytes(manifest_bytes)

    seal = json.loads(SEAL.read_text(encoding="utf-8"))
    seal.update(
        manifest_bytes=len(manifest_bytes),
        manifest_sha256=sha256(manifest_bytes),
        pass4_context="Pass 4 Unit 2 installs the passive Boot Status Strip at the current v30 inner-document boundary and atomically refreshes required runtime integrity identities.",
        sealed_branch=BRANCH,
    )
    SEAL.write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    bootstrap = BOOTSTRAP.read_text(encoding="utf-8")
    replacement = "const MANIFEST_SHA256='" + sha256(manifest_bytes) + "';"
    bootstrap, count = re.subn(r"const MANIFEST_SHA256='[0-9a-f]{64}';", replacement, bootstrap, count=1)
    assert count == 1
    BOOTSTRAP.write_text(bootstrap, encoding="utf-8")


def main() -> None:
    patch_inner()
    update_integrity()
    print("PASS: Pass 4 Unit 2 bounded passive integration and integrity identities applied")


if __name__ == "__main__":
    main()
