#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

from patch_a002_historic_lane_lifecycle_rehearsal110 import (
    A002_HISTORIC_LIFECYCLE_GUARDS,
    A002_HISTORIC_LIFECYCLE_LOOP,
)
from patch_ci_lane_closure_rehearsal109 import A003_SCREEN_LOOP_NEW


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"REHEARSAL111_{label}_ANCHOR_INVALID:{count}")
    return text.replace(old, new, 1)


A002_SINGLE_CONTEXT_HISTORIC_LOOP = r'''  const preHistoricStatus = await workerStatus(page);
  record('service-worker-live-status-a003', preHistoricStatus?.type === 'PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE' && preHistoricStatus?.receipt?.state === 'ENFORCED' && preHistoricStatus?.receipt?.unlisted_executable_policy === 'FAIL_CLOSED' && preHistoricStatus?.receipt?.offline_policy === 'MATCHING_VERIFIED_CACHE_ONLY', preHistoricStatus);

  const preHistoricRegistrations = await page.evaluate(async () => (await navigator.serviceWorker.getRegistrations()).map(r => r.active?.scriptURL || null));
  record('a002-matrix-did-not-replace-integrity-worker', preHistoricRegistrations.length === 1 && preHistoricRegistrations[0]?.includes('/' + INTEGRITY_SW), preHistoricRegistrations);

  const historicBrowser = page.context().browser();
  if (!historicBrowser) throw new Error('A002_HISTORIC_SHARED_BROWSER_MISSING');
  const primaryContext = page.context();
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
  await primaryContext.close();
  pmpA002Stage('historic-primary-realm-closed', { shared_browser_process: true, one_verified_historic_context: true });

  const historicContext = await historicBrowser.newContext({ serviceWorkers: 'allow' });
  await historicContext.addInitScript(() => {
    const descriptor = Object.getOwnPropertyDescriptor(MessagePort.prototype, 'onmessage');
    globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER = descriptor && descriptor.set;
  });
  let bootstrapPage = null;
  try {
    bootstrapPage = await historicContext.newPage();
    pmpA002Stage('historic-shared-context-bootstrap-start', { shared_browser_process: true, one_verified_historic_context: true });
    await bootstrap(bootstrapPage, '#world');
    const historicBarrierStatus = await workerStatus(bootstrapPage);
    if (!(historicBarrierStatus && historicBarrierStatus.type === 'PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE' && historicBarrierStatus.receipt && historicBarrierStatus.receipt.state === 'ENFORCED')) {
      throw new Error('A002_HISTORIC_SHARED_CONTEXT_INTEGRITY_NOT_ENFORCED');
    }
    await bootstrapPage.waitForLoadState('networkidle', { timeout: 15000 });
    pmpA002Stage('historic-shared-context-controlled', { controller_version: historicBarrierStatus.receipt.version });
    await bootstrapPage.close();
    bootstrapPage = null;

    for (const file of HISTORIC) {
      let historicLastError = null;
      for (let attempt = 1; attempt <= 3; attempt += 1) {
        let historicPage = null;
        try {
          historicPage = await historicContext.newPage();
          pmpA002AttachDiagnostics(historicPage);
          pmpA002Stage('historic-bookmark-shared-context-start', { file, attempt, shared_browser_process: true, one_verified_historic_context: true, fresh_page: true });
          await historicPage.goto(BASE + file + '#library', { timeout: 30000, waitUntil: 'commit' });
          await historicPage.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#library', { timeout: 30000, waitUntil: 'commit' });
          const controllerUrl = await historicPage.evaluate(() => navigator.serviceWorker.controller?.scriptURL || null);
          if (!controllerUrl || !controllerUrl.includes('/' + INTEGRITY_SW)) throw new Error('A002_HISTORIC_INTEGRITY_CONTROLLER_MISSING:' + file);
          await historicPage.waitForLoadState('networkidle', { timeout: 15000 });
          record(`historic-bookmark-forward:${file}`, true, { url: historicPage.url(), controller_url: controllerUrl, attempt, shared_browser_process: true, one_verified_historic_context: true, fresh_page: true });
          historicLastError = null;
          break;
        } catch (error) {
          historicLastError = error;
          pmpA002Stage('historic-bookmark-shared-context-attempt-failed', { file, attempt, name: String(error?.name || 'Error'), message: String(error?.message || error), retry_authorized: attempt < 3 });
          if (attempt >= 3) throw error;
        } finally {
          if (historicPage) await historicPage.close().catch(() => {});
          await new Promise(resolve => setTimeout(resolve, 250));
        }
      }
      if (historicLastError) throw historicLastError;
    }
  } finally {
    if (bootstrapPage) await bootstrapPage.close().catch(() => {});
    await historicContext.close().catch(() => {});
  }'''


