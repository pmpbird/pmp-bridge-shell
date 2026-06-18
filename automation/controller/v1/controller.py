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

CONTROLLER_VERSION = "1.1.0"
RUNTIME_SCHEMA = "pmp.automated-plan.controller-runtime.v1"
DECISION_SCHEMA = "pmp.automated-plan.controller-decision.v1"
TRANSPORT_SCHEMA = "pmp.automated-plan.transport-result.v1"
VERIFIED_SCHEMA = "pmp.automated-plan.verified-result.v2"
RESULT_SCHEMA = "pmp.automated-plan.result.v1"
EVIDENCE_SCHEMA = "pmp.automated-plan.evidence-capsule.v1"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")
FORBIDDEN_PAID_ENV = (
    "OPENAI_API_KEY", "AZURE_OPENAI_API_KEY", "AZURE_AI_API_KEY",
    "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY",
    "COHERE_API_KEY", "MISTRAL_API_KEY",
)
RECEIPT_KEYS = {
    "schema_id", "kind", "decision_sha256", "transport_sha256",
    "runtime_before_sha256", "live_main_sha", "proposal_manifest",
    "verification", "transition_evidence", "created_at",
}


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
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ControllerError("schema_invalid", f"invalid timestamp: {value}") from exc


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
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp.replace(path)


def ensure_fields(obj: dict[str, Any], fields: Iterable[str], label: str) -> None:
    missing = [name for name in fields if name not in obj]
    if missing:
        raise ControllerError("schema_invalid", f"{label} missing fields: {', '.join(missing)}")


def ensure_exact_keys(obj: dict[str, Any], allowed: set[str], label: str) -> None:
    extras = sorted(set(obj) - allowed)
    if extras:
        raise ControllerError("artifact_tampering_detected", f"{label} contains unexpected fields: {', '.join(extras)}")


def safe_rel_path(raw: str) -> Path:
    if not isinstance(raw, str) or not raw or "\\" in raw:
        raise ControllerError("changed_file_outside_allowlist", f"unsafe path: {raw!r}")
    path = Path(raw)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise ControllerError("changed_file_outside_allowlist", f"unsafe path: {raw!r}")
    return path


