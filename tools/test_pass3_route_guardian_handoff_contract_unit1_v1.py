#!/usr/bin/env python3
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "audit/pass3/pass3-route-guardian-handoff-contract-unit1-v1.json"
MAP = ROOT / "pmp-current-map-v12.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(contract, current_map, handoff):
    required = contract["required_fields"]
    if not isinstance(handoff, dict) or any(not handoff.get(k) for k in required):
        return False
    if handoff["type"] != contract["handoff_type"]:
        return False
    if handoff["source_role"] != contract["source_role"]:
        return False
    if handoff["destination_role"] != contract["destination_role"]:
        return False
    if handoff["map_path"] != contract["route_authority"]:
        return False
    if handoff["map_version"] != current_map["app_version"]:
        return False
    if handoff["route_epoch"] != current_map["route_epoch"]:
        return False
    return handoff["destination_path"] == current_map[contract["destination_role"]]["path"]


def canonical_handoff(contract, current_map):
    return {
        "type": contract["handoff_type"],
        "source_role": contract["source_role"],
        "destination_role": contract["destination_role"],
        "map_path": contract["route_authority"],
        "map_version": current_map["app_version"],
        "route_epoch": current_map["route_epoch"],
        "destination_path": current_map[contract["destination_role"]]["path"],
    }


def main():
    contract, current_map = load(CONTRACT), load(MAP)
    good = canonical_handoff(contract, current_map)
    assert validate(contract, current_map, good), "canonical handoff must pass"

    mutations = []
    for field in contract["required_fields"]:
        bad = copy.deepcopy(good)
        bad.pop(field)
        mutations.append((f"missing_{field}", bad))
    for field, value in (
        ("type", "OTHER"),
        ("source_role", "historic_guardian"),
        ("destination_role", "reload_owner"),
        ("map_path", "pmp-current-map-v11.json"),
        ("map_version", "stale"),
        ("route_epoch", "stale"),
        ("destination_path", "pmp-current-reload-owner-v27.html"),
    ):
        bad = copy.deepcopy(good)
        bad[field] = value
        mutations.append((f"wrong_{field}", bad))

    for name, bad in mutations:
        assert not validate(contract, current_map, bad), f"{name} must fail closed"

    assert contract["preservation"]["runtime_behavior_changed"] is False
    assert contract["preservation"]["persisted_user_data_changed"] is False
    print(f"PASS: 1 positive and {len(mutations)} fail-closed cases")


if __name__ == "__main__":
    main()
