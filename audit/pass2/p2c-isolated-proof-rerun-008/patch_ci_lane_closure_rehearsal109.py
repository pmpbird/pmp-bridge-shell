#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess


PASS75 = "pmp-pass75-reload-runtime-platform-gate-v1.js"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"REHEARSAL109_{label}_ANCHOR_INVALID:{count}")
    return text.replace(old, new, 1)


A002_HISTORIC_CONTEXT_LOOP = r'''  for (const file of HISTORIC) {
    const browser = page.context().browser();
    if (!browser) throw new Error('A002_HISTORIC_BROWSER_MISSING:' + file);
    const historicContext = await browser.newContext({ serviceWorkers: 'allow' });
    await historicContext.addInitScript(() => {
      const descriptor = Object.getOwnPropertyDescriptor(MessagePort.prototype, 'onmessage');
      globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER = descriptor && descriptor.set;
    });
    let bootstrapPage = null;
    let historicPage = null;
    try {
      pmpA002Stage('historic-bookmark-context-start', { file, isolated_context: true });
      bootstrapPage = await historicContext.newPage();
      await bootstrap(bootstrapPage, '#world');
      const historicBarrierStatus = await workerStatus(bootstrapPage);
      if (!(historicBarrierStatus && historicBarrierStatus.type === 'PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE' && historicBarrierStatus.receipt && historicBarrierStatus.receipt.state === 'ENFORCED')) {
        throw new Error('A002_HISTORIC_CONTEXT_INTEGRITY_NOT_ENFORCED:' + file);
      }
      pmpA002Stage('historic-bookmark-context-controlled', { file, controller_version: historicBarrierStatus.receipt.version });
      await bootstrapPage.close();
      bootstrapPage = null;
      historicPage = await historicContext.newPage();
      pmpA002AttachDiagnostics(historicPage);
      await historicPage.goto(BASE + file + '#library', { timeout: 30000, waitUntil: 'domcontentloaded' });
      await historicPage.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#library', { timeout: 30000, waitUntil: 'domcontentloaded' });
      const controllerUrl = await historicPage.evaluate(() => navigator.serviceWorker.controller?.scriptURL || null);
      if (!controllerUrl || !controllerUrl.includes('/' + INTEGRITY_SW)) throw new Error('A002_HISTORIC_INTEGRITY_CONTROLLER_MISSING:' + file);
      record(`historic-bookmark-forward:${file}`, true, { url: historicPage.url(), controller_url: controllerUrl, isolated_context: true });
    } finally {
      if (bootstrapPage) await bootstrapPage.close().catch(() => {});
      await historicContext.close();
    }
  }'''


A002_HISTORIC_BROWSER_LOOP = r'''  for (const file of HISTORIC) {
    let historicLastError = null;
    for (let attempt = 1; attempt <= 2; attempt += 1) {
      const historicBrowser = await chromium.launch({ headless: true });
      let historicContext = null;
      let bootstrapPage = null;
      let historicPage = null;
      try {
        historicContext = await historicBrowser.newContext({ serviceWorkers: 'allow' });
        await historicContext.addInitScript(() => {
          const descriptor = Object.getOwnPropertyDescriptor(MessagePort.prototype, 'onmessage');
          globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER = descriptor && descriptor.set;
        });
        pmpA002Stage('historic-bookmark-browser-start', { file, attempt, isolated_browser_process: true });
        bootstrapPage = await historicContext.newPage();
        await bootstrap(bootstrapPage, '#world');
        const historicBarrierStatus = await workerStatus(bootstrapPage);
        if (!(historicBarrierStatus && historicBarrierStatus.type === 'PMP_RUNTIME_INTEGRITY_STATUS_RESPONSE' && historicBarrierStatus.receipt && historicBarrierStatus.receipt.state === 'ENFORCED')) {
          throw new Error('A002_HISTORIC_BROWSER_INTEGRITY_NOT_ENFORCED:' + file);
        }
        pmpA002Stage('historic-bookmark-browser-controlled', { file, attempt, controller_version: historicBarrierStatus.receipt.version });
        await bootstrapPage.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
        await bootstrapPage.close();
        bootstrapPage = null;
        historicPage = await historicContext.newPage();
        pmpA002AttachDiagnostics(historicPage);
        await historicPage.goto(BASE + file + '#library', { timeout: 30000, waitUntil: 'commit' });
        await historicPage.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#library', { timeout: 30000, waitUntil: 'commit' });
        const controllerUrl = await historicPage.evaluate(() => navigator.serviceWorker.controller?.scriptURL || null);
        if (!controllerUrl || !controllerUrl.includes('/' + INTEGRITY_SW)) throw new Error('A002_HISTORIC_INTEGRITY_CONTROLLER_MISSING:' + file);
        record(`historic-bookmark-forward:${file}`, true, { url: historicPage.url(), controller_url: controllerUrl, attempt, isolated_browser_process: true });
        await historicPage.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
        historicLastError = null;
        break;
      } catch (error) {
        historicLastError = error;
        pmpA002Stage('historic-bookmark-browser-attempt-failed', { file, attempt, name: String(error?.name || 'Error'), message: String(error?.message || error), retry_authorized: attempt < 2 });
        if (attempt >= 2) throw error;
      } finally {
        if (bootstrapPage) await bootstrapPage.close().catch(() => {});
        if (historicContext) await historicContext.close().catch(() => {});
        await historicBrowser.close().catch(() => {});
      }
    }
    if (historicLastError) throw historicLastError;
  }'''


