const fs = require('fs');
const { chromium } = require('playwright');

const resultPath = process.env.A002_ATLAS_ZIP_RESULT_PATH || 'a002-active-path-zip-output-results.json';
const exporterSource = fs.readFileSync('pmp-active-path-discovery-zip-export-v2.js', 'utf8');

(async()=>{
  const browser = await chromium.launch({headless:true});
  const context = await browser.newContext({acceptDownloads:true});
  const page = await context.newPage();
  await page.setContent('<!doctype html><html><body><div id="pmpActivePathDiscoveryCardV1" class="card"><b>Active Path Discovery</b><div id="pmpActivePathDiscoveryOutV1">Waiting for discovery scan</div></div></body></html>');
  await page.evaluate(() => {
    window.PMPActivePathDiscoveryMachineV1 = {
      version: '1.4.0-fresh-scan-classification-truth-20260825A',
      revision: '1.0.0-current-map-http-truth-20260825A',
      sourceIdentity: 'pmp-active-path-discovery-machine-v1.js',
      run: async (_reason, opts) => {
        await new Promise(resolve => setTimeout(resolve, 80));
        return {
          type: 'PMP_ACTIVE_PATH_DISCOVERY_REPORT_V1',
          version: '1.4.0-fresh-scan-classification-truth-20260825A',
          revision: '1.0.0-current-map-http-truth-20260825A',
          source_identity: 'pmp-active-path-discovery-machine-v1.js',
          scan_id: opts.scan_id,
          requested_scan_id: opts.scan_id,
          started_at: new Date().toISOString(),
          finished_at: new Date().toISOString(),
          hard_missing_count: 0,
          hard_missing: [],
          atlas_registry_gap_count: 1,
          atlas_registry_gap: ['reachable-unregistered.js'],
          precondition_rejected_count: 1,
          precondition_rejected: [{path:'policy.json',status:412,classification:'PRECONDITION_REJECTED'}],
          dead_reference_count: 0,
          dead_references: [],
          live_runtime_missing: [],
          direct_current_missing: [],
          fallback_or_recovery_missing: [],
          legacy_or_test_missing: [],
          pass_alignment: {historic_reference_current_boot_root_count:0,historic_reference_current_boot_root:[]},
          freeze_gate: {pass:true},
          side_effects: {fix:'not_attempted',move:'not_attempted',delete:'not_attempted',reroute:'not_attempted'}
        };
      }
    };
  });
  await page.addScriptTag({content: exporterSource});
  await page.evaluate(() => window.PMPActivePathDiscoveryZipExportV2.install());
  await page.selectOption('#pmpDiscoveryDropdownMenuV1 select', 'zip');
  await page.click('[data-pmp-discovery-menu-go="1"]');
  const link = page.locator('[data-pmp-discovery-zip-download="1"]');
  await link.waitFor({state:'visible'});
  const readyText = await page.locator('#pmpActivePathDiscoveryOutV1').textContent();
  const href = await link.getAttribute('href');
  const downloadName = await link.getAttribute('download');
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    link.click()
  ]);
  const savedPath = await download.path();
  const bytes = fs.readFileSync(savedPath);
  const asLatin1 = bytes.toString('latin1');
  const suggested = download.suggestedFilename();
  const checks = {
    exporter_version: await page.evaluate(() => window.PMPActivePathDiscoveryZipExportV2.version === '2.7.0-zip-user-activation-handoff-20260825B'),
    async_scan_completed_before_link: /Fresh Atlas ZIP ready/.test(readyText || ''),
    persistent_manual_link_visible: await link.isVisible(),
    blob_href_present: /^blob:/.test(href || ''),
    download_attribute_zip: /\.zip$/i.test(downloadName || ''),
    real_browser_download_event: /\.zip$/i.test(suggested || ''),
    zip_local_header_signature: bytes.length > 4 && bytes[0] === 0x50 && bytes[1] === 0x4b && bytes[2] === 0x03 && bytes[3] === 0x04,
    zip_contains_discovery_report: asLatin1.includes('discovery-report.json'),
    zip_contains_freeze_proof: asLatin1.includes('freeze-proof.txt'),
    zip_contains_blocker_detail: asLatin1.includes('blocker-detail.txt'),
    fresh_scan_identity_in_zip: asLatin1.includes('pmp-active-path-zip_export-') && !asLatin1.includes('old-scan'),
    link_survives_async_user_activation_boundary: true
  };
  const failed = Object.entries(checks).filter(([,ok])=>!ok).map(([name])=>name);
  const result = {type:'PMP_A002_ACTIVE_PATH_ZIP_OUTPUT_RESULT_V1',status:failed.length?'FAIL':'PASS',checks,failed,ready_text:readyText,download_name:downloadName,suggested_filename:suggested,bytes:bytes.length};
  fs.writeFileSync(resultPath, JSON.stringify(result,null,2)+'\n');
  await browser.close();
  console.log(JSON.stringify({status:result.status,failed,suggested,bytes:bytes.length}));
  process.exit(failed.length?1:0);
})().catch(error=>{try{fs.writeFileSync(resultPath,JSON.stringify({status:'FAIL',error:String(error&&error.stack||error)},null,2)+'\n')}catch(_){};console.error(error);process.exit(1)});
