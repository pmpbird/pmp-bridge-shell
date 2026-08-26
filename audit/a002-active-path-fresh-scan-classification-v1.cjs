const fs = require('fs');
const { chromium } = require('playwright');

const base = process.env.A002_BASE_URL || 'http://127.0.0.1:8000/';
const resultPath = process.env.A002_ATLAS_RESULT_PATH || 'a002-active-path-fresh-scan-results.json';
const machineSource = fs.readFileSync('pmp-active-path-discovery-machine-v1.js', 'utf8');
const exporterSource = fs.readFileSync('pmp-active-path-discovery-zip-export-v2.js', 'utf8');
const syntheticMap = {
  type: 'PMP_CURRENT_APP_MAP', app_version: 'A002-ATLAS-SYNTHETIC', route_epoch: 'A002-ATLAS-20260825A',
  entry: {path:'root.html'}, route_guardian:{path:'root.html'}, route_guardian_loader:{path:'root.html'}, current_app:{path:'app.html'},
  runtime_chain:{app:{path:'app.html'}},
  tool_routes:{support:{path:'support.html'}},
  recovery_routes:{recovery:{path:'recovery.html'}},
  historic_routes:{historic:{path:'historic.html'}},
  known_broken_absent_claims:{'known-absent.html':'absent_do_not_route'}
};

(async()=>{
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage();
  await page.route('**/*', async route => {
    const url = new URL(route.request().url());
    const path = url.pathname.split('/').filter(Boolean).pop() || '';
    if (path === 'pmp-current-map-v12.json') return route.fulfill({status:200, contentType:'application/json', body:JSON.stringify(syntheticMap)});
    if (path === 'root.html') return route.fulfill({status:200, contentType:'text/html', body:"<a href='unregistered.js'>u</a><a href='missing-current.js'>m</a><a href='policy.json'>p</a>"});
    if (['app.html','support.html','recovery.html','historic.html','unregistered.js'].includes(path)) return route.fulfill({status:200, contentType:'text/plain', body:'ok'});
    if (path === 'missing-current.js' || path === 'known-absent.html') return route.fulfill({status:404, contentType:'text/plain', body:'missing'});
    if (path === 'policy.json') return route.fulfill({status:412, contentType:'text/plain', body:'integrity precondition rejected'});
    return route.continue();
  });
  await page.goto(base + 'pmp-pages-publish-smoke-v1.html', {waitUntil:'domcontentloaded'});
  await page.setContent('<!doctype html><html><body><section id="control"><div class="card"></div></section></body></html>');
  await page.evaluate(() => {
    localStorage.setItem('pmp_active_path_discovery_report_v1', JSON.stringify({type:'PMP_ACTIVE_PATH_DISCOVERY_REPORT_V1',version:'1.3.0-canonical-event-driven-mount-20260727B',scan_id:'old-scan',hard_missing_count:23,dead_reference_count:10,freeze_gate:{pass:false}}));
    localStorage.setItem('pmp_mount_registry_v1', JSON.stringify({files:[
      {path:'pmp-current-map-v12.json'},{path:'root.html'},{path:'app.html'},{path:'support.html'},{path:'recovery.html'},{path:'historic.html'}
    ]}));
  });
  await page.addScriptTag({content: machineSource});
  await page.addScriptTag({content: exporterSource});
  const first = await page.evaluate(() => window.PMPActivePathDiscoveryZipExportV2.runDiscovery('a002_first'));
  const second = await page.evaluate(() => window.PMPActivePathDiscoveryZipExportV2.runDiscovery('a002_second'));
  const checks = {
    fresh_not_stored: first.scan_id && first.scan_id !== 'old-scan',
    new_id_each_run: second.scan_id && second.scan_id !== first.scan_id,
    exact_version: first.version === '1.5.0-served-a003-reference-truth-20260826A',
    exact_revision: first.revision === '1.1.0-served-a003-reference-truth-20260826A',
    map_policy: first.map_policy && first.map_policy.source === 'CURRENT_MAP_FETCH' && first.map_policy.fetch_ok === true,
    true_404_hard_missing: first.hard_missing.includes('missing-current.js'),
    dead_is_missing_only: first.dead_references.some(x=>x.path==='missing-current.js' && x.classification==='MISSING') && !first.dead_references.some(x=>x.path==='policy.json'),
    precondition_separate: first.precondition_rejected.some(x=>x.path==='policy.json' && x.status===412 && x.classification==='PRECONDITION_REJECTED'),
    reachable_gap: first.atlas_registry_gap.includes('unregistered.js'),
    no_gap_as_hard_missing: !first.hard_missing.includes('unregistered.js'),
    known_absent_not_hard: !first.hard_missing.includes('known-absent.html'),
    fail_closed_current_failure: first.freeze_gate && first.freeze_gate.pass === false,
    bound_request: first.requested_scan_id === first.scan_id && second.requested_scan_id === second.scan_id
  };
  const failed = Object.entries(checks).filter(([,ok])=>!ok).map(([name])=>name);
  const result = {type:'PMP_A002_ACTIVE_PATH_FRESH_SCAN_CLASSIFICATION_RESULT_V1',status:failed.length?'FAIL':'PASS',checks,failed,first:{scan_id:first.scan_id,hard_missing:first.hard_missing,atlas_registry_gap:first.atlas_registry_gap,precondition_rejected:first.precondition_rejected,dead_references:first.dead_references,map_policy:first.map_policy},second_scan_id:second.scan_id};
  fs.writeFileSync(resultPath, JSON.stringify(result,null,2)+'\n');
  await browser.close();
  console.log(JSON.stringify({status:result.status,failed}));
  process.exit(failed.length?1:0);
})().catch(error=>{try{fs.writeFileSync(resultPath,JSON.stringify({status:'FAIL',error:String(error&&error.stack||error)},null,2)+'\n')}catch(_){};console.error(error);process.exit(1)});