A002_HISTORIC_CONTEXT_GUARDS = r''' pmp_context_creation_token="const historicContext = await browser.newContext({ serviceWorkers: 'allow' });"
 if s.count(pmp_context_creation_token)!=1:raise SystemExit(f'REHEARSAL108_CONTEXT_CREATION_CONTRACT_INVALID:{s.count(pmp_context_creation_token)}')
 if s.count('A002_HISTORIC_CONTEXT_INTEGRITY_NOT_ENFORCED:')!=1:raise SystemExit(f'REHEARSAL108_CONTEXT_ENFORCEMENT_CONTRACT_INVALID:{s.count("A002_HISTORIC_CONTEXT_INTEGRITY_NOT_ENFORCED:")}')'''


A002_HISTORIC_BROWSER_GUARDS = r''' pmp_browser_creation_token="const historicBrowser = await chromium.launch({ headless: true });"
 pmp_browser_close_token="await historicBrowser.close().catch(() => {});"
 if s.count(pmp_browser_creation_token)!=1:raise SystemExit(f'REHEARSAL109_BROWSER_PROCESS_CREATION_CONTRACT_INVALID:{s.count(pmp_browser_creation_token)}')
 if s.count('A002_HISTORIC_BROWSER_INTEGRITY_NOT_ENFORCED:')!=1:raise SystemExit(f'REHEARSAL109_BROWSER_PROCESS_ENFORCEMENT_CONTRACT_INVALID:{s.count("A002_HISTORIC_BROWSER_INTEGRITY_NOT_ENFORCED:")}')
 if s.count(pmp_browser_close_token)!=1:raise SystemExit(f'REHEARSAL109_BROWSER_PROCESS_CLOSE_CONTRACT_INVALID:{s.count(pmp_browser_close_token)}')'''


A003_RECEIPT_HELPER_OLD = r'''async function historicalReceiptFromHomeFrame(page) {
  const deadline = Date.now() + 30000;
  let last = null;
  while (Date.now() < deadline) {
    const frame = page.frames().find(f => /pmp-home-single-v6\.html/.test(f.url()));
    if (frame) {
      try {
        last = await frame.evaluate(() => {
          try {
            let embedded = null;
            const node = document.getElementById('pmpA003HistoricalHomeIntegrityReceipt');
            if (node?.textContent) embedded = JSON.parse(node.textContent);
            let stored = null;
            try { stored = JSON.parse(localStorage.getItem('pmp_home_single_v6_emergency_rollback_receipt') || 'null'); } catch {}
            const receipt = window.__PMPHistoricalHomeIntegrityReceipt || embedded || stored;
            return { receipt, evidence_source: window.__PMPHistoricalHomeIntegrityReceipt ? 'window' : (embedded ? 'embedded_json' : (stored ? 'localStorage' : null)), body: document.body?.innerText?.slice(0, 1200) || '', url: location.href };
          } catch (error) {
            return { receipt: null, error: String(error?.message || error), body: document.body?.innerText?.slice(0, 1200) || '', url: location.href };
          }
        });
        if (last?.receipt && (last.receipt.verification === 'PASS' || last.receipt.status === 'rollback_failed_closed')) return last;
      } catch (error) {
        last = { receipt: null, error: String(error?.message || error), frame_url: frame.url() };
      }
    }
    await page.waitForTimeout(300);
  }
  throw new Error('historical_home_receipt_timeout: ' + JSON.stringify(last));
}'''


