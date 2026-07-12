#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from urllib.parse import urljoin

from playwright.async_api import async_playwright

BASE_URL = os.environ.get("P2B_BASE_URL", "http://127.0.0.1:8000/")
OUTPUT = Path(os.environ.get("P2B_RESULT_PATH", "/tmp/pass2-p2b-browser-result.json"))
FIXTURE_PATH = "audit/pass2/p2b-forbidden-action-fixture.html?pmp_p2b_fixture=1"


async def main() -> int:
    unexpected_requests: list[str] = []
    page_errors: list[str] = []
    fixture_url = urljoin(BASE_URL, FIXTURE_PATH)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(service_workers="block")
        page = await context.new_page()

        def on_request(request):
            url = request.url
            if "should-never-request-p2b" in url or "p2b-unknown-never-execute.js" in url:
                unexpected_requests.append(url)

        page.on("request", on_request)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        response = await page.goto(fixture_url, wait_until="domcontentloaded", timeout=60_000)
        if response is None or not response.ok:
            raise RuntimeError(f"Fixture did not load: {response and response.status}")
        await page.wait_for_function("window.PMP_P2B_FIXTURE_RESULT !== undefined", timeout=60_000)
        result = await page.evaluate("window.PMP_P2B_FIXTURE_RESULT")
        ledger = await page.evaluate("window.PMPPass2ActorAuthorizationGateV1.quarantineLedger()")
        report = await page.evaluate("window.PMPPass2ActorAuthorizationGateV1.report()")
        marker = await page.evaluate("window.__PMP_P2B_REGISTERED_MARKER__ || null")
        await browser.close()

    events = ledger.get("events", []) if isinstance(ledger, dict) else []
    codes = sorted({event.get("code") for event in events if event.get("code")})
    checks = {
        "fixture_status_pass": result.get("status") == "PASS",
        "fixture_14_of_14": result.get("tests_passed") == 14 and result.get("tests_failed") == 0,
        "no_forbidden_network_request": not unexpected_requests,
        "no_uncaught_page_error": not page_errors,
        "registered_marker_executed": bool(marker),
        "gate_enforced_and_sealed": report.get("enforced") is True and report.get("bootstrap_sealed") is True,
        "quarantine_has_denials": len(events) >= 9,
        "every_denial_pre_effect": all(event.get("side_effect_executed") is False for event in events),
        "unknown_actor_recorded": "P2_UNKNOWN_ACTOR" in codes,
        "capability_denial_recorded": "P2_CAPABILITY_DENIED" in codes,
        "global_forbidden_recorded": "P2_CAPABILITY_GLOBALLY_FORBIDDEN" in codes,
        "pass2_not_falsely_closed": report.get("pass2_complete") is False,
        "pass3_not_started": report.get("pass3_started") is False,
    }
    failed = [name for name, passed in checks.items() if not passed]
    aggregate = {
        "type": "PMP_PASS2_P2B_ADVERSARIAL_BROWSER_RESULT_V1",
        "status": "PASS" if not failed else "FAIL",
        "tests_passed": sum(1 for passed in checks.values() if passed),
        "tests_failed": len(failed),
        "checks": checks,
        "failed_checks": failed,
        "fixture_result": result,
        "gate_report": report,
        "quarantine_event_count": len(events),
        "quarantine_codes": codes,
        "unexpected_requests": unexpected_requests,
        "page_errors": page_errors,
        "pass2_complete": False,
        "pass3_started": False,
    }
    OUTPUT.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n", "utf-8")
    print(json.dumps(aggregate, indent=2, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
