import { chromium } from 'playwright';
import fs from 'node:fs';
const base=process.env.P2B_BASE_URL||'http://127.0.0.1:8000';
const output=process.env.P2B_RESULT_PATH||'pass2-p2b-adversarial-result.json';
const browser=await chromium.launch({headless:true});
let probeRequests=0;
try{
 const page=await browser.newPage();
 page.on('request',request=>{if(new URL(request.url()).pathname==='/p2b-side-effect-probe')probeRequests+=1});
 await page.goto(base+'/audit/pass2/fixtures/p2b-authority-gate-adversarial.html',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.__P2B_RESULT__&&window.__P2B_RESULT__.status,{timeout:30000});
 const result=await page.evaluate(()=>window.__P2B_RESULT__);
 result.side_effect_probe_requests=probeRequests;
 result.tests.push({name:'blocked fetch produced zero network requests',pass:probeRequests===0,detail:{probeRequests}});
 result.tests_total=result.tests.length;
 result.tests_passed=result.tests.filter(t=>t.pass).length;
 result.tests_failed=result.tests_total-result.tests_passed;
 result.status=result.tests_failed===0&&!result.fatal_error?'PASS':'FAIL';
 result.decision=result.status==='PASS'?'P2B_GATE_AND_FIXTURES_PASS_READY_FOR_ACTIVE_CHAIN_INTEGRATION':'STOP_P2B_GATE_FAILED';
 fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({status:result.status,tests_total:result.tests_total,tests_passed:result.tests_passed,tests_failed:result.tests_failed,probe_requests:probeRequests,output}));
 if(result.status!=='PASS')process.exitCode=1;
}finally{await browser.close()}
