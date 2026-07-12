'use strict';
const fs=require('fs'),{chromium}=require('playwright');
const base=process.env.P2C_PROOF_BASE_URL||'http://127.0.0.1:8765/';
const out=process.env.P2C_PROOF_BROWSER_RESULT||'/tmp/p2c-proof-browser.json';
const tests=[];function rec(name,pass,detail={}){tests.push({name,pass:!!pass,detail});console.log(`${pass?'PASS':'FAIL'} ${name} ${JSON.stringify(detail)}`)}
(async()=>{
 const browser=await chromium.launch({headless:true});const context=await browser.newContext();const page=await context.newPage();
 const errors=[];page.on('pageerror',e=>errors.push(String(e.message||e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 let navigationError=null;try{await page.goto(base+'pmp-app-current.html#world',{waitUntil:'domcontentloaded',timeout:45000})}catch(e){navigationError=String(e.message||e)}
 await page.waitForTimeout(12000);
 const lock=await page.evaluate(async()=>{try{return await (await fetch('pmp-p2c-production-enforcement-activation-lock-candidate-001.json',{cache:'no-store'})).json()}catch(e){return{error:String(e)}}});
 rec('activation lock is proof-only authorized',lock.authorized===true&&lock.proof_scope==='DISPOSABLE_COPY_ONLY'&&lock.production_active_chain_integration===false,{lock});
 const root=await page.evaluate(()=>{let receipt=null;try{receipt=JSON.parse(localStorage.getItem('pmp_a003_bootstrap_receipt_v1')||'null')}catch{}return{receipt,prelude:!!window.PMPP2CProductionEnforcementPreludeCandidate001,failure:window.PMPP2CProductionEnforcementPreludeFailureCandidate001||null,frame_src:document.querySelector('iframe')?.getAttribute('src')||null,diagnostic:document.getElementById('routeDiagnostic')?.innerText||''}});
 rec('root A-003 bootstrap passes',root.receipt?.status==='PASS',{receipt:root.receipt,diagnostic:root.diagnostic});
 rec('root P2-C prelude is installed',root.prelude===true,{root});
 rec('root P2-C has no fail-closed receipt',!root.failure,{failure:root.failure});
 rec('root navigates through Route Guardian',/pmp-route-guardian-current-loader-v22\.html/.test(root.frame_src||''),{frame_src:root.frame_src});
 const expected=['pmp-route-guardian-current-loader-v22.html','pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html','pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html','pmp-current-inner-cleanbug-rgcontrols-v23.html'];
 const frames=[];
 for(const f of page.frames()){let state={url:f.url()};try{state=await f.evaluate(()=>({url:location.href,receipt:window.PMPP2CProductionEnforcementReceiptCandidate001||null,failure:window.PMPP2CProductionEnforcementPreludeFailureCandidate001||null}))}catch(e){state.error=String(e)}frames.push(state)}
 for(const p of expected){const f=frames.find(x=>(x.url||'').includes(p));rec(`realm present:${p}`,!!f,{frame:f||null});if(f)rec(`realm enforced without prelude failure:${p}`,!!f.receipt&&!f.failure,{receipt:f.receipt,failure:f.failure})}
 rec('no unexpected browser fatal error',!navigationError,{navigationError});
 const result={type:'PMP_P2C_PRODUCTION_SHAPED_ACTIVATION_BROWSER_PROOF_RESULT_001',status:tests.every(t=>t.pass)?'PASS':'FAIL',tests_total:tests.length,tests_passed:tests.filter(t=>t.pass).length,tests_failed:tests.filter(t=>!t.pass).length,tests,frames,errors,navigationError,production_changed:false,proof_scope:'DISPOSABLE_COPY_ONLY'};
 fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');await browser.close();console.log(JSON.stringify({status:result.status,tests:`${result.tests_passed}/${result.tests_total}`,errors:errors.slice(0,10)},null,2));process.exit(result.status==='PASS'?0:1);
})().catch(e=>{fs.writeFileSync(out,JSON.stringify({status:'FAIL',fatal_error:String(e.stack||e),tests},null,2)+'\n');console.error(e);process.exit(1)});