A002_SINGLE_CONTEXT_HISTORIC_GUARDS = r''' pmp_shared_browser_token="const historicBrowser = page.context().browser();"
 pmp_primary_context_close_token="await primaryContext.close();"
 pmp_single_context_creation_token="const historicContext = await historicBrowser.newContext({ serviceWorkers: 'allow' });"
 pmp_fresh_page_token="historicPage = await historicContext.newPage();"
 if s.count(pmp_shared_browser_token)!=1:raise SystemExit(f'REHEARSAL111_SHARED_BROWSER_CONTRACT_INVALID:{s.count(pmp_shared_browser_token)}')
 if s.count(pmp_primary_context_close_token)!=1:raise SystemExit(f'REHEARSAL111_PRIMARY_CONTEXT_CLOSE_CONTRACT_INVALID:{s.count(pmp_primary_context_close_token)}')
 if s.count(pmp_single_context_creation_token)!=1:raise SystemExit(f'REHEARSAL111_SINGLE_HISTORIC_CONTEXT_CONTRACT_INVALID:{s.count(pmp_single_context_creation_token)}')
 if s.count(pmp_fresh_page_token)!=1:raise SystemExit(f'REHEARSAL111_FRESH_PAGE_CONTRACT_INVALID:{s.count(pmp_fresh_page_token)}')
 if s.count('A002_HISTORIC_SHARED_CONTEXT_INTEGRITY_NOT_ENFORCED')!=1:raise SystemExit(f'REHEARSAL111_INTEGRITY_ENFORCEMENT_CONTRACT_INVALID:{s.count("A002_HISTORIC_SHARED_CONTEXT_INTEGRITY_NOT_ENFORCED")}')
 if s.count('attempt <= 3')!=1:raise SystemExit(f'REHEARSAL111_A002_BOUNDED_RETRY_CONTRACT_INVALID:{s.count("attempt <= 3")}')'''


