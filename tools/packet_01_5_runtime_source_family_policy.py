#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

REASONS = {
  "NO_CONCURRENCY_CONTROL_IN_CURRENT_RUNTIME": "The current runtime source corpus contains no lock, mutex, semaphore, compare-and-swap, revision guard, or transactional concurrency mechanism for simultaneous work. The preserved claim is therefore a current implementation limitation.",
  "NO_RECOGNIZED_QUALITY_BASELINE_CONFIG": "The tracked repository has no recognized static-type, lint, or security-baseline configuration selected for implementation artifacts. This directly supports a current tooling limitation.",
  "NO_DEPRECATION_POLICY_WITH_MULTIPLE_WRAPPERS": "The repository contains multiple current and fallback wrapper/loader generations but no tracked deprecation or retirement policy governing their removal. This is a current maintainability limitation.",
  "WALL_CLOCK_ONLY_NO_MONOTONIC_SEQUENCE": "The current runtime uses wall-clock timestamps such as Date.now and ISO dates, but contains no monotonic sequence or trusted ordering mechanism for receipts and approvals. This is a current ordering limitation.",
  "NO_TAMPER_EVIDENT_APPEND_ONLY_LEDGER": "Current runtime receipts are written as mutable browser or object state without a cryptographic hash chain, signature, or append-only enforcement. This is a current evidence-integrity limitation.",
  "CURRENT_MAP_EXPLICITLY_LIMITS_FREEZE_CLAIMS": "The authoritative current map explicitly states that the current route does not prove current-clean or frozen status. The preserved freeze-coverage claim is therefore currently applicable.",
  "AUDIT_RECEIPTS_NOT_UNIFORMLY_TRIPLE_PINNED": "The current audit set includes receipts and status files that do not uniformly carry branch, commit SHA, and content digest together. This is a current provenance limitation.",
  "NO_FROZEN_FIRST_RELEASE_SCOPE": "No tracked current authority artifact freezes a first-release scope and minimum viable safe capability, while the runtime exposes a growing wrapper and support-script surface. This is a current scope-control limitation.",
  "CONTEXT_USES_BROWSER_LOCAL_STORAGE": "The current app chain stores state in browser localStorage. Clearing browser storage can therefore remove locally saved Resident context unless separately restored, making the preserved claim an active conditional risk.",
  "STABLE_DOOR_AND_MAP_HAVE_FALLBACK_PATHS": "The stable door tries a fallback map and an older fallback loader, while the current map also defines fallback application behavior. These paths can mix generations without a complete mixed-version proof, creating an active conditional risk."
}

REOPEN = {
  "NO_CONCURRENCY_CONTROL_IN_CURRENT_RUNTIME": ["A reviewed lock, revision, or transaction mechanism is added.", "Concurrent-work adversarial tests pass.", "The effective runtime source changes."],
  "NO_RECOGNIZED_QUALITY_BASELINE_CONFIG": ["A lint, type, and security baseline is committed and enforced in CI.", "The baseline runs against all implementation artifacts.", "The tracked configuration set changes."],
  "NO_DEPRECATION_POLICY_WITH_MULTIPLE_WRAPPERS": ["A deprecation and wrapper-retirement policy is committed.", "Obsolete wrappers are inventoried and removed safely.", "The current/fallback route changes."],
  "WALL_CLOCK_ONLY_NO_MONOTONIC_SEQUENCE": ["A monotonic event sequence or trusted ordering source is implemented.", "Ordering and replay tests pass.", "Receipt-generation code changes."],
  "NO_TAMPER_EVIDENT_APPEND_ONLY_LEDGER": ["A signed or hash-chained append-only ledger is implemented.", "Mutation and truncation tests are rejected.", "Evidence-storage code changes."],
  "CURRENT_MAP_EXPLICITLY_LIMITS_FREEZE_CLAIMS": ["A verified freeze receipt covers all claimed state.", "The current map removes the limitation after proof.", "The authority boundary changes."],
  "AUDIT_RECEIPTS_NOT_UNIFORMLY_TRIPLE_PINNED": ["All current receipts include branch, commit SHA, and content digest.", "A verifier rejects incomplete provenance.", "Audit-format requirements change."],
  "NO_FROZEN_FIRST_RELEASE_SCOPE": ["A first-release scope and minimum safe capability are frozen.", "Scope-change governance is verified.", "The product authority artifact changes."],
  "CONTEXT_USES_BROWSER_LOCAL_STORAGE": ["Context is durably backed up and restorable.", "Storage-clear recovery tests pass.", "The persistence architecture changes."],
  "STABLE_DOOR_AND_MAP_HAVE_FALLBACK_PATHS": ["Fallbacks are removed or version-compatible proof is added.", "Mixed-version tests pass.", "The stable-door or current-map route changes."]
}

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def claim_from_queue(item: dict[str, Any]) -> str:
    text = item["missing_proof"]
    return text.split("Preserved claim: ",1)[1] if "Preserved claim: " in text else text