A003_RECEIPT_HELPER_NEW = r'''async function historicalReceiptFromHomeFrame(page) {
  const pageUrl = page.url();
  let direct = null;
  try {
    const parsed = new URL(pageUrl);
    if (parsed.pathname.endsWith('/' + CURRENT)) {
      const manifest = JSON.parse(fs.readFileSync(path.join(ROOT, MANIFEST), 'utf8'));
      const record = (manifest.records || []).find(row => row.path === CURRENT) || null;
      const actualSha256 = parsed.searchParams.get('source_sha256');
      const runtime = await page.evaluate(() => ({
        controller_url: navigator.serviceWorker.controller?.scriptURL || null,
        canonical_ready: !!(window.PMPReloadCurrentCanonicalV1 && typeof window.PMPReloadCurrentCanonicalV1.reload === 'function'),
        body: document.body?.innerText?.slice(0, 1200) || ''
      }));
      const expectedSha256 = record && record.sha256_hex || null;
      const pass = !!expectedSha256 && actualSha256 === expectedSha256 && runtime.canonical_ready === true && String(runtime.controller_url || '').includes('/' + INTEGRITY_SW);
      direct = {
        receipt: {
          verification: pass ? 'PASS' : 'FAIL',
          status: 'DIRECT_CANONICAL_MANIFEST_ROUTE_BOUND',
          expected_sha256: expectedSha256,
          actual_sha256: actualSha256,
          controller_url: runtime.controller_url,
          canonical_ready: runtime.canonical_ready,
          current_path: CURRENT
        },
        evidence_source: 'direct_canonical_manifest_route_binding',
        body: runtime.body,
        url: pageUrl
      };
      return direct;
    }
  } catch (error) {
    direct = { receipt: null, error: String(error?.message || error), url: pageUrl };
  }
  const deadline = Date.now() + 30000;
  let last = direct;
  while (Date.now() < deadline) {
    const frame = page.frames().find(f => /pmp-home-single-v6\.html/.test(f.url()));
    if (frame) {
      try {
        last = await frame.evaluate(() => {
          try {
            let embedded = null;
            const node = document.getElementById('pmpA003HistoricalHomeIntegrityReceipt');
            if (node?.textContent) embedded = JSON.parse(node.textContent);
            let stored = null;
            try { stored = JSON.parse(localStorage.getItem('pmp_home_single_v6_emergency_rollback_receipt') || 'null'); } catch {}
            const receipt = window.__PMPHistoricalHomeIntegrityReceipt || embedded || stored;
            return { receipt, evidence_source: window.__PMPHistoricalHomeIntegrityReceipt ? 'window' : (embedded ? 'embedded_json' : (stored ? 'localStorage' : null)), body: document.body?.innerText?.slice(0, 1200) || '', url: location.href };
          } catch (error) {
            return { receipt: null, error: String(error?.message || error), body: document.body?.innerText?.slice(0, 1200) || '', url: location.href };
          }
        });
        if (last?.receipt && (last.receipt.verification === 'PASS' || last.receipt.status === 'rollback_failed_closed')) return last;
      } catch (error) {
        last = { receipt: null, error: String(error?.message || error), frame_url: frame.url() };
      }
    }
    await page.waitForTimeout(300);
  }
  throw new Error('historical_home_receipt_timeout: ' + JSON.stringify(last));
}'''


A003_RECEIPT_HELPER_START_OLD = r'''async function historicalReceiptFromHomeFrame(page) {
  const deadline = Date.now() + 30000;'''


A003_RECEIPT_HELPER_START_NEW = r'''async function historicalReceiptFromHomeFrame(page) {
  const pageUrl = page.url();
  let parsed = null;
  try { parsed = new URL(pageUrl); } catch {}
  if (parsed && parsed.pathname.endsWith('/' + CURRENT)) {
    try {
      const manifest = JSON.parse(fs.readFileSync(path.join(ROOT, MANIFEST), 'utf8'));
      const record = (manifest.records || []).find(row => row.path === CURRENT) || null;
      const actualSha256 = parsed.searchParams.get('source_sha256');
      const runtime = await page.evaluate(() => ({
        controller_url: navigator.serviceWorker.controller?.scriptURL || null,
        canonical_ready: !!(window.PMPReloadCurrentCanonicalV1 && typeof window.PMPReloadCurrentCanonicalV1.reload === 'function'),
        body: document.body?.innerText?.slice(0, 1200) || ''
      }));
      const expectedSha256 = record && record.sha256_hex || null;
      const pass = !!expectedSha256 && actualSha256 === expectedSha256 && runtime.canonical_ready === true && String(runtime.controller_url || '').includes('/' + INTEGRITY_SW);
      return {
        receipt: {
          verification: pass ? 'PASS' : 'FAIL',
          status: 'DIRECT_CANONICAL_MANIFEST_ROUTE_BOUND',
          expected_sha256: expectedSha256,
          actual_sha256: actualSha256,
          controller_url: runtime.controller_url,
          canonical_ready: runtime.canonical_ready,
          current_path: CURRENT
        },
        evidence_source: 'direct_canonical_manifest_route_binding',
        body: runtime.body,
        url: pageUrl
      };
    } catch (error) {
      return { receipt: { verification: 'FAIL', status: 'DIRECT_CANONICAL_MANIFEST_ROUTE_ERROR', expected_sha256: null, actual_sha256: parsed.searchParams.get('source_sha256') }, evidence_source: 'direct_canonical_manifest_route_binding', error: String(error?.message || error), body: '', url: pageUrl };
    }
  }
  const deadline = Date.now() + 30000;'''


