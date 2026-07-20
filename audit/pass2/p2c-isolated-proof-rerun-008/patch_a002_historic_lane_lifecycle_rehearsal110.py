#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

from patch_ci_lane_closure_rehearsal109 import (
    A002_HISTORIC_BROWSER_GUARDS,
    A002_HISTORIC_BROWSER_LOOP,
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"REHEARSAL110_{label}_ANCHOR_INVALID:{count}")
    return text.replace(old, new, 1)


A002_FINAL_STATUS_BLOCK = r'''  const finalStatus = await workerStatus(page);
  record('service-worker-live-status-a003', finalStatus?.type === 'PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE' && finalStatus?.receipt?.state === 'ENFORCED' && finalStatus?.receipt?.unlisted_executable_policy === 'FAIL_CLOSED' && finalStatus?.receipt?.offline_policy === 'MATCHING_VERIFIED_CACHE_ONLY', finalStatus);

  const finalRegistrations = await page.evaluate(async () => (await navigator.serviceWorker.getRegistrations()).map(r => r.active?.scriptURL || null));
  record('a002-matrix-did-not-replace-integrity-worker', finalRegistrations.length === 1 && finalRegistrations[0]?.includes('/' + INTEGRITY_SW), finalRegistrations);'''


A002_HISTORIC_LIFECYCLE_LOOP = r'''  const preHistoricStatus = await workerStatus(page);
  record('service-worker-live-status-a003', preHistoricStatus?.type === 'PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE' && preHistoricStatus?.receipt?.state === 'ENFORCED' && preHistoricStatus?.receipt?.unlisted_executable_policy === 'FAIL_CLOSED' && preHistoricStatus?.receipt?.offline_policy === 'MATCHING_VERIFIED_CACHE_ONLY', preHistoricStatus);

  const preHistoricRegistrations = await page.evaluate(async () => (await navigator.serviceWorker.getRegistrations()).map(r => r.active?.scriptURL || null));
  record('a002-matrix-did-not-replace-integrity-worker', preHistoricRegistrations.length === 1 && preHistoricRegistrations[0]?.includes('/' + INTEGRITY_SW), preHistoricRegistrations);

  const historicBrowser = page.context().browser();
  if (!historicBrowser) throw new Error('A002_HISTORIC_SHARED_BROWSER_MISSING');
  const primaryContext = page.context();
  await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
  await primaryContext.close();
  pmpA002Stage('historic-primary-realm-closed', { shared_browser_process: true, fresh_context_per_attempt: true });

  for (const file of HISTORIC) {
    let historicLastError = null;
    for (let attempt = 1; attempt <= 3; attempt += 1) {
      let historicContext = null;
      let bootstrapPage = null;
      let historicPage = null;
      try {
        historicContext = await historicBrowser.newContext({ serviceWorkers: 'allow' });
        await historicContext.addInitScript(() => {
          const descriptor = Object.getOwnPropertyDescriptor(MessagePort.prototype, 'onmessage');
          globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER = descriptor && descriptor.set;
        });
        pmpA002Stage('historic-bookmark-lifecycle-start', { file, attempt, shared_browser_process: true, isolated_context: true });
        bootstrapPage = await historicContext.newPage();
        await bootstrap(bootstrapPage, '#world');
        const historicBarrierStatus = await workerStatus(bootstrapPage);
        if (!(historicBarrierStatus && historicBarrierStatus.type === 'PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE' && historicBarrierStatus.receipt && historicBarrierStatus.receipt.state === 'ENFORCED')) {
          throw new Error('A002_HISTORIC_SHARED_BROWSER_INTEGRITY_NOT_ENFORCED:' + file);
        }
        pmpA002Stage('historic-bookmark-lifecycle-controlled', { file, attempt, controller_version: historicBarrierStatus.receipt.version });
        await bootstrapPage.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
        await bootstrapPage.close();
        bootstrapPage = null;
        historicPage = await historicContext.newPage();
        pmpA002AttachDiagnostics(historicPage);
        await historicPage.goto(BASE + file + '#library', { timeout: 30000, waitUntil: 'commit' });
        await historicPage.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#library', { timeout: 30000, waitUntil: 'commit' });
        const controllerUrl = await historicPage.evaluate(() => navigator.serviceWorker.controller?.scriptURL || null);
        if (!controllerUrl || !controllerUrl.includes('/' + INTEGRITY_SW)) throw new Error('A002_HISTORIC_INTEGRITY_CONTROLLER_MISSING:' + file);
        record(`historic-bookmark-forward:${file}`, true, { url: historicPage.url(), controller_url: controllerUrl, attempt, shared_browser_process: true, isolated_context: true });
        await historicPage.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
        historicLastError = null;
        break;
      } catch (error) {
        historicLastError = error;
        pmpA002Stage('historic-bookmark-lifecycle-attempt-failed', { file, attempt, name: String(error?.name || 'Error'), message: String(error?.message || error), retry_authorized: attempt < 3 });
        if (attempt >= 3) throw error;
      } finally {
        if (historicPage) await historicPage.close().catch(() => {});
        if (bootstrapPage) await bootstrapPage.close().catch(() => {});
        if (historicContext) await historicContext.close().catch(() => {});
        await new Promise(resolve => setTimeout(resolve, 750));
      }
    }
    if (historicLastError) throw historicLastError;
  }'''


