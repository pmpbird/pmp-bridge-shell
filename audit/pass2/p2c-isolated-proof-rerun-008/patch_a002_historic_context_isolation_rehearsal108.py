#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=pathlib.Path, required=True)
    parser.add_argument("--evidence-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()
    if not args.path.is_file():
        raise SystemExit(f"REHEARSAL108_RUNNER_NOT_FOUND:{args.path}")

    original = args.path.read_text()
    original_sha256 = sha256(original.encode())
    anchor = """ if s.count('A002_HISTORIC_INTEGRITY_CONTROLLER_MISSING:')!=1:raise SystemExit(f'REHEARSAL107_CONTROLLER_ASSERTION_CONTRACT_INVALID:{s.count("A002_HISTORIC_INTEGRITY_CONTROLLER_MISSING:")}')
 a002.write_text(s)"""
    insert = r''' if s.count('A002_HISTORIC_INTEGRITY_CONTROLLER_MISSING:')!=1:raise SystemExit(f'REHEARSAL107_CONTROLLER_ASSERTION_CONTRACT_INVALID:{s.count("A002_HISTORIC_INTEGRITY_CONTROLLER_MISSING:")}')
 pmp_historic_page_loop_old="""  for (const file of HISTORIC) {
    const historicPage = await page.context().newPage();
    pmpA002AttachDiagnostics(historicPage);
    try {
      pmpA002Stage('historic-bookmark-start', { file, isolated_page: true });
      await historicPage.goto(BASE + file + '#library', { timeout: 30000, waitUntil: 'domcontentloaded' });
      await historicPage.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#library', { timeout: 30000, waitUntil: 'domcontentloaded' });
      const controllerUrl = await historicPage.evaluate(() => navigator.serviceWorker.controller?.scriptURL || null);
      if (!controllerUrl || !controllerUrl.includes('/' + INTEGRITY_SW)) throw new Error('A002_HISTORIC_INTEGRITY_CONTROLLER_MISSING:' + file);
      record(`historic-bookmark-forward:${file}`, true, { url: historicPage.url(), controller_url: controllerUrl, isolated_page: true });
    } finally {
      await historicPage.close();
    }
  }"""
 pmp_historic_context_loop_new="""  for (const file of HISTORIC) {
    const browser = page.context().browser();
    if (!browser) throw new Error('A002_HISTORIC_BROWSER_MISSING:' + file);
    const historicContext = await browser.newContext({ serviceWorkers: 'allow' });
    await historicContext.addInitScript(() => {
      const descriptor = Object.getOwnPropertyDescriptor(MessagePort.prototype, 'onmessage');
      globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER = descriptor && descriptor.set;
    });
    let bootstrapPage = null;
    let historicPage = null;
    try {
      pmpA002Stage('historic-bookmark-context-start', { file, isolated_context: true });
      bootstrapPage = await historicContext.newPage();
      await bootstrap(bootstrapPage, '#world');
      const historicBarrierStatus = await workerStatus(bootstrapPage);
      if (!(historicBarrierStatus && historicBarrierStatus.type === 'PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE' && historicBarrierStatus.receipt && historicBarrierStatus.receipt.state === 'ENFORCED')) {
        throw new Error('A002_HISTORIC_CONTEXT_INTEGRITY_NOT_ENFORCED:' + file);
      }
      pmpA002Stage('historic-bookmark-context-controlled', { file, controller_version: historicBarrierStatus.receipt.version });
      await bootstrapPage.close();
      bootstrapPage = null;
      historicPage = await historicContext.newPage();
      pmpA002AttachDiagnostics(historicPage);
      await historicPage.goto(BASE + file + '#library', { timeout: 30000, waitUntil: 'domcontentloaded' });
      await historicPage.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#library', { timeout: 30000, waitUntil: 'domcontentloaded' });
      const controllerUrl = await historicPage.evaluate(() => navigator.serviceWorker.controller?.scriptURL || null);
      if (!controllerUrl || !controllerUrl.includes('/' + INTEGRITY_SW)) throw new Error('A002_HISTORIC_INTEGRITY_CONTROLLER_MISSING:' + file);
      record(`historic-bookmark-forward:${file}`, true, { url: historicPage.url(), controller_url: controllerUrl, isolated_context: true });
    } finally {
      if (bootstrapPage) await bootstrapPage.close().catch(() => {});
      await historicContext.close();
    }
  }"""
 if s.count(pmp_historic_page_loop_old)!=1:raise SystemExit(f'REHEARSAL108_HISTORIC_PAGE_LOOP_ANCHOR_INVALID:{s.count(pmp_historic_page_loop_old)}')
 s=s.replace(pmp_historic_page_loop_old,pmp_historic_context_loop_new,1)
 pmp_context_creation_token="const historicContext = await browser.newContext({ serviceWorkers: 'allow' });"
 if s.count(pmp_context_creation_token)!=1:raise SystemExit(f'REHEARSAL108_CONTEXT_CREATION_CONTRACT_INVALID:{s.count(pmp_context_creation_token)}')
 if s.count('A002_HISTORIC_CONTEXT_INTEGRITY_NOT_ENFORCED:')!=1:raise SystemExit(f'REHEARSAL108_CONTEXT_ENFORCEMENT_CONTRACT_INVALID:{s.count("A002_HISTORIC_CONTEXT_INTEGRITY_NOT_ENFORCED:")}')
 a002.write_text(s)'''

    if original.count(anchor) != 1:
        raise SystemExit(f"REHEARSAL108_RUNNER_ANCHOR_INVALID:{original.count(anchor)}")
    patched = original.replace(anchor, insert, 1)
    compile(patched, str(args.path), "exec")
    contracts = {
        "runner_patch_regression_harnesses": patched.count("def patch_regression_harnesses(root):"),
        "historic_page_loop_anchor_guard": patched.count("REHEARSAL108_HISTORIC_PAGE_LOOP_ANCHOR_INVALID"),
        "context_creation_contract_guard": patched.count("REHEARSAL108_CONTEXT_CREATION_CONTRACT_INVALID"),
        "context_enforcement_contract_guard": patched.count("REHEARSAL108_CONTEXT_ENFORCEMENT_CONTRACT_INVALID"),
        "historic_context_creation": patched.count("const historicContext = await browser.newContext({ serviceWorkers: 'allow' });"),
        "historic_context_enforcement": patched.count("A002_HISTORIC_CONTEXT_INTEGRITY_NOT_ENFORCED:"),
        "bootstrap_context_page_creation": patched.count("bootstrapPage = await historicContext.newPage();"),
        "historic_context_page_creation": patched.count("historicPage = await historicContext.newPage();"),
    }
    expected = {
        "runner_patch_regression_harnesses": 1,
        "historic_page_loop_anchor_guard": 1,
        "context_creation_contract_guard": 1,
        "context_enforcement_contract_guard": 1,
        "historic_context_creation": 2,
        "historic_context_enforcement": 3,
        "bootstrap_context_page_creation": 1,
        "historic_context_page_creation": 1,
    }
    if contracts != expected:
        raise SystemExit("REHEARSAL108_RUNNER_CONTRACT_INVALID:" + json.dumps({"actual": contracts, "expected": expected}, sort_keys=True))

    args.path.write_text(patched)
    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence = {
        "type": "PMP_P2C_A002_HISTORIC_BROWSER_CONTEXT_ISOLATION_REPAIR_108",
        "status": "PASS",
        "target": str(args.path),
        "original_sha256": original_sha256,
        "patched_sha256": sha256(args.path.read_bytes()),
        "scope": "DISPOSABLE_A002_REHEARSAL_HARNESS_ONLY",
        "run8_observation": "FRESH_PAGE_ISOLATION_SHIFTED_RESTORED_TIMEOUT_FROM_V29_TO_V28_WITHOUT_HTTP_REQUEST_OR_FRAME_COMMIT",
        "remaining_boundary": "SHARED_BROWSER_CONTEXT_AND_SERVICE_WORKER_LIFECYCLE",
        "navigation_model_before": "FRESH_PAGE_PER_ROUTE_IN_ONE_SHARED_INTEGRITY_CONTEXT",
        "navigation_model_after": "FRESH_BOOTSTRAPPED_INTEGRITY_CONTEXT_PER_HISTORIC_ROUTE",
        "fresh_integrity_context_per_historic_route": True,
        "bootstrap_page_closed_before_historic_navigation": True,
        "service_worker_status_enforced_before_route": True,
        "service_worker_controller_asserted_after_route": True,
        "lane_specific_conditional_added": False,
        "active_lane_retained_as_symmetric_regression_control": True,
        "production_runtime_changed": False,
        "current_map_changed": False,
        "actor_policy_changed": False,
        "unknown_actor_policy_weakened": False,
        "persisted_data_changed": False,
        "production_activation_authorized": False,
        "formal_proof_executed": False,
        "contracts": contracts,
    }
    (args.evidence_dir / "a002-historic-browser-context-isolation-repair-108.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
