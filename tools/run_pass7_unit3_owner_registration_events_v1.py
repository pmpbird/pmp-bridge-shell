#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
UNIT2 = ROOT / "audit/pass7/pass7-section-owner-unit2-capability-contract-v1.json"
RECORD = ROOT / "audit/pass7/pass7-section-owner-unit3-registration-events-v1.json"
RESULT_TYPE = "PMP_PASS7_SECTION_OWNER_UNIT3_EVENT_RESULT_V1"
EVENT_VERSION = "PMP_SECTION_OWNER_REGISTRATION_EVENT_V1"
VERSION = "1.0.0"
ID = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
RFC3339 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
EVENT_TYPES = {
    "OWNER_REGISTERED",
    "OWNER_UPDATED",
    "OWNER_REMOVED",
    "OWNER_GROWTH_OBSERVED",
}
REQUIRED_FIELDS = {
    "event_version",
    "event_id",
    "operation_id",
    "monotonic_sequence",
    "registry_epoch",
    "event_type",
    "owner_id",
    "section_id",
    "source_version",
    "observed_at",
    "previous_event_digest",
    "authority",
}
AUTHORITY_FIELDS = {
    "contract_version",
    "authorizer",
    "subject_id",
    "capability_id",
    "decision",
    "action",
}


def canonical(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: canonical(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [canonical(item) for item in value]
    return value


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(canonical(value), separators=(",", ":")).encode()
    ).hexdigest()


def contract() -> dict[str, Any]:
    return json.loads(UNIT2.read_text())["capability_contract"]


def _deny(code: str, event: Any) -> dict[str, Any]:
    return {
        "accepted": False,
        "mutated": False,
        "authority_granted": False,
        "code": code,
        "event_id": event.get("event_id") if isinstance(event, dict) else None,
        "operation_id": event.get("operation_id") if isinstance(event, dict) else None,
    }


def _accept(code: str, event: dict[str, Any], mutated: bool) -> dict[str, Any]:
    return {
        "accepted": True,
        "mutated": mutated,
        "authority_granted": False,
        "code": code,
        "event_id": event["event_id"],
        "operation_id": event["operation_id"],
    }


def validate_shape(event: Any) -> str | None:
    if not isinstance(event, dict) or set(event) != REQUIRED_FIELDS:
        return "REJECTED_MALFORMED_EVENT"
    if event["event_version"] != EVENT_VERSION:
        return "REJECTED_EVENT_VERSION"
    for key in ("event_id", "operation_id", "owner_id", "section_id", "source_version"):
        if not isinstance(event[key], str) or not ID.fullmatch(event[key]):
            return "REJECTED_IDENTITY"
    if not isinstance(event["monotonic_sequence"], int) or event["monotonic_sequence"] < 1:
        return "REJECTED_SEQUENCE"
    if not isinstance(event["registry_epoch"], int) or event["registry_epoch"] < 1:
        return "REJECTED_EPOCH"
    if event["event_type"] not in EVENT_TYPES:
        return "REJECTED_EVENT_TYPE"
    if not isinstance(event["observed_at"], str) or not RFC3339.fullmatch(event["observed_at"]):
        return "REJECTED_TIME"
    previous = event["previous_event_digest"]
    if previous is not None and (
        not isinstance(previous, str)
        or len(previous) != 64
        or any(char not in "0123456789abcdef" for char in previous)
    ):
        return "REJECTED_PREVIOUS_DIGEST"
    authority = event["authority"]
    if not isinstance(authority, dict) or set(authority) != AUTHORITY_FIELDS:
        return "REJECTED_AUTHORITY_SHAPE"
    for key in ("contract_version", "authorizer", "subject_id", "capability_id", "decision", "action"):
        if not isinstance(authority[key], str) or not authority[key]:
            return "REJECTED_AUTHORITY_SHAPE"
    return None


def evaluate_events(events: list[Any]) -> dict[str, Any]:
    capability_contract = contract()
    known = capability_contract["owners"]
    contract_version = capability_contract["contract_version"]
    root = capability_contract["root_grant_authority"]
    registered: dict[str, dict[str, Any]] = {}
    pending_growth: dict[str, dict[str, Any]] = {}
    last_by_owner: dict[str, dict[str, Any]] = {}
    event_digests: dict[str, str] = {}
    operation_ids: set[str] = set()
    journal: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    outcomes: list[dict[str, Any]] = []

    for raw in events:
        event = copy.deepcopy(raw)
        shape = validate_shape(event)
        if shape:
            outcomes.append(_deny(shape, event))
            continue
        event_id = event["event_id"]
        event_digest = digest(event)
        if event_id in event_digests:
            if event_digests[event_id] == event_digest:
                outcomes.append(_accept("DUPLICATE_EVENT_IGNORED", event, False))
            else:
                outcomes.append(_deny("REJECTED_DUPLICATE_EVENT_CONFLICT", event))
            continue
        if event["operation_id"] in operation_ids:
            outcomes.append(_deny("REJECTED_DUPLICATE_OPERATION", event))
            continue

        authority = event["authority"]
        if authority["contract_version"] != contract_version:
            outcomes.append(_deny("REJECTED_CAPABILITY_CONTRACT_VERSION", event))
            continue
        owner = known.get(event["owner_id"])
        is_growth = event["event_type"] == "OWNER_GROWTH_OBSERVED"
        if owner is None and not is_growth:
            outcomes.append(_deny("REJECTED_UNDECLARED_OWNER", event))
            continue
        if owner is not None and event["section_id"] != owner["section_id"]:
            outcomes.append(_deny("REJECTED_OWNER_SECTION_MISMATCH", event))
            continue

        if is_growth:
            if authority != {
                "contract_version": contract_version,
                "authorizer": "diagnostics_owner",
                "subject_id": "diagnostics_owner",
                "capability_id": "cap:p7u3:growth-observer",
                "decision": "OBSERVED_ONLY_NO_AUTHORITY",
                "action": "observe_owner_growth",
            }:
                outcomes.append(_deny("REJECTED_GROWTH_OBSERVER_AUTHORITY", event))
                continue
        else:
            action = {
                "OWNER_REGISTERED": "register_owner",
                "OWNER_UPDATED": "update_owner",
                "OWNER_REMOVED": "remove_owner",
            }[event["event_type"]]
            if (
                authority["authorizer"] != root
                or authority["subject_id"] != event["owner_id"]
                or authority["decision"] != "AUTHORIZED"
                or authority["action"] != action
                or not authority["capability_id"].startswith("cap:p7u3:")
            ):
                outcomes.append(_deny("REJECTED_REGISTRATION_AUTHORITY", event))
                continue

        prior = last_by_owner.get(event["owner_id"])
        if prior is None:
            if event["monotonic_sequence"] != 1 or event["previous_event_digest"] is not None:
                outcomes.append(_deny("REJECTED_SEQUENCE_START", event))
                continue
        else:
            if event["registry_epoch"] < prior["registry_epoch"]:
                outcomes.append(_deny("REJECTED_STALE_EPOCH", event))
                continue
            if event["registry_epoch"] > prior["registry_epoch"] + 1:
                outcomes.append(_deny("REJECTED_EPOCH_GAP", event))
                continue
            if event["monotonic_sequence"] <= prior["monotonic_sequence"]:
                outcomes.append(_deny("REJECTED_STALE_SEQUENCE", event))
                continue
            if event["monotonic_sequence"] != prior["monotonic_sequence"] + 1:
                outcomes.append(_deny("REJECTED_SEQUENCE_GAP", event))
                continue
            if event["previous_event_digest"] != prior["event_digest"]:
                outcomes.append(_deny("REJECTED_EVENT_CHAIN", event))
                continue
            if event["observed_at"] < prior["observed_at"]:
                outcomes.append(_deny("REJECTED_TIME_REGRESSION", event))
                continue

        kind = event["event_type"]
        if kind == "OWNER_REGISTERED":
            if event["owner_id"] in registered:
                outcomes.append(_deny("REJECTED_DUPLICATE_OWNER", event))
                continue
            registered[event["owner_id"]] = {
                "owner_id": event["owner_id"],
                "section_id": event["section_id"],
                "source_version": event["source_version"],
                "registry_epoch": event["registry_epoch"],
                "status": "REGISTERED",
                "authority": "CAPABILITY_BOUND",
            }
            code = "OWNER_REGISTERED"
        elif kind == "OWNER_UPDATED":
            if event["owner_id"] not in registered:
                outcomes.append(_deny("REJECTED_OWNER_NOT_REGISTERED", event))
                continue
            registered[event["owner_id"]].update(
                source_version=event["source_version"],
                registry_epoch=event["registry_epoch"],
            )
            code = "OWNER_UPDATED"
        elif kind == "OWNER_REMOVED":
            if event["owner_id"] not in registered:
                outcomes.append(_deny("REJECTED_OWNER_NOT_REGISTERED", event))
                continue
            registered.pop(event["owner_id"])
            code = "OWNER_REMOVED"
        else:
            pending_growth[event["owner_id"]] = {
                "owner_id": event["owner_id"],
                "section_id": event["section_id"],
                "source_version": event["source_version"],
                "status": "OBSERVED_PENDING_NO_AUTHORITY",
                "authority_granted": False,
            }
            code = "OWNER_GROWTH_RECORDED_NO_AUTHORITY"

        normalized = copy.deepcopy(event)
        normalized["event_digest"] = event_digest
        last_by_owner[event["owner_id"]] = normalized
        event_digests[event_id] = event_digest
        operation_ids.add(event["operation_id"])
        journal.append(normalized)
        diagnostics.append(
            {
                "operation_id": event["operation_id"],
                "event_id": event_id,
                "owner_id": event["owner_id"],
                "event_type": kind,
                "result": code,
                "authority_granted": False,
            }
        )
        outcomes.append(_accept(code, event, True))

    journal_operations = [row["operation_id"] for row in journal]
    diagnostic_operations = [row["operation_id"] for row in diagnostics]
    result = {
        "type": RESULT_TYPE,
        "version": VERSION,
        "status": "PASS",
        "event_version": EVENT_VERSION,
        "outcomes": outcomes,
        "snapshot": {
            "registered": [registered[key] for key in sorted(registered)],
            "pending_growth": [pending_growth[key] for key in sorted(pending_growth)],
            "journal": journal,
            "diagnostics": diagnostics,
        },
        "summary": {
            "events": len(events),
            "accepted": sum(item["accepted"] for item in outcomes),
            "mutated": sum(item["mutated"] for item in outcomes),
            "rejected": sum(not item["accepted"] for item in outcomes),
            "registered_owners": len(registered),
            "pending_growth": len(pending_growth),
            "authority_grants": sum(item["authority_granted"] for item in outcomes),
            "shared_operation_identities": journal_operations == diagnostic_operations,
        },
        "effects": {
            "production_files_changed": False,
            "browser_launched": False,
            "network_requests": False,
            "storage_writes": False,
            "route_changes": False,
            "bank_mutations": False,
            "persisted_user_data_changed": False,
            "live_observation_performed": False,
            "formal_proof_performed": False,
        },
        "claim_ceiling": (
            "Pure event-contract evaluation only; pending growth is visible but grants "
            "no authority and no production owner is registered, updated, or removed."
        ),
    }
    result["result_sha256"] = digest(result)
    return result


def verify_result_hash(result: dict[str, Any]) -> bool:
    if not isinstance(result, dict) or not isinstance(result.get("result_sha256"), str):
        return False
    candidate = copy.deepcopy(result)
    expected = candidate.pop("result_sha256")
    return digest(candidate) == expected


def authority(
    owner_id: str,
    action: str,
    *,
    decision: str = "AUTHORIZED",
    authorizer: str = "app_orchestrator_owner",
    subject_id: str | None = None,
    capability_id: str | None = None,
) -> dict[str, str]:
    return {
        "contract_version": contract()["contract_version"],
        "authorizer": authorizer,
        "subject_id": subject_id or owner_id,
        "capability_id": capability_id or f"cap:p7u3:{owner_id}",
        "decision": decision,
        "action": action,
    }


def event(
    event_id: str,
    operation_id: str,
    sequence: int,
    event_type: str,
    owner_id: str,
    section_id: str,
    action: str,
    *,
    previous_event_digest: str | None = None,
    registry_epoch: int = 1,
    observed_at: str = "2026-07-27T00:00:00Z",
    event_authority: dict[str, str] | None = None,
) -> dict[str, Any]:
    return {
        "event_version": EVENT_VERSION,
        "event_id": event_id,
        "operation_id": operation_id,
        "monotonic_sequence": sequence,
        "registry_epoch": registry_epoch,
        "event_type": event_type,
        "owner_id": owner_id,
        "section_id": section_id,
        "source_version": "source:v1",
        "observed_at": observed_at,
        "previous_event_digest": previous_event_digest,
        "authority": event_authority or authority(owner_id, action),
    }


def scenario_result() -> dict[str, Any]:
    register = event(
        "evt:p7u3:register-bank",
        "op:p7u3:register-bank",
        1,
        "OWNER_REGISTERED",
        "bank_screen_owner",
        "bank",
        "register_owner",
    )
    update = event(
        "evt:p7u3:update-bank",
        "op:p7u3:update-bank",
        2,
        "OWNER_UPDATED",
        "bank_screen_owner",
        "bank",
        "update_owner",
        previous_event_digest=digest(register),
    )
    growth_authority = authority(
        "diagnostics_owner",
        "observe_owner_growth",
        decision="OBSERVED_ONLY_NO_AUTHORITY",
        authorizer="diagnostics_owner",
        subject_id="diagnostics_owner",
        capability_id="cap:p7u3:growth-observer",
    )
    growth = event(
        "evt:p7u3:growth-new",
        "op:p7u3:growth-new",
        1,
        "OWNER_GROWTH_OBSERVED",
        "future_section_owner",
        "future_section",
        "observe_owner_growth",
        event_authority=growth_authority,
    )
    result = evaluate_events([register, update, growth])
    return {
        "type": "PMP_PASS7_SECTION_OWNER_UNIT3_SCENARIO_RESULT_V1",
        "version": VERSION,
        "status": "PASS",
        "result": result,
        "summary": result["summary"],
        "result_sha256": digest(result),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    result = scenario_result()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(payload)
    print(payload, end="")


if __name__ == "__main__":
    main()
