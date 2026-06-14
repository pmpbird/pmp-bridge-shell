#!/usr/bin/env python3
"""Independent policy constants for Packet 01.5 scalable pass 001."""
from __future__ import annotations

import hashlib
import json
from typing import Any

INV_SHA = "76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477"
ADDR_SHA = "3d808e1ec3f163e4cb2ab7a15767563fe7c43b9920bcecde9abe711226220916"
B1_SHA = "2de246b718e99bae35f18eb2108e5df24e7bcaf240104e17595dcfc6311bba96"
B2_SHA = "8d629e824d29ab4549e2132a6401c10049d7a3c1476b66dfd52c2dc8849d1000"

EXPECTED = {
    "P01.5::B::0003": ("AI-003", "CURRENT DEFECT OR LIMITATION", 99, "WORKER_AI_ENDPOINTS_ABSENT"),
    "P01.5::B::0004": ("AI-004", "ACTIVE CONDITIONAL RISK", 99, "WORKER_WILDCARD_CORS"),
    "P01.5::B::0005": ("AI-005", "ACTIVE CONDITIONAL RISK", 98, "WORKER_POST_AUTH_ABSENT"),
    "P01.5::B::0006": ("AI-006", "ACTIVE CONDITIONAL RISK", 99, "WORKER_ARBITRARY_JSON_OVERWRITE"),
    "P01.5::B::0007": ("AI-007", "ACTIVE CONDITIONAL RISK", 96, "WORKER_ABUSE_CONTROLS_ABSENT"),
    "P01.5::B::0008": ("AI-008", "CURRENT DEFECT OR LIMITATION", 99, "WORKER_KV_BINDING_ABSENT_ACCEPTS_WRITES"),
}

QUEUE_FIELDS = {
    "composite_address", "source_record_ordinal", "original_identifier",
    "source_envelope_hash", "queue_id", "evidence_domain", "missing_proof",
    "recommended_acquisition_method", "decision_blocked_until", "reopening_trigger",
}

EVIDENCE_FIELDS = {
    "evidence_id", "source_reference", "source_hash_or_stable_reference", "claim_supported",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def envelope_hash(record: dict[str, Any]) -> str:
    value = dict(record)
    value.pop("envelope_hash", None)
    return sha256(canonical(value))


def evidence_domain(record: dict[str, Any]) -> str:
    text = (record.get("harm_text") or "").lower()
    if any(x in text for x in ("packet ", "roadmap", "authority", "implementation packet", "proof packet")):
        return "AUTHORITATIVE_PACKET_LAW"
    if any(x in text for x in ("worker", "endpoint", "cors", "deploy", "backend", "network", "request", "response")):
        return "DEPLOYMENT_AND_LIVE_BEHAVIOR"
    if any(x in text for x in ("provider", "model", "dependency", "ios", "safari", "cloudflare", "platform", "kv")):
        return "DEPENDENCY_OR_PLATFORM_STATE"
    if any(x in text for x in ("private", "memory", "notes", "secret", "token", "credential")):
        return "PRIVATE_OR_UNCAPTURED_EVIDENCE"
    if any(x in text for x in ("conflict", "contradict", "inconsistent", "disagree")):
        return "CROSS_SOURCE_CONFLICT"
    if any(x in text for x in ("resident", "runtime", "app", "loader", "route", "hook", "ui", "localstorage", "code")):
        return "CURRENT_RUNTIME_SOURCE"
    return "OTHER_RECORD_SPECIFIC_PROOF"


def verify_current_sources(worker: str, wrangler: str) -> None:
    assert 'main = "pmp-worker.js"' in wrangler
    assert '"Access-Control-Allow-Origin": "*"' in worker
    assert all(route not in worker for route in ("/api/provider", "/api/model", "/api/ai", "/api/chat"))
    assert 'request.headers.get("Authorization")' not in worker
    assert "request.headers.get('Authorization')" not in worker
    assert "...old" in worker and "...body" in worker
    assert all(term not in worker.lower() for term in ("idempotency-key", "content-length", "rate limiter", "replay nonce"))
    assert "# [[kv_namespaces]]" in wrangler and '# binding = "PMP_STORE"' in wrangler
    assert "accepted_not_persisted_no_store_binding" in worker
