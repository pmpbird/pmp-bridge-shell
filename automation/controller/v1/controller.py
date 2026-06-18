#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import copy
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable

CONTROLLER_VERSION = "1.0.0"
RUNTIME_SCHEMA = "pmp.automated-plan.controller-runtime.v1"
DECISION_SCHEMA = "pmp.automated-plan.controller-decision.v1"
TRANSPORT_SCHEMA = "pmp.automated-plan.transport-result.v1"
VERIFIED_SCHEMA = "pmp.automated-plan.verified-result.v1"
RESULT_SCHEMA = "pmp.automated-plan.result.v1"
EVIDENCE_SCHEMA = "pmp.automated-plan.evidence-capsule.v1"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")
FORBIDDEN_PAID_ENV = (
    "OPENAI_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "AZURE_AI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
    "COHERE_API_KEY",
    "MISTRAL_API_KEY",
)


class ControllerError(RuntimeError):
    def __init__(self, reason: str, message: str, *, retryable: bool = False, retry_after_seconds: int | None = None):
        super().__init__(message)
        self.reason = reason
        self.retryable = retryable
        self.retry_after_seconds = retry_after_seconds


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_time(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ControllerError("schema_invalid", f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ControllerError("schema_invalid", f"invalid JSON file: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ControllerError("schema_invalid", f"JSON object required: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, sort_keys=False, ensure_ascii=False) + "\n", encoding="utf-8")
    temp.replace(path)


def safe_rel_path(raw: str) -> Path:
    if not isinstance(raw, str) or not raw or "\\" in raw:
        raise ControllerError("changed_file_outside_allowlist", f"unsafe path: {raw!r}")
    p = Path(raw)
    if p.is_absolute() or any(part in ("", ".", "..") for part in p.parts):
        raise ControllerError("changed_file_outside_allowlist", f"unsafe path: {raw!r}")
    return p


def within(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def ensure_fields(obj: dict[str, Any], fields: Iterable[str], label: str) -> None:
    missing = [field for field in fields if field not in obj]
    if missing:
        raise ControllerError("schema_invalid", f"{label} missing fields: {', '.join(missing)}")


def require_zero_cost(policy: dict[str, Any]) -> None:
    cost = policy.get("cost_policy", {})
    if cost.get("spending_ceiling_usd") != 0:
        raise ControllerError("paid_path_detected", "spending ceiling is not $0")
    for key in ("paid_api_allowed", "paid_fallback_allowed", "automatic_cost_escalation_allowed"):
        if cost.get(key) is not False:
            raise ControllerError("paid_path_detected", f"{key} must remain false")


def reject_paid_environment() -> None:
    present = [name for name in FORBIDDEN_PAID_ENV if os.environ.get(name)]
    if present:
        raise ControllerError("paid_path_detected", "paid-provider credential detected: " + ", ".join(present))


def validate_live_main_sha(value: str) -> str:
    value = (value or "").strip().lower()
    if not SHA_RE.fullmatch(value):
        raise ControllerError("authoritative_main_changed", "a full 40-character live main SHA is required")
    return value


def validate_id(value: str, label: str) -> str:
    if not isinstance(value, str) or not SAFE_ID_RE.fullmatch(value):
        raise ControllerError("schema_invalid", f"unsafe {label}: {value!r}")
    return value


def copy_checkpoint(checkpoint: dict[str, Any]) -> dict[str, Any]:
    ensure_fields(checkpoint, (
        "schema_id", "authoritative_main_at_registration", "last_completed_boundary",
        "last_verified_unit", "next_unit", "checkpoint_sequence", "resume_requires_live_main_reverification"
    ), "checkpoint")
    return copy.deepcopy(checkpoint)


def definition_digest(definition_root: Path, state: dict[str, Any], plan: dict[str, Any], policy: dict[str, Any], contract: dict[str, Any], controller_contract: dict[str, Any]) -> str:
    paths = [
        Path(state["active_plan_path"]),
        Path(state["contract_path"]),
        Path("automation/state/active-plan.json"),
        Path("automation/engine/v1/engine-policy.json"),
        Path("automation/controller/v1/controller-contract.json"),
    ]
    pieces: list[bytes] = []
    for rel in paths:
        path = definition_root / safe_rel_path(rel.as_posix())
        if not within(definition_root, path) or not path.is_file():
            raise ControllerError("schema_invalid", f"definition path missing or unsafe: {rel}")
        pieces.append(rel.as_posix().encode("utf-8") + b"\0" + path.read_bytes())
    return sha256_bytes(b"\n".join(pieces))


def load_bundle(definition_root: Path) -> dict[str, Any]:
    state = load_json(definition_root / "automation/state/active-plan.json")
    policy = load_json(definition_root / "automation/engine/v1/engine-policy.json")
    contract = load_json(definition_root / state.get("contract_path", ""))
    plan = load_json(definition_root / state.get("active_plan_path", ""))
    controller_contract = load_json(definition_root / "automation/controller/v1/controller-contract.json")
    require_zero_cost(policy)
    if state.get("active_plan_id") != plan.get("plan_id") or state.get("active_plan_version") != plan.get("plan_version"):
        raise ControllerError("plan_identity_mismatch", "active state and registered plan do not match")
    if plan.get("backend_policy", {}).get("paid_fallback_allowed") is not False:
        raise ControllerError("paid_path_detected", "plan permits a paid fallback")
    allowed = set(state.get("execution", {}).get("allowed_backends", []))
    expected = {item.get("backend_id") for item in policy.get("execution_backends", [])}
    if allowed != expected or allowed != {"github_models_free", "local_ollama"}:
        raise ControllerError("backend_unavailable", "backend registry mismatch")
    checkpoint = copy_checkpoint(state.get("checkpoint", {}))
    return {
        "state": state,
        "policy": policy,
        "contract": contract,
        "plan": plan,
        "controller_contract": controller_contract,
        "checkpoint": checkpoint,
        "definition_digest": definition_digest(definition_root, state, plan, policy, contract, controller_contract),
    }


def initial_runtime(bundle: dict[str, Any]) -> dict[str, Any]:
    state = bundle["state"]
    checkpoint = copy_checkpoint(bundle["checkpoint"])
    return {
        "type": "PMP_AUTOMATED_PLAN_CONTROLLER_RUNTIME",
        "schema_id": RUNTIME_SCHEMA,
        "controller_version": CONTROLLER_VERSION,
        "plan_id": state["active_plan_id"],
        "plan_version": state["active_plan_version"],
        "definition_digest": bundle["definition_digest"],
        "seed_checkpoint_hash": sha256_json(checkpoint),
        "status": "controller_ready_execution_locked",
        "execution_enabled": bool(state.get("execution_enabled") and bundle["plan"].get("execution_enabled")),
        "selected_backend": state["execution"]["selected_backend"],
        "first_run_supervised_required": True,
        "first_run_completed": False,
        "auto_resume_enabled": False,
        "pinned_main_sha": None,
        "checkpoint": checkpoint,
        "active_request": None,
        "attempts_by_unit": {},
        "verified_overlay": {},
        "pause": {
            "reason": "execution_disabled",
            "message": "Controller is built; execution remains locked.",
            "resume_not_before": None,
            "same_unit_preserved": True,
        },
        "last_event": "controller_initialized",
        "last_result": None,
        "updated_at": now_utc(),
    }


def load_runtime(runtime_root: Path, bundle: dict[str, Any]) -> dict[str, Any]:
    path = runtime_root / "status.json"
    runtime = load_json(path) if path.exists() else initial_runtime(bundle)
    ensure_fields(runtime, (
        "schema_id", "controller_version", "plan_id", "plan_version", "definition_digest",
        "seed_checkpoint_hash", "status", "execution_enabled", "selected_backend",
        "first_run_supervised_required", "first_run_completed", "auto_resume_enabled",
        "pinned_main_sha", "checkpoint", "active_request", "attempts_by_unit",
        "verified_overlay", "pause", "last_event", "last_result", "updated_at"
    ), "runtime status")
    if runtime["schema_id"] != RUNTIME_SCHEMA:
        raise ControllerError("schema_invalid", "runtime schema mismatch")
    if runtime["plan_id"] != bundle["state"]["active_plan_id"] or runtime["plan_version"] != bundle["state"]["active_plan_version"]:
        raise ControllerError("plan_identity_mismatch", "runtime plan identity mismatch")
    if runtime["seed_checkpoint_hash"] != sha256_json(bundle["checkpoint"]):
        raise ControllerError("checkpoint_mismatch", "runtime checkpoint seed no longer matches registration")
    # A definition digest change is allowed only before the first supervised run. Afterwards it must stop.
    if runtime["definition_digest"] != bundle["definition_digest"]:
        if runtime.get("first_run_completed") or runtime.get("pinned_main_sha"):
            raise ControllerError("authoritative_main_changed", "controller definitions changed after execution was pinned")
        runtime["definition_digest"] = bundle["definition_digest"]
    runtime["execution_enabled"] = bool(bundle["state"].get("execution_enabled") and bundle["plan"].get("execution_enabled"))
    runtime["auto_resume_enabled"] = bool(bundle["state"].get("execution", {}).get("auto_resume_enabled", False))
    return runtime


@contextlib.contextmanager
def runtime_lock(runtime_root: Path):
    runtime_root.mkdir(parents=True, exist_ok=True)
    lock = runtime_root / ".controller.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ControllerError("manual_stop_requested", "another controller event owns the runtime lock") from exc
    try:
        os.write(fd, f"pid={os.getpid()} at={now_utc()}\n".encode())
        os.close(fd)
        yield
    finally:
        with contextlib.suppress(FileNotFoundError):
            lock.unlink()


def unit_map(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for unit in plan.get("compiled_units", []):
        if not isinstance(unit, dict):
            raise ControllerError("schema_invalid", "compiled unit must be an object")
        ensure_fields(unit, (
            "unit_id", "objective", "evidence_paths", "output_allowlist", "verification_commands", "next_unit"
        ), "compiled unit")
        uid = validate_id(unit["unit_id"], "unit_id")
        if uid in result:
            raise ControllerError("schema_invalid", f"duplicate unit: {uid}")
        result[uid] = unit
    return result


def selected_unit(bundle: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    units = unit_map(bundle["plan"])
    next_unit = runtime["checkpoint"].get("next_unit")
    if next_unit not in units:
        raise ControllerError("plan_not_compiled", f"next unit {next_unit!r} is not compiled")
    return units[next_unit]


def allowed_backend(bundle: dict[str, Any], backend: str) -> str:
    validate_id(backend, "backend")
    allowed = set(bundle["state"]["execution"]["allowed_backends"])
    if backend not in allowed:
        raise ControllerError("backend_unavailable", f"backend is not allowed: {backend}")
    return backend


def overlay_read(definition_root: Path, runtime_root: Path, runtime: dict[str, Any], rel: str) -> tuple[bytes, str]:
    rel_path = safe_rel_path(rel)
    overlay = runtime.get("verified_overlay", {}).get(rel)
    if overlay:
        stored = runtime_root / safe_rel_path(overlay["runtime_path"])
        if not within(runtime_root, stored) or not stored.is_file():
            raise ControllerError("checkpoint_mismatch", f"verified overlay is missing: {rel}")
        data = stored.read_bytes()
        if sha256_bytes(data) != overlay["sha256"]:
            raise ControllerError("checkpoint_mismatch", f"verified overlay hash changed: {rel}")
        return data, "verified_overlay"
    source = definition_root / rel_path
    if not within(definition_root, source) or not source.is_file():
        raise ControllerError("schema_invalid", f"evidence file missing: {rel}")
    return source.read_bytes(), "authoritative_main"


def build_evidence(definition_root: Path, runtime_root: Path, runtime: dict[str, Any], bundle: dict[str, Any], unit: dict[str, Any], request_id: str) -> dict[str, Any]:
    evidence = []
    total = 0
    cap = int(bundle["controller_contract"].get("limits", {}).get("max_evidence_bytes", 200_000))
    for rel in unit["evidence_paths"]:
        data, source = overlay_read(definition_root, runtime_root, runtime, rel)
        total += len(data)
        if total > cap:
            raise ControllerError("unresolved_ambiguity", "evidence capsule exceeds the configured free-mode cap")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ControllerError("schema_invalid", f"evidence must be UTF-8 text: {rel}") from exc
        evidence.append({"path": rel, "source": source, "sha256": sha256_bytes(data), "content": text})
    return {
        "schema_id": EVIDENCE_SCHEMA,
        "plan_id": runtime["plan_id"],
        "unit_id": unit["unit_id"],
        "request_id": request_id,
        "objective": unit["objective"],
        "evidence": evidence,
        "constraints": {
            "proposal_only": True,
            "repository_write_authority": "none",
            "merge_authority": "none",
            "paid_api_allowed": False,
            "output_allowlist": unit["output_allowlist"],
            "one_work_unit_only": True,
            "result_must_be_json": True,
        },
        "expected_result_schema_id": RESULT_SCHEMA,
        "authority": "request_for_proposal_only",
    }


def make_request_id(runtime: dict[str, Any], unit_id: str, backend: str) -> str:
    seq = int(runtime["checkpoint"].get("checkpoint_sequence", 0))
    attempt = int(runtime.get("attempts_by_unit", {}).get(unit_id, 0)) + 1
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{runtime['plan_id']}-{unit_id}-s{seq}-a{attempt}-{backend}-{stamp}"


def current_pause_allows_resume(runtime: dict[str, Any]) -> bool:
    resume_at = parse_time(runtime.get("pause", {}).get("resume_not_before"))
    return resume_at is None or dt.datetime.now(dt.timezone.utc) >= resume_at


def prepare_event(args: argparse.Namespace) -> int:
    definition_root = args.definition_root.resolve()
    runtime_root = args.runtime_root.resolve()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    live_main_sha = validate_live_main_sha(args.live_main_sha)
    bundle = load_bundle(definition_root)
    reject_paid_environment()
    with runtime_lock(runtime_root):
        runtime = load_runtime(runtime_root, bundle)
        action = args.action
        backend = allowed_backend(bundle, args.backend or runtime["selected_backend"])
        if args.automatic:
            if action != "resume":
                raise ControllerError("manual_stop_requested", "automatic events may only resume")
            if not runtime.get("auto_resume_enabled"):
                raise ControllerError("manual_stop_requested", "automatic resume is not enabled in reviewed state")
            if not runtime.get("first_run_completed"):
                raise ControllerError("manual_stop_requested", "automatic resume cannot perform the first real unit")
        decision: dict[str, Any] = {
            "schema_id": DECISION_SCHEMA,
            "controller_version": CONTROLLER_VERSION,
            "action": action,
            "should_infer": False,
            "reason": None,
            "plan_id": runtime["plan_id"],
            "plan_version": runtime["plan_version"],
            "backend_id": backend,
            "unit_id": runtime["checkpoint"].get("next_unit"),
            "request_id": None,
            "live_main_sha": live_main_sha,
            "definition_digest": bundle["definition_digest"],
            "checkpoint_before": copy.deepcopy(runtime["checkpoint"]),
            "checkpoint_before_hash": sha256_json(runtime["checkpoint"]),
            "runtime_patch": {},
            "created_at": now_utc(),
        }

        if action == "status":
            decision["reason"] = "status_only"
        elif action == "pause":
            decision["reason"] = "manual_stop_requested"
            decision["runtime_patch"] = {
                "status": "paused",
                "pause": {"reason": "manual_stop_requested", "message": "Paused by operator event.", "resume_not_before": None, "same_unit_preserved": True},
                "last_event": "manual_pause",
            }
        elif action == "switch_backend":
            decision["reason"] = "backend_switched_checkpoint_reverification_required"
            decision["runtime_patch"] = {
                "selected_backend": backend,
                "status": "paused" if runtime["execution_enabled"] else "controller_ready_execution_locked",
                "pause": {"reason": "backend_change", "message": "Backend changed; the same checkpoint will be reverified before work.", "resume_not_before": None, "same_unit_preserved": True},
                "last_event": "backend_switched",
            }
        elif action in ("run_one", "resume"):
            if not runtime["execution_enabled"]:
                raise ControllerError("execution_disabled", "execution is still locked in the registered plan and active state")
            if action == "resume" and not current_pause_allows_resume(runtime):
                raise ControllerError("free_limit_reached", "resume time has not arrived", retryable=True)
            if runtime["first_run_supervised_required"] and not runtime["first_run_completed"] and not args.supervised:
                raise ControllerError("manual_stop_requested", "the first real unit requires supervised=true")
            if runtime["pinned_main_sha"] and runtime["pinned_main_sha"] != live_main_sha:
                raise ControllerError("authoritative_main_changed", "live main moved after execution was pinned")
            unit = selected_unit(bundle, runtime)
            max_attempts = int(bundle["controller_contract"].get("limits", {}).get("maximum_automatic_attempts_per_unit", 3))
            prior_attempts = int(runtime.get("attempts_by_unit", {}).get(unit["unit_id"], 0))
            if prior_attempts >= max_attempts and not args.supervised:
                raise ControllerError("manual_stop_requested", "automatic attempt limit reached; supervised review is required")
            request_id = make_request_id(runtime, unit["unit_id"], backend)
            evidence = build_evidence(definition_root, runtime_root, runtime, bundle, unit, request_id)
            request = {
                "schema_id": "pmp.automated-plan.backend-request.v1",
                "controller_version": CONTROLLER_VERSION,
                "backend_id": backend,
                "model_id": bundle["controller_contract"]["backends"][backend].get("default_model"),
                "evidence_capsule": evidence,
                "result_contract": {
                    "schema_id": RESULT_SCHEMA,
                    "required_fields": bundle["contract"]["schema_registry"]["result_envelope"]["required_fields"] + ["proposals"],
                    "allowed_statuses": bundle["contract"]["schema_registry"]["result_envelope"]["allowed_statuses"],
                },
                "created_at": now_utc(),
            }
            write_json(out_dir / "request.json", request)
            decision.update({
                "should_infer": True,
                "reason": "one_verified_unit_ready",
                "unit_id": unit["unit_id"],
                "request_id": request_id,
                "unit": unit,
                "candidate_pinned_main_sha": runtime["pinned_main_sha"] or live_main_sha,
            })
        else:
            raise ControllerError("schema_invalid", f"unsupported action: {action}")

        write_json(out_dir / "decision.json", decision)
        write_json(out_dir / "runtime-before.json", runtime)
        print(json.dumps({"result": "PASS", "phase": "prepare", "action": action, "should_infer": decision["should_infer"], "reason": decision["reason"], "unit_id": decision["unit_id"]}, indent=2))
        return 0


def transport_result(status: str, *, backend_id: str, request_id: str, content: str | None = None, usage: dict[str, Any] | None = None, error: str | None = None, retry_after_seconds: int | None = None, http_status: int | None = None) -> dict[str, Any]:
    return {
        "schema_id": TRANSPORT_SCHEMA,
        "backend_id": backend_id,
        "request_id": request_id,
        "status": status,
        "content": content,
        "usage": usage or {},
        "error": error,
        "retry_after_seconds": retry_after_seconds,
        "http_status": http_status,
        "finished_at": now_utc(),
    }


def parse_retry_after(headers: Any) -> int | None:
    raw = headers.get("Retry-After") if headers else None
    if raw and str(raw).isdigit():
        return max(1, int(raw))
    reset = headers.get("X-RateLimit-Reset") if headers else None
    if reset and str(reset).isdigit():
        return max(1, int(reset) - int(time.time()))
    return None


def post_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int) -> tuple[dict[str, Any], Any]:
    request = urllib.request.Request(url, data=canonical_bytes(payload), headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read()
        return json.loads(body.decode("utf-8")), response.headers


def infer_event(args: argparse.Namespace) -> int:
    request = load_json(args.request.resolve())
    ensure_fields(request, ("schema_id", "backend_id", "evidence_capsule", "result_contract"), "backend request")
    backend = request["backend_id"]
    request_id = request["evidence_capsule"]["request_id"]
    reject_paid_environment()
    try:
        if backend == "github_models_free":
            token = os.environ.get("GITHUB_TOKEN")
            if not token:
                raise ControllerError("backend_unavailable", "GITHUB_TOKEN is required for Hosted Free")
            model = os.environ.get("PMP_GITHUB_MODEL") or request.get("model_id") or "openai/gpt-4o-mini"
            prompt = json.dumps({"evidence_capsule": request["evidence_capsule"], "result_contract": request["result_contract"]}, ensure_ascii=False)
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "Return one JSON object only. You are proposal-only. Never claim repository write or merge authority. Obey the output allowlist exactly."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0,
                "max_tokens": int(os.environ.get("PMP_MAX_OUTPUT_TOKENS", "3000")),
                "response_format": {"type": "json_object"},
                "stream": False,
            }
            data, _headers = post_json(
                "https://models.github.ai/inference/chat/completions",
                payload,
                {
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {token}",
                    "X-GitHub-Api-Version": "2026-03-10",
                    "Content-Type": "application/json",
                    "User-Agent": "pmp-automated-plan-controller/1.0",
                },
                timeout=120,
            )
            content = data["choices"][0]["message"]["content"]
            result = transport_result("ok", backend_id=backend, request_id=request_id, content=content, usage=data.get("usage", {}), http_status=200)
        elif backend == "local_ollama":
            endpoint = os.environ.get("PMP_OLLAMA_ENDPOINT", "http://127.0.0.1:11434/api/chat")
            parsed = urllib.parse.urlparse(endpoint)
            if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
                raise ControllerError("paid_path_detected", "Ollama endpoint must be local loopback HTTP")
            model = os.environ.get("PMP_OLLAMA_MODEL")
            if not model:
                raise ControllerError("backend_unavailable", "PMP_OLLAMA_MODEL is required on the laptop runner")
            payload = {
                "model": model,
                "stream": False,
                "format": "json",
                "messages": [
                    {"role": "system", "content": "Return one JSON object only. Proposal-only. No repository write or merge authority."},
                    {"role": "user", "content": json.dumps({"evidence_capsule": request["evidence_capsule"], "result_contract": request["result_contract"]}, ensure_ascii=False)},
                ],
                "options": {"temperature": 0},
            }
            data, _headers = post_json(endpoint, payload, {"Content-Type": "application/json"}, timeout=300)
            content = data["message"]["content"]
            result = transport_result("ok", backend_id=backend, request_id=request_id, content=content, usage=data.get("eval_count") and {"output_tokens_or_units": data.get("eval_count"), "input_tokens_or_units": data.get("prompt_eval_count", 0)} or {}, http_status=200)
        else:
            raise ControllerError("backend_unavailable", f"unsupported backend: {backend}")
    except urllib.error.HTTPError as exc:
        retry = parse_retry_after(exc.headers)
        body = exc.read(4096).decode("utf-8", "replace")
        if exc.code == 429:
            result = transport_result("rate_limited", backend_id=backend, request_id=request_id, error=body or str(exc), retry_after_seconds=retry or 3600, http_status=exc.code)
        elif 500 <= exc.code < 600:
            result = transport_result("transient_error", backend_id=backend, request_id=request_id, error=body or str(exc), retry_after_seconds=retry or 900, http_status=exc.code)
        else:
            result = transport_result("blocked", backend_id=backend, request_id=request_id, error=body or str(exc), http_status=exc.code)
    except (urllib.error.URLError, TimeoutError) as exc:
        result = transport_result("transient_error", backend_id=backend, request_id=request_id, error=str(exc), retry_after_seconds=900)
    except (ControllerError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        reason = exc.reason if isinstance(exc, ControllerError) else "backend_unavailable"
        result = transport_result("blocked", backend_id=backend, request_id=request_id, error=f"{reason}: {exc}")
    write_json(args.out.resolve(), result)
    print(json.dumps({"result": "PASS", "phase": "infer", "backend": backend, "transport_status": result["status"]}, indent=2))
    return 0


def path_allowed(path: str, allowlist: list[str]) -> bool:
    safe_rel_path(path)
    for item in allowlist:
        item = item.rstrip("/")
        safe_rel_path(item)
        if path == item or path.startswith(item + "/"):
            return True
    return False


def validate_model_result(content: str, decision: dict[str, Any], transport: dict[str, Any]) -> dict[str, Any]:
    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ControllerError("schema_invalid", f"model response is not JSON: {exc}") from exc
    if not isinstance(result, dict):
        raise ControllerError("schema_invalid", "model response must be a JSON object")
    required = (
        "schema_id", "plan_id", "unit_id", "request_id", "backend_id", "status", "proposal_only",
        "output_paths", "evidence_used", "usage", "verification_claims", "proposals"
    )
    ensure_fields(result, required, "model result")
    expected = {
        "schema_id": RESULT_SCHEMA,
        "plan_id": decision["plan_id"],
        "unit_id": decision["unit_id"],
        "request_id": decision["request_id"],
        "backend_id": decision["backend_id"],
    }
    for key, value in expected.items():
        if result.get(key) != value:
            raise ControllerError("schema_invalid", f"model result {key} mismatch")
    if result["proposal_only"] is not True or result["status"] not in {"proposed", "needs_more_evidence", "blocked", "failed"}:
        raise ControllerError("unsafe_permission_detected", "model result widened authority or used an invalid status")
    proposals = result["proposals"]
    if not isinstance(proposals, list):
        raise ControllerError("schema_invalid", "proposals must be an array")
    seen: set[str] = set()
    allowlist = decision["unit"]["output_allowlist"]
    normalized = []
    for item in proposals:
        if not isinstance(item, dict):
            raise ControllerError("schema_invalid", "proposal entry must be an object")
        ensure_fields(item, ("path", "content"), "proposal")
        path = item["path"]
        if path in seen or not path_allowed(path, allowlist):
            raise ControllerError("changed_file_outside_allowlist", f"proposal path is duplicate or outside allowlist: {path}")
        if not isinstance(item["content"], str):
            raise ControllerError("schema_invalid", f"proposal content must be text: {path}")
        seen.add(path)
        normalized.append({"path": path, "content": item["content"]})
    if sorted(result["output_paths"]) != sorted(seen):
        raise ControllerError("schema_invalid", "output_paths must exactly match proposal paths")
    result["proposals"] = normalized
    result["usage"] = transport.get("usage", {})
    return result


def materialize_workspace(definition_root: Path, runtime_root: Path, runtime: dict[str, Any], destination: Path) -> None:
    def ignore(directory: str, names: list[str]) -> set[str]:
        ignored = {".git", "node_modules", "__pycache__"}
        if Path(directory).resolve() == definition_root.resolve():
            ignored.add("automation-runtime")
        return ignored.intersection(names)
    shutil.copytree(definition_root, destination, dirs_exist_ok=True, ignore=ignore)
    for target, overlay in runtime.get("verified_overlay", {}).items():
        src = runtime_root / safe_rel_path(overlay["runtime_path"])
        dest = destination / safe_rel_path(target)
        if not within(destination, dest):
            raise ControllerError("changed_file_outside_allowlist", f"unsafe overlay target: {target}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)


def run_verification_commands(workspace: Path, commands: list[Any], timeout_seconds: int) -> list[dict[str, Any]]:
    records = []
    for index, command in enumerate(commands):
        if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
            raise ControllerError("schema_invalid", f"verification command {index} must be a nonempty argv array")
        executable = command[0]
        if executable not in {"python3", "node", "bash", "sh", "git"}:
            raise ControllerError("unsafe_permission_detected", f"verification executable not allowed: {executable}")
        started = time.monotonic()
        proc = subprocess.run(command, cwd=workspace, text=True, capture_output=True, timeout=timeout_seconds, env={
            "PATH": os.environ.get("PATH", ""),
            "HOME": tempfile.gettempdir(),
            "CI": "true",
            "PMP_VERIFICATION_SANDBOX": "1",
        })
        record = {
            "argv": command,
            "exit_code": proc.returncode,
            "stdout_sha256": sha256_bytes(proc.stdout.encode()),
            "stderr_sha256": sha256_bytes(proc.stderr.encode()),
            "elapsed_ms": int((time.monotonic() - started) * 1000),
        }
        records.append(record)
        if proc.returncode != 0:
            raise ControllerError("deterministic_verification_failed", f"verification command failed: {command!r}")
    return records


def tree_snapshot(workspace: Path) -> dict[str, str]:
    ignored_parts = {".git", "node_modules", "__pycache__", ".pytest_cache"}
    snapshot: dict[str, str] = {}
    for path in workspace.rglob("*"):
        if not path.is_file() or any(part in ignored_parts for part in path.relative_to(workspace).parts):
            continue
        rel = path.relative_to(workspace).as_posix()
        snapshot[rel] = sha256_bytes(path.read_bytes())
    return snapshot


def validate_changed_files(before: dict[str, str], after: dict[str, str], allowlist: list[str], artifact_allowlist: list[str] | None = None) -> list[str]:
    artifact_allowlist = artifact_allowlist or []
    changed = sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))
    allowed = allowlist + artifact_allowlist
    outside = [path for path in changed if not path_allowed(path, allowed)]
    if outside:
        raise ControllerError("changed_file_outside_allowlist", "verification changed files outside allowlist: " + ", ".join(outside[:10]))
    return changed


def workspace_hashes(workspace: Path, paths: list[str]) -> dict[str, str]:
    hashes = {}
    for rel in sorted(paths):
        path = workspace / safe_rel_path(rel)
        if not within(workspace, path) or not path.is_file():
            raise ControllerError("deterministic_verification_failed", f"verified output missing: {rel}")
        hashes[rel] = sha256_bytes(path.read_bytes())
    return hashes


def write_proposal_bundle(out_dir: Path, result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    manifest: dict[str, dict[str, Any]] = {}
    proposal_root = out_dir / "proposals"
    for item in result["proposals"]:
        rel = safe_rel_path(item["path"])
        stored_rel = Path("proposals") / rel
        dest = out_dir / stored_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = item["content"].encode("utf-8")
        dest.write_bytes(data)
        manifest[item["path"]] = {"bundle_path": stored_rel.as_posix(), "sha256": sha256_bytes(data), "size_bytes": len(data)}
    return manifest


def pause_verified(decision: dict[str, Any], runtime: dict[str, Any], transport: dict[str, Any]) -> dict[str, Any]:
    retry = int(transport.get("retry_after_seconds") or 900)
    resume_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=max(60, retry))
    reason = "free_limit_reached" if transport["status"] == "rate_limited" else "backend_unavailable"
    candidate = copy.deepcopy(runtime)
    candidate.update({
        "status": "paused",
        "active_request": None,
        "pause": {"reason": reason, "message": transport.get("error") or transport["status"], "resume_not_before": resume_at.replace(microsecond=0).isoformat().replace("+00:00", "Z"), "same_unit_preserved": True},
        "last_event": "safe_pause",
        "last_result": {"request_id": decision["request_id"], "unit_id": decision["unit_id"], "backend_id": decision["backend_id"], "status": transport["status"], "verified": False},
        "updated_at": now_utc(),
    })
    return candidate


def verify_event(args: argparse.Namespace) -> int:
    definition_root = args.definition_root.resolve()
    runtime_root = args.runtime_root.resolve()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    live_main_sha = validate_live_main_sha(args.live_main_sha)
    bundle = load_bundle(definition_root)
    runtime = load_runtime(runtime_root, bundle)
    decision = load_json(args.decision.resolve())
    transport = load_json(args.transport.resolve()) if args.transport else None
    if decision.get("schema_id") != DECISION_SCHEMA:
        raise ControllerError("schema_invalid", "decision schema mismatch")
    if decision["live_main_sha"] != live_main_sha:
        raise ControllerError("authoritative_main_changed", "main moved between prepare and verify")
    if decision["checkpoint_before_hash"] != sha256_json(runtime["checkpoint"]):
        raise ControllerError("checkpoint_mismatch", "checkpoint moved between prepare and verify")

    if not decision["should_infer"]:
        candidate = copy.deepcopy(runtime)
        candidate.update(decision.get("runtime_patch", {}))
        candidate["updated_at"] = now_utc()
        verified = {
            "schema_id": VERIFIED_SCHEMA,
            "kind": "state_only",
            "decision_sha256": sha256_json(decision),
            "transport_sha256": None,
            "runtime_before_sha256": sha256_json(runtime),
            "runtime_candidate": candidate,
            "proposal_manifest": {},
            "verification": {"passed": True, "commands": [], "output_hashes": {}},
            "live_main_sha": live_main_sha,
            "created_at": now_utc(),
        }
    else:
        if not transport or transport.get("schema_id") != TRANSPORT_SCHEMA:
            raise ControllerError("schema_invalid", "transport result missing or invalid")
        if transport.get("request_id") != decision["request_id"] or transport.get("backend_id") != decision["backend_id"]:
            raise ControllerError("schema_invalid", "transport identity mismatch")
        attempts = copy.deepcopy(runtime.get("attempts_by_unit", {}))
        attempts[decision["unit_id"]] = int(attempts.get(decision["unit_id"], 0)) + 1
        runtime["attempts_by_unit"] = attempts
        if transport["status"] in {"rate_limited", "transient_error"}:
            candidate = pause_verified(decision, runtime, transport)
            verified = {
                "schema_id": VERIFIED_SCHEMA,
                "kind": "safe_pause",
                "decision_sha256": sha256_json(decision),
                "transport_sha256": sha256_json(transport),
                "runtime_before_sha256": sha256_json(load_runtime(runtime_root, bundle)),
                "runtime_candidate": candidate,
                "proposal_manifest": {},
                "verification": {"passed": True, "commands": [], "output_hashes": {}, "same_unit_preserved": True},
                "live_main_sha": live_main_sha,
                "created_at": now_utc(),
            }
        elif transport["status"] != "ok":
            raise ControllerError("backend_unavailable", transport.get("error") or "backend blocked the request")
        else:
            result = validate_model_result(transport.get("content") or "", decision, transport)
            if result["status"] != "proposed":
                raise ControllerError("unresolved_ambiguity", f"model did not produce a complete proposal: {result['status']}")
            manifest = write_proposal_bundle(out_dir, result)
            timeout_seconds = int(bundle["controller_contract"].get("limits", {}).get("verification_command_timeout_seconds", 120))
            with tempfile.TemporaryDirectory(prefix="pmp-verify-a-") as a_dir, tempfile.TemporaryDirectory(prefix="pmp-verify-b-") as b_dir:
                wa, wb = Path(a_dir), Path(b_dir)
                materialize_workspace(definition_root, runtime_root, runtime, wa)
                materialize_workspace(definition_root, runtime_root, runtime, wb)
                before_a = tree_snapshot(wa)
                before_b = tree_snapshot(wb)
                for item in result["proposals"]:
                    for workspace in (wa, wb):
                        dest = workspace / safe_rel_path(item["path"])
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        dest.write_text(item["content"], encoding="utf-8")
                commands_a = run_verification_commands(wa, decision["unit"]["verification_commands"], timeout_seconds)
                commands_b = run_verification_commands(wb, decision["unit"]["verification_commands"], timeout_seconds)
                after_a = tree_snapshot(wa)
                after_b = tree_snapshot(wb)
                changed_a = validate_changed_files(before_a, after_a, decision["unit"]["output_allowlist"], decision["unit"].get("verification_artifact_allowlist", []))
                changed_b = validate_changed_files(before_b, after_b, decision["unit"]["output_allowlist"], decision["unit"].get("verification_artifact_allowlist", []))
                if changed_a != changed_b:
                    raise ControllerError("independent_rebuild_mismatch", "independent verification changed-file sets disagree")
                hashes_a = workspace_hashes(wa, result["output_paths"])
                hashes_b = workspace_hashes(wb, result["output_paths"])
                if hashes_a != hashes_b:
                    raise ControllerError("independent_rebuild_mismatch", "independent verification workspaces disagree")
            checkpoint = copy.deepcopy(runtime["checkpoint"])
            checkpoint["last_completed_boundary"] = decision["unit_id"]
            checkpoint["last_verified_unit"] = decision["unit_id"]
            checkpoint["next_unit"] = decision["unit"].get("next_unit")
            checkpoint["checkpoint_sequence"] = int(checkpoint.get("checkpoint_sequence", 0)) + 1
            candidate = copy.deepcopy(runtime)
            candidate.update({
                "status": "complete" if checkpoint["next_unit"] is None else "ready",
                "selected_backend": decision["backend_id"],
                "first_run_completed": True,
                "pinned_main_sha": decision.get("candidate_pinned_main_sha") or runtime.get("pinned_main_sha"),
                "checkpoint": checkpoint,
                "active_request": None,
                "attempts_by_unit": attempts,
                "pause": {"reason": None, "message": None, "resume_not_before": None, "same_unit_preserved": True},
                "last_event": "unit_verified",
                "last_result": {"request_id": decision["request_id"], "unit_id": decision["unit_id"], "backend_id": decision["backend_id"], "status": "proposed", "verified": True, "proposal_count": len(manifest)},
                "updated_at": now_utc(),
            })
            verified = {
                "schema_id": VERIFIED_SCHEMA,
                "kind": "verified_unit",
                "decision_sha256": sha256_json(decision),
                "transport_sha256": sha256_json(transport),
                "runtime_before_sha256": sha256_json(load_runtime(runtime_root, bundle)),
                "runtime_candidate": candidate,
                "proposal_manifest": manifest,
                "verification": {"passed": True, "commands_first": commands_a, "commands_second": commands_b, "changed_files": changed_a, "output_hashes": hashes_a, "independent_rebuild_match": True},
                "live_main_sha": live_main_sha,
                "created_at": now_utc(),
            }
            write_json(out_dir / "model-result.json", result)
    write_json(out_dir / "verified.json", verified)
    print(json.dumps({"result": "PASS", "phase": "verify", "kind": verified["kind"], "checkpoint_next": verified["runtime_candidate"]["checkpoint"].get("next_unit")}, indent=2))
    return 0


def copy_verified_proposals(verified_dir: Path, runtime_root: Path, verified: dict[str, Any]) -> dict[str, dict[str, Any]]:
    last_result = verified["runtime_candidate"].get("last_result") or {}
    request_id = last_result.get("request_id")
    overlay = copy.deepcopy(verified["runtime_candidate"].get("verified_overlay", {}))
    if not request_id:
        return overlay
    validate_id(request_id, "request_id")
    for target, meta in verified.get("proposal_manifest", {}).items():
        src = verified_dir / safe_rel_path(meta["bundle_path"])
        if not within(verified_dir, src) or not src.is_file():
            raise ControllerError("deterministic_verification_failed", f"verified proposal missing: {target}")
        data = src.read_bytes()
        if sha256_bytes(data) != meta["sha256"]:
            raise ControllerError("deterministic_verification_failed", f"verified proposal hash changed: {target}")
        runtime_rel = Path("proposals") / request_id / safe_rel_path(target)
        dest = runtime_root / runtime_rel
        if not within(runtime_root, dest):
            raise ControllerError("changed_file_outside_allowlist", f"unsafe runtime proposal path: {target}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        overlay[target] = {"runtime_path": runtime_rel.as_posix(), "sha256": meta["sha256"], "request_id": request_id}
    return overlay


def append_usage(runtime_root: Path, candidate: dict[str, Any], verified: dict[str, Any]) -> None:
    path = runtime_root / "usage-events.jsonl"
    last_result = candidate.get("last_result") or {}
    event = {
        "at": now_utc(),
        "plan_id": candidate["plan_id"],
        "unit_id": last_result.get("unit_id"),
        "backend_id": last_result.get("backend_id"),
        "request_id": last_result.get("request_id"),
        "status": last_result.get("status"),
        "verified": last_result.get("verified"),
        "checkpoint_sequence": candidate["checkpoint"].get("checkpoint_sequence"),
        "kind": verified["kind"],
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def persist_event(args: argparse.Namespace) -> int:
    definition_root = args.definition_root.resolve()
    runtime_root = args.runtime_root.resolve()
    verified_path = args.verified.resolve()
    live_main_sha = validate_live_main_sha(args.live_main_sha)
    bundle = load_bundle(definition_root)
    reject_paid_environment()
    verified = load_json(verified_path)
    if verified.get("schema_id") != VERIFIED_SCHEMA or verified.get("verification", {}).get("passed") is not True:
        raise ControllerError("deterministic_verification_failed", "verified bundle is not approved")
    if verified.get("live_main_sha") != live_main_sha:
        raise ControllerError("authoritative_main_changed", "main moved before persistence")
    with runtime_lock(runtime_root):
        runtime = load_runtime(runtime_root, bundle)
        if verified["runtime_before_sha256"] != sha256_json(runtime):
            raise ControllerError("checkpoint_mismatch", "runtime moved before persistence")
        candidate = verified["runtime_candidate"]
        if candidate["plan_id"] != runtime["plan_id"] or candidate["plan_version"] != runtime["plan_version"]:
            raise ControllerError("plan_identity_mismatch", "candidate runtime identity mismatch")
        candidate["verified_overlay"] = copy_verified_proposals(verified_path.parent, runtime_root, verified)
        candidate["updated_at"] = now_utc()
        write_json(runtime_root / "status.json", candidate)
        append_usage(runtime_root, candidate, verified)
    print(json.dumps({"result": "PASS", "phase": "persist", "status": candidate["status"], "next_unit": candidate["checkpoint"].get("next_unit"), "runtime_write_root": "automation/runtime"}, indent=2))
    return 0


def status_event(args: argparse.Namespace) -> int:
    bundle = load_bundle(args.definition_root.resolve())
    runtime = load_runtime(args.runtime_root.resolve(), bundle)
    print(json.dumps(runtime, indent=2))
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="PMP Automated Plan event-driven controller")
    sub = p.add_subparsers(dest="command", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--definition-root", type=Path, required=True)
    common.add_argument("--runtime-root", type=Path, required=True)
    common.add_argument("--live-main-sha", required=True)

    prepare = sub.add_parser("prepare", parents=[common])
    prepare.add_argument("--action", choices=("status", "run_one", "resume", "pause", "switch_backend"), required=True)
    prepare.add_argument("--backend", choices=("github_models_free", "local_ollama"), default=None)
    prepare.add_argument("--supervised", action="store_true")
    prepare.add_argument("--automatic", action="store_true")
    prepare.add_argument("--out-dir", type=Path, required=True)
    prepare.set_defaults(func=prepare_event)

    infer = sub.add_parser("infer")
    infer.add_argument("--request", type=Path, required=True)
    infer.add_argument("--out", type=Path, required=True)
    infer.set_defaults(func=infer_event)

    verify = sub.add_parser("verify", parents=[common])
    verify.add_argument("--decision", type=Path, required=True)
    verify.add_argument("--transport", type=Path)
    verify.add_argument("--out-dir", type=Path, required=True)
    verify.set_defaults(func=verify_event)

    persist = sub.add_parser("persist", parents=[common])
    persist.add_argument("--verified", type=Path, required=True)
    persist.set_defaults(func=persist_event)

    status = sub.add_parser("status")
    status.add_argument("--definition-root", type=Path, required=True)
    status.add_argument("--runtime-root", type=Path, required=True)
    status.set_defaults(func=status_event)
    return p


def main() -> int:
    args = parser().parse_args()
    try:
        return args.func(args)
    except ControllerError as exc:
        payload = {
            "result": "STOP",
            "reason": exc.reason,
            "message": str(exc),
            "retryable": exc.retryable,
            "retry_after_seconds": exc.retry_after_seconds,
        }
        print(json.dumps(payload, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