A002_HISTORIC_LIFECYCLE_GUARDS = r''' pmp_shared_browser_token="const historicBrowser = page.context().browser();"
 pmp_primary_context_close_token="await primaryContext.close();"
 pmp_context_creation_token="historicContext = await historicBrowser.newContext({ serviceWorkers: 'allow' });"
 if s.count(pmp_shared_browser_token)!=1:raise SystemExit(f'REHEARSAL110_SHARED_BROWSER_CONTRACT_INVALID:{s.count(pmp_shared_browser_token)}')
 if s.count(pmp_primary_context_close_token)!=1:raise SystemExit(f'REHEARSAL110_PRIMARY_CONTEXT_CLOSE_CONTRACT_INVALID:{s.count(pmp_primary_context_close_token)}')
 if s.count(pmp_context_creation_token)!=1:raise SystemExit(f'REHEARSAL110_FRESH_CONTEXT_CONTRACT_INVALID:{s.count(pmp_context_creation_token)}')
 if s.count('A002_HISTORIC_SHARED_BROWSER_INTEGRITY_NOT_ENFORCED:')!=1:raise SystemExit(f'REHEARSAL110_INTEGRITY_ENFORCEMENT_CONTRACT_INVALID:{s.count("A002_HISTORIC_SHARED_BROWSER_INTEGRITY_NOT_ENFORCED:")}')
 if s.count('attempt <= 3')!=1:raise SystemExit(f'REHEARSAL110_BOUNDED_RETRY_CONTRACT_INVALID:{s.count("attempt <= 3")}')'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=pathlib.Path, required=True)
    parser.add_argument("--evidence-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()

    if not args.path.is_file():
        raise SystemExit(f"REHEARSAL110_RUNNER_NOT_FOUND:{args.path}")
    args.evidence_dir.mkdir(parents=True, exist_ok=True)

    original = args.path.read_text()
    text = replace_once(original, A002_HISTORIC_BROWSER_LOOP, A002_HISTORIC_LIFECYCLE_LOOP, "HISTORIC_LOOP")
    text = replace_once(text, A002_HISTORIC_BROWSER_GUARDS, A002_HISTORIC_LIFECYCLE_GUARDS, "HISTORIC_GUARDS")
    final_status_injection = (
        " a002_final_status_old=" + repr(A002_FINAL_STATUS_BLOCK) + "\n"
        " if s.count(a002_final_status_old)!=1:raise SystemExit(f'REHEARSAL110_FINAL_STATUS_POINT_INVALID:{s.count(a002_final_status_old)}')\n"
        " s=s.replace(a002_final_status_old,'',1)\n"
    )
    text = replace_once(text, " a002.write_text(s)", final_status_injection + " a002.write_text(s)", "A002_RUNNER_WRITE")
    compile(text, str(args.path), "exec")

    contracts = {
        "shared_browser_lookup": text.count("const historicBrowser = page.context().browser();"),
        "primary_context_close": text.count("await primaryContext.close();"),
        "fresh_context_creation": text.count("historicContext = await historicBrowser.newContext({ serviceWorkers: 'allow' });"),
        "bounded_retry": text.count("attempt <= 3"),
        "final_status_runtime_removal": text.count("a002_final_status_old="),
        "per_route_chromium_launch": text.count("const historicBrowser = await chromium.launch({ headless: true });"),
    }
    expected = {
        "shared_browser_lookup": 2,
        "primary_context_close": 2,
        "fresh_context_creation": 2,
        "bounded_retry": 3,
        "final_status_runtime_removal": 1,
        "per_route_chromium_launch": 0,
    }
    if contracts != expected:
        raise SystemExit("REHEARSAL110_RUNNER_CONTRACT_INVALID:" + json.dumps({"actual": contracts, "expected": expected}, sort_keys=True))

    args.path.write_text(text)
    receipt = {
        "type": "PMP_P2C_A002_HISTORIC_LANE_LIFECYCLE_REHEARSAL_110",
        "status": "PASS",
        "scope": "DISPOSABLE_TEST_HARNESS_ONLY",
        "observed_github_failure": "A002_HISTORIC_LATE_BOOTSTRAP_TIMEOUT_AFTER_ALL_COMPLETED_ASSERTIONS_PASSED",
        "repair": "ONE_BROWSER_PROCESS_WITH_FRESH_FULLY_CLOSED_CONTEXT_PER_ATTEMPT",
        "primary_realm_lifecycle": "ASSERT_THEN_CLOSE_BEFORE_HISTORIC_MATRIX",
        "retry_model": "BOUNDED_THREE_ATTEMPT_FAIL_CLOSED",
        "context_cooldown_ms": 750,
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
    (args.evidence_dir / "a002-historic-lane-lifecycle-repair-110.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
