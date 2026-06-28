(()=>{
'use strict';
const V='1.1.1-visible-section-names';
const ACTIVE='pmp_helper_problem_memory_active_v1';
const RISK=/^(Duplicate helper files|Duplicate running helpers|Duplicate saved helper records|Empty Continuous Run level stack|Many uncategorized helpers)$/;
function T(){try{return top||window}catch(e){return window}}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>10)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function activeLoad(){try{return JSON.parse(localStorage.getItem(ACTIVE)||'[]').filter(Boolean)}catch(e){return[]}}
function isRiskName(x){return RISK.test(String(x||''))}
function stableCount(){return activeLoad().length}
function patchLive(){try{let api=T().PMPHelperBankLiveInspectorV2||window.PMPHelperBankLiveInspectorV2;if(!api||!api.live||api.__stableMemoryCountSourceNoDomFight)return;let old=api.live.bind(api);api.live=function(){let d=old()||{},stable=activeLoad(),risks=[];d.problems=(d.problems||[]).filter(p=>{risks.push(p);return false}).concat(stable.map(x=>({problem:x.kind,severity:x.severity||'medium',where:x.where,count:1,why:x.why})));d.checks=(d.checks||[]).map(c=>{if(c&&c.status==='PROBLEM'&&(isRiskName(c.check)||!/Auto Problem Memory:/.test(String(c.check||''))))return Object.assign({},c,{status:'risk',why:String(c.why||'')+' Kept as reference only; not counted as active unless stable problem memory confirms it.'});return c});d.summary=d.summary||{};d.summary.problems=stable.length;d.summary.stable_active_problems=stable.length;d.summary.problem_risks=risks.length;return d};api.__stableMemoryCountSourceNoDomFight=V}catch(e){}}
function renameText(s){return String(s||'')
 .replace(/\bProblems Found\b/g,'Active Problems Found')
 .replace(/\bActive Problems\b/g,'Active Problems Found')
 .replace(/\bAuto Problem Memory\b/g,'Known Problem Types')
 .replace(/\bLearned problem types\b/gi,'Known Problem Types')
 .replace(/\bSymptom Evidence Panel v1\b/g,'Symptom Evidence')
 .replace(/\bSymptom Evidence Panel\b/g,'Symptom Evidence');}
function renameDom(){docs(T().document).forEach(d=>{try{let bank=d.getElementById('bank');if(!bank)return;Array.from(bank.querySelectorAll('h1,h2,h3,p,summary,button,span,small,pre')).forEach(el=>{try{if(el.closest&&el.closest('pre.note')&&String(el.textContent||'').trim().charAt(0)==='{')return;let old=String(el.textContent||''),nu=renameText(old);if(nu!==old)el.textContent=nu}catch(e){}})}catch(e){}})}
function refresh(){try{patchLive();let api=T().PMPHelperBankLiveInspectorV2||window.PMPHelperBankLiveInspectorV2;if(api&&api.scan)api.scan();setTimeout(renameDom,120);setTimeout(renameDom,500)}catch(e){}}
function scan(){patchLive();renameDom()}
window.PMPHelperProblemDisplaySyncV1={version:V,scan,refresh,count:stableCount,renameDom};
try{let mo=new MutationObserver(()=>setTimeout(renameDom,80));mo.observe(document.documentElement,{childList:true,subtree:true,characterData:true})}catch(e){}
window.addEventListener('load',()=>[250,900,2500,5000].forEach(t=>setTimeout(scan,t)));
setInterval(scan,2500);scan();
})();