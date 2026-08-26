const fs=require('fs');
const crypto=require('crypto');
const {chromium}=require('playwright');

const base=process.env.A002_BASE_URL||'http://127.0.0.1:8000/';
const resultPath=process.env.A002_ATLAS_SEAL_RESULT_PATH||'a002-active-path-seal-binding-results.json';
const machineSource=fs.readFileSync('pmp-active-path-discovery-machine-v1.js','utf8');
const syntheticMap={
  type:'PMP_CURRENT_APP_MAP',app_version:'A002-ATLAS-SEAL',route_epoch:'A002-ATLAS-SEAL-20260826A',
  entry:{path:'root.html'},route_guardian:{path:'root.html'},route_guardian_loader:{path:'root.html'},current_app:{path:'app.html'},
  runtime_chain:{app:{path:'app.html'}},tool_routes:{support:{path:'support.html'}},recovery_routes:{recovery:{path:'recovery.html'}},historic_routes:{historic:{path:'historic.html'}},known_broken_absent_claims:{}
};
const manifestBody=JSON.stringify({version:'20260711A-A003-FINAL',runtime_source_set_sha256:'synthetic-runtime-set',records:[{path:'root.html',sha256_hex:'00'}]},null,2)+'\n';
const manifestSha=crypto.createHash('sha256').update(Buffer.from(manifestBody,'utf8')).digest('hex');
const falseBlockers=['metadata.json','packet.json','report.json','PMP_WHOLE_APP_HEALTH_LAYOUT_TRACE.json','TRACE_METADATA.json'];

(async()=>{
  const browser=await chromium.launch({headless:true});
  const page=await browser.newPage();
  await page.route('**/*',async route=>{
    const url=new URL(route.request().url());
    const p=url.pathname.split('/').filter(Boolean).pop()||'';
    if(p==='pmp-current-map-v12.json')return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(syntheticMap)});
    if(p==='pmp-runtime-integrity-manifest-v1.json')return route.fulfill({status:200,contentType:'application/json',body:manifestBody});
    if(p==='root.html')return route.fulfill({status:200,contentType:'text/html',body:"<script src='ref-source.js'></script><a href='unregistered.js'>u</a>"});
    if(p==='ref-source.js')return route.fulfill({status:200,contentType:'text/javascript',body:"/* 'PMP_WHOLE_APP_HEALTH_LAYOUT_TRACE.json' 'TRACE_METADATA.json' */ const outputs=['metadata.json','packet.json','report.json']; fetch('strong-output.json');"});
    if(['app.html','support.html','recovery.html','historic.html','unregistered.js','strong-output.json'].includes(p))return route.fulfill({status:200,contentType:'text/plain',body:'ok'});
    if(falseBlockers.includes(p))return route.fulfill({status:412,contentType:'text/plain',body:'should not be requested'});
    return route.continue();
  });
  await page.goto(base+'pmp-pages-publish-smoke-v1.html',{waitUntil:'domcontentloaded'});
  await page.setContent('<!doctype html><html><body><section id="control"><div class="card"></div></section></body></html>');
  await page.evaluate(()=>{
    localStorage.setItem('pmp_route_guardian_v22_receipt',JSON.stringify({integrity_manifest_sha256:'stale-route-receipt-sha'}));
    localStorage.setItem('pmp_mount_registry_v1',JSON.stringify({files:[
      {path:'pmp-current-map-v12.json'},{path:'root.html'},{path:'app.html'},{path:'support.html'},{path:'recovery.html'},{path:'historic.html'}
    ]}));
  });
  await page.addScriptTag({content:machineSource});
  const report=await page.evaluate(()=>window.PMPActivePathDiscoveryMachineV1.run('a002_seal_binding',{scan_id:'a002-seal-binding-20260826A'}));
  const scanned=new Set((report.scanned||[]).map(x=>x.path));
  const checks={
    exact_version:report.version==='1.5.0-served-a003-reference-truth-20260826A',
    exact_revision:report.revision==='1.1.0-served-a003-reference-truth-20260826A',
    served_manifest_sha:report.runtime_integrity_manifest_sha256===manifestSha,
    stale_receipt_ignored:report.runtime_integrity_manifest_sha256!=='stale-route-receipt-sha',
    manifest_binding:report.runtime_integrity_binding&&report.runtime_integrity_binding.source==='SERVED_A003_MANIFEST'&&report.runtime_integrity_binding.fetch_ok===true&&report.runtime_integrity_binding.scan_id===report.scan_id,
    manifest_runtime_set:report.runtime_integrity_binding&&report.runtime_integrity_binding.runtime_source_set_sha256==='synthetic-runtime-set',
    comment_markers_not_scanned:!scanned.has('PMP_WHOLE_APP_HEALTH_LAYOUT_TRACE.json')&&!scanned.has('TRACE_METADATA.json'),
    weak_outputs_not_scanned:!scanned.has('metadata.json')&&!scanned.has('packet.json')&&!scanned.has('report.json'),
    strong_fetch_preserved:scanned.has('strong-output.json'),
    no_false_current_412:(report.current_precondition_rejected_count||0)===0,
    freeze_pass:report.freeze_gate&&report.freeze_gate.pass===true,
    scan_bound:report.scan_id==='a002-seal-binding-20260826A'&&report.requested_scan_id===report.scan_id
  };
  const failed=Object.entries(checks).filter(([,ok])=>!ok).map(([k])=>k);
  const result={type:'PMP_A002_ACTIVE_PATH_SEAL_BINDING_REFERENCE_TRUTH_RESULT_V1',status:failed.length?'FAIL':'PASS',checks,failed,manifestSha,report:{scan_id:report.scan_id,runtime_integrity_manifest_sha256:report.runtime_integrity_manifest_sha256,runtime_integrity_binding:report.runtime_integrity_binding,current_precondition_rejected_count:report.current_precondition_rejected_count,freeze_gate:report.freeze_gate,scanned_paths:[...scanned]}};
  fs.writeFileSync(resultPath,JSON.stringify(result,null,2)+'\n');
  await browser.close();
  console.log(JSON.stringify({status:result.status,failed}));
  process.exit(failed.length?1:0);
})().catch(error=>{try{fs.writeFileSync(resultPath,JSON.stringify({status:'FAIL',error:String(error&&error.stack||error)},null,2)+'\n')}catch(_){};console.error(error);process.exit(1)});
