'use strict';
const fs = require('fs');
const { chromium } = require('playwright');

const BASE = process.env.A002_BASE_URL || 'http://127.0.0.1:8000/';
const RESULT_PATH = process.env.A002_DIAGNOSTICS_RESULT_PATH || 'a002-whole-app-diagnostics-results.json';
const CURRENT = 'pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html';
const REQUIRED_BOOT_VERSION = '3.2.0-transactional-versioned-bcd-bootstrap-20260801B';
const REQUIRED_BCD_VERSION = '1.1.0-final-two-live-proof-20260801A';
const SECTIONS = [
  'bridge_system',
  'library_system',
  'bank_system',
  'continuous_run_system',
  'errors_bug_watch_visual_stability'
];

const results = [];
const runtimeErrors = [];
let fatalError = null;

function errorValue(error) {
  return {
    name: String(error?.name || 'Error'),
    message: String(error?.message || error),
    stack: String(error?.stack || '')
  };
}
function record(name, pass, detail = {}) {
  results.push({ name, pass: !!pass, detail, at: new Date().toISOString() });
  console.log(`${pass ? 'PASS' : 'FAIL'} ${name} ${JSON.stringify(detail)}`);
}
function writeOutput() {
  const output = {
    type: 'PMP_A002_WHOLE_APP_DIAGNOSTICS_CERTIFICATION_V3',
    generated_at: new Date().toISOString(),
    base_url: BASE,
    required_bootstrap_version: REQUIRED_BOOT_VERSION,
    required_bcd_version: REQUIRED_BCD_VERSION,
    required_sections: SECTIONS,
    tests_total: results.length,
    tests_passed: results.filter(row => row.pass).length,
    tests_failed: results.filter(row => !row.pass).length,
    runtime_errors: runtimeErrors,
    fatal_error: fatalError,
    results
  };
  fs.writeFileSync(RESULT_PATH, JSON.stringify(output, null, 2));
  console.log(`A002_DIAGNOSTICS_RESULT_WRITTEN ${RESULT_PATH} ${JSON.stringify({
    tests_total: output.tests_total,
    tests_passed: output.tests_passed,
    tests_failed: output.tests_failed,
    runtime_errors: output.runtime_errors.length,
    fatal_error: !!fatalError
  })}`);
}
async function waitForFrame(page, pattern, timeout = 40000) {
  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    const frame = page.frames().find(candidate => pattern.test(candidate.url()));
    if (frame) return frame;
    await page.waitForTimeout(250);
  }
  throw new Error(`frame not found: ${pattern}`);
}
async function enterCurrentApp(page) {
  await page.goto(BASE + 'pmp-app-current.html#control', { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => {
    try {
      return JSON.parse(localStorage.getItem('pmp_a003_bootstrap_receipt_v1') || 'null')?.status === 'PASS';
    } catch {
      return false;
    }
  }, null, { timeout: 40000 });

  const guardian = await waitForFrame(page, /pmp-route-guardian-current-loader-v22\.html/);
  await guardian.click('#openBtn', { force: true });
  await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#control', { timeout: 40000 });

  // v30 direct boot is itself the current home surface. A nested historic
  // pmp-home-single-v6 frame is not required and must not gate Diagnostics.
  await page.waitForFunction(() => {
    const api = window.PMPCurrentBCDDiagnosticsBootstrapV1;
    return api && typeof api.run === 'function';
  }, null, { timeout: 45000 });
  await page.waitForTimeout(7000);
}
async function findRetiredTraceControls(page) {
  const found = [];
  for (const frame of page.frames()) {
    try {
      const count = await frame
        .locator('#pmpWholeAppHealthLayoutTraceV1, [data-pmp-whole-app-health-layout-trace]')
        .count();
      if (count) found.push({ url: frame.url(), count });
    } catch {}
  }
  return found;
}

(async () => {
  let browser = null;
  try {
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ serviceWorkers: 'allow' });
    const page = await context.newPage();
    page.setDefaultTimeout(40000);
    page.on('pageerror', error => runtimeErrors.push({ type: 'pageerror', ...errorValue(error) }));
    page.on('console', message => {
      if (message.type() === 'error') runtimeErrors.push({ type: 'console', message: message.text() });
    });

    await enterCurrentApp(page);
    const frameUrls = page.frames().map(frame => frame.url());
    record('current-direct-boot-surface-ready',
      new URL(page.url()).pathname.endsWith('/' + CURRENT) && new URL(page.url()).hash === '#control',
      { page_url: page.url(), frame_urls: frameUrls }
    );

    const state = await page.evaluate(async ({ requiredBootVersion, requiredBcdVersion, sections }) => {
      const parse = key => {
        try { return JSON.parse(localStorage.getItem(key) || 'null'); }
        catch { return null; }
      };
      const bootstrapApi = window.PMPCurrentBCDDiagnosticsBootstrapV1 || null;
      const runResult = bootstrapApi && typeof bootstrapApi.run === 'function'
        ? await bootstrapApi.run('a002_whole_app_diagnostics_certification_v3')
        : null;
      return {
        requiredBootVersion,
        requiredBcdVersion,
        sections,
        bootstrapApiVersion: bootstrapApi?.version || null,
        runResult,
        bootstrapReceipt: parse('pmp_current_bcd_diagnostics_bootstrap_v1_receipt'),
        bcdReceipt: parse('pmp_diagnostic_coverage_passes_bcd_v1_receipt'),
        journalReceipt: parse('pmp_diagnostic_journal_v1_receipt'),
        journalViewReceipt: parse('pmp_diagnostic_journal_view_v1_receipt'),
        continuousReceipt: parse('pmp_continuous_run_canonical_level_receipt_v1')
      };
    }, {
      requiredBootVersion: REQUIRED_BOOT_VERSION,
      requiredBcdVersion: REQUIRED_BCD_VERSION,
      sections: SECTIONS
    });

    record('transactional-bootstrap-api-current',
      state.bootstrapApiVersion === REQUIRED_BOOT_VERSION,
      { observed: state.bootstrapApiVersion, required: REQUIRED_BOOT_VERSION }
    );

    const completed = Array.isArray(state.bootstrapReceipt?.complete_sections)
      ? state.bootstrapReceipt.complete_sections
      : [];
    record('transactional-bootstrap-published-complete-current-receipt',
      state.runResult?.status === 'PASS' &&
      state.bootstrapReceipt?.status === 'PASS' &&
      state.bootstrapReceipt?.observed_api_version === REQUIRED_BCD_VERSION &&
      state.bootstrapReceipt?.observed_receipt_version === REQUIRED_BCD_VERSION &&
      SECTIONS.every(section => completed.includes(section)),
      { run_result: state.runResult, bootstrap_receipt: state.bootstrapReceipt }
    );
    record('passes-bcd-receipt-version-current',
      state.bcdReceipt?.version === REQUIRED_BCD_VERSION,
      { observed: state.bcdReceipt?.version || null, required: REQUIRED_BCD_VERSION }
    );

    for (const section of SECTIONS) {
      const value = state.bcdReceipt?.[section] || null;
      record(`whole-app-section-pass:${section}`,
        value?.status === 'PASS',
        {
          status: value?.status || 'MISSING',
          type: value?.type || null,
          issues: Array.isArray(value?.issues) ? value.issues : null,
          checks: value?.checks || null
        }
      );
    }

    record('passes-bcd-overall-pass',
      state.bcdReceipt?.status === 'PASS',
      { status: state.bcdReceipt?.status || 'MISSING', reason: state.bcdReceipt?.reason || null }
    );
    record('diagnostic-journal-current-session-proof',
      state.journalReceipt?.status === 'PASS' && state.journalViewReceipt?.available === true,
      { journal: state.journalReceipt, journal_view: state.journalViewReceipt }
    );
    record('continuous-run-canonical-32-level-proof',
      state.continuousReceipt?.status === 'PASS' &&
      state.continuousReceipt?.expected_level_count === 32 &&
      Array.isArray(state.continuousReceipt?.expected_levels) &&
      state.continuousReceipt.expected_levels.length === 32,
      { continuous: state.continuousReceipt }
    );

    const traceControls = await findRetiredTraceControls(page);
    record('retired-layout-trace-control-absent', traceControls.length === 0, traceControls);

    const relevantErrors = runtimeErrors.filter(error =>
      /diagnostic|passes[- _]?bcd|journal|continuous|syntaxerror|pmp-diagnostic-coverage-passes-bcd-v1-1-1-0/i
        .test(String(error.message || '') + ' ' + String(error.stack || ''))
    );
    record('no-diagnostics-runtime-errors', relevantErrors.length === 0, relevantErrors);

    if (results.some(row => !row.pass)) {
      throw new Error('Whole App diagnostics certification failed');
    }
  } catch (error) {
    fatalError = errorValue(error);
    console.error(error?.stack || error);
    process.exitCode = 1;
  } finally {
    try { if (browser) await browser.close(); }
    catch (error) {
      if (!fatalError) fatalError = errorValue(error);
      process.exitCode = 1;
    }
    try { writeOutput(); }
    catch (error) {
      console.error(error?.stack || error);
      process.exitCode = 1;
    }
  }
})();
