'use strict';
const fs = require('fs');
const { chromium } = require('playwright');

const BASE = process.env.A002_BASE_URL || 'http://127.0.0.1:8000/';
const RESULT_PATH = process.env.A002_RESULT_PATH || 'a002-live-runtime-results.json';
const CURRENT = 'pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html';
const INTEGRITY_SW = 'pmp-integrity-service-worker-v1.js';
const SCREENS = ['world','bridge','library','workshop','control','bank'];
const HISTORIC = [
  'pmp-route-guardian-current-loader-v15.html',
  'pmp-route-guardian-current-loader-v17.html',
  'pmp-route-guardian-current-loader-v18.html',
  'pmp-route-guardian-current-loader-v19.html',
  'pmp-route-guardian-current-loader-v20.html',
  'pmp-route-guardian-current-loader-v21.html',
  'pmp-current-reload-owner-v27.html',
  'pmp-current-reload-owner-v28.html',
  'pmp-current-reload-owner-v29.html',
  'pmp-current-reload-owner-v29-cachelift-20260706b.html',
  'pmp-current-reload-owner-v29-permanent-update-gate-20260706f.html',
  'pmp-current-inner-cleanbug-rgcontrols-v24.html',
  'pmp-current-inner-cleanbug-rgcontrols-v26.html',
  'pmp-current-inner-cleanbug-rgcontrols-v29.html'
];
const results = [];
let fatalError = null;

