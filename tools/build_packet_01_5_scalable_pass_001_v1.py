#!/usr/bin/env python3
"""Build the first scalable Packet 01.5 applicability pass."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "audit"
APP = AUDIT / "applicability"
ROUTING = AUDIT / "routing-inventory"

PLAN_PATH = APP / "Packet_01.5_Scalable_Pass_001_Plan_v1.json"
GATE_RECEIPT = AUDIT / "Packet_01.5_Scalable_Applicability_Gate_Independent_Verification_v1.json"
INVENTORY_PATH = ROUTING / "Packet_01.5_Blank_Routing_Inventory_v1.jsonl"
WORKER_PATH = REPO / "pmp-worker.js"
WRANGLER_PATH = REPO / "wrangler.toml"
B1_PATH = APP / "Packet_01.5_Applicability_Decisions_Batch_001_v1.jsonl"
B2_PATH = APP / "Packet_01.5_Applicability_Decisions_Batch_002_v1.jsonl"
WINDOW_OUT = APP / "Packet_01.5_Scalable_Pass_001_Window_v1.json"
DECISIONS_OUT = APP / "Packet_01.5_Scalable_Pass_001_Decisions_v1.jsonl"
QUEUE_OUT = APP / "Packet_01.5_Scalable_Pass_001_Evidence_Queue_v1.jsonl"
COVERAGE_OUT = AUDIT / "Packet_01.5_Scalable_Pass_001_Coverage_v1.json"
SUMMARY_OUT = AUDIT / "Packet_01.5_Scalable_Pass_001_v1.md"

INV_SHA = "76169a80e07603cea51d769d3d89b32735149c2aef7eb09f893ed94fe5d72477"
ADDR_SHA = "3d808e1ec3f163e4cb2ab7a15767563fe7c43b9920bcecde9abe711226220916"
B1_SHA = "2de246b718e99bae35f18eb2108e5df24e7bcaf240104e17595dcfc6311bba96"
B2_SHA = "8d629e824d29ab4549e2132a6401c10049d7a3c1476b66dfd52c2dc8849d1000"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"not an object: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def evidence(eid: str, reference: str, stable: str, claim: str) -> dict[str, str]:
    return {
        "evidence_id": eid,
        "source_reference": reference,
        "source_hash_or_stable_reference": stable,
        "claim_supported": claim,
    }


def verify_current_source(worker: str, wrangler: str) -> None:
    require('main = "pmp-worker.js"' in wrangler, "wrangler does not identify pmp-worker.js")
    require('"Access-Control-Allow-Origin": "*"' in worker, "wildcard CORS predicate absent")
    require('"POST /api/latest"' in worker and '"POST /api/truth"' in worker and '"POST /api/code-safety"' in worker, "POST endpoints missing")
    require('/api/provider' not in worker and '/api/model' not in worker and '/api/ai' not in worker and '/api/chat' not in worker, "AI endpoint absence predicate failed")
    require('request.headers.get("Authorization")' not in worker and "request.headers.get('Authorization')" not in worker, "authorization header is checked")
    require('...body' in worker and '...old' in worker and 'type: "PMP_BACKEND_CODE_SAFETY_STATUS"' in worker, "broad JSON merge predicate failed")
    lower = worker.lower()
    for term in ("idempotency-key", "content-length", "rate limiter", "replay nonce"):
        require(term not in lower, f"abuse-control predicate changed: {term}")
    require("# [[kv_namespaces]]" in wrangler and '# binding = "PMP_STORE"' in wrangler, "KV stanza is not commented")
    require("accepted_not_persisted_no_store_binding" in worker, "nonpersistent write acceptance predicate absent")


RULES = {
    "WORKER_AI_ENDPOINTS_ABSENT": {
        "reason": "The repository-configured worker is pmp-worker.js. Its complete endpoint list contains latest, truth, code-safety, and resident-learning routes but no provider, model, AI, or chat request/response endpoint. The preserved claim is therefore a current source-level limitation.",
        "reopen": ["pmp-worker.js gains a guarded provider/model endpoint.", "wrangler.toml selects a different worker entry point.", "Deployment evidence proves a different current backend."],
    },
    "WORKER_WILDCARD_CORS": {
        "reason": "The repository-configured worker sets Access-Control-Allow-Origin to a wildcard and exposes POST endpoints. This is an active conditional security risk because cross-origin reachability depends on deployment and browser context, while the permissive policy is directly present in current source.",
        "reopen": ["The worker replaces wildcard CORS with an explicit allowlist.", "The POST surface is removed or independently protected.", "Deployment evidence proves this source is not serving."],
    },
    "WORKER_POST_AUTH_ABSENT": {
        "reason": "The complete repository-configured worker exposes multiple POST endpoints and performs no Authorization-header or equivalent authentication/authorization check. The risk is current in source and conditional on endpoint reachability.",
        "reopen": ["Authentication and authorization checks are added and tested.", "The POST endpoints are made unreachable to untrusted clients.", "Deployment evidence proves another protected worker is serving."],
    },
    "WORKER_ARBITRARY_JSON_OVERWRITE": {
        "reason": "The current worker parses caller JSON and spreads it into the latest pointer and code-safety objects. Apart from a minimal latest-field check, no schema allowlist prevents caller fields from replacing protected values. This directly supports an active conditional overwrite risk.",
        "reopen": ["Strict request schemas and field allowlists are enforced.", "Protected fields are reconstructed after validation and cannot be caller-controlled.", "Adversarial overwrite tests prove rejection."],
    },
    "WORKER_ABUSE_CONTROLS_ABSENT": {
        "reason": "The complete current worker source contains no visible request-size enforcement, rate limiter, replay nonce, or idempotency-key handling around its POST endpoints. This is an active conditional abuse risk whose real exposure depends on deployment controls outside this file.",
        "reopen": ["Source or platform configuration adds each required control.", "Live edge-policy evidence proves equivalent controls exist outside the worker.", "Independent abuse and replay tests pass."],
    },
    "WORKER_KV_BINDING_ABSENT_ACCEPTS_WRITES": {
        "reason": "wrangler.toml selects pmp-worker.js but leaves the PMP_STORE KV binding commented out. The worker explicitly accepts write requests and returns accepted_not_persisted_no_store_binding when storage is absent. This is a current repository-configured persistence limitation.",
        "reopen": ["A real PMP_STORE binding is configured and independently verified.", "Write endpoints reject requests when storage is unavailable.", "Persistence survives a deployment restart and receives a proof receipt."],
    },
}


def queue_domain(record: dict[str, Any]) -> tuple[str, str, str]:
    text = (record.get("harm_text") or "").lower()
    if any(token in text for token in ("packet ", "roadmap", "authority", "implementation packet", "proof packet")):
        return (
            "AUTHORITATIVE_PACKET_LAW",
            "Capture the currently authoritative packet-law text that directly proves or disproves the preserved claim.",
            "Extract digest-bound governing clauses and independently compare them with this permanent address.",
        )
    if any(token in text for token in ("worker", "endpoint", "cors", "deploy", "backend", "network", "request", "response")):
        return (
            "DEPLOYMENT_AND_LIVE_BEHAVIOR",
            "Capture the current serving artifact, route, headers, and safe live behavior needed to decide the preserved claim.",
            "Identify the deployed revision and run bounded source-plus-live probes with receipts.",
        )
    if any(token in text for token in ("provider", "model", "dependency", "ios", "safari", "cloudflare", "platform", "kv")):
        return (
            "DEPENDENCY_OR_PLATFORM_STATE",
            "Capture the current provider, dependency, binding, or platform state tied to the preserved claim.",
            "Record versions/configuration and run a targeted compatibility or availability test.",
        )
    if any(token in text for token in ("private", "memory", "notes", "secret", "token", "credential")):
        return (
            "PRIVATE_OR_UNCAPTURED_EVIDENCE",
            "Capture a privacy-safe receipt proving or disproving the claim without exposing private values.",
            "Produce a redacted digest or boolean proof through the approved private-evidence boundary.",
        )
    if any(token in text for token in ("conflict", "contradict", "inconsistent", "disagree")):
        return (
            "CROSS_SOURCE_CONFLICT",
            "Resolve the conflicting sources and establish which one is current and authoritative.",
            "Create a precedence comparison with dates, hashes, and an independent adjudication receipt.",
        )
    if any(token in text for token in ("resident", "runtime", "app", "loader", "route", "hook", "ui", "localstorage", "code")):
        return (
            "CURRENT_RUNTIME_SOURCE",
            "Trace the exact current runtime source path and test the behavior named in the preserved claim.",
            "Capture source hashes, effective-map precedence, and a bounded runtime proof.",
        )
    return (
        "OTHER_RECORD_SPECIFIC_PROOF",
        "Gather direct current evidence that specifically proves or disproves the preserved claim.",
        "Define and execute a record-specific source, document, or runtime test with a stable receipt.",
    )


def main() -> None:
    inventory_raw = INVENTORY_PATH.read_bytes()
    require(sha256(inventory_raw) == INV_SHA, "inventory hash changed")
    inventory = [json.loads(line) for line in inventory_raw.splitlines()]
    require(len(inventory) == 2750, "inventory count changed")
    addresses = [record["composite_address"] for record in inventory]
    require(sha256(("\n".join(addresses) + "\n").encode()) == ADDR_SHA, "address sequence changed")
    window = inventory[:122]
    require(window[0]["composite_address"] == "P01.5::B::0001" and window[-1]["composite_address"] == "P01.5::B::0122", "window bounds changed")
    require(all(record["source_set"] == "BASELINE" for record in window), "window includes non-baseline record")

    plan = load_object(PLAN_PATH)
    gate = load_object(GATE_RECEIPT)
    require(gate.get("status") == "PASS_SCALABLE_APPLICABILITY_PROCESSING_AUTHORIZED", "scalable gate is not PASS")
    require(gate.get("first_pass_records") == 122 and gate.get("mass_unknown_hold_prohibited") is True, "gate constraints changed")
    require(plan.get("decision_author") != plan.get("decision_verifier"), "author equals verifier")
    require(sha256(B1_PATH.read_bytes()) == B1_SHA and sha256(B2_PATH.read_bytes()) == B2_SHA, "prior overlay changed")

    worker = WORKER_PATH.read_text(encoding="utf-8")
    wrangler = WRANGLER_PATH.read_text(encoding="utf-8")
    verify_current_source(worker, wrangler)
    worker_sha = sha256(WORKER_PATH.read_bytes())
    wrangler_sha = sha256(WRANGLER_PATH.read_bytes())
    gate_sha = sha256(GATE_RECEIPT.read_bytes())
    plan_sha = sha256(PLAN_PATH.read_bytes())
    prior = {}
    for path in (B1_PATH, B2_PATH):
        for item in load_jsonl(path):
            prior[item["composite_address"]] = (str(path.relative_to(REPO)), sha256(path.read_bytes()), item)

    source_by_address = {record["composite_address"]: record for record in window}
    decisions = []
    decided_addresses = set()
    for rule in plan["evidence_supported_decisions"]:
        address = rule["composite_address"]
        source = source_by_address[address]
        require(source["original_identifier"] == rule["original_identifier"], f"identifier mismatch: {address}")
        require(rule["rule_id"] in RULES, f"unknown rule: {address}")
        require(address in prior, f"missing prior decision: {address}")
        prior_path, prior_sha, prior_item = prior[address]
        decision = {
            "composite_address": address,
            "source_inventory_sha256": INV_SHA,
            "source_envelope_hash": source["envelope_hash"],
            "source_block_hash": source["source_block_hash"],
            "decision_stage": "APPLICABILITY_ONLY",
            "applicability_state": rule["state"],
            "applicability_evidence": [
                evidence(f"SP001-SOURCE-{address}", f"{INVENTORY_PATH.relative_to(REPO)}#{address}", source["envelope_hash"], "Preserves the exact historical claim and immutable identity."),
                evidence(f"SP001-WORKER-{address}", str(WORKER_PATH.relative_to(REPO)), f"sha256:{worker_sha}", f"Current worker source satisfies evidence rule {rule['rule_id']}."),
                evidence(f"SP001-WRANGLER-{address}", str(WRANGLER_PATH.relative_to(REPO)), f"sha256:{wrangler_sha}", "Current repository configuration selects pmp-worker.js and records the storage binding state."),
                evidence(f"SP001-PRIOR-{address}", f"{prior_path}#{address}", f"sha256:{prior_sha}#{address}", f"Supersedes the earlier {prior_item['applicability_state']} decision using stronger current source evidence."),
                evidence(f"SP001-GATE-{address}", str(GATE_RECEIPT.relative_to(REPO)), f"sha256:{gate_sha}", "Authorizes evidence-first scalable applicability processing while prohibiting routing."),
                evidence(f"SP001-PLAN-{address}", f"{PLAN_PATH.relative_to(REPO)}#{rule['rule_id']}", f"sha256:{plan_sha}#{rule['rule_id']}", "Binds the record to its reviewed evidence predicate and state."),
            ],
            "applicability_reasoning_summary": RULES[rule["rule_id"]]["reason"],
            "applicability_confidence": rule["confidence"],
            "primary_destination": None,
            "secondary_destinations": [],
            "cross_cutting_laws": [],
            "semantic_cluster_ids": [],
            "routing_evidence": [],
            "routing_rationale": "",
            "routing_confidence": None,
            "expected_receiving_work": "",
            "expected_completion_evidence": "",
            "unresolved_dependencies": [],
            "hold_reason": "",
            "reopening_conditions": RULES[rule["rule_id"]]["reopen"],
            "decision_version": "Packet-01.5-Scalable-Pass-001-v1",
            "decision_author": plan["decision_author"],
            "routing_decision_verifier": plan["decision_verifier"],
            "closure_state": "OPEN",
        }
        decisions.append(decision)
        decided_addresses.add(address)

    queues = []
    domain_counts: dict[str, int] = {}
    for record in window:
        address = record["composite_address"]
        if address in decided_addresses:
            continue
        domain, missing, method = queue_domain(record)
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        queues.append({
            "composite_address": address,
            "source_record_ordinal": record["source_record_ordinal"],
            "original_identifier": record["original_identifier"],
            "source_envelope_hash": record["envelope_hash"],
            "queue_id": f"SP001-{domain}",
            "evidence_domain": domain,
            "missing_proof": f"{missing} Preserved claim: {record['harm_text']}",
            "recommended_acquisition_method": method,
            "decision_blocked_until": "The missing proof is captured, hashed, and independently verified against this permanent address.",
            "reopening_trigger": "New current evidence, a source/configuration change, a conflict, or a stale prior receipt.",
        })

    window_manifest = {
        "packet": "01.5",
        "pass_id": "SCALABLE-PASS-001",
        "source_inventory_sha256": INV_SHA,
        "address_sequence_sha256": ADDR_SHA,
        "first_address": window[0]["composite_address"],
        "last_address": window[-1]["composite_address"],
        "records": 122,
        "source_set": "BASELINE",
        "record_identities": [
            {key: record[key] for key in ("composite_address", "source_record_ordinal", "original_identifier", "envelope_hash", "source_block_hash")}
            for record in window
        ],
    }
    WINDOW_OUT.write_text(json.dumps(window_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    DECISIONS_OUT.write_text("".join(json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for item in decisions), encoding="utf-8")
    QUEUE_OUT.write_text("".join(json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for item in queues), encoding="utf-8")

    coverage = {
        "packet": "01.5",
        "pass_id": "SCALABLE-PASS-001",
        "window_records": 122,
        "decided_records": len(decisions),
        "queued_records": len(queues),
        "unknown_hold_decisions": 0,
        "coverage_complete": len(decisions) + len(queues) == 122,
        "decision_addresses": [item["composite_address"] for item in decisions],
        "queue_domain_counts": domain_counts,
        "routing_assignments": 0,
        "grouping_assignments": 0,
        "source_records_removed_or_closed": 0,
    }
    COVERAGE_OUT.write_text(json.dumps(coverage, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    SUMMARY_OUT.write_text(f"""# Packet 01.5 — Scalable Pass 001 v1

