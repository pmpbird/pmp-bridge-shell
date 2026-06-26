(()=>{
'use strict';
const V='1.0.0-level21-one-tap-full-chain-retest-lock';
const L10K='pmp_level10_full_chain_certification_lock_v1';
const L21K='pmp_level21_one_tap_full_chain_retest_lock_v1';
function W(){try{return window.top||window}catch(e){return window}}
function read(k,d){try{return JSON.parse(W().localStorage.getItem(k)||'')||d}catch(e){return d}}
function write(k,v){try{W().localStorage.setItem(k,JSON.stringify(v,null,2))}catch(e){}return v}
function hash(s){let h=2166136261;s=String(s||'');for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return(h>>>0).toString(16).padStart(8,'0')}
function wins(w,a,n){a=a||[];n=n||0;if(!w||n>8)return a;try{a.push(w);let d=w.document;if(d)d.querySelectorAll('iframe').forEach(f=>{try{if(f.contentWindow)wins(f.contentWindow,a,n+1)}catch(e){}})}catch(e){}return a}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>8)return a;try{a.push(r);r.querySelectorAll('iframe').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function api(name,method){for(const w of wins(W())){let a=w[name];if(a&&typeof a[method||'run']==='function')return a}return null}
function latest10(){let x=read(L10K,null);return x&&(x.latest||x)}
function seed(){let c=latest10(),a=c&&Array.isArray(c.coverage)?c.coverage:[];return a[0]&&a[0].phrase||c&&c.random_source_phrase||''}
function leaf(x){return x&&x.latest?x.latest:x}
function status(x){return leaf(x)&&leaf(x).status||'NONE'}
function resultHash(x){let r=leaf(x)||{};return r.hash||r.guard_hash||r.enforcement_hash||r.failure_test_hash||r.recovery_hash||r.gate_hash||r.block_test_hash||r.summary_hash||'none'}
function pass(level,x){let r=leaf(x)||{};let s=r.status||'';if(level===10)return s==='FULL_CHAIN_CERTIFIED';if(level===11)return s==='STARTUP_CERTIFIED';if(level===12)return s==='RESIDENT_STARTUP_ENFORCED';return r.passed===true||/PASSED$/.test(String(s))}
function title(level){return({10:'Strict full-chain certification',11:'Startup certification guard',12:'Resident startup enforcement',13:'Enforcement failure test',14:'Post-failure recovery proof',15:'Source change invalidation guard',16:'Source-bound startup enforcement',17:'Source-mismatch Resident block test',18:'Source re-certification required gate',19:'Re-certification recovery proof',20:'Certification chain summary lock'})[level]||('Level '+level)}
async function callStep(level,name,method,arg){let a=api(name,method||'run');if(!a)throw Error('Level '+level+' API is not loaded');let fn=a[method||'run'];let out=await fn.call(a,arg);return out}
async function run(){let steps=[],err=null,summary=null;async function one(level,name,method,arg){let out=await callStep(level,name,method,arg);let r={level,name:title(level),status:status(out),passed:pass(level,out),hash:resultHash(out),result:leaf(out)};steps.push(r);return out}
try{
 await one(10,'PMPFullChainCertificationLevel10V1','run');
 await one(11,'PMPStartupCertificationGuardLevel11V1','guard');
 await one(12,'PMPResidentStartupEnforcementLevel12V1','run',seed());
 await one(13,'PMPEnforcementFailureTestLevel13V1','run');
 await one(14,'PMPPostFailureRecoveryProofLevel14V1','run');
 await one(15,'PMPSourceChangeInvalidationGuardLevel15V1','run');
 await one(16,'PMPSourceBoundStartupEnforcementLevel16V1','run');
 await one(17,'PMPSourceMismatchResidentBlockTestLevel17V1','run');
 await one(18,'PMPSourceRecertificationRequiredGateLevel18V1','run');
 await one(19,'PMPRecertificationRecoveryProofLevel19V1','run');
 summary=await one(20,'PMPCertificationChainSummaryLockLevel20V1','run');
}catch(e){err=e&&e.message||String(e)}
let ok=steps.length===11&&steps.every(s=>s.passed)&&!err;let s20=leaf(summary)||{};let rec={level:21,type:'ONE_TAP_FULL_CHAIN_RETEST_LOCK',version:V,at:new Date().toISOString(),status:ok?'ONE_TAP_FULL_CHAIN_RETEST_LOCK_PASSED':'ONE_TAP_FULL_CHAIN_RETEST_LOCK_FAILED',passed:ok,critical_retests_passed:steps.filter(s=>s.passed).length,critical_retests_total:11,levels_verified:ok?'20/20':'PARTIAL',level10_hash:(latest10()&&latest10().hash)||'none',source_hash:s20.source_hash||steps.map(s=>s.result&&s.result.source_hash).filter(Boolean).pop()||'none',level20_summary_hash:s20.summary_hash||'none',steps,error:err,retest_hash:hash(JSON.stringify({steps,err,version:V,source:s20.source_hash,level10:latest10()&&latest10().hash})),rule:'One tap reruns Levels 10-20 live. Levels 1-9 are re-covered by the fresh strict Level 10 certification, then Level 20 summarizes the full Levels 1-19 chain, and Level 21 locks the fresh re-test receipt.'};return write(L21K,rec)}
function render(x){if(!x)return 'Level 21 ready.';let lines=(x.steps||[]).map(s=>'L'+s.level+' '+(s.passed?'PASS':'FAIL')+' — '+s.name+' — '+(s.hash||'none')).join('\n');return 'Level 21\nStatus: '+(x.status||'NONE')+'\nCritical re-tests passed: '+(x.critical_retests_passed||0)+'/'+(x.critical_retests_total||11)+'\nLevels verified: '+(x.levels_verified||'PARTIAL')+'\nLevel 10 hash: '+(x.level10_hash||'none')+'\nSource hash: '+(x.source_hash||'none')+'\nLevel 20 summary hash: '+(x.level20_summary_hash||'none')+'\nRe-test hash: '+(x.retest_hash||'none')+(x.error?'\nError: '+x.error:'')+'\n\nLive re-test steps:\n'+lines}
function section(){return '<div data-level21-full-retest style="margin-top:8px;padding:8px;border-radius:10px;border:1px solid rgba(0,0,0,.08)"><h4 style="margin:0 0 4px">Level 21 — One-Tap Full Chain Re-Test Lock</h4><p class="sub">Reruns the critical chain live in one tap, then locks a fresh final re-test receipt.</p><div class="grid"><button class="mini" data-l21-run>Run Full Re-Test</button><button class="mini" data-l21-view>View Re-Test Lock</button></div><pre class="note" data-l21-out style="max-height:440px;overflow:auto;white-space:pre-wrap">Level 21 ready.</pre></div>'}
function patch(d){let root=d.querySelector('[data-source-reference-gate-level4]');if(!root)return;let h=root.querySelector('h4');if(h&&!root.querySelector('[data-l21-badge]'))h.insertAdjacentHTML('afterend','<div data-l21-badge style="margin:4px 0 8px;padding:8px;border-radius:10px;border:2px solid rgba(0,0,0,.18);font-weight:950">Level 21: One-Tap Full Chain Re-Test Lock — READY</div>');if(!root.querySelector('[data-level21-full-retest]'))root.insertAdjacentHTML('beforeend',section());let out=root.querySelector('[data-l21-out]'),rn=root.querySelector('[data-l21-run]'),vw=root.querySelector('[data-l21-view]');if(rn)rn.onclick=async()=>{out.textContent='Running one-tap full chain re-test...';try{out.textContent=render(await run())}catch(e){out.textContent='Level 21\nStatus: ROADBLOCK\n'+(e&&e.message||e)}};if(vw)vw.onclick=()=>{out.textContent=render(read(L21K,null))}}
function scan(){docs(W().document).forEach(d=>{try{patch(d)}catch(e){}})}
W().PMPOneTapFullChainRetestLockLevel21V1={version:V,run,view:()=>read(L21K,null),render};
window.addEventListener('load',()=>[300,1000,2500,5000].forEach(t=>setTimeout(scan,t)));
setInterval(scan,1000);scan();
})();