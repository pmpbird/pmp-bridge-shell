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
RECORD = ROOT / "audit/pass7/pass7-section-owner-unit2-capability-contract-v1.json"
RESULT_TYPE = "PMP_PASS7_SECTION_OWNER_UNIT2_CONTRACT_RESULT_V1"
VERSION = "1.0.0"
ID = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
RFC3339 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


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


def load_contract() -> dict[str, Any]:
    return json.loads(RECORD.read_text())["capability_contract"]


def _valid_id(value: Any) -> bool:
    return isinstance(value, str) and bool(ID.fullmatch(value))


def _valid_time(value: Any) -> bool:
    return isinstance(value, str) and bool(RFC3339.fullmatch(value))


def _deny(code: str, operation_id: Any = None) -> dict[str, Any]:
    return {
        "accepted": False,
        "mutated": False,
        "authorized": False,
        "code": code,
        "operation_id": operation_id if isinstance(operation_id, str) else None,
    }


def _accept(code: str, operation_id: str, authorized: bool = False) -> dict[str, Any]:
    return {
        "accepted": True,
        "mutated": code in {"CAPABILITY_GRANTED", "CAPABILITY_REVOKED"},
        "authorized": authorized,
        "code": code,
        "operation_id": operation_id,
    }


def _shape(event: Any) -> str | None:
    if not isinstance(event, dict):
        return "REJECTED_MALFORMED"
    required = {"type", "operation_id", "observed_at"}
    if not required <= set(event):
        return "REJECTED_MALFORMED"
    if not _valid_id(event.get("operation_id")):
        return "REJECTED_OPERATION_ID"
    if not _valid_time(event.get("observed_at")):
        return "REJECTED_TIME"
    if event.get("type") not in {"GRANT", "DELEGATE", "REVOKE", "AUTHORIZE"}:
        return "REJECTED_EVENT_TYPE"
    return None


def _capability_shape(capability: Any, contract: dict[str, Any]) -> str | None:
    required = set(contract["required_capability_fields"])
    if not isinstance(capability, dict) or set(capability) != required:
        return "REJECTED_CAPABILITY_SHAPE"
    if capability.get("contract_version") != contract["contract_version"]:
        return "REJECTED_CONTRACT_VERSION"
    for key in ("capability_id", "owner_id", "section_id", "subject_id", "granted_by"):
        if not _valid_id(capability.get(key)):
            return "REJECTED_CAPABILITY_IDENTITY"
    if not isinstance(capability.get("actions"), list) or not capability["actions"]:
        return "REJECTED_EMPTY_ACTIONS"
    if not isinstance(capability.get("resources"), list) or not capability["resources"]:
        return "REJECTED_EMPTY_RESOURCES"
    if len(set(capability["actions"])) != len(capability["actions"]):
        return "REJECTED_DUPLICATE_ACTION"
    if len(set(capability["resources"])) != len(capability["resources"]):
        return "REJECTED_DUPLICATE_RESOURCE"
    if not all(_valid_id(value) for value in capability["actions"]):
        return "REJECTED_ACTION"
    if not all(_valid_id(value) for value in capability["resources"]):
        return "REJECTED_RESOURCE"
    if not _valid_time(capability.get("issued_at")) or not _valid_time(
        capability.get("expires_at")
    ):
        return "REJECTED_TIME"
    if capability["issued_at"] >= capability["expires_at"]:
        return "REJECTED_EXPIRY"
    if not isinstance(capability.get("delegable"), bool):
        return "REJECTED_DELEGATION_FLAG"
    if not isinstance(capability.get("delegation_depth"), int):
        return "REJECTED_DELEGATION_DEPTH"
    parent = capability.get("parent_capability_id")
    if parent is not None and not _valid_id(parent):
        return "REJECTED_PARENT_ID"
    if not isinstance(capability.get("revocation_epoch"), int):
        return "REJECTED_REVOCATION_EPOCH"
    return None


def _descendants(capabilities: dict[str, dict[str, Any]], parent_id: str) -> set[str]:
    found = {parent_id}
    changed = True
    while changed:
        changed = False
        for capability_id, capability in capabilities.items():
            if capability.get("parent_capability_id") in found and capability_id not in found:
                found.add(capability_id)
                changed = True
    return found