def within(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def validate_id(value: str, label: str) -> str:
    if not isinstance(value, str) or not SAFE_ID_RE.fullmatch(value):
        raise ControllerError("schema_invalid", f"unsafe {label}: {value!r}")
    return value


def validate_live_main_sha(value: str) -> str:
    value = (value or "").strip().lower()
    if not SHA_RE.fullmatch(value):
        raise ControllerError("authoritative_main_changed", "a full 40-character live main SHA is required")
    return value


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


def hosted_billing_attestation(contract: dict[str, Any]) -> dict[str, Any]:
    expected_scope = contract["backends"]["github_models_free"]["required_billing_scope"]
    disabled = os.environ.get("PMP_GITHUB_MODELS_PAID_USAGE_DISABLED", "").strip().lower() == "true"
    scope = os.environ.get("PMP_GITHUB_MODELS_BILLING_SCOPE", "").strip()
    verified_at_raw = os.environ.get("PMP_GITHUB_MODELS_BILLING_VERIFIED_AT", "").strip()
    try:
        verified_at = parse_time(verified_at_raw) if verified_at_raw else None
    except (TypeError, ValueError, ControllerError):
        verified_at = None
    max_age_days = int(contract.get("billing_gate", {}).get("maximum_attestation_age_days", 31))
    now = dt.datetime.now(dt.timezone.utc)
    age = (now - verified_at) if verified_at and verified_at.tzinfo else None
    fresh = bool(age is not None and dt.timedelta(minutes=-5) <= age <= dt.timedelta(days=max_age_days))
    verified = disabled and scope == expected_scope and fresh
    return {
        "status": "verified" if verified else "unverified",
        "account_level_paid_usage_disabled": disabled,
        "scope": scope or None,
        "verified_at": verified_at_raw or None,
        "maximum_age_days": max_age_days,
        "fresh": fresh,
    }


def require_hosted_billing_gate(contract: dict[str, Any]) -> dict[str, Any]:
    attestation = hosted_billing_attestation(contract)
    if attestation["status"] != "verified":
        raise ControllerError(
            "paid_usage_setting_unverified",
            "Hosted inference is blocked until account-level GitHub Models paid usage is disabled and freshly attested",
        )
    return attestation


def copy_checkpoint(checkpoint: dict[str, Any]) -> dict[str, Any]:
    ensure_fields(checkpoint, (
        "schema_id", "authoritative_main_at_registration", "last_completed_boundary",
        "last_verified_unit", "next_unit", "checkpoint_sequence",
        "resume_requires_live_main_reverification",
    ), "checkpoint")
    return copy.deepcopy(checkpoint)


def definition_digest(definition_root: Path, state: dict[str, Any]) -> str:
    paths = [
        Path(state["active_plan_path"]), Path(state["contract_path"]),
        Path("automation/state/active-plan.json"),
        Path("automation/engine/v1/engine-policy.json"),
        Path("automation/controller/v1/controller-contract.json"),
    ]
    pieces: list[bytes] = []
    for rel in paths:
        path = definition_root / safe_rel_path(rel.as_posix())
        if not within(definition_root, path) or not path.is_file():
            raise ControllerError("schema_invalid", f"definition path missing or unsafe: {rel}")
        pieces.append(rel.as_posix().encode() + b"\0" + path.read_bytes())
    return sha256_bytes(b"\n".join(pieces))


def load_bundle(definition_root: Path) -> dict[str, Any]:
    state = load_json(definition_root / "automation/state/active-plan.json")
    policy = load_json(definition_root / "automation/engine/v1/engine-policy.json")
    contract = load_json(definition_root / state["contract_path"])
    plan = load_json(definition_root / state["active_plan_path"])
    controller_contract = load_json(definition_root / "automation/controller/v1/controller-contract.json")
    require_zero_cost(policy)
    if state.get("active_plan_id") != plan.get("plan_id") or state.get("active_plan_version") != plan.get("plan_version"):
        raise ControllerError("plan_identity_mismatch", "active state and registered plan do not match")
    if plan.get("backend_policy", {}).get("paid_fallback_allowed") is not False:
        raise ControllerError("paid_path_detected", "plan permits a paid fallback")
    allowed = set(state.get("execution", {}).get("allowed_backends", []))
    if allowed != {"github_models_free", "local_ollama"}:
        raise ControllerError("backend_unavailable", "backend registry mismatch")
    return {
        "state": state, "policy": policy, "contract": contract, "plan": plan,
        "controller_contract": controller_contract,
        "checkpoint": copy_checkpoint(state["checkpoint"]),
        "definition_digest": definition_digest(definition_root, state),
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
        "billing_gate": {"status": "unverified", "account_level_paid_usage_disabled": False, "scope": None, "verified_at": None},
        "pause": {"reason": "execution_disabled", "message": "Controller is built; execution remains locked.", "resume_not_before": None, "same_unit_preserved": True},
        "last_event": "controller_initialized",
        "last_result": None,
        "updated_at": "1970-01-01T00:00:00Z",
    }


def load_runtime(runtime_root: Path, bundle: dict[str, Any]) -> dict[str, Any]:
    path = runtime_root / "status.json"
    runtime = load_json(path) if path.exists() else initial_runtime(bundle)
    ensure_fields(runtime, (
        "schema_id", "controller_version", "plan_id", "plan_version", "definition_digest",
        "seed_checkpoint_hash", "status", "execution_enabled", "selected_backend",
        "first_run_supervised_required", "first_run_completed", "auto_resume_enabled",
        "pinned_main_sha", "checkpoint", "active_request", "attempts_by_unit",
        "verified_overlay", "billing_gate", "pause", "last_event", "last_result", "updated_at",
    ), "runtime status")
    if runtime["schema_id"] != RUNTIME_SCHEMA:
        raise ControllerError("schema_invalid", "runtime schema mismatch")
    if runtime["plan_id"] != bundle["state"]["active_plan_id"] or runtime["plan_version"] != bundle["state"]["active_plan_version"]:
        raise ControllerError("plan_identity_mismatch", "runtime plan identity mismatch")
    if runtime["seed_checkpoint_hash"] != sha256_json(bundle["checkpoint"]):
        raise ControllerError("checkpoint_mismatch", "runtime checkpoint seed no longer matches registration")
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
    units: dict[str, dict[str, Any]] = {}
    for unit in plan.get("compiled_units", []):
        ensure_fields(unit, ("unit_id", "objective", "evidence_paths", "output_allowlist", "verification_commands", "next_unit"), "compiled unit")
        uid = validate_id(unit["unit_id"], "unit_id")
        if uid in units:
            raise ControllerError("schema_invalid", f"duplicate unit: {uid}")
        units[uid] = unit
    return units


def selected_unit(bundle: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    units = unit_map(bundle["plan"])
    next_unit = runtime["checkpoint"].get("next_unit")
    if next_unit not in units:
        raise ControllerError("plan_not_compiled", f"next unit {next_unit!r} is not compiled")
    return units[next_unit]


def allowed_backend(bundle: dict[str, Any], backend: str) -> str:
    validate_id(backend, "backend")
    if backend not in set(bundle["state"]["execution"]["allowed_backends"]):
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
    cap = int(bundle["controller_contract"]["limits"]["max_evidence_bytes"])
    for rel in unit["evidence_paths"]:
        data, source = overlay_read(definition_root, runtime_root, runtime, rel)
        total += len(data)
        if total > cap:
            raise ControllerError("unresolved_ambiguity", "evidence capsule exceeds the configured free-mode cap")
        try:
            content = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ControllerError("schema_invalid", f"evidence must be UTF-8 text: {rel}") from exc
        evidence.append({"path": rel, "source": source, "sha256": sha256_bytes(data), "content": content})
    return {
        "schema_id": EVIDENCE_SCHEMA,
        "plan_id": runtime["plan_id"], "unit_id": unit["unit_id"], "request_id": request_id,
        "objective": unit["objective"], "evidence": evidence,
        "constraints": {
            "proposal_only": True, "repository_write_authority": "none", "merge_authority": "none",
            "paid_api_allowed": False, "output_allowlist": unit["output_allowlist"],
            "one_work_unit_only": True, "result_must_be_json": True,
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
    definition_root, runtime_root, out_dir = args.definition_root.resolve(), args.runtime_root.resolve(), args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    live_main_sha = validate_live_main_sha(args.live_main_sha)
    bundle = load_bundle(definition_root)
    reject_paid_environment()
    with runtime_lock(runtime_root):
        runtime = load_runtime(runtime_root, bundle)
        action = args.action
        backend = allowed_backend(bundle, args.backend or runtime["selected_backend"])
        if args.automatic:
            if action != "resume" or not runtime.get("auto_resume_enabled") or not runtime.get("first_run_completed"):
                raise ControllerError("manual_stop_requested", "automatic events may only resume after the supervised first run")
        decision: dict[str, Any] = {
            "schema_id": DECISION_SCHEMA, "controller_version": CONTROLLER_VERSION,
            "action": action, "should_infer": False, "reason": None,
            "plan_id": runtime["plan_id"], "plan_version": runtime["plan_version"],
            "backend_id": backend, "unit_id": runtime["checkpoint"].get("next_unit"),
            "request_id": None, "live_main_sha": live_main_sha,
            "definition_digest": bundle["definition_digest"],
            "checkpoint_before": copy.deepcopy(runtime["checkpoint"]),
            "checkpoint_before_hash": sha256_json(runtime["checkpoint"]),
            "runtime_before_hash": sha256_json(runtime),
            "billing_gate": hosted_billing_attestation(bundle["controller_contract"]),
            "unit": None, "created_at": now_utc(),
        }
        if action == "status":
            decision["reason"] = "status_only"
        elif action == "pause":
            decision["reason"] = "manual_stop_requested"
        elif action == "switch_backend":
            decision["reason"] = "backend_switched_checkpoint_reverification_required"
        elif action in ("run_one", "resume"):
            if not runtime["execution_enabled"]:
                raise ControllerError("execution_disabled", "execution is still locked in the registered plan and active state")
            if action == "resume" and not current_pause_allows_resume(runtime):
                raise ControllerError("free_limit_reached", "resume time has not arrived", retryable=True)
            if runtime["first_run_supervised_required"] and not runtime["first_run_completed"] and not args.supervised:
                raise ControllerError("manual_stop_requested", "the first real unit requires supervised=true")
            if runtime["pinned_main_sha"] and runtime["pinned_main_sha"] != live_main_sha:
                raise ControllerError("authoritative_main_changed", "live main moved after execution was pinned")
            if backend == "github_models_free":
                decision["billing_gate"] = require_hosted_billing_gate(bundle["controller_contract"])
            unit = selected_unit(bundle, runtime)
            prior_attempts = int(runtime.get("attempts_by_unit", {}).get(unit["unit_id"], 0))
            if prior_attempts >= int(bundle["controller_contract"]["limits"]["maximum_automatic_attempts_per_unit"]) and not args.supervised:
                raise ControllerError("manual_stop_requested", "automatic attempt limit reached; supervised review is required")
            request_id = make_request_id(runtime, unit["unit_id"], backend)
            request = {
                "schema_id": "pmp.automated-plan.backend-request.v1", "controller_version": CONTROLLER_VERSION,
                "backend_id": backend, "model_id": bundle["controller_contract"]["backends"][backend].get("default_model"),
                "billing_gate": decision["billing_gate"],
                "evidence_capsule": build_evidence(definition_root, runtime_root, runtime, bundle, unit, request_id),
                "result_contract": {
                    "schema_id": RESULT_SCHEMA,
                    "required_fields": bundle["contract"]["schema_registry"]["result_envelope"]["required_fields"] + ["proposals"],
                    "allowed_statuses": bundle["contract"]["schema_registry"]["result_envelope"]["allowed_statuses"],
                },
                "created_at": now_utc(),
            }
            write_json(out_dir / "request.json", request)
            decision.update({"should_infer": True, "reason": "one_verified_unit_ready", "unit_id": unit["unit_id"], "request_id": request_id, "unit": unit})
        else:
            raise ControllerError("schema_invalid", f"unsupported action: {action}")
        write_json(out_dir / "decision.json", decision)
        write_json(out_dir / "runtime-before.json", runtime)
    print(json.dumps({"result": "PASS", "phase": "prepare", "action": action, "should_infer": decision["should_infer"], "reason": decision["reason"]}, indent=2))
    return 0


def transport_result(status: str, *, backend_id: str, request_id: str, content: str | None = None, usage: dict[str, Any] | None = None, error: str | None = None, retry_after_seconds: int | None = None, http_status: int | None = None) -> dict[str, Any]:
    return {
        "schema_id": TRANSPORT_SCHEMA, "backend_id": backend_id, "request_id": request_id,
        "status": status, "content": content, "usage": usage or {}, "error": error,
        "retry_after_seconds": retry_after_seconds, "http_status": http_status, "finished_at": now_utc(),
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
        return json.loads(response.read().decode("utf-8")), response.headers


def infer_event(args: argparse.Namespace) -> int:
    request = load_json(args.request.resolve())
    ensure_fields(request, ("schema_id", "backend_id", "billing_gate", "evidence_capsule", "result_contract"), "backend request")
    backend, request_id = request["backend_id"], request["evidence_capsule"]["request_id"]
    reject_paid_environment()
    try:
        if backend == "github_models_free":
            contract = load_json(args.definition_root.resolve() / "automation/controller/v1/controller-contract.json")
            live_attestation = require_hosted_billing_gate(contract)
            if request.get("billing_gate") != live_attestation:
                raise ControllerError("paid_usage_setting_unverified", "billing attestation changed between prepare and inference")
            token = os.environ.get("GITHUB_TOKEN")
            if not token:
                raise ControllerError("backend_unavailable", "GITHUB_TOKEN is required for Hosted Free")
            payload = {
                "model": os.environ.get("PMP_GITHUB_MODEL") or request.get("model_id") or "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "Return one JSON object only. Proposal-only. No repository write or merge authority."},
                    {"role": "user", "content": json.dumps({"evidence_capsule": request["evidence_capsule"], "result_contract": request["result_contract"]}, ensure_ascii=False)},
                ],
                "temperature": 0, "max_tokens": int(os.environ.get("PMP_MAX_OUTPUT_TOKENS", "3000")),
                "response_format": {"type": "json_object"}, "stream": False,
            }
            data, _ = post_json("https://models.github.ai/inference/chat/completions", payload, {
                "Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2026-03-10", "Content-Type": "application/json",
                "User-Agent": "pmp-automated-plan-controller/1.1",
            }, 120)
            result = transport_result("ok", backend_id=backend, request_id=request_id, content=data["choices"][0]["message"]["content"], usage=data.get("usage", {}), http_status=200)
        elif backend == "local_ollama":
            endpoint = os.environ.get("PMP_OLLAMA_ENDPOINT", "http://127.0.0.1:11434/api/chat")
            parsed = urllib.parse.urlparse(endpoint)
            if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
                raise ControllerError("paid_path_detected", "Ollama endpoint must be local loopback HTTP")
            model = os.environ.get("PMP_OLLAMA_MODEL")
            if not model:
                raise ControllerError("backend_unavailable", "PMP_OLLAMA_MODEL is required on the laptop runner")
            data, _ = post_json(endpoint, {
                "model": model, "stream": False, "format": "json",
                "messages": [
                    {"role": "system", "content": "Return one JSON object only. Proposal-only. No repository write or merge authority."},
                    {"role": "user", "content": json.dumps({"evidence_capsule": request["evidence_capsule"], "result_contract": request["result_contract"]}, ensure_ascii=False)},
                ], "options": {"temperature": 0},
            }, {"Content-Type": "application/json"}, 300)
            result = transport_result("ok", backend_id=backend, request_id=request_id, content=data["message"]["content"], usage={"input_tokens_or_units": data.get("prompt_eval_count", 0), "output_tokens_or_units": data.get("eval_count", 0)}, http_status=200)
        else:
            raise ControllerError("backend_unavailable", f"unsupported backend: {backend}")
    except urllib.error.HTTPError as exc:
        body = exc.read(4096).decode("utf-8", "replace")
        if exc.code == 429:
            result = transport_result("rate_limited", backend_id=backend, request_id=request_id, error=body or str(exc), retry_after_seconds=parse_retry_after(exc.headers) or 3600, http_status=exc.code)
        elif 500 <= exc.code < 600:
            result = transport_result("transient_error", backend_id=backend, request_id=request_id, error=body or str(exc), retry_after_seconds=parse_retry_after(exc.headers) or 900, http_status=exc.code)
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
    ensure_fields(result, ("schema_id", "plan_id", "unit_id", "request_id", "backend_id", "status", "proposal_only", "output_paths", "evidence_used", "usage", "verification_claims", "proposals"), "model result")
    expected = {"schema_id": RESULT_SCHEMA, "plan_id": decision["plan_id"], "unit_id": decision["unit_id"], "request_id": decision["request_id"], "backend_id": decision["backend_id"]}
    for key, value in expected.items():
        if result.get(key) != value:
            raise ControllerError("schema_invalid", f"model result {key} mismatch")
    if result["proposal_only"] is not True or result["status"] not in {"proposed", "needs_more_evidence", "blocked", "failed"}:
        raise ControllerError("unsafe_permission_detected", "model result widened authority or used an invalid status")
    if not isinstance(result["proposals"], list):
        raise ControllerError("schema_invalid", "proposals must be an array")
    seen: set[str] = set()
    normalized = []
    for item in result["proposals"]:
        if not isinstance(item, dict):
            raise ControllerError("schema_invalid", "proposal entry must be an object")
        ensure_fields(item, ("path", "content"), "proposal")
        path = item["path"]
        if path in seen or not path_allowed(path, decision["unit"]["output_allowlist"]):
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
        return {name for name in names if name in {".git", "node_modules", "__pycache__", ".pytest_cache"}}
    shutil.copytree(definition_root, destination, dirs_exist_ok=True, ignore=ignore)
    for target, overlay in runtime.get("verified_overlay", {}).items():
        source = runtime_root / safe_rel_path(overlay["runtime_path"])
        destination_path = destination / safe_rel_path(target)
        if not within(destination, destination_path):
            raise ControllerError("changed_file_outside_allowlist", f"unsafe overlay target: {target}")
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination_path)


def safe_workspace_write(workspace: Path, rel: str, content: str) -> None:
    destination = workspace / safe_rel_path(rel)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not within(workspace, destination) or any(part.is_symlink() for part in [destination, *destination.parents] if within(workspace, part)):
        raise ControllerError("changed_file_outside_allowlist", f"unsafe proposal destination: {rel}")
    destination.write_text(content, encoding="utf-8")


def chmod_for_container(workspace: Path) -> None:
    for path in [workspace, *workspace.rglob("*")]:
        try:
            path.chmod(0o777 if path.is_dir() else 0o666)
        except OSError as exc:
            raise ControllerError("sandbox_unavailable", f"could not prepare isolated workspace: {path}") from exc


def container_argv(workspace: Path, command: list[str], contract: dict[str, Any]) -> list[str]:
    if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
        raise ControllerError("schema_invalid", "verification command must be a nonempty argv array")
    allowed = set(contract["verification_sandbox"]["allowed_executables"])
    if command[0] not in allowed:
        raise ControllerError("unsafe_permission_detected", f"verification executable not allowed: {command[0]}")
    image = os.environ.get("PMP_VERIFIER_IMAGE") or contract["verification_sandbox"]["image"]
    return [
        "docker", "run", "--rm", "--init", "--network", "none", "--read-only",
        "--pids-limit", str(contract["verification_sandbox"]["pids_limit"]),
        "--memory", contract["verification_sandbox"]["memory_limit"],
        "--cpus", str(contract["verification_sandbox"]["cpu_limit"]),
        "--cap-drop", "ALL", "--security-opt", "no-new-privileges:true",
        "--user", "65534:65534",
        "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=64m",
        "--mount", f"type=bind,src={workspace},dst=/workspace",
        "--workdir", "/workspace", "--env", "HOME=/tmp", "--env", "CI=true",
        image, *command,
    ]


def run_verification_commands(workspace: Path, commands: list[Any], timeout_seconds: int, contract: dict[str, Any]) -> list[dict[str, Any]]:
    if shutil.which("docker") is None:
        raise ControllerError("sandbox_unavailable", "Docker is required for proposal verification")
    chmod_for_container(workspace)
    records = []
    for command in commands:
        argv = container_argv(workspace, command, contract)
        started = time.monotonic()
        proc = subprocess.run(argv, text=True, capture_output=True, timeout=timeout_seconds, env={"PATH": os.environ.get("PATH", "")})
        records.append({
            "containerized": True, "network": "none", "root_filesystem": "read_only",
            "argv_sha256": sha256_json(command), "exit_code": proc.returncode,
            "stdout_sha256": sha256_bytes(proc.stdout.encode()), "stderr_sha256": sha256_bytes(proc.stderr.encode()),
            "elapsed_ms": int((time.monotonic() - started) * 1000),
        })
        if proc.returncode != 0:
            raise ControllerError("deterministic_verification_failed", f"containerized verification command failed: {command!r}")
    return records


def tree_snapshot(workspace: Path) -> dict[str, str]:
    ignored = {".git", "node_modules", "__pycache__", ".pytest_cache"}
    result: dict[str, str] = {}
    for path in workspace.rglob("*"):
        if path.is_file() and not any(part in ignored for part in path.relative_to(workspace).parts):
            result[path.relative_to(workspace).as_posix()] = sha256_bytes(path.read_bytes())
    return result


def validate_changed_files(before: dict[str, str], after: dict[str, str], allowlist: list[str], artifact_allowlist: list[str] | None = None) -> list[str]:
    changed = sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))
    allowed = allowlist + (artifact_allowlist or [])
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
    for item in result["proposals"]:
        rel = safe_rel_path(item["path"])
        stored_rel = Path("proposals") / rel
        destination = out_dir / stored_rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = item["content"].encode("utf-8")
        destination.write_bytes(data)
        manifest[item["path"]] = {"bundle_path": stored_rel.as_posix(), "sha256": sha256_bytes(data), "size_bytes": len(data)}
    return manifest


def verify_event(args: argparse.Namespace) -> int:
    definition_root, runtime_root, out_dir = args.definition_root.resolve(), args.runtime_root.resolve(), args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    live_main_sha = validate_live_main_sha(args.live_main_sha)
    bundle = load_bundle(definition_root)
    runtime = load_runtime(runtime_root, bundle)
    decision = load_json(args.decision.resolve())
    transport = load_json(args.transport.resolve()) if args.transport else None
    if decision.get("schema_id") != DECISION_SCHEMA or decision["live_main_sha"] != live_main_sha:
        raise ControllerError("authoritative_main_changed", "decision identity or main SHA mismatch")
    if decision["definition_digest"] != bundle["definition_digest"] or decision["checkpoint_before_hash"] != sha256_json(runtime["checkpoint"]) or decision["runtime_before_hash"] != sha256_json(runtime):
        raise ControllerError("checkpoint_mismatch", "definition or checkpoint moved between prepare and verify")
    receipt: dict[str, Any] = {
        "schema_id": VERIFIED_SCHEMA, "kind": None, "decision_sha256": sha256_json(decision),
        "transport_sha256": sha256_json(transport) if transport else None,
        "runtime_before_sha256": sha256_json(runtime), "live_main_sha": live_main_sha,
        "proposal_manifest": {}, "verification": {}, "transition_evidence": {}, "created_at": now_utc(),
    }
    if not decision["should_infer"]:
        receipt.update({"kind": "state_only", "verification": {"passed": True}, "transition_evidence": {"action": decision["action"], "backend_id": decision["backend_id"]}})
    else:
        if not transport or transport.get("schema_id") != TRANSPORT_SCHEMA or transport.get("request_id") != decision["request_id"] or transport.get("backend_id") != decision["backend_id"]:
            raise ControllerError("schema_invalid", "transport identity mismatch")
        if transport["status"] in {"rate_limited", "transient_error", "blocked"}:
            receipt.update({
                "kind": "safe_pause", "verification": {"passed": True, "same_unit_preserved": True},
                "transition_evidence": {"unit_id": decision["unit_id"], "request_id": decision["request_id"], "backend_id": decision["backend_id"], "transport_status": transport["status"], "retry_after_seconds": transport.get("retry_after_seconds")},
            })
        elif transport["status"] == "ok":
            result = validate_model_result(transport.get("content") or "", decision, transport)
            if result["status"] != "proposed":
                raise ControllerError("unresolved_ambiguity", f"model did not produce a complete proposal: {result['status']}")
            manifest = write_proposal_bundle(out_dir, result)
            timeout_seconds = int(bundle["controller_contract"]["limits"]["verification_command_timeout_seconds"])
            with tempfile.TemporaryDirectory(prefix="pmp-verify-a-") as a_dir, tempfile.TemporaryDirectory(prefix="pmp-verify-b-") as b_dir:
                wa, wb = Path(a_dir), Path(b_dir)
                materialize_workspace(definition_root, runtime_root, runtime, wa)
                materialize_workspace(definition_root, runtime_root, runtime, wb)
                before_a, before_b = tree_snapshot(wa), tree_snapshot(wb)
                for item in result["proposals"]:
                    safe_workspace_write(wa, item["path"], item["content"])
                    safe_workspace_write(wb, item["path"], item["content"])
                commands_a = run_verification_commands(wa, decision["unit"]["verification_commands"], timeout_seconds, bundle["controller_contract"])
                commands_b = run_verification_commands(wb, decision["unit"]["verification_commands"], timeout_seconds, bundle["controller_contract"])
                after_a, after_b = tree_snapshot(wa), tree_snapshot(wb)
                changed_a = validate_changed_files(before_a, after_a, decision["unit"]["output_allowlist"], decision["unit"].get("verification_artifact_allowlist", []))
                changed_b = validate_changed_files(before_b, after_b, decision["unit"]["output_allowlist"], decision["unit"].get("verification_artifact_allowlist", []))
                hashes_a, hashes_b = workspace_hashes(wa, result["output_paths"]), workspace_hashes(wb, result["output_paths"])
                if changed_a != changed_b or hashes_a != hashes_b:
                    raise ControllerError("independent_rebuild_mismatch", "independent container workspaces disagree")
            receipt.update({
                "kind": "verified_unit", "proposal_manifest": manifest,
                "verification": {"passed": True, "commands_first": commands_a, "commands_second": commands_b, "changed_files": changed_a, "output_hashes": hashes_a, "independent_rebuild_match": True, "sandbox": "docker-network-none-read-only-root"},
                "transition_evidence": {"unit_id": decision["unit_id"], "request_id": decision["request_id"], "backend_id": decision["backend_id"], "result_status": result["status"], "proposal_count": len(manifest)},
            })
            write_json(out_dir / "model-result.json", result)
        else:
            raise ControllerError("backend_unavailable", transport.get("error") or "backend blocked the request")
    write_json(out_dir / "verified.json", receipt)
    print(json.dumps({"result": "PASS", "phase": "verify", "kind": receipt["kind"]}, indent=2))
    return 0


def validate_decision_for_persist(decision: dict[str, Any], runtime: dict[str, Any], bundle: dict[str, Any], live_main_sha: str) -> None:
    if decision.get("schema_id") != DECISION_SCHEMA or decision.get("live_main_sha") != live_main_sha:
        raise ControllerError("artifact_tampering_detected", "decision identity or main SHA changed")
    if decision.get("definition_digest") != bundle["definition_digest"]:
        raise ControllerError("artifact_tampering_detected", "decision definition digest changed")
    if decision.get("runtime_before_hash") != sha256_json(runtime) or decision.get("checkpoint_before_hash") != sha256_json(runtime["checkpoint"]):
        raise ControllerError("checkpoint_mismatch", "runtime moved before persistence")
    if decision.get("checkpoint_before") != runtime["checkpoint"]:
        raise ControllerError("checkpoint_mismatch", "decision checkpoint does not equal live runtime")
    if decision.get("plan_id") != runtime["plan_id"] or decision.get("plan_version") != runtime["plan_version"]:
        raise ControllerError("plan_identity_mismatch", "decision plan identity mismatch")


def copy_verified_proposals(verified_dir: Path, runtime_root: Path, receipt: dict[str, Any], request_id: str, existing: dict[str, Any]) -> dict[str, Any]:
    overlay = copy.deepcopy(existing)
    validate_id(request_id, "request_id")
    for target, meta in receipt["proposal_manifest"].items():
        source = verified_dir / safe_rel_path(meta["bundle_path"])
        if not within(verified_dir, source) or not source.is_file():
            raise ControllerError("artifact_tampering_detected", f"verified proposal missing: {target}")
        data = source.read_bytes()
        if sha256_bytes(data) != meta["sha256"] or len(data) != int(meta["size_bytes"]):
            raise ControllerError("artifact_tampering_detected", f"verified proposal changed: {target}")
        if receipt["verification"]["output_hashes"].get(target) != meta["sha256"]:
            raise ControllerError("artifact_tampering_detected", f"verification hash does not bind proposal: {target}")
        runtime_rel = Path("proposals") / request_id / safe_rel_path(target)
        destination = runtime_root / runtime_rel
        if not within(runtime_root, destination):
            raise ControllerError("changed_file_outside_allowlist", f"unsafe runtime proposal path: {target}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        overlay[target] = {"runtime_path": runtime_rel.as_posix(), "sha256": meta["sha256"], "request_id": request_id}
    return overlay


def reconstruct_candidate(runtime: dict[str, Any], decision: dict[str, Any], receipt: dict[str, Any], transport: dict[str, Any] | None, bundle: dict[str, Any], runtime_root: Path, verified_dir: Path) -> dict[str, Any]:
    candidate = copy.deepcopy(runtime)
    kind = receipt["kind"]
    if kind == "state_only":
        if decision["should_infer"] or receipt["transition_evidence"].get("action") != decision["action"]:
            raise ControllerError("artifact_tampering_detected", "state-only receipt does not match decision")
        if decision["action"] == "status":
            candidate["last_event"] = "status"
        elif decision["action"] == "pause":
            candidate.update({"status": "paused", "pause": {"reason": "manual_stop_requested", "message": "Paused by operator event.", "resume_not_before": None, "same_unit_preserved": True}, "last_event": "manual_pause"})
        elif decision["action"] == "switch_backend":
            allowed_backend(bundle, decision["backend_id"])
            candidate.update({"selected_backend": decision["backend_id"], "status": "paused" if runtime["execution_enabled"] else "controller_ready_execution_locked", "pause": {"reason": "backend_change", "message": "Backend changed; the same checkpoint will be reverified before work.", "resume_not_before": None, "same_unit_preserved": True}, "last_event": "backend_switched"})
        else:
            raise ControllerError("artifact_tampering_detected", "unsupported state-only action")
    elif kind == "safe_pause":
        if not decision["should_infer"] or not transport or receipt["transport_sha256"] != sha256_json(transport):
            raise ControllerError("artifact_tampering_detected", "safe-pause receipt is not bound to transport")
        if transport["status"] not in {"rate_limited", "transient_error", "blocked"}:
            raise ControllerError("artifact_tampering_detected", "safe-pause transport status is invalid")
        if decision["unit_id"] != runtime["checkpoint"]["next_unit"]:
            raise ControllerError("checkpoint_jump_detected", "safe pause changed the current unit")
        attempts = copy.deepcopy(runtime["attempts_by_unit"])
        attempts[decision["unit_id"]] = int(attempts.get(decision["unit_id"], 0)) + 1
        retry = int(transport.get("retry_after_seconds") or 900)
        resume_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=max(60, retry))
        reason = "free_limit_reached" if transport["status"] == "rate_limited" else "backend_unavailable"
        candidate.update({
            "status": "paused", "attempts_by_unit": attempts, "active_request": None,
            "pause": {"reason": reason, "message": transport.get("error") or transport["status"], "resume_not_before": resume_at.replace(microsecond=0).isoformat().replace("+00:00", "Z"), "same_unit_preserved": True},
            "last_event": "safe_pause", "last_result": {"request_id": decision["request_id"], "unit_id": decision["unit_id"], "backend_id": decision["backend_id"], "status": transport["status"], "verified": False},
        })
    elif kind == "verified_unit":
        if not decision["should_infer"] or not transport or receipt["transport_sha256"] != sha256_json(transport) or transport["status"] != "ok":
            raise ControllerError("artifact_tampering_detected", "verified receipt is not bound to successful transport")
        units = unit_map(bundle["plan"])
        unit_id = runtime["checkpoint"]["next_unit"]
        unit = units.get(unit_id)
        if not unit or decision.get("unit_id") != unit_id or decision.get("unit") != unit:
            raise ControllerError("checkpoint_jump_detected", "decision unit does not equal the reviewed next compiled unit")
        verification = receipt.get("verification", {})
        if verification.get("passed") is not True or verification.get("independent_rebuild_match") is not True or verification.get("sandbox") != "docker-network-none-read-only-root":
            raise ControllerError("artifact_tampering_detected", "verification receipt lacks isolated independent proof")
        if sorted(receipt["proposal_manifest"]) != sorted(verification.get("output_hashes", {})):
            raise ControllerError("artifact_tampering_detected", "proposal manifest and output hashes differ")
        checkpoint = copy_checkpoint(runtime["checkpoint"])
        old_sequence = int(checkpoint["checkpoint_sequence"])
        checkpoint.update({"last_completed_boundary": unit_id, "last_verified_unit": unit_id, "next_unit": unit.get("next_unit"), "checkpoint_sequence": old_sequence + 1})
        if checkpoint["checkpoint_sequence"] != old_sequence + 1:
            raise ControllerError("checkpoint_jump_detected", "checkpoint sequence did not advance exactly once")
        attempts = copy.deepcopy(runtime["attempts_by_unit"])
        attempts[unit_id] = int(attempts.get(unit_id, 0)) + 1
        overlay = copy_verified_proposals(verified_dir, runtime_root, receipt, decision["request_id"], runtime["verified_overlay"])
        candidate.update({
            "status": "complete" if checkpoint["next_unit"] is None else "ready",
            "selected_backend": decision["backend_id"], "first_run_completed": True,
            "pinned_main_sha": runtime.get("pinned_main_sha") or decision["live_main_sha"],
            "checkpoint": checkpoint, "active_request": None, "attempts_by_unit": attempts,
            "verified_overlay": overlay, "billing_gate": decision.get("billing_gate", runtime["billing_gate"]),
            "pause": {"reason": None, "message": None, "resume_not_before": None, "same_unit_preserved": True},
            "last_event": "unit_verified", "last_result": {"request_id": decision["request_id"], "unit_id": unit_id, "backend_id": decision["backend_id"], "status": "proposed", "verified": True, "proposal_count": len(receipt["proposal_manifest"])},
        })
    else:
        raise ControllerError("artifact_tampering_detected", f"unsupported receipt kind: {kind}")
    candidate["updated_at"] = now_utc()
    return candidate


def append_usage(runtime_root: Path, candidate: dict[str, Any], receipt: dict[str, Any]) -> None:
    last = candidate.get("last_result") or {}
    event = {"at": now_utc(), "plan_id": candidate["plan_id"], "unit_id": last.get("unit_id"), "backend_id": last.get("backend_id"), "request_id": last.get("request_id"), "status": last.get("status"), "verified": last.get("verified"), "checkpoint_sequence": candidate["checkpoint"].get("checkpoint_sequence"), "kind": receipt["kind"]}
    with (runtime_root / "usage-events.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def persist_event(args: argparse.Namespace) -> int:
    definition_root, runtime_root = args.definition_root.resolve(), args.runtime_root.resolve()
    live_main_sha = validate_live_main_sha(args.live_main_sha)
    bundle = load_bundle(definition_root)
    reject_paid_environment()
    decision = load_json(args.decision.resolve())
    receipt = load_json(args.verified.resolve())
    transport = load_json(args.transport.resolve()) if args.transport else None
    ensure_exact_keys(receipt, RECEIPT_KEYS, "verified receipt")
    if receipt.get("schema_id") != VERIFIED_SCHEMA or receipt.get("verification", {}).get("passed") is not True:
        raise ControllerError("artifact_tampering_detected", "verified receipt is not approved")
    if receipt.get("live_main_sha") != live_main_sha or receipt.get("decision_sha256") != sha256_json(decision):
        raise ControllerError("artifact_tampering_detected", "receipt binding changed")
    if receipt.get("transport_sha256") != (sha256_json(transport) if transport else None):
        raise ControllerError("artifact_tampering_detected", "transport binding changed")
    with runtime_lock(runtime_root):
        runtime = load_runtime(runtime_root, bundle)
        validate_decision_for_persist(decision, runtime, bundle, live_main_sha)
        if receipt["runtime_before_sha256"] != sha256_json(runtime):
            raise ControllerError("checkpoint_mismatch", "receipt runtime hash does not match live runtime")
        candidate = reconstruct_candidate(runtime, decision, receipt, transport, bundle, runtime_root, args.verified.resolve().parent)
        write_json(runtime_root / "status.json", candidate)
        append_usage(runtime_root, candidate, receipt)
    print(json.dumps({"result": "PASS", "phase": "persist", "status": candidate["status"], "next_unit": candidate["checkpoint"].get("next_unit"), "runtime_write_root": "automation/runtime"}, indent=2))
    return 0


def status_event(args: argparse.Namespace) -> int:
    print(json.dumps(load_runtime(args.runtime_root.resolve(), load_bundle(args.definition_root.resolve())), indent=2))
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="PMP Automated Plan event-driven controller")
    sub = root.add_subparsers(dest="command", required=True)
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
    infer.add_argument("--definition-root", type=Path, required=True)
    infer.add_argument("--request", type=Path, required=True)
    infer.add_argument("--out", type=Path, required=True)
    infer.set_defaults(func=infer_event)
    verify = sub.add_parser("verify", parents=[common])
    verify.add_argument("--decision", type=Path, required=True)
    verify.add_argument("--transport", type=Path)
    verify.add_argument("--out-dir", type=Path, required=True)
    verify.set_defaults(func=verify_event)
    persist = sub.add_parser("persist", parents=[common])
    persist.add_argument("--decision", type=Path, required=True)
    persist.add_argument("--transport", type=Path)
    persist.add_argument("--verified", type=Path, required=True)
    persist.set_defaults(func=persist_event)
    status = sub.add_parser("status")
    status.add_argument("--definition-root", type=Path, required=True)
    status.add_argument("--runtime-root", type=Path, required=True)
    status.set_defaults(func=status_event)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        return args.func(args)
    except ControllerError as exc:
        print(json.dumps({"result": "STOP", "reason": exc.reason, "message": str(exc), "retryable": exc.retryable, "retry_after_seconds": exc.retry_after_seconds}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
