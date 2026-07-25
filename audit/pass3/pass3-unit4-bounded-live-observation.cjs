#!/usr/bin/env node
const { chromium } = require('playwright');
const fs = require('fs');
const http = require('http');
const path = require('path');
const root = path.resolve(__dirname, '../..');
const port = 4174;
const mime={'.html':'text/html','.js':'text/javascript','.json':'application/json','.css':'text/css'};
const server=http.createServer((req,res)=>{
  const u=new URL(req.url,'http://127.0.0.1');
  let rel=decodeURIComponent(u.pathname).replace(/^\/+/, '')||'pmp-app-current.html';
  const file=path.resolve(root,rel);
  if(!file.startsWith(root)||!fs.existsSync(file)||fs.statSync(file).isDirectory()){res.writeHead(404);return res.end('not found')}
  res.writeHead(200,{'content-type':mime[path.extname(file)]||'application/octet-stream','cache-control':'no-store'});
  fs.createReadStream(file).pipe(res);
});
function sleep(ms){return new Promise(r=>setTimeout(r,ms))}
(async()=>{
  await new Promise(r=>server.listen(port,'127.0.0.1',r));
  const browser=await chromium.launch({headless:true});
  const context=await browser.newContext();
  const page=await context.newPage();
  const base=`http://127.0.0.1:${port}/`;
  const result={type:'PMP_PASS3_UNIT4_BOUNDED_LIVE_OBSERVATION_V1',canonical:null,invalid_probe:null,claim_ceiling:'bounded live current-path observation only'};
  try{
    await page.goto(base+'pmp-app-current.html',{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>{
      try{return JSON.parse(localStorage.getItem('pmp_a003_bootstrap_receipt_v1')||'null')?.status==='PASS'}catch(e){return false}
    },null,{timeout:35000});
    const deadline=Date.now()+30000;
    let currentFrame=null, guardianFrame=null;
    while(Date.now()<deadline){
      for(const f of page.frames()){
        const u=f.url();
        if(u.includes('pmp-route-guardian-current-loader-v22.html')) guardianFrame=f;
        if(u.includes('pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html')) currentFrame=f;
      }
      if(currentFrame) break;
      if(guardianFrame){
        const run=await guardianFrame.$('#openBtn');
        if(run) { try{await run.click()}catch(e){} }
      }
      await sleep(300);
    }
    if(!currentFrame) throw new Error('canonical current_app destination was not observed');
    const appOrchestratorAcknowledged=await currentFrame.evaluate(()=>{
      const scripts=[...document.scripts].map(s=>s.src||'');
      const body=(document.body&&document.body.innerText)||'';
      return scripts.some(s=>/orchestrator/i.test(s))||/orchestrator/i.test(body)||!!window.PMPAppOrchestrator;
    });
    result.canonical={route_guardian:'pmp-route-guardian-current-loader-v22.html',current_app:'pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html',consumer_accepted_before_navigation:true,app_orchestrator_acknowledged:appOrchestratorAcknowledged,observed_url:currentFrame.url()};
    if(!appOrchestratorAcknowledged) throw new Error('App Orchestrator was not acknowledged at current_app boundary');
    const probe=await context.newPage();
    await probe.goto(base+'pmp-app-current.html',{waitUntil:'domcontentloaded'});
    await probe.waitForFunction(()=>{
      try{return JSON.parse(localStorage.getItem('pmp_a003_bootstrap_receipt_v1')||'null')?.status==='PASS'}catch(e){return false}
    },null,{timeout:35000});
    await probe.goto(base+'pmp-route-guardian-current-loader-v22.html',{waitUntil:'domcontentloaded'});
    const beforeUrl=probe.url();
    const beforeStorage=await probe.evaluate(()=>JSON.stringify(localStorage));
    const invalid=await probe.evaluate(async()=>{
      const resolver=window.PMPCurrentRouteResolver;
      if(!resolver) throw new Error('resolver unavailable');
      const loaded=await resolver.load();
      const valid=resolver.resolve(loaded.map,'current_app');
      const bad=Object.assign({},valid,{map_version:'historical-map-version'});
      try{ consumeCurrentAppHandoff(loaded,bad); return {blocked:false}; }
      catch(error){ return {blocked:true,code:String(error&&error.code||error&&error.message||error)}; }
    });
    const afterUrl=probe.url();
    const afterStorage=await probe.evaluate(()=>JSON.stringify(localStorage));
    result.invalid_probe={mutation:'map_version=historical-map-version',blocked_before_navigation:invalid.blocked===true&&beforeUrl===afterUrl,navigation_assignments:beforeUrl===afterUrl?0:1,persisted_user_data_writes:beforeStorage===afterStorage?0:1,diagnostic_code:invalid.code||''};
    if(!result.invalid_probe.blocked_before_navigation||result.invalid_probe.navigation_assignments!==0||result.invalid_probe.persisted_user_data_writes!==0) throw new Error('invalid probe did not fail closed');
    fs.writeFileSync(path.join(root,'audit/pass3/pass3-unit4-live-observation-result.json'),JSON.stringify(result,null,2)+'\n');
    console.log(JSON.stringify(result,null,2));
  }finally{
    await browser.close();
    await new Promise(r=>server.close(r));
  }
})().catch(e=>{
  try{
    fs.writeFileSync(path.join(root,'audit/pass3/pass3-unit4-live-observation-result.json'),JSON.stringify({
      type:'PMP_PASS3_UNIT4_BOUNDED_LIVE_OBSERVATION_V1',
      status:'FAIL',
      error:{name:String(e&&e.name||'Error'),message:String(e&&e.message||e),stack:String(e&&e.stack||'')},
      claim_ceiling:'bounded live current-path observation only'
    },null,2)+'\n');
  }catch(_e){}
  console.error(e);
  process.exit(1);
});
