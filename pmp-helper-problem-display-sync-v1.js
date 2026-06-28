(()=>{
'use strict';
const V='1.2.0-headless-bug-bank-terminology';
const OLD_ACTIVE='pmp_helper_problem_memory_active_v1';
const OLD_TYPES='pmp_helper_problem_memory_types_v1';
const OLD_EVID='pmp_helper_symptom_evidence_v1';
const ACTIVE='pmp_bug_bank_active_bugs_v1';
const TYPES='pmp_bug_bank_known_types_v1';
const EVID='pmp_bug_bank_symptom_evidence_v1';
function T(){try{return top||window}catch(e){return window}}
function clean(s){return String(s||'').replace(/\s+/g,' ').trim()}
function docs(r,a,n){a=a||[];n=n||0;if(!r||n>10)return a;try{a.push(r);r.querySelectorAll('iframe,frame').forEach(f=>{try{let d=f.contentDocument||(f.contentWindow&&f.contentWindow.document);if(d)docs(d,a,n+1)}catch(e){}})}catch(e){}return a}
function load(k,d){try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(d))}catch(e){return d}}
function save(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function merge(a,b){let out=[],seen={};(Array.isArray(a)?a:[]).concat(Array.isArray(b)?b:[]).filter(Boolean).forEach(x=>{let k=String(x.signature||x.key||x.id||x.type||x.kind||x.problem||JSON.stringify(x).slice(0,100));if(seen[k])Object.assign(seen[k],x);else{seen[k]=Object.assign({},x);out.push(seen[k])}});return out}
function norm(list,section){return (Array.isArray(list)?list:[]).map((x,i)=>Object.assign({},x,{bug_bank_section:section,type:x.type||x.kind||x.problem||section+' '+(i+1),how_it_happens:x.how_it_happens||x.why||x.symptom||'',where:x.where||x.where_seen||'',fix_rule:x.fix_rule||''}))}
function mirror(){save(TYPES,norm(merge(load(TYPES,[]),load(OLD_TYPES,[])),'Known Bug Types').slice(-80));save(EVID,norm(merge(load(EVID,[]),load(OLD_EVID,[])),'Symptom Evidence').slice(-80));save(ACTIVE,norm(merge(load(ACTIVE,[]),load(OLD_ACTIVE,[])),'Active Bugs Found').slice(0,40));return{known:load(TYPES,[]).length,evidence:load(EVID,[]).length,active:load(ACTIVE,[]).length}}
function patchLive(){try{let api=T().PMPHelperBankLiveInspectorV2||window.PMPHelperBankLiveInspectorV2;if(!api||!api.live||api.__bugBankHeadlessTerminology)return;let old=api.live.bind(api);api.live=function(){let d=old()||{};d.summary=d.summary||{};d.summary.mode='helper inventory only';d.summary.bug_information_owner='Bug Bank';delete d.summary.active_problems_found;delete d.summary.known_problem_types;delete d.summary.stable_active_problems;return d};api.__bugBankHeadlessTerminology=V}catch(e){}}
function cleanVisibleOldLabels(){docs(T().document).forEach(d=>{try{let bank=d.getElementById('bank');if(!bank)return;let title=clean((bank.querySelector('[data-bank-detail-title]')||{}).textContent||'');if(title==='Bug Bank')return;if(title==='Helper Bank'){Array.from(bank.querySelectorAll('[data-helper-problem-memory-v1],[data-pm-smart-fix],[data-symptom-evidence-panel-v1]')).forEach(x=>x.remove());Array.from(bank.querySelectorAll('p.sub')).forEach(p=>{if(/Active Problems|Problem Memory|Known Problem|Symptom Evidence/i.test(p.textContent||''))p.textContent='Helper Bank shows helper inventory only. Bug information lives in Bug Bank.'})}}catch(e){}})}
function refresh(){patchLive();mirror();cleanVisibleOldLabels();try{let api=T().PMPHelperBankLiveInspectorV2||window.PMPHelperBankLiveInspectorV2;if(api&&api.scan)api.scan()}catch(e){}}
function count(){return load(ACTIVE,[]).length}
function scan(){patchLive();mirror();cleanVisibleOldLabels()}
window.PMPHelperProblemDisplaySyncV1={version:V,scan,refresh,count,renameDom:cleanVisibleOldLabels};
window.addEventListener('load',()=>[250,900,2500,5000].forEach(t=>setTimeout(scan,t)));
setInterval(scan,3000);scan();
})();