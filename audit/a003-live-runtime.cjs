'use strict';
const fs = require('fs');
const http = require('http');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = process.cwd();
const HOST = '127.0.0.1';
const PORT = Number(process.env.A003_PORT || 8013);
const BASE = `http://${HOST}:${PORT}/`;
const RESULT_PATH = process.env.A003_RESULT_PATH || 'a003-live-runtime-results.json';
const CURRENT = 'pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html';
const MANIFEST = 'pmp-runtime-integrity-manifest-v1.json';
const EXPECTED_RECORD_COUNT = JSON.parse(fs.readFileSync(path.join(ROOT, MANIFEST), 'utf8')).records.length;
const RESOLVER = 'pmp-current-route-resolver-v1.js';
const INTEGRITY_SW = 'pmp-integrity-service-worker-v1.js';
const GUARDIAN = 'pmp-route-guardian-current-loader-v22.html';
const HOME = 'pmp-home-single-v6.html';
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
const state = { tamperPath: null, offlinePath: null, requests: [] };
const results = [];
let fatalError = null;

const MIME = {
  '.html':'text/html; charset=utf-8','.htm':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.mjs':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.css':'text/css; charset=utf-8','.wasm':'application/wasm','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.svg':'image/svg+xml'
};
function safeRel(url) {
  const decoded = decodeURIComponent(new URL(url, BASE).pathname).replace(/^\/+/, '');
  const normalized = path.posix.normalize(decoded || 'index.html');
  if (normalized.startsWith('../') || normalized === '..') return null;
  return normalized;
}
function startServer() {
  const server = http.createServer((req, res) => {
    const rel = safeRel(req.url);
    state.requests.push({ at: new Date().toISOString(), method: req.method, path: rel, url: req.url });
    if (!rel) { res.writeHead(400); res.end('bad path'); return; }
    if (state.offlinePath === rel) { res.writeHead(503, {'Cache-Control':'no-store','Content-Type':'text/plain'}); res.end('A003 simulated offline'); return; }
    const file = path.join(ROOT, rel);
    if (!fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404, {'Cache-Control':'no-store','Content-Type':'text/plain'}); res.end('not found'); return; }
    let body = fs.readFileSync(file);
    if (state.tamperPath === rel) body = Buffer.concat([body, Buffer.from('\n/* A003_ONE_BYTE_TAMPER */x')]);
    const headers = {
      'Content-Type': MIME[path.extname(file).toLowerCase()] || 'application/octet-stream',
      'Content-Length': String(body.length),
      'Cache-Control': 'no-store',
      'Access-Control-Allow-Origin': '*'
    };
    res.writeHead(200, headers); res.end(body);
  });
  return new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(PORT, HOST, () => resolve(server));
  });
}
function errorObject(error) { return { name: String(error?.name || 'Error'), message: String(error?.message || error), stack: String(error?.stack || '') }; }
function record(name, pass, detail = {}) {
  const item = { name, pass: !!pass, detail, at: new Date().toISOString() };
  results.push(item);
  console.log(`${pass ? 'PASS' : 'FAIL'} ${name} ${JSON.stringify(detail)}`);
  if (!pass) throw new Error(`${name}: ${JSON.stringify(detail)}`);
}
function writeOutput() {
  const output = {
    type: 'PMP_A003_LIVE_RUNTIME_RESULT_V1', repair_id: 'A-003', generated_at: new Date().toISOString(), base_url: BASE,
    tests_total: results.length, tests_passed: results.filter(r => r.pass).length, tests_failed: results.filter(r => !r.pass).length,
    fatal_error: fatalError, results, request_count: state.requests.length
  };
  fs.writeFileSync(RESULT_PATH, JSON.stringify(output, null, 2));
  console.log(`A003_RESULT_WRITTEN ${RESULT_PATH} ${JSON.stringify({tests_total:output.tests_total,tests_passed:output.tests_passed,tests_failed:output.tests_failed,fatal_error:!!fatalError})}`);
}
async function bootstrap(context, hash = '#control') {
  const page = await context.newPage();
  page.setDefaultTimeout(30000);
  await page.goto(BASE + 'pmp-app-current.html' + hash, { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => {
    try { return JSON.parse(localStorage.getItem('pmp_a003_bootstrap_receipt_v1') || 'null')?.status === 'PASS'; } catch { return false; }
  }, null, { timeout: 35000 });
  await page.waitForFunction(() => {
    const f = document.querySelector('iframe'); return f && /pmp-route-guardian-current-loader-v22\.html/.test(f.getAttribute('src') || '');
  });
  return page;
}
async function workerStatus(page) {
  return page.evaluate(() => new Promise((resolve, reject) => {
    const controller = navigator.serviceWorker.controller;
    if (!controller) return reject(new Error('controller missing'));
    const timer = setTimeout(() => reject(new Error('status timeout')), 8000);
    const channel = new MessageChannel();
    channel.port1.onmessage = e => { clearTimeout(timer); resolve(e.data); };
    controller.postMessage({ type:'PMP_RUNTIME_INTEGRITY_STATUS_REQUEST', from:'a003-live-test' }, [channel.port2]);
  }));
}
async function guardianFrame(page) {
  const deadline = Date.now() + 20000;
  while (Date.now() < deadline) {
    const frame = page.frames().find(f => /pmp-route-guardian-current-loader-v22\.html/.test(f.url()));
    if (frame) return frame;
    await page.waitForTimeout(250);
  }
  throw new Error('Guardian frame not found');
}
async function frameReachedHome(page, expectedHash) {
  const deadline = Date.now() + 30000;
  while (Date.now() < deadline) {
    const urls = page.frames().map(f => f.url());
    const homeUrl = urls.find(u => /pmp-home-single-v6\.html/.test(u));
    if (homeUrl) {
      const actualHash = new URL(homeUrl).hash;
      return { reached:true, expected_hash:expectedHash, actual_hash:actualHash, hash_matches:actualHash === expectedHash, home_url:homeUrl, urls };
    }
    await page.waitForTimeout(400);
  }
  return { reached:false, expected_hash:expectedHash, actual_hash:null, hash_matches:false, home_url:null, urls:page.frames().map(f=>f.url()) };
}
async function historicalReceiptFromHomeFrame(page) {
  const deadline = Date.now() + 30000;
  let last = null;
  while (Date.now() < deadline) {
    const frame = page.frames().find(f => /pmp-home-single-v6\.html/.test(f.url()));
    if (frame) {
      try {
        last = await frame.evaluate(() => {
          try {
            const receipt = JSON.parse(localStorage.getItem('pmp_home_single_v6_emergency_rollback_receipt') || 'null');
            return { receipt, body: document.body?.innerText?.slice(0, 1200) || '', url: location.href };
          } catch (error) {
            return { receipt: null, error: String(error?.message || error), body: document.body?.innerText?.slice(0, 1200) || '', url: location.href };
          }
        });
        if (last?.receipt && (last.receipt.verification === 'PASS' || last.receipt.status === 'rollback_failed_closed')) return last;
      } catch (error) {
        last = { receipt: null, error: String(error?.message || error), frame_url: frame.url() };
      }
    }
    await page.waitForTimeout(300);
  }
  throw new Error('historical_home_receipt_timeout: ' + JSON.stringify(last));
}
async function openCurrentFromGuardian(page, screen) {
  const frame = await guardianFrame(page);
  await frame.click('#openBtn',{force:true});
  await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#' + screen, { timeout: 30000 });
  return frameReachedHome(page, '#' + screen);
}
async function fetchInPage(page, url) {
  return page.evaluate(async u => {
    const response = await fetch(u, { cache:'no-store' });
    return { status:response.status, ok:response.ok, integrity:response.headers.get('X-PMP-Integrity'), transform:response.headers.get('X-PMP-Integrity-Transform'), sha:response.headers.get('X-PMP-Integrity-SHA256'), text:await response.text() };
  }, url);
}
async function expectBootstrapFailure(pathName, expectedCode) {
  state.tamperPath = pathName;
  const context = await browser.newContext({ serviceWorkers:'allow' });
  const page = await context.newPage(); page.setDefaultTimeout(30000);
  await page.goto(BASE + 'pmp-app-current.html#control', { waitUntil:'domcontentloaded' });
  await page.waitForFunction(() => document.querySelector('#routeDiagnostic')?.textContent.includes('application_launch_blocked_no_unverified_fallback'), null, { timeout:30000 });
  const text = await page.textContent('#routeDiagnostic');
  const src = await page.getAttribute('#app', 'src');
  record(`bootstrap-tamper-block:${pathName}`, text.includes(expectedCode) && !src, { expected_code:expectedCode, iframe_src:src, diagnostic:text.slice(0,1200) });
  await context.close(); state.tamperPath = null;
}

let browser;
(async () => {
  const server = await startServer();
  try {
    browser = await chromium.launch({ headless:true });

    const context = await browser.newContext({ serviceWorkers:'allow' });
    let page = await bootstrap(context, '#control');
    const bootReceipt = await page.evaluate(() => JSON.parse(localStorage.getItem('pmp_a003_bootstrap_receipt_v1')));
    record('bootstrap-root-pass', bootReceipt.status === 'PASS' && /^[0-9a-f]{64}$/.test(bootReceipt.manifest_sha256) && /^[0-9a-f]{64}$/.test(bootReceipt.worker_sha256) && /^[0-9a-f]{64}$/.test(bootReceipt.resolver_sha256) && /^[0-9a-f]{64}$/.test(bootReceipt.map_sha256), bootReceipt);

    const status = await workerStatus(page);
    record('integrity-worker-enforced', status.type === 'PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE' && status.receipt?.state === 'ENFORCED' && status.receipt?.version === '1.1.0-a003-runtime-integrity-sri' && status.receipt?.record_count === EXPECTED_RECORD_COUNT, status);
    const registrations = await page.evaluate(async () => (await navigator.serviceWorker.getRegistrations()).map(r => ({scope:r.scope, active:r.active?.scriptURL||null, waiting:r.waiting?.scriptURL||null, installing:r.installing?.scriptURL||null})));
    record('only-integrity-worker-registration', registrations.length === 1 && registrations[0].active?.includes('/' + INTEGRITY_SW), registrations);

    const manifestFetch = await fetchInPage(page, MANIFEST);
    record('manifest-response-verified', manifestFetch.status === 200 && manifestFetch.integrity === 'verified-manifest', {status:manifestFetch.status, integrity:manifestFetch.integrity, sha:manifestFetch.sha});

    const mapFetch = await fetchInPage(page, 'pmp-current-map-v12.json');
    record('map-response-verified-before-consumption', mapFetch.status === 200 && mapFetch.integrity === 'verified-network' && /^[0-9a-f]{64}$/.test(mapFetch.sha || ''), {status:mapFetch.status, integrity:mapFetch.integrity, sha:mapFetch.sha});

    const sriFetch = await fetchInPage(page, 'private-bug-mixer-lab-v1.html');
    record('external-script-sri-injected-after-document-verification', sriFetch.status === 200 && sriFetch.transform?.startsWith('external-sri:') && sriFetch.text.includes('integrity="sha256-rMfkFFWoB2W1/Zx+4bgHim0WC7vKRVrq6FTeZclH1Z4="') && sriFetch.text.includes('crossorigin="anonymous"'), {status:sriFetch.status, integrity:sriFetch.integrity, transform:sriFetch.transform});

    const unlisted = await fetchInPage(page, 'a003-unlisted-executable-test.js');
    record('unlisted-executable-blocked', unlisted.status === 412 && unlisted.text.includes('UNLISTED_EXECUTABLE_SOURCE'), {status:unlisted.status, body:unlisted.text.slice(0,500)});

    const offlinePath = 'safe-writer-v14.html';
    const warm = await fetchInPage(page, offlinePath);
    record('verified-cache-warm', warm.status === 200 && warm.integrity === 'verified-network', {status:warm.status, integrity:warm.integrity});
    state.offlinePath = offlinePath;
    const offline = await fetchInPage(page, offlinePath + '?offline=1');
    record('offline-exact-hash-cache-accepted', offline.status === 200 && offline.integrity === 'verified-cache', {status:offline.status, integrity:offline.integrity, sha:offline.sha});
    state.offlinePath = null;

    state.tamperPath = offlinePath;
    const mismatchWithCache = await fetchInPage(page, offlinePath + '?tampered=1');
    record('network-mismatch-never-falls-back-to-cache', mismatchWithCache.status === 412 && mismatchWithCache.text.includes('SOURCE_DIGEST_MISMATCH'), {status:mismatchWithCache.status, integrity:mismatchWithCache.integrity, body:mismatchWithCache.text.slice(0,500)});
    state.tamperPath = null;

    state.tamperPath = 'pmp-current-map-v12.json';
    const mapRejected = await page.evaluate(async () => {
      try { await window.PMPCurrentRouteResolver.load(); return {rejected:false}; }
      catch (e) { return {rejected:true, code:e.code||null, message:String(e.message||e), details:e.details||null}; }
    });
    record('tampered-map-rejected-by-resolver', mapRejected.rejected && /BOOTSTRAP_HTTP_FAILED|INTEGRITY_HTTP_FAILED|SOURCE_DIGEST_MISMATCH/.test(String(mapRejected.code)+' '+mapRejected.message), mapRejected);
    state.tamperPath = null;

    state.tamperPath = GUARDIAN;
    const guardianResponse = await page.goto(BASE + GUARDIAN + '?tampered=1', { waitUntil:'domcontentloaded' });
    const guardianBody = await page.textContent('body');
    record('tampered-navigation-blocked-before-execution', guardianResponse?.status() === 412 && guardianBody.includes('SOURCE_DIGEST_MISMATCH') && !guardianBody.includes('ROUTE GUARDIAN v22.10'), {status:guardianResponse?.status(), body:guardianBody.slice(0,700)});
    state.tamperPath = null;

    await page.close();
    for (const screen of SCREENS) {
      page = await bootstrap(context, '#' + screen);
      const home = await openCurrentFromGuardian(page, screen);
      record(`integrity-current-chain-home:${screen}`, home.reached && home.hash_matches, {expected:home.expected_hash, actual:home.actual_hash, home_url:home.home_url, frame_urls:home.urls.slice(-8)});
      const homeState = await historicalReceiptFromHomeFrame(page);
      const homeReceipt = homeState.receipt;
      record(`historical-home-sha256-pass:${screen}`, homeReceipt.verification === 'PASS' && homeReceipt.expected_sha256 === homeReceipt.actual_sha256, {expected:homeReceipt.expected_sha256, actual:homeReceipt.actual_sha256, status:homeReceipt.status, frame_url:homeState.url, frame_body:homeState.body});
      await page.close();
    }

    page = await bootstrap(context, '#control');
    let frame = await guardianFrame(page); await frame.click('#openBtn',{force:true});
    await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#control', {timeout:30000});
    await page.goto(BASE + 'safe-writer-v14.html?return_hash=%23control', {waitUntil:'domcontentloaded'}); await page.click('text=Back to Control');
    await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#control');
    record('safe-writer-return-under-integrity', true, {url:page.url()});
    await page.goto(BASE + 'code-safety-v13.html?return_hash=%23control', {waitUntil:'domcontentloaded'}); await page.click('#backToControlBtn');
    await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#control');
    record('code-safety-return-under-integrity', true, {url:page.url()});

    await page.goto(BASE + 'pmp-move-ledger-candidate-follow-v1.html?candidate=arbitrary-not-allowed.html', {waitUntil:'domcontentloaded'});
    await page.waitForFunction(() => document.querySelector('#status')?.textContent.includes('BLOCKED_NOT_IN_CURRENT_MAP'));
    record('arbitrary-recovery-candidate-blocked-under-integrity', !(await page.getAttribute('#target','src')));
    await page.goto(BASE + 'pmp-move-ledger-candidate-follow-v1.html?candidate=' + encodeURIComponent(CURRENT), {waitUntil:'domcontentloaded'});
    await page.waitForFunction(() => document.querySelector('#status')?.textContent.includes('VIEWING_ALLOWED_NOT_CURRENT'));
    const allowedSrc = await page.getAttribute('#target','src');
    record('allowlisted-recovery-review-under-integrity', !!allowedSrc && allowedSrc.includes(CURRENT), {iframe_src:allowedSrc});

    for (const file of HISTORIC) {
      await page.goto(BASE + file + '#library', {waitUntil:'domcontentloaded'});
      await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#library', {timeout:30000});
      record(`historic-forward-under-integrity:${file}`, true, {url:page.url()});
    }
    const afterRegistrations = await page.evaluate(async () => (await navigator.serviceWorker.getRegistrations()).map(r => r.active?.scriptURL||null));
    record('guardian-and-historic-pages-did-not-replace-integrity-worker', afterRegistrations.length === 1 && afterRegistrations[0]?.includes('/' + INTEGRITY_SW), afterRegistrations);
    await context.close();

    await expectBootstrapFailure(MANIFEST, 'MANIFEST_DIGEST_MISMATCH');
    await expectBootstrapFailure(INTEGRITY_SW, 'BOOTSTRAP_SOURCE_DIGEST_MISMATCH');
    await expectBootstrapFailure(RESOLVER, 'BOOTSTRAP_SOURCE_DIGEST_MISMATCH');

    const historicalContext = await browser.newContext({serviceWorkers:'allow'});
    const historicalPage = await bootstrap(historicalContext, '#world');
    await historicalContext.route('https://raw.githubusercontent.com/pmpbird/pmp-bridge-shell/7ac7213aeeeb8bb55692a4985e0fa80a547cff4e/pmp-home-single-v6.html*', async route => {
      const response = await route.fetch();
      const body = Buffer.concat([await response.body(), Buffer.from('\n<!-- A003 HISTORICAL TAMPER -->')]);
      const headers = {...response.headers(), 'access-control-allow-origin':'*', 'cache-control':'no-store'};
      await route.fulfill({status:200, headers, body});
    });
    await historicalPage.goto(BASE + HOME + '?requested_hash=%23world#world', {waitUntil:'domcontentloaded'});
    await historicalPage.waitForFunction(() => {
      try { return JSON.parse(localStorage.getItem('pmp_home_single_v6_emergency_rollback_receipt') || 'null')?.status === 'rollback_failed_closed'; } catch { return false; }
    }, null, {timeout:30000});
    const historicalReceipt = await historicalPage.evaluate(() => JSON.parse(localStorage.getItem('pmp_home_single_v6_emergency_rollback_receipt')));
    record('tampered-historical-home-blocked-before-document-write', historicalReceipt.status === 'rollback_failed_closed' && historicalReceipt.expected_sha256 !== historicalReceipt.actual_sha256 && historicalReceipt.diagnostic?.action === 'navigation_blocked_no_unverified_fallback_consulted', historicalReceipt);
    await historicalContext.close();

    await browser.close(); browser = null;
  } catch (error) {
    fatalError = errorObject(error); console.error(error?.stack || error); process.exitCode = 1;
  } finally {
    state.tamperPath = null; state.offlinePath = null;
    try { if (browser) await browser.close(); } catch (e) { if (!fatalError) fatalError = errorObject(e); process.exitCode = 1; }
    await new Promise(resolve => server.close(resolve));
    writeOutput();
  }
})();