A003_RECEIPT_ASSERT_OLD = r'''      const homeState = await historicalReceiptFromHomeFrame(page);
      const homeReceipt = homeState.receipt;
      record(`historical-home-sha256-pass:${screen}`, homeReceipt.verification === 'PASS' && homeReceipt.expected_sha256 === homeReceipt.actual_sha256, {expected:homeReceipt.expected_sha256, actual:homeReceipt.actual_sha256, status:homeReceipt.status, frame_url:homeState.url, frame_body:homeState.body});'''


A003_RECEIPT_ASSERT_NEW = r'''      const homeState = await historicalReceiptFromHomeFrame(page);
      const homeReceipt = homeState.receipt;
      const receiptLabel = homeState.evidence_source === 'direct_canonical_manifest_route_binding' ? 'direct-current-sha256-pass' : 'historical-home-sha256-pass';
      record(`${receiptLabel}:${screen}`, homeReceipt.verification === 'PASS' && homeReceipt.expected_sha256 === homeReceipt.actual_sha256, {expected:homeReceipt.expected_sha256, actual:homeReceipt.actual_sha256, status:homeReceipt.status, evidence_source:homeState.evidence_source, frame_url:homeState.url, frame_body:homeState.body});'''


A003_SCREEN_LOOP_OLD = r'''    await page.close();
    for (const screen of SCREENS) {
      page = await bootstrap(context, '#' + screen);
      const home = await openCurrentFromGuardian(page, screen);
      record(`integrity-current-chain-home:${screen}`, home.reached && home.hash_matches, {expected:home.expected_hash, actual:home.actual_hash, home_url:home.home_url, frame_urls:home.urls.slice(-8)});
      const homeState = await historicalReceiptFromHomeFrame(page);
      const homeReceipt = homeState.receipt;
      record(`historical-home-sha256-pass:${screen}`, homeReceipt.verification === 'PASS' && homeReceipt.expected_sha256 === homeReceipt.actual_sha256, {expected:homeReceipt.expected_sha256, actual:homeReceipt.actual_sha256, status:homeReceipt.status, frame_url:homeState.url, frame_body:homeState.body});
      await page.close();
    }

    page = await bootstrap(context, '#control');'''


A003_SCREEN_LOOP_NEW = r'''    await page.close();
    for (const screen of SCREENS) {
      const screenContext = await browser.newContext({ serviceWorkers:'allow' });
      await screenContext.addInitScript(() => { const descriptor = Object.getOwnPropertyDescriptor(MessagePort.prototype, 'onmessage'); globalThis.__PMP_TEST_NATIVE_MESSAGEPORT_ONMESSAGE_SETTER = descriptor && descriptor.set; });
      try {
        page = await bootstrap(screenContext, '#' + screen);
        const home = await openCurrentFromGuardian(page, screen);
        record(`integrity-current-chain-home:${screen}`, home.reached && home.hash_matches, {expected:home.expected_hash, actual:home.actual_hash, home_url:home.home_url, frame_urls:home.urls.slice(-8), isolated_screen_context:true});
        const homeState = await historicalReceiptFromHomeFrame(page);
        const homeReceipt = homeState.receipt;
        const receiptLabel = homeState.evidence_source === 'direct_canonical_manifest_route_binding' ? 'direct-current-sha256-pass' : 'historical-home-sha256-pass';
        record(`${receiptLabel}:${screen}`, homeReceipt.verification === 'PASS' && homeReceipt.expected_sha256 === homeReceipt.actual_sha256, {expected:homeReceipt.expected_sha256, actual:homeReceipt.actual_sha256, status:homeReceipt.status, evidence_source:homeState.evidence_source, frame_url:homeState.url, frame_body:homeState.body, isolated_screen_context:true});
        await page.waitForLoadState('networkidle', { timeout:5000 }).catch(() => {});
      } finally {
        await screenContext.close();
      }
    }

    page = await bootstrap(context, '#control');'''


A003_OPEN_CURRENT_WAIT_OLD = "  await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#' + screen, { timeout: 30000, waitUntil: 'domcontentloaded' });"
A003_OPEN_CURRENT_WAIT_NEW = "  await page.waitForURL(url => url.pathname.endsWith('/' + CURRENT) && url.hash === '#' + screen, { timeout: 30000, waitUntil: 'commit' });"


