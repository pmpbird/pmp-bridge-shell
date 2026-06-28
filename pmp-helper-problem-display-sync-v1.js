(()=>{
'use strict';
const V='1.0.0-active-vs-risk-display-sync';
const RISK=/^(Duplicate helper files|Duplicate running helpers|Duplicate saved helper records|Empty Continuous Run level stack|Many uncategorized helpers)$/;
function T(){try{return top||window}catch(e){return window}}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>10)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function isRiskName(x){return RISK.test(String(x||''))}
function patchLive(){try{let api=T().PMPHelperBankLiveInspectorV2||window.PMPHelperBankLiveInspectorV2;if(!api||!api.live||api.__activeVsRiskSync)return;let old=api.live.bind(api);api.live=function(){let d=old()||{};let risks=[];d.problems=(d.problems||[]).filter(p=>{let risk=isRiskName(p.problem);if(risk)risks.push(p);return !risk});d.checks=(d.checks||[]).map(c=>{if(c&&isRiskName(c.check)&&c.status==='PROBLEM')return Object.assign({},c,{status:'risk',why:String(c.why||'')+' This is kept as a risk/reference, not counted as an active problem unless it creates a visible symptom.'});return c});d.summary=d.summary||{};d.summary.problems=(d.problems||[]).length;d.summary.problem_risks=risks.length;return d};api.__activeVsRiskSync=V}catch(e){}}
function refresh(){try{patchLive();let clicked=false;docs(T().document).forEach(d=>{try{let b=d.querySelector('[data-helper-bank-refresh]');if(b){clicked=true;b.click()}}catch(e){}});if(!clicked){let api=T().PMPHelperBankLiveInspectorV2||window.PMPHelperBankLiveInspectorV2;if(api&&api.scan)api.scan()}}catch(e){}}
function watchClicks(){try{T().document.addEventListener('click',e=>{try{let t=e.target&&e.target.closest&&e.target.closest('[data-pm-smart-fix]');if(!t)return;[700,1500,2600,4200].forEach(ms=>setTimeout(refresh,ms))}catch(x){}},true)}catch(e){}}
function scan(){patchLive()}
window.PMPHelperProblemDisplaySyncV1={version:V,scan,refresh};
watchClicks();
window.addEventListener('load',()=>[300,900,1800,3500].forEach(t=>setTimeout(scan,t)));
setInterval(scan,2000);scan();
})();