#!/usr/bin/env python3
"""Corrected adversarial harness for the scalable applicability gate verifier."""
from __future__ import annotations

import copy
import verify_packet_01_5_scalable_applicability_gate_v1 as base


def corrected_adversarial_tests(gate, records):
    tests = []

    def mutate():
        item = copy.deepcopy(gate)
        tests.append(item)
        return item

    mutate()["window_contract"]["maximum_records"] = 2750
    mutate()["window_contract"]["new_gate_required_per_window"] = True
    mutate()["window_contract"]["first_authorized_window"]["records"] = 4
    mutate()["window_contract"]["first_authorized_window"]["last_address"] = "P01.5::B::0004"
    mutate()["decision_eligibility"]["unknown_hold_requires_completed_evidence_attempt"] = False
    mutate()["decision_eligibility"]["unresolved_without_completed_evidence_attempt"] = "UNKNOWN — HOLD"
    mutate()["decision_eligibility"]["old_labels_are_not_evidence"] = False
    mutate()["decision_eligibility"]["supersession_requires_stronger_current_evidence"] = False
    mutate()["evidence_acquisition_queues"]["required_for_every_undecided_record"] = False
    mutate()["evidence_acquisition_queues"]["preserve_source_order"] = False
    mutate()["pass_outputs"]["coverage_rule"] = "PARTIAL_COVERAGE_ALLOWED"
    mutate()["prohibited_work"]["routing"] = False
    mutate()["prohibited_work"]["implementation"] = False
    mutate()["prohibited_work"]["packet_04"] = False
    candidate = mutate()
    candidate["gate_verifier"] = candidate["gate_author"]
    mutate()["source_inventory"]["sha256"] = "0" * 64

    rejected = 0
    for candidate in tests:
        try:
            base.validate_gate(candidate, records)
        except base.GateError:
            rejected += 1
    base.require(rejected == len(tests), "an adversarial gate mutation passed")
    return rejected


base.adversarial_tests = corrected_adversarial_tests

if __name__ == "__main__":
    try:
        base.main()
    except base.GateError as exc:
        raise SystemExit(f"FAIL: {exc}")