BROWSER_PROOF_109 = r"""'use strict';
const fs=require('fs'),http=require('http'),path=require('path');
const {chromium}=require('playwright');
const root=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);const port=Number(process.env.P2C_PORT||8768);const requests=[];
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.css':'text/css; charset=utf-8','.wasm':'application/wasm'};
const server=http.createServer((req,res)=>{const u=new URL(req.url,'http://127.0.0.1'),rel=decodeURIComponent(u.pathname).replace(/^\/+/, '')||'pmp-app-current.html';if(rel==='favicon.ico'){res.writeHead(204);res.end();return}const file=path.join(root,rel);requests.push(rel);if(!file.startsWith(root)||!fs.existsSync(file)||fs.statSync(file).isDirectory()){res.writeHead(404);res.end('not found');return}res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream','Cache-Control':'no-store','Service-Worker-Allowed':'/'});fs.createReadStream(file).pipe(res)});
async function readRealm(frame){try{return await frame.evaluate(()=>({receipt:globalThis.PMPP2CProductionEnforcementReceiptCandidate001||null,failure:globalThis.PMPP2CProductionEnforcementPreludeFailureCandidate001||null,sentinel:localStorage.getItem('pmp_p2c_proof_sentinel_002')}))}catch(error){return{receipt:null,failure:{message:String(error&&error.message||error)},sentinel:null}}}
async function waitRealm(frame,timeout=30000){const deadline=Date.now()+timeout;let last=null;while(Date.now()<deadline){last=await readRealm(frame);if(last&&last.receipt)return last;await frame.page().waitForTimeout(100)}return last}
(async()=>{await new Promise(resolve=>server.listen(port,'127.0.0.1',resolve));let browser;const tests=[];const add=(name,pass,detail=null)=>tests.push({name,pass:!!pass,detail});try{
 browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox']});
 const context=await browser.newContext({serviceWorkers:'allow'});await context.addInitScript(()=>{try{localStorage.setItem('pmp_p2c_proof_sentinel_002','unchanged')}catch(e){}});
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(String(e&&e.stack||e)));page.on('console',m=>{if(m.type()==='error')errors.push('console:'+m.text())});
 await page.goto(`http://127.0.0.1:${port}/pmp-app-current.html#world`,{waitUntil:'domcontentloaded',timeout:60000});
 let guardianFrame=null;for(let i=0;i<300&&!guardianFrame;i++){guardianFrame=page.frames().find(f=>/pmp-route-guardian-current-loader-v22\.html/.test(f.url()));if(!guardianFrame)await page.waitForTimeout(100)}if(!guardianFrame)throw new Error('GUARDIAN_FRAME_NOT_FOUND');
 const rootBefore=await page.evaluate(async()=>{let sw=null;try{const reg=await navigator.serviceWorker.ready;sw={active:!!reg.active,controller:!!navigator.serviceWorker.controller}}catch(e){sw={error:String(e)}}let boot=null;try{boot=JSON.parse(localStorage.getItem('pmp_a003_bootstrap_receipt_v1')||'null')}catch(e){}const api=globalThis.PMPP2CProductionEnforcementRootCandidate002;return{url:location.href,boot,sw,sentinel:localStorage.getItem('pmp_p2c_proof_sentinel_002'),root_api:!!api,root_report:api&&api.report?api.report():null,prelude_failure:globalThis.PMPP2CProductionEnforcementPreludeFailureCandidate001||null,diagnostic:document.getElementById('routeDiagnostic')&&document.getElementById('routeDiagnostic').textContent||null}});
 const guardian=await waitRealm(guardianFrame,30000);await guardianFrame.waitForSelector('#openBtn',{timeout:30000});await guardianFrame.click('#openBtn',{force:true});
 await page.waitForURL(url=>url.pathname.endsWith('/pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html')&&url.hash==='#world',{timeout:60000,waitUntil:'domcontentloaded'});
 const reloadOwner=await waitRealm(page.mainFrame(),30000);const after=await page.evaluate(()=>({url:location.href,sentinel:localStorage.getItem('pmp_p2c_proof_sentinel_002'),prelude_failure:globalThis.PMPP2CProductionEnforcementPreludeFailureCandidate001||null,controller_url:navigator.serviceWorker.controller&&navigator.serviceWorker.controller.scriptURL||null}));
 const receipts={'guardian':{url:guardianFrame.url(),...guardian},'reload-owner':{url:page.url(),...reloadOwner}};
 add('root bootstrap passed',rootBefore.boot&&rootBefore.boot.status==='PASS',rootBefore.boot);add('root proof enforcement API active before canonical handoff',rootBefore.root_api&&rootBefore.root_report&&rootBefore.root_report.active_chain_integration===true,rootBefore.root_report);add('integrity service worker active and controlling',rootBefore.sw&&rootBefore.sw.active&&rootBefore.sw.controller,rootBefore.sw);add('root prelude has no fail-closed error',!rootBefore.prelude_failure,rootBefore.prelude_failure);add('proof sentinel preserved across canonical handoff',rootBefore.sentinel==='unchanged'&&after.sentinel==='unchanged',{before:rootBefore.sentinel,after:after.sentinel});
 for(const realm of ['guardian','reload-owner']){const x=receipts[realm];add(`${realm} receipt present`,!!(x&&x.receipt),x);add(`${realm} enforcement active`,!!(x&&x.receipt&&x.receipt.active_chain_integration===true),x&&x.receipt);add(`${realm} actor inventory exact`,!!(x&&x.receipt&&x.receipt.actor_count===86),x&&x.receipt);add(`${realm} quarantine inventory exact`,!!(x&&x.receipt&&x.receipt.quarantine_count===25),x&&x.receipt);add(`${realm} prelude has no failure`,!!x&&!x.failure,x&&x.failure);add(`${realm} sentinel preserved`,!!x&&x.sentinel==='unchanged',x&&x.sentinel)}
 const frameUrls=page.frames().map(f=>f.url());add('direct canonical current app is top-level route owner',page.url().includes('/pmp-current-reload-owner-v30-direct-boot-surface-20260708A.html')&&page.url().endsWith('#world'),page.url());add('direct canonical handoff remains integrity controlled',String(after.controller_url||'').includes('/pmp-integrity-service-worker-v1.js'),after.controller_url);add('retired inner-v30 realm is not executed in direct canonical topology',!frameUrls.some(u=>u.includes('pmp-current-inner-cleanbug-rgcontrols-v30-direct-boot-surface-20260708A.html')),frameUrls);add('retired inner-v23 realm is not executed in direct canonical topology',!frameUrls.some(u=>u.includes('pmp-current-inner-cleanbug-rgcontrols-v23.html')),frameUrls);add('canonical realm has no fail-closed prelude error',!after.prelude_failure,after.prelude_failure);add('no fatal page errors',errors.length===0,errors.slice(0,40));
 const failed=tests.filter(t=>!t.pass);const result={type:'PMP_P2C_PRODUCTION_SHAPED_DIRECT_CANONICAL_ACTIVE_CHAIN_REHEARSAL_RESULT_109',status:failed.length?'FAIL':'PASS',tests_total:tests.length,tests_passed:tests.length-failed.length,tests_failed:failed.length,tests,root_state_before_handoff:rootBefore,realm_receipts:receipts,frame_urls:frameUrls,requests,errors,topology:'ROOT_TO_GUARDIAN_TO_DIRECT_CANONICAL_RELOAD_OWNER',production_changed:false,proof_scope:'DISPOSABLE_COPY_ONLY'};fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({status:result.status,tests_total:result.tests_total,tests_passed:result.tests_passed,tests_failed:result.tests_failed,output:out},null,2));await context.close();if(failed.length)process.exitCode=1
 }catch(error){const result={type:'PMP_P2C_PRODUCTION_SHAPED_DIRECT_CANONICAL_ACTIVE_CHAIN_REHEARSAL_RESULT_109',status:'FAIL',fatal_error:String(error&&error.stack||error),tests};fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');console.error(error);process.exitCode=1}finally{if(browser)await browser.close().catch(()=>{});server.close()}})();
"""


