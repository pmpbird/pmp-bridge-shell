#!/usr/bin/env python3
import argparse
import hashlib
import json
import pathlib


p = argparse.ArgumentParser()
p.add_argument('--path', required=True)
p.add_argument('--evidence-dir', required=True)
a = p.parse_args()

path = pathlib.Path(a.path)
evidence_dir = pathlib.Path(a.evidence_dir)
evidence_dir.mkdir(parents=True, exist_ok=True)
if not path.is_file():
    raise SystemExit(f'REHEARSAL105_RUNNER_NOT_FOUND:{path}')

original = path.read_text()
original_sha256 = hashlib.sha256(original.encode()).hexdigest()

anchor = """ if s.count('pmpA002PollPage(')!=7:raise SystemExit(f'REHEARSAL104_POLL_CALL_CONTRACT_INVALID:{s.count(\"pmpA002PollPage(\")}')
 a002.write_text(s)"""
insert = r''' if s.count('pmpA002PollPage(')!=7:raise SystemExit(f'REHEARSAL104_POLL_CALL_CONTRACT_INVALID:{s.count("pmpA002PollPage(")}')
 pmp_cdp_helper_anchor="async function bootstrap(page, hash) {"
 pmp_cdp_helper="""async function pmpA002ArmReloadReceipt(page, expectedHash, options = {}) {
  const timeout = Number(options.timeout || 30000);
  const receiptKey = 'pmp_reload_current_canonical_v1_receipt';
  const expectedOrigin = new URL(BASE).origin;
  const storageId = { securityOrigin: expectedOrigin, isLocalStorage: true };
  const client = await page.context().newCDPSession(page);
  const observed = {
    event_count: 0,
    matching_key_event_count: 0,
    last_event: null,
    initial_read_error: null,
  };
  let settled = false;
  let timer = null;
  let resolveObservation;
  const promise = new Promise(resolve => { resolveObservation = resolve; });

  const sanitizeReceipt = receipt => receipt && typeof receipt === 'object' ? {
    type: receipt.type || null,
    status: receipt.status || null,
    source: receipt.source || null,
    page: receipt.page || null,
    target_role: receipt.target_role || null,
    target_path: receipt.target_path || null,
    map_path: receipt.map_path || null,
    map_version: receipt.map_version || null,
    route_epoch: receipt.route_epoch || null,
  } : null;

  const finish = (receipt, observationSource) => {
    if (settled) return;
    settled = true;
    if (timer) clearTimeout(timer);
    client.off('DOMStorage.domStorageItemAdded', onAdded);
    client.off('DOMStorage.domStorageItemUpdated', onUpdated);
    resolveObservation({ receipt, observation_source: observationSource, observed });
  };

  const observe = (event, observationSource) => {
    observed.event_count += 1;
    const eventStorageId = event && event.storageId || {};
    const eventOrigin = String(eventStorageId.securityOrigin || '');
    observed.last_event = {
      source: observationSource,
      key: event && event.key || null,
      is_local_storage: eventStorageId.isLocalStorage === true,
      security_origin: eventOrigin || null,
    };
    if (!event || event.key !== receiptKey) return;
    observed.matching_key_event_count += 1;
    if (eventStorageId.isLocalStorage !== true) return;
    if (eventOrigin && eventOrigin !== expectedOrigin) return;
    let receipt = null;
    try {
      receipt = JSON.parse(event.newValue);
    } catch (error) {
      observed.last_event.parse_error = String(error && error.message || error);
      return;
    }
    observed.last_event.receipt = sanitizeReceipt(receipt);
    if (
      receipt &&
      receipt.type === 'PMP_RELOAD_CURRENT_CANONICAL_V1_RECEIPT' &&
      receipt.status === 'MAP_CURRENT_APP_HANDOFF_READY' &&
      receipt.source === 'a002-a003-compatible-live' &&
      receipt.page === expectedHash &&
      receipt.target_role === 'current_app' &&
      receipt.map_path === 'pmp-current-map-v12.json'
    ) finish(receipt, observationSource);
  };

  const onAdded = event => observe(event, 'DOMStorage.domStorageItemAdded');
  const onUpdated = event => observe(event, 'DOMStorage.domStorageItemUpdated');
  client.on('DOMStorage.domStorageItemAdded', onAdded);
  client.on('DOMStorage.domStorageItemUpdated', onUpdated);

  try {
    await client.send('DOMStorage.enable');
    const response = await client.send('DOMStorage.getDOMStorageItems', { storageId });
    const entry = (response.entries || []).find(row => row[0] === receiptKey);
    if (entry) observe({ storageId, key: receiptKey, newValue: entry[1] }, 'DOMStorage.initialSnapshot');
  } catch (error) {
    observed.initial_read_error = String(error && error.message || error);
  }

  if (!settled) timer = setTimeout(() => finish(null, 'timeout'), timeout);
  return {
    promise,
    async dispose() {
      finish(null, 'disposed');
      await client.detach().catch(() => {});
    },
  };
}
"""
 if s.count(pmp_cdp_helper_anchor)!=1:raise SystemExit(f'REHEARSAL105_CDP_HELPER_ANCHOR_INVALID:{s.count(pmp_cdp_helper_anchor)}')
 s=s.replace(pmp_cdp_helper_anchor,pmp_cdp_helper+pmp_cdp_helper_anchor,1)
 pmp_reload_observation_old="""    await page.evaluate(async s => {
      await window.PMPReloadCurrentCanonicalV1.reload(null, { source: 'a002-a003-compatible-live', page: '#' + s, pressed_text: 'Reload Current' });
    }, screen).catch(() => {});
    await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === expectedHash, { timeout: 30000, waitUntil: 'domcontentloaded' });
    await pmpA002PollPage(page, () => {
      try {
        const r = JSON.parse(localStorage.getItem('pmp_reload_current_canonical_v1_receipt') || 'null');
        return r && r.status === 'MAP_CURRENT_APP_HANDOFF_READY';
      } catch { return false; }
    }, { timeout: 30000, label: 'reload-current-receipt' });
    const receipt = await page.evaluate(() => JSON.parse(localStorage.getItem('pmp_reload_current_canonical_v1_receipt')));"""
 pmp_reload_observation_new="""    const receiptObserver = await pmpA002ArmReloadReceipt(page, expectedHash, { timeout: 30000 });
    let receiptObservation = null;
    try {
      await page.evaluate(async s => {
        await window.PMPReloadCurrentCanonicalV1.reload(null, { source: 'a002-a003-compatible-live', page: '#' + s, pressed_text: 'Reload Current' });
      }, screen).catch(() => {});
      await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === expectedHash, { timeout: 30000, waitUntil: 'domcontentloaded' });
      receiptObservation = await receiptObserver.promise;
    } finally {
      await receiptObserver.dispose();
    }
    if (!receiptObservation || !receiptObservation.receipt) {
      throw new Error('A002_CDP_RECEIPT_EVENT_TIMEOUT:reload-current-receipt:' + JSON.stringify(receiptObservation && receiptObservation.observed || {}));
    }
    const receipt = receiptObservation.receipt;"""
 if s.count(pmp_reload_observation_old)!=1:raise SystemExit(f'REHEARSAL105_RELOAD_OBSERVATION_POINT_INVALID:{s.count(pmp_reload_observation_old)}')
 s=s.replace(pmp_reload_observation_old,pmp_reload_observation_new,1)
 if s.count('pmpA002ArmReloadReceipt(')!=2:raise SystemExit(f'REHEARSAL105_CDP_RECEIPT_CALL_CONTRACT_INVALID:{s.count("pmpA002ArmReloadReceipt(")}')
 if s.count('pmpA002PollPage(')!=6:raise SystemExit(f'REHEARSAL105_PAGE_POLL_CALL_CONTRACT_INVALID:{s.count("pmpA002PollPage(")}')
 if s.count("DOMStorage.getDOMStorageItems")!=1:raise SystemExit(f'REHEARSAL105_DOMSTORAGE_CONTRACT_INVALID:{s.count("DOMStorage.getDOMStorageItems")}')
 if s.count("DOMStorage.domStorageItemAdded")!=3:raise SystemExit(f'REHEARSAL105_DOMSTORAGE_ADDED_EVENT_CONTRACT_INVALID:{s.count("DOMStorage.domStorageItemAdded")}')
 if s.count("DOMStorage.domStorageItemUpdated")!=3:raise SystemExit(f'REHEARSAL105_DOMSTORAGE_UPDATED_EVENT_CONTRACT_INVALID:{s.count("DOMStorage.domStorageItemUpdated")}')
 a002.write_text(s)'''

