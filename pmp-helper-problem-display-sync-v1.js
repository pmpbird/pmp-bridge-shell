(()=>{
'use strict';
const V='1.0.2-stable-memory-count-source';
const ACTIVE='pmp_helper_problem_memory_active_v1';
const RISK=/^(Duplicate helper files|Duplicate running helpers|Duplicate saved helper records|Empty Continuous Run level stack|Many uncategorized helpers)$/;
function T(){try{return top||window}catch(e){return window}}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>10)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function activeLoad(){try{return JSON.parse(localStorage.getItem(ACTIVE)||'[]').filter(Boolean)}catch(e){return[]}}
function isRiskName(x){return RISK.test(String(x||''))}
function stableCount(){return activeLoad().length}
function patchLive(){try{let api=T().PMPHelperBankLiveInspectorV2||window.PMPHelperBankLiveInspectorV2;if(!api||!api.live||api.__stableMemoryCountSource)return;let old=api.live.bind(api);api.live=function(){let d=old()||{},stable=activeLoad();let risks=[];d.problems=(d.problems||[]).filter(p=>{let name=String(p.problem||'');let risk=isRiskName(name)||!/^Auto-detected |^Learned problem detected:/.test(name);if(risk)risks.push(p);return false}).concat(stable.map(x=>({problem:x.kind,severity:x.severity||'medium',where:x.where,count:1,why:x.why})));d.checks=(d.checks||[]).map(c=>{if(c&&c.status==='PROBLEM'&&(isRiskName(c.check)||!/Auto Problem Memory:/.test(String(c.check||''))))return Object.assign({},c,{status:'risk',why:String(c.why||'')+' This is kept as a risk/reference, not counted as active unless stable problem memory confirms it.'});return c});d.summary=d.summary||{};d.summary.problems=stable.length;d.summary.stable_active_problems=stable.length;d.summary.problem_risks=risks.length;return d};api.__stableMemoryCountSource=V}catch(e){}}
function setTextDeep(root,to){try{Array.from(root.querySelectorAll('*')).forEach(el=>{try{if(el.children&&el.children.length)return;let tx=String(el.textContent||'');if(/^Active Problems — \d+$/.test(tx))el.textContent='Active Problems — '+to;if(/^Problems Found — \d+$/.test(tx))el.textContent='Problems Found — '+to}catch(e){}})}catch(e){}}
function syncDom(){let n=stableCount();docs(T().document).forEach(d=>{try{let bank=d.getElementById('bank');if(!bank)return;let p=bank.querySelector('[data-helper-tab="problems"] span')||bank.querySelector('[data-helper-tab="problems"]');if(p)p.textContent='Problems Found — '+n;setTextDeep(bank,n);let pres=Array.from(bank.querySelectorAll('pre.note,pre')).find(x=>String(x.textContent||'').indexOf('"problems"')>=0&&String(x.textContent||'').indexOf('"problem_checks"')>=0);if(pres){try{let obj=JSON.parse(pres.textContent);obj.problems=n;obj.stable_active_problems=n;pres.textContent=JSON.stringify(obj,null,2)}catch(e){}}}catch(e){}})}
function refresh(){try{patchLive();let api=T().PMPHelperBankLiveInspectorV2||window.PMPHelperBankLiveInspectorV2;if(api&&api.scan)api.scan();[120,350,900,1600].forEach(ms=>setTimeout(syncDom,ms))}catch(e){}}
function watchClicks(){try{T().document.addEventListener('click',e=>{try{let t=e.target&&e.target.closest&&e.target.closest('[data-pm-smart-fix],[data-helper-bank-refresh],[data-helper-tab]');if(!t)return;[100,300,800,1500,2600,4200].forEach(ms=>setTimeout(syncDom,ms))}catch(x){}},true)}catch(e){}}
function scan(){patchLive();syncDom()}
window.PMPHelperProblemDisplaySyncV1={version:V,scan,refresh,syncDom,count:stableCount};
watchClicks();
window.addEventListener('load',()=>[250,700,1300,2300,4000,6500].forEach(t=>setTimeout(scan,t)));
setInterval(scan,900);scan();
})();