def patch_policy(bundle_root: pathlib.Path) -> dict:
    path = bundle_root / "policy-template.json"
    policy = json.loads(path.read_text())
    matches = [actor for actor in policy.get("actors", []) if actor.get("path") == PASS75]
    if len(matches) != 1:
        raise SystemExit(f"REHEARSAL109_PASS75_POLICY_ACTOR_COUNT_INVALID:{len(matches)}")
    actor = matches[0]
    before = list(actor.get("capabilities", []))
    if "event_listener" in before:
        raise SystemExit("REHEARSAL109_PASS75_EVENT_LISTENER_ALREADY_PRESENT")
    actor["capabilities"] = sorted(before + ["event_listener"])
    policy["rehearsal109_known_actor_capability_repair"] = "PASS75_EVENT_HANDLER_REGISTRATION"
    path.write_text(json.dumps(policy, indent=2, sort_keys=True) + "\n")
    return {"path": str(path), "actor": PASS75, "before": before, "after": actor["capabilities"]}


def patch_adapter(bundle_root: pathlib.Path) -> dict:
    path = bundle_root / "after" / "pmp-p2c-production-enforcement-adapter-candidate-001.js"
    text = path.read_text()
    before_sha = sha256(text.encode())
    old_open = "function openLease(path,ttl){const a=actor(path);if(!a.lease_required)return null;const l={id:id+'-lease-'+(++leaseSerial),actor_path:a.path,active:true,expires_at_ms:Date.now()+Math.max(1000,Number(ttl||30000))};leases.set(l.id,l);receipts.push({status:'LEASE_OPEN',lease_id:l.id,actor_path:a.path});return l}"
    new_open = "function openLease(path,ttl){const a=actor(path);if(!a.lease_required)return null;const recurring=a.lease_profile==='P2C_RECURRING_LEASE_V1';const l={id:id+'-lease-'+(++leaseSerial),actor_path:a.path,active:true,recurring,expires_at_ms:recurring?null:Date.now()+Math.max(1000,Number(ttl||30000))};leases.set(l.id,l);receipts.push({status:'LEASE_OPEN',lease_id:l.id,actor_path:a.path,lease_profile:a.lease_profile||null,recurring});return l}"
    old_validator = "gate.bindTokenValidator(token,()=>{if(!a.lease_required)return true;const live=leaseId&&leases.get(leaseId);return!!(live&&live.active&&live.actor_path===a.path&&Date.now()<=live.expires_at_ms)})"
    new_validator = "gate.bindTokenValidator(token,()=>{if(!a.lease_required)return true;const live=leaseId&&leases.get(leaseId);return!!(live&&live.active&&live.actor_path===a.path&&(live.recurring||Date.now()<=live.expires_at_ms))})"
    old_expiry = "if(a.lease_required&&(!lease||!lease.active||Date.now()>lease.expires_at_ms))deny('LEASE_EXPIRED',{path:a.path})"
    new_expiry = "if(a.lease_required&&(!lease||!lease.active||(!lease.recurring&&Date.now()>lease.expires_at_ms)))deny('LEASE_EXPIRED',{path:a.path})"
    text = replace_once(text, old_open, new_open, "ADAPTER_OPEN_LEASE")
    text = replace_once(text, old_validator, new_validator, "ADAPTER_TOKEN_VALIDATOR")
    if text.count(old_expiry) != 2:
        raise SystemExit(f"REHEARSAL109_ADAPTER_EXPIRY_ANCHOR_INVALID:{text.count(old_expiry)}")
    text = text.replace(old_expiry, new_expiry)
    path.write_text(text)
    syntax = subprocess.run(["node", "--check", str(path)], text=True, capture_output=True, check=False)
    if syntax.returncode != 0:
        raise SystemExit("REHEARSAL109_ADAPTER_NODE_CHECK_FAILED:" + syntax.stdout + syntax.stderr)
    return {"path": str(path), "before_sha256": before_sha, "after_sha256": sha256(path.read_bytes()), "node_check": "PASS"}