A003_REUSED_CONTEXT_SCREEN_LOOP = r'''    await page.close();
    page = null;
    for (const screen of SCREENS) {
      let screenLastError = null;
      for (let attempt = 1; attempt <= 2; attempt += 1) {
        try {
          page = await bootstrap(context, '#' + screen);
          const home = await openCurrentFromGuardian(page, screen);
          const homeState = await historicalReceiptFromHomeFrame(page);
          const homeReceipt = homeState.receipt;
          await page.waitForLoadState('networkidle', { timeout:15000 });
          record(`integrity-current-chain-home:${screen}`, home.reached && home.hash_matches, {expected:home.expected_hash, actual:home.actual_hash, home_url:home.home_url, frame_urls:home.urls.slice(-8), reused_verified_context:true, attempt});
          const receiptLabel = homeState.evidence_source === 'direct_canonical_manifest_route_binding' ? 'direct-current-sha256-pass' : 'historical-home-sha256-pass';
          record(`${receiptLabel}:${screen}`, homeReceipt.verification === 'PASS' && homeReceipt.expected_sha256 === homeReceipt.actual_sha256, {expected:homeReceipt.expected_sha256, actual:homeReceipt.actual_sha256, status:homeReceipt.status, evidence_source:homeState.evidence_source, frame_url:homeState.url, frame_body:homeState.body, reused_verified_context:true, attempt});
          screenLastError = null;
          break;
        } catch (error) {
          screenLastError = error;
          console.log(`A003_SCREEN_ATTEMPT_FAILED ${JSON.stringify({screen,attempt,name:String(error?.name||'Error'),message:String(error?.message||error),retry_authorized:attempt<2})}`);
          if (attempt >= 2) throw error;
        } finally {
          if (page) await page.close().catch(() => {});
          page = null;
          await new Promise(resolve => setTimeout(resolve, 250));
        }
      }
      if (screenLastError) throw screenLastError;
    }

    page = await bootstrap(context, '#control');'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=pathlib.Path, required=True)
    parser.add_argument("--evidence-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()

    if not args.path.is_file():
        raise SystemExit(f"REHEARSAL111_RUNNER_NOT_FOUND:{args.path}")
    args.evidence_dir.mkdir(parents=True, exist_ok=True)

    original = args.path.read_text()
    text = replace_once(original, A002_HISTORIC_LIFECYCLE_LOOP, A002_SINGLE_CONTEXT_HISTORIC_LOOP, "A002_HISTORIC_LOOP")
    text = replace_once(text, A002_HISTORIC_LIFECYCLE_GUARDS, A002_SINGLE_CONTEXT_HISTORIC_GUARDS, "A002_HISTORIC_GUARDS")
    a003_assignment_old = " a003_screen_loop_new=" + repr(A003_SCREEN_LOOP_NEW)
    a003_assignment_new = " a003_screen_loop_new=" + repr(A003_REUSED_CONTEXT_SCREEN_LOOP)
    text = replace_once(text, a003_assignment_old, a003_assignment_new, "A003_SCREEN_LOOP")
    compile(text, str(args.path), "exec")

    contracts = {
        "a002_single_historic_context": text.count("const historicContext = await historicBrowser.newContext({ serviceWorkers: 'allow' });"),
        "a002_fresh_page": text.count("historicPage = await historicContext.newPage();"),
        "a002_retry_three": text.count("attempt <= 3"),
        "a002_per_attempt_context": text.count("\n        historicContext = await historicBrowser.newContext({ serviceWorkers: 'allow' });"),
        "a003_reused_context_bootstrap": text.count("page = await bootstrap(context, '#' + screen);"),
        "a003_retry_two": text.count("attempt <= 2"),
        "a003_fresh_screen_context": text.count("const screenContext = await browser.newContext({ serviceWorkers:'allow' });"),
    }
    expected = {
        "a002_single_historic_context": 2,
        "a002_fresh_page": 2,
        "a002_retry_three": 3,
        "a002_per_attempt_context": 0,
        "a003_reused_context_bootstrap": 2,
        "a003_retry_two": 1,
        "a003_fresh_screen_context": 0,
    }
    if contracts != expected:
        raise SystemExit("REHEARSAL111_RUNNER_CONTRACT_INVALID:" + json.dumps({"actual": contracts, "expected": expected}, sort_keys=True))

    args.path.write_text(text)
    receipt = {
        "type": "PMP_P2C_CI_LANE_LIFECYCLE_REHEARSAL_111",
        "status": "PASS",
        "scope": "DISPOSABLE_TEST_HARNESS_ONLY",
        "github_observation": "FRESH_SERVICE_WORKER_CONTEXT_CHURN_PRECEDED_ABORTED_NAVIGATION",
        "a002_repair": "ONE_VERIFIED_HISTORIC_CONTEXT_WITH_FRESH_PAGE_PER_ROUTE",
        "a003_repair": "REUSE_VERIFIED_CONTEXT_WITH_FRESH_PAGE_PER_SCREEN",
        "a002_retry_model": "BOUNDED_THREE_ATTEMPT_FAIL_CLOSED",
        "a003_retry_model": "BOUNDED_TWO_ATTEMPT_FAIL_CLOSED",
        "navigation_quiescence_required_before_assertion": True,
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
    (args.evidence_dir / "ci-lane-lifecycle-repair-111.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
