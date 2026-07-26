#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"REHEARSAL115_{label}_ANCHOR_INVALID:{count}")
    return text.replace(old, new, 1)


OLD_ELIGIBILITY = (
    " return ('page.goto' in message or 'ERR_ABORTED' in message) and "
    "(name=='TimeoutError' or 'Timeout' in message or 'ERR_ABORTED' in message)"
)
NEW_ELIGIBILITY = (
    " return ('page.goto' in message or 'page.waitForURL' in message or "
    "'ERR_ABORTED' in message) and "
    "(name=='TimeoutError' or 'Timeout' in message or 'ERR_ABORTED' in message)"
)
OLD_MODEL = (
    "BOUNDED_ONE_FRESH_NODE_BROWSER_PROCESS_RETRY_FOR_ZERO_ASSERTION_FAILURE_"
    "PAGE_GOTO_TIMEOUT_ONLY"
)
NEW_MODEL = (
    "BOUNDED_ONE_FRESH_NODE_BROWSER_PROCESS_RETRY_FOR_ZERO_ASSERTION_FAILURE_"
    "NAVIGATION_TIMEOUT_ONLY"
)
OLD_REASON = "ZERO_ASSERTION_FAILURE_PAGE_GOTO_TIMEOUT"
NEW_REASON = "ZERO_ASSERTION_FAILURE_NAVIGATION_TIMEOUT"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=pathlib.Path, required=True)
    parser.add_argument("--evidence-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()

    if not args.path.is_file():
        raise SystemExit(f"REHEARSAL115_RUNNER_NOT_FOUND:{args.path}")
    args.evidence_dir.mkdir(parents=True, exist_ok=True)

    original = args.path.read_text()
    text = replace_once(
        original,
        OLD_ELIGIBILITY,
        NEW_ELIGIBILITY,
        "WAIT_FOR_URL_ELIGIBILITY",
    )
    text = replace_once(text, OLD_MODEL, NEW_MODEL, "RETRY_MODEL")
    text = replace_once(text, OLD_REASON, NEW_REASON, "RETRY_REASON")
    compile(text, str(args.path), "exec")

    contracts = {
        "bounded_attempt_tuple": text.count("for attempt in (1,2):"),
        "fresh_process_invocation": text.count(
            "command_result=run(f'{name}-attempt-{attempt}'"
        ),
        "zero_assertion_failure_gate": text.count(
            "payload.get('tests_failed')!=0"
        ),
        "positive_progress_gate": text.count(
            "payload.get('tests_passed')<=0"
        ),
        "page_goto_gate": text.count("'page.goto' in message"),
        "wait_for_url_gate": text.count("'page.waitForURL' in message"),
        "err_aborted_gate": text.count("'ERR_ABORTED' in message"),
        "bounded_lane_calls": text.count(
            "results.append(run_a002_with_bounded_fresh_process_retry("
        ),
        "attempt_limit": 2,
    }
    expected = {
        "bounded_attempt_tuple": 1,
        "fresh_process_invocation": 1,
        "zero_assertion_failure_gate": 1,
        "positive_progress_gate": 1,
        "page_goto_gate": 1,
        "wait_for_url_gate": 1,
        "err_aborted_gate": 2,
        "bounded_lane_calls": 2,
        "attempt_limit": 2,
    }
    if contracts != expected:
        raise SystemExit(
            "REHEARSAL115_RUNNER_CONTRACT_INVALID:"
            + json.dumps(
                {"actual": contracts, "expected": expected},
                sort_keys=True,
            )
        )

    args.path.write_text(text)
    receipt = {
        "type": "PMP_P2C_A002_BOUNDED_NAVIGATION_WAIT_RETRY_REHEARSAL_115",
        "status": "PASS",
        "scope": "DISPOSABLE_TEST_HARNESS_ONLY",
        "github_observation": (
            "ACTIVE_A002_PASSED_EIGHT_ASSERTIONS_BEFORE_NONDETERMINISTIC_"
            "WAITFORURL_TIMEOUT"
        ),
        "repair": (
            "INCLUDE_WAITFORURL_IN_EXISTING_BOUNDED_FRESH_PROCESS_"
            "NAVIGATION_TIMEOUT_RETRY"
        ),
        "retry_eligibility": (
            "NONZERO_PROGRESS_AND_ZERO_ASSERTION_FAILURES_AND_"
            "NAVIGATION_TIMEOUT_OR_ERR_ABORTED"
        ),
        "attempt_limit": 2,
        "fresh_process_per_attempt": True,
        "all_attempt_evidence_preserved": True,
        "assertions_weakened": False,
        "original_sha256": sha256(original.encode()),
        "patched_sha256": sha256(text.encode()),
        "contracts": contracts,
        "production_changed": False,
        "production_activation_authorized": False,
        "current_map_changed": False,
        "persisted_data_changed": False,
        "formal_proof_executed": False,
        "merge_authorized": False,
        "unknown_actor_policy_weakened": False,
        "unauthorized_capability_policy_weakened": False,
    }
    (
        args.evidence_dir
        / "a002-bounded-navigation-wait-retry-repair-115.json"
    ).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