function serializableError(error) {
  return { name: String(error?.name || 'Error'), message: String(error?.message || error), stack: String(error?.stack || '') };
}
function writeOutput() {
  const output = {
    type: 'PMP_A002_LIVE_RUNTIME_RESULT_V2_A003_COMPATIBLE',
    generated_at: new Date().toISOString(),
    base_url: BASE,
    compatibility: 'A-002 sole-route-authority checks executed under A-003 runtime-integrity enforcement',
    tests_total: results.length,
    tests_passed: results.filter(r => r.pass).length,
    tests_failed: results.filter(r => !r.pass).length,
    fatal_error: fatalError,
    results
  };
  fs.writeFileSync(RESULT_PATH, JSON.stringify(output, null, 2));
  console.log(`A002_RESULT_WRITTEN ${RESULT_PATH} ${JSON.stringify({tests_total:output.tests_total,tests_passed:output.tests_passed,tests_failed:output.tests_failed,fatal_error:!!fatalError})}`);
}
function record(name, pass, detail = {}) {
  results.push({ name, pass: !!pass, detail, at: new Date().toISOString() });
  console.log(`${pass ? 'PASS' : 'FAIL'} ${name} ${JSON.stringify(detail)}`);
  if (!pass) throw new Error(`${name}: ${JSON.stringify(detail)}`);
}
async function bootstrap(page, hash) {
  await page.goto(BASE + 'pmp-app-current.html' + hash, { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => {
    try { return JSON.parse(localStorage.getItem('pmp_a003_bootstrap_receipt_v1') || 'null')?.status === 'PASS'; }
    catch { return false; }
  }, null, { timeout: 35000 });
  await page.waitForFunction(() => {
    const frame = document.querySelector('iframe');
    return frame && /pmp-route-guardian-current-loader-v22\.html/.test(frame.getAttribute('src') || '');
  }, null, { timeout: 30000 });
}
async function guardianFrame(page) {
  const deadline = Date.now() + 20000;
  while (Date.now() < deadline) {
    const frame = page.frames().find(f => /pmp-route-guardian-current-loader-v22\.html/.test(f.url()));
    if (frame) return frame;
    await page.waitForTimeout(250);
  }
  throw new Error('current Route Guardian frame not found');
}
async function workerStatus(page) {
  return page.evaluate(() => new Promise((resolve, reject) => {
    const controller = navigator.serviceWorker.controller;
    if (!controller) return reject(new Error('A-003 integrity controller missing'));
    const timer = setTimeout(() => reject(new Error('A-003 integrity status timeout')), 8000);
    const channel = new MessageChannel();
    channel.port1.onmessage = event => { clearTimeout(timer); resolve(event.data); };
    controller.postMessage({ type:'PMP_RUNTIME_INTEGRITY_STATUS_REQUEST', from:'a002-live-compatibility' }, [channel.port2]);
  }));
}
async function waitForCanonical(page) {
  await page.waitForFunction(() => window.PMPReloadCurrentCanonicalV1 && typeof window.PMPReloadCurrentCanonicalV1.reload === 'function', null, { timeout: 30000 });
}
async function frameReachedHome(page, expectedHash) {
  const deadline = Date.now() + 30000;
  while (Date.now() < deadline) {
    const urls = page.frames().map(f => f.url());
    const homeUrl = urls.find(u => /pmp-home-single-v6\.html/.test(u));
    if (homeUrl) {
      let actualHash = '';
      try { actualHash = new URL(homeUrl).hash; } catch {}
      return { reached: true, hash_matches: actualHash === expectedHash, expected_hash: expectedHash, actual_hash: actualHash, home_url: homeUrl, urls };
    }
    await page.waitForTimeout(400);
  }
  return { reached: false, hash_matches: false, expected_hash: expectedHash, actual_hash: null, home_url: null, urls: page.frames().map(f => f.url()) };
}

async function runMatrix(page) {
  const map = await (await page.request.get(BASE + 'pmp-current-map-v12.json?live=' + Date.now())).json();
  record('current-map-contract-a003-compatible',
    map.route_contract?.sole_authority === 'pmp-current-map-v12.json' &&
    map.route_contract?.implicit_fallbacks === false &&
    map.route_contract?.runtime_integrity_required === true &&
    map.current_app?.path === CURRENT &&
    String(map.historic_policy?.status || '').includes('a002_p6'),
    { app_version: map.app_version, route_epoch: map.route_epoch, current_app: map.current_app?.path, historic_policy: map.historic_policy?.status }
  );

  for (const oldMap of ['pmp-current-map-v11.json','pmp-current-map-v10.json','pmp-current-map-v9.json','pmp-current-map.json']) {
    const data = await (await page.request.get(BASE + oldMap + '?live=' + Date.now())).json();
    record(`historic-map-evidence:${oldMap}`, data.type === 'PMP_HISTORIC_MAP_EVIDENCE_V1' && data.executable === false && data.contains_current_destination_truth === false && !data.current_app, { status: data.status });
  }

  await bootstrap(page, '#world');
  const bootstrapReceipt = await page.evaluate(() => JSON.parse(localStorage.getItem('pmp_a003_bootstrap_receipt_v1')));
  record('stable-entry-a003-bootstrap-pass', bootstrapReceipt.status === 'PASS' && bootstrapReceipt.target === 'pmp-route-guardian-current-loader-v22.html', { target: bootstrapReceipt.target, map_version: bootstrapReceipt.map_version, route_epoch: bootstrapReceipt.route_epoch });

  const firstStatus = await workerStatus(page);
  record('a003-integrity-controller-enforced', firstStatus?.type === 'PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE' && firstStatus?.receipt?.state === 'ENFORCED' && String(firstStatus?.receipt?.version || '').startsWith('1.1.0-a003-runtime-integrity'), firstStatus);

  const registrations = await page.evaluate(async () => (await navigator.serviceWorker.getRegistrations()).map(r => r.active?.scriptURL || null));
  record('only-a003-integrity-worker-registered', registrations.length === 1 && registrations[0]?.includes('/' + INTEGRITY_SW), registrations);

  const guardian = await guardianFrame(page);
  await guardian.click('#openBtn', { force: true });
  await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#world', { timeout: 30000 });
  record('stable-entry-map-guardian-current-handoff', true, { url: page.url() });

  for (const screen of SCREENS) {
    const expectedHash = '#' + screen;
    if (!(new URL(page.url()).pathname.endsWith('/' + CURRENT) && new URL(page.url()).hash === expectedHash)) {
      await page.goto(BASE + CURRENT + expectedHash, { waitUntil: 'domcontentloaded' });
    }
    await waitForCanonical(page);
    const home = await frameReachedHome(page, expectedHash);
    record(`current-chain-home:${screen}`, home.reached && home.hash_matches, { expected_hash: home.expected_hash, actual_hash: home.actual_hash, home_url: home.home_url, frame_urls: home.urls.slice(-8) });

    await page.evaluate(async s => {
      await window.PMPReloadCurrentCanonicalV1.reload(null, { source: 'a002-a003-compatible-live', page: '#' + s, pressed_text: 'Reload Current' });
    }, screen).catch(() => {});
    await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === expectedHash, { timeout: 30000 });
    await page.waitForFunction(() => {
      try {
        const r = JSON.parse(localStorage.getItem('pmp_reload_current_canonical_v1_receipt') || 'null');
        return r && r.status === 'MAP_CURRENT_APP_HANDOFF_READY';
      } catch { return false; }
    }, null, { timeout: 30000 });
    const receipt = await page.evaluate(() => JSON.parse(localStorage.getItem('pmp_reload_current_canonical_v1_receipt')));
    record(`reload-current:${screen}`, receipt.page === expectedHash && receipt.target_role === 'current_app' && receipt.map_path === 'pmp-current-map-v12.json', { target: receipt.target_path, page: receipt.page, map_version: receipt.map_version, route_epoch: receipt.route_epoch });
  }

  await page.goto(BASE + 'safe-writer-v14.html?return_hash=%23control', { waitUntil: 'domcontentloaded' });
  await page.click('text=Back to Control');
  await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#control');
  record('safe-writer-return-current-map', true, { url: page.url() });

  await page.goto(BASE + 'code-safety-v13.html?return_hash=%23control', { waitUntil: 'domcontentloaded' });
  await page.click('#backToControlBtn');
  await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#control');
  record('code-safety-return-current-map', true, { url: page.url() });

  await page.goto(BASE + 'pmp-move-ledger-candidate-follow-v1.html?candidate=arbitrary-not-allowed.html', { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => document.querySelector('#status')?.textContent.includes('BLOCKED_NOT_IN_CURRENT_MAP'));
  const blockedSrc = await page.getAttribute('#target', 'src');
  record('arbitrary-recovery-candidate-blocked', !blockedSrc, { iframe_src: blockedSrc });

  await page.goto(BASE + 'pmp-move-ledger-candidate-follow-v1.html?candidate=' + encodeURIComponent(CURRENT), { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => document.querySelector('#status')?.textContent.includes('VIEWING_ALLOWED_NOT_CURRENT'));
  const allowedSrc = await page.getAttribute('#target', 'src');
  record('allowlisted-recovery-candidate-review', !!allowedSrc && allowedSrc.includes(CURRENT), { iframe_src: allowedSrc });

  for (const file of HISTORIC) {
    await page.goto(BASE + file + '#library', { waitUntil: 'domcontentloaded' });
    await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#library', { timeout: 30000 });
    record(`historic-bookmark-forward:${file}`, true, { url: page.url() });
  }

  const finalStatus = await workerStatus(page);
  record('service-worker-live-status-a003', finalStatus?.type === 'PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE' && finalStatus?.receipt?.state === 'ENFORCED' && finalStatus?.receipt?.unlisted_executable_policy === 'FAIL_CLOSED' && finalStatus?.receipt?.offline_policy === 'MATCHING_VERIFIED_CACHE_ONLY', finalStatus);

  const finalRegistrations = await page.evaluate(async () => (await navigator.serviceWorker.getRegistrations()).map(r => r.active?.scriptURL || null));
  record('a002-matrix-did-not-replace-integrity-worker', finalRegistrations.length === 1 && finalRegistrations[0]?.includes('/' + INTEGRITY_SW), finalRegistrations);
}

(async () => {
  let browser = null;
  try {
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ serviceWorkers: 'allow' });
    const page = await context.newPage();
    page.setDefaultTimeout(30000);
    await runMatrix(page);
  } catch (error) {
    fatalError = serializableError(error);
    console.error(error?.stack || error);
    process.exitCode = 1;
  } finally {
    try { if (browser) await browser.close(); } catch (closeError) {
      if (!fatalError) fatalError = serializableError(closeError);
      process.exitCode = 1;
    }
    try { writeOutput(); } catch (writeError) {
      console.error(writeError?.stack || writeError);
      process.exitCode = 1;
    }
  }
})();
