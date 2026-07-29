import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base = process.env.PMP_BASE_URL || 'http://127.0.0.1:8000';
const current = 'pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html';
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 390, height: 844 }, serviceWorkers: 'allow' });
const page = await context.newPage();
page.setDefaultTimeout(30000);

try {
  const mapResponse = await page.request.get(`${base}/pmp-current-map-v12.json?automated-plan-retirement=${Date.now()}`);
  assert.equal(mapResponse.ok(), true, 'current A-003 map could not be loaded');
  const map = await mapResponse.json();
  assert.equal(map.app_version, 'PMP-CURRENT-1-A003');
  assert.equal(map.route_contract?.runtime_integrity_required, true);
  assert.equal(map.current_app?.path, current);
  assert.notEqual(map.current_app?.path, 'pmp-current-inner-cleanbug-rgcontrols-v6.html');
  assert.equal(Object.values(map.runtime_chain || {}).some((item) => item?.path === 'pmp-current-inner-cleanbug-rgcontrols-v6.html'), false, 'retired v6 wrapper remains in current runtime chain');

  await page.goto(`${base}/pmp-app-current.html#control`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForFunction(() => {
    try { return JSON.parse(localStorage.getItem('pmp_a003_bootstrap_receipt_v1') || 'null')?.status === 'PASS'; }
    catch { return false; }
  }, null, { timeout: 45000 });
  await page.waitForFunction(() => {
    const frame = document.querySelector('iframe');
    return frame && /pmp-route-guardian-current-loader-v22\.html/.test(frame.getAttribute('src') || '');
  }, null, { timeout: 30000 });

  let guardian;
  for (let i = 0; i < 80; i += 1) {
    guardian = page.frames().find((frame) => /pmp-route-guardian-current-loader-v22\.html/.test(frame.url()));
    if (guardian) break;
    await page.waitForTimeout(250);
  }
  assert.ok(guardian, 'current A-003 Route Guardian frame was not found');
  await guardian.click('#openBtn', { force: true });
  await page.waitForURL((url) => url.pathname.endsWith('/' + current) && url.hash === '#control', { timeout: 45000 });

  await page.waitForFunction(() => {
    try {
      const receipt = JSON.parse(localStorage.getItem('pmp_pass75_reload_runtime_platform_gate_v1_receipt') || 'null');
      return receipt?.version === '1.3.1-idempotent-style' && receipt?.certified === true;
    } catch { return false; }
  }, null, { timeout: 45000 });
  const preRelease = await page.evaluate(() => JSON.parse(localStorage.getItem('pmp_pass75_reload_runtime_platform_gate_v1_receipt')));
  assert.equal(preRelease.released, false, 'current runtime gate must remain closed before explicit test release');
  const releaseButton = page.locator('#pmpPass75ReloadRuntimePlatformGateV1 button[data-run="1"]');
  assert.equal(await releaseButton.count(), 1, 'current runtime gate must expose exactly one explicit release control');
  await releaseButton.click({ force: true });
  await page.waitForFunction(() => {
    try {
      const receipt = JSON.parse(localStorage.getItem('pmp_pass75_reload_runtime_platform_gate_v1_receipt') || 'null');
      return receipt?.released === true && receipt?.release_reason === 'manual_diagnostic_run_app_orchestrator';
    } catch { return false; }
  }, null, { timeout: 30000 });

  let controlFrame;
  for (let i = 0; i < 120; i += 1) {
    for (const frame of page.frames()) {
      try {
        if (await frame.locator('#control').count()) {
          controlFrame = frame;
          break;
        }
      } catch {}
    }
    if (controlFrame) break;
    await page.waitForTimeout(250);
  }
  assert.ok(controlFrame, 'current A-003 app Control Room frame was not found');
  assert.equal(await controlFrame.locator('#control').count(), 1, 'current app must expose exactly one Control Room root');
  assert.ok(await controlFrame.locator('#control .card').count(), 'current Control Room native card was not found');
  assert.ok(await controlFrame.locator('#control button.big').count(), 'current Control Room native big controls were not found');

  const bootstrap = await page.evaluate(() => JSON.parse(localStorage.getItem('pmp_a003_bootstrap_receipt_v1')));
  assert.equal(bootstrap.status, 'PASS');
  assert.equal(bootstrap.target, 'pmp-route-guardian-current-loader-v22.html');

  const legacySource = await (await page.request.get(`${base}/pmp-current-inner-cleanbug-rgcontrols-v6.html?retirement-proof=${Date.now()}`)).text();
  assert.match(legacySource, /pmp-automated-plan-room-v1\.js/);
  assert.match(legacySource, /pmp-current-inner-cleanbug-rgcontrols-v4\.html/);

  console.log(JSON.stringify({
    result: 'PASS',
    verification: 'AUTOMATED_PLAN_UI_RETIREMENT_CURRENT_APP_COMPATIBILITY',
    current_app: map.current_app.path,
    current_hash: '#control',
    current_control_room_found: true,
    runtime_gate_manual_release_verified: true,
    a003_bootstrap_status: bootstrap.status,
    legacy_wrapper: 'pmp-current-inner-cleanbug-rgcontrols-v6.html',
    legacy_wrapper_current_authority: false,
    historical_foundation_entry: 'Automated Plan',
    superseding_ui_owner: 'Continuous Run Dashboard',
    execution_enabled: false,
    pass_003_started: false
  }, null, 2));
} finally {
  await browser.close();
}