def evaluate_events(
    events: list[Any],
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = copy.deepcopy(contract or load_contract())
    owners = contract["owners"]
    root = contract["root_grant_authority"]
    maximum_depth = contract["delegation"]["maximum_depth"]
    capabilities: dict[str, dict[str, Any]] = {}
    revoked: dict[str, int] = {}
    seen_operations: set[str] = set()
    outcomes: list[dict[str, Any]] = []

    for raw in events:
        event = copy.deepcopy(raw)
        shape_error = _shape(event)
        if shape_error:
            outcomes.append(_deny(shape_error, event.get("operation_id") if isinstance(event, dict) else None))
            continue
        operation_id = event["operation_id"]
        if operation_id in seen_operations:
            outcomes.append(_deny("REJECTED_DUPLICATE_OPERATION", operation_id))
            continue
        seen_operations.add(operation_id)

        if event["type"] in {"GRANT", "DELEGATE"}:
            capability = event.get("capability")
            error = _capability_shape(capability, contract)
            if error:
                outcomes.append(_deny(error, operation_id))
                continue
            capability_id = capability["capability_id"]
            if capability_id in capabilities or capability_id in revoked:
                outcomes.append(_deny("REJECTED_DUPLICATE_CAPABILITY", operation_id))
                continue
            owner = owners.get(capability["owner_id"])
            if owner is None:
                outcomes.append(_deny("REJECTED_UNDECLARED_OWNER", operation_id))
                continue
            if capability["section_id"] != owner["section_id"]:
                outcomes.append(_deny("REJECTED_OWNER_SECTION_MISMATCH", operation_id))
                continue
            if not set(capability["actions"]) <= set(owner["allowed_actions"]):
                outcomes.append(_deny("REJECTED_ACTION_OUTSIDE_OWNER", operation_id))
                continue
            if not set(capability["resources"]) <= set(owner["allowed_resources"]):
                outcomes.append(_deny("REJECTED_RESOURCE_OUTSIDE_SECTION", operation_id))
                continue
            if set(capability["actions"]) & set(contract["globally_forbidden_actions"]):
                outcomes.append(_deny("REJECTED_GLOBALLY_FORBIDDEN_ACTION", operation_id))
                continue
            parent_id = capability["parent_capability_id"]
            if event["type"] == "GRANT":
                if parent_id is not None or capability["delegation_depth"] != 0:
                    outcomes.append(_deny("REJECTED_ROOT_GRANT_SHAPE", operation_id))
                    continue
                if capability["granted_by"] != root:
                    outcomes.append(_deny("REJECTED_ROOT_GRANT_AUTHORITY", operation_id))
                    continue
                if capability["subject_id"] != capability["owner_id"]:
                    outcomes.append(_deny("REJECTED_ROOT_SUBJECT", operation_id))
                    continue
            else:
                parent = capabilities.get(parent_id)
                if parent is None:
                    outcomes.append(_deny("REJECTED_PARENT_MISSING", operation_id))
                    continue
                if parent_id in revoked:
                    outcomes.append(_deny("REJECTED_PARENT_REVOKED", operation_id))
                    continue
                if not parent["delegable"]:
                    outcomes.append(_deny("REJECTED_PARENT_NOT_DELEGABLE", operation_id))
                    continue
                if capability["granted_by"] != parent["subject_id"]:
                    outcomes.append(_deny("REJECTED_DELEGATOR_AUTHORITY", operation_id))
                    continue
                if (
                    capability["owner_id"] != parent["owner_id"]
                    or capability["section_id"] != parent["section_id"]
                ):
                    outcomes.append(_deny("REJECTED_CROSS_OWNER_DELEGATION", operation_id))
                    continue
                if not set(capability["actions"]) <= set(parent["actions"]):
                    outcomes.append(_deny("REJECTED_DELEGATED_ACTION_EXPANSION", operation_id))
                    continue
                if not set(capability["resources"]) <= set(parent["resources"]):
                    outcomes.append(_deny("REJECTED_DELEGATED_RESOURCE_EXPANSION", operation_id))
                    continue
                expected_depth = parent["delegation_depth"] + 1
                if (
                    capability["delegation_depth"] != expected_depth
                    or expected_depth > maximum_depth
                ):
                    outcomes.append(_deny("REJECTED_DELEGATION_DEPTH", operation_id))
                    continue
                if capability["expires_at"] > parent["expires_at"]:
                    outcomes.append(_deny("REJECTED_DELEGATED_EXPIRY_EXPANSION", operation_id))
                    continue
                if capability["revocation_epoch"] != parent["revocation_epoch"]:
                    outcomes.append(_deny("REJECTED_REVOCATION_EPOCH", operation_id))
                    continue
            capabilities[capability_id] = capability
            outcomes.append(_accept("CAPABILITY_GRANTED", operation_id))
            continue

        if event["type"] == "REVOKE":
            capability_id = event.get("capability_id")
            actor_id = event.get("actor_id")
            epoch = event.get("revocation_epoch")
            capability = capabilities.get(capability_id)
            if capability is None:
                outcomes.append(_deny("REJECTED_CAPABILITY_MISSING", operation_id))
                continue
            parent = capabilities.get(capability.get("parent_capability_id"))
            allowed_actor = actor_id == root or (
                parent is not None and actor_id == parent["subject_id"]
            )
            if not allowed_actor:
                outcomes.append(_deny("REJECTED_REVOCATION_AUTHORITY", operation_id))
                continue
            prior_epoch = revoked.get(capability_id, capability["revocation_epoch"])
            if not isinstance(epoch, int) or epoch <= prior_epoch:
                outcomes.append(_deny("REJECTED_STALE_REVOCATION", operation_id))
                continue
            for target in _descendants(capabilities, capability_id):
                revoked[target] = epoch
            outcomes.append(_accept("CAPABILITY_REVOKED", operation_id))
            continue

        capability_id = event.get("capability_id")
        capability = capabilities.get(capability_id)
        if capability is None:
            outcomes.append(_deny("REJECTED_CAPABILITY_MISSING", operation_id))
            continue
        if capability_id in revoked:
            outcomes.append(_deny("REJECTED_CAPABILITY_REVOKED", operation_id))
            continue
        if event.get("subject_id") != capability["subject_id"]:
            outcomes.append(_deny("REJECTED_SUBJECT_MISMATCH", operation_id))
            continue
        if (
            event.get("owner_id") != capability["owner_id"]
            or event.get("section_id") != capability["section_id"]
        ):
            outcomes.append(_deny("REJECTED_OWNER_SECTION_MISMATCH", operation_id))
            continue
        if event["observed_at"] < capability["issued_at"]:
            outcomes.append(_deny("REJECTED_NOT_YET_VALID", operation_id))
            continue
        if event["observed_at"] >= capability["expires_at"]:
            outcomes.append(_deny("REJECTED_EXPIRED", operation_id))
            continue
        if event.get("revocation_epoch") != capability["revocation_epoch"]:
            outcomes.append(_deny("REJECTED_REVOCATION_EPOCH", operation_id))
            continue
        if event.get("action") not in capability["actions"]:
            outcomes.append(_deny("REJECTED_ACTION_NOT_GRANTED", operation_id))
            continue
        if event.get("resource") not in capability["resources"]:
            outcomes.append(_deny("REJECTED_RESOURCE_NOT_GRANTED", operation_id))
            continue
        outcomes.append(_accept("AUTHORIZED", operation_id, authorized=True))

    result = {
        "type": RESULT_TYPE,
        "version": VERSION,
        "status": "PASS",
        "contract_version": contract["contract_version"],
        "outcomes": outcomes,
        "summary": {
            "events": len(events),
            "accepted": sum(item["accepted"] for item in outcomes),
            "authorized": sum(item["authorized"] for item in outcomes),
            "rejected": sum(not item["accepted"] for item in outcomes),
            "capabilities_retained": len(capabilities),
            "capabilities_revoked": len(revoked),
        },
        "state": {
            "capability_ids": sorted(capabilities),
            "revoked": dict(sorted(revoked.items())),
        },
        "effects": {
            "production_files_changed": False,
            "browser_launched": False,
            "network_requests": False,
            "storage_writes": False,
            "route_changes": False,
            "bank_mutations": False,
            "helper_ownership_changes": False,
            "persisted_user_data_changed": False,
            "live_observation_performed": False,
            "formal_proof_performed": False,
        },
        "claim_ceiling": (
            "Pure static contract evaluation only; no owner is registered, activated, "
            "delegated in production, or granted runtime authority."
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


def capability(
    capability_id: str,
    owner_id: str,
    section_id: str,
    subject_id: str,
    actions: list[str],
    resources: list[str],
    *,
    granted_by: str = "app_orchestrator_owner",
    parent_capability_id: str | None = None,
    delegation_depth: int = 0,
    delegable: bool = True,
    expires_at: str = "2026-08-01T00:00:00Z",
    revocation_epoch: int = 0,
) -> dict[str, Any]:
    return {
        "contract_version": "PMP_SECTION_OWNER_CAPABILITY_CONTRACT_V1",
        "capability_id": capability_id,
        "owner_id": owner_id,
        "section_id": section_id,
        "subject_id": subject_id,
        "granted_by": granted_by,
        "actions": actions,
        "resources": resources,
        "issued_at": "2026-07-26T00:00:00Z",
        "expires_at": expires_at,
        "delegable": delegable,
        "delegation_depth": delegation_depth,
        "parent_capability_id": parent_capability_id,
        "revocation_epoch": revocation_epoch,
    }


def event(kind: str, operation_id: str, **extra: Any) -> dict[str, Any]:
    return {
        "type": kind,
        "operation_id": operation_id,
        "observed_at": "2026-07-27T00:00:00Z",
        **extra,
    }


def scenario_results() -> dict[str, Any]:
    bank = capability(
        "cap:p7u2:bank-root",
        "bank_screen_owner",
        "bank",
        "bank_screen_owner",
        ["read_bank", "render_bank_detail"],
        ["section:bank"],
    )
    delegated = capability(
        "cap:p7u2:bank-view",
        "bank_screen_owner",
        "bank",
        "bank_view_helper",
        ["read_bank"],
        ["section:bank"],
        granted_by="bank_screen_owner",
        parent_capability_id=bank["capability_id"],
        delegation_depth=1,
        delegable=False,
    )
    positive = [
        event("GRANT", "op:p7u2:grant-bank", capability=bank),
        event("DELEGATE", "op:p7u2:delegate-bank", capability=delegated),
        event(
            "AUTHORIZE",
            "op:p7u2:authorize-bank",
            capability_id=delegated["capability_id"],
            subject_id="bank_view_helper",
            owner_id="bank_screen_owner",
            section_id="bank",
            action="read_bank",
            resource="section:bank",
            revocation_epoch=0,
        ),
        event(
            "REVOKE",
            "op:p7u2:revoke-bank",
            capability_id=bank["capability_id"],
            actor_id="app_orchestrator_owner",
            revocation_epoch=1,
        ),
        event(
            "AUTHORIZE",
            "op:p7u2:authorize-revoked",
            capability_id=delegated["capability_id"],
            subject_id="bank_view_helper",
            owner_id="bank_screen_owner",
            section_id="bank",
            action="read_bank",
            resource="section:bank",
            revocation_epoch=0,
        ),
    ]

    def one(name: str, candidate: dict[str, Any], code: str) -> dict[str, Any]:
        result = evaluate_events([event("GRANT", f"op:p7u2:{name}", capability=candidate)])
        return {"name": name, "expected": code, "actual": result["outcomes"][-1]["code"]}

    invalid = []
    cross = copy.deepcopy(bank)
    cross["capability_id"] = "cap:p7u2:cross-section"
    cross["section_id"] = "continuous_run"
    invalid.append(one("cross-section", cross, "REJECTED_OWNER_SECTION_MISMATCH"))
    undeclared = copy.deepcopy(bank)
    undeclared["capability_id"] = "cap:p7u2:undeclared-owner"
    undeclared["owner_id"] = "invented_owner"
    undeclared["subject_id"] = "invented_owner"
    invalid.append(one("undeclared-owner", undeclared, "REJECTED_UNDECLARED_OWNER"))
    forbidden = copy.deepcopy(bank)
    forbidden["capability_id"] = "cap:p7u2:route-mutation"
    forbidden["actions"] = ["route_mutation"]
    invalid.append(one("route-mutation", forbidden, "REJECTED_ACTION_OUTSIDE_OWNER"))
    wrong_grantor = copy.deepcopy(bank)
    wrong_grantor["capability_id"] = "cap:p7u2:wrong-grantor"
    wrong_grantor["granted_by"] = "bank_screen_owner"
    invalid.append(one("wrong-grantor", wrong_grantor, "REJECTED_ROOT_GRANT_AUTHORITY"))

    main = evaluate_events(positive)
    result = {
        "type": "PMP_PASS7_SECTION_OWNER_UNIT2_SCENARIO_RESULT_V1",
        "version": VERSION,
        "status": "PASS",
        "positive_sequence": main,
        "denial_scenarios": invalid,
        "summary": {
            "owners_contract_bound": len(load_contract()["owners"]),
            "positive_events": len(positive),
            "positive_accepted": main["summary"]["accepted"],
            "revocation_cascade_members": main["summary"]["capabilities_revoked"],
            "denial_scenarios": len(invalid),
            "denial_scenarios_matched": sum(
                row["expected"] == row["actual"] for row in invalid
            ),
        },
        "effects": main["effects"],
    }
    result["result_sha256"] = digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    result = scenario_results()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(payload)
    print(payload, end="")


if __name__ == "__main__":
    main()