if original.count(anchor) != 1:
    raise SystemExit(f'REHEARSAL105_A002_WRITE_ANCHOR_INVALID:{original.count(anchor)}')
text = original.replace(anchor, insert, 1)
compile(text, str(path), 'exec')

contracts = {
    'runner_patch_regression_harnesses': text.count('def patch_regression_harnesses(root):'),
    'cdp_helper_anchor_guard': text.count('REHEARSAL105_CDP_HELPER_ANCHOR_INVALID'),
    'cdp_receipt_call_guard': text.count('REHEARSAL105_CDP_RECEIPT_CALL_CONTRACT_INVALID'),
    'domstorage_get_contract': text.count('DOMStorage.getDOMStorageItems'),
    'domstorage_added_event_contract': text.count('DOMStorage.domStorageItemAdded'),
    'domstorage_updated_event_contract': text.count('DOMStorage.domStorageItemUpdated'),
    'page_evaluate_receipt_reads': text.count("page.evaluate(() => JSON.parse(localStorage.getItem('pmp_reload_current_canonical_v1_receipt')))"),
}
expected = {
    'runner_patch_regression_harnesses': 1,
    'cdp_helper_anchor_guard': 1,
    'cdp_receipt_call_guard': 1,
    'domstorage_get_contract': 3,
    'domstorage_added_event_contract': 5,
    'domstorage_updated_event_contract': 5,
    'page_evaluate_receipt_reads': 1,
}
if contracts != expected:
    raise SystemExit('REHEARSAL105_RUNNER_CONTRACT_INVALID:' + json.dumps({'actual': contracts, 'expected': expected}, sort_keys=True))

