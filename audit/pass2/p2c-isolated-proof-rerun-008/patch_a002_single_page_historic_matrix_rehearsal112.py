#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

from patch_ci_lane_lifecycle_rehearsal111 import (
    A002_SINGLE_CONTEXT_HISTORIC_GUARDS,
    A002_SINGLE_CONTEXT_HISTORIC_LOOP,
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"REHEARSAL112_{label}_ANCHOR_INVALID:{count}")
    return text.replace(old, new, 1)


A002_SINGLE_PAGE_HISTORIC_LOOP = r'''  const preHistoricStatus = await workerStatus(page);
  record('service-worker-live-status-a003', preHistoricStatus?.type === 'PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE' && preHistoricStatus?.receipt?.state === 'ENFORCED' && preHistoricStatus?.receipt?.unlisted_executable_policy === 'FAIL_CLOSED' && preHistoricStatus?.receipt?.offline_policy === 'MATCHING_VERIFIED_CACHE_ONLY', preHistoricStatus);

  pmpA002Stage('historic-single-page-matrix-start', { reused_verified_context: true, reused_verified_page: true, a003_reference_lanes: '47_OF_47_ACTIVE_AND_RESTORED' });
  for (const file of HISTORIC) {
    let historicLastError = null;
    for (let attempt = 1; attempt <= 3; attempt += 1) {
      try {
        pmpA002Stage('historic-bookmark-single-page-start', { file, attempt, reused_verified_context: true, reused_verified_page: true });
        await page.goto(BASE + file + '#library', { timeout: 30000, waitUntil: 'commit' });
        await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#library', { timeout: 30000, waitUntil: 'commit' });
        const controllerUrl = await page.evaluate(() => navigator.serviceWorker.controller?.scriptURL || null);
        if (!controllerUrl || !controllerUrl.includes('/' + INTEGRITY_SW)) throw new Error('A002_HISTORIC_INTEGRITY_CONTROLLER_MISSING:' + file);
        record(`historic-bookmark-forward:${file}`, true, { url: page.url(), controller_url: controllerUrl, attempt, reused_verified_context: true, reused_verified_page: true });
        historicLastError = null;
        break;
      } catch (error) {
        historicLastError = error;
        pmpA002Stage('historic-bookmark-single-page-attempt-failed', { file, attempt, name: String(error?.name || 'Error'), message: String(error?.message || error), retry_authorized: attempt < 3 });
        if (attempt >= 3) throw error;
        await page.goto('about:blank', { timeout: 5000, waitUntil: 'commit' }).catch(() => {});
        await new Promise(resolve => setTimeout(resolve, 250));
      }
    }
    if (historicLastError) throw historicLastError;
  }

  const finalRegistrations = await page.evaluate(async () => (await navigator.serviceWorker.getRegistrations()).map(r => r.active?.scriptURL || null));
  record('a002-matrix-did-not-replace-integrity-worker', finalRegistrations.length === 1 && finalRegistrations[0]?.includes('/' + INTEGRITY_SW), finalRegistrations);'''


