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
    raise SystemExit(f'REHEARSAL104_RUNNER_NOT_FOUND:{path}')

original = path.read_text()
original_sha256 = hashlib.sha256(original.encode()).hexdigest()

anchor = " a002.write_text(s)\n a003=root/'audit/a003-live-runtime.cjs';s=a003.read_text()"
insert = r''' pmp_poll_helper_anchor="async function bootstrap(page, hash) {"
 pmp_poll_helper="""async function pmpA002PollPage(page, predicate, options = {}) {
  const timeout = Number(options.timeout || 30000);
  const interval = Number(options.interval || 100);
  const label = String(options.label || 'condition');
  const deadline = Date.now() + timeout;
  let lastError = null;
  while (Date.now() < deadline) {
    try {
      if (await page.evaluate(predicate)) return true;
    } catch (error) {
      lastError = error;
    }
    await page.waitForTimeout(interval);
  }
  const suffix = lastError ? ':' + String(lastError.message || lastError) : '';
  throw new Error('A002_PAGE_POLL_TIMEOUT:' + label + suffix);
}
"""
 if s.count(pmp_poll_helper_anchor)!=1:raise SystemExit(f'REHEARSAL104_POLL_HELPER_ANCHOR_INVALID:{s.count(pmp_poll_helper_anchor)}')
 s=s.replace(pmp_poll_helper_anchor,pmp_poll_helper+pmp_poll_helper_anchor,1)
 pmp_replacements=[
  ('bootstrap-receipt',("""  await page.waitForFunction(() => {
    try { return JSON.parse(localStorage.getItem('pmp_a003_bootstrap_receipt_v1') || 'null')?.status === 'PASS'; }
    catch { return false; }
  }, null, { timeout: 35000 });""",),"""  await pmpA002PollPage(page, () => {
    try { return JSON.parse(localStorage.getItem('pmp_a003_bootstrap_receipt_v1') || 'null')?.status === 'PASS'; }
    catch { return false; }
  }, { timeout: 35000, label: 'a003-bootstrap-receipt' });"""),
  ('guardian-frame-source',("""  await page.waitForFunction(() => {
    const frame = document.querySelector('iframe');
    return frame && /pmp-route-guardian-current-loader-v22\.html/.test(frame.getAttribute('src') || '');
  }, null, { timeout: 30000 });""","""  await page.waitForFunction(() => {
    const frame = document.querySelector('iframe');
    return frame && /pmp-route-guardian-current-loader-v22\.html/.test(frame.getAttribute('src') || '');
  }, null, { timeout: 30000, waitUntil: 'domcontentloaded' });"""),"""  await pmpA002PollPage(page, () => {
    const frame = document.querySelector('iframe');
    return frame && /pmp-route-guardian-current-loader-v22\.html/.test(frame.getAttribute('src') || '');
  }, { timeout: 30000, label: 'guardian-frame-source' });"""),
  ('canonical-reload-api',("""  await page.waitForFunction(() => window.PMPReloadCurrentCanonicalV1 && typeof window.PMPReloadCurrentCanonicalV1.reload === 'function', null, { timeout: 30000 });""","""  await page.waitForFunction(() => window.PMPReloadCurrentCanonicalV1 && typeof window.PMPReloadCurrentCanonicalV1.reload === 'function', null, { timeout: 30000, waitUntil: 'domcontentloaded' });"""),"""  await pmpA002PollPage(page, () => window.PMPReloadCurrentCanonicalV1 && typeof window.PMPReloadCurrentCanonicalV1.reload === 'function', { timeout: 30000, label: 'canonical-reload-api' });"""),
  ('reload-receipt',("""    await page.waitForFunction(() => {
      try {
        const r = JSON.parse(localStorage.getItem('pmp_reload_current_canonical_v1_receipt') || 'null');
        return r && r.status === 'MAP_CURRENT_APP_HANDOFF_READY';
      } catch { return false; }
    }, null, { timeout: 30000 });""","""    await page.waitForFunction(() => {
      try {
        const r = JSON.parse(localStorage.getItem('pmp_reload_current_canonical_v1_receipt') || 'null');
        return r && r.status === 'MAP_CURRENT_APP_HANDOFF_READY';
      } catch { return false; }
    }, null, { timeout: 30000, waitUntil: 'domcontentloaded' });"""),"""    await pmpA002PollPage(page, () => {
      try {
        const r = JSON.parse(localStorage.getItem('pmp_reload_current_canonical_v1_receipt') || 'null');
        return r && r.status === 'MAP_CURRENT_APP_HANDOFF_READY';
      } catch { return false; }
    }, { timeout: 30000, label: 'reload-current-receipt' });"""),
  ('blocked-candidate-status',("""  await page.waitForFunction(() => document.querySelector('#status')?.textContent.includes('BLOCKED_NOT_IN_CURRENT_MAP'));""",),"""  await pmpA002PollPage(page, () => document.querySelector('#status')?.textContent.includes('BLOCKED_NOT_IN_CURRENT_MAP'), { timeout: 30000, label: 'blocked-candidate-status' });"""),
  ('allowed-candidate-status',("""  await page.waitForFunction(() => document.querySelector('#status')?.textContent.includes('VIEWING_ALLOWED_NOT_CURRENT'));""",),"""  await pmpA002PollPage(page, () => document.querySelector('#status')?.textContent.includes('VIEWING_ALLOWED_NOT_CURRENT'), { timeout: 30000, label: 'allowed-candidate-status' });"""),
 ]
 for label,olds,new in pmp_replacements:
  matches=sum(s.count(old) for old in olds)
  if matches!=1:raise SystemExit(f'REHEARSAL104_{label.upper().replace("-","_")}_POINT_INVALID:{matches}')
  for old in olds:
   if s.count(old)==1:
    s=s.replace(old,new,1)
    break
 if 'waitForFunction' in s:raise SystemExit(f'REHEARSAL104_A002_WAITFORFUNCTION_REMAINS:{s.count("waitForFunction")}')
 if s.count('pmpA002PollPage(')!=7:raise SystemExit(f'REHEARSAL104_POLL_CALL_CONTRACT_INVALID:{s.count("pmpA002PollPage(")}')
 a002.write_text(s)
 a003=root/'audit/a003-live-runtime.cjs';s=a003.read_text()'''