def tracked_files(repo: Path) -> list[str]:
    return subprocess.check_output(["git","ls-files"],cwd=repo,text=True).splitlines()

def current_corpus(repo: Path, files: list[str]) -> tuple[str,list[str]]:
    selected=[]; chunks=[]
    for name in files:
        if "/" not in name and (name.startswith("pmp-") or name in {"wrangler.toml","worker.js","cloudflare-worker.js"}) and Path(name).suffix in {".html",".js",".json",".toml"}:
            path=repo/name
            if path.is_file():
                selected.append(name); chunks.append(path.read_text(encoding="utf-8",errors="replace"))
    return "\n".join(chunks),selected

def evaluate(predicate: str, repo: Path, files: list[str], corpus: str) -> tuple[bool,dict[str,Any]]:
    low=corpus.lower()
    if predicate=="NO_CONCURRENCY_CONTROL_IN_CURRENT_RUNTIME":
        markers=["navigator.locks","mutex","semaphore","compare-and-swap","compareandswap","revision guard","transactional lock"]
        return not any(x in low for x in markers),{"absent_markers":markers}
    if predicate=="NO_RECOGNIZED_QUALITY_BASELINE_CONFIG":
        names={Path(x).name.lower() for x in files}; markers={"tsconfig.json","eslint.config.js","eslint.config.mjs",".eslintrc","pyproject.toml","ruff.toml","mypy.ini","bandit.yaml","semgrep.yml"}
        found=sorted(names&markers)
        return not found,{"recognized_configs_found":found}
    if predicate=="NO_DEPRECATION_POLICY_WITH_MULTIPLE_WRAPPERS":
        policy_files=[x for x in files if Path(x).name.lower() in {"deprecation.md","deprecation_policy.md","maintenance.md","wrapper_retirement.md"}]
        wrappers=[x for x in files if Path(x).name.startswith("pmp-current-inner") or "route-guardian-current-loader" in Path(x).name]
        return not policy_files and len(wrappers)>2,{"policy_files":policy_files,"wrapper_count":len(wrappers)}
    if predicate=="WALL_CLOCK_ONLY_NO_MONOTONIC_SEQUENCE":
        wall=("date.now" in low or "new date(" in low); markers=["monotonic","sequence_number","sequence-number","eventsequence","logical clock","lamport"]
        return wall and not any(x in low for x in markers),{"wall_clock_present":wall,"absent_markers":markers}
    if predicate=="NO_TAMPER_EVIDENT_APPEND_ONLY_LEDGER":
        receipt=("receipt" in low or "evidence" in low); markers=["crypto.subtle.digest","hash chain","hash_chain","append-only","digital signature","signed receipt"]
        return receipt and not any(x in low for x in markers),{"receipt_state_present":receipt,"absent_markers":markers}
    if predicate=="CURRENT_MAP_EXPLICITLY_LIMITS_FREEZE_CLAIMS":
        text=(repo/"pmp-current-map-v9.json").read_text(encoding="utf-8")
        return "does not prove" in text and "frozen" in text,{"map_sha256":sha256(text.encode())}
    if predicate=="AUDIT_RECEIPTS_NOT_UNIFORMLY_TRIPLE_PINNED":
        candidates=[x for x in files if x.startswith("audit/") and Path(x).suffix in {".json",".md"}]
        incomplete=[]
        for name in candidates[:500]:
            text=(repo/name).read_text(encoding="utf-8",errors="replace").lower()
            if not ("branch" in text and "commit" in text and "sha256" in text): incomplete.append(name)
        return bool(incomplete),{"audited_files":len(candidates),"incomplete_sample":incomplete[:20],"incomplete_count_at_least":len(incomplete)}
    if predicate=="NO_FROZEN_FIRST_RELEASE_SCOPE":
        authority=[x for x in files if Path(x).suffix in {".md",".json"} and not x.startswith("audit/applicability/")]
        found=[]
        for name in authority[:800]:
            text=(repo/name).read_text(encoding="utf-8",errors="replace").lower()
            if "minimum viable safe capability" in text and "frozen" in text: found.append(name)
        return not found,{"frozen_scope_artifacts":found}
    if predicate=="CONTEXT_USES_BROWSER_LOCAL_STORAGE":
        matches=[name for name in files if name.startswith("pmp-") and Path(name).suffix in {".html",".js"} and "localStorage" in (repo/name).read_text(encoding="utf-8",errors="replace")]
        return bool(matches),{"local_storage_files":matches[:30],"count":len(matches)}
    if predicate=="STABLE_DOOR_AND_MAP_HAVE_FALLBACK_PATHS":
        door=(repo/"pmp-app-current.html").read_text(encoding="utf-8"); current=(repo/"pmp-current-map-v9.json").read_text(encoding="utf-8")
        ok="pmp-current-map.json" in door and "FALLBACK_LOADER" in door and "fallback_app" in current
        return ok,{"door_sha256":sha256(door.encode()),"map_sha256":sha256(current.encode())}
    return False,{"error":"unknown predicate"}
