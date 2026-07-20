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
        raise SystemExit(f"REHEARSAL107_RUNNER_NOT_FOUND:{args.path}")

    original = args.path.read_text()
    original_sha256 = sha256(original.encode())
    anchor = ''' if s.count("DOMStorage.domStorageItemUpdated")!=3:raise SystemExit(f'REHEARSAL105_DOMSTORAGE_UPDATED_EVENT_CONTRACT_INVALID:{s.count("DOMStorage.domStorageItemUpdated")}')
 a002.write_text(s)'''
    insert = r''' if s.count("DOMStorage.domStorageItemUpdated")!=3:raise SystemExit(f'REHEARSAL105_DOMSTORAGE_UPDATED_EVENT_CONTRACT_INVALID:{s.count("DOMStorage.domStorageItemUpdated")}')
 pmp_historic_loop_old="""  for (const file of HISTORIC) {
    await page.goto(BASE + file + '#library', { waitUntil: 'domcontentloaded' });
    await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#library', { timeout: 30000, waitUntil: 'domcontentloaded' });
    record(`historic-bookmark-forward:${file}`, true, { url: page.url() });
  }"""
 pmp_historic_loop_new="""  for (const file of HISTORIC) {
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
 if s.count(pmp_historic_loop_old)!=1:raise SystemExit(f'REHEARSAL107_HISTORIC_LOOP_ANCHOR_INVALID:{s.count(pmp_historic_loop_old)}')
 s=s.replace(pmp_historic_loop_old,pmp_historic_loop_new,1)
 if s.count('const historicPage = await page.context().newPage();')!=1:raise SystemExit(f'REHEARSAL107_ISOLATED_PAGE_CONTRACT_INVALID:{s.count("const historicPage = await page.context().newPage();")}')
 if s.count('A002_HISTORIC_INTEGRITY_CONTROLLER_MISSING:')!=1:raise SystemExit(f'REHEARSAL107_CONTROLLER_ASSERTION_CONTRACT_INVALID:{s.count("A002_HISTORIC_INTEGRITY_CONTROLLER_MISSING:")}')
 a002.write_text(s)'''

    if original.count(anchor) != 1:
        raise SystemExit(f"REHEARSAL107_RUNNER_ANCHOR_INVALID:{original.count(anchor)}")
    patched = original.replace(anchor, insert, 1)
    compile(patched, str(args.path), "exec")

    contracts = {
        "runner_patch_regression_harnesses": patched.count("def patch_regression_harnesses(root):"),
        "historic_loop_anchor_guard": patched.count("REHEARSAL107_HISTORIC_LOOP_ANCHOR_INVALID"),
        "isolated_page_contract_guard": patched.count("REHEARSAL107_ISOLATED_PAGE_CONTRACT_INVALID"),
        "controller_assertion_contract_guard": patched.count("REHEARSAL107_CONTROLLER_ASSERTION_CONTRACT_INVALID"),
        "isolated_page_creation": patched.count("const historicPage = await page.context().newPage();"),
        "controller_assertion": patched.count("A002_HISTORIC_INTEGRITY_CONTROLLER_MISSING:"),
    }
    expected = {
        "runner_patch_regression_harnesses": 1,
        "historic_loop_anchor_guard": 1,
        "isolated_page_contract_guard": 1,
        "controller_assertion_contract_guard": 1,
        "isolated_page_creation": 3,
        "controller_assertion": 3,
    }
    if contracts != expected:
        raise SystemExit(
            "REHEARSAL107_RUNNER_CONTRACT_INVALID:"
            + json.dumps({"actual": contracts, "expected": expected}, sort_keys=True)
        )

    args.path.write_text(patched)
    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence = {
        "type": "PMP_P2C_A002_HISTORIC_NAVIGATION_ISOLATION_REPAIR_107",
        "status": "PASS",
        "target": str(args.path),
        "original_sha256": original_sha256,
        "patched_sha256": sha256(args.path.read_bytes()),
        "scope": "DISPOSABLE_A002_REHEARSAL_HARNESS_ONLY",
        "observed_failure": "RESTORED_V29_TOP_LEVEL_REQUEST_NEVER_COMMITTED_AND_ENDED_NET_ERR_ABORTED_AT_TIMEOUT",
        "mechanism_inference": "SAME_PAGE_HISTORIC_NAVIGATION_LIFECYCLE_OVERLAPPED_CURRENT_OWNER_SUBRESOURCE_CHURN",
        "navigation_model_before": "ONE_REUSED_PAGE_FOR_ALL_HISTORIC_BOOKMARKS",
        "navigation_model_after": "ONE_FRESH_PAGE_PER_HISTORIC_BOOKMARK_IN_EXISTING_CONTEXT",
        "fresh_page_per_historic_route": True,
        "same_browser_context_preserved": True,
        "service_worker_controller_asserted_per_route": True,
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
    evidence_path = args.evidence_dir / "a002-historic-navigation-isolation-repair-107.json"
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
