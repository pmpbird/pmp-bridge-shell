(()=>{
'use strict';
const V='1.0.3-no-live-dom-fighting';
const ACTIVE='pmp_helper_problem_memory_active_v1';
const RISK=/^(Duplicate helper files|Duplicate running helpers|Duplicate saved helper records|Empty Continuous Run level stack|Many uncategorized helpers)$/;
function T(){try{return top||window}catch(e){return window}}
function activeLoad(){try{return JSON.parse(localStorage.getItem(ACTIVE)||'[]').filter(Boolean)}catch(e){return[]}}
function isRiskName(x){return RISK.test(String(x||''))}
function stableCount(){return activeLoad().length}
function patchLive(){try{let api=T().PMPHelperBankLiveInspectorV2||window.PMPHelperBankLiveInspectorV2;if(!api||!api.live||api.__stableMemoryCountSourceNoDomFight)return;let old=api.live.bind(api);api.live=function(){let d=old()||{},stable=activeLoad(),risks=[];d.problems=(d.problems||[]).filter(p=>{let name=String(p.problem||'');risks.push(p);return false}).concat(stable.map(x=>({problem:x.kind,severity:x.severity||'medium',where:x.where,count:1,why:x.why})));d.checks=(d.checks||[]).map(c=>{if(c&&c.status==='PROBLEM'&&(isRiskName(c.check)||!/Auto Problem Memory:/.test(String(c.check||''))))return Object.assign({},c,{status:'risk',why:String(c.why||'')+' Kept as reference only; not counted as active unless stable problem memory confirms it.'});return c});d.summary=d.summary||{};d.summary.problems=stable.length;d.summary.stable_active_problems=stable.length;d.summary.problem_risks=risks.length;return d};api.__stableMemoryCountSourceNoDomFight=V}catch(e){}}
function refresh(){try{patchLive();let api=T().PMPHelperBankLiveInspectorV2||window.PMPHelperBankLiveInspectorV2;if(api&&api.scan)api.scan()}catch(e){}}
function scan(){patchLive()}
window.PMPHelperProblemDisplaySyncV1={version:V,scan,refresh,count:stableCount};
window.addEventListener('load',()=>[250,900,2500].forEach(t=>setTimeout(scan,t)));
scan();
})();