STATUS: BUILT — PENDING INDEPENDENT VERIFICATION
WINDOW: 122 baseline records (`P01.5::B::0001` through `P01.5::B::0122`)
EVIDENCE-SUPPORTED DECISIONS: {len(decisions)}
EVIDENCE-ACQUISITION QUEUE ENTRIES: {len(queues)}
UNKNOWN — HOLD CREATED: 0
ROUTING ASSIGNMENTS: 0
SEMANTIC GROUPING: 0
SOURCE RECORDS REMOVED OR CLOSED: 0

## Evidence-supported decisions

- `AI-003`: `CURRENT DEFECT OR LIMITATION`
- `AI-004`: `ACTIVE CONDITIONAL RISK`
- `AI-005`: `ACTIVE CONDITIONAL RISK`
- `AI-006`: `ACTIVE CONDITIONAL RISK`
- `AI-007`: `ACTIVE CONDITIONAL RISK`
- `AI-008`: `CURRENT DEFECT OR LIMITATION`

The other {len(queues)} records remain undecided and are separated into evidence-acquisition queues with record-specific missing proof. They were not mass-classified as HOLD.

Stop before routing, grouping, closure, implementation, or Packet 04.
""", encoding="utf-8")
    require(INVENTORY_PATH.read_bytes() == inventory_raw, "inventory changed during build")
    print(f"PASS: built scalable pass with {len(decisions)} decisions and {len(queues)} queue entries")


if __name__ == "__main__":
    main()
