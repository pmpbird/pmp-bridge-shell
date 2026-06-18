import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base = process.env.PMP_BASE_URL || 'http://127.0.0.1:8000';
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
const page = await context.newPage();

try {
  await page.goto(`${base}/pmp-current-inner-cleanbug-rgcontrols-v6.html#control`, { waitUntil: 'domcontentloaded', timeout: 60000 });

  let appFrame;
  for (let i = 0; i < 80; i += 1) {
    for (const frame of page.frames()) {
      try {
        if (await frame.locator('#control').count()) {
          appFrame = frame;
          break;
        }
      } catch {}
    }
    if (appFrame) break;
    await page.waitForTimeout(250);
  }
  assert.ok(appFrame, 'real app Control Room frame was not found');

  await appFrame.waitForSelector('#pmpAutomatedPlanEntryV1', { timeout: 30000 });
  await page.waitForTimeout(1200);

  assert.equal(await appFrame.locator('#pmpAutomatedPlanEntryV1').count(), 1, 'Control Room must contain exactly one Automated Plan entry');
  const entryText = (await appFrame.locator('#pmpAutomatedPlanEntryV1').innerText()).trim();
  assert.match(entryText, /Automated Plan\s+Setup — execution is safely locked/);
  assert.doesNotMatch(entryText, /Packet|01\.5|packet_01_5/i);

  const buttonProperties = [
    'backgroundColor', 'color', 'borderTopColor', 'borderTopWidth', 'borderTopStyle',
    'borderRadius', 'fontFamily', 'fontSize', 'fontWeight', 'boxShadow',
    'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft', 'width'
  ];
  const cardProperties = [
    'backgroundColor', 'color', 'borderTopColor', 'borderTopWidth', 'borderTopStyle',
    'borderRadius', 'boxShadow', 'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft'
  ];
  const miniProperties = [
    'backgroundColor', 'color', 'borderTopColor', 'borderTopWidth', 'borderRadius',
    'fontFamily', 'fontSize', 'fontWeight', 'boxShadow', 'paddingTop', 'paddingBottom'
  ];
  const subProperties = ['color', 'fontFamily', 'fontSize', 'fontWeight', 'lineHeight'];

  async function computed(selector, properties) {
    return appFrame.locator(selector).first().evaluate((node, props) => {
      const style = getComputedStyle(node);
      return Object.fromEntries(props.map((name) => [name, style[name]]));
    }, properties);
  }

  async function assertNativeMatch(label) {
    assert.deepEqual(
      await computed('#pmpAutomatedPlanEntryV1', buttonProperties),
      await computed('#control button.big:not(#pmpAutomatedPlanEntryV1)', buttonProperties),
      `${label}: main entry does not match a native Control Room big button`
    );
    assert.deepEqual(
      await computed('#pmpAutomatedPlanOverlayV1 .card', cardProperties),
      await computed('#control > .card', cardProperties),
      `${label}: Automated Plan card does not match the Control Room card`
    );
    assert.deepEqual(
      await computed('#pmpAutomatedPlanOverlayV1 button.mini', miniProperties),
      await computed('#colorPanel button.mini', miniProperties),
      `${label}: Automated Plan small control does not match a native small control`
    );
    assert.deepEqual(
      await computed('#pmpAutomatedPlanOverlayV1 .sub', subProperties),
      await computed('#control > .card > .sub', subProperties),
      `${label}: Automated Plan secondary text does not match native secondary text`
    );
  }

  await appFrame.locator('#pmpAutomatedPlanEntryV1').click();
  await appFrame.waitForSelector('#pmpAutomatedPlanOverlayV1', { timeout: 10000 });
  await appFrame.waitForFunction(() => {
    const legacy = document.getElementById('pmp-automated-plan-room-v1-style');
    return Boolean(document.querySelector('#pmpAutomatedPlanOverlayV1 .wrap') && document.querySelector('#pmpAutomatedPlanOverlayV1 .card') && legacy && legacy.disabled);
  }, null, { timeout: 10000 });

  await assertNativeMatch('default live theme');

  const profiles = [
    {
      name: 'high contrast',
      vars: { '--a': '#f8d24a', '--floor': '#101010', '--card': '#202020', '--line': '#ffffff', '--text': '#ffffff', '--muted': '#f0f0f0', '--panel': '#050505', '--buttonText': '#101010', '--borderWidth': '4px', '--shadow': '0 0 0 #0000' }
    },
    {
      name: 'soft contrast',
      vars: { '--a': '#b9d9ff', '--floor': '#efe6de', '--card': '#fffaf6', '--line': '#4d5660', '--text': '#17202a', '--muted': '#45515c', '--panel': '#27313c', '--buttonText': '#17202a', '--borderWidth': '1px', '--shadow': '0 8px 20px #0002' }
    }
  ];

  for (const profile of profiles) {
    await appFrame.evaluate((vars) => {
      for (const [key, value] of Object.entries(vars)) document.documentElement.style.setProperty(key, value);
    }, profile.vars);
    await page.waitForTimeout(250);
    await assertNativeMatch(profile.name);
  }

  await appFrame.locator('#pmpAutomatedPlanOverlayV1 button.mini', { hasText: 'Details' }).click();
  const detailsText = await appFrame.locator('#pmpAutomatedPlanDetailsV1').innerText();
  assert.match(detailsText, /Internal plan\s+packet_01_5/);
  assert.match(detailsText, /Last completed\s+pass_002/);
  assert.match(detailsText, /Next unit\s+pass_003/);
  assert.match(detailsText, /Free-only lock\s+\$0 additional API usage/);
  assert.match(detailsText, /Execution enabled\s+no/);

  await appFrame.locator('#pmpAutomatedPlanOverlayV1 button.big', { hasText: 'Back to Control Room' }).click();
  await appFrame.waitForSelector('#pmpAutomatedPlanOverlayV1', { state: 'detached', timeout: 10000 });

  console.log(JSON.stringify({
    result: 'PASS',
    real_app: 'pmp-current-inner-cleanbug-rgcontrols-v6.html#control',
    control_room_entry_count: 1,
    native_style_profiles_tested: ['default live theme', ...profiles.map((p) => p.name)],
    internal_plan: 'packet_01_5',
    last_completed: 'pass_002',
    next_unit: 'pass_003',
    execution_enabled: false
  }, null, 2));
} finally {
  await browser.close();
}