path.write_text(text)
patched_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
evidence = {
    'type': 'PMP_P2C_A002_NAVIGATION_STABLE_RECEIPT_OBSERVATION_REPAIR_105',
    'status': 'PASS',
    'target': str(path),
    'original_sha256': original_sha256,
    'patched_sha256': patched_sha256,
    'scope': 'A002_REHEARSAL_HARNESS_ONLY',
    'observation_model_before': 'PAGE_EVALUATE_ACROSS_DOCUMENT_REPLACEMENT',
    'observation_model_after': 'NODE_SIDE_CHROMIUM_DOMSTORAGE_EVENT_OBSERVER_ARMED_BEFORE_RELOAD',
    'receipt_key': 'pmp_reload_current_canonical_v1_receipt',
    'receipt_status': 'MAP_CURRENT_APP_HANDOFF_READY',
    'expected_hash_bound': True,
    'expected_source_bound': True,
    'expected_current_map_role_bound': True,
    'page_script_injected_for_receipt_observation': False,
    'playwright_actor_capability_added': False,
    'unknown_actor_runtime_capability_added': False,
    'production_actor_policy_changed': False,
    'unknown_actor_policy_weakened': False,
    'production_changed': False,
    'production_activation_authorized': False,
    'current_map_changed': False,
    'persisted_data_changed': False,
    'formal_proof_executed': False,
    'contracts': contracts,
}
(evidence_dir / 'a002-navigation-stable-receipt-observation-repair-105.json').write_text(json.dumps(evidence, indent=2, sort_keys=True) + '\n')
print(json.dumps(evidence, sort_keys=True))