if original.count(anchor) != 1:
    raise SystemExit(f'REHEARSAL104_A002_WRITE_ANCHOR_INVALID:{original.count(anchor)}')
text = original.replace(anchor, insert, 1)
compile(text, str(path), 'exec')

contracts = {
    'runner_patch_regression_harnesses': text.count('def patch_regression_harnesses(root):'),
    'a002_waitforfunction_guard': text.count('REHEARSAL104_A002_WAITFORFUNCTION_REMAINS'),
    'a002_poll_helper_contract': text.count('pmpA002PollPage('),
    'a003_write_anchor': text.count("a003=root/'audit/a003-live-runtime.cjs';s=a003.read_text()"),
}
expected = {
    'runner_patch_regression_harnesses': 1,
    'a002_waitforfunction_guard': 1,
    'a002_poll_helper_contract': 9,
    'a003_write_anchor': 1,
}
if contracts != expected:
    raise SystemExit('REHEARSAL104_RUNNER_CONTRACT_INVALID:' + json.dumps({'actual': contracts, 'expected': expected}, sort_keys=True))

path.write_text(text)
patched_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
evidence = {
    'type': 'PMP_P2C_A002_NO_WAITFORFUNCTION_HARNESS_REPAIR_104',
    'status': 'PASS',
    'target': str(path),
    'original_sha256': original_sha256,
    'patched_sha256': patched_sha256,
    'scope': 'A002_REHEARSAL_HARNESS_ONLY',
    'a002_waitforfunction_calls_before': 6,
    'a002_waitforfunction_calls_after': 0,
    'replacement_model': 'BOUNDED_NODE_DRIVEN_PAGE_EVALUATION_POLLING',
    'playwright_actor_capability_added': False,
    'unknown_actor_runtime_capability_added': False,
    'production_actor_policy_changed': False,
    'unknown_actor_policy_weakened': False,
    'a003_harness_changed': False,
    'production_changed': False,
    'production_activation_authorized': False,
    'current_map_changed': False,
    'persisted_data_changed': False,
    'formal_proof_executed': False,
    'contracts': contracts,
}
(evidence_dir / 'a002-no-waitforfunction-harness-repair-104.json').write_text(json.dumps(evidence, indent=2, sort_keys=True) + '\n')
print(json.dumps(evidence, sort_keys=True))