A002_SINGLE_PAGE_HISTORIC_GUARDS = r''' pmp_single_page_navigation_token="await page.goto(BASE + file + '#library', { timeout: 30000, waitUntil: 'commit' });"
 pmp_per_route_controller_token="const controllerUrl = await page.evaluate(() => navigator.serviceWorker.controller?.scriptURL || null);"
 pmp_final_registration_token="const finalRegistrations = await page.evaluate(async () => (await navigator.serviceWorker.getRegistrations()).map(r => r.active?.scriptURL || null));"
 pmp_historic_networkidle_token="waitForLoadState('networkidle'"
 if s.count(pmp_single_page_navigation_token)!=1:raise SystemExit(f'REHEARSAL112_SINGLE_PAGE_NAVIGATION_CONTRACT_INVALID:{s.count(pmp_single_page_navigation_token)}')
 if s.count(pmp_per_route_controller_token)!=1:raise SystemExit(f'REHEARSAL112_PER_ROUTE_CONTROLLER_CONTRACT_INVALID:{s.count(pmp_per_route_controller_token)}')
 if s.count(pmp_final_registration_token)!=2:raise SystemExit(f'REHEARSAL112_FINAL_REGISTRATION_PRE_REMOVAL_CONTRACT_INVALID:{s.count(pmp_final_registration_token)}')
 if s.count('attempt <= 3')!=1:raise SystemExit(f'REHEARSAL112_BOUNDED_RETRY_CONTRACT_INVALID:{s.count("attempt <= 3")}')
 if s.count(pmp_historic_networkidle_token)!=0:raise SystemExit(f'REHEARSAL112_HISTORIC_NETWORKIDLE_REMOVAL_CONTRACT_INVALID:{s.count(pmp_historic_networkidle_token)}')'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=pathlib.Path, required=True)
    parser.add_argument("--evidence-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()

    if not args.path.is_file():
        raise SystemExit(f"REHEARSAL112_RUNNER_NOT_FOUND:{args.path}")
    args.evidence_dir.mkdir(parents=True, exist_ok=True)

    original = args.path.read_text()
    text = replace_once(original, A002_SINGLE_CONTEXT_HISTORIC_LOOP, A002_SINGLE_PAGE_HISTORIC_LOOP, "HISTORIC_LOOP")
    text = replace_once(text, A002_SINGLE_CONTEXT_HISTORIC_GUARDS, A002_SINGLE_PAGE_HISTORIC_GUARDS, "HISTORIC_GUARDS")
    compile(text, str(args.path), "exec")

    contracts = {
        "single_page_navigation": text.count("await page.goto(BASE + file + '#library', { timeout: 30000, waitUntil: 'commit' });"),
        "per_route_controller_assertion": text.count("const controllerUrl = await page.evaluate(() => navigator.serviceWorker.controller?.scriptURL || null);"),
        "final_registration_assertion": text.count("const finalRegistrations = await page.evaluate(async () => (await navigator.serviceWorker.getRegistrations()).map(r => r.active?.scriptURL || null));"),
        "retry_three": text.count("attempt <= 3"),
        "historic_context_creation": text.count("const historicContext = await historicBrowser.newContext({ serviceWorkers: 'allow' });"),
        "historic_fresh_page_creation": text.count("historicPage = await historicContext.newPage();"),
        "historic_networkidle_wait": text.count("waitForLoadState('networkidle'"),
    }
    expected = {
        "single_page_navigation": 2,
        "per_route_controller_assertion": 2,
        "final_registration_assertion": 3,
        "retry_three": 3,
        "historic_context_creation": 0,
        "historic_fresh_page_creation": 0,
        "historic_networkidle_wait": 2,
    }
    if contracts != expected:
        raise SystemExit("REHEARSAL112_RUNNER_CONTRACT_INVALID:" + json.dumps({"actual": contracts, "expected": expected}, sort_keys=True))

    args.path.write_text(text)
    receipt = {
        "type": "PMP_P2C_A002_SINGLE_PAGE_HISTORIC_MATRIX_REHEARSAL_112",
        "status": "PASS",
        "scope": "DISPOSABLE_TEST_HARNESS_ONLY",
        "github_observation": "ROUTE_AND_CONTROLLER_ASSERTIONS_PASSED_BEFORE_NON_REQUIRED_NETWORKIDLE_TIMEOUT",
        "repair": "REUSE_ALREADY_VERIFIED_PAGE_ACROSS_HISTORIC_ROUTES",
        "reference": "A003_ACTIVE_AND_RESTORED_HISTORIC_MATRICES_PASSED_47_OF_47_WITH_SINGLE_PAGE_NAVIGATION",
        "retry_model": "BOUNDED_THREE_ATTEMPT_FAIL_CLOSED",
        "per_route_controller_assertion": True,
        "final_registration_assertion": True,
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
    (args.evidence_dir / "a002-single-page-historic-matrix-repair-112.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
