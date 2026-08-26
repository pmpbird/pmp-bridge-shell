const fs=require('fs');
const {chromium}=require('playwright');

const resultPath=process.env.A002_ATLAS_REGISTRY_RESULT_PATH||'a002-atlas-registry-completeness-semantics-results.json';
const source=fs.readFileSync('pmp-mount-registry-v1.js','utf8');
const expectedOutside=new Set([
  'GO_TO_SAFETY.html','Index.html','automation/controller/v1/controller-contract.json','automation/engine/v1/engine-policy.json','automation/engine/v1/free-in-app-engine-contract.json','automation/engine/v1/universal-contract.json','automation/plans/packet-01-5.v1.json','automation/state/active-plan.json','automation/state/controller-status.json','automation/state/free-in-app-engine-status.json','automation/state/usage-ledger.json','bm.html','bridge-cloak.html','bug-memory-current-clean-v2.html','bug-memory-hub-link-v1.html','hard-fresh.html','pmp-continuous-run-helper-conflict-blocker-v1.js','pmp-current-inner.html','pmp-helper-bank-live-inspector-v1.js','pmp-helper-symptom-watcher-v1.js','pmp-inventory-eyes-manifest-v1.0.0.json','pmp-p15-helper-tidy-v1.js'
]);

(async()=>{
  const browser=await chromium.launch({headless:true});
  const page=await browser.newPage();
  await page.setContent('<!doctype html><html><body><iframe id="app"></iframe></body></html>');
  await page.addScriptTag({content:source});
  const registry=await page.evaluate(()=>window.PMPMountRegistryV1.registry());
  const outside=new Set(registry.repo_file_classification.INTENTIONAL_OUTSIDE_ACTIVE_ATLAS||[]);
  const recovery=new Set(registry.repo_file_classification.RECOVERY_REACHABLE||[]);
  const active=new Set(registry.repo_file_classification.ACTIVE_CURRENT_APP||[]);
  const support=new Set(registry.repo_file_classification.SUPPORT_REACHABLE||[]);
  const slots=new Set((registry.slots||[]).flatMap(x=>x.files||[]));
  const fileRows=new Map((registry.files||[]).map(x=>[x.path,x.bucket]));
  const checks={
    exact_version:registry.version==='1.7.0-registry-completeness-semantics-20260826A',
    six_semantic_buckets:(registry.atlas_buckets||[]).length===6,
    recovery_bucket_present:(registry.atlas_buckets||[]).some(x=>x.id==='RECOVERY_REACHABLE'),
    intentional_outside_bucket_present:(registry.atlas_buckets||[]).some(x=>x.id==='INTENTIONAL_OUTSIDE_ACTIVE_ATLAS'),
    exact_recovery_count:recovery.size===10,
    exact_outside_count:outside.size===22,
    exact_outside_identity:outside.size===expectedOutside.size&&[...expectedOutside].every(x=>outside.has(x)),
    outside_has_no_slots:[...outside].every(x=>!slots.has(x)),
    outside_rows_known:[...outside].every(x=>fileRows.get(x)==='INTENTIONAL_OUTSIDE_ACTIVE_ATLAS'),
    recovery_controller_reclassified:recovery.has('pmp-route-guardian-last-good-clean-v1.js')&&!active.has('pmp-route-guardian-last-good-clean-v1.js'),
    control_plane_registered:active.has('pmp-runtime-integrity-manifest-v1.json')&&active.has('pmp-integrity-service-worker-v1.js')&&active.has('pmp-app-orchestrator-ownership-registry-v1.json'),
    current_tools_registered:support.has('code-safety-v13.html')&&support.has('pmp-current-inner-cleanbug-rgcontrols-v2.html')&&support.has('resident.html'),
    no_authority_by_presence:/no authority is granted by registry presence/i.test(registry.rule||''),
    passive_mode:registry.mode==='active_path_registry_only'
  };
  const failed=Object.entries(checks).filter(([,ok])=>!ok).map(([k])=>k);
  const result={type:'PMP_A002_ATLAS_REGISTRY_COMPLETENESS_SEMANTICS_RESULT_V1',status:failed.length?'FAIL':'PASS',checks,failed,counts:{files:(registry.files||[]).length,slots:(registry.slots||[]).length,recovery:recovery.size,intentional_outside:outside.size}};
  fs.writeFileSync(resultPath,JSON.stringify(result,null,2)+'\n');
  await browser.close();
  console.log(JSON.stringify({status:result.status,failed,counts:result.counts}));
  process.exit(failed.length?1:0);
})().catch(error=>{try{fs.writeFileSync(resultPath,JSON.stringify({status:'FAIL',error:String(error&&error.stack||error)},null,2)+'\n')}catch(_){};console.error(error);process.exit(1)});
