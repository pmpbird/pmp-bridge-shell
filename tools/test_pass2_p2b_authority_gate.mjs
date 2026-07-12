import { chromium } from 'playwright';
import fs from 'node:fs';
const base=process.env.P2B_BASE_URL||'http://127.0.0.1:8000';
const output=process.env.P2B_RESULT_PATH||'pass2-p2b-adversarial-result.json';
const browser=await chromium.launch({headless:true});
let probeRequests=0;
try{
 const page=await browser.newPage();
 page.on('request',request=>{if(new URL(request.url()).pathname==='/p2b-side-effect-probe')probeRequests+=1});
 let resolveResult,rejectResult;
 const resultPromise=new Promise((resolve,reject)=>{resolveResult=resolve;rejectResult=reject});
 const timeout=setTimeout(()=>rejectResult(new Error('Timed out waiting for P2-B console result.')),30000);
 page.on('console',message=>{
   const text=message.text();
   if(!text.startsWith('P2B_RESULT:'))return;
   try{clearTimeout(timeout);resolveResult(JSON.parse(text.slice('P2B_RESULT:'.length)))}catch(error){clearTimeout(timeout);rejectResult(error)}
 });
 await page.goto(base+'/audit/pass2/fixtures/p2b-authority-gate-adversarial.html',{waitUntil:'domcontentloaded'});
 const result=await resultPromise;
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