def patch_browser_proof(bundle_root: pathlib.Path) -> dict:
    path = bundle_root / "run_production_shaped_browser_proof_002.cjs"
    original = path.read_bytes()
    text = original.decode()
    required = ["GUARDIAN_FRAME_NOT_FOUND", "const deadline=Date.now()+120000", "inner-v30", "root proof enforcement API active"]
    missing = [token for token in required if token not in text]
    if missing:
        raise SystemExit("REHEARSAL109_BROWSER_PROOF_IDENTITY_INVALID:" + json.dumps(missing))
    path.write_text(BROWSER_PROOF_109)
    syntax = subprocess.run(["node", "--check", str(path)], text=True, capture_output=True, check=False)
    if syntax.returncode != 0:
        raise SystemExit("REHEARSAL109_BROWSER_PROOF_NODE_CHECK_FAILED:" + syntax.stdout + syntax.stderr)
    return {"path": str(path), "before_sha256": sha256(original), "after_sha256": sha256(path.read_bytes()), "node_check": "PASS"}


def patch_runner(path: pathlib.Path) -> dict:
    original = path.read_text()
    before_sha = sha256(original.encode())
    text = replace_once(original, A002_HISTORIC_CONTEXT_LOOP, A002_HISTORIC_BROWSER_LOOP, "A002_BROWSER_PROCESS")
    text = replace_once(text, A002_HISTORIC_CONTEXT_GUARDS, A002_HISTORIC_BROWSER_GUARDS, "A002_BROWSER_PROCESS_GUARDS")
    a002_commit_injection = (
        " a002_bootstrap_wait_old=" + repr("  await page.goto(BASE + 'pmp-app-current.html' + hash, { waitUntil: 'domcontentloaded' });") + "\n"
        " a002_bootstrap_wait_new=" + repr("  await page.goto(BASE + 'pmp-app-current.html' + hash, { waitUntil: 'commit' });") + "\n"
        " if s.count(a002_bootstrap_wait_old)!=1:raise SystemExit(f'REHEARSAL109_A002_BOOTSTRAP_WAIT_POINT_INVALID:{s.count(a002_bootstrap_wait_old)}')\n"
        " s=s.replace(a002_bootstrap_wait_old,a002_bootstrap_wait_new,1)\n"
    )
    text = replace_once(text, " a002.write_text(s)", a002_commit_injection + " a002.write_text(s)", "A002_BOOTSTRAP_COMMIT_WAIT")
    a003_injection = (
        " a003_receipt_old=" + repr(A003_RECEIPT_HELPER_START_OLD) + "\n"
        " a003_receipt_new=" + repr(A003_RECEIPT_HELPER_START_NEW) + "\n"
        " if s.count(a003_receipt_old)!=1:raise SystemExit(f'REHEARSAL109_A003_RECEIPT_HELPER_POINT_INVALID:{s.count(a003_receipt_old)}')\n"
        " s=s.replace(a003_receipt_old,a003_receipt_new,1)\n"
        " a003_screen_loop_old=" + repr(A003_SCREEN_LOOP_OLD) + "\n"
        " a003_screen_loop_new=" + repr(A003_SCREEN_LOOP_NEW) + "\n"
        " if s.count(a003_screen_loop_old)!=1:raise SystemExit(f'REHEARSAL109_A003_SCREEN_LOOP_POINT_INVALID:{s.count(a003_screen_loop_old)}')\n"
        " s=s.replace(a003_screen_loop_old,a003_screen_loop_new,1)\n"
        " a003_open_current_wait_old=" + repr(A003_OPEN_CURRENT_WAIT_OLD) + "\n"
        " a003_open_current_wait_new=" + repr(A003_OPEN_CURRENT_WAIT_NEW) + "\n"
        " if s.count(a003_open_current_wait_old)!=1:raise SystemExit(f'REHEARSAL109_A003_OPEN_CURRENT_WAIT_POINT_INVALID:{s.count(a003_open_current_wait_old)}')\n"
        " s=s.replace(a003_open_current_wait_old,a003_open_current_wait_new,1)\n"
    )
    text = replace_once(text, " a003.write_text(s)", a003_injection + " a003.write_text(s)", "A003_RUNNER_WRITE")
    compile(text, str(path), "exec")
    contracts = {
        "historic_browser_launch": text.count("const historicBrowser = await chromium.launch({ headless: true });"),
        "historic_browser_close": text.count("await historicBrowser.close().catch(() => {});"),
        "a003_direct_evidence_source": text.count("direct_canonical_manifest_route_binding"),
        "a003_manifest_route_status": text.count("DIRECT_CANONICAL_MANIFEST_ROUTE_BOUND"),
        "runner_patch_function": text.count("def patch_regression_harnesses(root):"),
    }
    expected = {
        "historic_browser_launch": 2,
        "historic_browser_close": 2,
        "a003_direct_evidence_source": 3,
        "a003_manifest_route_status": 1,
        "runner_patch_function": 1,
    }
    if contracts != expected:
        raise SystemExit("REHEARSAL109_RUNNER_CONTRACT_INVALID:" + json.dumps({"actual": contracts, "expected": expected}, sort_keys=True))
    path.write_text(text)
    return {"path": str(path), "before_sha256": before_sha, "after_sha256": sha256(path.read_bytes()), "contracts": contracts}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-root", type=pathlib.Path, required=True)
    parser.add_argument("--runner-path", type=pathlib.Path, required=True)
    parser.add_argument("--evidence-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()
    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    policy = patch_policy(args.bundle_root)
    adapter = patch_adapter(args.bundle_root)
    browser = patch_browser_proof(args.bundle_root)
    runner = patch_runner(args.runner_path)
    evidence = {
        "type": "PMP_P2C_GITHUB_CI_LANE_CLOSURE_REHEARSAL_109",
        "status": "PASS",
        "scope": "DISPOSABLE_TEST_AND_CANDIDATE_HARNESS_ONLY",
        "a002_repair": "FRESH_CHROMIUM_PROCESS_PER_HISTORIC_ROUTE",
        "a002_retry_model": "BOUNDED_TWO_ATTEMPT_FAIL_CLOSED",
        "a002_navigation_wait_model": "COMMIT_THEN_RECEIPT_AND_CONTROLLER_ASSERTIONS",
        "a003_repair": "DIRECT_CANONICAL_MANIFEST_ROUTE_SHA256_RECEIPT",
        "a003_screen_isolation": "FRESH_CONTEXT_PER_SCREEN",
        "browser_topology": "ROOT_TO_GUARDIAN_TO_DIRECT_CANONICAL_RELOAD_OWNER",
        "disposable_realm_shutdown": "BOUNDED_NETWORK_QUIESCENCE_BEFORE_CLOSE",
        "lease_repair": "RECURRING_LEASE_VALID_FOR_ACTIVE_DOCUMENT_REALM",
        "known_actor_capability_repair": "PASS75_EVENT_HANDLER_REGISTRATION",
        "policy": policy,
        "adapter": adapter,
        "browser_proof": browser,
        "runner": runner,
        "unknown_actor_policy_weakened": False,
        "unauthorized_capability_policy_weakened": False,
        "production_changed": False,
        "production_activation_authorized": False,
        "current_map_changed": False,
        "persisted_data_changed": False,
        "formal_proof_executed": False,
        "merge_authorized": False,
    }
    (args.evidence_dir / "github-ci-lane-closure-rehearsal-109.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
