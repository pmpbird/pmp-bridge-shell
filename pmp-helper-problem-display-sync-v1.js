(()=>{
'use strict';
const V='1.0.1-visible-active-count-sync';
const ACTIVE='pmp_helper_problem_memory_active_v1';
const RISK=/^(Duplicate helper files|Duplicate running helpers|Duplicate saved helper records|Empty Continuous Run level stack|Many uncategorized helpers)$/;
function T(){try{return top||window}catch(e){return window}}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>10)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function activeLoad(){try{return JSON.parse(localStorage.getItem(ACTIVE)||'[]').filter(Boolean)}catch(e){return[]}}
function isRiskName(x){return RISK.test(String(x||''))}
function patchLive(){try{let api=T().PMPHelperBankLiveInspectorV2||window.PMPHelperBankLiveInspectorV2;if(!api||!api.live||api.__activeVsRiskSync)return;let old=api.live.bind(api);api.live=function(){let d=old()||{};let risks=[];d.problems=(d.problems||[]).filter(p=>{let risk=isRiskName(p.problem);if(risk)risks.push(p);return !risk});d.checks=(d.checks||[]).map(c=>{if(c&&isRiskName(c.check)&&c.status==='PROBLEM')return Object.assign({},c,{status:'risk',why:String(c.why||'')+' This is kept as a risk/reference, not counted as an active problem unless it creates a visible symptom.'});return c});d.summary=d.summary||{};d.summary.problems=(d.problems||[]).length;d.summary.problem_risks=risks.length;return d};api.__activeVsRiskSync=V}catch(e){}}
function count(){try{patchLive();let api=T().PMPHelperBankLiveInspectorV2||window.PMPHelperBankLiveInspectorV2;if(api&&api.live){let d=api.live()||{};return (d.problems||[]).length}}catch(e){}return activeLoad().length}
function setTextDeep(root,from,to){try{Array.from(root.querySelectorAll('*')).forEach(el=>{try{if(el.children&&el.children.length)return;let tx=String(el.textContent||'');if(tx.indexOf(from)>=0)el.textContent=tx.replace(from,to)}catch(e){}})}catch(e){}}
function syncDom(){let n=count();docs(T().document).forEach(d=>{try{let bank=d.getElementById('bank');if(!bank)return;let p=bank.querySelector('[data-helper-tab="problems"] span')||bank.querySelector('[data-helper-tab="problems"]');if(p)p.textContent='Problems Found — '+n;setTextDeep(bank,'Active Problems — 4','Active Problems — '+n);setTextDeep(bank,'Active Problems — 3','Active Problems — '+n);setTextDeep(bank,'Active Problems — 2','Active Problems — '+n);setTextDeep(bank,'Active Problems — 1','Active Problems — '+n);setTextDeep(bank,'Active Problems — 0','Active Problems — '+n);let pres=Array.from(bank.querySelectorAll('pre.note,pre')).find(x=>String(x.textContent||'').indexOf('"problems"')>=0&&String(x.textContent||'').indexOf('"problem_checks"')>=0);if(pres){try{let obj=JSON.parse(pres.textContent);obj.problems=n;pres.textContent=JSON.stringify(obj,null,2)}catch(e){}}}catch(e){}})}
function refresh(){try{patchLive();let api=T().PMPHelperBankLiveInspectorV2||window.PMPHelperBankLiveInspectorV2;if(api&&api.scan)api.scan();setTimeout(syncDom,200);setTimeout(syncDom,900);setTimeout(syncDom,1800)}catch(e){}}
function watchClicks(){try{T().document.addEventListener('click',e=>{try{let t=e.target&&e.target.closest&&e.target.closest('[data-pm-smart-fix],[data-helper-bank-refresh],[data-helper-tab]');if(!t)return;[300,800,1500,2600,4200].forEach(ms=>setTimeout(syncDom,ms))}catch(x){}},true)}catch(e){}}
function scan(){patchLive();syncDom()}
window.PMPHelperProblemDisplaySyncV1={version:V,scan,refresh,syncDom,count};
watchClicks();
window.addEventListener('load',()=>[300,900,1800,3500,6000].forEach(t=>setTimeout(scan,t)));
setInterval(scan,1200);scan();
})();